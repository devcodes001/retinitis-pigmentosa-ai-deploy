import streamlit as st
import pandas as pd
from datetime import datetime
import utils, db
import plotly.graph_objects as go

st.set_page_config(page_title="RPeyecare | Admin", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()

if st.session_state.get('role') != 'admin':
    st.switch_page('pages/login.py')

utils.render_navbar(show_dash_links=True, role='admin', username='Administrator')

if 'admin_page' not in st.session_state:
    st.session_state['admin_page'] = 'Overview'

col_nav, col_main = st.columns([1, 4])

with col_nav:
    st.markdown('<div class="dash-sidebar">', unsafe_allow_html=True)
    st.markdown('<div class="snav-section">MENU</div>', unsafe_allow_html=True)
    
    pages = ["🏠 Overview", "⏳ Clinic Approval", "✅ Active Clinics", "👥 Users", "📊 Analytics"]
    for p in pages:
        is_active = p.split(" ", 1)[1] == st.session_state['admin_page']
        cls = "snav-active" if is_active else "snav-item"
        if st.button(p, key=f"nav_{p}", use_container_width=True):
            st.session_state['admin_page'] = p.split(" ", 1)[1]
            st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_main:
    st.markdown("""
    <div class="dash-hdr" style="border-radius:15px; margin-bottom:2rem;">
      <div>
        <div class="dash-title">🛡️ Admin Dashboard</div>
        <div class="dash-sub">System Management & Analytics</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    stats = db.get_stats()

    if st.session_state['admin_page'] == "Overview":
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="mcard"><div class="mval" style="color:#2563eb;">{stats["total_users"]}</div><div class="mlbl">Registered Patients</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="mcard"><div class="mval" style="color:#059669;">{stats["total_clinics"]}</div><div class="mlbl">Active Verified Clinics</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="mcard"><div class="mval" style="color:#d97706;">{stats["pending_clinics"]}</div><div class="mlbl">Pending Approvals</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        c4, c5, c6 = st.columns(3)
        c4.markdown(f'<div class="mcard"><div class="mval" style="color:#0ea5e9;">{stats["total_detections"]}</div><div class="mlbl">Total AI Screenings</div></div>', unsafe_allow_html=True)
        c5.markdown(f'<div class="mcard"><div class="mval" style="color:#7c3aed;">{stats["total_bookings"]}</div><div class="mlbl">Clinic Consultations</div></div>', unsafe_allow_html=True)
        c6.markdown(f'<div class="mcard"><div class="mval" style="color:#dc2626;">{stats["high_risk"]}</div><div class="mlbl">High Risk Detections</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("🟢 System Operational — ResNet-50 inference engine and SQLite database connected.")
            
    elif st.session_state['admin_page'] == "Clinic Approval":
        st.markdown("### ⏳ Pending Clinic Verifications")
        pending = [c for c in db.get_all_clinics(False) if not c["approved"]]
        if not pending:
            st.success("✅ All clinic registration applications have been reviewed.")
        else:
            for c in pending:
                with st.expander(f"Pending Application: {c['clinic_name']} — Dr. {c['doctor_name']}", expanded=True):
                    st.markdown(f"""
                    <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:1.2rem; margin-bottom:1rem; font-size:0.92rem; line-height:1.8;">
                        <b>🔬 Specialization:</b> {c['specialization']} &nbsp;|&nbsp; <b>Medical Reg:</b> <code>{c['reg_number']}</code><br>
                        <b>✉️ Email:</b> {c['email']} &nbsp;|&nbsp; <b>📞 Phone:</b> {c['phone']}<br>
                        <b>📍 Location:</b> {c['address']}, {c['city']}, {c['state']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, _ = st.columns([1.5, 1, 3])
                    if col1.button("✅ Approve & Activate Clinic", key=f"ap_{c['id']}", type="primary"):
                        db.approve_clinic(c["id"])
                        st.toast(f"Approved {c['clinic_name']}")
                        st.rerun()
                    if col2.button("❌ Reject", key=f"rj_{c['id']}"):
                        db.reject_clinic(c["id"])
                        st.toast(f"Rejected {c['clinic_name']}")
                        st.rerun()
                        
    elif st.session_state['admin_page'] == "Active Clinics":
        st.markdown("### 🏥 Verified Clinic Network")
        active = [c for c in db.get_all_clinics(True)]
        if not active:
            st.info("ℹ️ No active clinics currently verified.")
        else:
            for c in active:
                st.markdown(f"""
                <div class="card" style="margin-bottom:0.8rem; padding:1.2rem 1.5rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:700; color:#0f172a; font-size:1.05rem;">{c['clinic_name']}</div>
                            <div style="color:#64748b; font-size:0.88rem; margin-top:0.2rem;">
                                👨‍⚕️ Dr. {c['doctor_name']} ({c['specialization']}) &nbsp;|&nbsp; 📍 {c['city']}, {c['state']} &nbsp;|&nbsp; 📞 {c['phone']}
                            </div>
                        </div>
                        <span class="rb-low rbadge">Active Partner</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
    elif st.session_state['admin_page'] == "Users":
        st.markdown("### 👥 Patient Accounts Directory")
        users = db.get_all_users()
        if not users:
            st.info("ℹ️ No registered patient accounts found.")
        else:
            c1, c2 = st.columns([3, 1.2], gap="medium")
            with c1:
                df = pd.DataFrame(users)
                st.dataframe(df, use_container_width=True, hide_index=True)
            with c2:
                with st.form("delete_user_form"):
                    st.markdown("<b>Account Actions</b>", unsafe_allow_html=True)
                    del_id = st.number_input("Enter User ID to Remove", min_value=1, step=1)
                    if st.form_submit_button("🗑️ Delete Account", type="primary", use_container_width=True):
                        db.delete_user(del_id)
                        st.toast(f"User #{del_id} removed.")
                        st.rerun()
                
    elif st.session_state['admin_page'] == "Analytics":
        st.markdown("### 📊 Platform Metrics & Screening Distribution")
        fig = go.Figure(go.Bar(
            x=["Patients", "Active Clinics", "Pending Clinics", "Total Scans", "Bookings", "High Risk Scans"],
            y=[stats["total_users"], stats["total_clinics"], stats["pending_clinics"],
               stats["total_detections"], stats["total_bookings"], stats["high_risk"]],
            marker_color=["#2563eb", "#10b981", "#f59e0b", "#0ea5e9", "#7c3aed", "#ef4444"],
            text=[stats["total_users"], stats["total_clinics"], stats["pending_clinics"],
                  stats["total_detections"], stats["total_bookings"], stats["high_risk"]],
            textposition="outside",
            textfont=dict(color="#0f172a", family="Plus Jakarta Sans", size=13)
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#0f172a", family="Plus Jakarta Sans"),
            yaxis=dict(gridcolor="#e2e8f0"),
            xaxis=dict(gridcolor="#e2e8f0"),
            height=380,
            margin=dict(t=20, b=10, l=10, r=10),
            bargap=0.45
        )
        st.plotly_chart(fig, use_container_width=True)

