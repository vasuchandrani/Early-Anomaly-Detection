import pandas as pd
import numpy as np

def load_data(path="../data/transactions_raw.csv"):
    df = pd.read_csv(path, parse_dates=["timestamp"])
    return df

def compute_features(df):
    # financial health over the full 180-day window.
    results = []

    for user_id, group in df.groupby("user_id"):
        group = group.sort_values("timestamp")

        credits = group[group.transaction_type == "CREDIT"]
        debits  = group[group.transaction_type == "DEBIT"]

        # ── Feature 1: ratio_inflow_outflow ──────────────────
        total_in  = credits.amount.sum()
        total_out = debits.amount.sum()
        ratio_inflow_outflow = total_in / total_out if total_out > 0 else 999

        # ── Feature 2: emi_to_income_ratio ───────────────────
        emi_debits = debits[debits.narration.str.contains("EMI", case=False, na=False)]
        total_emi  = emi_debits.amount.sum()
        # Estimate monthly income: avg monthly SALARY credit
        salary_credits = credits[credits.narration.str.contains("SALARY", case=False, na=False)]
        monthly_income = salary_credits.amount.sum() / 6 if len(salary_credits) > 0 else 1
        emi_to_income_ratio = total_emi / monthly_income if monthly_income > 0 else 0

        # ── Feature 3: amb_drop_percentage ───────────────────
        # 7-day avg balance vs 90-day avg balance
        latest_date = group.timestamp.max()
        last_7  = group[group.timestamp >= latest_date - pd.Timedelta(days=7)]
        last_90 = group[group.timestamp >= latest_date - pd.Timedelta(days=90)]

        amb_7  = last_7.balance_after.mean()  if len(last_7)  > 0 else 0
        amb_90 = last_90.balance_after.mean() if len(last_90) > 0 else 1
        amb_drop_percentage = (amb_90 - amb_7) / amb_90 if amb_90 > 0 else 0

        results.append({
            "user_id":              user_id,
            "ratio_inflow_outflow": round(ratio_inflow_outflow, 4),
            "emi_to_income_ratio":  round(emi_to_income_ratio, 4),
            "amb_drop_percentage":  round(amb_drop_percentage, 4),
        })

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = load_data()
    features = compute_features(df)
    features.to_csv("../data/features.csv", index=False)

    print(features.to_string())
    print(f"\nSaved {len(features)} user feature rows to data/features.csv")
