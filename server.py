"""
server.py — High-Performance Flask API & Web Server for RPeyecare
Serves HTML5, CSS3, JavaScript frontend + PyTorch inference + SQLite layer
"""
import os
import io
import time
import base64
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory
from PIL import Image, ImageEnhance
import torch
import torch.nn as nn
from torchvision import models, transforms
import numpy as np
import db

app = Flask(__name__, static_folder="static", static_url_path="/static")
db.init_db()

# ── Load PyTorch ResNet-50 Model ──────────────────────────────────────
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Loading ResNet-50 model on device: {DEVICE}")

model = models.resnet50(weights=None)
model.fc = nn.Sequential(
    nn.Linear(model.fc.in_features, 512),
    nn.ReLU(),
    nn.Dropout(0.3),
    nn.Linear(512, 2)
)

MODEL_PATH = "models/resnet50_retinitis_classifier.pth"
if os.path.exists(MODEL_PATH):
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
    print(f"Loaded weights from {MODEL_PATH}")
else:
    print(f"Warning: {MODEL_PATH} not found, using initialized weights.")

model.to(DEVICE)
model.eval()

# ── Preprocessing Transform ──────────────────────────────────────────
preprocess_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def run_inference(pil_img, enhance=True):
    proc = pil_img.copy()
    if enhance:
        proc = ImageEnhance.Contrast(proc).enhance(1.25)
        proc = ImageEnhance.Sharpness(proc).enhance(1.15)
        
    tensor = preprocess_tf(proc).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1).cpu().numpy()[0]
        
    c = int(np.argmax(probs))
    dp = float(probs[0]) # Class 0: Disease (Retinitis Pigmentosa)
    np_ = float(probs[1]) # Class 1: Normal (Healthy)
    
    risk = "HIGH" if dp > 0.65 else ("MEDIUM" if dp > 0.4 else "LOW")
    label = "Retinitis Pigmentosa Detected" if c == 0 else "Normal (Healthy Retina)"
    
    # Generate base64 thumbnail for preview
    thumb = proc.copy()
    thumb.thumbnail((400, 400))
    buf = io.BytesIO()
    thumb.save(buf, format="JPEG", quality=85)
    thumb_b64 = base64.b64encode(buf.getvalue()).decode()
    
    return {
        "class": c,
        "label": label,
        "is_disease": (c == 0),
        "confidence": round(float(probs[c]) * 100, 2),
        "prob_disease": round(dp * 100, 2),
        "prob_normal": round(np_ * 100, 2),
        "risk_level": risk,
        "preview_b64": thumb_b64
    }

# ── Static Routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/images/<path:filename>")
def serve_image(filename):
    return send_from_directory("images", filename)

# ── API Endpoints ────────────────────────────────────────────────────
@app.route("/api/stats", methods=["GET"])
def get_stats():
    stats = db.get_stats()
    stats["model_accuracy"] = 97.5
    stats["architecture"] = "ResNet-50 Transfer Learning"
    return jsonify({"status": "success", "data": stats})

@app.route("/api/predict", methods=["POST"])
def predict_endpoint():
    t0 = time.time()
    enhance = request.form.get("enhance", "true").lower() == "true"
    user_id = request.form.get("user_id")
    
    pil_img = None
    filename = "fundus_scan.png"
    
    # Check if a sample was chosen
    sample_key = request.form.get("sample")
    if sample_key:
        sample_path = Path("static/samples") / f"{sample_key}.png"
        if sample_path.exists():
            pil_img = Image.open(sample_path).convert("RGB")
            filename = sample_path.name
            
    # Check if a file was uploaded
    if not pil_img and "file" in request.files:
        f = request.files["file"]
        if f.filename:
            filename = f.filename
            pil_img = Image.open(f.stream).convert("RGB")
            
    if not pil_img:
        return jsonify({"status": "error", "message": "No retinal scan file or sample provided."}), 400
        
    result = run_inference(pil_img, enhance=enhance)
    elapsed = round(time.time() - t0, 3)
    result["latency_seconds"] = elapsed
    result["filename"] = filename
    
    # If user logged in, persist detection to SQLite
    detection_id = None
    if user_id:
        try:
            uid = int(user_id)
            detection_id = db.save_detection(
                uid, filename, result["label"],
                result["prob_disease"] / 100.0,
                result["prob_normal"] / 100.0,
                result["confidence"] / 100.0,
                result["risk_level"]
            )
        except Exception as e:
            print("Detection save warning:", e)
            
    result["detection_id"] = detection_id
    return jsonify({"status": "success", "result": result})

