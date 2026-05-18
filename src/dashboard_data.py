from __future__ import annotations

import json

import pandas as pd

from src.config import PROCESSED_DIR, RAW_DIR
from src.triage_engine import run_triage


def ensure_outputs() -> None:
    if not (PROCESSED_DIR / "triaged_exceptions.csv").exists():
        run_triage()


def load_triage() -> pd.DataFrame:
    ensure_outputs()
    return pd.read_csv(PROCESSED_DIR / "triaged_exceptions.csv")


def load_anomalies() -> pd.DataFrame:
    ensure_outputs()
    return pd.read_csv(PROCESSED_DIR / "anomaly_scores.csv")


def load_matches() -> pd.DataFrame:
    ensure_outputs()
    return pd.read_csv(PROCESSED_DIR / "smart_match_results.csv")


def load_metrics() -> tuple[pd.DataFrame, dict]:
    ensure_outputs()
    metrics = pd.read_csv(PROCESSED_DIR / "model_metrics.csv")
    summary_path = PROCESSED_DIR / "model_summary.json"
    summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    return metrics, summary


def load_prices() -> pd.DataFrame:
    ensure_outputs()
    return pd.read_csv(RAW_DIR / "prices.csv", parse_dates=["price_date"])
