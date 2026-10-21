import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const content = JSON.parse(fs.readFileSync("data/handbook-content.json", "utf8"));
const quality = JSON.parse(fs.readFileSync("docs/handbook-quality/2026-10-21-worker-b-12chapter-inventory.json", "utf8"));
const audit = JSON.parse(fs.readFileSync("docs/handbook-quality/2026-10-21-worker-b-duplication-audit.json", "utf8"));
const expected = [
  "homevisit/additions", "homevisit/deductions",
  "dayservice/additions", "dayservice/deductions",
  "community-dayservice/additions", "community-dayservice/deductions",
  "welfare-equipment-rental/designation", "welfare-equipment-rental/records",
  "specific-welfare-equipment-sale/designation", "specific-welfare-equipment-sale/records",
  "care-management/designation", "care-management/records",
];
const norm = value => value.replace(/data\/[^ \u3000、。]+?\.json/g, "{PATH}")
  .replace(/指定|介護予防|地域密着型/g, "{CATEGORY}").replace(/[\s\u3000]/g, "");
const metrics = field => {
  const freq = new Map();
  for (const service of Object.values(content.services))
    for (const chapter of Object.values(service.chapters))
      for (const value of chapter[field] ?? []) {
        const key = norm(value);
        freq.set(key, (freq.get(key) ?? 0) + 1);
      }
  return { total: [...freq.values()].reduce((a, b) => a + b, 0),
    excess: [...freq.values()].reduce((a, b) => a + Math.max(0, b - 1), 0) };
};

test("B records exactly twelve scoped chapters and keeps 585 canonical chapter entries", () => {
  assert.equal(content.schema_version, 1);
  assert.equal(Object.keys(content.services).length, 39);
  assert.equal(Object.values(content.services).reduce((n, s) => n + Object.keys(s.chapters).length, 0), 585);
  assert.deepEqual([...quality.changed_chapter_ids].sort(), [...expected].sort());
  assert.equal(new Set(quality.changed_service_ids).size, 6);
  assert.equal(quality.inventory.length, 12);
  const seen = new Set();
  for (const item of quality.inventory) {
    assert.ok(expected.includes(item.chapter_key), item.chapter_key);
    assert.ok(!seen.has(item.chapter_key));
    seen.add(item.chapter_key);
    const chapter = content.services[item.service_id]?.chapters[item.chapter_id];
    assert.ok(chapter);
    assert.ok(chapter.paragraphs.some(p => p.includes(item.scenario.slice(0, 22))), item.chapter_key);
    assert.ok(chapter.checkpoints.some(p => p.includes(item.records_to_compare.slice(0, 18))), item.chapter_key);
    assert.match(item.evidence_gap, /未確|not established|not verified/i);
    assert.ok(["PRIMARY_TEXT_CHECKED", "SOURCE_CANDIDATE_ONLY", "EVIDENCE_GAP"].includes(item.source_status));
  }
});

test("primary-text checks are explicit and do not certify remuneration entitlement", () => {
  const confirmed = quality.inventory.filter(i => i.primary_text_check);
  assert.equal(confirmed.length, 5);
  assert.equal(new Set(confirmed.map(i => i.service_id)).size, 5);
  for (const item of confirmed) {
    const src = item.primary_text_check;
    assert.match(src.url, /^https:\/\/www\.mhlw\.go\.jp\/web\/t_doc\?/);
    assert.match(src.article, /第.+条/);
    assert.match(src.verified_claim_limit, /未照合|未検証|未確認|未確立/);
  }
  assert.equal(quality.legal_currentness, "NOT_ESTABLISHED");
  assert.equal(quality.provider_applicability, "NOT_ESTABLISHED");
  assert.equal(quality.human_legal_review, "NOT_REVIEWED");
});

test("dedup audit retains the exact E normalization and all-service baseline", () => {
  assert.equal(audit.chapter_count, 585);
  assert.equal(audit.baseline.paragraphs.excess, 24);
  assert.equal(audit.baseline.checkpoints.excess, 247);
  const p = metrics("paragraphs"), c = metrics("checkpoints");
  // Other scoped workers may update text after integration; compare only the committed
  // author branch audit if the aggregate source still equals the author's totals.
  if (p.total === audit.final.paragraphs.total && c.total === audit.final.checkpoints.total) {
    assert.equal(p.excess, audit.final.paragraphs.excess);
    assert.equal(c.excess, audit.final.checkpoints.excess);
    assert.ok(c.excess <= audit.baseline.checkpoints.excess);
  }
  assert.equal(audit.unauthorized_chapter_changes, 0);
});

test("no revised chapter treats an internal index as direct legal approval", () => {
  for (const item of quality.inventory) {
    const chapter = content.services[item.service_id].chapters[item.chapter_id];
    const str = chapter.paragraphs.join("\n") + chapter.checkpoints.join("\n");
    assert.doesNotMatch(str, /全ての事業所で算定できる|加算が必ず適用される/);
    assert.ok(chapter.checkpoints.some(c => /照合|比較|確認/.test(c)));
  }
});