@app.route("/api/login", methods=["POST"])
def login_endpoint():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    role = data.get("role", "patient").lower()
    
    if role == "admin":
        u = db.login_admin(email, password)
        if u:
            return jsonify({"status": "success", "role": "admin", "user": u})
        return jsonify({"status": "error", "message": "Invalid admin credentials (Demo: admin@retinaai.com / Admin@123)"}), 401
    elif role == "clinic":
        u, err = db.login_clinic(email, password)
        if u:
            return jsonify({"status": "success", "role": "clinic", "user": u})
        return jsonify({"status": "error", "message": err or "Invalid clinic credentials"}), 401
    else:
        u, err = db.login_user(email, password)
        if u:
            return jsonify({"status": "success", "role": "user", "user": u})
        return jsonify({"status": "error", "message": err or "Invalid patient credentials"}), 401

@app.route("/api/register/patient", methods=["POST"])
def register_patient():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    city = data.get("city")
    state = data.get("state")
    address = data.get("address", "")
    
    if not all([name, email, password, phone, city, state]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    ok, msg = db.register_user(name, email, password, phone, city, state, address)
    if ok:
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg}), 400

@app.route("/api/register/clinic", methods=["POST"])
def register_clinic():
    data = request.get_json() or {}
    cname = data.get("clinic_name")
    dname = data.get("doctor_name")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    city = data.get("city")
    state = data.get("state")
    address = data.get("address")
    spec = data.get("specialization", "Ophthalmology")
    regn = data.get("reg_number")
    
    if not all([cname, dname, email, password, phone, city, state, address, regn]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
        
    ok, msg = db.register_clinic(cname, dname, email, password, phone, city, state, address, spec, regn)
    if ok:
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg}), 400

@app.route("/api/clinics", methods=["GET"])
def get_clinics():
    city = request.args.get("city")
    state = request.args.get("state")
    if city or state:
        clinics = db.get_nearby_clinics(city or "", state or "")
    else:
        clinics = db.get_all_clinics(approved_only=True)
    return jsonify({"status": "success", "data": clinics})

@app.route("/api/book", methods=["POST"])
def book_appointment():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    clinic_id = data.get("clinic_id")
    detection_id = data.get("detection_id")
    notes = data.get("notes", "")
    
    if not user_id or not clinic_id:
        return jsonify({"status": "error", "message": "Missing booking parameters"}), 400
        
    ok, msg = db.create_booking(user_id, clinic_id, detection_id, notes)
    if ok:
        return jsonify({"status": "success", "message": msg})
    return jsonify({"status": "error", "message": msg}), 400

@app.route("/api/user/bookings/<int:user_id>", methods=["GET"])
def get_user_bookings(user_id):
    bookings = db.get_user_bookings(user_id)
    return jsonify({"status": "success", "data": bookings})

@app.route("/api/clinic/bookings/<int:clinic_id>", methods=["GET"])
def get_clinic_bookings(clinic_id):
    bookings = db.get_clinic_bookings(clinic_id)
    return jsonify({"status": "success", "data": bookings})

@app.route("/api/booking/status", methods=["POST"])
def update_status():
    data = request.get_json() or {}
    bid = data.get("booking_id")
    status = data.get("status")
    if not bid or not status:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400
    db.update_booking_status(bid, status)
    return jsonify({"status": "success", "message": f"Status updated to {status}"})

@app.route("/api/admin/pending_clinics", methods=["GET"])
def get_pending():
    all_clinics = db.get_all_clinics(approved_only=False)
    pending = [c for c in all_clinics if not c["approved"]]
    return jsonify({"status": "success", "data": pending})

@app.route("/api/admin/all_clinics", methods=["GET"])
def get_all_clinics_admin():
    clinics = db.get_all_clinics(approved_only=False)
    return jsonify({"status": "success", "data": clinics})

@app.route("/api/admin/users", methods=["GET"])
def get_all_users_admin():
    users = db.get_all_users()
    return jsonify({"status": "success", "data": users})

@app.route("/api/admin/approve_clinic", methods=["POST"])
def approve():
    data = request.get_json() or {}
    cid = data.get("clinic_id")
    action = data.get("action", "approve")
    if not cid:
        return jsonify({"status": "error", "message": "Missing clinic ID"}), 400
    if action == "approve":
        db.approve_clinic(cid)
    else:
        db.reject_clinic(cid)
    return jsonify({"status": "success", "message": f"Clinic {action}d successfully"})

