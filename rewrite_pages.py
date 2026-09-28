import re

login_content = r'''import streamlit as st
import utils
import db

st.set_page_config(page_title="Retina AI | Login", page_icon="🔑", layout="centered", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()

# Redirect if already logged in
role = st.session_state.get("role")
if role == "user":    st.switch_page("pages/patient.py")
elif role == "clinic": st.switch_page("pages/clinic.py")
elif role == "admin":  st.switch_page("pages/admin.py")

utils.render_navbar()

st.markdown("""
<div class="auth-box">
  <div class="auth-title">Welcome Back</div>
  <div class="auth-sub">Sign in to your Retina AI account</div>
</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    role = st.radio("Login as", ["Patient", "Clinic", "Admin"], horizontal=True)
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Sign In 🔑", use_container_width=True, type="primary")

if submitted:
    if not email or not password:
        st.error("❌ Please enter both email and password.")
    else:
        if role == "Admin":
            u = db.login_admin(email, password)
            if u:
                st.session_state.update({"role": "admin", "user": u})
                st.switch_page("pages/admin.py")
            else:
                st.error("❌ Invalid admin credentials.")
        elif role == "Patient":
            u, err = db.login_user(email, password)
            if u:
                st.session_state.update({"role": "user", "user": u})
                st.switch_page("pages/patient.py")
            else:
                st.error(f"❌ {err}")
        elif role == "Clinic":
            u, err = db.login_clinic(email, password)
            if u:
                st.session_state.update({"role": "clinic", "user": u})
                st.switch_page("pages/clinic.py")
            else:
                st.error(f"❌ {err}")

st.info("🛡️ Admin: admin@retinaai.com / Admin@123")

if st.button("Don't have an account? Register here", use_container_width=True):
    st.switch_page("pages/register.py")
'''

register_content = r'''import streamlit as st
import utils, db
import re

st.set_page_config(page_title="Retina AI | Register", page_icon="📝", layout="centered", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()
utils.render_navbar()

tab1, tab2 = st.tabs(["👤 Patient Registration", "🏥 Clinic Registration"])

with tab1:
    st.markdown("""<div class="auth-box">
    <div class="auth-title">Patient Registration</div>
    <div class="auth-sub">Create your account to start screening</div>
    </div>""", unsafe_allow_html=True)
    
    with st.form("reg_user"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name *")
        email = c2.text_input("Email Address *")
        pw = c1.text_input("Password *", type="password")
        pw2 = c2.text_input("Confirm Password *", type="password")
        phone = c1.text_input("Phone Number (10 digits) *")
        city = c2.text_input("City *")
        state = c1.text_input("State *")
        addr = st.text_area("Address")
        sub = st.form_submit_button("Register as Patient 👤", use_container_width=True, type="primary")
        
        if sub:
            if not all([name, email, pw, phone, city, state]):
                st.error("❌ Please fill all required fields.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("❌ Invalid email format.")
            elif not phone.isdigit() or len(phone) < 10:
                st.error("❌ Phone number must contain at least 10 digits.")
            elif pw != pw2:
                st.error("❌ Passwords do not match.")
            elif len(pw) < 6:
                st.error("❌ Password must be at least 6 characters.")
            else:
                ok, msg = db.register_user(name, email, pw, phone, city, state, addr)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
    if st.button("Already have an account? Login here", key="login_p"):
        st.switch_page("pages/login.py")

with tab2:
    st.markdown("""<div class="auth-box">
    <div class="auth-title">Clinic Registration</div>
    <div class="auth-sub">Register your clinic — pending admin approval</div>
    </div>""", unsafe_allow_html=True)
    with st.form("reg_clinic"):
        c1, c2 = st.columns(2)
        cname = c1.text_input("Clinic Name *")
        dname = c2.text_input("Doctor Name *")
        email = c1.text_input("Email *")
        phone = c2.text_input("Phone (10 digits) *")
        pw = c1.text_input("Password *", type="password")
        pw2 = c2.text_input("Confirm Password *", type="password")
        city = c1.text_input("City *")
        state = c2.text_input("State *")
        spec = c1.selectbox("Specialization *", ["Ophthalmology", "Retinal Surgery", "Neuro-Ophthalmology", "Low Vision Care", "General Eye Care"])
        regn = c2.text_input("Registration Number *")
        addr = st.text_area("Full Address *")
        sub = st.form_submit_button("Submit Clinic Registration 🏥", use_container_width=True, type="primary")
        
        if sub:
            if not all([cname, dname, email, phone, pw, city, state, addr, regn]):
                st.error("❌ Please fill all required fields.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("❌ Invalid email format.")
            elif not phone.isdigit() or len(phone) < 10:
                st.error("❌ Phone number must contain at least 10 digits.")
            elif pw != pw2:
                st.error("❌ Passwords do not match.")
            else:
                ok, msg = db.register_clinic(cname, dname, email, pw, phone, city, state, addr, spec, regn)
                if ok:
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
    if st.button("Already have a clinic account? Login here", key="login_c"):
        st.switch_page("pages/login.py")
'''

