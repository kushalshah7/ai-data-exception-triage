from __future__ import annotations

import plotly.express as px
import streamlit as st

from src.dashboard_data import load_anomalies, load_matches, load_metrics, load_prices, load_triage

st.set_page_config(page_title="AI Exception Triage", page_icon="⚙️", layout="wide")

st.markdown(
    """
    <style>
    .stApp {background:#f6f8fb;color:#172033;}
    [data-testid="stSidebar"] {background:#111827;color:white;}
    .block-container {padding-top:1.25rem; padding-bottom:2rem;}
    .metric-card {background:white;border:1px solid #e5e7eb;border-radius:8px;padding:16px 18px;box-shadow:0 1px 2px rgba(15,23,42,.04);}
    .metric-label {font-size:12px;color:#5b667a;text-transform:uppercase;letter-spacing:.04em;margin-bottom:6px;}
    .metric-value {font-size:26px;font-weight:750;color:#111827;line-height:1.1;}
    .metric-note {font-size:12px;color:#64748b;margin-top:5px;}
    .status-high {color:#b91c1c;font-weight:700;}
    div[data-testid="stDataFrame"] {background:white;border-radius:8px;}
    h1, h2, h3 {letter-spacing:0;}
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>""",
        unsafe_allow_html=True,
    )


triage = load_triage()
anomalies = load_anomalies()
matches = load_matches()
metrics, summary = load_metrics()
prices = load_prices()

page = st.sidebar.radio(
    "Workspace",
    ["Triage Overview", "Exception Queue", "Anomaly Detection", "Smart Matching", "Model Performance", "Governance and Explainability"],
)
st.sidebar.caption("Local demo data, deterministic controls, and ML accelerators for investment-data exception operations.")

if page == "Triage Overview":
    st.title("AI-Powered Data Exception Triage")
    st.caption("Operations command center for classifying breaks, prioritizing queues, and routing analyst action.")
    total = len(triage)
    auto = 1 - triage["sme_review_flag"].mean()
    high_priority = (triage["priority_score"] >= 70).sum()
    sla = (triage["sla_status"] == "Breached").sum()
    avg_conf = triage["confidence_score"].mean()
    saved_hours = int(total * auto * 4 / 60)
    cols = st.columns(6)
    with cols[0]:
        metric_card("Exceptions", f"{total:,}", "Processed this run")
    with cols[1]:
        metric_card("Auto-triaged", f"{auto:.0%}", "Human review avoided")
    with cols[2]:
        metric_card("High priority", f"{high_priority:,}", "Score >= 70")
    with cols[3]:
        metric_card("SLA breaches", f"{sla:,}", "Needs escalation")
    with cols[4]:
        metric_card("Avg confidence", f"{avg_conf:.0%}", "Classifier max probability")
    with cols[5]:
        metric_card("Hours saved", f"{saved_hours:,}", "First-pass triage estimate")

    left, right = st.columns([1.2, 1])
    trend = triage.assign(created_at=lambda d: d["created_at"].astype(str)).groupby(["created_at", "severity"]).size().reset_index(name="exceptions")
    with left:
        st.plotly_chart(px.bar(trend, x="created_at", y="exceptions", color="severity", title="Exception Trend by Severity"), use_container_width=True)
    mix = triage["predicted_exception_type"].value_counts().reset_index()
    mix.columns = ["category", "exceptions"]
    with right:
        st.plotly_chart(px.pie(mix, values="exceptions", names="category", hole=0.52, title="Predicted Exception Mix"), use_container_width=True)
    workload = triage.groupby("owner_recommendation", as_index=False)["exception_id"].count().rename(columns={"exception_id": "exceptions"})
    st.plotly_chart(px.bar(workload, x="owner_recommendation", y="exceptions", color="owner_recommendation", title="Owner Workload"), use_container_width=True)

