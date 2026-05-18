# Data Dictionary

## Raw Data

| File | Grain | Description | Refresh |
| --- | --- | --- | --- |
| `securities.csv` | Security | Security master with identifiers, issuer, asset class, exchange, region, and currency. | Daily |
| `trades.csv` | Trade | Trade economics, status, client, portfolio, source system, and security key. | Intraday |
| `positions.csv` | Position | Client and portfolio holdings by security and source system. | Daily |
| `prices.csv` | Security-date | Daily vendor close prices and currency. | Daily |
| `historical_exceptions.csv` | Exception | Labeled operational exceptions with features, owner, SLA, severity, and resolution. | Daily |

## Processed Data

| File | Description |
| --- | --- |
| `exception_features.csv` | Model-ready features and derived SLA/recurrence fields. |
| `triaged_exceptions.csv` | Final dashboard queue with predictions, confidence, owners, priority, actions, and explanations. |
| `anomaly_scores.csv` | Isolation Forest anomaly score, flag, reason code, and severity recommendation. |
| `smart_match_results.csv` | Fuzzy security matching candidates and review flags. |
| `model_metrics.csv` | Class-level precision, recall, and F1. |
