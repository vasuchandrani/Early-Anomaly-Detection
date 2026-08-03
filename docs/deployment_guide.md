# Complete Deployment & Operation Guide

This guide provides step-by-step instructions for running, testing, building, and deploying the **Financial Early Warning System** locally and in containerized environments.

---

## Environment Prerequisites

- **Docker & Docker Compose** (Recommended for containerized execution)
- **Java OpenJDK 17** & **Maven 3.8+** (For local Java development)
- **Python 3.10+** (For local ML pipeline development)
- **PostgreSQL 15** & **Apache Kafka 3.x / Confluent 7.x** (If running infrastructure bare-metal)

---

## Deployment Option 1: Docker Compose (One-Command Deployment)

The fastest and most reliable way to launch the entire system (Database, Kafka Broker, Spring Boot Service, Python Inference Engine) is using Docker Compose.

### Step 1: Clone & Configure Environment
```bash
git clone https://github.com/vatsalchandrani/Early-Anomaly-Detection.git
cd Early-Anomaly-Detection

# Copy sample environment configuration
cp .env.example .env
```

### Step 2: Build and Start Containers
```bash
docker-compose up --build -d
```

### Step 3: Verify Services
Once launched, verify service status:

| Service | Port | Endpoint / Health Check |
| :--- | :--- | :--- |
| **Java Webhook Backend** | `8080` | `http://localhost:8080/webhook/health` |
| **Python ML Inference** | `8000` | `http://localhost:8000/health` |
| **PostgreSQL Database** | `5433` | `localhost:5433` (`creditrisk`) |
| **Apache Kafka Broker** | `9092` | `localhost:9092` |

---

## Deployment Option 2: Local Development Setup

If you wish to run components individually for debugging:

### Step 1: Start Infrastructure (Kafka & Postgres)
```bash
docker-compose up zookeeper kafka postgres -d
```

### Step 2: Run Data Generation & Train ML Model
```bash
# Navigate to ML-Pipeline
cd ML-Pipeline

# Create and activate Python virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic bank data (creates data/transactions_raw.csv)
python data_generator.py

# Compute features (creates data/features.csv)
python feature_engineering.py

# Train Isolation Forest & log to MLflow (creates models/pipeline.pkl)
python train.py
```

### Step 3: Start Python Real-Time Inference Service
```bash
python inference_service.py
```
*Inference Service runs at `http://localhost:8000` and starts listening to Kafka topic `transactions`.*

### Step 4: Build & Run Spring Boot Backend
In a new terminal window:
```bash
cd Backend

# Build application JAR
./mvnw clean package -DskipTests  # On Windows: mvnw.cmd clean package -DskipTests

# Run Spring Boot Application
java -jar target/Backend-0.0.1-SNAPSHOT.jar
```
*Backend runs at `http://localhost:8080`.*

---

## Testing & Simulating Real-Time Streams

To verify the end-to-end event stream from ingestion -> feature extraction -> model inference -> database insertion:

### Run Producer Test Script
```bash
cd ML-Pipeline
python kafka_producer_test.py
```
This script pushes transaction batches for test accounts (including distress archetypes `USER_ANOM_JL`, `USER_ANOM_AW`, `USER_ANOM_CS`) into Kafka topic `transactions`.

### Query Detected Anomalies via REST API
```bash
# Fetch all detected anomalies stored in PostgreSQL
curl -X GET http://localhost:8080/anomalies

# Fetch anomalies for job loss user
curl -X GET http://localhost:8080/anomalies/USER_ANOM_JL
```

---

## MLflow Dashboard & Model Tracking

To view logged experiment runs, contamination metrics, and model artifacts:
```bash
cd ML-Pipeline
mlflow ui
```
Open browser at `http://localhost:5000` to inspect the `bfsi-anomaly-detection` experiment.
