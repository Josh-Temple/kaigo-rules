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
    const previous = chapter.candidate_paragraphs.map(p => p.text);
    assert.deepEqual(row.paragraphs.slice(0, previous.length), previous,
      `original paragraphs changed: ${chapter.section_id}`);
    if (["applicability", "operations"].includes(chapter.section_id)) {
      assert.equal(row.paragraphs.length, previous.length + 2,
        `expected two additional paragraphs: ${chapter.section_id}`);
    } else if (["designation", "staffing", "equipment", "records", "remuneration", "safeguarding", "incident_and_infection", "business_continuity", "deductions", "additions", "notifications", "national_qa", "sources_and_history"].includes(chapter.section_id) && readJson("data/handbook-content.json").services.dayrehab.chapters[chapter.section_id]) {
      const override = readJson("data/handbook-content.json").services.dayrehab.chapters[chapter.section_id];
      assert.deepEqual(row.paragraphs, override.paragraphs,
        `projected prose differs from authored prose: ${chapter.section_id}`);
      assert.equal(row.paragraphs.length, override.paragraphs.length,
        `override projection length differs: ${chapter.section_id}`);
    } else {
      assert.deepEqual(row.paragraphs, previous,
        `unexpected edits to preserved chapter: ${chapter.section_id}`);
    }
    assert.equal(row.editorial_state, "作成中・未確認");
  }
  assert.equal(original.human_review, "NOT_REVIEWED");
  assert.equal(original.publication, "BLOCKED");
});

