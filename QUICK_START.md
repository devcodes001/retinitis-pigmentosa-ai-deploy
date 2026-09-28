# 🚀 QUICK START GUIDE

Get Retina AI running in **5 minutes**.

## ⚡ Option 1: Try Online (Easiest)

**Visit Hugging Face Spaces:** [gayathri0811-git/retina-ai](https://huggingface.co/spaces/gayathri0811-git/retina-ai)

1. Upload a retinal image (PNG/JPG)
2. Wait for analysis (~5-10 seconds)
3. View results and download report

✅ **No installation needed!**

---

## 💻 Option 2: Run Locally (GPU Recommended)

### Prerequisites
```bash
Python 3.8+ | Git | ~5GB disk space
```

### Installation (2 minutes)

```bash
# 1. Clone repository
git clone https://github.com/gayathri0811-git/retina-ai.git
cd retina-ai

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download model files (if not in repo)
# Ensure models/ folder contains:
# - resnet50_retinitis_classifier.pth
# - (optional) other model files

# 5. Run application
streamlit run app.py
```

### First Run
```
The app will be available at: http://localhost:8501
```

### Test with Sample Image
```bash
# 1. Prepare a retinal fundus image
# 2. Upload via browser interface
# 3. Click "Run Analysis"
# 4. See results instantly
```

---

## 📱 Option 3: Docker (Fast & Reproducible)

### Using Docker Compose
```bash
docker-compose up --build
# Access at http://localhost:8501
```

### Manual Docker
```bash
# Build image
docker build -t retina-ai .

# Run container
docker run -p 8501:8501 retina-ai

# Access at http://localhost:8501
```

---

## 🔍 Using the Application

### Step 1: Upload Image
- Click **"📤 Upload Image"** area
- Select PNG, JPG, JPEG, or BMP file
- Minimum recommended: 224×224 pixels

### Step 2: Configure (Optional)
**Sidebar Settings:**
- **Confidence Threshold** - Minimum score required (default: 50%)
- **Auto-enhance** - Improve contrast automatically
- **Show Details** - Display detailed analysis

### Step 3: Analyze
- System automatically preprocesses image
- Model inference runs (~3-10 seconds)
- Results display with confidence score

### Step 4: Review Results
```
🟢 Normal (Healthy)          ← Prediction
├─ Confidence: 87.5%        ← Score
├─ Normal Probability: 87.5%
└─ Disease Probability: 12.5%
```

### Step 5: Download Report
- Click **"📥 Download Report"**
- Saves text file with all details
- Use for medical records

---

## 🤖 Multiple Models (Advanced)

Switch between models via config:

### Edit `config/model_config.json`
```json
{
  "models": {
    "resnet50": {"enabled": true, "default": true},
    "swin": {"enabled": true, "default": false},
    "vit": {"enabled": true, "default": false},
    "efficientnet": {"enabled": true, "default": false},
    "mobilenet": {"enabled": true, "default": false}
  }
}
```

### API Usage
```python
from app import load_resnet50_model, preprocess_image
from PIL import Image

# Load model
model = load_resnet50_model()

# Load image
image = Image.open("retinal_image.jpg")
tensor = preprocess_image(image)

# Predict
results = model(tensor)
```

---

## ⚙️ Configuration

### Requirements
Edit `requirements.txt` as needed:
```
torch==2.1.2
torchvision==0.16.2
streamlit==1.28.1
# ... other packages
```

### Model Config
Edit `config/model_config.json`:
```json
{
  "inference": {
    "confidence_threshold": 0.5,
    "device": "auto",
    "batch_size": 32
  }
}
```

### Streamlit Config
Create `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#1f77b4"

[client]
maxUploadSize = 200
showErrorDetails = true
```

---

## 🆘 Troubleshooting

### "Model not found" Error
```bash
# Check model file exists
ls models/resnet50_retinitis_classifier.pth

# If missing, download from Hugging Face Hub
python -c "
from huggingface_hub import hf_hub_download
hf_hub_download('gayathri0811-git/retina-ai', 
                'resnet50_retinitis_classifier.pth')
"
```

### "Out of memory" Error
```bash
# Reduce batch size in config/model_config.json
# Or use lighter model (MobileNet)
```

### "Port 8501 already in use"
```bash
streamlit run app.py --server.port 8502
```

### Slow Inference
```bash
# Enable GPU acceleration
# For NVIDIA: Install CUDA 11.8+
# PyTorch will auto-detect GPU

# Or use lighter model:
# - MobileNet (fastest)
# - ResNet50 (balanced)
# - Vision Transformer (slowest, most accurate)
```

---

## 📊 Performance Reference

| Model | Speed | Accuracy | Size |
|-------|-------|----------|------|
| MobileNet | ⚡⚡⚡ Fast | ⭐⭐⭐ Good | 25 MB |
| ResNet50 | ⚡⚡ Medium | ⭐⭐⭐⭐ Great | 100 MB |
| EfficientNet | ⚡⚡ Medium | ⭐⭐⭐⭐ Great | 80 MB |
| Swin | ⚡ Slower | ⭐⭐⭐⭐⭐ Excellent | 350 MB |
| Vision Transformer | ⚡ Slower | ⭐⭐⭐⭐⭐ Excellent | 350 MB |

---

## 🆕 What's New

**v1.0.0** (Current)
- ✅ ResNet50 optimized deployment
- ✅ Streamlit web interface
- ✅ Hugging Face Spaces ready
- ✅ Multi-model support
- ✅ Production-grade error handling
- ✅ Report generation

**Roadmap** 🗺️
- [ ] FastAPI backend for batch processing
- [ ] Model ensemble (combine multiple models)
- [ ] Export to ONNX for mobile deployment
- [ ] API authentication & rate limiting
- [ ] Admin dashboard for analytics
- [ ] Automated model retraining pipeline

---

## 📚 More Resources

| Resource | Link |
|----------|------|
| Full Documentation | [README.md](README.md) |
| HF Spaces Guide | [HF_SPACES_DEPLOYMENT.md](HF_SPACES_DEPLOYMENT.md) |
| Production Checklist | [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md) |
| GitHub Repository | https://github.com/gayathri0811-git/retina-ai |
| Hugging Face Spaces | https://huggingface.co/spaces/gayathri0811-git/retina-ai |

---

## ❓ FAQ

**Q: Can I use this for clinical diagnosis?**  
A: No. This is a research/educational tool. Always consult qualified ophthalmologists.

**Q: How accurate is the model?**  
A: ResNet50 achieves ~92% accuracy on test data. Results vary by image quality.

**Q: What image formats are supported?**  
A: PNG, JPG, JPEG, BMP (224×224px minimum recommended)

**Q: Can I train my own models?**  
A: Yes. See configuration guide for custom model setup.

**Q: How do I deploy to production?**  
A: See HF_SPACES_DEPLOYMENT.md for cloud hosting options.

**Q: Is my data private?**  
A: Images are processed locally and not stored. See privacy policy in README.

---

## 🙋 Need Help?

**GitHub Issues:** https://github.com/gayathri0811-git/retina-ai/issues  
**Email:** gayathriproject1108@gmail.com  
**GitHub:** @gayathri0811-git  

---

**Ready? Start with Option 1! 🚀**

Visit: https://huggingface.co/spaces/gayathri0811-git/retina-ai
