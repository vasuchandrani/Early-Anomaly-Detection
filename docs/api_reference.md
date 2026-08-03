# API Specification Reference

This document details all HTTP REST API endpoints exposed by the **Java Spring Boot Backend** and **Python FastAPI ML Inference Service**.

---

## 1. Java Spring Boot Webhook API (`port 8080`)

### `POST /webhook/aa-fetch`
Ingests an Account Aggregator transaction fetch payload and queues it onto Kafka topic `transactions`.

#### Request Headers
`Content-Type: application/json`

#### Request Body Schema (`WebHookPayload`)
```json
{
  "consentId": "c8d4a1b2-3e4f-5a6b-7c8d-9e0f1a2b3c4d",
  "userId": "USER_ANOM_JL",
  "fetchTimestamp": "2024-12-31T00:00:00",
  "bankName": "HDFC",
  "transactions": [
    {
      "transactionId": "txn-001",
      "userId": "USER_ANOM_JL",
      "accountId": "ACC0001",
      "timestamp": "2024-12-01T10:30:00",
      "amount": 18500.0,
      "transactionType": "DEBIT",
      "narration": "EMI PAYMENT HDFC LOAN",
      "balanceAfter": 66500.0,
      "bankName": "HDFC"
    }
  ]
}
```

#### Response (`200 OK`)
```json
{
  "status": "queued",
  "userId": "USER_ANOM_JL",
  "transactionCount": 1
}
```

---

### `GET /webhook/health`
Health check for Webhook service.

#### Response (`200 OK`)
```json
{
  "status": "UP"
}
```

---

## 2. Java Spring Boot Anomaly Query API (`port 8080`)

### `GET /anomalies`
Retrieves all detected financial anomaly records stored in PostgreSQL.

#### Response (`200 OK`)
```json
[
  {
    "id": 1,
    "userId": "USER_ANOM_JL",
    "anomalyType": "JOB_LOSS_DISRUPT",
    "anomalyScore": 0.1845,
    "ratioInflowOutflow": 0.1624,
    "emiToIncomeRatio": 0.8521,
    "ambDropPercentage": 0.3412,
    "transactionCount": 142,
    "detectedAt": "2026-08-04T02:00:00"
  }
]
```

---

### `GET /anomalies/{userId}`
Retrieves financial anomaly records for a specific user ID.

#### Response (`200 OK`)
```json
[
  {
    "id": 1,
    "userId": "USER_ANOM_JL",
    "anomalyType": "JOB_LOSS_DISRUPT",
    "anomalyScore": 0.1845,
    "ratioInflowOutflow": 0.1624,
    "emiToIncomeRatio": 0.8521,
    "ambDropPercentage": 0.3412,
    "transactionCount": 142,
    "detectedAt": "2026-08-04T02:00:00"
  }
]
```

---

## 3. Python FastAPI ML Inference API (`port 8000`)

### `GET /health`
Health check for ML Inference Engine and background Kafka Consumer.

#### Response (`200 OK`)
```json
{
  "status": "UP",
  "model_loaded": true,
  "processed_count": 42,
  "anomalies_detected": 3
}
```

---

### `POST /predict`
Executes real-time ad-hoc ML inference for an incoming transaction batch without queuing to Kafka.

#### Request Body Schema
Same as `WebHookPayload` above.

#### Response (`200 OK`)
```json
{
  "userId": "USER_ANOM_JL",
  "isAnomaly": true,
  "anomalyType": "JOB_LOSS_DISRUPT",
  "anomalyScore": 0.1845,
  "features": {
    "ratioInflowOutflow": 0.1624,
    "emiToIncomeRatio": 0.8521,
    "ambDropPercentage": 0.3412
  }
}
```
