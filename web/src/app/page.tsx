"use client";

import { useEffect, useMemo, useState } from "react";

type Kpis = {
  total: number;
  autoTriaged: number;
  highPriority: number;
  slaBreaches: number;
  avgConfidence: number;
};

type DashboardData = {
  kpis: Kpis;
  triage: Array<Record<string, string>>;
  anomalies: Array<Record<string, string>>;
  matches: Array<Record<string, string>>;
  metrics: Array<Record<string, string>>;
};

const tabs = [
  "Overview",
  "Exception Queue",
  "Anomaly Detection",
  "Smart Matching",
  "Model Performance",
] as const;

function StatCard(props: { label: string; value: string }) {
  return (
    <div className="card">
      <p className="label">{props.label}</p>
      <p className="value">{props.value}</p>
    </div>
  );
}

function severityClass(value: string) {
  const v = value.toLowerCase();
  if (v.includes("critical")) return "pill critical";
  if (v.includes("high")) return "pill high";
  if (v.includes("medium")) return "pill medium";
  return "pill low";
}

export default function Home() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [tab, setTab] = useState<(typeof tabs)[number]>("Overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("./dashboard-data.json")
      .then((r) => r.json())
      .then((d: DashboardData) => setData(d))
      .finally(() => setLoading(false));
  }, []);

  const topQueue = useMemo(() => {
    if (!data) return [];
    return [...data.triage]
      .sort((a, b) => Number(b.priority_score) - Number(a.priority_score))
      .slice(0, 20);
  }, [data]);

  if (loading) return <main className="shell">Loading dashboard...</main>;
  if (!data) return <main className="shell">Unable to load dashboard data.</main>;

  return (
    <main className="shell">
      <header className="header">
        <div className="hero">
          <p className="eyebrow">OPERATIONS INTELLIGENCE</p>
          <h1>AI Data Exception Triage</h1>
          <p>Unified triage, anomaly detection, smart matching, and model signals for analyst workflows.</p>
        </div>
      </header>

      <nav className="tabs">
        {tabs.map((t) => (
          <button key={t} className={tab === t ? "tab active" : "tab"} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </nav>

      {tab === "Overview" && (
        <>
          <section className="grid five">
            <StatCard label="Exceptions" value={data.kpis.total.toLocaleString()} />
            <StatCard label="Auto-Triaged" value={`${Math.round(data.kpis.autoTriaged * 100)}%`} />
            <StatCard label="High Priority" value={data.kpis.highPriority.toLocaleString()} />
            <StatCard label="SLA Breaches" value={data.kpis.slaBreaches.toLocaleString()} />
            <StatCard label="Avg Confidence" value={`${Math.round(data.kpis.avgConfidence * 100)}%`} />
          </section>
          <section className="panel">
            <h2>Exception Mix</h2>
            <div className="list">
              {Object.entries(
                data.triage.reduce<Record<string, number>>((acc, row) => {
                  const key = row.predicted_exception_type || "Unknown";
                  acc[key] = (acc[key] ?? 0) + 1;
                  return acc;
                }, {}),
              )
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10)
                .map(([name, count]) => (
                  <div key={name} className="row">
                    <span>{name}</span>
                    <strong>{count.toLocaleString()}</strong>
                  </div>
                ))}
            </div>
          </section>
        </>
      )}

      {tab === "Exception Queue" && (
        <section className="panel">
          <h2>Priority Queue</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Type</th><th>Severity</th><th>Priority</th><th>Owner</th><th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {topQueue.map((r) => (
                <tr key={r.exception_id}>
                  <td>{r.exception_id}</td><td>{r.predicted_exception_type}</td><td>{r.severity}</td><td>{r.priority_score}</td><td>{r.owner_recommendation}</td><td>{Math.round(Number(r.confidence_score) * 100)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === "Anomaly Detection" && (
        <section className="panel">
          <h2>Top Anomalies</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Type</th><th>Score</th><th>Reason</th><th>Recommended Severity</th>
              </tr>
            </thead>
            <tbody>
              {data.anomalies
                .sort((a, b) => Number(b.anomaly_score) - Number(a.anomaly_score))
                .slice(0, 20)
                .map((r) => (
                  <tr key={r.exception_id}>
                    <td>{r.exception_id}</td><td>{r.exception_type}</td><td>{r.anomaly_score}</td><td>{r.reason_code}</td><td><span className={severityClass(r.severity_recommendation)}>{r.severity_recommendation}</span></td>
                  </tr>
                ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === "Smart Matching" && (
        <section className="panel">
          <h2>Smart Matching Candidates</h2>
          <table>
            <thead>
              <tr>
                <th>Query</th><th>Candidate</th><th>Confidence</th><th>Review Needed</th>
              </tr>
            </thead>
            <tbody>
              {data.matches.slice(0, 25).map((r, idx) => (
                <tr key={`${r.query_security_id}-${idx}`}>
                  <td>{r.query_name}</td><td>{r.candidate_name}</td><td>{r.match_confidence}</td><td><span className={r.review_needed === "True" || r.review_needed === "true" ? "pill high" : "pill low"}>{r.review_needed}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {tab === "Model Performance" && (
        <section className="panel">
          <h2>Model Metrics</h2>
          <table>
            <thead>
              <tr>
                <th>Class</th><th>Precision</th><th>Recall</th><th>F1</th><th>Support</th>
              </tr>
            </thead>
            <tbody>
              {data.metrics.slice(0, 20).map((r, idx) => (
                <tr key={`${r.class}-${idx}`}>
                  <td>{r.class}</td><td>{r.precision}</td><td>{r.recall}</td><td>{r["f1-score"]}</td><td>{r.support}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </main>
  );
}