patient_content = r'''import streamlit as st
import torch, torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageEnhance
import numpy as np, os, io, base64, time
from datetime import datetime
import utils, db
import plotly.graph_objects as go

st.set_page_config(page_title="Retina AI | Patient Dashboard", page_icon="👤", layout="wide", initial_sidebar_state="expanded")
utils.init_session()
utils.render_css()

if st.session_state.get('role') != 'user':
    st.switch_page('pages/login.py')

user = st.session_state.user
utils.render_navbar(show_dash_links=True, role='user', username=user['name'])

# ── Sidebar Navigation ──
with st.sidebar:
    st.markdown("## 👤 Menu")
    pages = ["🏠 Overview", "🔬 AI Screening", "📋 My Reports", "🏥 Book Clinic", "📍 My Profile"]
    current_page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"**{user['name']}**")
    st.markdown(f"📍 {user.get('city','—')}, {user.get('state','—')}")

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
    story.append(Paragraph(f'Retina AI v2.0 | Report ID: RP-{datetime.now().strftime("%Y%m%d%H%M%S")}', ParagraphStyle('ft', fontSize=8, textColor=colors.HexColor('#aaa'), alignment=TA_CENTER)))
    doc.build(story)
    buf.seek(0)
    return buf.read()


st.markdown(f"""
<div class="dash-hdr" style="border-radius:15px; margin-bottom:2rem;">
  <div>
    <div class="dash-title">👤 Patient Dashboard</div>
    <div class="dash-sub">Welcome back, {user['name']} · {user.get('city','—')}, {user.get('state','—')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

if "Overview" in current_page:
    dets = db.get_user_detections(user["id"])
    high_risk_count = sum(1 for d in dets if d['risk_level'] == 'HIGH')
    bookings = db.get_user_bookings(user["id"])
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="mcard"><div class="mval">{len(dets)}</div><div class="mlbl">Total Screenings</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mcard"><div class="mval" style="color:#ff6b6b;">{high_risk_count}</div><div class="mlbl">High Risk Scans</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mcard"><div class="mval">{len(bookings)}</div><div class="mlbl">Total Bookings</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="mcard"><div class="mval">{dets[0]["timestamp"].split(" ")[0] if dets else "None"}</div><div class="mlbl">Last Scan</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if high_risk_count > 0:
        st.markdown("""<div class="urgent" style="margin-bottom:2rem;">
        <h3 style="color:#ff6b6b;margin:0 0 .5rem;">🚨 High Risk Detected</h3>
        <p style="color:#ef9a9a;margin:0;font-size:.92rem;">You have high-risk scans. Please book a clinic appointment from the menu.</p>
        </div>""", unsafe_allow_html=True)
            
    st.markdown("### Recent Screenings")
    if not dets:
        st.info("No screenings yet. Go to AI Screening to upload your first image.")
    else:
        for d in dets[:3]:
            risk = d["risk_level"]
            badge = f'<span class="rb-{"high" if risk=="HIGH" else "medium" if risk=="MEDIUM" else "low"} rbadge">{risk}</span>'
            st.markdown(f"""
            <div class="card" style="padding:1rem; margin-bottom:.5rem;">
               <div style="display:flex; justify-content:space-between; align-items:center;">
                  <div><b>{d['timestamp']}</b> - {d['result']}</div>
                  <div>{badge}</div>
               </div>
            </div>
            """, unsafe_allow_html=True)
            
elif "AI Screening" in current_page:
    st.markdown("### 📤 Upload Retinal Image")
    st.info("Upload a retinal fundus image (.png, .jpg, .bmp) for AI disease detection.")
    uploaded = st.file_uploader("Choose a retinal fundus image", type=["png","jpg","jpeg","bmp"])
    
    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        auto_enh = st.checkbox("Auto-enhance contrast before processing", value=True)
        
        if st.button("🧠 Run AI Analysis", type="primary", use_container_width=True):
            proc = img.copy()
            if auto_enh:
                proc = ImageEnhance.Contrast(proc).enhance(1.2)
                proc = ImageEnhance.Sharpness(proc).enhance(1.1)

            model = load_model()
            with st.spinner("Analysing retinal features..."):
                pb = st.progress(0, "Preprocessing...")
                t  = preprocess(proc); pb.progress(40, "Running Inference...")
                r  = predict(model, t); pb.progress(90, "Generating Results...")
                time.sleep(0.2);       pb.progress(100, "Done!")

            is_dis  = r["class"] == 0
            cls_box = "res-disease" if is_dis else "res-normal"
            label   = "DISEASE DETECTED" if is_dis else "NORMAL (HEALTHY)"
            risk    = r["risk"]

            st.markdown(f"""<div class="{cls_box}" style="margin:2rem 0;">
            <div class="res-label">{label}</div>
            <div class="res-sub">Confidence: {r['confidence']*100:.2f}% | Risk Level: {risk}</div>
            </div>""", unsafe_allow_html=True)
            
            db.save_detection(user["id"], uploaded.name, label, r["prob_disease"], r["prob_normal"], r["confidence"], risk)
            st.toast("✅ Detection saved to your history.")
            
            c1, c2 = st.columns([1,1])
            with c1:
                st.markdown("**Processed Image**")
                st.image(proc, use_container_width=True)
            with c2:
                fig = go.Figure(go.Bar(
                    x=["Normal","Disease"],
                    y=[r["prob_normal"]*100, r["prob_disease"]*100],
                    marker_color=["#27ae60","#e74c3c"],
                    text=[f"{r['prob_normal']*100:.1f}%",f"{r['prob_disease']*100:.1f}%"],
                    textposition="outside", textfont=dict(size=14,color="white")
                ))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="white"),yaxis=dict(range=[0,115],gridcolor="rgba(255,255,255,.07)"),
                    height=320,margin=dict(t=20,b=10),showlegend=False,bargap=0.45)
                st.plotly_chart(fig, use_container_width=True)
            
            pdf = generate_pdf(dict(user), r, uploaded.name, img)
            st.download_button("⬇️ Download Full PDF Report", pdf, f"RetinaAI_{user['name']}.pdf", "application/pdf", use_container_width=True)
            
            if risk == "HIGH":
                st.markdown("""<div class="urgent" style="margin-top:2rem;">
                <h3 style="color:#ff6b6b;margin:0 0 .5rem;">🚨 High Risk Detected</h3>
                <p style="color:#ef9a9a;margin:0;font-size:.92rem;">Please book a clinic appointment from the side menu immediately.</p>
                </div>""", unsafe_allow_html=True)
                    
elif "My Reports" in current_page:
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
                
elif "Book Clinic" in current_page:
    st.markdown("### 🏥 Find & Book Nearby Clinics")
    
    with st.form("search_clinics"):
        c1, c2 = st.columns(2)
        scity  = c1.text_input("City",  value=user.get("city",""))
        sstate = c2.text_input("State", value=user.get("state",""))
        search = st.form_submit_button("🔍 Search Clinics", use_container_width=True)
    
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
            
elif "My Profile" in current_page:
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
'''

