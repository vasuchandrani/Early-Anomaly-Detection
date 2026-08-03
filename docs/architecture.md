# System Architecture & Technical Specification

The **Financial Early Warning System** is an event-driven, microservices-based credit risk monitoring platform. It ingests banking transaction streams from Account Aggregators (AA), computes financial distress metrics in real-time, executes unsupervised anomaly detection models (Isolation Forest), and persists risk alerts for underwriting & early debt recovery teams.

---

## High-Level Architecture Diagram

```
                       +-----------------------------------+
                       | Account Aggregator / Bank Webhook |
                       +-----------------------------------+
                                         |
                                         v  POST /webhook/aa-fetch
                       +-----------------------------------+
                       |     Java Spring Boot Backend      |
                       +-----------------------------------+
                                         |
                                         | Publish Payload
                                         v
                      =======================================
                      Kafka Topic: "transactions" (Port 9092)
                      =======================================
                                         |
                                         | Consume Payload
                                         v
                       +-----------------------------------+
                       |    Python ML Inference Service    |
                       | (FastAPI + Isolation Forest + ML) |
                       +-----------------------------------+
                                         |
                                         | Feature Extraction:
                                         |  - Debt-to-Income Ratio
                                         |  - Inflow vs Outflow Ratio
                                         |  - AMB 7d vs 90d Drop %
                                         |
                                         | Publish AnomalyResult
                                         v
                      =======================================
                      Kafka Topic: "anomalies" (Port 9092)
                      =======================================
                                         |
                                         | Consume AnomalyResult
                                         v
                       +-----------------------------------+
                       |     Java Spring Boot Backend      |
                       +-----------------------------------+
                                         |
                                         v Write AnomalyEntity
                       +-----------------------------------+
                       |    PostgreSQL DB (Port 5433)      |
                       +-----------------------------------+
                                         |
                                         v GET /anomalies/{userId}
                       +-----------------------------------+
                       |   Risk & Underwriting Dashboard   |
                       +-----------------------------------+
```

---

## Core Components Breakdown

### 1. Ingestion Layer (Java Spring Boot)
- **Responsibility**: Ingests high-throughput webhook JSON requests (`/webhook/aa-fetch`) representing consent-based Account Aggregator data fetches.
- **Tech Stack**: Java 17, Spring Boot 3.2.5, Spring Kafka, Spring Validation.
- **Decoupling**: Immediately validates incoming JSON schema and queues payloads onto Kafka topic `transactions` within **<50ms**, ensuring non-blocking performance for incoming webhooks.

### 2. Event Streaming Backbone (Apache Kafka & ZooKeeper)
- **Topics**:
  - `transactions`: Carries raw transaction batch payloads keyed by `userId`.
  - `anomalies`: Carries processed anomaly inference vectors, anomaly scores, and distress classifications.
- **Serialization**: String keys with JSON payloads. Schema registry support prepared for Avro records (`schemas/transaction.avsc`).

### 3. Real-Time Feature Engineering & ML Inference Engine (Python / FastAPI)
- **Responsibility**: Listens to raw transaction events, calculates domain-specific financial health vectors, and passes them through a pre-trained scikit-learn pipeline.
- **Feature Set**:
  $$\text{Ratio}_{\text{In/Out}} = \frac{\sum \text{Credits}}{\sum \text{Debits}}$$
  $$\text{EMI Ratio} = \frac{\sum \text{EMI Debits}}{\text{Estimated Monthly Salary}}$$
  $$\Delta \text{AMB}_{\%} = \frac{\text{AMB}_{90d} - \text{AMB}_{7d}}{\text{AMB}_{90d}}$$
- **Model**: **Isolation Forest** (Unsupervised Anomaly Detection). Identifies outliers in multi-dimensional feature space without needing labeled historical defaults.
- **MLOps & Tracking**: **MLflow** tracks training runs, contamination hyper-parameters, and model registry artifacts under experiment `bfsi-anomaly-detection`.

### 4. Anomaly Alerting & Persistence Layer (PostgreSQL & Spring JPA)
- **Responsibility**: Consumes `AnomalyResult` messages from Kafka topic `anomalies` via `@KafkaListener` in Java, saving structured anomaly records to PostgreSQL table `anomalies`.
- **API Access**: Exposes REST endpoints (`GET /anomalies`, `GET /anomalies/{userId}`) for risk operations.

---

## Data Model Schemas

### PostgreSQL Table Schema (`anomalies`)

| Field Name | Type | Description |
| :--- | :--- | :--- |
| `id` | `BIGINT PRIMARY KEY` | Auto-incrementing identifier |
| `user_id` | `VARCHAR(255)` | Account Aggregator User Identifier |
| `anomaly_type` | `VARCHAR(255)` | `AMB_DRAINAGE`, `CREDIT_STACKING`, `JOB_LOSS_DISRUPT`, `FINANCIAL_DISTRESS` |
| `anomaly_score` | `DOUBLE PRECISION` | Normalized anomaly score (higher = higher risk) |
| `ratio_inflow_outflow` | `DOUBLE PRECISION` | Calculated inflow/outflow ratio |
| `emi_to_income_ratio` | `DOUBLE PRECISION` | EMI to monthly salary ratio |
| `amb_drop_percentage` | `DOUBLE PRECISION` | Drop percentage in 7-day AMB vs 90-day AMB |
| `transaction_count` | `INTEGER` | Number of transactions evaluated |
| `detected_at` | `TIMESTAMP` | Timestamp when anomaly was evaluated and logged |
