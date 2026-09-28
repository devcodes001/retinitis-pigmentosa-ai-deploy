import streamlit as st
import torch, torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageEnhance
import numpy as np, os, io, base64, time
from datetime import datetime
import utils, db
import plotly.graph_objects as go

st.set_page_config(page_title="RPeyecare | Patient Dashboard", page_icon="👤", layout="wide", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()

if st.session_state.get('role') != 'user':
    st.switch_page('pages/login.py')

user = st.session_state.user
utils.render_navbar(show_dash_links=True, role='user', username=user['name'])

if 'patient_page' not in st.session_state:
    st.session_state['patient_page'] = 'Overview'

# ── Sidebar Navigation ──
col_nav, col_main = st.columns([1, 4])

with col_nav:
    st.markdown('<div class="dash-sidebar">', unsafe_allow_html=True)
    st.markdown('<div class="snav-section">MENU</div>', unsafe_allow_html=True)
    
    pages = ["🏠 Overview", "🔬 AI Screening", "📋 My Reports", "🏥 Book Clinic", "📍 My Profile"]
    for p in pages:
        is_active = p.split(" ", 1)[1] == st.session_state['patient_page']
        cls = "snav-active" if is_active else "snav-item"
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state['patient_page'] = p.split(" ", 1)[1]
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

# ── AI Model ──
@st.cache_resource
def load_model():
    m = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    m.fc = nn.Sequential(nn.Linear(m.fc.in_features, 512), nn.ReLU(), nn.Dropout(0.3), nn.Linear(512, 2))
    if os.path.exists('models/resnet50_retinitis_classifier.pth'):
        m.load_state_dict(torch.load('models/resnet50_retinitis_classifier.pth', map_location='cpu'))
    m.eval()
    return m

def preprocess(img):
    tf = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(),
                             transforms.Normalize([.485, .456, .406], [.229, .224, .225])])
    return tf(img).unsqueeze(0)

def predict(model, tensor):
    with torch.no_grad():
        probs = torch.softmax(model(tensor), 1).numpy()[0]
    c = int(np.argmax(probs))
    dp, np_ = float(probs[0]), float(probs[1])
    risk = 'HIGH' if dp > 0.65 else ('MEDIUM' if dp > 0.4 else 'LOW')
    return {'class': c, 'confidence': float(probs[c]), 'prob_disease': dp, 'prob_normal': np_, 'risk': risk}