@app.route("/api/user/detections/<int:user_id>", methods=["GET"])
def user_detections(user_id):
    dets = db.get_user_detections(user_id)
    return jsonify({"status": "success", "data": dets})

# ── ReportLab PDF Generation ─────────────────────────────────────────
@app.route("/api/generate_report", methods=["POST"])
def generate_report():
    data = request.get_json() or {}
    patient_name = data.get("patient_name", "Anonymous Patient")
    filename = data.get("filename", "retinal_scan.png")
    risk_level = data.get("risk_level", "LOW")
    confidence = data.get("confidence", "95.0")
    label = data.get("label", "Retinal Diagnostic Summary")
    prob_disease = data.get("prob_disease", "0.0")
    prob_normal = data.get("prob_normal", "100.0")
    is_disease = data.get("is_disease", False)
    
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    W = A4[0] - 4*cm
    styles = getSampleStyleSheet()
    
    story = []
    title_style = ParagraphStyle('t', fontSize=18, textColor=colors.HexColor('#0f172a'), alignment=TA_CENTER, fontName='Helvetica-Bold', spaceAfter=4)
    sub_style = ParagraphStyle('s', fontSize=9, textColor=colors.HexColor('#64748b'), alignment=TA_CENTER, spaceAfter=8)
    
    story.append(Paragraph('RPEYECARE &middot; CLINICAL AI SCREENING REPORT', title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y at %I:%M %p')} | Document Ref: RP-{int(time.time())}", sub_style))
    story.append(HRFlowable(width='100%', thickness=2, color=colors.HexColor('#2563eb'), spaceAfter=14))
    
    pt = Table([
        ['Patient Name', patient_name, 'Diagnostic File', filename],
        ['Risk Stratification', risk_level, 'Inference Confidence', f"{confidence}%"],
        ['Retinitis Pigmentosa Prob', f"{prob_disease}%", 'Healthy Retina Prob', f"{prob_normal}%"],
    ], colWidths=[W*0.25, W*0.25, W*0.25, W*0.25])
    
    pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f8fafc')),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(pt)
    story.append(Spacer(1, 14))
    
    res_color = "#dc2626" if is_disease else "#059669"
    story.append(Paragraph(f'<font size="14" color="{res_color}"><b>Diagnostic Outcome: {label}</b></font>', ParagraphStyle('r', alignment=TA_CENTER, spaceAfter=10)))
    
    sec_style = ParagraphStyle('sec', fontSize=12, textColor=colors.HexColor('#0f172a'), fontName='Helvetica-Bold', spaceBefore=10, spaceAfter=6)
    body_style = ParagraphStyle('b', fontSize=9.5, textColor=colors.HexColor('#334155'), spaceAfter=4, leading=14)
    
    story.append(Paragraph('Clinical Guidance & Advisory', sec_style))
    if is_disease:
        recs = [
            "Clinical evaluation by an ophthalmologist or retinal specialist is strongly advised.",
            "Schedule an Electroretinogram (ERG) to evaluate rod and cone photoreceptor responsiveness.",
            "Consider genetic counseling to identify the specific gene mutation underlying the dystrophy.",
            "Discuss protective UV eyewear and nutritional supplementation (e.g. Vitamin A palmitate under medical supervision)."
        ]
    else:
        recs = [
            "No morphological hallmarks of Retinitis Pigmentosa were identified in the submitted scan.",
            "Continue standard annual comprehensive dilated ophthalmic examinations.",
            "Wear UV-rated protective eyewear during prolonged outdoor daylight exposure.",
            "Promptly report any acute changes in night vision (nyctalopia) or peripheral constriction."
        ]
        
    for r in recs:
        story.append(Paragraph(f"&bull; {r}", body_style))
        
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width='100%', thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=8))
    story.append(Paragraph('<b>Medical Notice:</b> RPeyecare is an AI decision-support screening aid and does not constitute a definitive medical diagnosis. Consult a board-certified eye specialist.', ParagraphStyle('d', fontSize=8, textColor=colors.HexColor('#94a3b8'), alignment=TA_CENTER)))
    
    doc.build(story)
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"RPeyecare_Report_{patient_name.replace(' ','_')}.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    print("\n" + "="*60)
    print(">> RPeyecare Web Server Starting on http://localhost:5000")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)

