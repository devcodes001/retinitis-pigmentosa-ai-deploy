"""utils.py — Shared CSS, helpers, auth guards for RPeyecare Portal"""
import streamlit as st
import base64
from pathlib import Path

# ── Image helper ──────────────────────────────────────────────────────
def img_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

IMAGES = Path("images")

def get_retinal_b64(prefix, indices):
    out = []
    for i in indices:
        p = IMAGES / f"{prefix}_{i}.png"
        if p.exists():
            out.append(img_b64(p))
    return out

# ── Auth guards ───────────────────────────────────────────────────────
def require_auth(role):
    if st.session_state.get("role") != role:
        st.switch_page("app.py")

def init_session():
    for k, v in {"role": None, "user": None}.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── GLOBAL CSS ────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,600&display=swap');

:root {
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --primary-light: #eff6ff;
    --primary-glow: rgba(37, 99, 235, 0.18);
    --secondary: #0ea5e9;
    --bg-page: #f8fafc;
    --bg-surface: #ffffff;
    --border-color: #e2e8f0;
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --success: #10b981;
    --success-bg: #ecfdf5;
    --warning: #f59e0b;
    --warning-bg: #fffbeb;
    --danger: #ef4444;
    --danger-bg: #fef2f2;
}

*, html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
}

#MainMenu, footer, header { visibility: hidden; height: 0 !important; }
.block-container {
    padding: 1.2rem 2.5rem 3rem !important;
    max-width: 1400px !important;
    margin: 0 auto !important;
}
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebar"]    { display: none !important; }

/* Background & Body */
.stApp {
    background-color: var(--bg-page);
    background-image: 
        radial-gradient(at 10% 10%, rgba(37, 99, 235, 0.05) 0px, transparent 50%),
        radial-gradient(at 90% 15%, rgba(14, 165, 233, 0.06) 0px, transparent 50%),
        radial-gradient(at 50% 90%, rgba(37, 99, 235, 0.04) 0px, transparent 50%);
    background-attachment: fixed;
}

/* Animations */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes floatSlow {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-8px); }
}
@keyframes pulseSubtle {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.02); opacity: 0.95; }
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }

/* Enhanced Navbar */
.top-nav-bar {
    background: rgba(255, 255, 255, 0.88);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid rgba(226, 232, 240, 0.8);
    border-radius: 16px;
    padding: 0.8rem 1.6rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04);
}
.nav-logo-group {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.nav-logo-icon {
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #2563eb, #0ea5e9);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.25rem;
    color: white;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}
.nav-brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
}
.nav-brand-title span {
    background: linear-gradient(135deg, #2563eb, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nav-badge-pill {
    background: #eff6ff;
    color: #2563eb;
    border: 1px solid #dbeafe;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}
.nav-badge-live {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    display: inline-block;
    box-shadow: 0 0 0 2px #d1fae5;
}

/* Streamlit Buttons Global Polish */
div.stButton > button {
    border-radius: 11px !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
    border: 1px solid #cbd5e1 !important;
    background: #ffffff !important;
    color: #1e293b !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
}
div.stButton > button:hover {
    border-color: #3b82f6 !important;
    color: #2563eb !important;
    background: #eff6ff !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.12) !important;
}
div.stButton > button:active {
    transform: translateY(0px) scale(0.98) !important;
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    color: #ffffff !important;
    border: 1px solid #1d4ed8 !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.28) !important;
}
div.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #1d4ed8, #1e40af) !important;
    color: #ffffff !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.38) !important;
    transform: translateY(-2px) !important;
}

/* Modern Form Inputs */
.stTextInput input, .stSelectbox [data-baseweb="select"], .stTextArea textarea {
    border-radius: 11px !important;
    border: 1.5px solid #e2e8f0 !important;
    padding: 0.65rem 0.9rem !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-size: 0.95rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.14) !important;
    outline: none !important;
}

/* Modern Cards */
.card, .portal-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    padding: 1.8rem;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    overflow: hidden;
    height: 100%;
}
.card:hover, .portal-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 18px 36px -4px rgba(37, 99, 235, 0.12);
    border-color: #93c5fd;
}
.c-icon {
    font-size: 2.2rem;
    margin-bottom: 0.8rem;
    display: inline-block;
}
.c-title {
    color: #0f172a;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.3px;
}
.c-desc {
    color: #64748b;
    font-size: 0.92rem;
    line-height: 1.65;
}

