import os
import sys
import json
import time
import uuid
import logging
import pickle
import threading
import pandas as pd
import numpy as np
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from confluent_kafka import Consumer, Producer, KafkaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("inference_service")

# Configurations
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
INPUT_TOPIC = os.getenv("KAFKA_INPUT_TOPIC", "transactions")
OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "anomalies")
CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "ml-inference-group")
MODEL_PATH = os.getenv("MODEL_PATH", "../models/pipeline.pkl")

# FastAPI App
app = FastAPI(
    title="Financial Early Warning System - Inference Service",
    description="Real-time ML inference service for Account Aggregator transaction streams",
    version="1.0.0"
)

# Shared State
model_pipeline = None
processed_count = 0
anomalies_detected = 0

def load_or_train_model():
    global model_pipeline
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, "rb") as f:
                model_pipeline = pickle.load(f)
            logger.info(f"Loaded ML pipeline model from {MODEL_PATH}")
            return
        except Exception as e:
            logger.warning(f"Could not load model from {MODEL_PATH}: {e}")

    logger.info("Attempting to run training pipeline to build model...")
    try:
        from train import train as run_training
        run_training()
        with open(MODEL_PATH, "rb") as f:
            model_pipeline = pickle.load(f)
        logger.info("Model successfully trained and loaded.")
    except Exception as e:
        logger.error(f"Failed to auto-train model: {e}")

def compute_features_from_payload(user_id: str, transactions: list) -> pd.DataFrame:
    df = pd.DataFrame(transactions)
    if df.empty:
        return pd.DataFrame()

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        df["timestamp"] = pd.to_datetime("now")

    credits = df[df["transactionType"] == "CREDIT"] if "transactionType" in df.columns else df[df["transaction_type"] == "CREDIT"]
    debits  = df[df["transactionType"] == "DEBIT"]  if "transactionType" in df.columns else df[df["transaction_type"] == "DEBIT"]

    total_in = credits["amount"].sum() if not credits.empty else 0.0
    total_out = debits["amount"].sum() if not debits.empty else 0.0
    ratio_inflow_outflow = total_in / total_out if total_out > 0 else 999.0

    emi_debits = debits[debits["narration"].str.contains("EMI", case=False, na=False)] if not debits.empty else pd.DataFrame()
    total_emi = emi_debits["amount"].sum() if not emi_debits.empty else 0.0

    salary_credits = credits[credits["narration"].str.contains("SALARY", case=False, na=False)] if not credits.empty else pd.DataFrame()
    monthly_income = salary_credits["amount"].sum() / 6.0 if not salary_credits.empty else 1.0
    emi_to_income_ratio = total_emi / monthly_income if monthly_income > 0 else 0.0

    latest_date = df["timestamp"].max()
    last_7 = df[df["timestamp"] >= latest_date - pd.Timedelta(days=7)]
    last_90 = df[df["timestamp"] >= latest_date - pd.Timedelta(days=90)]

    amb_7 = last_7["balanceAfter"].mean() if "balanceAfter" in last_7.columns and not last_7.empty else (last_7["balance_after"].mean() if "balance_after" in last_7.columns and not last_7.empty else 0.0)
    amb_90 = last_90["balanceAfter"].mean() if "balanceAfter" in last_90.columns and not last_90.empty else (last_90["balance_after"].mean() if "balance_after" in last_90.columns and not last_90.empty else 1.0)
    amb_drop_percentage = (amb_90 - amb_7) / amb_90 if amb_90 > 0 else 0.0

    return pd.DataFrame([{
        "user_id": user_id,
        "ratio_inflow_outflow": float(round(ratio_inflow_outflow, 4)),
        "emi_to_income_ratio": float(round(emi_to_income_ratio, 4)),
        "amb_drop_percentage": float(round(amb_drop_percentage, 4))
    }])

def classify_anomaly_type(ratio_in, emi_ratio, amb_drop) -> str:
    if amb_drop > 0.5:
        return "AMB_DRAINAGE"
    elif emi_ratio > 0.6:
        return "CREDIT_STACKING"
    elif ratio_in < 0.3:
        return "JOB_LOSS_DISRUPT"
    else:
        return "FINANCIAL_DISTRESS"

