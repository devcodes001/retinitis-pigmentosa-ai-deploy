# RPeyecare — Clinical AI Screening for Retinitis Pigmentosa

A full-stack Clinical AI platform for early detection of **Retinitis Pigmentosa** using deep learning retinal fundus image analysis.

## 🚀 Live Demo
```
python server.py
# Open: http://localhost:5000
```

## 🧠 Tech Stack
| Layer | Technology |
|---|---|
| AI Model | PyTorch ResNet-50 (Transfer Learning) |
| Backend | Python + Flask REST API |
| Database | SQLite + bcrypt |
| Frontend | HTML5 + CSS3 + Vanilla JS (SPA) |
| PDF Reports | ReportLab |
| Image Processing | Pillow |

## 🏗️ Features
- **AI Retinal Scanner** — Upload fundus images or use 1-click sample scans; get instant RP probability breakdown
- **Vision Simulator** — Interactive canvas showing progressive tunnel vision at different RP stages
- **Patient Portal** — Screening history, appointment booking, nearby clinic search
- **Clinic Portal** — Doctor queue: view referrals, confirm/cancel appointments
- **Admin Console** — Approve clinics, view all users/clinics, live platform analytics
- **Auth System** — Secure login + registration for Patients and Clinics (bcrypt hashed)
- **PDF Reports** — One-click clinical report download with diagnosis & recommendations

## 🔑 Demo Credentials
- **Admin:** `admin@retinaai.com` / `Admin@123`
- **Patient/Clinic:** Register via the Sign In → Register tab

## ⚙️ Setup

```bash
pip install flask pillow torch torchvision reportlab bcrypt numpy
python server.py
```

> **Note:** Place your trained model weights at `models/resnet50_retinitis_classifier.pth`  
> Without the model file, the server still runs using randomly initialized ResNet-50 weights.

## 📁 Project Structure
```
├── server.py          # Flask API server (main entry point)
├── db.py              # SQLite database layer
├── utils.py           # Utility helpers
├── static/
│   ├── index.html     # Single-page application
│   ├── style.css      # Dark glassmorphism design system
│   ├── app.js         # Complete client-side logic
│   └── samples/       # 4 benchmark retinal scan images
├── pages/             # Streamlit pages (legacy)
├── models/            # Model weights (not tracked by git)
└── requirements.txt   # Python dependencies
```

## ⚠️ Disclaimer
RPeyecare is an AI decision-support tool and does **not** constitute a clinical diagnosis. All findings must be confirmed by a board-certified ophthalmologist.
