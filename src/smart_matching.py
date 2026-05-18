from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from rapidfuzz import fuzz, process

from src.config import PROCESSED_DIR, RAW_DIR


def normalize_text(value: str) -> str:
    return re.sub(r"[^A-Z0-9 ]+", " ", str(value).upper()).strip()


def score_match(query: dict, candidate: dict) -> float:
    name_score = fuzz.token_set_ratio(normalize_text(query.get("security_name", "")), normalize_text(candidate.get("security_name", "")))
    ticker_boost = 12 if str(query.get("ticker", "")).upper() == str(candidate.get("ticker", "")).upper() else 0
    isin_boost = 18 if pd.notna(query.get("isin")) and query.get("isin") == candidate.get("isin") else 0
    currency_boost = 5 if query.get("currency") == candidate.get("currency") else 0
    exchange_boost = 5 if query.get("exchange") == candidate.get("exchange") else 0
    return min(100.0, round(name_score * 0.72 + ticker_boost + isin_boost + currency_boost + exchange_boost, 2))


def run_smart_matching(limit: int = 80) -> pd.DataFrame:
    path = RAW_DIR / "securities.csv"
    if not path.exists():
        from src.generate_synthetic_data import generate

        generate()
    securities = pd.read_csv(path)
    candidates = securities.dropna(subset=["isin"]).reset_index(drop=True)
    queries = securities.sample(min(limit, len(securities)), random_state=4).copy()
    queries["security_name"] = queries["security_name"].str.replace("Capital", "Cap", regex=False).str.replace("Bond", "Bd", regex=False)
    queries.loc[queries.index[: max(1, len(queries) // 8)], "ticker"] = queries["ticker"].astype(str) + ".X"
    choices = candidates["security_name"].map(normalize_text).tolist()
    rows = []
    for _, query in queries.iterrows():
        _, fuzzy_score, match_idx = process.extractOne(normalize_text(query["security_name"]), choices, scorer=fuzz.token_set_ratio)
        candidate = candidates.iloc[match_idx]
        confidence = score_match(query.to_dict(), candidate.to_dict())
        rows.append(
            {
                "query_security_id": query["security_id"],
                "query_name": query["security_name"],
                "matched_security_id": candidate["security_id"],
                "candidate_name": candidate["security_name"],
                "fuzzy_name_score": round(float(fuzzy_score), 2),
                "match_confidence": confidence,
                "exact_ticker_match": str(query["ticker"]).upper() == str(candidate["ticker"]).upper(),
                "currency_match": query["currency"] == candidate["currency"],
                "review_needed": confidence < 82,
            }
        )
    out = pd.DataFrame(rows)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(PROCESSED_DIR / "smart_match_results.csv", index=False)
    return out


if __name__ == "__main__":
    matches = run_smart_matching()
    print(f"Generated {len(matches)} smart match candidates")
