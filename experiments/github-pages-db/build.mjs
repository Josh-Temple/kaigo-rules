// Private feasibility experiment. This is NOT a deployable Pages export.
// Run with: node --import ./experiments/github-pages-db/register.mjs ...
// Search content is written only under the OS temporary directory.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { stripTypeScriptTypes } from "node:module";
import care from "../../data/care-insurance-act-nodes.json" with { type: "json" };
import ordinance from "../../data/ordinance37-nodes.json" with { type: "json" };
import qa from "../../data/qa-corpus.json" with { type: "json" };
import { publicNoticeRecords } from "../../lib/notice-database.ts";
import { listServices } from "../../lib/service-catalog.ts";
import { publicUnitPriceRows } from "../../lib/unit-price-discovery.ts";
import { publicVerificationLabel } from "../../lib/public-verification.ts";
import {
  filterProgressivePublishedRecords, getProgressiveSourceRecords,
} from "../../lib/publication-policy.ts";
import {
  DELEGATED_REMUNERATION_SOURCE_FAMILY as DELEGATED,
  GOVERNING_STANDARDS_SOURCE_FAMILY as STANDARDS,
  publicSourceFamiliesForService,
} from "../../lib/public-source-navigation.ts";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const groups = ["law", "ordinance", "unitPrice", "delegated", "notice", "qa"];
const join = (a) => a.filter(Boolean).join(" ");

function groupArticles(nodes) {
  const byArticle = new Map();
  for (const node of nodes) {
    const array = byArticle.get(node.article_num) || [];
    array.push(node);
    byArticle.set(node.article_num, array);
  }
  return byArticle;
}

function articles(nodes, serviceId = "", filtered = null) {
  const byArticle = groupArticles(nodes);
  return (filtered || nodes.filter((x) => x.node_type === "article")).map((a) => ({
    id: String(a.id),
    title: join([a.article_title, a.caption]) || "条文",
    href: (serviceId || nodes === ordinance ? "/rules/" : "/law/") + a.article_num +
      (serviceId ? "?service=" + encodeURIComponent(serviceId) : ""),
    excerpt: "", sourceUrl: "",
    fields: [
      { value: join((byArticle.get(a.article_num) || []).map((n) => n.official_text)), weight: 10 },
      { value: join([a.article_title, a.caption]), weight: 9 },
      { value: join([...(a.path || []), a.service_scope]), weight: 5 },
      { value: a.source_locator || "", weight: 2 },
    ],
  }));
}

function unitRows(serviceId) {
  return publicUnitPriceRows(serviceId || undefined).map((r) => ({
    id: r.id, title: r.service_label + " / " + r.region_class,
    href: "/fees/unit-price?service=" + encodeURIComponent(r.service_id),
    excerpt: r.region_class + "：" + r.unit_price_yen.toFixed(2) + "円",
    sourceUrl: r.source_url,
    serviceId: r.service_id,
    fields: [
      { value: [r.region_class, r.service_label].join(" "), weight: 10 },
      { value: [r.ratio_text, String(r.unit_price_yen) + "円"].join(" "), weight: 8 },
      { value: "地域区分 一単位単価 単価", weight: 4 },
      { value: r.source_locator, weight: 1 },
    ],
  }));
}

function notices() {
  return publicNoticeRecords.map((n) => ({
    id: n.id, title: n.title,
    href: "/notices?service=" + n.service_id + "#" + n.id,
    excerptField: 0, sourceUrl: "",
    statusText: "本文：" + publicVerificationLabel(n.content_verification, "content") +
      " / 現行性：" + publicVerificationLabel(n.currentness_state, "currentness") +
      " / 人手確認：" + publicVerificationLabel(n.human_review_state, "human"),
    fields: [
      { value: n.body_text, weight: 10 }, { value: n.title, weight: 9 },
      { value: join([n.service_label, n.section]), weight: 5 },
      { value: (n.number_path || []).join(" "), weight: 2 },
    ],
  }));
}

function questions() {
  return qa.map((q) => ({
    id: q.id, title: q.question,
    href: "/qa/" + encodeURIComponent(q.id),
    excerptField: 1, sourceUrl: "",
    fields: [
      { value: q.question || "", weight: 10 }, { value: q.answer || "", weight: 8 },
      { value: q.topic || "", weight: 6 },
      { value: join([q.scope, q.service_label, q.current_service_scope]), weight: 5 },
      { value: q.standard_label || "", weight: 3 },
      { value: join([q.issued_source, q.number]), weight: 1 },
    ],
  }));
}

