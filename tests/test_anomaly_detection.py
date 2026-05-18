import pandas as pd

from src.anomaly_detection import detect_anomalies


def test_anomaly_detection_returns_reason_codes():
    frame = pd.DataFrame(
        {
            "exception_id": [f"E{i}" for i in range(40)],
            "exception_type": ["Price Outlier"] * 40,
            "domain": ["Pricing"] * 40,
            "source_system": ["Bloomberg"] * 40,
            "region": ["EMEA"] * 40,
            "asset_class": ["Equity"] * 40,
            "missing_field_count": [0] * 40,
            "age_days": list(range(40)),
            "break_amount": [1000 + i * 200 for i in range(40)],
            "price_movement_pct": [1.0] * 39 + [35.0],
            "duplicate_flag": [0] * 40,
            "currency_mismatch_flag": [0] * 40,
            "refresh_delay_hours": [2] * 39 + [90],
            "severity": ["Medium"] * 40,
        }
    )
    out = detect_anomalies(frame)
    assert {"anomaly_score", "anomaly_flag", "reason_code"}.issubset(out.columns)
    assert out["anomaly_flag"].sum() > 0
