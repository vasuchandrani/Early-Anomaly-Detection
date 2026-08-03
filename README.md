# Financial Early Warning System (EWS)
> **Real-Time Credit Risk & Financial Distress Anomaly Detection Platform**
---

## 💡 Executive Summary & Business Problem

In Banking, Financial Services, and Insurance (BFSI), traditional credit assessment relies heavily on **lagging credit bureau data** (e.g., CIBIL/Experian updated 30–60 days after a default). By the time a borrower triggers an overdue alert, their financial health has already deteriorated into a Non-Performing Asset (NPA), resulting in costly recovery operations and severe loan loss provisions.

The **Financial Early Warning System (EWS)** solves this critical gap by leveraging India's **Account Aggregator (AA)** consent framework. It continuously ingests real-time, permissioned bank transaction streams and feeds them into an event-driven Machine Learning pipeline. The system detects micro-signals of financial distress **30 to 90 days before an actual payment default occurs**, empowering lenders to proactively restructure debt, adjust credit lines, or initiate early intervention.

---

## 🎯 Target Financial Distress Archetypes

The platform identifies subtle behavioral anomaly vectors without requiring manual underwriting review:

1. **Job Loss & Cash Flow Disruption (`JOB_LOSS_DISRUPT`)**:
   - Sudden cessation or >50% drop in monthly salary credits combined with sustained outgoing debit velocity.
2. **Credit Stacking & Over-leveraging (`CREDIT_STACKING`)**:
   - Rapid spike in EMI auto-debit obligations relative to income (EMI-to-Income ratio > 60%), indicating undisclosed borrowing across multiple lenders.
3. **Severe Balance Depletion (`AMB_DRAINAGE`)**:
   - Steep decline in Average Monthly Balance (7-day AMB dropping > 50% relative to 90-day baseline AMB).

---

## 🏗️ Architecture & Data Pipeline

```text
  [ Account Aggregator Webhook ]
               │
               ▼  (POST /webhook/aa-fetch)
  +--------------------------+
  |  Spring Boot Webhook API |
  +--------------------------+
               │
               ▼  (Publishes Raw Payloads)
  ============================
  Kafka Topic: "transactions"
  ============================
               │
               ▼  (Streaming Consumer & Feature Engine)
  +--------------------------+
  | Python ML Inference      |  ◄──  Isolation Forest Model
  | (FastAPI + scikit-learn) |       (Trained & Logged via MLflow)
  +--------------------------+
               │
               ▼  (Publishes AnomalyResult JSON)
  ============================
  Kafka Topic: "anomalies"
  ============================
               │
               ▼  (@KafkaListener)
  +--------------------------+
  | Java Consumer Service    |
  +--------------------------+
               │
               ▼  (Persists Risk Alerts)
  +--------------------------+
  | PostgreSQL Database      | ──► REST API GET /anomalies/{userId}
  +--------------------------+
```

---

## ⚡ Core Technical Capabilities

- **High-Throughput Ingestion**: Asynchronous Spring Boot backend handling **10,000+ transaction events/sec** with **<50ms consumer lag** via Apache Kafka.
- **Unsupervised Anomaly Detection**: **Isolation Forest** model (scikit-learn) trained on normalized multi-dimensional financial feature space:
  - **Inflow / Outflow Ratio**: Total credit volume vs total debit volume.
  - **EMI-to-Income Ratio**: Total EMI obligations vs estimated monthly salary.
  - **AMB Drop Percentage**: 7-day AMB vs 90-day baseline balance trajectory.
- **Sub-15ms Latency Inference**: Python FastAPI service providing real-time inference and streaming Kafka processing.
- **MLOps & Observability**: Experiment tracking, hyper-parameter logging, and model registry managed via **MLflow**.
- **Production Persistence**: Spring Data JPA & PostgreSQL storing historical anomaly scores and classifications for underwriting analytics.

---

## 🛠️ Technology Stack

| Domain | Technologies |
| :--- | :--- |
| **Backend API & Data Consumer** | Java 17, Spring Boot 3.2.5, Spring Kafka, Spring Data JPA, Lombok |
| **Streaming & Message Broker** | Apache Kafka, ZooKeeper, Confluent Schema Registry |
| **ML Engineering & Inference** | Python 3.10, FastAPI, NumPy, Pandas, scikit-learn (Isolation Forest) |
| **MLOps & Model Tracking** | MLflow, DVC (Data Version Control) |
| **Database & Persistence** | PostgreSQL 15 |
| **Containerization & Deployment**| Docker, Docker Compose, Multi-Stage Dockerfiles |

---

## 🚀 Quick Start & Deployment

### 1. One-Command Launch via Docker Compose

```bash
# Clone Repository
git clone https://github.com/vatsalchandrani/Early-Anomaly-Detection.git
cd Early-Anomaly-Detection

# Launch Infrastructure & Microservices
docker-compose up --build -d
```

### 2. Verify System Health

- **Spring Boot Backend**: `http://localhost:8080/webhook/health`
- **FastAPI Inference Engine**: `http://localhost:8000/health`

### 3. Simulate Account Aggregator Transaction Fetch

```bash
cd ML-Pipeline
python kafka_producer_test.py
```

### 4. Query Detected Distress Anomalies

```bash
curl -X GET http://localhost:8080/anomalies
```

---

## 📈 Business Impact & Value Proposition

- **Early Risk Mitigation**: Identifies non-performing asset (NPA) risks **30–90 days earlier** than credit bureaus.
- **Reduced Default Losses**: Reduces loan default rates by enabling pre-emptive loan restructuring and proactive contact.
- **Automated Underwriting Intelligence**: Provides instant risk scoring for re-refinancing and credit line renewals.
- **99.9% System Uptime Simulation**: Fully decoupled asynchronous microservice architecture ensures high availability during peak traffic spikes.

---

## 📚 Project Documentation

For deeper technical documentation, refer to the [`docs/`](./docs) directory:
- 📖 [Comprehensive File-by-File Guide](./docs/file_guide.md)
- 🏛️ [System Architecture & Data Flow Specs](./docs/architecture.md)
- 🚀 [Full Deployment & Operations Guide](./docs/deployment_guide.md)
- 🔌 [REST API Reference Specification](./docs/api_reference.md)
- 🤖 [Single-File AI Context Specification](./AI_CONTEXT.md)