/* Metric Cards */
.mcard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
    transition: all 0.25s ease;
    height: 100%;
}
.mcard:hover {
    border-color: #93c5fd;
    transform: translateY(-3px);
    box-shadow: 0 10px 25px -3px rgba(37, 99, 235, 0.1);
}
.mval {
    font-size: 2.2rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -0.5px;
}
.mlbl {
    color: #64748b;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 0.4rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Dashboard Header */
.dash-hdr {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border-radius: 18px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.8rem;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.18);
}
.dash-title {
    font-size: 1.65rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.dash-sub {
    color: #94a3b8;
    font-size: 0.95rem;
    margin-top: 0.3rem;
}

/* Sidebar navigation inside dashboard */
.dash-sidebar {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 1.2rem 0.8rem;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
}
.snav-section {
    color: #94a3b8;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.5rem 0.8rem;
    margin-top: 0.4rem;
}

/* Risk Badges */
.rb-high {
    background: #fef2f2 !important;
    color: #dc2626 !important;
    border: 1px solid #fecaca !important;
}
.rb-medium {
    background: #fffbeb !important;
    color: #d97706 !important;
    border: 1px solid #fde68a !important;
}
.rb-low {
    background: #ecfdf5 !important;
    color: #059669 !important;
    border: 1px solid #a7f3d0 !important;
}
.rbadge {
    padding: 0.3rem 0.85rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.5px;
}

/* Screening Result Card */
.res-normal {
    background: linear-gradient(135deg, #ecfdf5, #f0fdf4);
    border: 2px solid #10b981;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 8px 30px rgba(16, 185, 129, 0.12);
    animation: fadeUp 0.45s ease;
}
.res-disease {
    background: linear-gradient(135deg, #fef2f2, #fff1f2);
    border: 2px solid #ef4444;
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 8px 30px rgba(239, 68, 68, 0.12);
    animation: fadeUp 0.45s ease;
}
.res-label {
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.res-normal .res-label { color: #047857; }
.res-disease .res-label { color: #b91c1c; }
.res-sub {
    color: #475569;
    font-size: 1rem;
    margin-top: 0.5rem;
    font-weight: 500;
}

/* Urgent Alert */
.urgent {
    background: linear-gradient(135deg, #fef2f2, #fee2e2);
    border: 1.5px solid #ef4444;
    border-radius: 16px;
    padding: 1.4rem;
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.12);
}

/* Clinic Cards */
.clcard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    transition: all 0.25s ease;
    margin-bottom: 0.8rem;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}
.clcard:hover {
    transform: translateY(-3px);
    border-color: #93c5fd;
    box-shadow: 0 10px 24px -2px rgba(37, 99, 235, 0.1);
}
.clcard-name {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.3rem;
}
.clcard-detail {
    color: #64748b;
    font-size: 0.88rem;
    line-height: 1.7;
}

/* Modern Auth Form Box */
.auth-box {
    max-width: 520px;
    margin: 1.5rem auto 2rem;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 22px;
    padding: 2.2rem 2.4rem;
    box-shadow: 0 12px 40px -4px rgba(15, 23, 42, 0.08);
    animation: fadeUp 0.5s ease;
}
.auth-title {
    font-size: 1.9rem;
    font-weight: 800;
    color: #0f172a;
    text-align: center;
    letter-spacing: -0.5px;
    margin-bottom: 0.4rem;
}
.auth-sub {
    color: #64748b;
    font-size: 0.95rem;
    text-align: center;
    margin-bottom: 1.8rem;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9;
    border-radius: 14px;
    padding: 5px;
    border: 1px solid #e2e8f0;
    gap: 6px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 8px 20px;
    font-weight: 600;
    color: #64748b;
    font-size: 0.9rem;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #2563eb !important;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.06) !important;
}

/* Image preview containers */
.preview-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 0.8rem;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
    text-align: center;
}
</style>
"""

def render_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_navbar(show_dash_links=False, role=None, username=None):
    if show_dash_links and role:
        icon = {"user": "👤", "clinic": "🏥", "admin": "🛡️"}.get(role, "👤")
        page_name = {"user": "Patient", "clinic": "Clinic Portal", "admin": "System Admin"}.get(role, "Portal")
        
        col_brand, col_user, col_btn = st.columns([6, 3, 1.2])
        with col_brand:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:0.75rem;padding:0.4rem 0;">
                <div class="nav-logo-icon">👁️</div>
                <div>
                    <div class="nav-brand-title">RP<span>eyecare</span></div>
                    <div style="color:#64748b;font-size:0.78rem;font-weight:500;">{page_name}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_user:
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;align-items:center;height:100%;padding:0.4rem 0;">
                <div class="nav-badge-pill">
                    <span class="nav-badge-live"></span>
                    <span>{icon} {username}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if st.button("🚪 Logout", key="nav_logout_btn", use_container_width=True):
                st.session_state.update({"role": None, "user": None, "screening_result": None})
                st.switch_page("app.py")
        st.markdown("<hr style='margin:0.2rem 0 1.4rem;border:none;border-bottom:1px solid #e2e8f0;'/>", unsafe_allow_html=True)
    else:
        col_brand, col_actions = st.columns([7, 3])
        with col_brand:
            st.markdown("""
            <div style="display:flex;align-items:center;gap:0.75rem;padding:0.4rem 0;">
                <div class="nav-logo-icon">👁️</div>
                <div>
                    <div class="nav-brand-title">RP<span>eyecare</span></div>
                    <div style="color:#64748b;font-size:0.78rem;font-weight:500;">AI Retinal Disease Intelligence</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_actions:
            b1, b2 = st.columns(2)
            with b1:
                if st.button("🔑 Sign In", key="nav_signin_btn", use_container_width=True):
                    st.switch_page("pages/login.py")
            with b2:
                if st.button("✨ Register", key="nav_reg_btn", type="primary", use_container_width=True):
                    st.switch_page("pages/register.py")
        st.markdown("<hr style='margin:0.2rem 0 1.4rem;border:none;border-bottom:1px solid #e2e8f0;'/>", unsafe_allow_html=True)

