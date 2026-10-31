// Compares the private browser-index experiment with a separately assembled
// reference taken from app/databases/search/page.tsx. Never deploy the output.
import test, { after } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import net from "node:net";
import path from "node:path";
import { spawn, spawnSync } from "node:child_process";
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
  const permitted = new Set(["id", "title", "href", "excerpt", "excerptField", "sourceUrl", "serviceId",
    "serviceLabel", "regionClass", "unitPrice", "checkedAt", "statusText", "fields"]);
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

test("rendered Next.js search agrees with the private browser index", { timeout: 180000 }, async (t) => {
  const root = path.resolve(import.meta.dirname, "..");
  const next = path.join(root, "node_modules/next/dist/bin/next");
  if (!fs.existsSync(next) || !fs.existsSync(path.join(root, ".next/BUILD_ID"))) {
    if (process.env.GITHUB_ACTIONS === "true") assert.fail("Built Next.js application is unavailable");
    t.skip("Built Next.js application is unavailable locally");
    return;
  }
  const reservation = net.createServer();
  await new Promise((resolve, reject) => { reservation.once("error", reject); reservation.listen(0, "127.0.0.1", resolve); });
  const port = reservation.address().port;
  await new Promise((resolve) => reservation.close(resolve));
  const child = spawn(process.execPath, [next, "start", "--hostname", "127.0.0.1", "--port", String(port)], {
    cwd: root, stdio: "ignore",
  });
  child.on("error", () => {});
  const get = (url) => new Promise((resolve, reject) => {
    const request = http.get({ hostname: "127.0.0.1", port, path: url, timeout: 30000 }, (response) => {
      const chunks = [];
      response.on("data", (chunk) => chunks.push(chunk));
      response.on("end", () => response.statusCode === 200
        ? resolve(Buffer.concat(chunks).toString("utf8"))
        : reject(new Error("Local Next.js returned " + response.statusCode)));
    });
    request.on("timeout", () => request.destroy(new Error("Local Next.js request timed out")));
    request.on("error", reject);
  });
  try {
    let ready = false;
    const deadline = Date.now() + 30000;
    while (!ready && Date.now() < deadline && child.exitCode === null) {
      try { await get("/api/version"); ready = true; }
      catch { await new Promise((resolve) => setTimeout(resolve, 200)); }
    }
    assert.ok(ready, "Local Next.js server did not start");
    const cases = [
      ["", "看護職員"], ["", "生活相談員"], ["", "常勤換算"],
      ["", "個別機能訓練加算"], ["", "送迎"], ["", "業務継続計画"],
      ["", "ＢＣＰ"], ["", "架空語ゼロ件xyz"],
      ["dayservice", "看護職員"], ["homevisit", "常勤換算"],
      ["dayrehab", "送迎"], ["nursing-small-scale-multifunctional", "業務継続計画"],
    ];
    for (const [serviceId, q] of cases) {
      const query = new URLSearchParams({ q });
      if (serviceId) query.set("service", serviceId);
      const html = await get("/databases/search?" + query);
      const extracted = spawnSync("python3", ["scripts/extract_database_search_snapshot.py"], {
        cwd: root, input: html, encoding: "utf8", maxBuffer: 2 * 1024 * 1024,
      });
      assert.equal(extracted.status, 0, "Could not read rendered search groups: " + extracted.stderr);
      const actual = JSON.parse(extracted.stdout);
      const rows = readRows(serviceId ? "service-" + serviceId + ".json" : "global.json");
      const ranked = browser.runSearch(rows, q);
      for (const group of browser.GROUPS) {
        let visible = ranked[group].slice(0, 10);
        if (group === "unitPrice") {
          const first = new Map();
          for (const row of ranked[group]) if (!first.has(row.serviceId)) first.set(row.serviceId, row);
          visible = [...first.values()].slice(0, 20);
        }
        const expected = { count: ranked[group].length, links: visible.map((row) => browser.resultHref(group, row, q)) };
        assert.deepEqual(actual[group], expected, "Rendered Next.js mismatch: " + serviceId + " / " + q + " / " + group);
      }
    }
    console.log("Rendered Next.js parity: " + cases.length + " / " + cases.length + " scenarios");
  } finally {
    if (child.exitCode === null) {
      child.kill("SIGTERM");
      await Promise.race([new Promise((resolve) => child.once("exit", resolve)), new Promise((resolve) => setTimeout(resolve, 3000))]);
      if (child.exitCode === null) child.kill("SIGKILL");
    }
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
      " keyboard=" + result.keyboard + " touch=" + result.touch + " unitGroups=" + result.unitGroups + " pinchScale=" +
      result.pinchScale + " printed=" + result.printed);
  }
});
