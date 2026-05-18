from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.config import MODELS_DIR, PROCESSED_DIR
from src.feature_engineering import build_exception_features


def detect_anomalies(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    df = build_exception_features() if frame is None else frame.copy()
    cols = ["break_amount", "price_movement_pct", "age_days", "refresh_delay_hours"]
    X = df[cols].fillna(0)
    scaler = StandardScaler()
    model = IsolationForest(contamination=0.12, random_state=42)
    scaled = scaler.fit_transform(X)
    model.fit(scaled)
    decision = model.decision_function(scaled)
    out = df[["exception_id", "exception_type", "domain", "severity"] + cols].copy()
    out["anomaly_score"] = np.round((decision.max() - decision) / max(decision.max() - decision.min(), 1e-9), 4)
    out["anomaly_flag"] = model.predict(scaled) == -1
    out["reason_code"] = np.select(
        [
            out["price_movement_pct"].abs() > 12,
            out["break_amount"] > out["break_amount"].quantile(0.9),
            out["refresh_delay_hours"] > 48,
            out["age_days"] > 12,
        ],
        ["Large price/return move", "High-value reconciliation break", "Late source refresh", "Aging unresolved item"],
        default="Multi-factor isolation signal",
    )
    out["severity_recommendation"] = np.where(out["anomaly_score"] > 0.78, "Critical", np.where(out["anomaly_score"] > 0.55, "High", out["severity"]))
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODELS_DIR / "anomaly_detector.joblib")
    out.to_csv(PROCESSED_DIR / "anomaly_scores.csv", index=False)
    return out


if __name__ == "__main__":
    anomalies = detect_anomalies()
    print(f"Flagged {int(anomalies.anomaly_flag.sum())} anomalies")