clinic_content = r'''import streamlit as st
from datetime import datetime
import utils, db
import plotly.graph_objects as go

st.set_page_config(page_title="Retina AI | Clinic Portal", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")
utils.init_session()
utils.render_css()

if st.session_state.get('role') != 'clinic':
    st.switch_page('pages/login.py')

cl = st.session_state.user
utils.render_navbar(show_dash_links=True, role='clinic', username=cl['clinic_name'])

with st.sidebar:
    st.markdown("## 🏥 Menu")
    pages = ["🏠 Dashboard", "📅 Appointments", "⚠️ High Risk Patients", "🏥 Clinic Profile"]
    current_page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"**{cl['clinic_name']}**")
    st.markdown(f"👨‍⚕️ Dr. {cl['doctor_name']}")

st.markdown(f"""
<div class="dash-hdr" style="border-radius:15px; margin-bottom:2rem;">
  <div>
    <div class="dash-title">🏥 Clinic Dashboard</div>
    <div class="dash-sub">{cl['clinic_name']} · Dr. {cl['doctor_name']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

bookings = db.get_clinic_bookings(cl["id"])

if "Dashboard" in current_page:
    pending = sum(1 for b in bookings if b["status"] == "pending")
    confirmed = sum(1 for b in bookings if b["status"] == "confirmed")
    high = sum(1 for b in bookings if b.get("risk_level") == "HIGH")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="mcard"><div class="mval">{len(bookings)}</div><div class="mlbl">Total Appointments</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mcard"><div class="mval">{pending}</div><div class="mlbl">Pending</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mcard"><div class="mval">{confirmed}</div><div class="mlbl">Confirmed</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="mcard"><div class="mval" style="color:#ff6b6b;">{high}</div><div class="mlbl">High Risk</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br>### 📊 Appointment Status", unsafe_allow_html=True)
    fig = go.Figure(go.Bar(
        x=["Pending", "Confirmed", "Cancelled"],
        y=[pending, confirmed, sum(1 for b in bookings if b["status"] == "cancelled")],
        marker_color=["#f39c12", "#27ae60", "#e74c3c"]
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font=dict(color="white"),height=300)
    st.plotly_chart(fig, use_container_width=True)
    
elif "Appointments" in current_page:
    st.markdown("### 📅 Manage Appointments")
    filter_status = st.selectbox("Filter Status", ["All", "Pending", "Confirmed", "Cancelled"])
    st.markdown("---")
    
    for b in bookings:
        if filter_status != "All" and b["status"].lower() != filter_status.lower(): continue
        
        risk = b.get("risk_level", "N/A")
        rb = f'<span class="rb-{"high" if risk=="HIGH" else "medium" if risk=="MEDIUM" else "low"} rbadge">{risk}</span>'
        
        with st.expander(f"{b['user_name']} — {b['timestamp']} — {b['status'].upper()}", expanded=(b["status"]=="pending")):
            st.markdown(f"""
            **Contact:** {b['user_phone']} ({b['user_city']})<br>
            **AI Result:** {b.get('result', 'N/A')} (Risk: {rb})<br>
            **Notes:** {b.get('notes', '—')}
            """, unsafe_allow_html=True)
            
            col1, col2, _ = st.columns([1,1,3])
            if col1.button("✅ Confirm Appointment", key=f"con_{b['id']}", type="primary"):
                db.update_booking_status(b["id"], "confirmed")
                st.toast(f"Confirmed appointment for {b['user_name']}")
                st.rerun()
            if col2.button("❌ Cancel", key=f"can_{b['id']}"):
                db.update_booking_status(b["id"], "cancelled")
                st.toast(f"Cancelled appointment for {b['user_name']}")
                st.rerun()
                
elif "High Risk" in current_page:
    st.markdown("### ⚠️ High Risk Patients requiring immediate attention")
    high_risk = [b for b in bookings if b.get("risk_level") == "HIGH"]
    if not high_risk:
        st.success("No high risk patients currently.")
    else:
        for b in high_risk:
            st.markdown(f"""<div class="urgent" style="margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between;">
              <h4 style="color:#ff6b6b; margin:0;">{b['user_name']}</h4>
              <span style="font-weight:bold;">Status: {b['status'].upper()}</span>
            </div>
            <p style="margin:0.5rem 0;">📞 {b['user_phone']} | 📍 {b['user_city']}</p>
            </div>""", unsafe_allow_html=True)
            
elif "Clinic Profile" in current_page:
    st.markdown("### 🏥 Clinic Profile")
    st.markdown(f"""<div class="card">
    <div class="c-title">{cl['clinic_name']}</div>
    <div class="c-desc">
    <b>Doctor:</b> {cl['doctor_name']}<br>
    <b>Specialization:</b> {cl['specialization']}<br>
    <b>Address:</b> {cl['address']}, {cl['city']}, {cl['state']}<br>
    <b>Phone:</b> {cl['phone']}<br>
    <b>Reg Number:</b> {cl['reg_number']}<br>
    <b>Status:</b> {'✅ Active & Approved' if cl['approved'] else '⏳ Pending Admin Approval'}
    </div></div>""", unsafe_allow_html=True)
'''

