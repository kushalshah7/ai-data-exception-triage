from __future__ import annotations


def explain_exception(row: dict) -> str:
    return (
        f"{row.get('predicted_exception_type', row.get('exception_type'))} in {row.get('domain')} from "
        f"{row.get('source_system')} is ranked {row.get('severity')} because the item is "
        f"{row.get('age_days')} days old, has a break amount of {row.get('break_amount')}, "
        f"and carries confidence {row.get('confidence_score')}."
    )


def recommended_action(row: dict) -> str:
    issue = row.get("predicted_exception_type", row.get("exception_type", "Unknown"))
    if issue == "Missing Reference Data":
        return "Validate security master fields, enrich ISIN/ticker, and rerun downstream load."
    if issue in {"Stale Price", "Price Outlier", "Performance Return Outlier"}:
        return "Check vendor price history, compare secondary source, and escalate material moves."
    if issue == "Trade Match Break":
        return "Review counterparty economic fields and run fuzzy security/client match."
    if issue == "Position Reconciliation Break":
        return "Compare IBOR, ABOR, and custodian balances; prioritize material value gaps."
    if issue == "Duplicate Record":
        return "Confirm duplicate key collision and suppress or merge after control approval."
    if issue == "Invalid Currency":
        return "Validate security currency, trade currency, and portfolio base currency mapping."
    if issue == "Missing Client Mapping":
        return "Route to client-data operations to complete portfolio and account mapping."
    if issue == "Delayed Source Load":
        return "Check source-system batch status and notify technology owner if SLA breached."
    return "Send to SME review with source evidence and model explanation."
