# Backend Dockerfile for FastAPI + CadQuery
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required by CadQuery and OCP
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libopencascade-dev \
    libopencascade-foundation-7.6 \
    libopencascade-modeling-7.6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')" || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