function delegatedRows(records, serviceId) {
  return records.map((r) => ({
    id: String(r.id), title: r.heading || r.item_label || r.id,
    href: "/fees/criteria?service=" + encodeURIComponent(serviceId) + "#" + r.id,
    excerptField: 0, sourceUrl: r.source_url || "",
    fields: [
      { value: r.official_text || "", weight: 10 }, { value: r.heading || "", weight: 9 },
      { value: join([r.item_label, r.source_document_title]), weight: 5 },
      { value: r.source_locator || "", weight: 2 },
    ],
  }));
}

function empty() { return Object.fromEntries(groups.map((key) => [key, []])); }

function validate(rows) {
  const allowed = new Set(["id", "title", "href", "excerpt", "excerptField", "sourceUrl", "serviceId", "statusText", "fields"]);
  for (const group of groups) {
    for (const row of rows[group]) {
      if (!row.id || !row.title || typeof row.href !== "string" || !row.href.startsWith("/") ||
          row.href.startsWith("//") || Object.keys(row).some((key) => !allowed.has(key))) {
        throw new Error("Invalid search projection: " + group + " / " + row.id);
      }
      if (row.fields.some((field) => typeof field.value !== "string" || !Number.isFinite(field.weight))) {
        throw new Error("Invalid search field: " + group + " / " + row.id);
      }
    }
  }
}

export function buildPilot() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "kaigo-db-search-private-"));
  const global = empty();
  global.law = articles(care);
  global.ordinance = articles(ordinance);
  global.unitPrice = unitRows("");
  global.notice = notices();
  global.qa = questions();
  validate(global);
  fs.writeFileSync(path.join(dir, "global.json"), JSON.stringify(global));
  const services = [];
  let delegatedUnsafe = 0;
  let checkedServiceNodes = 0;
  for (const item of listServices()) {
    const families = publicSourceFamiliesForService(item.service_id);
    if (!families.length) continue;
    if (!/^[a-z0-9-]+$/.test(item.service_id)) throw new Error("Invalid service id");
    const rows = empty();
    if (families.some((x) => x.source_family === STANDARDS)) {
      const nodes = getProgressiveSourceRecords(item.service_id);
      const permitted = filterProgressivePublishedRecords(item.service_id, STANDARDS, nodes, (n) => n.id);
      const permittedIds = new Set(permitted.map((n) => n.id));
      const selected = nodes.filter((n) => n.node_type === "article" && permittedIds.has(n.id));
      const articleNumbers = new Set(selected.map((n) => n.article_num));
      const usedNodes = nodes.filter((n) => articleNumbers.has(n.article_num));
      if (usedNodes.some((n) => !permittedIds.has(n.id))) {
        throw new Error("A scoped article would expose a node outside its publication gate: " + item.service_id);
      }
      checkedServiceNodes += usedNodes.length;
      rows.ordinance = articles(nodes, item.service_id, selected);
    }
    rows.unitPrice = unitRows(item.service_id);
    if (families.some((x) => x.source_family === DELEGATED)) {
      const source = getProgressiveSourceRecords(item.service_id, DELEGATED);
      const checked = filterProgressivePublishedRecords(item.service_id, DELEGATED, source, (r) => r.id);
      delegatedUnsafe += source.length - checked.length;
      // Fail closed: do not put a record that did not pass the shared policy in the pilot.
      if (source.length !== checked.length) throw new Error("Delegated search requires publication review");
      rows.delegated = delegatedRows(checked, item.service_id);
    }
    validate(rows);
    const file = "service-" + item.service_id + ".json";
    fs.writeFileSync(path.join(dir, file), JSON.stringify(rows));
    services.push({ id: item.service_id, label: item.label, file });
  }
  fs.writeFileSync(path.join(dir, "services.json"), JSON.stringify(services));
  // The browser receives a direct stripped-JS copy of the current ranking logic,
  // so synonyms, normalisation, weights and tie-breaking stay in one source.
  const ranking = fs.readFileSync(path.join(root, "lib/database-search.ts"), "utf8");
  fs.writeFileSync(path.join(dir, "rank-core.mjs"), stripTypeScriptTypes(ranking, { mode: "strip" }));
  for (const name of ["index.html", "app.mjs", "search.mjs", "style.css"]) {
    fs.copyFileSync(path.join(root, "experiments/github-pages-db", name), path.join(dir, name));
  }
  const files = fs.readdirSync(dir).map((name) => ({ name, bytes: fs.statSync(path.join(dir, name)).size }));
  return { dir, files, bytes: files.reduce((a, b) => a + b.bytes, 0),
    services: services.length, globalCounts: Object.fromEntries(groups.map((k) => [k, global[k].length])),
    delegatedUnsafe, checkedServiceNodes };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const result = buildPilot();
  console.log(JSON.stringify(result, null, 2));
}
