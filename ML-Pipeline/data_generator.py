import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta

def _txn(user_id, date, amount, txn_type, narration, balance):
    return {
        "transaction_id": str(uuid.uuid4()),
        "user_id": user_id,
        "account_id": f"ACC{user_id[-4:]}",
        "timestamp": date.isoformat(),
        "amount": round(abs(amount), 2),
        "transaction_type": txn_type,
        "narration": narration,
        "balance_after": round(balance, 2),
        "bank_name": "HDFC"
    }

def generate_user_profile(user_id, inject_anomaly=None):
    transactions = []
    base_date = datetime(2024, 7, 1)
    balance = 85000.0
    np.random.seed(abs(hash(user_id)) % 10000)

    upi_merchants = [
        "UPI/SWIGGY FOOD", "UPI/ZOMATO ORDER", "UPI/AMAZON PAY",
        "UPI/PHONEPE FUEL", "UPI/BIGBASKET", "UPI/UBER RIDE",
        "UPI/NETFLIX SUB", "UPI/MEDICAL STORE", "UPI/DMART RETAIL"
    ]

    for day_offset in range(180):
        date = base_date + timedelta(days=day_offset)
        day = date.day

        # Salary on 1st
        if day == 1:
            amt = np.random.normal(75000, 2000)
            if inject_anomaly == "job_loss" and day_offset > 120:
                amt = np.random.normal(12000, 1000)
            balance += amt
            transactions.append(_txn(user_id, date, amt, "CREDIT", "SALARY CREDIT EMPLOYER", balance))

        # EMI on 5th and 20th
        if day in [5, 20]:
            emi_amt = 18500
            if inject_anomaly == "credit_stacking" and 90 < day_offset < 106:
                emi_amt += int(np.random.choice([12000, 15000, 9500]))
            balance -= emi_amt
            transactions.append(_txn(user_id, date, emi_amt, "DEBIT", "EMI PAYMENT HDFC LOAN", balance))

        # Utility on 10th
        if day == 10:
            amt = np.random.normal(3200, 300)
            balance -= amt
            transactions.append(_txn(user_id, date, amt, "DEBIT", "BESCOM ELECTRICITY BILL", balance))

        # Daily UPI spends (1-3 per day, skip ~20% of days)
        if np.random.random() > 0.2:
            n_spends = np.random.randint(1, 4)
            for _ in range(n_spends):
                amt = np.random.exponential(400)
                amt = min(amt, 3000)
                balance -= amt
                merchant = np.random.choice(upi_merchants)
                transactions.append(_txn(user_id, date, amt, "DEBIT", merchant, balance))

        # Occasional UPI inflow (freelance/transfer) ~5% of days
        if np.random.random() < 0.05:
            amt = np.random.uniform(500, 8000)
            balance += amt
            transactions.append(_txn(user_id, date, amt, "CREDIT", "UPI CREDIT FROM FRIEND", balance))

        # AMB wipeout on day 150
        if inject_anomaly == "amb_wipeout" and day_offset == 150:
            wipeout = balance * 0.91
            balance -= wipeout
            transactions.append(_txn(user_id, date, wipeout, "DEBIT",
                                     "IMPS TRANSFER TO UNKNOWN ACC 9XXXXXXX", balance))

    return transactions

if __name__ == "__main__":
    all_txns = []

    for i in range(20):
        all_txns.extend(generate_user_profile(f"USER_{i:04d}"))

    all_txns.extend(generate_user_profile("USER_ANOM_JL", "job_loss"))
    all_txns.extend(generate_user_profile("USER_ANOM_CS", "credit_stacking"))
    all_txns.extend(generate_user_profile("USER_ANOM_AW", "amb_wipeout"))

    df = pd.DataFrame(all_txns)
    df.to_csv("../data/transactions_raw.csv", index=False)

    print(f"Generated {len(df)} transactions for {df['user_id'].nunique()} users")
    print(f"CREDIT rows : {len(df[df.transaction_type == 'CREDIT'])}")
    print(f"DEBIT rows  : {len(df[df.transaction_type == 'DEBIT'])}")
    print(f"Anomaly users: {[u for u in df.user_id.unique() if 'ANOM' in u]}")
