# 🚀 HUGGING FACE SPACES DEPLOYMENT GUIDE

## Overview
This guide explains how to deploy Retina AI on Hugging Face Spaces for free cloud hosting.

## Prerequisites
1. **Hugging Face Account** - Free signup at [huggingface.co](https://huggingface.co)
2. **GitHub Access Token** (optional, for private repos)
3. **Model Files** - Pre-trained weights in `models/` directory

## Deployment Methods

### Method 1: Deploy from GitHub (Recommended)

#### Step 1: Create Hugging Face Space
```bash
# 1. Go to https://huggingface.co/spaces
# 2. Click "Create new Space"
# 3. Fill in details:
#    - Space name: retina-ai
#    - License: MIT
#    - SDK: Streamlit
#    - Space hardware: CPU (free) or GPU T4 (paid)
```

#### Step 2: Clone Your GitHub Repository
```bash
# In HF Space settings:
# - Repository: https://github.com/gayathri0811-git/retina-ai.git
# - Branch: main
# - Sync: Enable auto-sync from GitHub
```

#### Step 3: Upload Model Files
Since Git LFS might not be available:
```bash
# Option A: Upload via HF UI
# 1. Open Space settings
# 2. Go to "Repository files"
# 3. Upload models/*.pth files

# Option B: Use Hugging Face CLI
huggingface-cli upload gayathri0811-git/retina-ai models/ ./models/ --repo-type=space
```

### Method 2: Direct Upload to HF Space

```bash
# 1. Create space on Hugging Face
# 2. Clone the space locally
git clone https://huggingface.co/spaces/gayathri0811-git/retina-ai

# 3. Copy project files
cp -r . ./retina-ai/

# 4. Upload model files
cp models/*.pth ./retina-ai/models/

# 5. Push to space
cd retina-ai
git add .
git commit -m "Initial Retina AI deployment"
git push
```

### Method 3: Docker Deployment

```bash
# Build Docker image
docker build -t retina-ai .

# Push to Docker Hub
docker tag retina-ai your-username/retina-ai:latest
docker push your-username/retina-ai:latest

# In HF Space, select "Docker" SDK and configure
```

## File Structure for HF Spaces

```
retina-ai-space/
├── app.py                          # Main Streamlit app
├── README.md                       # Space description
├── requirements.txt                # Python dependencies
├── config/
│   └── model_config.json          # Model configuration
├── models/
│   ├── resnet50_retinitis_classifier.pth    # Main model
│   ├── swin_retina_rp_deploy.pth            # Alternative models
│   ├── VIT_rp.pth
│   ├── efficientnet_rp_model.pth
│   └── mobilenet.pth
├── src/
│   └── models/
│       └── model_loader.py        # Loading utilities
└── .gitignore
```

## Configuration

### requirements.txt
Ensure your requirements.txt has:
```
torch==2.1.2
torchvision==0.16.2
streamlit==1.28.1
pillow==10.1.0
numpy==1.24.3
```

### app.py
Make sure app.py works with HF Spaces:
- ✅ Uses relative paths for models
- ✅ Has proper error handling
- ✅ Works with CPU fallback
- ✅ No hardcoded authentication tokens

## Model Files Handling

### Option 1: Git LFS (if available)
```bash
git lfs install
git lfs track "*.pth"
git add .gitattributes models/
```

### Option 2: HF Model Hub
Upload model once, then load from Hub:
```python
from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    "gayathri0811-git/retina-ai",
    "resnet50_retinitis_classifier.pth"
)
```

### Option 3: Cloud Storage
Store on Google Drive or AWS S3, download on startup:
```python
import gdown

def download_model():
    url = "https://drive.google.com/uc?id=YOUR_FILE_ID"
    model_path = "models/resnet50_retinitis_classifier.pth"
    gdown.download(url, model_path, quiet=False)
```

## Troubleshooting

### Issue: "Model not found" Error
**Solution:** 
- Ensure models/ directory exists
- Check file paths are relative
- Upload model files directly in Space

### Issue: Out of Memory (OOM)
**Solution:**
- Use CPU hardware initially
- Reduce image preprocessing
- Upgrade to GPU T4

### Issue: Slow Loading
**Solution:**
- Use `@st.cache_resource` for model caching
- Optimize requirements.txt
- Consider model quantization

### Issue: Model Files Too Large
**Solution:**
- Use HF Model Hub: `huggingface-hub`
- Implement lazy loading
- Store on external cloud

## Performance Optimization

### 1. Streamlit Optimization
```python
# In app.py
import streamlit as st

st.set_page_config(
    page_title="Retina AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Use caching
@st.cache_resource
def load_model():
    return torch.load(...)
```

### 2. Model Optimization
```bash
# Convert to ONNX for faster inference
python -m torch.onnx export model.pth model.onnx

# Or use TorchScript
traced_model = torch.jit.trace(model, example_input)
traced_model.save("model_scripted.pt")
```

## Monitoring & Logs

View Space logs:
1. Go to Space Settings
2. Click "Server logs"
3. Check for errors and warnings

Access logs via SSH:
```bash
# Configure SSH key in Space settings
ssh spaces-user@your-space.huggingface.co
tail -f /var/log/app.log
```

## Security Considerations

⚠️ **Never commit:**
- API keys or tokens
- Private credentials
- Personal data images
- Password files

✅ **Do:**
- Use `.env` files locally, add to `.gitignore`
- Use HF Secrets in Space settings
- Validate user inputs
- Log anonymized predictions

## Scaling to Production

For production deployment beyond Hugging Face:

### Docker Compose Setup
```yaml
version: '3.8'
services:
  streamlit:
    build: .
    ports:
      - "8501:8501"
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    volumes:
      - ./models:/app/models
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: retina-ai
spec:
  replicas: 3
  containers:
  - name: streamlit
    image: retina-ai:latest
    ports:
    - containerPort: 8501
    resources:
      limits:
        memory: "2Gi"
```

### API Backend (FastAPI)
For high-performance inference:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0
```

## Testing Before Deployment

```bash
# 1. Test locally
streamlit run app.py

# 2. Test with sample image
curl -X POST http://localhost:8501/api/predict \
  -F "image=@sample.jpg"

# 3. Verify model paths
python -c "import sys; print(sys.path)"
```

## Cost Estimation

### Hugging Face Spaces Pricing
- **CPU (Free):** Unlimited
- **GPU T4 (Paid):** ~$0.50/hour (~$7.50/day)
- **GPU A40 (Paid):** ~$0.75/hour

### Optimization Tips
- Start with free CPU tier
- Use model caching to reduce loading
- Implement request throttling
- Monitor usage regularly

## Next Steps

1. ✅ Deploy to Hugging Face Spaces
2. ✅ Test with sample images
3. ✅ Share Space link with collaborators
4. ✅ Monitor usage and performance
5. ✅ Gather user feedback
6. ✅ Iterate and improve

---

**Need Help?**
- HF Spaces Docs: https://huggingface.co/docs/hub/spaces
- Streamlit Docs: https://docs.streamlit.io
- GitHub Issues: https://github.com/gayathri0811-git/retina-ai/issues
