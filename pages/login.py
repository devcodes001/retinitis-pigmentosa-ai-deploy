import streamlit as st
import utils
import db

st.set_page_config(page_title="RPeyecare | Login", page_icon="👁️", layout="centered", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()

# Redirect if already logged in
session_role = st.session_state.get("role")
if session_role == "user":    st.switch_page("pages/patient.py")
elif session_role == "clinic": st.switch_page("pages/clinic.py")
elif session_role == "admin":  st.switch_page("pages/admin.py")

utils.render_navbar()

st.markdown("""
<div class="auth-box">
  <div class="nav-logo-icon" style="margin: 0 auto 0.8rem; width:44px; height:44px; font-size:1.3rem;">👁️</div>
  <div class="auth-title">Welcome Back</div>
  <div class="auth-sub">Select your account role and sign in to proceed</div>
</div>
""", unsafe_allow_html=True)

with st.form("login_form"):
    role_choice = st.radio(
        "Account Type", 
        ["👤 Patient", "🏥 Clinic Doctor", "🛡️ Administrator"], 
        horizontal=True,
        help="Select the role associated with your account"
    )
    email = st.text_input("Email Address", placeholder="e.g. yourname@domain.com")
    password = st.text_input("Password", type="password", placeholder="••••••••")
    submitted = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

if submitted:
    if not email or not password:
        st.error("⚠️ Please provide both your email address and password.")
    else:
        clean_email = email.strip()
        if "Administrator" in role_choice:
            u = db.login_admin(clean_email, password)
            if u:
                st.session_state.update({"role": "admin", "user": u})
                st.switch_page("pages/admin.py")
            else:
                st.error("❌ Invalid administrator credentials. (Demo: admin@retinaai.com / Admin@123)")
        elif "Patient" in role_choice:
            u, err = db.login_user(clean_email, password)
            if u:
                st.session_state.update({"role": "user", "user": u})
                st.switch_page("pages/patient.py")
            else:
                st.error(f"❌ {err}")
        elif "Clinic" in role_choice:
            u, err = db.login_clinic(clean_email, password)
            if u:
                st.session_state.update({"role": "clinic", "user": u})
                st.switch_page("pages/clinic.py")
            else:
                st.error(f"❌ {err}")

st.markdown("""
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:0.9rem 1.2rem; margin:1.2rem 0; font-size:0.85rem; color:#475569;">
    <b>💡 Demo Administrator Access:</b><br>
    Email: <code>admin@retinaai.com</code> &nbsp;|&nbsp; Password: <code>Admin@123</code>
</div>
""", unsafe_allow_html=True)

col_reg1, col_reg2 = st.columns([1.5, 1])
with col_reg1:
    st.markdown("<div style='padding-top:0.5rem;color:#64748b;font-size:0.9rem;'>Don't have an account yet?</div>", unsafe_allow_html=True)
with col_reg2:
    if st.button("Create Account ✨", use_container_width=True):
        st.switch_page("pages/register.py")