elif page == "Exception Queue":
    st.title("Exception Queue")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        severities = st.multiselect("Severity", sorted(triage["severity"].unique()), default=sorted(triage["severity"].unique()))
    with c2:
        owners = st.multiselect("Owner", sorted(triage["owner_recommendation"].unique()), default=sorted(triage["owner_recommendation"].unique()))
    with c3:
        sla_filter = st.multiselect("SLA", sorted(triage["sla_status"].unique()), default=sorted(triage["sla_status"].unique()))
    with c4:
        min_conf = st.slider("Minimum confidence", 0.0, 1.0, 0.0, 0.05)
    search = st.text_input("Search exception ID, type, owner, or action")
    filtered = triage[
        triage["severity"].isin(severities)
        & triage["owner_recommendation"].isin(owners)
        & triage["sla_status"].isin(sla_filter)
        & (triage["confidence_score"] >= min_conf)
    ].copy()
    if search:
        haystack = filtered.astype(str).agg(" ".join, axis=1).str.lower()
        filtered = filtered[haystack.str.contains(search.lower(), regex=False)]
    filtered = filtered.sort_values("priority_score", ascending=False)
    st.dataframe(
        filtered[
            [
                "exception_id",
                "predicted_exception_type",
                "severity",
                "priority_score",
                "sla_status",
                "owner_recommendation",
                "confidence_score",
                "recommended_action",
                "sme_review_flag",
            ]
        ],
        use_container_width=True,
        height=430,
    )
    if not filtered.empty:
        selected = st.selectbox("Detail panel", filtered["exception_id"].head(150))
        row = filtered[filtered["exception_id"] == selected].iloc[0]
        st.subheader(selected)
        st.write(row["explainability_summary"])
        st.info(row["recommended_action"])

elif page == "Anomaly Detection":
    st.title("Anomaly Detection")
    left, right = st.columns([1.2, 1])
    with left:
        st.plotly_chart(
            px.scatter(
                anomalies,
                x="price_movement_pct",
                y="anomaly_score",
                color="anomaly_flag",
                size="break_amount",
                hover_data=["exception_id", "reason_code", "severity_recommendation"],
                title="Price Movement vs Anomaly Score",
            ),
            use_container_width=True,
        )
    one_security = prices["security_id"].value_counts().index[0]
    sec_prices = prices[prices["security_id"] == one_security].sort_values("price_date")
    with right:
        st.plotly_chart(px.line(sec_prices, x="price_date", y="close_price", title=f"Price History: {one_security}"), use_container_width=True)
    st.dataframe(anomalies.sort_values("anomaly_score", ascending=False).head(40), use_container_width=True, height=380)

elif page == "Smart Matching":
    st.title("Smart Matching")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(px.histogram(matches, x="match_confidence", nbins=20, title="Match Confidence Distribution"), use_container_width=True)
    with c2:
        risk = matches.assign(risk=lambda d: d["review_needed"].map({True: "Review Needed", False: "Auto Match"}))
        st.plotly_chart(px.pie(risk, names="risk", hole=0.55, title="False-positive Risk Control"), use_container_width=True)
    st.dataframe(matches.sort_values("match_confidence"), use_container_width=True, height=430)

elif page == "Model Performance":
    st.title("Model Performance")
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Accuracy", f"{summary.get('accuracy', 0):.0%}", summary.get("model_version", "rf_triage_v1"))
    with c2:
        metric_card("Macro F1", f"{summary.get('macro_f1', 0):.0%}", "Class-balanced signal")
    with c3:
        metric_card("Training rows", f"{summary.get('training_rows', 0):,}", "Synthetic historical exceptions")
    class_metrics = metrics[~metrics["class"].isin(["accuracy", "macro avg", "weighted avg"])].copy()
    st.plotly_chart(px.bar(class_metrics, x="class", y="f1-score", title="Per-class F1 Score"), use_container_width=True)
    st.dataframe(metrics, use_container_width=True)

else:
    st.title("Governance and Explainability")
    st.subheader("Human-in-the-loop controls")
    st.write(
        "Low-confidence, unknown-category, high-priority, and anomaly-driven results are routed to SME review. "
        "The model supports first-pass prioritization only; analysts remain accountable for final remediation decisions."
    )
    st.subheader("Audit and privacy assumptions")
    st.write(
        "This demo uses synthetic investment operations data only. Outputs are persisted locally in CSV and SQLite so each run can be reviewed, reproduced, and tested."
    )
    st.subheader("Validation controls")
    st.dataframe(
        triage[["exception_id", "predicted_exception_type", "confidence_score", "priority_score", "sme_review_flag", "root_cause_hint"]]
        .sort_values("priority_score", ascending=False)
        .head(30),
        use_container_width=True,
    )
