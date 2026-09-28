/**
 * RPeyecare — Complete Client-Side Logic (Vanilla JavaScript)
 * Features: AI Inference, Vision Simulator, SPA Router, Auth (Login+Register),
 *           Patient Dashboard (History/Bookings/Clinics), Clinic Portal,
 *           Admin Portal (Pending/All Clinics/Users), Toast Notifications
 */

// ── Application State ──────────────────────────────────────────────────
const state = {
  currentUser: JSON.parse(localStorage.getItem("rpeye_user")) || null,
  activeView: "home",
  selectedFile: null,
  selectedSample: null,
  currentResult: null,
  simImage: null,
  activePatientTab: "detections",
  activeAdminTab: "pending",
  activeRegTab: "patient"
};

// ── Toast Notification System ─────────────────────────────────────────
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  const bg = {
    success: "linear-gradient(135deg,#10b981,#059669)",
    error: "linear-gradient(135deg,#f43f5e,#dc2626)",
    info: "linear-gradient(135deg,#2563eb,#0ea5e9)",
    warning: "linear-gradient(135deg,#f59e0b,#d97706)"
  }[type] || "linear-gradient(135deg,#10b981,#059669)";

  toast.style.cssText = `
    background:${bg};color:#fff;padding:0.85rem 1.3rem;border-radius:12px;
    font-size:0.9rem;font-weight:600;font-family:'Plus Jakarta Sans',sans-serif;
    box-shadow:0 8px 24px rgba(0,0,0,0.35);max-width:340px;
    animation:slideInRight 0.35s cubic-bezier(0.16,1,0.3,1);
    display:flex;align-items:center;gap:0.6rem;
  `;
  const icons = { success: "✅", error: "❌", info: "ℹ️", warning: "⚠️" };
  toast.innerHTML = `<span>${icons[type] || "✅"}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "fadeOut 0.3s ease forwards";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Add toast animations to DOM
const style = document.createElement("style");
style.textContent = `
  @keyframes slideInRight { from{opacity:0;transform:translateX(40px)} to{opacity:1;transform:translateX(0)} }
  @keyframes fadeOut { from{opacity:1} to{opacity:0;transform:translateX(40px)} }
  .auth-tab-btn { flex:1;padding:0.55rem;border:none;background:transparent;color:var(--text-muted);cursor:pointer;border-radius:8px;font-family:inherit;font-weight:600;font-size:0.9rem;transition:all 0.2s; }
  .auth-tab-btn.active { background:var(--primary);color:#fff; }
  .patient-tab { transition:all 0.2s; }
  .patient-tab.active-tab, .admin-tab.active-tab { background:var(--primary) !important; color:#fff !important; }
  .ptab-panel, .atab-panel { animation:fadeIn 0.25s ease; }
  @keyframes fadeIn { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
`;
document.head.appendChild(style);

// ── DOM Ready Initialization ──────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  initRouter();
  initAuthUI();
  initScanner();
  initVisionSimulator();
  loadLiveStats();
  setupTabListeners();

  // Navigation Event Listeners
  document.querySelectorAll("[data-navigate]").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      navigateTo(btn.getAttribute("data-navigate"));
    });
  });
});

// ── SPA View Router ───────────────────────────────────────────────────
function navigateTo(viewId) {
  state.activeView = viewId;
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  const targetSection = document.getElementById(`view-${viewId}`);
  if (targetSection) {
    targetSection.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  document.querySelectorAll(".nav-item").forEach(link => {
    link.classList.toggle("active", link.getAttribute("data-navigate") === viewId);
  });

  if (viewId === "patient") loadPatientDashboard();
  if (viewId === "clinic")  loadClinicPortal();
  if (viewId === "admin")   loadAdminPortal();
}

function initRouter() {
  const hash = window.location.hash.replace("#", "");
  navigateTo(hash || "home");
}

// ── Tab Listeners ─────────────────────────────────────────────────────
function setupTabListeners() {
  // Patient tabs
  document.querySelectorAll(".patient-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-ptab");
      document.querySelectorAll(".patient-tab").forEach(b => b.classList.remove("active-tab"));
      document.querySelectorAll(".ptab-panel").forEach(p => p.style.display = "none");
      btn.classList.add("active-tab");
      document.getElementById(`ptab-${tab}`).style.display = "block";
      state.activePatientTab = tab;
      if (tab === "clinics") loadAllClinics();
      if (tab === "bookings") loadPatientBookings();
    });
  });

  // Admin tabs
  document.querySelectorAll(".admin-tab").forEach(btn => {
    btn.addEventListener("click", () => {
      const tab = btn.getAttribute("data-atab");
      document.querySelectorAll(".admin-tab").forEach(b => b.classList.remove("active-tab"));
      document.querySelectorAll(".atab-panel").forEach(p => p.style.display = "none");
      btn.classList.add("active-tab");
      document.getElementById(`atab-${tab}`).style.display = "block";
      state.activeAdminTab = tab;
      if (tab === "allclinics") loadAdminAllClinics();
      if (tab === "users") loadAdminUsers();
    });
  });
}

// ── Auth Tab Switching ────────────────────────────────────────────────
window.switchAuthTab = function(tab) {
  if (tab === "login") {
    document.getElementById("loginForm").style.display = "block";
    document.getElementById("registerForm").style.display = "none";
    document.getElementById("tabLoginBtn").classList.add("active");
    document.getElementById("tabRegisterBtn").classList.remove("active");
  } else {
    document.getElementById("loginForm").style.display = "none";
    document.getElementById("registerForm").style.display = "block";
    document.getElementById("tabLoginBtn").classList.remove("active");
    document.getElementById("tabRegisterBtn").classList.add("active");
  }
};

window.switchRegTab = function(tab) {
  state.activeRegTab = tab;
  if (tab === "patient") {
    document.getElementById("patientRegForm").style.display = "block";
    document.getElementById("clinicRegForm").style.display = "none";
    document.getElementById("regPatientBtn").classList.add("active");
    document.getElementById("regClinicBtn").classList.remove("active");
  } else {
    document.getElementById("patientRegForm").style.display = "none";
    document.getElementById("clinicRegForm").style.display = "block";
    document.getElementById("regPatientBtn").classList.remove("active");
    document.getElementById("regClinicBtn").classList.add("active");
  }
};

// ── Live Scanner & AI Inference ───────────────────────────────────────
function initScanner() {
  const dropzone = document.getElementById("scannerDropzone");
  const fileInput = document.getElementById("fundusFileInput");
  const previewImg = document.getElementById("liveScanPreview");
  const previewBox = document.getElementById("scannerCard");
  const scanBtn = document.getElementById("runAnalysisBtn");
  if (!dropzone) return;

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("drag-over"); });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("drag-over"));
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("drag-over");
    if (e.dataTransfer.files.length) handleSelectedFile(e.dataTransfer.files[0]);
  });
  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) handleSelectedFile(e.target.files[0]);
  });

  document.querySelectorAll(".sample-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      document.querySelectorAll(".sample-pill").forEach(p => p.style.outline = "none");
      pill.style.outline = "2px solid #38bdf8";
      state.selectedFile = null;
      state.selectedSample = pill.getAttribute("data-sample");
      previewImg.src = pill.getAttribute("data-img-url");
      document.getElementById("selectedScanName").textContent = `Selected: ${pill.textContent.trim()}`;
      scanBtn.disabled = false;
      document.getElementById("resultCard").classList.remove("active");
    });
  });

  function handleSelectedFile(file) {
    state.selectedFile = file;
    state.selectedSample = null;
    document.querySelectorAll(".sample-pill").forEach(p => p.style.outline = "none");
    const reader = new FileReader();
    reader.onload = (e) => {
      previewImg.src = e.target.result;
      document.getElementById("selectedScanName").textContent = `Uploaded: ${file.name}`;
      scanBtn.disabled = false;
      document.getElementById("resultCard").classList.remove("active");
    };
    reader.readAsDataURL(file);
  }

  scanBtn.addEventListener("click", async () => {
    if (!state.selectedFile && !state.selectedSample) return;
    previewBox.classList.add("scanning");
    scanBtn.disabled = true;
    scanBtn.innerHTML = `<span>⚡</span> Analyzing Vasculature &amp; Bone Spicules...`;

    const formData = new FormData();
    if (state.selectedFile) formData.append("file", state.selectedFile);
    else formData.append("sample", state.selectedSample);
    if (state.currentUser) formData.append("user_id", state.currentUser.id);
    formData.append("enhance", "true");

    try {
      const response = await fetch("/api/predict", { method: "POST", body: formData });
      const data = await response.json();
      setTimeout(() => {
        previewBox.classList.remove("scanning");
        scanBtn.disabled = false;
        scanBtn.innerHTML = `<span>🧠</span> Run Deep Learning Screening`;
        if (data.status === "success") {
          state.currentResult = data.result;
          renderScanResult(data.result);
        } else {
          showToast(`Analysis Error: ${data.message}`, "error");
        }
      }, 700);
    } catch (err) {
      previewBox.classList.remove("scanning");
      scanBtn.disabled = false;
      scanBtn.innerHTML = `<span>🧠</span> Run Deep Learning Screening`;
      showToast("Inference connection failed. Please ensure server is running.", "error");
    }
  });

  const reportBtn = document.getElementById("downloadReportBtn");
  if (reportBtn) {
    reportBtn.addEventListener("click", async () => {
      if (!state.currentResult) { showToast("Run a scan first before downloading a report.", "warning"); return; }
      const res = state.currentResult;
      reportBtn.innerHTML = `<span>⏳</span> Generating PDF...`;
      reportBtn.disabled = true;
      try {
        const response = await fetch("/api/generate_report", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            patient_name: state.currentUser ? (state.currentUser.name || "Guest Patient") : "Guest Patient",
            filename: res.filename,
            risk_level: res.risk_level,
            confidence: res.confidence,
            label: res.label,
            prob_disease: res.prob_disease,
            prob_normal: res.prob_normal,
            is_disease: res.is_disease
          })
        });
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `RPeyecare_Report_${(state.currentUser?.name || "Guest").replace(/\s+/g, "_")}.pdf`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast("Clinical PDF report downloaded successfully!", "success");
      } catch (e) {
        showToast("Failed to generate report. Please try again.", "error");
      }
      reportBtn.innerHTML = `<span>📑</span> Download Clinical PDF Report`;
      reportBtn.disabled = false;
    });
  }
}

function renderScanResult(res) {
  const resultCard = document.getElementById("resultCard");
  const badge = document.getElementById("resultBadge");
  const title = document.getElementById("resultTitle");
  const confText = document.getElementById("resultConfidence");
  const normalFill = document.getElementById("probNormalFill");
  const diseaseFill = document.getElementById("probDiseaseFill");
  const normalVal = document.getElementById("probNormalVal");
  const diseaseVal = document.getElementById("probDiseaseVal");
  const advisoryBox = document.getElementById("resultAdvisory");

  resultCard.classList.add("active");
  title.textContent = res.label;
  confText.textContent = `${res.confidence}% Model Certainty (ResNet-50) — ${res.latency_seconds}s latency`;

  badge.className = "result-badge";
  if (res.risk_level === "HIGH") {
    badge.classList.add("badge-high");
    badge.textContent = "High Risk Pathology";
  } else if (res.risk_level === "MEDIUM") {
    badge.classList.add("badge-high");
    badge.textContent = "Moderate Suspicion";
  } else {
    badge.classList.add("badge-low");
    badge.textContent = "Healthy Architecture";
  }

  // Animate bars
  normalVal.textContent = `${res.prob_normal}%`;
  diseaseVal.textContent = `${res.prob_disease}%`;
  normalFill.style.width = "0%";
  diseaseFill.style.width = "0%";
  setTimeout(() => {
    normalFill.style.transition = "width 1s ease";
    diseaseFill.style.transition = "width 1s ease";
    normalFill.style.width = `${res.prob_normal}%`;
    diseaseFill.style.width = `${res.prob_disease}%`;
  }, 50);

  if (res.is_disease) {
    advisoryBox.innerHTML = `
      <div style="background:rgba(244,63,94,0.12);border:1px solid rgba(244,63,94,0.3);border-radius:12px;padding:1rem;margin-top:1.2rem;">
        <b style="color:#fb7185;">⚠️ Clinical Recommendation:</b>
        <p style="color:#fda4af;font-size:0.88rem;margin-top:0.3rem;">Peripheral bone-spicule hyperpigmentation and vascular attenuation patterns were detected. Immediate in-person electroretinogram (ERG) and visual field testing is recommended.</p>
        <button class="btn btn-primary btn-sm" style="margin-top:0.6rem;" onclick="navigateTo('patient')">🏥 Find &amp; Book Nearby Clinic →</button>
      </div>`;
    showToast("⚠️ High-risk RP indicators detected!", "error");
  } else {
    advisoryBox.innerHTML = `
      <div style="background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:12px;padding:1rem;margin-top:1.2rem;">
        <b style="color:#34d399;">✔️ Normal Morphology:</b>
        <p style="color:#a7f3d0;font-size:0.88rem;margin-top:0.3rem;">No characteristic hallmarks of rod dystrophy or diffuse retinal pigmentation were detected. Routine annual eye checkups are advised.</p>
      </div>`;
    showToast("✔️ Healthy retina — no RP detected!", "success");
  }
}

// ── Interactive RP Vision Simulator (Canvas) ──────────────────────────
function initVisionSimulator() {
  const canvas = document.getElementById("visionCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  const slider = document.getElementById("rpSlider");
  const stageLabel = document.getElementById("simStageLabel");
  const stageDesc = document.getElementById("simStageDesc");

  const img = new Image();
  img.crossOrigin = "anonymous";
  img.src = "/static/samples/normal_1.png";
  img.onload = () => { state.simImage = img; drawSimulatedVision(0); };
  img.onerror = () => {
    // Fallback: draw a colored scene
    state.simImage = null;
    drawSimulatedVision(0);
  };

  slider.addEventListener("input", (e) => {
    drawSimulatedVision(parseInt(e.target.value));
  });

  function drawSimulatedVision(severity) {
    const w = canvas.width = 480;
    const h = canvas.height = 480;
    ctx.clearRect(0, 0, w, h);

    if (state.simImage) {
      ctx.drawImage(state.simImage, 0, 0, w, h);
    } else {
      // Fallback gradient scene
      const sceneGrad = ctx.createRadialGradient(w/2, h/2, 0, w/2, h/2, w/2);
      sceneGrad.addColorStop(0, "#38bdf8");
      sceneGrad.addColorStop(1, "#0f172a");
      ctx.fillStyle = sceneGrad;
      ctx.fillRect(0, 0, w, h);
    }

    const cx = w / 2, cy = h / 2;
    // clearRadius: 240px (full) -> 30px (pinhole)
    const clearRadius = Math.max(30, 240 - (severity * 2.1));
    const fadeRadius = clearRadius + 55;

    // Vignette gradient
    const grad = ctx.createRadialGradient(cx, cy, clearRadius * 0.7, cx, cy, fadeRadius);
    grad.addColorStop(0, "rgba(0,0,0,0)");
    grad.addColorStop(0.5, "rgba(0,0,0,0.6)");
    grad.addColorStop(1, "rgba(0,0,0,0.98)");

    // Fill entire canvas with vignette, then punch out clear central circle
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, 0, w, h);
    ctx.arc(cx, cy, fadeRadius, 0, Math.PI * 2, true); // hole
    ctx.fillStyle = "rgba(0,0,0,0.98)";
    ctx.fill("evenodd");
    ctx.restore();

    // Soft gradient ring
    ctx.save();
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, fadeRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Stage labels
    if (severity < 15) {
      stageLabel.textContent = "Stage 0: Unimpaired Retinal Vision";
      stageDesc.textContent = "Full 180° visual field with crisp peripheral detail and normal photoreceptor signaling.";
    } else if (severity < 40) {
      stageLabel.textContent = "Stage 1: Early Nyctalopia & Peripheral Fading";
      stageDesc.textContent = "Loss of rod photoreceptor sensitivity in dim lighting with mild peripheral contrast degradation.";
    } else if (severity < 70) {
      stageLabel.textContent = "Stage 2: Mid-Stage Ring Scotoma (Tunnel Vision)";
      stageDesc.textContent = "Concentric narrowing of visual field. Difficulties navigating in unfamiliar surroundings.";
    } else {
      stageLabel.textContent = "Stage 3: Advanced Pinhole / Tunnel Vision (<20°)";
      stageDesc.textContent = "Severe concentric peripheral loss. Patient relies solely on central macular cone vision.";
    }
  }
}

// ── Authentication & Modal Management ─────────────────────────────────
function initAuthUI() {
  const modal = document.getElementById("authModal");
  const closeBtn = document.getElementById("closeAuthModal");
  const authForm = document.getElementById("authForm");

  if (closeBtn) closeBtn.addEventListener("click", () => modal.classList.remove("open"));
  modal.addEventListener("click", (e) => { if (e.target === modal) modal.classList.remove("open"); });

  // Auto-fill demo
  document.querySelectorAll("[data-autofill]").forEach(btn => {
    btn.addEventListener("click", () => {
      if (btn.getAttribute("data-autofill") === "admin") {
        document.querySelector("input[name='authRole'][value='admin']").checked = true;
        document.getElementById("authEmail").value = "admin@retinaai.com";
        document.getElementById("authPassword").value = "Admin@123";
      }
    });
  });

  // Login submit
  authForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("authEmail").value;
    const password = document.getElementById("authPassword").value;
    const role = document.querySelector("input[name='authRole']:checked").value;
    const submitBtn = authForm.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in...";

    try {
      const res = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role })
      });
      const data = await res.json();
      if (data.status === "success") {
        state.currentUser = { ...data.user, role: data.role };
        localStorage.setItem("rpeye_user", JSON.stringify(state.currentUser));
        modal.classList.remove("open");
        updateUserHeader();
        showToast(`Welcome back, ${state.currentUser.name || state.currentUser.clinic_name || "User"}! 👋`, "success");
        if (data.role === "admin")  navigateTo("admin");
        else if (data.role === "clinic") navigateTo("clinic");
        else navigateTo("patient");
      } else {
        showToast(data.message || "Login failed", "error");
      }
    } catch (err) {
      showToast("Server connection error during login.", "error");
    }
    submitBtn.disabled = false;
    submitBtn.textContent = "Sign In →";
  });

  // Patient registration
  const patientRegForm = document.getElementById("patientRegForm");
  if (patientRegForm) {
    patientRegForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(patientRegForm);
      const btn = patientRegForm.querySelector("button[type='submit']");
      btn.disabled = true; btn.textContent = "Registering...";
      try {
        const res = await fetch("/api/register/patient", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(Object.fromEntries(fd))
        });
        const data = await res.json();
        if (data.status === "success") {
          showToast("Account created! Please sign in.", "success");
          patientRegForm.reset();
          switchAuthTab("login");
        } else {
          showToast(data.message || "Registration failed", "error");
        }
      } catch (e) {
        showToast("Server error during registration.", "error");
      }
      btn.disabled = false; btn.textContent = "Create Patient Account →";
    });
  }

  // Clinic registration
  const clinicRegForm = document.getElementById("clinicRegForm");
  if (clinicRegForm) {
    clinicRegForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(clinicRegForm);
      const data = Object.fromEntries(fd);
      if (!data.specialization) data.specialization = "Ophthalmology";
      const btn = clinicRegForm.querySelector("button[type='submit']");
      btn.disabled = true; btn.textContent = "Submitting...";
      try {
        const res = await fetch("/api/register/clinic", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data)
        });
        const resp = await res.json();
        if (resp.status === "success") {
          showToast("Clinic submitted for admin approval! You'll be able to login once approved.", "success");
          clinicRegForm.reset();
          modal.classList.remove("open");
        } else {
          showToast(resp.message || "Registration failed", "error");
        }
      } catch (e) {
        showToast("Server error during registration.", "error");
      }
      btn.disabled = false; btn.textContent = "Submit Clinic for Approval →";
    });
  }

  updateUserHeader();
}

function updateUserHeader() {
  const container = document.getElementById("userHeaderActions");
  if (!container) return;
  if (state.currentUser) {
    const roleIcon = { admin: "🛡️", clinic: "🏥", user: "👤" }[state.currentUser.role] || "👤";
    const displayName = state.currentUser.name || state.currentUser.clinic_name || "User";
    container.innerHTML = `
      <div style="display:flex;align-items:center;gap:0.75rem;">
        <span class="btn btn-secondary btn-sm" style="cursor:default;">${roleIcon} ${displayName}</span>
        <button class="btn btn-sm btn-primary" onclick="logoutUser()">Logout</button>
      </div>`;
  } else {
    container.innerHTML = `
      <button class="btn btn-secondary btn-sm" onclick="document.getElementById('authModal').classList.add('open')">Sign In</button>
      <button class="btn btn-primary btn-sm" onclick="navigateTo('scanner')">Scan Retina</button>`;
  }
}

window.logoutUser = function() {
  const name = state.currentUser?.name || state.currentUser?.clinic_name || "User";
  localStorage.removeItem("rpeye_user");
  state.currentUser = null;
  updateUserHeader();
  navigateTo("home");
  showToast(`Logged out successfully. See you, ${name}!`, "info");
};

// ── Live Stats Loader ─────────────────────────────────────────────────
async function loadLiveStats() {
  try {
    const res = await fetch("/api/stats");
    const json = await res.json();
    if (json.status === "success") {
      const d = json.data;
      animateCount("statUsers", d.total_users);
      animateCount("statClinics", d.total_clinics);
      animateCount("statScans", d.total_detections);
    }
  } catch (e) {}
}

function animateCount(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const duration = 1200;
  const start = performance.now();
  const startVal = 0;
  function update(now) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.floor(startVal + (target - startVal) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

// ── Patient Portal ─────────────────────────────────────────────────────
async function loadPatientDashboard() {
  // Default: load detections
  loadPatientDetections();
}

async function loadPatientDetections() {
  const container = document.getElementById("patientDetectionsList");
  if (!container) return;
  if (!state.currentUser || state.currentUser.role !== "user") {
    container.innerHTML = `<div class="glass-panel" style="padding:1.5rem;text-align:center;">
      <div style="font-size:2rem;margin-bottom:0.5rem;">🔒</div>
      <p style="color:#94a3b8;margin-bottom:1rem;">Please sign in as a Patient to view your screening history.</p>
      <button class="btn btn-primary btn-sm" onclick="document.getElementById('authModal').classList.add('open')">Sign In</button>
    </div>`;
    return;
  }
  container.innerHTML = `<p style="color:var(--text-muted);">Loading...</p>`;
  try {
    const res = await fetch(`/api/user/detections/${state.currentUser.id}`);
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = json.data.map(d => `
        <div class="glass-panel" style="padding:1rem;margin-bottom:0.6rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;">
          <div style="flex:1;">
            <div style="font-weight:700;color:#fff;margin-bottom:0.2rem;">${d.result}</div>
            <div style="color:#64748b;font-size:0.8rem;">📅 ${d.timestamp} &middot; 📁 ${d.filename}</div>
            <div style="color:#94a3b8;font-size:0.8rem;margin-top:0.2rem;">RP: ${(d.disease_prob*100).toFixed(1)}% &middot; Normal: ${(d.normal_prob*100).toFixed(1)}%</div>
          </div>
          <span class="result-badge ${d.risk_level === 'HIGH' ? 'badge-high' : 'badge-low'}">${d.risk_level} RISK</span>
        </div>`).join("");
    } else {
      container.innerHTML = `<p style="color:#64748b;padding:1rem;">No prior scans recorded. Use the AI Scanner to upload your first image.</p>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load screening history.</p>`;
  }
}

async function loadPatientBookings() {
  const container = document.getElementById("patientBookingsList");
  if (!container) return;
  if (!state.currentUser || state.currentUser.role !== "user") {
    container.innerHTML = `<p style="color:#94a3b8;padding:1rem;">Please sign in to see your appointments.</p>`;
    return;
  }
  container.innerHTML = `<p style="color:var(--text-muted);">Loading appointments...</p>`;
  try {
    const res = await fetch(`/api/user/bookings/${state.currentUser.id}`);
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = json.data.map(b => {
        const statusColor = { confirmed: "#34d399", pending: "#fbbf24", cancelled: "#f43f5e" }[b.status] || "#94a3b8";
        return `
        <div class="glass-panel" style="padding:1.2rem;margin-bottom:0.7rem;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
            <div style="font-weight:700;color:#fff;font-size:1.05rem;">🏥 ${b.clinic_name}</div>
            <span style="font-weight:700;color:${statusColor};font-size:0.85rem;text-transform:uppercase;">${b.status}</span>
          </div>
          <div style="color:#94a3b8;font-size:0.85rem;">Dr. ${b.doctor_name} &middot; 📍 ${b.clinic_city} &middot; 📞 ${b.clinic_phone}</div>
          <div style="color:#64748b;font-size:0.8rem;margin-top:0.3rem;">📅 Booked: ${b.timestamp}</div>
          ${b.notes ? `<div style="color:#94a3b8;font-size:0.82rem;margin-top:0.3rem;font-style:italic;">Notes: ${b.notes}</div>` : ""}
        </div>`;
      }).join("");
    } else {
      container.innerHTML = `<p style="color:#64748b;padding:1rem;">No appointments booked yet. Find a clinic in the "Find Nearby Clinics" tab.</p>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load appointments.</p>`;
  }
}

window.searchClinics = async function() {
  const city = document.getElementById("searchCity").value.trim();
  const state2 = document.getElementById("searchState").value.trim();
  if (!city && !state2) { showToast("Enter a city or state to search.", "warning"); return; }
  const params = new URLSearchParams();
  if (city) params.append("city", city);
  if (state2) params.append("state", state2);
  await renderClinicList(`/api/clinics?${params}`);
};

window.loadAllClinics = async function() {
  await renderClinicList("/api/clinics");
};

async function renderClinicList(url) {
  const container = document.getElementById("nearbyClinicsList");
  if (!container) return;
  container.innerHTML = `<p style="color:var(--text-muted);">Searching...</p>`;
  try {
    const res = await fetch(url);
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = json.data.map(cl => `
        <div class="glass-panel" style="padding:1.2rem;margin-bottom:0.7rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;">
          <div>
            <div style="font-weight:700;color:#fff;font-size:1.05rem;">🏥 ${cl.clinic_name}</div>
            <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.2rem;">
              Dr. ${cl.doctor_name} &middot; ${cl.specialization} &middot; 📍 ${cl.city}, ${cl.state}
            </div>
            <div style="color:#64748b;font-size:0.8rem;margin-top:0.2rem;">📞 ${cl.phone} &middot; ${cl.address}</div>
          </div>
          <button class="btn btn-sm btn-primary" style="flex-shrink:0;" onclick="bookClinic(${cl.id})">Book →</button>
        </div>`).join("");
    } else {
      container.innerHTML = `<p style="color:#64748b;padding:1rem;">No approved clinics found for this location.</p>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load clinics.</p>`;
  }
}

window.bookClinic = async function(clinicId) {
  if (!state.currentUser) {
    showToast("Please sign in as a Patient to book a consultation.", "warning");
    document.getElementById("authModal").classList.add("open");
    return;
  }
  if (state.currentUser.role !== "user") {
    showToast("Only patient accounts can book appointments.", "warning");
    return;
  }
  const notes = prompt("Enter any specific concerns or symptoms for the doctor:", "High risk screening follow-up");
  if (notes === null) return;
  try {
    const res = await fetch("/api/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: state.currentUser.id, clinic_id: clinicId, notes: notes })
    });
    const data = await res.json();
    if (data.status === "success") {
      showToast("Appointment booked successfully! ✅", "success");
    } else {
      showToast(data.message || "Booking failed.", "error");
    }
  } catch (e) {
    showToast("Server error during booking.", "error");
  }
};

// ── Clinic Portal ──────────────────────────────────────────────────────
async function loadClinicPortal() {
  const container = document.getElementById("clinicBookingsList");
  if (!container) return;
  if (!state.currentUser || state.currentUser.role !== "clinic") {
    container.innerHTML = `<div class="glass-panel" style="padding:1.5rem;text-align:center;">
      <div style="font-size:2rem;margin-bottom:0.5rem;">🔒</div>
      <p style="color:#fda4af;margin-bottom:1rem;">Please sign in with a verified Clinic account to access the doctor queue.</p>
      <button class="btn btn-primary btn-sm" onclick="document.getElementById('authModal').classList.add('open')">Sign In</button>
    </div>`;
    return;
  }
  container.innerHTML = `<p style="color:var(--text-muted);">Loading queue...</p>`;
  try {
    const res = await fetch(`/api/clinic/bookings/${state.currentUser.id}`);
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = json.data.map(b => {
        const statusColor = { confirmed: "#34d399", pending: "#fbbf24", cancelled: "#f43f5e" }[b.status] || "#94a3b8";
        const riskBadge = b.risk_level ? `<span class="result-badge ${b.risk_level === 'HIGH' ? 'badge-high' : 'badge-low'}" style="font-size:0.75rem;">${b.risk_level} RISK</span>` : "";
        return `
        <div class="glass-panel" style="padding:1.2rem;margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">
            <h4 style="color:#fff;">👤 ${b.user_name} ${riskBadge}</h4>
            <span style="font-weight:700;color:${statusColor};font-size:0.85rem;text-transform:uppercase;">${b.status}</span>
          </div>
          <p style="color:#94a3b8;font-size:0.87rem;margin-bottom:0.6rem;">
            📞 ${b.user_phone} &middot; 📍 ${b.user_city} &middot; 📅 ${b.timestamp}
          </p>
          ${b.result ? `<p style="color:#64748b;font-size:0.82rem;margin-bottom:0.6rem;">AI Result: ${b.result} (RP: ${(b.disease_prob*100).toFixed(1)}%)</p>` : ""}
          ${b.notes ? `<p style="color:#94a3b8;font-size:0.82rem;font-style:italic;margin-bottom:0.6rem;">Notes: ${b.notes}</p>` : ""}
          <div style="display:flex;gap:0.6rem;">
            ${b.status !== "confirmed" ? `<button class="btn btn-sm btn-primary" onclick="setBookingStatus(${b.id},'confirmed')">✅ Confirm</button>` : ""}
            ${b.status !== "cancelled" ? `<button class="btn btn-sm btn-secondary" onclick="setBookingStatus(${b.id},'cancelled')">✖ Cancel</button>` : ""}
          </div>
        </div>`;
      }).join("");
    } else {
      container.innerHTML = `<p style="color:#94a3b8;padding:1rem;">No appointment requests currently in queue.</p>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load bookings.</p>`;
  }
}

window.setBookingStatus = async function(bookingId, status) {
  try {
    await fetch("/api/booking/status", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ booking_id: bookingId, status: status })
    });
    showToast(`Appointment ${status} successfully.`, "success");
    loadClinicPortal();
  } catch (e) {
    showToast("Failed to update status.", "error");
  }
};

// ── Admin Portal ──────────────────────────────────────────────────────
async function loadAdminPortal() {
  const container = document.getElementById("adminPendingList");
  const statsRow = document.getElementById("adminStatsRow");
  if (!container) return;

  if (!state.currentUser || state.currentUser.role !== "admin") {
    container.innerHTML = `<div class="glass-panel" style="padding:1.5rem;text-align:center;">
      <div style="font-size:2rem;margin-bottom:0.5rem;">🔒</div>
      <p style="color:#fda4af;margin-bottom:1rem;">Administrative authentication required.</p>
      <button class="btn btn-primary btn-sm" onclick="document.getElementById('authModal').classList.add('open')">Sign In as Admin</button>
    </div>`;
    if (statsRow) statsRow.innerHTML = "";
    return;
  }

  // Load stats
  try {
    const sres = await fetch("/api/stats");
    const sjson = await sres.json();
    if (sjson.status === "success" && statsRow) {
      const d = sjson.data;
      statsRow.innerHTML = [
        { label: "Total Patients", val: d.total_users, icon: "👤", color: "#2563eb" },
        { label: "Approved Clinics", val: d.total_clinics, icon: "🏥", color: "#10b981" },
        { label: "Pending Clinics", val: d.pending_clinics, icon: "⏳", color: "#f59e0b" },
        { label: "Total Scans", val: d.total_detections, icon: "🔬", color: "#06b6d4" },
        { label: "Total Bookings", val: d.total_bookings, icon: "📅", color: "#7c3aed" },
        { label: "High Risk Scans", val: d.high_risk, icon: "⚠️", color: "#f43f5e" },
      ].slice(0, 4).map(s => `
        <div class="glass-panel stat-box" style="border-top:3px solid ${s.color};">
          <div class="stat-value" style="color:${s.color};">${s.icon} ${s.val}</div>
          <div class="stat-label">${s.label}</div>
        </div>`).join("");
    }
  } catch (e) {}

  loadAdminPending();
}

async function loadAdminPending() {
  const container = document.getElementById("adminPendingList");
  if (!container) return;
  container.innerHTML = `<p style="color:var(--text-muted);">Loading...</p>`;
  try {
    const res = await fetch("/api/admin/pending_clinics");
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = json.data.map(cl => `
        <div class="glass-panel" style="padding:1.2rem;margin-bottom:0.8rem;">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:1rem;flex-wrap:wrap;">
            <div>
              <div style="font-weight:700;color:#fff;font-size:1.1rem;">${cl.clinic_name} — Dr. ${cl.doctor_name}</div>
              <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.25rem;">
                Reg: <code>${cl.reg_number}</code> &middot; 📧 ${cl.email} &middot; 📞 ${cl.phone}
              </div>
              <div style="color:#64748b;font-size:0.82rem;margin-top:0.2rem;">📍 ${cl.address}, ${cl.city}, ${cl.state}</div>
            </div>
            <div style="display:flex;gap:0.5rem;flex-shrink:0;">
              <button class="btn btn-sm btn-primary" onclick="handleClinicAuth(${cl.id},'approve')">✅ Approve</button>
              <button class="btn btn-sm btn-secondary" onclick="handleClinicAuth(${cl.id},'reject')">❌ Reject</button>
            </div>
          </div>
        </div>`).join("");
    } else {
      container.innerHTML = `<div class="glass-panel" style="padding:1.2rem;text-align:center;"><span style="color:#34d399;font-size:1.5rem;">✅</span><p style="color:#34d399;margin-top:0.5rem;">All clinic registrations are approved and current.</p></div>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load pending clinics.</p>`;
  }
}

async function loadAdminAllClinics() {
  const container = document.getElementById("adminAllClinicsList");
  if (!container || !state.currentUser || state.currentUser.role !== "admin") return;
  container.innerHTML = `<p style="color:var(--text-muted);">Loading...</p>`;
  try {
    const res = await fetch("/api/admin/all_clinics");
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = json.data.map(cl => `
        <div class="glass-panel" style="padding:1rem;margin-bottom:0.6rem;display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;">
          <div>
            <div style="font-weight:700;color:#fff;">${cl.clinic_name}</div>
            <div style="color:#94a3b8;font-size:0.83rem;">Dr. ${cl.doctor_name} &middot; ${cl.city}, ${cl.state}</div>
          </div>
          <span class="result-badge ${cl.approved ? 'badge-low' : 'badge-high'}">${cl.approved ? '✅ APPROVED' : '⏳ PENDING'}</span>
        </div>`).join("");
    } else {
      container.innerHTML = `<p style="color:#64748b;padding:1rem;">No clinics registered yet.</p>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load clinics.</p>`;
  }
}

async function loadAdminUsers() {
  const container = document.getElementById("adminUsersList");
  if (!container || !state.currentUser || state.currentUser.role !== "admin") return;
  container.innerHTML = `<p style="color:var(--text-muted);">Loading...</p>`;
  try {
    const res = await fetch("/api/admin/users");
    const json = await res.json();
    if (json.status === "success" && json.data.length) {
      container.innerHTML = `
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:0.8rem;">
          ${json.data.map(u => `
            <div class="glass-panel" style="padding:1rem;">
              <div style="font-weight:700;color:#fff;margin-bottom:0.3rem;">👤 ${u.name}</div>
              <div style="color:#94a3b8;font-size:0.82rem;">📧 ${u.email}</div>
              <div style="color:#64748b;font-size:0.8rem;">📞 ${u.phone || "—"} &middot; 📍 ${u.city || "—"}, ${u.state || "—"}</div>
              <div style="color:#475569;font-size:0.78rem;margin-top:0.3rem;">Joined: ${u.created_at}</div>
            </div>`).join("")}
        </div>`;
    } else {
      container.innerHTML = `<p style="color:#64748b;padding:1rem;">No patients registered yet.</p>`;
    }
  } catch (e) {
    container.innerHTML = `<p style="color:#f43f5e;padding:1rem;">Failed to load users.</p>`;
  }
}

window.handleClinicAuth = async function(clinicId, action) {
  try {
    await fetch("/api/admin/approve_clinic", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clinic_id: clinicId, action: action })
    });
    showToast(`Clinic ${action}d successfully!`, action === "approve" ? "success" : "info");
    loadAdminPending();
    // Refresh stats
    const sres = await fetch("/api/stats");
    const sjson = await sres.json();
    // Re-render stats row
    loadAdminPortal();
  } catch (e) {
    showToast("Failed to update clinic status.", "error");
  }
};

// Expose navigateTo globally for inline onclick use
window.navigateTo = navigateTo;
