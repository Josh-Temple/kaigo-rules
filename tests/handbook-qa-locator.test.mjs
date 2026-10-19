import { readFileSync } from "node:fs";
import test from "node:test";
import assert from "node:assert/strict";
import { sourceCandidateMatchesQuery } from "../lib/handbook/preview-source-search.ts";

const read = path => readFileSync(new URL("../" + path, import.meta.url), "utf8");
const source = JSON.parse(read("docs/prototypes/data/dayservice-handbook-source-candidates.v2.json"));
const candidates = source.sections.flatMap(section => section.candidates ?? []);
const oldQa = candidates.find(c => c.candidate_id === "handbook.a.national_qa.2015-question50");
const projected = c => ({
  candidateId: c.candidate_id,
  sourceName: c.title ?? null,
  sourceVersion: c.source_version ?? null,
  sourceLocator: c.source_locator ?? null,
});

test("actual 2015 question 50 source locator exists and remains historical", () => {
  assert.ok(oldQa);
  assert.equal(oldQa.source_locator, "source_number=問50;issued_at=2015-04-01");
  assert.equal(oldQa.source_version, "2015-04-01");
  assert.equal(oldQa.candidate_status, "HISTORICAL");
  assert.equal(sourceCandidateMatchesQuery(projected(oldQa), "問50"), true);
  assert.equal(sourceCandidateMatchesQuery(projected(oldQa), "issued_at=2015-04-01"), true);
});

test("source ID, display title and source version are searchable", () => {
  const candidate = projected(oldQa);
  assert.equal(sourceCandidateMatchesQuery(candidate, "2015-question50"), true);
  assert.equal(sourceCandidateMatchesQuery(candidate, "平成27年度"), true);
  assert.equal(sourceCandidateMatchesQuery(candidate, "2015-04-01"), true);
  assert.equal(sourceCandidateMatchesQuery(candidate, "  問50  "), true);
});

test("missing source locator stays absent, rather than inheriting question 50", () => {
  const missing = { candidateId: "separate", sourceName: null, sourceVersion: null, sourceLocator: null };
  assert.equal(sourceCandidateMatchesQuery(missing, "問50"), false);
  assert.equal(sourceCandidateMatchesQuery(missing, "2015"), false);
  assert.equal(sourceCandidateMatchesQuery(missing, ""), true);
});

test("similarly titled QA from different years retain their own locators", () => {
  const a = { candidateId: "a", sourceName: "同名Q&A", sourceVersion: "2015-04-01", sourceLocator: "source_number=問50" };
  const b = { candidateId: "b", sourceName: "同名Q&A", sourceVersion: "2024-03-15", sourceLocator: "source_number=問59" };
  assert.equal(sourceCandidateMatchesQuery(a, "問50"), true);
  assert.equal(sourceCandidateMatchesQuery(b, "問50"), false);
  assert.equal(sourceCandidateMatchesQuery(a, "2024"), false);
  assert.equal(sourceCandidateMatchesQuery(b, "2024"), true);
});

test("malicious input is a literal substring, never an executable pattern", () => {
  const candidate = projected(oldQa);
  for (const q of ["<img src=x onerror=alert(1)>", ".*", "javascript:alert(1)", "(?=a)"]) {
    assert.equal(sourceCandidateMatchesQuery(candidate, q), false);
  }
});

test("service selection and historical publication boundary remain intact", () => {
  const server = read("app/handbook-preview/page.tsx");
  const client = read("app/handbook-preview/PreviewWorkspace.tsx");
  assert.match(server, /sourceLocator: source\.source_locator/);
  assert.match(server, /process\.env\.VERCEL_ENV !== "preview"/);
  assert.match(server, /projection\.publication !== "BLOCKED"/);
  assert.match(server, /projection\.currentness !== "NOT_ESTABLISHED"/);
  assert.match(client, /service\?\.chapters \?\? \[\]/);
  assert.match(client, /setServiceId\(option\.serviceId\); setSectionId\("all"\); setQuery\(""\)/);
  assert.match(client, /chapter\.sourceCandidates\.some\(\(candidate\) => sourceCandidateMatchesQuery\(candidate, normalized\)\)/);
  assert.match(client, /candidate\.sourceLocator &&/);
  assert.match(client, /原典内の位置（記録値・未照合）/);
  assert.doesNotMatch(client, /dangerouslySetInnerHTML|eval\(|XMLHttpRequest\(|sendBeacon\(/);
});

test("unreviewed QA is not promoted or exposed on public handbook page", () => {
  const publicPage = read("app/handbook-sources/page.tsx");
  const server = read("app/handbook-preview/page.tsx");
  assert.doesNotMatch(publicPage, /PreviewWorkspace|sourceLocator/);
  assert.match(server, /projection\.human_review !== "NOT_REVIEWED"/);
  assert.match(server, /source\.source_record_status === "HISTORICAL"/);
});
