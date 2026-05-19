import fs from "node:fs/promises";
import path from "node:path";

function parseCsvLine(line) {
  const cells = [];
  let current = "";
  let inQuotes = false;
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i];
    if (ch === '"') {
      const next = line[i + 1];
      if (inQuotes && next === '"') {
        current += '"';
        i += 1;
      } else {
        inQuotes = !inQuotes;
      }
      continue;
    }
    if (ch === "," && !inQuotes) {
      cells.push(current);
      current = "";
      continue;
    }
    current += ch;
  }
  cells.push(current);
  return cells;
}

async function readCsv(filePath) {
  const raw = await fs.readFile(filePath, "utf8");
  const lines = raw.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = parseCsvLine(lines[0]);
  return lines.slice(1).map((line) => {
    const values = parseCsvLine(line);
    const row = {};
    headers.forEach((h, idx) => {
      row[h] = values[idx] ?? "";
    });
    return row;
  });
}

const base = path.resolve(process.cwd(), "..", "data", "processed");
const [triage, anomalies, matches, metrics] = await Promise.all([
  readCsv(path.join(base, "triaged_exceptions.csv")),
  readCsv(path.join(base, "anomaly_scores.csv")),
  readCsv(path.join(base, "smart_match_results.csv")),
  readCsv(path.join(base, "model_metrics.csv")),
]);

const total = triage.length;
const autoTriaged = total
  ? 1 - triage.filter((r) => String(r.sme_review_flag).toLowerCase() === "true").length / total
  : 0;
const highPriority = triage.filter((r) => Number(r.priority_score) >= 70).length;
const slaBreaches = triage.filter((r) => r.sla_status === "Breached").length;
const avgConfidence = total
  ? triage.reduce((acc, r) => acc + Number(r.confidence_score || 0), 0) / total
  : 0;

const payload = {
  kpis: { total, autoTriaged, highPriority, slaBreaches, avgConfidence },
  triage,
  anomalies,
  matches,
  metrics,
};

const outputDir = path.resolve(process.cwd(), "public");
await fs.mkdir(outputDir, { recursive: true });
await fs.writeFile(
  path.join(outputDir, "dashboard-data.json"),
  JSON.stringify(payload),
  "utf8",
);

console.log("Generated web/public/dashboard-data.json");
