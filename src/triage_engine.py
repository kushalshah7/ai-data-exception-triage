from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import pandas as pd

from src.anomaly_detection import detect_anomalies
from src.config import MODELS_DIR, PROCESSED_DIR, SEVERITY_WEIGHTS
from src.feature_engineering import FEATURE_COLUMNS, build_exception_features
from src.smart_matching import run_smart_matching
from src.summarizer import explain_exception, recommended_action
from src.train_exception_classifier import train


def owner_for(row: pd.Series) -> str:
    if row["domain"] == "Pricing":
        return "Pricing Control"
    if row["domain"] == "Trades":
        return "Trade Support"
    if row["domain"] == "Positions":
        return "Reconciliation"
    if row["domain"] == "Client Data":
        return "Client Data Ops"
    if row["domain"] == "Source Control":
        return "Source Systems"
    return "Reference Data Ops"


def priority_score(row: pd.Series) -> float:
    severity_weight = SEVERITY_WEIGHTS.get(str(row.get("severity")), 2) / 4
    sla_weight = 1.0 if row.get("sla_status") == "Breached" else 0.2
    break_weight = min(float(row.get("break_amount", 0)) / 250000, 1.0)
    recurrence_weight = min(float(row.get("recurrence_count", 1)) / 250, 1.0)
    confidence_adjustment = 1 - float(row.get("confidence_score", 0.75))
    score = (severity_weight * 0.35 + sla_weight * 0.25 + break_weight * 0.20 + recurrence_weight * 0.10 + confidence_adjustment * 0.10) * 100
    return round(float(score), 1)


def run_triage() -> pd.DataFrame:
    if not (MODELS_DIR / "exception_classifier.joblib").exists():
        train()
    df = build_exception_features()
    model = joblib.load(MODELS_DIR / "exception_classifier.joblib")
    X = df[FEATURE_COLUMNS]
    df["predicted_exception_type"] = model.predict(X)
    if hasattr(model.named_steps["model"], "predict_proba"):
        df["confidence_score"] = np.round(model.predict_proba(X).max(axis=1), 3)
    else:
        df["confidence_score"] = 0.75
    df["owner_recommendation"] = df.apply(owner_for, axis=1)
    df["root_cause_hint"] = df["predicted_exception_type"].map(lambda x: f"Most similar historical pattern: {x}")
    df["recommended_action"] = df.apply(lambda row: recommended_action(row.to_dict()), axis=1)
    df["sme_review_flag"] = (df["confidence_score"] < 0.72) | (df["predicted_exception_type"] == "Unknown / Needs SME Review")
    df["priority_score"] = df.apply(priority_score, axis=1)
    df["explainability_summary"] = df.apply(lambda row: explain_exception(row.to_dict()), axis=1)
    anomalies = detect_anomalies(df)
    anomaly_cols = ["exception_id", "anomaly_score", "anomaly_flag", "reason_code", "severity_recommendation"]
    df = df.merge(anomalies[anomaly_cols], on="exception_id", how="left")
    df.to_csv(PROCESSED_DIR / "triaged_exceptions.csv", index=False)
    run_smart_matching()
    return df


if __name__ == "__main__":
    triaged = run_triage()
    print(f"Triaged {len(triaged):,} exceptions into {PROCESSED_DIR / 'triaged_exceptions.csv'}")