def process_and_publish(producer, payload: dict):
    global processed_count, anomalies_detected

    user_id = payload.get("userId", "UNKNOWN")
    transactions = payload.get("transactions", [])

    if not transactions:
        return

    feat_df = compute_features_from_payload(user_id, transactions)
    if feat_df.empty:
        return

    features = ["ratio_inflow_outflow", "emi_to_income_ratio", "amb_drop_percentage"]
    X = feat_df[features]

    if model_pipeline is None:
        logger.error("Model pipeline is not initialized!")
        return

    pred = model_pipeline.predict(X)[0] # -1 anomaly, 1 normal
    raw_score = model_pipeline.named_steps["model"].score_samples(
        model_pipeline.named_steps["scaler"].transform(X)
    )[0]

    # Convert score to positive anomaly index (higher = more anomalous)
    anomaly_score = float(round(-raw_score, 4))
    processed_count += 1

    ratio_in = float(feat_df["ratio_inflow_outflow"].iloc[0])
    emi_ratio = float(feat_df["emi_to_income_ratio"].iloc[0])
    amb_drop = float(feat_df["amb_drop_percentage"].iloc[0])

    is_anomaly = (pred == -1)
    if is_anomaly:
        anomalies_detected += 1
        anomaly_type = classify_anomaly_type(ratio_in, emi_ratio, amb_drop)
    else:
        anomaly_type = "NORMAL"

    result_payload = {
        "userId": user_id,
        "anomalyType": anomaly_type,
        "anomalyScore": anomaly_score,
        "ratioInflowOutflow": ratio_in,
        "emiToIncomeRatio": emi_ratio,
        "ambDropPercentage": amb_drop,
        "transactionCount": len(transactions),
        "detectedAt": datetime.now().isoformat()
    }

    if producer:
        producer.produce(
            OUTPUT_TOPIC,
            key=user_id,
            value=json.dumps(result_payload).encode("utf-8")
        )
        producer.flush()
        logger.info(f"Published AnomalyResult for userId={user_id} type={anomaly_type} score={anomaly_score}")

def kafka_consumer_loop():
    logger.info(f"Starting Kafka Consumer thread connecting to {KAFKA_BOOTSTRAP}...")
    consumer = None
    producer = None

    while True:
        try:
            consumer = Consumer({
                "bootstrap.servers": KAFKA_BOOTSTRAP,
                "group.id": CONSUMER_GROUP,
                "auto.offset.reset": "earliest"
            })
            producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})
            consumer.subscribe([INPUT_TOPIC])
            logger.info(f"Kafka consumer successfully subscribed to topic '{INPUT_TOPIC}'")
            break
        except Exception as e:
            logger.warning(f"Kafka not ready yet ({e}). Retrying in 5 seconds...")
            time.sleep(5)

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    logger.error(f"Kafka consumer error: {msg.error()}")
                continue

            payload = json.loads(msg.value().decode("utf-8"))
            process_and_publish(producer, payload)
        except Exception as e:
            logger.error(f"Error processing Kafka message: {e}")
            time.sleep(1)

# API Models
class TransactionItem(BaseModel):
    transactionId: str
    userId: str
    accountId: str
    timestamp: str
    amount: float
    transactionType: str
    narration: str
    balanceAfter: float
    bankName: str

class PredictRequest(BaseModel):
    consentId: str
    userId: str
    fetchTimestamp: str
    bankName: str
    transactions: List[TransactionItem]

@app.on_event("startup")
def startup_event():
    load_or_train_model()
    # Launch Kafka Consumer thread
    thread = threading.Thread(target=kafka_consumer_loop, daemon=True)
    thread.start()

@app.get("/health")
def health():
    return {
        "status": "UP",
        "model_loaded": model_pipeline is not None,
        "processed_count": processed_count,
        "anomalies_detected": anomalies_detected
    }

@app.post("/predict")
def predict_adhoc(req: PredictRequest):
    if model_pipeline is None:
        raise HTTPException(status_code=503, detail="ML model pipeline not initialized")

    payload = req.model_dump()
    feat_df = compute_features_from_payload(req.userId, payload["transactions"])
    features = ["ratio_inflow_outflow", "emi_to_income_ratio", "amb_drop_percentage"]
    X = feat_df[features]

    pred = model_pipeline.predict(X)[0]
    raw_score = model_pipeline.named_steps["model"].score_samples(
        model_pipeline.named_steps["scaler"].transform(X)
    )[0]

    anomaly_score = float(round(-raw_score, 4))
    ratio_in = float(feat_df["ratio_inflow_outflow"].iloc[0])
    emi_ratio = float(feat_df["emi_to_income_ratio"].iloc[0])
    amb_drop = float(feat_df["amb_drop_percentage"].iloc[0])

    anomaly_type = classify_anomaly_type(ratio_in, emi_ratio, amb_drop) if pred == -1 else "NORMAL"

    return {
        "userId": req.userId,
        "isAnomaly": bool(pred == -1),
        "anomalyType": anomaly_type,
        "anomalyScore": anomaly_score,
        "features": {
            "ratioInflowOutflow": ratio_in,
            "emiToIncomeRatio": emi_ratio,
            "ambDropPercentage": amb_drop
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
