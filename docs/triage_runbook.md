# Triage Runbook

## Daily Workflow

1. Run `python src/generate_synthetic_data.py` for demo data or replace raw CSVs with approved inputs.
2. Run `python src/train_exception_classifier.py` after data changes.
3. Run `python src/triage_engine.py` to refresh the exception queue.
4. Open `streamlit run app.py`.
5. Start with high-priority SLA breaches in the Exception Queue.

## Analyst Interpretation

- `priority_score`: composite urgency score from severity, SLA, value, recurrence, and confidence.
- `confidence_score`: model certainty for predicted exception type.
- `sme_review_flag`: true when the model should not be trusted without analyst review.
- `recommended_action`: first action for operations teams.
- `root_cause_hint`: explainable cue from historical patterns.

## Escalation Rules

- Critical severity and breached SLA: immediate owner escalation.
- Confidence below 72%: SME review.
- Unknown category: SME review and taxonomy update.
- Anomaly score above 0.78: validate vendor/source evidence before closure.
