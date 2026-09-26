import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { getSearchableNotices, matchesNoticeTerms } from "../lib/notice-search.ts";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const load = (relativePath) =>
  JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));

const notices = load("data/notice-nodes.json");
const questions = load("data/questions.json");
const sources = load("data/sources.json");

test("C3 exposes only notice nodes already reachable from verified FAQ publication paths", () => {
  const searchable = getSearchableNotices({ notices, questions, sources });

  assert.deepEqual(
    searchable.map((notice) => notice.id),
    [
      "notice.dayservice.nurse.external-linkage",
      "notice.dayservice.staffing.schedule",
      "notice.common.important-matters.explanation",
      "notice.dayservice.bcp.frequency",
      "notice.dayservice.infection.frequency",
      "notice.dayservice.abuse.frequency",
    ],
  );
});

test("C3 excludes UNKNOWN structural notice nodes", () => {
  const searchable = getSearchableNotices({ notices, questions, sources });
  const ids = new Set(searchable.map((notice) => notice.id));

  for (const id of [
    "notice.dayservice.root",
    "notice.dayservice.personnel",
    "notice.dayservice.operation",
  ]) {
    assert.ok(!ids.has(id), id);
  }
});

test("C3 fails closed when source provenance cannot be resolved", () => {
  const searchable = getSearchableNotices({
    notices,
    questions,
    sources: sources.filter((source) => source.id !== "mhlw-interpretation-html"),
  });
  const ids = new Set(searchable.map((notice) => notice.id));

  assert.ok(!ids.has("notice.dayservice.staffing.schedule"));
  assert.ok(!ids.has("notice.common.important-matters.explanation"));
});

test("C3 does not publish a notice solely from an unverified FAQ linkage", () => {
  const synthetic = {
    id: "notice.synthetic",
    verification_status: "VERIFIED_SOURCE_TEXT",
    editorial_summary: "synthetic searchable text",
    source_ids: ["mhlw-interpretation-html"],
  };
  const searchable = getSearchableNotices({
    notices: [...notices, synthetic],
    questions: [
      ...questions,
      {
        slug: "synthetic",
        status: "draft",
        notice_node_ids: ["notice.synthetic"],
      },
    ],
    sources,
  });

  assert.ok(!searchable.some((notice) => notice.id === "notice.synthetic"));
});

test("C3 lexical notice matching uses the cross-search expanded terms independently of FAQ relations", () => {
  const searchable = getSearchableNotices({ notices, questions, sources });
  const nurse = searchable.find(
    (notice) => notice.id === "notice.dayservice.nurse.external-linkage",
  );

  assert.ok(nurse);
  assert.equal(
    matchesNoticeTerms(nurse, [
      ["看護師", "看護職員", "准看護師"],
      ["外部"],
    ]),
    true,
  );
  assert.equal(matchesNoticeTerms(nurse, [["送迎"]]), false);
});
