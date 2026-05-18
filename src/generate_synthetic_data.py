from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from src.config import DATA_DIR, EXCEPTION_TYPES, PROCESSED_DIR, RANDOM_SEED, RAW_DIR


def _isin(i: int) -> str:
    return f"US{1000000000 + i:010d}"


def generate(seed: int = RANDOM_SEED, n_securities: int = 320, n_exceptions: int = 1400) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    asset_classes = ["Equity", "Corporate Bond", "Government Bond", "ETF", "Derivative"]
    currencies = ["USD", "EUR", "GBP", "JPY", "INR", "CAD"]
    regions = ["Americas", "EMEA", "APAC"]
    exchanges = ["NYSE", "NASDAQ", "LSE", "XETRA", "TSE", "NSE"]
    issuers = ["Apex Capital", "Northstar", "Blue Harbor", "Zenith", "Riverstone", "Atlas"]
    security_ids = [f"SEC{i:05d}" for i in range(n_securities)]

    securities = pd.DataFrame(
        {
            "security_id": security_ids,
            "isin": [_isin(i) for i in range(n_securities)],
            "ticker": [f"{chr(65 + i % 26)}{chr(65 + (i // 3) % 26)}{i % 997}" for i in range(n_securities)],
            "security_name": [f"{rng.choice(issuers)} {rng.choice(asset_classes)} {2028 + i % 12}" for i in range(n_securities)],
            "asset_class": rng.choice(asset_classes, n_securities, p=[0.38, 0.22, 0.18, 0.14, 0.08]),
            "currency": rng.choice(currencies, n_securities, p=[0.42, 0.17, 0.12, 0.08, 0.15, 0.06]),
            "exchange": rng.choice(exchanges, n_securities),
            "issuer": rng.choice(issuers, n_securities),
            "region": rng.choice(regions, n_securities, p=[0.42, 0.30, 0.28]),
        }
    )
    missing_idx = rng.choice(securities.index, size=14, replace=False)
    securities.loc[missing_idx, "isin"] = np.nan

    n_trades = 2200
    trade_sec = rng.choice(security_ids, n_trades)
    trades = pd.DataFrame(
        {
            "trade_id": [f"TRD{i:07d}" for i in range(n_trades)],
            "trade_date": [datetime.today().date() - timedelta(days=int(x)) for x in rng.integers(0, 45, n_trades)],
            "settlement_date": [datetime.today().date() - timedelta(days=int(x)) + timedelta(days=2) for x in rng.integers(0, 45, n_trades)],
            "security_id": trade_sec,
            "client_id": [f"CL{rng.integers(100, 999)}" for _ in range(n_trades)],
            "portfolio": [f"PORT-{rng.integers(1, 80):03d}" for _ in range(n_trades)],
            "quantity": rng.normal(18000, 7500, n_trades).round(0),
            "trade_price": rng.lognormal(4.2, 0.35, n_trades).round(2),
            "trade_currency": rng.choice(currencies, n_trades),
            "status": rng.choice(["Booked", "Matched", "Unmatched", "Cancelled"], n_trades, p=[0.42, 0.42, 0.13, 0.03]),
            "source_system": rng.choice(["Aladdin", "SimCorp", "Bloomberg AIM", "Murex"], n_trades),
        }
    )
    trades.loc[rng.choice(trades.index, 32, replace=False), "security_id"] = "UNKNOWN"
    trades.loc[rng.choice(trades.index, 18, replace=False), "quantity"] *= -1
    trades = pd.concat([trades, trades.sample(18, random_state=seed)], ignore_index=True)

    n_positions = 1100
    positions = pd.DataFrame(
        {
            "position_id": [f"POS{i:07d}" for i in range(n_positions)],
            "as_of_date": [datetime.today().date() - timedelta(days=int(x)) for x in rng.integers(0, 6, n_positions)],
            "client_id": [f"CL{rng.integers(100, 999)}" for _ in range(n_positions)],
            "portfolio": [f"PORT-{rng.integers(1, 80):03d}" for _ in range(n_positions)],
            "security_id": rng.choice(security_ids, n_positions),
            "quantity": rng.normal(50000, 22000, n_positions).round(0),
            "market_value": rng.lognormal(12.0, 0.6, n_positions).round(2),
            "source_system": rng.choice(["Custodian", "IBOR", "ABOR"], n_positions),
            "base_currency": rng.choice(currencies, n_positions),
        }
    )

    price_dates = pd.date_range(datetime.today().date() - timedelta(days=60), periods=61, freq="D")
    price_rows = []
    for sec in security_ids[:180]:
        base = float(rng.lognormal(4.0, 0.45))
        series = base * np.cumprod(1 + rng.normal(0.0005, 0.018, len(price_dates)))
        if rng.random() < 0.16:
            series[rng.integers(15, len(series))] *= rng.choice([0.72, 1.38])
        for date, price in zip(price_dates, series):
            price_rows.append((sec, date.date(), round(price, 2), rng.choice(["Bloomberg", "Refinitiv", "ICE"]), rng.choice(currencies)))
    prices = pd.DataFrame(price_rows, columns=["security_id", "price_date", "close_price", "vendor", "currency"])
    stale_secs = rng.choice(security_ids[:180], 18, replace=False)
    prices = prices[~((prices.security_id.isin(stale_secs)) & (pd.to_datetime(prices.price_date) > pd.Timestamp.today() - pd.Timedelta(days=4)))]

    domains = ["Reference Data", "Trades", "Positions", "Pricing", "Client Data", "Source Control"]
    source_systems = ["Aladdin", "SimCorp", "Bloomberg", "Refinitiv", "Custodian", "IBOR", "ABOR", "Murex"]
    owners = ["Reference Data Ops", "Trade Support", "Pricing Control", "Reconciliation", "Client Data Ops", "Source Systems"]
    labels = rng.choice(EXCEPTION_TYPES, n_exceptions, p=[0.12, 0.10, 0.09, 0.14, 0.13, 0.08, 0.07, 0.08, 0.08, 0.05, 0.06])
    historical = pd.DataFrame({"exception_id": [f"EXC{i:07d}" for i in range(n_exceptions)], "exception_type": labels})
    historical["domain"] = historical["exception_type"].map(
        {
            "Missing Reference Data": "Reference Data",
            "Stale Price": "Pricing",
            "Price Outlier": "Pricing",
            "Trade Match Break": "Trades",
            "Position Reconciliation Break": "Positions",
            "Duplicate Record": "Trades",
            "Invalid Currency": "Reference Data",
            "Missing Client Mapping": "Client Data",
            "Delayed Source Load": "Source Control",
            "Performance Return Outlier": "Positions",
            "Unknown / Needs SME Review": "Reference Data",
        }
    )
    historical["source_system"] = rng.choice(source_systems, n_exceptions)
    historical["region"] = rng.choice(regions, n_exceptions)
    historical["asset_class"] = rng.choice(asset_classes, n_exceptions)
    historical["missing_field_count"] = np.where(historical.exception_type.str.contains("Missing"), rng.integers(1, 5, n_exceptions), rng.integers(0, 2, n_exceptions))
    historical["age_days"] = rng.integers(0, 22, n_exceptions)
    historical["break_amount"] = np.where(historical.domain.isin(["Positions", "Trades"]), rng.lognormal(10.5, 1.0, n_exceptions), rng.lognormal(7.5, 0.8, n_exceptions)).round(2)
    historical["price_movement_pct"] = np.where(historical.exception_type.isin(["Price Outlier", "Performance Return Outlier"]), rng.normal(16, 8, n_exceptions), rng.normal(1.5, 2.5, n_exceptions)).round(2)
    historical["duplicate_flag"] = (historical.exception_type == "Duplicate Record").astype(int)
    historical["currency_mismatch_flag"] = (historical.exception_type == "Invalid Currency").astype(int)
    historical["refresh_delay_hours"] = np.where(historical.exception_type.isin(["Stale Price", "Delayed Source Load"]), rng.integers(20, 96, n_exceptions), rng.integers(0, 20, n_exceptions))
    historical["severity"] = pd.cut(historical["break_amount"].rank(pct=True) + historical["age_days"] / 35, [0, 0.55, 0.9, 1.25, 2], labels=["Low", "Medium", "High", "Critical"]).astype(str)
    historical["root_cause"] = historical["exception_type"].map(lambda x: f"{x} pattern detected from source controls")
    historical["owner"] = historical["domain"].map(
        {
            "Reference Data": "Reference Data Ops",
            "Trades": "Trade Support",
            "Positions": "Reconciliation",
            "Pricing": "Pricing Control",
            "Client Data": "Client Data Ops",
            "Source Control": "Source Systems",
        }
    )
    historical["sla_hours"] = historical["severity"].map({"Low": 72, "Medium": 48, "High": 24, "Critical": 8})
    historical["resolution_label"] = rng.choice(["Resolved", "Open", "Escalated", "Suppressed"], n_exceptions, p=[0.62, 0.20, 0.14, 0.04])
    historical["created_at"] = [datetime.today().date() - timedelta(days=int(x)) for x in rng.integers(0, 60, n_exceptions)]

    frames = {
        "securities": securities,
        "trades": trades,
        "positions": positions,
        "prices": prices,
        "historical_exceptions": historical,
    }
    for name, frame in frames.items():
        frame.to_csv(RAW_DIR / f"{name}.csv", index=False)

    with sqlite3.connect(DATA_DIR / "exception_triage.db") as conn:
        for name, frame in frames.items():
            frame.to_sql(name, conn, if_exists="replace", index=False)
    return frames


if __name__ == "__main__":
    frames = generate()
    print(f"Generated {sum(len(v) for v in frames.values()):,} source records in {RAW_DIR}")
