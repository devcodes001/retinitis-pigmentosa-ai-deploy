"""app.py — Home / Landing Page"""
import streamlit as st
import base64
from pathlib import Path
from datetime import datetime
import utils, db

st.set_page_config(page_title="RPeyecare | Home", page_icon="👁️",
                   layout="wide", initial_sidebar_state="collapsed")
utils.init_session()
utils.render_css()

# Redirect if already logged in
role = st.session_state.get("role")
if role == "user":    st.switch_page("pages/patient.py")
elif role == "clinic": st.switch_page("pages/clinic.py")
elif role == "admin":  st.switch_page("pages/admin.py")

db.init_db()

# ── Load real retinal images ──
normal_imgs  = utils.get_retinal_b64("Normal",           list(range(6)))
disease_imgs = utils.get_retinal_b64("Retina_Pigmentosa",list(range(6)))
stats        = db.get_stats()

utils.render_navbar()

# ── Hero Section ──
col_hero_left, col_hero_right = st.columns([1.15, 0.85], gap="large")

with col_hero_left:
    st.markdown("""
    <div style="padding: 1.5rem 0 1rem; animation: fadeUp 0.6s ease;">
        <div style="display:inline-flex; align-items:center; gap:0.5rem; background:#eff6ff; border:1px solid #bfdbfe; color:#1d4ed8; padding:0.4rem 1rem; border-radius:9999px; font-size:0.82rem; font-weight:700; letter-spacing:0.8px; text-transform:uppercase; margin-bottom:1.2rem;">
            <span>🔬</span> Next-Gen Deep Learning Ophthalmology
        </div>
        <h1 style="font-size:3.2rem; font-weight:800; color:#0f172a; line-height:1.15; letter-spacing:-1.2px; margin-bottom:1.2rem;">
            Early Detection for <br>
            <span style="background:linear-gradient(135deg,#2563eb,#0ea5e9); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Retinitis Pigmentosa
            </span>
        </h1>
        <p style="color:#475569; font-size:1.1rem; line-height:1.75; margin-bottom:2rem; max-width:580px;">
            Harness transfer learning and deep neural networks to screen retinal fundus photographs in seconds. Empowering patients with early diagnostics, instant clinical PDF reports, and seamless ophthalmic referrals.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c_cta1, c_cta2, c_cta3 = st.columns([1.2, 1, 1])
    with c_cta1:
        if st.button("🚀 Start Screening", key="hero_patient_btn", type="primary", use_container_width=True):
            st.switch_page("pages/login.py")
    with c_cta2:
        if st.button("🏥 Clinic Portal", key="hero_clinic_btn", use_container_width=True):
            st.switch_page("pages/login.py")
    with c_cta3:
        if st.button("🛡️ Admin Console", key="hero_admin_btn", use_container_width=True):
            st.switch_page("pages/login.py")

with col_hero_right:
    normal_b64 = normal_imgs[0] if normal_imgs else ""
    disease_b64 = disease_imgs[0] if disease_imgs else ""
    
    st.markdown(f"""
    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:24px; padding:1.4rem; box-shadow:0 20px 45px -10px rgba(15,23,42,0.08); animation:floatSlow 5s ease-in-out infinite;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
            <div style="display:flex; align-items:center; gap:0.5rem;">
                <div style="width:10px; height:10px; border-radius:50%; background:#10b981;"></div>
                <span style="font-weight:700; font-size:0.85rem; color:#0f172a;">Live Retinal Benchmark</span>
            </div>
            <span class="rb-low rbadge">97.5% Accuracy</span>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.8rem;">
            <div style="border-radius:14px; overflow:hidden; border:1px solid #e2e8f0; background:#f8fafc;">
                <img src="data:image/png;base64,{normal_b64}" style="width:100%; height:160px; object-fit:cover; display:block;"/>
                <div style="padding:0.7rem; text-align:center; background:#ffffff; border-top:1px solid #e2e8f0;">
                    <span style="font-weight:700; font-size:0.8rem; color:#059669;">✔️ Normal Retina</span>
                </div>
            </div>
            <div style="border-radius:14px; overflow:hidden; border:1px solid #fecaca; background:#fff5f5;">
                <img src="data:image/png;base64,{disease_b64}" style="width:100%; height:160px; object-fit:cover; display:block;"/>
                <div style="padding:0.7rem; text-align:center; background:#ffffff; border-top:1px solid #fee2e2;">
                    <span style="font-weight:700; font-size:0.8rem; color:#dc2626;">⚠️ Retinitis Pigmentosa</span>
                </div>
            </div>
        </div>
        <div style="margin-top:1rem; padding:0.8rem 1rem; background:#f8fafc; border-radius:12px; border:1px solid #e2e8f0; display:flex; justify-content:space-between; align-items:center;">
            <span style="color:#64748b; font-size:0.82rem; font-weight:500;">Architecture: ResNet-50</span>
            <span style="color:#2563eb; font-size:0.82rem; font-weight:700;">Inference: &lt; 0.2s</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Metrics Banner ──
st.markdown(f"""
<div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; padding:1.8rem; box-shadow:0 4px 20px -2px rgba(15,23,42,0.04); display:grid; grid-template-columns:repeat(5, 1fr); gap:1rem; text-align:center;">
    <div style="border-right:1px solid #f1f5f9; padding:0.5rem;">
        <div class="mval" style="color:#2563eb;">97.5%</div>
        <div class="mlbl">AI Validation Accuracy</div>
    </div>
    <div style="border-right:1px solid #f1f5f9; padding:0.5rem;">
        <div class="mval">{stats['total_users']}</div>
        <div class="mlbl">Registered Patients</div>
    </div>
    <div style="border-right:1px solid #f1f5f9; padding:0.5rem;">
        <div class="mval">{stats['total_clinics']}</div>
        <div class="mlbl">Verified Clinics</div>
    </div>
    <div style="border-right:1px solid #f1f5f9; padding:0.5rem;">
        <div class="mval">{stats['total_detections']}</div>
        <div class="mlbl">Scans Analyzed</div>
    </div>
    <div style="padding:0.5rem;">
        <div class="mval" style="color:#0ea5e9;">&lt; 1s</div>
        <div class="mlbl">Report Generation</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Dedicated Portals Section ──
st.markdown("""
<div style="text-align:center; margin-bottom:2.2rem;">
    <div style="color:#2563eb; font-weight:700; letter-spacing:1px; text-transform:uppercase; font-size:0.85rem; margin-bottom:0.4rem;">
        Unified Healthcare Ecosystem
    </div>
    <h2 style="font-size:2.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.8px;">
        Three Purpose-Built Portals
    </h2>
    <p style="color:#64748b; font-size:1.05rem; max-width:650px; margin:0 auto;">
        Integrated workflows designed for patient autonomy, clinical collaboration, and strict administrative oversight.
    </p>
</div>
""", unsafe_allow_html=True)

p1, p2, p3 = st.columns(3, gap="medium")

portals = [
    (p1, "🧑‍⚕️", "Patient Portal", "#2563eb",
     "Self-service AI fundus screening, high-risk detection, instant clinical PDF downloads, and booking near your city.",
     ["Instant AI Screening", "PDF Medical Report", "Nearby Clinic Locator", "Scan History & Trends"]),
    (p2, "🏥", "Clinic Portal", "#059669",
     "Doctor dashboard to review AI risk assessments, examine patient scan histories, and confirm appointments.",
     ["Appointment Schedule", "High-Risk Alerts", "Patient Retinal Records", "Doctor Verification"]),
    (p3, "🛡️", "Admin Console", "#dc2626",
     "Governance and platform analytics. Review pending clinic registrations, monitor screening volumes, and audit logs.",
     ["Clinic Approvals", "User Management", "System Health Analytics", "High-Risk Oversight"])
]

for col, icon, title, color, desc, feats in portals:
    with col:
        feat_items = "".join(f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.45rem;color:#334155;font-size:0.88rem;font-weight:500;"><span style="color:{color};font-weight:700;">✓</span> {f}</div>' for f in feats)
        st.markdown(f"""
        <div class="card" style="border-top: 4px solid {color}; padding:2rem 1.6rem 1.6rem;">
            <div style="font-size:2.5rem; margin-bottom:0.8rem;">{icon}</div>
            <div class="c-title" style="color:#0f172a;">{title}</div>
            <p class="c-desc" style="margin-bottom:1.4rem; min-height:60px;">{desc}</p>
            <div style="border-top:1px solid #f1f5f9; padding-top:1.2rem; margin-bottom:1.5rem;">
                {feat_items}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Enter {title} →", key=f"portal_btn_{title}", use_container_width=True):
            st.switch_page("pages/login.py")

st.markdown("<br><br>", unsafe_allow_html=True)

# ── How It Works Section ──
st.markdown("""
<div style="text-align:center; margin-bottom:2.2rem;">
    <div style="color:#2563eb; font-weight:700; letter-spacing:1px; text-transform:uppercase; font-size:0.85rem; margin-bottom:0.4rem;">
        Simple 4-Step Journey
    </div>
    <h2 style="font-size:2.4rem; font-weight:800; color:#0f172a; letter-spacing:-0.8px;">
        How Retinal AI Screening Works
    </h2>
</div>
""", unsafe_allow_html=True)

s1, s2, s3, s4 = st.columns(4, gap="medium")
steps = [
    ("1", "📝", "Create Account", "Sign up in 30 seconds with your location details to enable customized clinic recommendations."),
    ("2", "📤", "Upload Fundus Scan", "Upload standard digital fundus image in JPG, PNG, or BMP with optional contrast enhancement."),
    ("3", "🧠", "Deep Learning Scan", "ResNet-50 evaluates vascular patterns, pigment deposits, and optic disc clarity."),
    ("4", "📑", "Clinical Report", "Download a clinical summary and instantly connect with verified ophthalmologists if at risk.")
]

for col, num, icon, heading, details in zip([s1, s2, s3, s4], *zip(*steps)):
    with col:
        st.markdown(f"""
        <div class="card" style="text-align:center; padding:1.8rem 1.2rem;">
            <div style="width:36px; height:36px; line-height:36px; border-radius:50%; background:#eff6ff; color:#2563eb; font-weight:800; margin:0 auto 0.8rem; font-size:0.9rem; border:1px solid #dbeafe;">
                {num}
            </div>
            <div style="font-size:2rem; margin-bottom:0.6rem;">{icon}</div>
            <div style="font-weight:700; color:#0f172a; font-size:1.05rem; margin-bottom:0.5rem;">{heading}</div>
            <div style="color:#64748b; font-size:0.88rem; line-height:1.6;">{details}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Retinal Image Sample Gallery ──
st.markdown("""
<div style="text-align:center; margin-bottom:1.8rem;">
    <h2 style="font-size:2.2rem; font-weight:800; color:#0f172a; letter-spacing:-0.6px;">
        🖼️ Sample Retinal Examination Gallery
    </h2>
    <p style="color:#64748b; font-size:0.95rem;">
        Representative fundus scans comparing healthy retinas against pathological Retinitis Pigmentosa features.
    </p>
</div>
""", unsafe_allow_html=True)

gc = st.columns(6, gap="small")
gallery = ([(b, "Healthy Retina", "Normal", "#059669") for b in normal_imgs[:3]] +
           [(b, "RP Degeneration", "Pathological", "#dc2626") for b in disease_imgs[:3]])

for col, (b64, lbl, sublbl, clr) in zip(gc, gallery[:6]):
    with col:
        st.markdown(f"""
        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; overflow:hidden; box-shadow:0 3px 12px rgba(15,23,42,0.04); transition:transform 0.2s ease;">
            <img src="data:image/png;base64,{b64}" style="width:100%; height:135px; object-fit:cover; display:block;"/>
            <div style="padding:0.75rem 0.6rem; text-align:center;">
                <div style="font-weight:700; font-size:0.82rem; color:{clr};">{lbl}</div>
                <div style="color:#94a3b8; font-size:0.72rem; margin-top:0.2rem; font-weight:600; text-transform:uppercase;">{sublbl}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Modern Footer ──
st.markdown(f"""
<div style="margin-top:3rem; padding:2.5rem 2rem 1.8rem; background:#ffffff; border:1px solid #e2e8f0; border-radius:20px; box-shadow:0 4px 18px rgba(15,23,42,0.03);">
    <div style="display:grid; grid-template-columns:2fr 1fr 1fr; gap:2.5rem; margin-bottom:2rem;">
        <div>
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.8rem;">
                <div class="nav-logo-icon" style="width:32px; height:32px; font-size:1.1rem;">👁️</div>
                <div class="nav-brand-title" style="font-size:1.25rem;">RP<span>eyecare</span></div>
            </div>
            <p style="color:#64748b; font-size:0.9rem; line-height:1.7; max-width:380px;">
                Advanced AI-assisted retinal screening system focused on early detection of Retinitis Pigmentosa and seamless clinical collaboration.
            </p>
        </div>
        <div>
            <div style="color:#0f172a; font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.8rem;">
                Platform Access
            </div>
            <div style="color:#64748b; font-size:0.88rem; line-height:2;">
                <div>• Patient Diagnostic Portal</div>
                <div>• Verified Clinic Network</div>
                <div>• Administrative Console</div>
            </div>
        </div>
        <div>
            <div style="color:#0f172a; font-size:0.85rem; font-weight:700; text-transform:uppercase; letter-spacing:1px; margin-bottom:0.8rem;">
                Framework & Stack
            </div>
            <div style="color:#64748b; font-size:0.88rem; line-height:2;">
                <div>• PyTorch &amp; ResNet-50</div>
                <div>• Streamlit Reactive UI</div>
                <div>• ReportLab PDF Engine</div>
            </div>
        </div>
    </div>
    <div style="border-top:1px solid #f1f5f9; padding-top:1.4rem; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
        <div style="color:#94a3b8; font-size:0.82rem;">
            &copy; {datetime.now().year} RPeyecare &middot; Medical AI Research Initiative
        </div>
        <div style="color:#94a3b8; font-size:0.8rem;">
            🔒 End-to-end encrypted password storage &middot; Research demonstration tool
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

