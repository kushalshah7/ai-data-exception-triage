import pandas as pd

from src.feature_engineering import FEATURE_COLUMNS, build_exception_features


def test_feature_engineering_adds_operational_fields():
    frame = pd.DataFrame(
        {
            "exception_id": ["E1", "E2"],
            "exception_type": ["Stale Price", "Trade Match Break"],
            "domain": ["Pricing", "Trades"],
            "source_system": ["Bloomberg", "Aladdin"],
            "region": ["EMEA", "Americas"],
            "asset_class": ["Equity", "ETF"],
            "missing_field_count": [0, 1],
            "age_days": [3, 1],
            "break_amount": [1000, 50000],
            "price_movement_pct": [14.0, 1.2],
            "duplicate_flag": [0, 0],
            "currency_mismatch_flag": [0, 0],
            "refresh_delay_hours": [60, 4],
            "sla_hours": [48, 24],
        }
    )
    out = build_exception_features(frame)
    assert set(FEATURE_COLUMNS).issubset(out.columns)
    assert out.loc[0, "sla_status"] == "Breached"
    assert "recurrence_count" in out.columns
