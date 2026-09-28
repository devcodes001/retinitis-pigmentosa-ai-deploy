import streamlit as st
import utils, db
import re

st.set_page_config(page_title="RPeyecare | Register", page_icon="👁️", layout="centered", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()
utils.render_navbar()

st.markdown("""
<div style="text-align:center; margin: 1rem 0 1.5rem;">
    <h2 style="font-size:2rem; font-weight:800; color:#0f172a; letter-spacing:-0.5px; margin-bottom:0.3rem;">
        Join RPeyecare Network
    </h2>
    <p style="color:#64748b; font-size:0.95rem;">
        Select your registration category below to get started
    </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["👤 Patient Registration", "🏥 Clinic / Doctor Registration"])

with tab1:
    st.markdown("""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:2rem; box-shadow:0 4px 20px rgba(15,23,42,0.04); margin-top:1rem;">
        <h3 style="font-size:1.3rem; font-weight:700; color:#0f172a; margin-bottom:0.4rem;">Patient Account</h3>
        <p style="color:#64748b; font-size:0.88rem; margin-bottom:1.5rem;">Upload retinal images and track your diagnostic history.</p>
    """, unsafe_allow_html=True)
    
    with st.form("reg_user"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Full Name *", placeholder="Jane Doe")
        email = c2.text_input("Email Address *", placeholder="jane@example.com").strip()
        pw = c1.text_input("Password *", type="password", placeholder="Min 6 characters")
        pw2 = c2.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
        phone = c1.text_input("Phone Number *", placeholder="10-digit mobile number")
        city = c2.text_input("City *", placeholder="e.g. New Delhi")
        state = c1.text_input("State *", placeholder="e.g. Delhi")
        addr = st.text_area("Full Address (Optional)", placeholder="Street address, apartment or area...")
        sub = st.form_submit_button("Create Patient Account ✨", use_container_width=True, type="primary")
        
        if sub:
            if not all([name, email, pw, phone, city, state]):
                st.error("⚠️ Please fill in all required fields marked with an asterisk (*).")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("⚠️ Please enter a valid email address.")
            elif not phone.isdigit() or len(phone) < 10:
                st.error("⚠️ Phone number must contain at least 10 numeric digits.")
            elif pw != pw2:
                st.error("⚠️ Passwords do not match.")
            elif len(pw) < 6:
                st.error("⚠️ Password must be at least 6 characters long.")
            else:
                ok, msg = db.register_user(name, email, pw, phone, city, state, addr)
                if ok:
                    st.success(f"🎉 {msg} You can now log in.")
                else:
                    st.error(f"❌ {msg}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        st.markdown("<div style='padding-top:0.6rem;color:#64748b;font-size:0.9rem;'>Already have an account?</div>", unsafe_allow_html=True)
    with col_l2:
        if st.button("Sign In 🔑", key="login_p", use_container_width=True):
            st.switch_page("pages/login.py")

with tab2:
    st.markdown("""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:2rem; box-shadow:0 4px 20px rgba(15,23,42,0.04); margin-top:1rem;">
        <h3 style="font-size:1.3rem; font-weight:700; color:#0f172a; margin-bottom:0.4rem;">Clinic & Ophthalmologist Portal</h3>
        <p style="color:#64748b; font-size:0.88rem; margin-bottom:1.5rem;">Join as a verified clinical partner to receive patient referrals.</p>
    """, unsafe_allow_html=True)
    
    with st.form("reg_clinic"):
        c1, c2 = st.columns(2)
        cname = c1.text_input("Clinic / Hospital Name *", placeholder="Vision Care Center")
        dname = c2.text_input("Head Doctor's Name *", placeholder="Dr. Sarah Jenkins")
        email = c1.text_input("Work Email *", placeholder="clinic@visioncare.com").strip()
        phone = c2.text_input("Contact Phone *", placeholder="10-digit clinic number")
        pw = c1.text_input("Password *", type="password", placeholder="Min 6 characters")
        pw2 = c2.text_input("Confirm Password *", type="password", placeholder="Re-enter password")
        city = c1.text_input("City *", placeholder="e.g. Mumbai")
        state = c2.text_input("State *", placeholder="e.g. Maharashtra")
        spec = c1.selectbox("Specialization *", ["Ophthalmology", "Retinal Surgery", "Neuro-Ophthalmology", "Low Vision Care", "General Eye Care"])
        regn = c2.text_input("Medical Registration No. *", placeholder="e.g. MED-84920")
        addr = st.text_area("Full Clinic Address *", placeholder="Street, Landmark, City, State, PIN")
        sub_c = st.form_submit_button("Submit Clinic for Verification 🏥", use_container_width=True, type="primary")
        
        if sub_c:
            if not all([cname, dname, email, phone, pw, city, state, addr, regn]):
                st.error("⚠️ Please fill in all required fields.")
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("⚠️ Please enter a valid email address.")
            elif not phone.isdigit() or len(phone) < 10:
                st.error("⚠️ Phone number must contain at least 10 digits.")
            elif pw != pw2:
                st.error("⚠️ Passwords do not match.")
            elif len(pw) < 6:
                st.error("⚠️ Password must be at least 6 characters.")
            else:
                ok, msg = db.register_clinic(cname, dname, email, pw, phone, city, state, addr, spec, regn)
                if ok:
                    st.success(f"🎉 {msg}")
                else:
                    st.error(f"❌ {msg}")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col_cl1, col_cl2 = st.columns([2, 1])
    with col_cl1:
        st.markdown("<div style='padding-top:0.6rem;color:#64748b;font-size:0.9rem;'>Already registered your clinic?</div>", unsafe_allow_html=True)
    with col_cl2:
        if st.button("Clinic Login 🏥", key="login_c", use_container_width=True):
            st.switch_page("pages/login.py")