def generate_pdf(patient, res, filename, img):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                     TableStyle, HRFlowable, Image as RLImage)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    W = A4[0] - 4*cm
    styles = getSampleStyleSheet()
    is_dis = res['class'] == 0
    result_label = 'DISEASE DETECTED' if is_dis else 'NORMAL (HEALTHY)'
    result_color = colors.HexColor('#c0392b') if is_dis else colors.HexColor('#27ae60')
    story = []
    title_style = ParagraphStyle('t', fontSize=20, textColor=colors.HexColor('#1a3a5c'), alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=4)
    sub_style = ParagraphStyle('s', fontSize=9, textColor=colors.HexColor('#666'), alignment=TA_CENTER, spaceAfter=4)
    story.append(Paragraph('RETINA AI — MEDICAL SCREENING REPORT', title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", sub_style))
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#1a3a5c'), spaceAfter=10))
    pt = Table([
        ['Patient Name', patient.get('name','N/A'), 'City', patient.get('city','N/A')],
        ['Phone', patient.get('phone','N/A'), 'State', patient.get('state','N/A')],
        ['Risk Level', res['risk'], 'File', filename],
    ], colWidths=[W*.2, W*.3, W*.2, W*.3])
    pt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#eaf0fb')),
        ('BACKGROUND',(2,0),(2,-1),colors.HexColor('#eaf0fb')),
        ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold'),
        ('FONTNAME',(2,0),(2,-1),'Helvetica-Bold'),
        ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#ccc')),
        ('PADDING',(0,0),(-1,-1),7),
    ]))
    story.append(pt)
    story.append(Spacer(1,10))
    result_p = Paragraph(f'<font size="14" color="{"#c0392b" if is_dis else "#27ae60"}"><b>{result_label}</b></font>', ParagraphStyle('r', alignment=TA_CENTER, spaceAfter=6))
    conf_p = Paragraph(f'Confidence: {res["confidence"]*100:.2f}% | Normal: {res["prob_normal"]*100:.2f}% | Disease: {res["prob_disease"]*100:.2f}%', ParagraphStyle('c', fontSize=10, alignment=TA_CENTER, textColor=colors.HexColor('#333')))
    ic = img.copy().convert('RGB'); ic.thumbnail((180,180))
    ib = io.BytesIO(); ic.save(ib,'JPEG',quality=85); ib.seek(0)
    rt = Table([[RLImage(ib,4.5*cm,4.5*cm),[result_p,conf_p]]],colWidths=[5*cm,W-5*cm])
    rt.setStyle(TableStyle([
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f4f8ff')),
        ('GRID',(0,0),(-1,-1),.5,colors.HexColor('#ccc')),
        ('PADDING',(0,0),(-1,-1),10),
        ('LINEABOVE',(0,0),(-1,0),3,result_color),
    ]))
    story.append(rt)
    story.append(Spacer(1,10))
    sec = ParagraphStyle('h', fontSize=12, textColor=colors.HexColor('#1a3a5c'), spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold')
    bd  = ParagraphStyle('b', fontSize=10, textColor=colors.HexColor('#333'), spaceAfter=4)
    story.append(Paragraph('Clinical Recommendations', sec))
    recs = (['Consult an ophthalmologist immediately.', 'Bring this report to your eye doctor.', 'Consider genetic counselling for RP.', 'Discuss Vitamin A supplementation and gene therapy eligibility.', 'Use UV-protective eyewear.'] if is_dis else ['No RP signs detected. Continue annual checkups.', 'Maintain a diet rich in Vitamins A, C, E.', 'Use UV-protective sunglasses outdoors.', 'Report any changes in night/peripheral vision promptly.'])
    for r2 in recs: story.append(Paragraph(f'• {r2}', bd))
    disc = ParagraphStyle('d', fontSize=8, textColor=colors.HexColor('#888'), leftIndent=10)
    story.append(Spacer(1,10))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#ccc'), spaceAfter=6))
    story.append(Paragraph('DISCLAIMER: For research/educational use only. Not a clinical diagnosis.', disc))
    story.append(Paragraph(f'RPeyecare v2.0 | Report ID: RP-{datetime.now().strftime("%Y%m%d%H%M%S")}', ParagraphStyle('ft', fontSize=8, textColor=colors.HexColor('#aaa'), alignment=TA_CENTER)))
    doc.build(story)
    buf.seek(0)
    return buf.read()


with col_main:
    st.markdown(f"""
    <div class="dash-hdr" style="border-radius:15px; margin-bottom:2rem;">
      <div>
        <div class="dash-title">👤 Patient Dashboard</div>
        <div class="dash-sub">Welcome back, {user['name']} · {user.get('city','—')}, {user.get('state','—')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state['patient_page'] == "Overview":
        dets = db.get_user_detections(user["id"])
        high_risk_count = sum(1 for d in dets if d['risk_level'] == 'HIGH')
        bookings = db.get_user_bookings(user["id"])
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="mcard"><div class="mval" style="color:#2563eb;">{len(dets)}</div><div class="mlbl">Total Screenings</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="mcard"><div class="mval" style="color:{"#dc2626" if high_risk_count>0 else "#059669"};">{high_risk_count}</div><div class="mlbl">High Risk Scans</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="mcard"><div class="mval" style="color:#0ea5e9;">{len(bookings)}</div><div class="mlbl">Total Bookings</div></div>', unsafe_allow_html=True)
        last_date = dets[0]["timestamp"].split(" ")[0] if dets else "No scans yet"
        c4.markdown(f'<div class="mcard"><div class="mval" style="font-size:1.4rem;padding-top:0.4rem;color:#475569;">{last_date}</div><div class="mlbl">Latest Activity</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if high_risk_count > 0:
            st.markdown("""
            <div class="urgent" style="margin-bottom:1.8rem; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h3 style="color:#dc2626; margin:0 0 0.3rem; font-size:1.15rem; font-weight:800;">🚨 Retinal Pathologies Flagged</h3>
                    <p style="color:#7f1d1d; margin:0; font-size:0.9rem;">You have screenings indicating high risk for Retinitis Pigmentosa. Please schedule an ophthalmic clinical consultation.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🏥 Book an Appointment Now →", key="urgent_book_btn", type="primary"):
                st.session_state['patient_page'] = "Book Clinic"
                st.rerun()
                
        st.markdown("### 📋 Recent Screening Activity")
        if not dets:
            st.info("ℹ️ No screenings found. Navigate to **🔬 AI Screening** to analyze your first retinal fundus scan.")
        else:
            for d in dets[:4]:
                risk = d["risk_level"]
                badge_cls = "rb-high" if risk == "HIGH" else ("rb-medium" if risk == "MEDIUM" else "rb-low")
                st.markdown(f"""
                <div class="card" style="padding:1.1rem 1.4rem; margin-bottom:0.6rem;">
                   <div style="display:flex; justify-content:space-between; align-items:center;">
                      <div>
                          <div style="font-weight:700; color:#0f172a; font-size:0.98rem;">{d['result']}</div>
                          <div style="color:#64748b; font-size:0.82rem; margin-top:0.2rem;">📅 {d['timestamp']} &nbsp;|&nbsp; File: <code>{d.get('filename','scan.png')}</code></div>
                      </div>
                      <div><span class="{badge_cls} rbadge">{risk} RISK</span></div>
                   </div>
                </div>
                """, unsafe_allow_html=True)
                
    elif st.session_state['patient_page'] == "AI Screening":
        st.markdown("### 🔬 Automated Retinal Screening")
        st.markdown("<p style='color:#64748b;font-size:0.95rem;margin-top:-0.5rem;'>Upload a fundus image (color photograph of the back of the eye) for instant AI classification.</p>", unsafe_allow_html=True)
        
        # State initialization for persistent screening
        if 'active_screening' not in st.session_state:
            st.session_state['active_screening'] = None

        c_up, c_ctrl = st.columns([2.2, 1], gap="medium")
        with c_up:
            uploaded = st.file_uploader("Upload Retinal Scan (PNG/JPG/BMP)", type=["png","jpg","jpeg","bmp"], label_visibility="collapsed")
        
        with c_ctrl:
            auto_enh = st.checkbox("Apply Contrast Equalization", value=True, help="Enhances vascular contrast and pigment definition")
            run_btn = st.button("🧠 Run AI Screening", type="primary", use_container_width=True, disabled=(uploaded is None))
            
        if uploaded:
            raw_img = Image.open(uploaded).convert("RGB")
            
            if run_btn:
                proc = raw_img.copy()
                if auto_enh:
                    proc = ImageEnhance.Contrast(proc).enhance(1.2)
                    proc = ImageEnhance.Sharpness(proc).enhance(1.1)

                model = load_model()
                with st.spinner("Analyzing retinal vasculature & pigment patterns..."):
                    pb = st.progress(0, "Normalizing tensors...")
                    t = preprocess(proc)
                    pb.progress(45, "Executing ResNet-50 feature extraction...")
                    r = predict(model, t)
                    pb.progress(85, "Generating diagnostic probabilities...")
                    time.sleep(0.2)
                    pb.progress(100, "Done!")

                is_dis = (r["class"] == 0)
                label = "DISEASE DETECTED (Retinitis Pigmentosa)" if is_dis else "NORMAL (Healthy Retina)"
                risk = r["risk"]
                
                # Save detection to DB
                db.save_detection(user["id"], uploaded.name, label, r["prob_disease"], r["prob_normal"], r["confidence"], risk)
                pdf_bytes = generate_pdf(dict(user), r, uploaded.name, raw_img)
                
                # Persist in session state
                st.session_state['active_screening'] = {
                    "result": r,
                    "label": label,
                    "is_dis": is_dis,
                    "risk": risk,
                    "raw_img": raw_img,
                    "proc_img": proc,
                    "filename": uploaded.name,
                    "pdf": pdf_bytes
                }
                st.toast("✅ Analysis complete and archived to your medical record.")
                st.rerun()

        # Render Active Screening Results Persistently
        if st.session_state['active_screening']:
            active = st.session_state['active_screening']
            r = active["result"]
            is_dis = active["is_dis"]
            label = active["label"]
            risk = active["risk"]
            
            cls_box = "res-disease" if is_dis else "res-normal"
            risk_chip = "🔴 HIGH" if risk == "HIGH" else ("🟡 MEDIUM" if risk == "MEDIUM" else "🟢 LOW")
            
            st.markdown(f"""
            <div class="{cls_box}" style="margin:1.6rem 0;">
                <div class="res-label">{label}</div>
                <div class="res-sub">
                    Confidence: <b>{r['confidence']*100:.1f}%</b> &nbsp;|&nbsp; 
                    Assessed Risk Level: <b>{risk_chip}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            c_img1, c_img2, c_chart = st.columns([1, 1, 1.4], gap="medium")
            with c_img1:
                st.markdown("<div class='preview-box'><b>Original Scan</b></div>", unsafe_allow_html=True)
                st.image(active["raw_img"], use_container_width=True)
            with c_img2:
                st.markdown("<div class='preview-box'><b>Enhanced View</b></div>", unsafe_allow_html=True)
                st.image(active["proc_img"], use_container_width=True)
            with c_chart:
                fig = go.Figure(go.Bar(
                    x=["Normal Retina", "Retinitis Pigmentosa"],
                    y=[r["prob_normal"] * 100, r["prob_disease"] * 100],
                    marker_color=["#10b981", "#ef4444"],
                    text=[f"{r['prob_normal']*100:.1f}%", f"{r['prob_disease']*100:.1f}%"],
                    textposition="outside",
                    textfont=dict(size=13, color="#0f172a", family="Plus Jakarta Sans")
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#0f172a", family="Plus Jakarta Sans"),
                    yaxis=dict(range=[0, 118], gridcolor="#e2e8f0"),
                    xaxis=dict(gridcolor="#e2e8f0"),
                    height=240,
                    margin=dict(t=20, b=10, l=10, r=10),
                    showlegend=False,
                    bargap=0.45
                )
                st.plotly_chart(fig, use_container_width=True)
            
            col_d1, col_d2 = st.columns([2, 1])
            with col_d1:
                st.download_button(
                    "📄 Download Clinical PDF Diagnostic Report",
                    data=active["pdf"],
                    file_name=f"RPeyecare_Report_{user['name'].replace(' ','_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
            with col_d2:
                if st.button("🔄 Reset / New Scan", use_container_width=True):
                    st.session_state['active_screening'] = None
                    st.rerun()
            
            if risk == "HIGH":
                st.markdown("""
                <div class="urgent" style="margin-top:1.5rem; display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <h4 style="color:#dc2626; margin:0 0 0.3rem;">⚠️ Recommended Action: Clinical Consultation</h4>
                        <p style="color:#7f1d1d; margin:0; font-size:0.88rem;">Significant signs of peripheral photoreceptor degeneration detected. Connect with a specialist immediately.</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("🏥 Find & Book Clinic Near Me →", key="high_risk_book_btn", use_container_width=True):
                    st.session_state['patient_page'] = "Book Clinic"
                    st.rerun()

                        
    elif st.session_state['patient_page'] == "My Reports":
        st.markdown("### 📋 My Reports")
        dets = db.get_user_detections(user["id"])
        if not dets:
            st.info("No detections yet.")
        else:
            for d in dets:
                risk = d["risk_level"]
                badge = f'<span class="rb-{"high" if risk=="HIGH" else "medium" if risk=="MEDIUM" else "low"} rbadge">{risk}</span>'
                with st.expander(f"{d['timestamp']} — {d['result']}"):
                    c1,c2,c3,c4 = st.columns(4)
                    c1.metric("Result",    d["result"])
                    c2.metric("Confidence",f"{d['confidence']*100:.1f}%")
                    c3.metric("Disease Prob",f"{d['disease_prob']*100:.1f}%")
                    c4.markdown(f"Risk: {badge}", unsafe_allow_html=True)
                    st.markdown(f"📁 File: `{d['filename']}`")
                    
    elif st.session_state['patient_page'] == "Book Clinic":
        st.markdown("### 🏥 Find & Book Nearby Clinics")
        
        with st.form("search_clinics"):
            c1, c2, c3 = st.columns([2, 2, 1])
            scity  = c1.text_input("City",  value=user.get("city",""), label_visibility="collapsed")
            sstate = c2.text_input("State", value=user.get("state",""), label_visibility="collapsed")
            search = c3.form_submit_button("🔍 Search", use_container_width=True)
        
        if search or scity:
            clinics = db.get_nearby_clinics(scity, sstate)
            if not clinics:
                st.warning("No clinics found near you.")
            else:
                st.success(f"Found {len(clinics)} clinics.")
                dets = db.get_user_detections(user["id"])
                det_id = dets[0]["id"] if dets else None
                for cl in clinics:
                    st.markdown(f"""<div class="clcard">
                    <div class="clcard-name">🏥 {cl['clinic_name']}</div>
                    <div class="clcard-detail">
                    👨‍⚕️ Dr. {cl['doctor_name']} · {cl['specialization']}<br>
                    📍 {cl['address']}, {cl['city']}, {cl['state']} · 📞 {cl['phone']}
                    </div></div>""", unsafe_allow_html=True)
                    if st.button(f"📅 Book Appointment at {cl['clinic_name']}", key=f"bk_{cl['id']}"):
                        notes = f"Risk: {dets[0]['risk_level'] if dets else 'N/A'}"
                        ok, msg = db.create_booking(user["id"], cl["id"], det_id, notes)
                        if ok: 
                            st.toast("✅ Appointment Requested Successfully!")
                            st.success(f"✅ {msg}")
                        else: st.error(f"❌ {msg}")
                        
        st.markdown("---")
        st.markdown("### 📅 My Appointments")
        bookings = db.get_user_bookings(user["id"])
        if not bookings:
            st.info("No appointments.")
        else:
            for b in bookings:
                st.markdown(f"""<div class="clcard">
                <div class="clcard-name">🏥 {b['clinic_name']}</div>
                <div class="clcard-detail">
                📅 {b['timestamp']} · Status: <b>{b['status'].upper()}</b>
                </div></div>""", unsafe_allow_html=True)
                
    elif st.session_state['patient_page'] == "My Profile":
        st.markdown("### 👤 My Profile")
        st.markdown(f"""
        <div class="card" style="margin-bottom: 2rem;">
        <div class="c-title">Patient Information</div>
        <div class="c-desc">
        <b>Name:</b> {user.get('name')}<br>
        <b>Email:</b> {user.get('email')}<br>
        <b>Phone:</b> {user.get('phone')}<br>
        <b>City:</b> {user.get('city')}<br>
        <b>State:</b> {user.get('state')}<br>
        </div></div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📍 Update Location")
        with st.form("loc_form"):
            city  = st.text_input("City",  value=user.get("city",""))
            state = st.text_input("State", value=user.get("state",""))
            addr  = st.text_area("Address", value=user.get("address",""))
            if st.form_submit_button("Update Location", type="primary", use_container_width=True):
                db.update_user_location(user["id"], city, state, addr)
                st.session_state.user.update({"city": city, "state": state, "address": addr})
                st.toast("✅ Location updated.")
                st.rerun()
