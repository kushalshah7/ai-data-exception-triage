# Model Card

## Purpose

The exception classifier predicts investment-data exception categories from operational features so analysts can prioritize and route breaks faster.

## Training Data

Training data is synthetic and generated locally by `src/generate_synthetic_data.py`. It represents securities, trades, positions, prices, and historical exception labels with controlled issue injection.

## Intended Use

- First-pass triage for demo and portfolio projects.
- Explainable routing, prioritization, and SME review queues.
- Analyst productivity storytelling for investment data operations.

## Non-Intended Use

- Production trade, valuation, or client reporting decisions.
- Fully automated closure of operational exceptions.
- Use with confidential data without privacy, retention, and access controls.

## Metrics

Metrics are written to `data/processed/model_metrics.csv` and `data/processed/model_summary.json` after training. The dashboard reports accuracy, macro F1, and per-class F1.

## Limitations

Synthetic data cannot represent all real vendor, custodian, or portfolio accounting edge cases. Low-confidence predictions and unknown categories must route to human review.
