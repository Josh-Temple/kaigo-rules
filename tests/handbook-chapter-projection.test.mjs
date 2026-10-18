import { readFileSync } from "node:fs";
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  composeHandbookProjection,
  safeOfficialSourceUrl,
} from "../lib/handbook/compose.ts";

const read = path => JSON.parse(readFileSync(new URL("../" + path, import.meta.url), "utf8"));
const day = read("docs/prototypes/evidence-bridges/dayservice.json");
const rehab = read("docs/prototypes/evidence-bridges/dayrehab.json");
const drafts = read("docs/prototypes/data/dayservice-handbook-drafts.v1.json");
const old = read("docs/prototypes/data/dayservice-handbook-source-candidates.v2.json");
const registry = read("data/sources.json");
const catalog = read("data/services/catalog.generated.json");
const ids = catalog.services.map(s => s.service_id);
const input = (serviceId = "dayservice") => ({
  serviceId,
  registeredServiceIds: ids,
  bridge: structuredClone(serviceId === "dayservice" ? day : rehab),
  registry: structuredClone(registry),
  // Isolated unit tests pass publication-policy output as a dependency.
  // Tests do not infer published routes from source identifiers.
  publishedServiceRoutes: [{ source_family: "governing_standards_ordinance",
    label: "既存の公開範囲", href: "/rules?service=" + serviceId }],
  ...(serviceId === "dayservice" ? {
    oldDraft: structuredClone(drafts), oldSourceCandidates: structuredClone(old),
  } : {}),
});

test("30 chapters, 29 new bridge candidates, 11 old source candidates, 65 old drafts", () => {
  const a = composeHandbookProjection(input("dayservice"));
  const b = composeHandbookProjection(input("dayrehab"));
  assert.equal(a.chapters.length, 15);
  assert.equal(b.chapters.length, 15);
  assert.equal(a.candidate_count, 11);
  assert.equal(b.candidate_count, 18);
  assert.equal(a.old_source_candidate_count, 11);
  assert.equal(a.historical_draft_statement_count, 65);
  assert.equal(b.old_source_candidate_count, 0);
  assert.equal(b.historical_draft_statement_count, 0);
  assert.deepEqual(a.chapters.map(c => c.section_id), b.chapters.map(c => c.section_id));
});

test("distinct types and IDs, no repeated bridge candidate in 30 chapters", () => {
  const all = ["dayservice", "dayrehab"].flatMap(id =>
    composeHandbookProjection(input(id)).chapters.flatMap(c => c.source_candidates));
  assert.equal(new Set(all.map(c => c.candidate_id)).size, all.length);
  assert.equal(all.filter(c => c.candidate_type === "EVIDENCE_BRIDGE").length, 29);
  assert.equal(all.filter(c => c.candidate_type === "OLD_SOURCE_CANDIDATE").length, 11);
});

test("all candidates are withheld even when the registry describes a verified source", () => {
  const rows = composeHandbookProjection(input()).chapters.flatMap(c => c.source_candidates);
  for (const row of rows) {
    assert.equal(row.publication, "NOT_GRANTED");
    assert.equal(row.currentness, "NOT_ESTABLISHED");
    assert.equal(row.human_review, "NOT_REVIEWED");
    assert.equal(row.applicability, "NOT_ESTABLISHED");
  }
});

test("no preview paragraph text is present in the projection", () => {
  for (const serviceId of ["dayservice", "dayrehab"]) {
    const projection = JSON.stringify(composeHandbookProjection(input(serviceId)));
    for (const chapter of (serviceId === "dayservice" ? day : rehab).chapters) {
      for (const candidate of chapter.candidate_paragraphs) {
        assert.ok(!projection.includes(candidate.text));
      }
    }
  }
});

test("no prototype draft statements are copied to projection", () => {
  const text = JSON.stringify(composeHandbookProjection(input()));
  for (const section of drafts.sections) {
    for (const statement of section.draft_statements) {
      assert.ok(!text.includes(statement.text));
    }
  }
});

test("empty chapter remains empty, rather than being filled by shared source guesses", () => {
  const r = composeHandbookProjection(input("dayrehab"));
  for (const id of ["designation", "business_continuity", "deductions", "notifications", "national_qa"]) {
    assert.equal(r.chapters.find(c => c.section_id === id).source_candidates.length, 0);
  }
  assert.ok(r.chapters.every(c => c.public_search_href === "/databases/search?service=dayrehab"));
});

