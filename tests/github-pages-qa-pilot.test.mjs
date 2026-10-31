import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { DAY_SERVICE_QA_CODES, QA_PAGE_SIZE, searchQaEntries } from "../experiments/github-pages-qa/search-core.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const corpus = JSON.parse(fs.readFileSync(path.join(root, "data/qa-corpus.json"), "utf8"));
const meta = JSON.parse(fs.readFileSync(path.join(root, "data/qa-corpus-meta.json"), "utf8"));
const output = path.join(root, ".github-pages-qa-pilot");
const projected = JSON.parse(fs.readFileSync(path.join(output, "qa-dayservice.json"), "utf8"));

// Independent reference: original app/qa/page.tsx behavior, rather than importing
// the pilot matcher on both sides of a parity test.
const synonyms = [
  ["看護師", "看護職員", "准看護師"], ["生活相談員", "相談員"],
  ["ハンコ", "判子", "押印", "捺印", "印鑑"], ["サイン", "署名", "自署"],
  ["bcp", "業務継続計画"], ["デイサービス", "通所介護"],
  ["計画書", "通所介護計画", "計画"], ["機能訓練室", "機能訓練"],
  ["常勤換算", "常勤換算方法"],
];
function normalized(text) {
  return String(text || "").normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();
}
function reference(rows, { q = "", service = "", standard = "", page = 1 } = {}) {
  const terms = normalized(q.trim()).split(" ").filter(Boolean);
  const groups = terms.map((term) => {
    const group = synonyms.find((items) => items.some((item) => normalized(item) === term));
    return group ? group.map(normalized) : [term];
  });
  const filtered = rows.filter((row) => {
    if (service && row.service_code !== service) return false;
    if (standard && row.standard_label !== standard) return false;
    if (terms.length === 0) return true;
    const text = normalized([
      row.scope, row.service_label, row.current_service_scope, row.standard_label,
      row.topic, row.question, row.answer, row.issued_source, row.number,
    ].join(" "));
    return groups.every((group) => group.some((word) => text.includes(word)));
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / QA_PAGE_SIZE));
  const actualPage = Math.min(Math.max(1, Number.parseInt(String(page), 10) || 1), totalPages);
  return {
    total: filtered.length, page: actualPage, totalPages,
    ids: filtered.slice((actualPage - 1) * QA_PAGE_SIZE, actualPage * QA_PAGE_SIZE).map((row) => row.id),
  };
}
test("only already publicly listed /qa records and UI-visible fields are projected", () => {
  const ids = new Set(corpus.filter((row) => DAY_SERVICE_QA_CODES.includes(row.service_code)).map((row) => row.id));
  assert.ok(ids.size > 0);
  assert.equal(projected.length, ids.size);
  assert.equal(meta.review_status, "INGESTED_UNREVIEWED");
  const allowed = new Set([
    "id", "service_code", "scope", "service_label", "current_service_scope",
    "standard_label", "topic", "question", "answer", "issued_source", "number",
  ]);
  for (const row of projected) {
    assert.ok(ids.has(row.id), "Not listed on public /qa: " + row.id);
    assert.ok(DAY_SERVICE_QA_CODES.includes(row.service_code));
    assert.ok(Object.keys(row).every((key) => allowed.has(key)));
    assert.equal(typeof row.answer, "string");
  }
  assert.equal(fs.existsSync(path.join(output, "handbook-preview.html")), false);
  assert.equal(fs.existsSync(path.join(output, "out")), false);
});
test("browser search parity for synonyms, AND search, filters, pagination and no matches", () => {
  const sourceSubset = corpus.filter((row) => DAY_SERVICE_QA_CODES.includes(row.service_code));
  const queries = [
    "", "看護師", "看護職員", "デイサービス", "BCP",
    "生活相談員", "サイン", "署名", "個別機能訓練",
    "  送迎  ", "通所介護 介護職員", "駐車場の料金", "xyzabc123",
    "常勤換算", "計画書", "看護職員 施設", "年1回",
  ];
  const cases = [];
  for (const q of queries) {
    for (const page of [1, 2, 5, 999]) cases.push({ q, page });
  }
  for (const service of ["01", "02", "06", "16"]) {
    for (const q of ["", "看護師", "送迎", "計画書", "BCP"]) {
      for (const page of [1, 2]) cases.push({ q, service, page });
    }
  }
  const standards = [...new Set(sourceSubset.map((row) => row.standard_label).filter(Boolean))].sort();
  for (const standard of standards.slice(0, 10)) {
    cases.push({ q: "看護師", standard, page: 1 });
    cases.push({ q: "", standard, service: "16", page: 2 });
  }
  for (const params of cases) {
    const expected = reference(sourceSubset, params);
    const actual = searchQaEntries(projected, params);
    assert.deepEqual({
      total: actual.total, page: actual.page, totalPages: actual.totalPages,
      ids: actual.visible.map((row) => row.id),
    }, expected, "Mismatch for " + JSON.stringify(params));
  }
  console.log("Parity scenarios: " + cases.length + " (records=" + projected.length + ")");
});
test("prototype is static, mobile-friendly and has safety notice", () => {
  const html = fs.readFileSync(path.join(output, "index.html"), "utf8");
  const app = fs.readFileSync(path.join(output, "app.mjs"), "utf8");
  assert.match(html, /viewport/);
  assert.match(html, /noindex,nofollow/);
  assert.match(html, /現在も有効とは限りません/);
  assert.match(html, /<form/);
  assert.match(app, /textContent/);
  assert.match(app, /searchQaEntries/);
  assert.doesNotMatch(app, /innerHTML/);
});
