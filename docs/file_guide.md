# Comprehensive File-by-File Guide

This document provides a line-by-line inventory and functional guide for every file in the **Financial Early Warning System** repository.

---

## Directory Overview

```text
Early-Anomaly-Detection/
├── .env.example
├── docker-compose.yml
├── README.md
├── AI_CONTEXT.md
├── schemas/
│   └── transaction.avsc
├── data/
│   ├── .gitignore
│   ├── features.csv
│   └── transactions_raw.csv.dvc
├── models/
│   ├── .gitignore
│   └── pipeline.pkl.dvc
├── Backend/
│   ├── Dockerfile
│   ├── pom.xml
│   ├── mvnw / mvnw.cmd
│   └── src/
│       └── main/
│           ├── java/org/example/backend/
│           │   ├── BackendApplication.java
│           │   ├── Controller/
│           │   │   ├── WebhookController.java
│           │   │   └── AnomalyController.java
│           │   ├── config/
│           │   │   └── KafkaProducerConfig.java
│           │   ├── consumer/
│           │   │   └── AnomalyConsumer.java
│           │   ├── model/
│           │   │   ├── AnomalyEntity.java
│           │   │   ├── AnomalyResult.java
│           │   │   ├── Transaction.java
│           │   │   └── WebHookPayload.java
│           │   └── Repository/
│           │       └── AnomalyRepository.java
│           └── resources/
│               └── application.properties
└── ML-Pipeline/
    ├── Dockerfile
    ├── requirements.txt
    ├── data_generator.py
    ├── feature_engineering.py
    ├── train.py
    ├── kafka_producer_test.py
    └── inference_service.py
```

---

## Root Level Files

### 1. [docker-compose.yml](file:///d:/@Vatsal/Early-Anomaly-Detection/docker-compose.yml)
- **Why it exists**: Orchestrates all infrastructure services (ZooKeeper, Kafka, Schema Registry, PostgreSQL) and application microservices (`backend` Spring Boot app and `ml-inference` Python FastAPI service) using Docker.
- **What it does**:
  - `zookeeper`: Manages Kafka cluster state.
  - `kafka`: Event broker handling `transactions` and `anomalies` topics.
  - `schema-registry`: Stores Avro schemas for message serialization.
  - `postgres`: Relational database storing persistent anomaly flags and user scores on port `5433:5432`.
  - `backend`: Spring Boot Webhook API and DB Consumer.
  - `ml-inference`: FastAPI server & real-time streaming ML engine.

### 2. [.env.example](file:///d:/@Vatsal/Early-Anomaly-Detection/.env.example)
- **Why it exists**: Defines environment variable defaults for database credentials, ports, and Kafka broker URLs.
- **What it does**: Provides a copy-paste template for deployment environments.

### 3. [README.md](file:///d:/@Vatsal/Early-Anomaly-Detection/README.md)
- **Why it exists**: Main project documentation covering business context, value proposition, BFSI early warning use case, architecture overview, tech stack, and setup steps.

### 4. [AI_CONTEXT.md](file:///d:/@Vatsal/Early-Anomaly-Detection/AI_CONTEXT.md)
- **Why it exists**: Optimized single-file context document for AI coding assistants and LLMs to understand the codebase structure, APIs, schemas, and design patterns instantly.

---

## Schema & Data Management (`schemas/`, `data/`, `models/`)

### 5. [schemas/transaction.avsc](file:///d:/@Vatsal/Early-Anomaly-Detection/schemas/transaction.avsc)
- **Why it exists**: Apache Avro schema defining the standardized format for Account Aggregator transaction events.
- **Key Fields**: `transaction_id`, `user_id`, `account_id`, `timestamp`, `amount`, `transaction_type` (CREDIT/DEBIT), `narration`, `balance_after`, `bank_name`.

### 6. [data/features.csv](file:///d:/@Vatsal/Early-Anomaly-Detection/data/features.csv)
- **Why it exists**: Extracted training features generated from historical raw transactions.
- **Columns**: `user_id`, `ratio_inflow_outflow`, `emi_to_income_ratio`, `amb_drop_percentage`.

### 7. [data/transactions_raw.csv.dvc](file:///d:/@Vatsal/Early-Anomaly-Detection/data/transactions_raw.csv.dvc) & [models/pipeline.pkl.dvc](file:///d:/@Vatsal/Early-Anomaly-Detection/models/pipeline.pkl.dvc)
- **Why it exists**: DVC (Data Version Control) pointer files tracking large datasets and binary ML pipeline models without committing them directly into Git.

---

## Java Backend Microservice (`Backend/`)

### 8. [Backend/pom.xml](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/pom.xml)
- **Why it exists**: Maven project configuration specifying dependencies (Spring Boot 3.2.5, Spring Kafka, Spring Data JPA, PostgreSQL driver, Lombok, Validation).

### 9. [Backend/Dockerfile](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/Dockerfile)
- **Why it exists**: Multi-stage container build definition. Compiles the Java project using Maven 3.9 and runs the final JAR inside JDK 17 JRE environment.