test("legacy 27 original candidates retained separately in the existing HTML prototype", () => {
  const html = readFileSync(new URL("../docs/prototypes/dayservice-handbook.html", import.meta.url), "utf8");
  const match = html.match(/const CANDIDATES=(\[.*?\]);\n/s);
  assert.ok(match);
  assert.equal(JSON.parse(match[1]).length, 27);
  // Historical 27 are not silently summed as 27 new legally accepted sources.
  assert.equal(composeHandbookProjection(input()).old_source_candidate_count, 11);
});

test("unknown ID is rejected and another known service is not relabeled dayservice", () => {
  const a = input();
  a.serviceId = "not-a-service";
  assert.throws(() => composeHandbookProjection(a), /unknown service ID/);
  const b = input();
  b.serviceId = "dayrehab";
  assert.throws(() => composeHandbookProjection(b), /another service/);
});

test("cross-service evidence is rejected", () => {
  const a = input();
  a.bridge.source_evidence[0].service_id = "dayrehab";
  assert.throws(() => composeHandbookProjection(a), /cross-service/);
});

test("missing source evidence ID is rejected", () => {
  const a = input();
  a.bridge.chapters[0].candidate_paragraphs[0].evidence_task_id = "KR-EVIDENCE-999";
  assert.throws(() => composeHandbookProjection(a), /invalid\/duplicate evidence candidate/);
});

test("mismatched Library provenance is rejected", () => {
  const a = input();
  a.bridge.chapters[0].candidate_paragraphs[0].evidence_library_file_id = "libfile_spoof";
  assert.throws(() => composeHandbookProjection(a), /invalid\/duplicate evidence candidate/);
});

test("duplicate candidate IDs are rejected", () => {
  const a = input();
  const first = a.bridge.chapters[0].candidate_paragraphs[0];
  a.bridge.chapters[1].candidate_paragraphs[0].bridge_id = first.bridge_id;
  assert.throws(() => composeHandbookProjection(a), /invalid\/duplicate evidence candidate/);
});

test("registry URL mismatches and non-existent registry references fail closed", () => {
  const a = input();
  a.oldSourceCandidates.sections[0].candidates[0].source_url = "https://example.org/changes";
  assert.throws(() => composeHandbookProjection(a), /legacy source reference/);
  const b = input();
  b.oldSourceCandidates.sections[0].candidates[0].source_id = "made-up-source";
  assert.throws(() => composeHandbookProjection(b), /legacy source reference/);
});

test("unreviewed flags cannot be made approved via input", () => {
  const a = input();
  a.bridge.human_review = "APPROVED";
  assert.throws(() => composeHandbookProjection(a), /release\/review gate/);
  const b = input();
  b.oldDraft.publication_state = "PUBLICATION_APPROVED";
  assert.throws(() => composeHandbookProjection(b), /old draft trust boundary/);
  const c = input();
  c.oldSourceCandidates.legal_currentness_acceptance = "PASS";
  assert.throws(() => composeHandbookProjection(c), /old candidate trust boundary/);
});

test("malicious official URL host and credentials are not linked", () => {
  for (const x of ["http://www.mhlw.go.jp/a", "https://www.mhlw.go.jp.evil.net/a",
    "https://www.mhlw.go.jp@evil.net/", "https://a@www.mhlw.go.jp/a",
    "https://www.mhlw.go.jp:444/a", "https://www.mhlw.go.jp/a#b",
    "https://github.com/Josh-Temple/kaigo-rules/pull/495", "javascript:alert(1)"]) {
    assert.equal(safeOfficialSourceUrl(x), null);
  }
  assert.ok(safeOfficialSourceUrl("https://laws.e-gov.go.jp/law/409AC0000000123"));
});

test("unofficial GitHub evidence never gets an official source link", () => {
  const s = composeHandbookProjection(input());
  const candidate = s.chapters.flatMap(c => c.source_candidates)
    .find(c => c.evidence_task_id === "KR-EVIDENCE-005");
  assert.ok(candidate);
  assert.equal(candidate.official_url_candidate, null);
});

test("published routes must be provided and cannot be invented from candidates", () => {
  const a = input();
  a.publishedServiceRoutes = [];
  const p = composeHandbookProjection(a);
  assert.equal(p.published_service_routes.length, 0);
  assert.equal(p.candidate_count, 11);
  const b = input();
  b.publishedServiceRoutes[0].href = "//evil.example";
  assert.throws(() => composeHandbookProjection(b), /unsafe published route/);
});

test("missing candidate counts and duplicate chapters are rejected", () => {
  const a = input();
  a.bridge.candidate_paragraph_count = 200;
  assert.throws(() => composeHandbookProjection(a), /candidate count mismatch/);
  const b = input();
  b.bridge.chapters[1].section_id = b.bridge.chapters[0].section_id;
  assert.throws(() => composeHandbookProjection(b), /duplicate\/empty chapter/);
});
