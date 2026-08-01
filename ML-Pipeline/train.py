import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import mlflow
import mlflow.sklearn
import pickle, os

FEATURES = ["ratio_inflow_outflow", "emi_to_income_ratio", "amb_drop_percentage"]

def train(contamination=0.05, n_estimators=100, random_state=42):
    df = pd.read_csv("../data/features.csv")
    X  = df[FEATURES]

    mlflow.set_experiment("bfsi-anomaly-detection")

    with mlflow.start_run(run_name=f"isolation_forest_c{contamination}"):

        # Log params
        mlflow.log_param("contamination",  contamination)
        mlflow.log_param("n_estimators",   n_estimators)
        mlflow.log_param("random_state",   random_state)
        mlflow.log_param("training_users", len(df))

        # Build pipeline: scale → model
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("model",  IsolationForest(
                contamination=contamination,
                n_estimators=n_estimators,
                random_state=random_state
            ))
        ])

        pipeline.fit(X)

        # Predict — -1 anomaly, 1 normal
        df["prediction"] = pipeline.predict(X)
        df["anomaly_score"] = pipeline.named_steps["model"].score_samples(
            pipeline.named_steps["scaler"].transform(X)
        )

        anomalies = df[df.prediction == -1]

        # Log metrics
        anomaly_rate = len(anomalies) / len(df)
        mlflow.log_metric("anomaly_rate",   round(anomaly_rate, 4))
        mlflow.log_metric("anomalies_found", len(anomalies))

        # Log model
        mlflow.sklearn.log_model(pipeline, "isolation_forest_pipeline")

        # Save locally too
        os.makedirs("../models", exist_ok=True)
        with open("../models/pipeline.pkl", "wb") as f:
            pickle.dump(pipeline, f)

        print("=" * 50)
        print(f"Training complete — {len(anomalies)} anomalies detected")
        print("=" * 50)
        print(anomalies[["user_id", "prediction", "anomaly_score",
                          "ratio_inflow_outflow", "emi_to_income_ratio",
                          "amb_drop_percentage"]].to_string())
        print(f"\nMLflow run logged. Start UI with: mlflow ui")

if __name__ == "__main__":
    train()