admin_content = r'''import streamlit as st
import pandas as pd
from datetime import datetime
import utils, db
import plotly.graph_objects as go

st.set_page_config(page_title="Retina AI | Admin", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
utils.init_session()
utils.render_css()

if st.session_state.get('role') != 'admin':
    st.switch_page('pages/login.py')

utils.render_navbar(show_dash_links=True, role='admin', username='Administrator')

with st.sidebar:
    st.markdown("## 🛡️ Admin Menu")
    pages = ["🏠 Overview", "⏳ Clinic Approval", "✅ Active Clinics", "👥 Users", "📊 Analytics"]
    current_page = st.radio("Navigate", pages, label_visibility="collapsed")
    st.markdown("---")
    st.markdown("**System Administrator**")

st.markdown("""
<div class="dash-hdr" style="border-radius:15px; margin-bottom:2rem;">
  <div>
    <div class="dash-title">🛡️ Admin Dashboard</div>
    <div class="dash-sub">System Management & Analytics</div>
  </div>
</div>
""", unsafe_allow_html=True)

stats = db.get_stats()

if "Overview" in current_page:
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="mcard"><div class="mval">{stats["total_users"]}</div><div class="mlbl">Total Users</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="mcard"><div class="mval">{stats["total_clinics"]}</div><div class="mlbl">Active Clinics</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="mcard"><div class="mval" style="color:#f39c12;">{stats["pending_clinics"]}</div><div class="mlbl">Pending Clinics</div></div>', unsafe_allow_html=True)
    
    c4, c5, c6 = st.columns(3)
    c4.markdown(f'<div class="mcard"><div class="mval">{stats["total_detections"]}</div><div class="mlbl">Total Screenings</div></div>', unsafe_allow_html=True)
    c5.markdown(f'<div class="mcard"><div class="mval">{stats["total_bookings"]}</div><div class="mlbl">Total Bookings</div></div>', unsafe_allow_html=True)
    c6.markdown(f'<div class="mcard"><div class="mval" style="color:#ff6b6b;">{stats["high_risk"]}</div><div class="mlbl">High Risk Cases</div></div>', unsafe_allow_html=True)
    
    st.success("✅ System operational.")
        
elif "Clinic Approval" in current_page:
    st.markdown("### ⏳ Pending Clinic Approvals")
    pending = [c for c in db.get_all_clinics(False) if not c["approved"]]
    if not pending:
        st.success("✅ No pending approvals.")
    else:
        for c in pending:
            with st.expander(f"Pending: {c['clinic_name']} - Dr. {c['doctor_name']}", expanded=True):
                st.markdown(f"""
                **Specialization:** {c['specialization']} | **Reg No:** {c['reg_number']}<br>
                **Contact:** {c['email']} | {c['phone']}<br>
                **Location:** {c['address']}, {c['city']}, {c['state']}
                """, unsafe_allow_html=True)
                
                col1, col2, _ = st.columns([1,1,4])
                if col1.button("✅ Approve Clinic", key=f"ap_{c['id']}", type="primary"):
                    db.approve_clinic(c["id"])
                    st.toast(f"Approved {c['clinic_name']}")
                    st.rerun()
                if col2.button("❌ Reject", key=f"rj_{c['id']}"):
                    db.reject_clinic(c["id"])
                    st.toast(f"Rejected {c['clinic_name']}")
                    st.rerun()
                    
elif "Active Clinics" in current_page:
    st.markdown("### ✅ Active Clinics")
    active = [c for c in db.get_all_clinics(True)]
    if not active:
        st.info("No active clinics.")
    else:
        for c in active:
            st.markdown(f"""<div class="card" style="margin-bottom:1rem; padding:1rem;">
            <b>{c['clinic_name']}</b> - Dr. {c['doctor_name']} ({c['specialization']})<br>
            📍 {c['city']}, {c['state']} | 📞 {c['phone']}
            </div>""", unsafe_allow_html=True)
            
elif "Users" in current_page:
    st.markdown("### 👥 Manage Users")
    users = db.get_all_users()
    if not users:
        st.info("No users found.")
    else:
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("### 🗑️ Delete User")
        with st.form("delete_user_form"):
            del_id = st.number_input("Enter User ID to delete", min_value=1, step=1)
            if st.form_submit_button("Delete User", type="primary"):
                db.delete_user(del_id)
                st.toast(f"User {del_id} deleted.")
                st.rerun()
            
elif "Analytics" in current_page:
    st.markdown("### 📊 System Analytics")
    fig = go.Figure(go.Bar(
        x=["Users", "Active Clinics", "Pending", "Screenings", "Bookings", "High Risk"],
        y=[stats["total_users"], stats["total_clinics"], stats["pending_clinics"],
           stats["total_detections"], stats["total_bookings"], stats["high_risk"]],
        marker_color=["#3498db", "#27ae60", "#f39c12", "#9b59b6", "#1abc9c", "#e74c3c"]
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), height=400)
    st.plotly_chart(fig, use_container_width=True)
'''

with open('pages/login.py', 'w', encoding='utf-8') as f:
    f.write(login_content)

with open('pages/register.py', 'w', encoding='utf-8') as f:
    f.write(register_content)

with open('pages/patient.py', 'w', encoding='utf-8') as f:
    f.write(patient_content)

with open('pages/clinic.py', 'w', encoding='utf-8') as f:
    f.write(clinic_content)

with open('pages/admin.py', 'w', encoding='utf-8') as f:
    f.write(admin_content)

print("Rewrite complete.")
