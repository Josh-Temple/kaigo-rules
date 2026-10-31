#!/usr/bin/env node
// Build an *unpublished* static search pilot, using only fields already rendered
// on the public /qa page. Never archive corpus or publish this output from CI.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DAY_SERVICE_QA_CODES } from "../experiments/github-pages-qa/search-core.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const src = path.join(root, "experiments/github-pages-qa");
const dest = path.join(root, ".github-pages-qa-pilot");
const corpus = JSON.parse(fs.readFileSync(path.join(root, "data/qa-corpus.json"), "utf8"));
const meta = JSON.parse(fs.readFileSync(path.join(root, "data/qa-corpus-meta.json"), "utf8"));

if (!Array.isArray(corpus) || corpus.length !== meta.rows_included) {
  throw new Error("Public QA corpus/meta mismatch; refuse to produce a pilot");
}
if (meta.review_status !== "INGESTED_UNREVIEWED") {
  throw new Error("QA review-status contract changed; reassess before export");
}

const fields = [
  "id", "service_code", "scope", "service_label", "current_service_scope",
  "standard_label", "topic", "question", "answer", "issued_source", "number",
];
const codes = new Set(DAY_SERVICE_QA_CODES);
const selected = corpus.filter((row) => codes.has(row.service_code)).map((row) => {
  const projected = {};
  for (const field of fields) {
    if (typeof row[field] === "string") projected[field] = row[field];
  }
  if (!projected.id || !projected.question || !projected.service_code) {
    throw new Error("Missing required published QA field; refusing export");
  }
  if (Object.keys(projected).some((key) => !fields.includes(key))) {
    throw new Error("Unexpected private field in published projection");
  }
  return projected;
});
if (!selected.length || selected.length >= corpus.length) {
  throw new Error("Expected bounded day-service QA subset");
}
if (new Set(selected.map((row) => row.id)).size !== selected.length) {
  throw new Error("Duplicate QA ids");
}
fs.mkdirSync(dest, { recursive: true });
for (const name of ["index.html", "app.mjs", "search-core.mjs"]) {
  fs.copyFileSync(path.join(src, name), path.join(dest, name));
}
fs.writeFileSync(path.join(dest, "qa-dayservice.json"), JSON.stringify(selected), "utf8");
const files = fs.readdirSync(dest).map((name) => ({
  name, bytes: fs.statSync(path.join(dest, name)).size,
}));
const bytes = files.reduce((total, file) => total + file.bytes, 0);
if (bytes >= 1_000_000_000) throw new Error("Pilot exceeds GitHub Pages 1GB limit");
const summary = {
  pilot: "dayservice QA search only; no handbook static export, no deployment",
  source_rows: corpus.length,
  selected_rows: selected.length,
  codes: DAY_SERVICE_QA_CODES,
  source_review_status: meta.review_status,
  public_projection_fields: fields,
  output_bytes: bytes,
  output_files: files,
  published: false,
  browser_perf_measured: false,
};
const report = [
  "# Isolated GitHub Pages Q&A search prototype (NOT published)",
  "",
  "- Source: already-listed national Q&A entries from existing /qa; no hidden preview/draft sources",
  "- Coverage: shared, home-service, day-service and dayservice codes: " + DAY_SERVICE_QA_CODES.join(", "),
  "- Records: " + selected.length + " / " + corpus.length + " (scoped subset, not full database)",
  "- Original official corpus currentness: " + meta.review_status + " (not a legal-currentness certification)",
  "- Static pilot size: " + bytes + " bytes (" + (bytes / 1_000_000).toFixed(3) + " MB) across " + files.length + " files",
  "- Includes only projected /qa-visible fields; all Q&A still bear currentness warning",
  "- No official handbook/Notices/DB search/API static export yet; no Android benchmark yet",
  "- NO DEPLOY, NO MAIN CHANGE, no artifact containing exported Q&A data",
  "",
];
fs.writeFileSync(path.join(dest, "measurement.md"), report.join("\n"), "utf8");
fs.writeFileSync(path.join(dest, "measurement.json"), JSON.stringify(summary, null, 2) + "\n", "utf8");
console.log(report.join("\n"));
