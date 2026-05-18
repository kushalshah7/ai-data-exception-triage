from src.smart_matching import normalize_text, score_match


def test_normalize_text_removes_noise():
    assert normalize_text("Apex-Capital, Inc.") == "APEX CAPITAL  INC"


def test_score_match_uses_exact_boosts():
    query = {"security_name": "Apex Capital Equity 2030", "ticker": "APX", "isin": "US123", "currency": "USD", "exchange": "NYSE"}
    candidate = dict(query)
    assert score_match(query, candidate) >= 95
