FROM python:3.10-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source files
COPY . .

# Create models directory (model file loaded at runtime if present)
RUN mkdir -p models static/samples

# Hugging Face Spaces runs on port 7860
ENV PORT=7860
EXPOSE 7860

# Start Flask via gunicorn (production-ready)
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "1", "--timeout", "120", "server:app"]
