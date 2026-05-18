# Governance Notes

## Privacy

The repository uses synthetic data. Any production adaptation must classify data sensitivity, mask client identifiers, and enforce least-privilege access.

## Explainability

The dashboard exposes prediction confidence, reason codes, root-cause hints, SME review flags, and recommended actions. It avoids presenting ML output as final truth.

## Validation

Validation controls include unit tests, class-level model metrics, confusion matrix output, deterministic data generation, and a CI workflow.

## Auditability

Pipeline outputs are persisted to local CSV and SQLite files. Each run can be reviewed through generated artifacts in `data/processed/`.

## Human Oversight

Analysts remain responsible for exception closure. Automated triage should route, rank, and summarize; it should not suppress or close exceptions without approved control evidence.
