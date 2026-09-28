# Deployment Guide for Retina AI

## Table of Contents
- [Local Deployment](#local-deployment)
- [Docker Deployment](#docker-deployment)
- [HuggingFace Spaces](#huggingface-spaces)
- [Cloud Deployment](#cloud-deployment)
- [Production Considerations](#production-considerations)

---

## Local Deployment

### Quick Start

```bash
# Clone repository
git clone https://github.com/gayathri0811/retina-ai.git
cd retina-ai

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app.py
```

The app will be available at `http://localhost:8501`

### Requirements
- Python 3.8+
- 8GB RAM minimum
- GPU (optional but recommended for faster inference)

---

## Docker Deployment

### Build Docker Image

```bash
# Build image
docker build -t retina-ai:latest .

# Run container
docker run -p 8501:8501 retina-ai:latest
```

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 8501

# Run app
CMD ["streamlit", "run", "app.py"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  retina-ai:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./images:/app/images
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
```

---

## HuggingFace Spaces

### Automated Deployment

```bash
# Create HF Space
python create_hf_space.py --username gayathri0811 --token <your_token>

# Push to HF
git remote add hf https://huggingface.co/spaces/gayathri0811/retina-ai
git push hf main
```

**Space URL:** `https://huggingface.co/spaces/gayathri0811/retina-ai`

---

## Cloud Deployment

### AWS EC2

```bash
# Launch EC2 instance (Ubuntu 22.04)
# - t3.medium or larger
# - 30GB storage
# - Security group: Allow 8501 (Streamlit)

# SSH into instance
ssh -i key.pem ubuntu@<instance-ip>

# Clone and deploy
git clone https://github.com/gayathri0811/retina-ai.git
cd retina-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Railway.app

1. Login to [railway.app](https://railway.app)
2. Create new project → Deploy from GitHub
3. Select `retina-ai` repository
4. Deploy → Auto-deployed on every push

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/retina-ai

# Deploy
gcloud run deploy retina-ai \
  --image gcr.io/PROJECT-ID/retina-ai \
  --platform managed \
  --region us-central1 \
  --memory 2Gi
```

### Azure App Service

```bash
# Create App Service Plan
az appservice plan create --name retina-ai-plan --resource-group mygroup --sku B2

# Deploy
az webapp create --resource-group mygroup --plan retina-ai-plan --name retina-ai-app
az webapp deployment source config-zip --resource-group mygroup --name retina-ai-app --src app.zip
```

---

## Production Considerations

### Security
- ✅ Use HTTPS/TLS
- ✅ Implement authentication if needed
- ✅ Validate all inputs
- ✅ Store credentials in environment variables
- ✅ Use secrets management (AWS Secrets Manager, etc.)

### Performance
- ✅ Use GPU acceleration
- ✅ Implement model caching
- ✅ Add request queuing
- ✅ Monitor inference times
- ✅ Implement load balancing

### Monitoring
- ✅ Log all predictions
- ✅ Monitor system resources
- ✅ Track model performance
- ✅ Set up alerts
- ✅ Regular model validation

### Compliance
- ✅ Maintain audit logs
- ✅ Ensure HIPAA compliance if handling medical data
- ✅ Data encryption at rest and in transit
- ✅ Regular security audits

---

## API Deployment (FastAPI)

```bash
# Start API server
uvicorn src.api:app --host 0.0.0.0 --port 8000

# With Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api:app
```

### Example Request

```bash
curl -X POST http://localhost:8000/predict \
  -F "image=@sample.png" \
  -F "model=swin"
```

---

## Health Checks & Monitoring

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter('predictions_total', 'Total predictions')
inference_time = Histogram('inference_seconds', 'Inference time')
```

### Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Prediction: {result}")
```

---

## Troubleshooting

### GPU Not Detected
```python
import torch
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
```

### Out of Memory
```python
# Reduce batch size or use smaller model
predictor = RetinaAIPredictor(model_name='mobilenet')
```

### Slow Performance
- Use GPU acceleration
- Switch to faster model (MobileNet)
- Check network latency
- Monitor system resources

---

## Maintenance

### Regular Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Update models
python scripts/update_models.py
```

### Backup Logs
```bash
# Backup predictions
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

---

## Support
- Documentation: [docs/](../docs/)
- Issues: [GitHub Issues](https://github.com/gayathri0811/retina-ai/issues)
- Email: gayathriproject1108@gmail.com