test("A remaining chapters preserve the fixed #522 baseline and add only manifest IDs", () => {
  const content = readJson("data/handbook-content.json");
  const legacy = readJson("tests/fixtures/handbook-a-legacy.json");
  const quality = readJson("docs/handbook-quality/2026-10-20-worker-a-quality-inventory.json");
  const revisedChapters = new Set(quality.changed_chapter_ids);
  // Current scoped source corrections may extend, never replace, the fixed #522 baseline.
  const scopedB = readJson("docs/handbook-quality/2026-10-21-b-pr536-nonfacility-primary-evidence.json");
  const BAllowed = ["dayservice/records", "welfare-equipment-rental/records", "care-management/records", "community-dayservice/staffing"];
  assert.deepEqual(scopedB.changed_chapters.toSorted(), BAllowed.toSorted(), "unreviewed Worker B chapter scope");
  const bEdits = new Map(scopedB.edits.map(e => [`${e.service}/${e.chapter}`, e]));
  assert.equal(bEdits.size, BAllowed.length, "Worker B evidence must be unique");
  for (const key of BAllowed) {
    const evidence = bEdits.get(key);
    assert.ok(evidence, `missing Worker B evidence: ${key}`);
    assert.equal(evidence.source_status, "PRIMARY_TEXT_CHECKED_SCOPED");
    assert.equal(evidence.currentness_as_of_2026_10_21, "NOT_ESTABLISHED");
    const [service, chapter] = key.split("/");
    const value = content.services[service].chapters[chapter];
    assert.deepEqual(value, evidence.after, `Worker B chapter does not match source ledger: ${key}`);
    assert.deepEqual(value.paragraphs.slice(0, evidence.before.paragraphs.length), evidence.before.paragraphs);
    assert.deepEqual(value.checkpoints.slice(0, evidence.before.checkpoints.length), evidence.before.checkpoints);
    assert.equal(value.paragraphs.length, evidence.before.paragraphs.length + 1);
    assert.equal(value.checkpoints.length, evidence.before.checkpoints.length + 1);
  }
  assert.equal(revisedChapters.size, 51, "only scoped Worker A chapter edits are allowed");
  assert.equal(legacy.source_commit, "0d26dc8e29fd0567e723872290785a2cc979c30b");
  const manifest = {
    homevisit: ["business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    homebath: ["deductions", "additions", "national_qa", "sources_and_history"],
    "preventive-homebath": ["safeguarding", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    homenursing: ["safeguarding", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "preventive-homenursing": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    homerehab: ["safeguarding", "incident_and_infection", "business_continuity", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "preventive-homerehab": ["safeguarding", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    homecaremanagement: ["equipment", "safeguarding", "incident_and_infection", "business_continuity", "deductions", "additions", "notifications", "national_qa"],
    "preventive-homecaremanagement": ["equipment", "incident_and_infection", "business_continuity", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "regular-round": ["equipment", "safeguarding", "business_continuity", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "night-homevisit": ["equipment", "safeguarding", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    dayservice: ["safeguarding", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    dayrehab: ["safeguarding", "incident_and_infection", "business_continuity", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "preventive-dayrehab": ["safeguarding", "incident_and_infection", "business_continuity", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "community-dayservice": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "dementia-dayservice": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "preventive-dementia-dayservice": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
  };
  const addedParagraphs = [];
  const bridge = readJson("docs/prototypes/evidence-bridges/dayrehab.json");
  const proto = Object.fromEntries(bridge.chapters.map(c => [c.section_id, c.candidate_paragraphs.map(p => p.text)]));
  let total = 0;
  for (const [serviceId, allowed] of Object.entries(manifest)) {
    const chapters = content.services[serviceId]?.chapters || {};
    const previous = legacy.services[serviceId];
    for (const [sectionId, authored] of Object.entries(previous)) {
      if (revisedChapters.has(`${serviceId}/${sectionId}`)) {
        const current = chapters[sectionId];
        assert.deepEqual(current.checkpoints.slice(0, authored.checkpoints.length), authored.checkpoints,
          `#522 baseline checkpoints changed: ${serviceId}:${sectionId}`);
        assert.equal(current.checkpoints.length, authored.checkpoints.length + 2,
          `expected two scoped checkpoints: ${serviceId}:${sectionId}`);
        if (sectionId === "national_qa") {
          assert.equal(current.paragraphs.length, authored.paragraphs.length);
          assert.deepEqual(current.paragraphs.slice(1), authored.paragraphs.slice(1),
            `#522 QA source/limitations paragraphs changed: ${serviceId}`);
        } else {
          assert.deepEqual(current.paragraphs.slice(0, authored.paragraphs.length), authored.paragraphs,
            `#522 baseline prose changed: ${serviceId}:${sectionId}`);
          assert.equal(current.paragraphs.length, authored.paragraphs.length + 1);
        }
      } else if (bEdits.has(`${serviceId}/${sectionId}`)) {
        const current = chapters[sectionId];
        assert.deepEqual(current.paragraphs.slice(0, authored.paragraphs.length), authored.paragraphs,
          `#522 baseline prose changed: ${serviceId}:${sectionId}`);
        assert.deepEqual(current.checkpoints.slice(0, authored.checkpoints.length), authored.checkpoints,
          `#522 baseline checkpoints changed: ${serviceId}:${sectionId}`);
        assert.deepEqual(current, bEdits.get(`${serviceId}/${sectionId}`).after,
          `Worker B evidence mismatch: ${serviceId}:${sectionId}`);
      } else {
        assert.deepEqual(chapters[sectionId], authored, `#522 baseline changed: ${serviceId}:${sectionId}`);
      }
    }
    const added = Object.keys(chapters).filter(sectionId => !Object.hasOwn(previous, sectionId));
    assert.ok(added.length >= 3, `${serviceId} needs an intermediate three-chapter minimum`);
    assert.ok(added.length <= allowed.length, `${serviceId} exceeds manifest`);
    assert.ok(added.every(sectionId => allowed.includes(sectionId)), `${serviceId} contains a non-manifest chapter`);
    const projected = serviceHandbook(serviceId);
    for (const sectionId of added) {
      const authored = chapters[sectionId];
      const chapter = projected.chapters.find(c => c.section_id === sectionId);
      assert.ok(authored.paragraphs.length >= 2 && authored.checkpoints.length >= 3, `${serviceId}:${sectionId} is too thin`);
      assert.ok(authored.paragraphs.every(p => p.length >= 80 || (serviceId === "dayrehab" && (proto[sectionId] || []).includes(p))), `${serviceId}:${sectionId} has short prose`);
      assert.ok(authored.paragraphs.some(p => p.includes("参照候補") || p.includes("原典候補")), `${serviceId}:${sectionId} lacks a source candidate`);
      assert.deepEqual(chapter.paragraphs, authored.paragraphs, `${serviceId}:${sectionId} paragraph projection`);
      assert.deepEqual(chapter.checkpoints, authored.checkpoints, `${serviceId}:${sectionId} checkpoint projection`);
      assert.equal(chapter.editorial_state, "作成中・未確認");
      if (serviceId === "dayrehab") {
        assert.deepEqual(authored.paragraphs.slice(0, (proto[sectionId] || []).length), proto[sectionId] || [], `dayrehab prototype prefix changed: ${sectionId}`);
      }
      addedParagraphs.push(...authored.paragraphs);
      total++;
    }
  }
  assert.equal(total, 131, `A chapter total must match the complete manifest: ${total}`);
  assert.equal(new Set(addedParagraphs).size, addedParagraphs.length, "A authored paragraphs must be distinct");
});

test("Worker A quality ledger matches authored changes without source-status promotion", () => {
  const content = readJson("data/handbook-content.json");
  const quality = readJson("docs/handbook-quality/2026-10-20-worker-a-quality-inventory.json");
  assert.equal(quality.inventory.length, 51);
  assert.equal(quality.primary_text_checks, 0);
  assert.equal(new Set(quality.changed_service_ids).size, 17);
  const actual = new Set();
  for (const item of quality.inventory) {
    const id = `${item.service_id}/${item.chapter_id}`;
    assert.ok(!actual.has(id), `duplicated quality ledger entry: ${id}`);
    actual.add(id);
    const authored = content.services[item.service_id]?.chapters[item.chapter_id];
    assert.ok(authored, `missing chapter: ${id}`);
    assert.equal(
      item.chapter_id === "national_qa" ? authored.paragraphs[0] : authored.paragraphs.at(-1),
      item.after_substantive_change.replace(" は検索候補であり", " は参照候補であり"),
      `quality ledger prose mismatch: ${id}`);
    assert.equal(item.checkpoints_changed, 2);
    assert.ok(authored.checkpoints.slice(-2).some(p => p.includes(item.document_or_record_to_check)),
      `missing verifiable documents: ${id}`);
    assert.ok(["SOURCE_CANDIDATE_ONLY", "EVIDENCE_GAP"].includes(item.source_status));
    assert.equal(item.currentness_status, "NOT_ESTABLISHED");
    assert.equal(item.provider_applicability_status, "NOT_ESTABLISHED");
  }
  assert.deepEqual(actual, new Set(quality.changed_chapter_ids));
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

test("C equipment and care-management old text remains exact and 30 new chapters project", () => {
  const content = readJson("data/handbook-content.json");
  const legacy = readJson("tests/fixtures/handbook-c-legacy.json");
  assert.equal(legacy.source_commit, "5688a8691e974728062fc9dc6e9d06264fab62cb");
  const addedSections = {
    "welfare-equipment-rental": ["designation", "staffing", "equipment", "records", "incident_and_infection"],
    "preventive-welfare-equipment-rental": ["designation", "staffing", "equipment", "records", "safeguarding"],
    "specific-welfare-equipment-sale": ["designation", "staffing", "equipment", "records", "safeguarding"],
    "specific-preventive-welfare-equipment-sale": ["designation", "staffing", "equipment", "records", "safeguarding"],
    "care-management": ["designation", "staffing", "records", "safeguarding", "notifications"],
    "preventive-support": ["designation", "staffing", "records", "safeguarding", "notifications"],
  };
  const completionSections = {
    "welfare-equipment-rental": ["safeguarding", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "preventive-welfare-equipment-rental": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "specific-welfare-equipment-sale": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "specific-preventive-welfare-equipment-sale": ["incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "notifications", "national_qa", "sources_and_history"],
    "care-management": ["equipment", "incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "national_qa", "sources_and_history"],
    "preventive-support": ["equipment", "incident_and_infection", "business_continuity", "remuneration", "deductions", "additions", "national_qa", "sources_and_history"],
  };
  const expected = [
    ["welfare-equipment-rental", "第205条", "貸与"],
    ["preventive-welfare-equipment-rental", "第276条", "介護予防"],
    ["specific-welfare-equipment-sale", "第216条", "購入費"],
    ["specific-preventive-welfare-equipment-sale", "第289条", "介護予防"],
    ["care-management", "第30条", "居宅サービス計画"],
    ["preventive-support", "第32条", "介護予防サービス計画"],
  ];
  const allParagraphs = [];
  for (const [serviceId, source, term] of expected) {
    const chapters = content.services[serviceId]?.chapters;
    assert.deepEqual(Object.keys(chapters || {}).sort(), [
      "applicability", "operations", ...addedSections[serviceId], ...completionSections[serviceId],
    ].sort());
    const projected = serviceHandbook(serviceId);
    for (const sectionId of ["applicability", "operations"]) {
      const added = chapters[sectionId];
      const preserved = legacy.services[serviceId][sectionId];
      if (sectionId === "operations") {
        assert.deepEqual(added.paragraphs.slice(0, preserved.paragraphs.length), preserved.paragraphs, `legacy prose changed: ${serviceId}:${sectionId}`);
        assert.deepEqual(added.checkpoints.slice(0, preserved.checkpoints.length), preserved.checkpoints, `legacy checkpoints changed: ${serviceId}:${sectionId}`);
        assert.equal(added.paragraphs.length, preserved.paragraphs.length + 1, `operations editorial paragraph: ${serviceId}`);
        assert.equal(added.checkpoints.length, preserved.checkpoints.length + 2, `operations editorial checkpoints: ${serviceId}`);
      } else {
        assert.deepEqual(added, preserved, `legacy changed: ${serviceId}:${sectionId}`);
      }
      const chapter = projected.chapters.find(ch => ch.section_id === sectionId);
      assert.ok(chapter, serviceId + ":" + sectionId);
      assert.ok(added.paragraphs.length >= 2 && added.checkpoints.length >= 3);
      assert.deepEqual(chapter.paragraphs, added.paragraphs, serviceId + ":" + sectionId);
      assert.deepEqual(chapter.checkpoints, added.checkpoints, serviceId + ":" + sectionId);
      assert.equal(chapter.editorial_state, "作成中・未確認");
      allParagraphs.push(...added.paragraphs);
    }
    for (const sectionId of addedSections[serviceId]) {
      const authored = chapters[sectionId];
      const chapter = projected.chapters.find(ch => ch.section_id === sectionId);
      assert.ok(chapter, `${serviceId}:${sectionId} projection missing`);
      assert.ok(authored.paragraphs.length >= 2 && authored.checkpoints.length >= 3, `${serviceId}:${sectionId} insufficient content`);
      assert.ok(authored.paragraphs.every(p => p.length >= 80), `${serviceId}:${sectionId} too short`);
      assert.ok(authored.paragraphs.some(p => p.includes("参照候補")), `${serviceId}:${sectionId} missing source candidate`);
      assert.deepEqual(chapter.paragraphs, authored.paragraphs, `${serviceId}:${sectionId} paragraphs`);
      assert.deepEqual(chapter.checkpoints, authored.checkpoints, `${serviceId}:${sectionId} checkpoints`);
      assert.equal(chapter.editorial_state, "作成中・未確認");
      allParagraphs.push(...authored.paragraphs);
    }
    const prose = Object.values(chapters).flatMap(ch => ch.paragraphs).join(" ");
    assert.ok(prose.includes(source), serviceId + " missing source " + source);
    assert.ok(prose.includes(term), serviceId + " missing distinction " + term);
  }
  assert.equal(new Set(allParagraphs).size, allParagraphs.length, "duplicated boilerplate paragraphs");
});

test("chapter evidence anchor is linked and long drafting text wraps", () => {
  const tsx = fs.readFileSync("components/service-handbook.tsx", "utf8");
  const css = fs.readFileSync("app/globals.css", "utf8");
  assert.match(tsx, /href=\{\x60#handbook-sources-/);
  assert.match(tsx, /id=\{\x60handbook-sources-/);
  assert.match(tsx, /手引のこの章へ戻る/);
  assert.match(tsx, /個別資料が未登録のため、法令等の全候補から探す/);
  assert.match(css, /\.handbook-checkpoints li\{overflow-wrap:anywhere\}/);
});


// Staffing role display is strictly opt-in; old chapters and scope databases are unmodified.
test("staffing roles are an optional backward-compatible projection", () => {
  const authored = readJson("data/handbook-content.json").services;
  for (const service of serviceHandbooks) {
    for (const chapter of service.chapters) {
      const value = authored[service.service_id]?.chapters?.[chapter.section_id];
      assert.deepEqual(chapter.role_sections, value?.role_sections, service.service_id + "/" + chapter.section_id);
      if (chapter.role_sections) {
        assert.ok(["homevisit", "small-scale-multifunctional"].includes(service.service_id));
        assert.equal(chapter.section_id, "staffing");
      }
    }
  }
  assert.equal(serviceHandbooks.length, 39);
  assert.equal(serviceHandbooks.reduce((total, service) => total + service.chapters.length, 0), 585);
});

test("role data rejects out-of-scope fields, unsafe links and false verification", async () => {
  const { spawnSync } = await import("node:child_process");
  const script = String.raw\`import importlib.util,json,sys
spec=importlib.util.spec_from_file_location("handbook_builder","scripts/build_handbook_site.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
sid,chapter,roles=json.load(sys.stdin)
try:
    module.validate_role_sections(sid,chapter,roles)
except ValueError as exc:
    print(exc)
    sys.exit(2)
\`;
  const valid = [{
    id: "manager", title: "管理者", requirements: [{
      id: "placement", title: "配置", aspect: "placement",
      description: "原典確認待ちです。", applicability: "適用範囲未確認",
      verification_state: "EVIDENCE_GAP", evidence: [], practical_checks: [],
    }],
  }];
  const check = (roles, sid = "homevisit", chapter = "staffing") =>
    spawnSync("python", ["-c", script], { input: JSON.stringify([sid, chapter, roles]), encoding: "utf8" });
  assert.equal(check(valid).status, 0);
  assert.equal(check(valid, "dayservice").status, 2);
  assert.equal(check(valid, "homevisit", "equipment").status, 2);
  assert.equal(check([...valid, valid]).status, 2);
  assert.equal(check([{ ...valid[0], evil: "unknown" }]).status, 2);
  assert.equal(check([{ ...valid[0], requirements: [{ ...valid[0].requirements[0], verification_state: "PRIMARY_TEXT_CHECKED_SCOPED" }] }]).status, 2);
  const example = {
    kind: "national_standard", title: "条文", issuer: "e-Gov",
    locator: "第1条", version: "未確認", scope: "未確認", checked_at_jst: "",
    verification_state: "SOURCE_CANDIDATE_UNVERIFIED",
  };
  for (const url of ["javascript:alert(1)", "https://www.mhlw.go.jp.evil.example/a",
      "https://www.mhlw.go.jp@evil.example/a", "https://www.mhlw.go.jp:444/a",
      "https://www.mhlw.go.jp/a#page=bad", "data:text/html,abc"]) {
    const item = [{ ...valid[0], requirements: [{ ...valid[0].requirements[0],
      evidence: [{ ...example, url }] }] }];
    assert.equal(check(item).status, 2, url);
  }
  assert.equal(check([{ ...valid[0], requirements: [{ ...valid[0].requirements[0],
      description: "<img src=x onerror=alert(1)>" }] }]).status, 2);
  assert.equal(check([{ ...valid[0], requirements: [{ ...valid[0].requirements[0],
      evidence: [{ ...example, kind: "invalid" }] }] }]).status, 2);
  assert.equal(check([{ ...valid[0], requirements: [{ ...valid[0].requirements[0],
      evidence: [{ ...example, verification_state: "PRIMARY_TEXT_CHECKED_SCOPED", url: "https://laws.e-gov.go.jp/law/abc" }] }] }]).status, 2);
});
