# Master Execution & Operations Guide (Financial Early Warning System)

This guide provides end-to-end instructions for running, testing, and verifying the **Financial Early Warning System (Credit Risk Anomaly Detection)**.

---

## 🏗️ System Architecture & Workflow Summary

```
                      +-----------------------------------+
                      | Account Aggregator / Bank Webhook |
                      +-----------------------------------+
                                        |
                                        | POST /webhook/aa-fetch (Port 8080 or 8085)
                                        v
                      +-----------------------------------+
                      |     Java Spring Boot Backend      |
                      +-----------------------------------+
                                        |
                                        | Kafka Producer
                                        v
                     =======================================
                     Kafka Topic: "transactions" (Port 9092)
                     =======================================
                                        |
                                        | Kafka Consumer
                                        v
                      +-----------------------------------+
                      |    Python ML Inference Service    |
                      | (FastAPI + Isolation Forest + ML) |
                      +-----------------------------------+
                                        |
                                        | 1. Dynamic Feature Extraction
                                        | 2. Isolation Forest Outlier Score
                                        | 3. Distress Type Classification
                                        |
                                        | Kafka Producer
                                        v
                     =======================================
                     Kafka Topic: "anomalies" (Port 9092)
                     =======================================
                                        |
                                        | Kafka Consumer
                                        v
                      +-----------------------------------+
                      |     Java Spring Boot Backend      |
                      +-----------------------------------+
                                        |
                                        | JPA Database Save
                                        v
                      +-----------------------------------+
                      |   PostgreSQL Database (Port 5433) |
                      +-----------------------------------+
                                        |
                                        | GET /anomalies/{userId}
                                        v
                      +-----------------------------------+
                      |   Risk & Underwriting Operations  |
                      +-----------------------------------+
```

---

## ⚡ Deployment Options

### Option A: Full Automated Stack (Docker Compose - Recommended)

To launch the entire microservices stack (Postgres, Kafka, Zookeeper, Schema Registry, Java Backend, Python ML Inference) with a single command:

```bash
docker-compose up --build -d
```

#### Check Service Health:
```bash
docker-compose ps
```

#### View Container Logs:
```bash
# View backend logs
docker logs -f early-anomaly-detection-backend-1

# View ML inference logs
docker logs -f early-anomaly-detection-ml-inference-1
```

---

### Option B: Local / Hybrid Development Setup

If you prefer running services locally or through your IDE (e.g. IntelliJ IDEA / VS Code):

#### Step 1: Start Core Infrastructure (Kafka, Zookeeper, PostgreSQL)
```bash
docker-compose up -d zookeeper kafka schema-registry postgres
```

#### Step 2: Set Up & Run Python ML Pipeline
Create virtual environment and install dependencies:
```bash
cd ML-Pipeline

# Create environment using uv (or standard venv)
uv venv .venv-win
uv pip install -r requirements.txt --python .venv-win

# 1. Generate synthetic banking transactions (180 days, 23 profiles)
& ".venv-win/Scripts/python.exe" data_generator.py

# 2. Extract financial ratios (Inflow/Outflow, EMI ratio, AMB drop %)
& ".venv-win/Scripts/python.exe" feature_engineering.py

# 3. Train Isolation Forest & export model checkpoint
& ".venv-win/Scripts/python.exe" train.py

# 4. Start Real-time Streaming Inference Worker (FastAPI on Port 8000)
& ".venv-win/Scripts/python.exe" inference_service.py
```

#### Step 3: Run Java Spring Boot Backend
From the root workspace directory:
```bash
cd Backend

# Build & Run via Maven
./mvnw spring-boot:run
```
*(Or run `org.example.backend.BackendApplication` directly from IntelliJ IDEA / Eclipse).*

---

## 🧪 Testing & Verification

### 1. Simulate AA Webhook Data Ingestion
Send raw transaction batches to the Spring Boot ingestion endpoint:

```bash
curl -X POST http://localhost:8080/webhook/aa-fetch \
  -H "Content-Type: application/json" \
  -d '{
    "consentId": "CONSENT-9901",
    "userId": "USER_ANOM_JL",
    "fetchTimestamp": "2026-08-12T02:00:00",
    "bankName": "HDFC",
    "transactions": [
      {
        "transactionId": "TXN-001",
        "userId": "USER_ANOM_JL",
        "accountId": "ACC-8812",
        "timestamp": "2026-08-01T10:00:00",
        "amount": 15000.0,
        "transactionType": "DEBIT",
        "narration": "EMI PAYMENT HDFC LOAN",
        "balanceAfter": 12000.0,
        "bankName": "HDFC"
      }
    ]
  }'
```

### 2. Simulate Automated Test Batch
Run the built-in Kafka Producer test script to simulate live transaction streams for 5 users:

```bash
cd ML-Pipeline
& "../.venv-win/Scripts/python.exe" kafka_producer_test.py
```

### 3. Query Anomaly REST API
Retrieve all flagged risk records from the Java Backend:

```bash
# Get all detected anomalies / evaluated records
curl -s http://localhost:8080/anomalies

# Query specific user profile
curl -s http://localhost:8080/anomalies/USER_ANOM_JL
```

### 4. Query PostgreSQL Database Directly
Inspect persisted records in the `anomalies` table inside PostgreSQL:

```bash
docker exec -it early-anomaly-detection-postgres-1 psql -U admin -d creditrisk -c "SELECT id, user_id, anomaly_type, anomaly_score, emi_to_income_ratio, amb_drop_percentage, detected_at FROM anomalies;"
```

---

## ⚙️ Configuration Reference

| Key Configuration | Location | Default Value | Description |
| :--- | :--- | :--- | :--- |
| **Server Port** | `application.properties` | `8080` (Docker) / `8085` (Local) | HTTP Port for REST Controllers |
| **PostgreSQL URL** | `application.properties` | `jdbc:postgresql://localhost:5433/creditrisk` | Database Connection string |
| **Kafka Bootstrap** | `application.properties` / `.env` | `localhost:9092` (Host) / `kafka:29092` (Docker) | Event Streaming Broker Host |
| **Inference API** | `inference_service.py` | `http://localhost:8000` | FastAPI ML Server |
| **ML Model Path** | `models/pipeline.pkl` | `models/pipeline.pkl` | Serialized Isolation Forest Pipeline |

---

## 🛠️ Troubleshooting FAQ

### 1. `Port 8080 was already in use`
- **Cause**: Another process or Docker container is running on port 8080.
- **Solution**: Either stop the conflicting process or set `SERVER_PORT=8085` in `application.properties` / environment variables.

### 2. `Connect to localhost:9092 failed` / `Broker: Unknown topic or partition`
- **Cause**: Kafka container is stopped or still starting up.
- **Solution**: Execute `docker-compose up -d kafka` and wait 10 seconds for broker registration.

### 3. `Model pipeline is not initialized!`
- **Cause**: `models/pipeline.pkl` model file is missing.
- **Solution**: Run `python ML-Pipeline/train.py` to generate and export the model binary before starting `inference_service.py`.
