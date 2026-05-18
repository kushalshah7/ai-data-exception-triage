import pandas as pd

from src.triage_engine import owner_for, priority_score


def test_owner_routing_for_pricing():
    row = pd.Series({"domain": "Pricing"})
    assert owner_for(row) == "Pricing Control"


def test_priority_score_increases_for_breached_critical_item():
    row = pd.Series(
        {
            "severity": "Critical",
            "sla_status": "Breached",
            "break_amount": 500000,
            "recurrence_count": 300,
            "confidence_score": 0.55,
        }
    )
    assert priority_score(row) > 85
