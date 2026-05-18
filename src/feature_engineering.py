from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.config import PROCESSED_DIR, RAW_DIR

FEATURE_COLUMNS = [
    "domain",
    "source_system",
    "region",
    "asset_class",
    "missing_field_count",
    "age_days",
    "break_amount",
    "price_movement_pct",
    "duplicate_flag",
    "currency_mismatch_flag",
    "refresh_delay_hours",
]


def load_historical_exceptions() -> pd.DataFrame:
    path = RAW_DIR / "historical_exceptions.csv"
    if not path.exists():
        from src.generate_synthetic_data import generate

        generate()
    return pd.read_csv(path)


def build_exception_features(frame: pd.DataFrame | None = None) -> pd.DataFrame:
    df = load_historical_exceptions() if frame is None else frame.copy()
    for col in FEATURE_COLUMNS:
        if col not in df:
            df[col] = 0
    df["sla_status"] = (df["age_days"] * 24 > df.get("sla_hours", 48)).map({True: "Breached", False: "Within SLA"})
    df["recurrence_count"] = df.groupby(["exception_type", "source_system"])["exception_id"].transform("count")
    df["is_high_value_break"] = (df["break_amount"] >= df["break_amount"].quantile(0.85)).astype(int)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DIR / "exception_features.csv", index=False)
    return df


def model_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    return df[FEATURE_COLUMNS], df["exception_type"]


if __name__ == "__main__":
    features = build_exception_features()
    print(f"Built {len(features):,} exception feature rows")
