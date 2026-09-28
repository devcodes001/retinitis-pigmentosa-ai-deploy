import streamlit as st
from datetime import datetime
import utils, db
import plotly.graph_objects as go

st.set_page_config(page_title="RPeyecare | Clinic Portal", page_icon="🏥", layout="wide", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()

if st.session_state.get('role') != 'clinic':
    st.switch_page('pages/login.py')

cl = st.session_state.user
utils.render_navbar(show_dash_links=True, role='clinic', username=cl['clinic_name'])

if 'clinic_page' not in st.session_state:
    st.session_state['clinic_page'] = 'Dashboard'

col_nav, col_main = st.columns([1, 4])

with col_nav:
    st.markdown('<div class="dash-sidebar">', unsafe_allow_html=True)
    st.markdown('<div class="snav-section">MENU</div>', unsafe_allow_html=True)
    
    pages = ["🏠 Dashboard", "📅 Appointments", "⚠️ High Risk Patients", "🏥 Clinic Profile"]
    for p in pages:
        is_active = p.split(" ", 1)[1] == st.session_state['clinic_page']
        cls = "snav-active" if is_active else "snav-item"
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state['clinic_page'] = p.split(" ", 1)[1]
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)


with col_main:
    st.markdown(f"""
    <div class="dash-hdr" style="border-radius:15px; margin-bottom:2rem;">
      <div>
        <div class="dash-title">🏥 Clinic Dashboard</div>
        <div class="dash-sub">{cl['clinic_name']} · Dr. {cl['doctor_name']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    bookings = db.get_clinic_bookings(cl["id"])

    if st.session_state['clinic_page'] == "Dashboard":
        pending = sum(1 for b in bookings if b["status"] == "pending")
        confirmed = sum(1 for b in bookings if b["status"] == "confirmed")
        high = sum(1 for b in bookings if b.get("risk_level") == "HIGH")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="mcard"><div class="mval" style="color:#2563eb;">{len(bookings)}</div><div class="mlbl">Total Appointments</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="mcard"><div class="mval" style="color:#d97706;">{pending}</div><div class="mlbl">Pending Confirmation</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="mcard"><div class="mval" style="color:#059669;">{confirmed}</div><div class="mlbl">Confirmed</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="mcard"><div class="mval" style="color:#dc2626;">{high}</div><div class="mlbl">High Risk Scans</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>### 📊 Appointment Status Overview", unsafe_allow_html=True)
        fig = go.Figure(go.Bar(
            x=["Pending", "Confirmed", "Cancelled"],
            y=[pending, confirmed, sum(1 for b in bookings if b["status"] == "cancelled")],
            marker_color=["#f59e0b", "#10b981", "#ef4444"],
            text=[pending, confirmed, sum(1 for b in bookings if b["status"] == "cancelled")],
            textposition="outside",
            textfont=dict(color="#0f172a", family="Plus Jakarta Sans", size=13)
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#0f172a", family="Plus Jakarta Sans"),
            yaxis=dict(gridcolor="#e2e8f0"),
            xaxis=dict(gridcolor="#e2e8f0"),
            height=280,
            margin=dict(t=20, b=10, l=10, r=10),
            bargap=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
        
    elif st.session_state['clinic_page'] == "Appointments":
        c1, c2 = st.columns([1.5, 3])
        with c1:
            filter_status = st.selectbox("Filter Status", ["All", "Pending", "Confirmed", "Cancelled"], label_visibility="collapsed")
        st.markdown("---")
        
        filtered = [b for b in bookings if filter_status == "All" or b["status"].lower() == filter_status.lower()]
        if not filtered:
            st.info(f"ℹ️ No appointments found with status: **{filter_status}**.")
        else:
            for b in filtered:
                risk = b.get("risk_level", "N/A")
                badge_cls = "rb-high" if risk == "HIGH" else ("rb-medium" if risk == "MEDIUM" else "rb-low")
                rb = f'<span class="{badge_cls} rbadge">{risk} RISK</span>'
                
                with st.expander(f"👤 {b['user_name']} — {b['timestamp']} — [{b['status'].upper()}]", expanded=(b["status"]=="pending")):
                    st.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1rem; margin-bottom:1rem;">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; font-size:0.9rem;">
                            <div><b>📞 Contact:</b> {b['user_phone']}</div>
                            <div><b>📍 City:</b> {b['user_city']}</div>
                            <div><b>🔬 AI Diagnosis:</b> {b.get('result', 'N/A')}</div>
                            <div><b>⚠️ Clinical Risk:</b> {rb}</div>
                        </div>
                        <div style="margin-top:0.6rem; padding-top:0.6rem; border-top:1px solid #e2e8f0; font-size:0.88rem; color:#475569;">
                            <b>Notes from Patient:</b> {b.get('notes', 'No notes provided')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, _ = st.columns([1.3, 1, 3])
                    if b["status"] != "confirmed":
                        if col1.button("✅ Confirm Consultation", key=f"con_{b['id']}", type="primary"):
                            db.update_booking_status(b["id"], "confirmed")
                            st.toast(f"Confirmed appointment for {b['user_name']}")
                            st.rerun()
                    if b["status"] != "cancelled":
                        if col2.button("❌ Reject", key=f"can_{b['id']}"):
                            db.update_booking_status(b["id"], "cancelled")
                            st.toast(f"Cancelled appointment for {b['user_name']}")
                            st.rerun()
                        
    elif st.session_state['clinic_page'] == "High Risk Patients":
        st.markdown("### ⚠️ Priority Ophthalmic Attention Queue")
        st.markdown("<p style='color:#64748b;font-size:0.9rem;margin-top:-0.5rem;'>Patients whose AI screenings exhibited acute retinitis pigmentosa pathology.</p>", unsafe_allow_html=True)
        high_risk = [b for b in bookings if b.get("risk_level") == "HIGH"]
        if not high_risk:
            st.success("✅ No critical high-risk patients currently waiting in queue.")
        else:
            for b in high_risk:
                st.markdown(f"""
                <div class="urgent" style="margin-bottom:1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <h4 style="color:#dc2626; margin:0; font-size:1.1rem;">👤 {b['user_name']}</h4>
                        <span class="rb-high rbadge">Status: {b['status'].upper()}</span>
                    </div>
                    <p style="margin:0.5rem 0 0; color:#7f1d1d; font-size:0.92rem;">
                        📞 <b>Phone:</b> {b['user_phone']} &nbsp;|&nbsp; 📍 <b>City:</b> {b['user_city']} &nbsp;|&nbsp; 📅 <b>Booked:</b> {b['timestamp']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
                    
    elif st.session_state['clinic_page'] == "Clinic Profile":
        st.markdown("### 🏥 Practice & Accreditation Profile")
        status_badge = '<span class="rb-low rbadge">Verified Partner</span>' if cl['approved'] else '<span class="rb-medium rbadge">Pending Verification</span>'
        st.markdown(f"""
        <div class="card" style="max-width:700px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                <div class="c-title" style="margin:0;">{cl['clinic_name']}</div>
                {status_badge}
            </div>
            <div style="font-size:0.95rem; line-height:1.9; color:#334155;">
                <b>👨‍⚕️ Lead Doctor:</b> Dr. {cl['doctor_name']}<br>
                <b>🔬 Specialization:</b> {cl['specialization']}<br>
                <b>📍 Clinic Address:</b> {cl['address']}, {cl['city']}, {cl['state']}<br>
                <b>📞 Contact Phone:</b> {cl['phone']}<br>
                <b>📋 State Medical Registration:</b> <code>{cl['reg_number']}</code><br>
                <b>📅 Account Created:</b> {cl.get('created_at', '—')}
            </div>
        </div>
        """, unsafe_allow_html=True)