### 10. [Backend/src/main/resources/application.properties](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/resources/application.properties)
- **Why it exists**: Spring Boot runtime properties configuring server port (`8080`), Kafka bootstrap servers, PostgreSQL JDBC connection, and JSON deserialization parameters.

### 11. [BackendApplication.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/BackendApplication.java)
- **Why it exists**: Spring Boot application main entry point annotated with `@SpringBootApplication`.

### 12. [WebhookController.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/Controller/WebhookController.java)
- **Why it exists**: REST Controller handling incoming financial transaction webhooks from Account Aggregators.
- **Endpoints**:
  - `POST /webhook/aa-fetch`: Validates incoming `WebHookPayload` and publishes it asynchronously to Kafka topic `transactions`.
  - `GET /webhook/health`: Health check endpoint.

### 13. [AnomalyController.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/Controller/AnomalyController.java)
- **Why it exists**: REST Controller serving detected financial anomalies to internal risk dashboards or underwriting teams.
- **Endpoints**:
  - `GET /anomalies`: Returns all detected anomalies recorded in PostgreSQL.
  - `GET /anomalies/{userId}`: Returns detected anomaly history for a specific borrower/user.

### 14. [KafkaProducerConfig.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/config/KafkaProducerConfig.java)
- **Why it exists**: Spring configuration bean setting up `KafkaTemplate<String, WebHookPayload>` with JSON serialization for sending webhooks to Kafka.

### 15. [AnomalyConsumer.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/consumer/AnomalyConsumer.java)
- **Why it exists**: Kafka event listener subscribing to the `anomalies` topic (`groupId = "java-anomaly-writer"`).
- **Functionality**: Receives `AnomalyResult` objects emitted by the ML Inference Service and persists them into PostgreSQL via `AnomalyRepository`.

### 16. Data Models & Entities
- **[WebHookPayload.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/model/WebHookPayload.java)**: DTO representing the incoming Account Aggregator payload (`consentId`, `userId`, `fetchTimestamp`, `bankName`, list of `Transaction`).
- **[Transaction.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/model/Transaction.java)**: DTO representing an individual bank statement transaction line item.
- **[AnomalyResult.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/model/AnomalyResult.java)**: DTO matching the JSON structure emitted by the ML inference pipeline.
- **[AnomalyEntity.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/model/AnomalyEntity.java)**: JPA Entity mapped to table `anomalies` storing detected risk signals.
- **[AnomalyRepository.java](file:///d:/@Vatsal/Early-Anomaly-Detection/Backend/src/main/java/org/example/backend/Repository/AnomalyRepository.java)**: Spring Data JPA repository extending `JpaRepository<AnomalyEntity, Long>` providing `findByUserId(...)`.

---

## Python ML & Streaming Pipeline (`ML-Pipeline/`)

### 17. [ML-Pipeline/requirements.txt](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/requirements.txt)
- **Why it exists**: Lists Python package requirements (`pandas`, `numpy`, `scikit-learn`, `mlflow`, `fastapi`, `uvicorn`, `confluent-kafka`, `pydantic`).

### 18. [ML-Pipeline/Dockerfile](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/Dockerfile)
- **Why it exists**: Docker container definition for Python 3.10 runtime environment, installing `librdkafka` C libraries and launching `inference_service.py`.

### 19. [data_generator.py](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/data_generator.py)
- **Why it exists**: Synthetic transaction generator simulating 180 days of realistic banking transactions across normal users and distinct financial anomaly archetypes (`job_loss`, `credit_stacking`, `amb_wipeout`). Writes output to `data/transactions_raw.csv`.

### 20. [feature_engineering.py](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/feature_engineering.py)
- **Why it exists**: Extracts domain-specific financial health metrics from raw transaction streams:
  - `ratio_inflow_outflow`: Inflow credits vs outflow debits.
  - `emi_to_income_ratio`: Estimated total EMI debits vs monthly salary income.
  - `amb_drop_percentage`: 7-day average monthly balance vs 90-day average monthly balance.

### 21. [train.py](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/train.py)
- **Why it exists**: Builds and trains an **Isolation Forest** anomaly detection model using scikit-learn (`StandardScaler` + `IsolationForest`).
- **Functionality**: Logs hyper-parameters and metrics to **MLflow** experiment `bfsi-anomaly-detection` and exports binary pipeline to `models/pipeline.pkl`.

### 22. [kafka_producer_test.py](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/kafka_producer_test.py)
- **Why it exists**: Simulation test script reading generated transactions for test users (`USER_ANOM_JL`, `USER_ANOM_AW`, `USER_ANOM_CS`, `USER_0000`) and pushing webhooks into Kafka topic `transactions` to simulate live Account Aggregator fetches.

### 23. [inference_service.py](file:///d:/@Vatsal/Early-Anomaly-Detection/ML-Pipeline/inference_service.py)
- **Why it exists**: Main production execution service for real-time ML inference.
- **Functionality**:
  - Launches a FastAPI web server on port `8000`.
  - Runs a background Kafka consumer listening to topic `transactions`.
  - Computes features dynamically, runs Isolation Forest model inference, classifies distress category (`JOB_LOSS_DISRUPT`, `CREDIT_STACKING`, `AMB_DRAINAGE`), and emits results to topic `anomalies`.
