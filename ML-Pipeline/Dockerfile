# Dockerfile for Python ML Inference & Streaming Pipeline
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for confluent-kafka
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure models directory exists
RUN mkdir -p ../models ../data

EXPOSE 8000

CMD ["python", "inference_service.py"]
