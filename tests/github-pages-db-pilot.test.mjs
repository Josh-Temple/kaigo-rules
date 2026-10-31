// Compares the private browser-index experiment with a separately assembled
// reference taken from app/databases/search/page.tsx. Never deploy the output.
import test, { after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import care from "../data/care-insurance-act-nodes.json" with { type: "json" };
import ordinance from "../data/ordinance37-nodes.json" with { type: "json" };
import qa from "../data/qa-corpus.json" with { type: "json" };
import { publicNoticeRecords } from "../lib/notice-database.ts";
import { listServices } from "../lib/service-catalog.ts";
import { publicUnitPriceRows, unitPriceHref } from "../lib/unit-price-discovery.ts";
import {
  filterProgressivePublishedRules, filterProgressivePublishedRecords, getProgressiveSourceRecords,
} from "../lib/publication-policy.ts";
import {
  DELEGATED_REMUNERATION_SOURCE_FAMILY as DELEGATED,
  GOVERNING_STANDARDS_SOURCE_FAMILY as STANDARDS,
  publicSourceFamiliesForService,
} from "../lib/public-source-navigation.ts";
import { rankDatabaseSearch } from "../lib/database-search.ts";
import { buildPilot } from "../experiments/github-pages-db/build.mjs";
import { chromePath, chromeSmoke } from "../experiments/github-pages-db/chrome-smoke.mjs";

const pilot = buildPilot();
console.log("Private DB pilot: " + pilot.bytes + " bytes / " + pilot.files.length +
  " files; global.json=" + pilot.files.find((f) => f.name === "global.json").bytes +
  " bytes; service nodes checked=" + pilot.checkedServiceNodes);
after(() => fs.rmSync(pilot.dir, { recursive: true, force: true }));
const browser = await import(pathToFileURL(path.join(pilot.dir, "search.mjs")));
const services = listServices();
const publicServices = services.filter((s) => publicSourceFamiliesForService(s.service_id).length);
const readRows = (file) => JSON.parse(fs.readFileSync(path.join(pilot.dir, file), "utf8"));
const join = (x) => x.filter(Boolean).join(" ");

function fixture(serviceId) {
  const selected = services.find((s) => s.service_id === serviceId);
  const families = selected ? publicSourceFamiliesForService(serviceId) : [];
  const active = selected && families.length ? selected : null;
  const hasStandards = families.some((x) => x.source_family === STANDARDS);
  const nodes = active && hasStandards ? getProgressiveSourceRecords(serviceId) : ordinance;
  const nodeMap = new Map();
  const lawMap = new Map();
  for (const [source, map] of [[nodes, nodeMap], [care, lawMap]]) {
    for (const node of source) {
      const list = map.get(node.article_num) || [];
      list.push(node); map.set(node.article_num, list);
    }
  }
  const articleFields = (a, map) => [
    { value: (map.get(a.article_num) || []).map((n) => n.official_text).filter(Boolean).join(" "), weight: 10 },
    { value: [a.article_title, a.caption].filter(Boolean).join(" "), weight: 9 },
    { value: [...(a.path || []), a.service_scope].filter(Boolean).join(" "), weight: 5 },
    { value: a.source_locator || "", weight: 2 },
  ];
  const articleCandidates = nodes.filter((n) => n.node_type === "article");
  const scoped = serviceId
    ? active && hasStandards ? filterProgressivePublishedRules(serviceId, articleCandidates, (n) => n.id) : []
    : articleCandidates;
  if (serviceId && active && hasStandards) {
    const articleNumbers = new Set(scoped.map((n) => n.article_num));
    const used = nodes.filter((n) => articleNumbers.has(n.article_num));
    const permitted = filterProgressivePublishedRecords(serviceId, STANDARDS, used, (n) => n.id);
    assert.equal(permitted.length, used.length, "Unpublished child node in scoped search: " + serviceId);
  }
  const delegated = active && families.some((x) => x.source_family === DELEGATED)
    ? getProgressiveSourceRecords(serviceId, DELEGATED) : [];
  const unit = publicUnitPriceRows(serviceId || undefined);
  return (q) => {
    const by = (rows, f) => rankDatabaseSearch(rows, q, f);
    const law = serviceId ? [] : by(care.filter((n) => n.node_type === "article"), (r) => articleFields(r, lawMap));
    const rules = by(scoped, (r) => articleFields(r, nodeMap));
    const notices = serviceId ? [] : by(publicNoticeRecords, (n) => [
      { value: n.body_text, weight: 10 }, { value: n.title, weight: 9 },
      { value: join([n.service_label, n.section]), weight: 5 },
      { value: (n.number_path || []).join(" "), weight: 2 },
    ]);
    const questions = serviceId ? [] : by(qa, (r) => [
      { value: r.question || "", weight: 10 }, { value: r.answer || "", weight: 8 },
      { value: r.topic || "", weight: 6 },
      { value: join([r.scope, r.service_label, r.current_service_scope]), weight: 5 },
      { value: r.standard_label || "", weight: 3 }, { value: join([r.issued_source, r.number]), weight: 1 },
    ]);
    const prices = by(unit, (r) => [
      { value: [r.region_class, r.service_label].join(" "), weight: 10 },
      { value: [r.ratio_text, String(r.unit_price_yen) + "円"].join(" "), weight: 8 },
      { value: "地域区分 一単位単価 単価", weight: 4 }, { value: r.source_locator, weight: 1 },
    ]);
    const delegatedMatches = by(delegated, (r) => [
      { value: r.official_text || "", weight: 10 }, { value: r.heading || "", weight: 9 },
      { value: join([r.item_label, r.source_document_title]), weight: 5 },
      { value: r.source_locator || "", weight: 2 },
    ]);
    return {
      law: law.map((r) => ({ id: r.id, href: "/law/" + r.article_num })),
      ordinance: rules.map((r) => ({ id: r.id, href: "/rules/" + r.article_num + (active ? "?service=" + encodeURIComponent(serviceId) : "") })),
      unitPrice: prices.map((r) => ({ id: r.id, href: unitPriceHref(r.service_id, q) })),
      delegated: delegatedMatches.map((r) => ({ id: r.id, href: "/fees/criteria?service=" + encodeURIComponent(serviceId) + "#" + r.id })),
      notice: notices.map((r) => ({ id: r.id, href: "/notices?service=" + r.service_id + "#" + r.id })),
      qa: questions.map((r) => ({ id: r.id, href: "/qa/" + encodeURIComponent(r.id) })),
    };
  };
}

test("projection keeps the original search results and links across services", { timeout: 300000 }, () => {
  const words = [
    "看護職員", "生活相談員", "常勤換算", "個別機能訓練加算", "送迎",
    "業務継続計画", "ＢＣＰ", "看護師", "デイサービス", "介護職員　配置",
    "地域区分", "架空語ゼロ件xyz",
  ];
  const cases = [{ id: "", file: "global.json", words }];
  for (const service of publicServices) {
    cases.push({ id: service.service_id, file: "service-" + service.service_id + ".json",
      words: ["看護職員", "生活相談員", "常勤換算", "送迎", "ＢＣＰ", "地域区分"] });
  }
  let comparisons = 0;
  for (const c of cases) {
    const reference = fixture(c.id);
    const data = readRows(c.file);
    for (const q of c.words) {
      const expected = reference(q);
      const found = browser.runSearch(data, q);
      for (const group of browser.GROUPS) {
        const actual = found[group].map((row) => ({ id: row.id, href: browser.resultHref(group, row, q) }));
        assert.deepEqual(actual, expected[group], c.id + " / " + q + " / " + group);
      }
      comparisons += 1;
    }
  }
  console.log("DB parity scenarios: " + comparisons + " / " + comparisons + " across " + publicServices.length + " services");
});

test("category filtering and projection exclude internal metadata fields", () => {
  const data = readRows("global.json");
  const all = browser.runSearch(data, "看護職員");
  assert.ok(all.qa.length > 0);
  for (const selected of browser.GROUPS) {
    const found = browser.runSearch(data, "看護職員", selected);
    assert.deepEqual(found[selected], all[selected]);
    for (const group of browser.GROUPS.filter((g) => g !== selected)) assert.equal(found[group].length, 0);
  }
  const permitted = new Set(["id", "title", "href", "excerpt", "excerptField", "sourceUrl", "serviceId", "statusText", "fields"]);
  for (const group of browser.GROUPS) for (const row of data[group]) {
    assert.ok(Object.keys(row).every((key) => permitted.has(key)));
    assert.ok(row.href.startsWith("/") && !row.href.startsWith("//"));
  }
  assert.equal(fs.existsSync(path.join(pilot.dir, "handbook-preview")), false);
  const relative = path.relative(fs.realpathSync(path.resolve(import.meta.dirname, "..")), fs.realpathSync(pilot.dir));
  assert.ok(relative === ".." || relative.startsWith(".." + path.sep) || path.isAbsolute(relative));
});

test("refuses to build temporary search data inside the repository", () => {
  const previous = process.env.TMPDIR;
  process.env.TMPDIR = path.resolve(import.meta.dirname, "..");
  try {
    assert.throws(() => buildPilot(), /Temporary output cannot be inside/);
  } finally {
    if (previous === undefined) delete process.env.TMPDIR;
    else process.env.TMPDIR = previous;
  }
});

test("headless Chrome can search without horizontal overflow", { timeout: 110000 }, async (t) => {
  if (!chromePath) {
    if (process.env.GITHUB_ACTIONS === "true") {
      assert.fail("Chrome is unavailable on the Actions runner; browser verification did not run");
    }
    t.skip("Chrome is not installed; real-browser and Android checks remain open");
    return;
  }
  for (const width of [360, 390]) {
    const result = await chromeSmoke(pilot.dir, width);
    console.log("Chrome viewport: requested=" + result.requestedWidth + " actual=" + result.actualWidth +
      " scrollWidth=" + result.scrollWidth + " searchMs=" + result.searchMs +
      " readyMs=" + result.readyMs + " heapBytes=" + result.heapBytes +
      " keyboard=" + result.keyboard + " touch=" + result.touch + " pinchScale=" +
      result.pinchScale + " printed=" + result.printed);
  }
});
