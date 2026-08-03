import pandas as pd
import json
from confluent_kafka import Producer
import uuid

producer = Producer({"bootstrap.servers": "localhost:9092"})

def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")

def send_user(user_id: str):
    df = pd.read_csv("../data/transactions_raw.csv")
    user_txns = df[df["user_id"] == user_id].copy()

    if user_txns.empty:
        print(f"No transactions found for {user_id}")
        return

    transactions = []
    for _, row in user_txns.iterrows():
        transactions.append({
            "transactionId":   row["transaction_id"],
            "userId":          row["user_id"],
            "accountId":       row["account_id"],
            "timestamp":       row["timestamp"],
            "amount":          float(row["amount"]),
            "transactionType": row["transaction_type"],
            "narration":       row["narration"],
            "balanceAfter":    float(row["balance_after"]),
            "bankName":        row["bank_name"]
        })

    payload = {
        "consentId":      str(uuid.uuid4()),
        "userId":         user_id,
        "fetchTimestamp": "2024-12-31T00:00:00",
        "bankName":       "HDFC",
        "transactions":   transactions
    }

    producer.produce(
        "transactions",
        key=user_id,
        value=json.dumps(payload).encode("utf-8"),
        callback=delivery_report
    )
    producer.flush()
    print(f"Sent {len(transactions)} transactions for {user_id}")

if __name__ == "__main__":
    # Send all 3 anomaly users + 2 normal users for comparison
    for uid in ["USER_ANOM_JL", "USER_ANOM_AW", "USER_ANOM_CS", "USER_0000", "USER_0001"]:
        send_user(uid)
