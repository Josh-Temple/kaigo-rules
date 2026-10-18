import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  serviceHandbooks, legalDocuments, legalRecords, filterLegalRecords,
  serviceHandbook, chapterRecords, legalHref,
} from "../lib/working-handbook.ts";

const readJson = path => JSON.parse(fs.readFileSync(path, "utf8"));

test("every canonical current service has 15 complete chapter entries", () => {
  const expected = readJson("data/services/catalog.generated.json").services.map(s => s.service_id);
  assert.equal(serviceHandbooks.length, 39);
  assert.deepEqual(new Set(serviceHandbooks.map(s => s.service_id)), new Set(expected));
  for (const service of serviceHandbooks) {
    assert.equal(service.chapters.length, 15, service.service_id);
    assert.equal(new Set(service.chapters.map(c => c.section_id)).size, 15);
    assert.deepEqual(service.chapters.map(c => c.number), Array.from({ length: 15 }, (_, i) => i + 1));
    for (const chapter of service.chapters) {
      assert.ok(chapter.summary.length > 20);
      assert.ok(chapter.checkpoints.length >= 2);
      assert.equal(chapterRecords(chapter).length, chapter.reference_ids.length);
      assert.ok(chapterRecords(chapter).every(r => r.service_ids.includes(service.service_id)));
    }
    assert.ok(filterLegalRecords({ service: service.service_id, category: "law" }).length > 0);
    assert.ok(filterLegalRecords({ service: service.service_id, category: "standards" }).length > 0);
  }
});

test("legal corpus keeps each article's committed text byte-for-byte", () => {
  for (const document of legalDocuments.filter(d => ["law", "standards"].includes(d.category))) {
    const rows = legalRecords.filter(r => r.document_id === document.id);
    assert.ok(rows.length > 0);
    const path = rows[0].source_file;
    const original = new Map(readJson(path).filter(n => n.node_type === "article").map(n => [n.id, n.official_text]));
    assert.equal(rows.length, original.size);
    for (const row of rows) assert.equal(row.text, original.get(row.id), row.id);
  }
});

test("article sorting is numeric and inserted articles precede the next main article", () => {
  for (const doc of legalDocuments.filter(d => ["law", "standards"].includes(d.category))) {
    const rows = legalRecords.filter(r => r.document_id === doc.id);
    const sorted = rows.toSorted((a, b) => {
      for (let i = 0; i < Math.max(a.order.length, b.order.length); i++) {
        const delta = (a.order[i] || 0) - (b.order[i] || 0);
        if (delta) return delta;
      }
      return 0;
    });
    assert.deepEqual(rows.map(r => r.id), sorted.map(r => r.id));
  }
  const ids = filterLegalRecords({ document: "care-insurance-act" }).map(r => r.id);
  assert.ok(ids.indexOf("careact.article.8") < ids.indexOf("careact.article.8-2"));
  assert.ok(ids.indexOf("careact.article.5") < ids.indexOf("careact.article.5-2"));
  assert.ok(ids.indexOf("careact.article.5-2") < ids.indexOf("careact.article.6"));
  assert.ok(ids.indexOf("careact.article.8-2") < ids.indexOf("careact.article.18"));
});

test("service references include the right staffing provisions without leaking another service's chapter", () => {
  const homebath = filterLegalRecords({ service: "homebath", category: "standards" });
  assert.ok(homebath.some(r => r.id === "ordinance37.article.45"));
  assert.ok(!homebath.some(r => r.id === "ordinance37.article.111"));
  assert.ok(filterLegalRecords({ service: "dayrehab", category: "standards" }).some(r => r.id === "ordinance37.article.111"));
  const preventive = filterLegalRecords({ service: "preventive-homebath", category: "standards" });
  assert.ok(preventive.some(r => r.id === "standards35.article.47"));
  assert.ok(preventive.every(r => r.document_id === "preventive-services-standards"));
});

test("service, family, document, keyword and single-record filters compose", () => {
  const rows = filterLegalRecords({ service: "homebath", category: "standards", document: "ordinance37", q: "従業者" });
  assert.ok(rows.length > 0);
  assert.ok(rows.every(r => r.service_ids.includes("homebath") && r.document_id === "ordinance37"));
  assert.deepEqual(filterLegalRecords({ service: "not-a-service" }), []);
  assert.deepEqual(filterLegalRecords({ service: "homebath", record: "ordinance37.article.111" }), []);
  assert.equal(filterLegalRecords({ record: "ordinance37.article.111" }).length, 1);
  assert.ok(filterLegalRecords({ document: "ordinance37", q: "第45条" }).some(r => r.id === "ordinance37.article.45"));
  assert.deepEqual(filterLegalRecords({ q: "ＮＯ＿ＳＵＣＨ＿ＷＯＲＤ" }), []);
});

test("links preserve composed filters and encode literal query characters", () => {
  const url = new URL(legalHref({ service: "homebath", category: "standards", q: "感染症 & 記録", page: 2 }), "https://kaigo-rules.vercel.app");
  assert.equal(url.searchParams.get("q"), "感染症 & 記録");
  assert.equal(url.searchParams.get("page"), "2");
  assert.equal(url.searchParams.get("service"), "homebath");
});

test("old draft paragraphs survive and status remains a working draft", () => {
  const original = readJson("docs/prototypes/evidence-bridges/dayrehab.json");
  const actual = serviceHandbook("dayrehab");
  for (const chapter of original.chapters) {
    const row = actual.chapters.find(c => c.section_id === chapter.section_id);
    assert.deepEqual(row.paragraphs, chapter.candidate_paragraphs.map(p => p.text));
    assert.equal(row.editorial_state, "作成中・未確認");
  }
  assert.equal(original.human_review, "NOT_REVIEWED");
  assert.equal(original.publication, "BLOCKED");
});

test("all legal reference URLs are official HTTPS sources and record IDs stay unique", () => {
  assert.equal(new Set(legalRecords.map(r => r.id)).size, legalRecords.length);
  for (const row of [...legalRecords, ...legalDocuments]) {
    if (!row.url) continue;
    const url = new URL(row.url);
    assert.equal(url.protocol, "https:");
    assert.ok(["laws.e-gov.go.jp", "www.mhlw.go.jp"].includes(url.hostname));
  }
});
