import { runSearch, resultHref, GROUPS } from "./search.mjs";
import { databaseSearchExcerpt } from "./rank-core.mjs";

const labels = {
  law: "介護保険法", ordinance: "基準省令", unitPrice: "一単位単価・地域区分",
  delegated: "報酬算定基準（別告示）", notice: "基準解釈通知", qa: "国Q&A",
};
const form = document.querySelector("#search");
const query = document.querySelector("#query");
const service = document.querySelector("#service");
const category = document.querySelector("#category");
const status = document.querySelector("#status");
const results = document.querySelector("#results");
const localLegalDetails = document.querySelector('meta[name="kaigo-legal-local-details"]')?.content === "true";
const cache = new Map();
let services = [];
let latestSearch = 0;

async function json(file) {
  if (!cache.has(file)) {
    const response = await fetch("./" + file);
    if (!response.ok) throw new Error("データを読み込めませんでした。");
    cache.set(file, await response.json());
  }
  return cache.get(file);
}

function element(tag, text) {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}

function internalLink(label, href) {
  if (!href.startsWith("/") || href.startsWith("//")) throw new Error("不正なリンクを検出しました。");
  const destination = new URL(href, "https://kaigo-rules.vercel.app");
  if (destination.origin !== "https://kaigo-rules.vercel.app") throw new Error("不正なリンクを検出しました。");
  const link = element("a", label);
  const legal = destination.pathname.match(/^\/(law|rules)\/([0-9]+(?:-[0-9]+)*(?::[0-9]+(?:-[0-9]+)*)?)\/?$/);
  const params = [...destination.searchParams.keys()];
  const selectedService = destination.searchParams.get("service") || "";
  if (localLegalDetails && legal && !destination.hash &&
      params.every((key) => key === "service") && params.length <= 1 &&
      (!selectedService || /^[a-z0-9-]+$/.test(selectedService))) {
    link.href = "./legal/" + legal[1] + "/" + (selectedService || "all") + "/" +
      legal[2].replace(":", "__range__") + ".html";
  } else {
    link.href = destination.href;
  }
  return link;
}

function appendSource(card, url) {
  if (!url) return;
  const source = new URL(url);
  if (!["https:", "http:"].includes(source.protocol) || source.username || source.password) {
    throw new Error("不正な原典リンクを検出しました。");
  }
  const original = element("a", "原典を見る");
  original.href = source.href;
  original.rel = "noopener noreferrer";
  card.append(original);
}

async function display() {
  const searchNumber = ++latestSearch;
  const q = query.value.trim();
  if (!q) { results.replaceChildren(); status.textContent = "キーワードを入力してください。"; return; }
  const selected = services.find((x) => x.id === service.value);
  if (service.value && !selected) {
    results.replaceChildren(); status.textContent = "このサービスは現在の検索対象ではありません。"; return;
  }
  status.textContent = "検索しています。";
  const data = await json(selected ? selected.file : "global.json");
  if (searchNumber !== latestSearch) return;
  const start = performance.now();
  const found = runSearch(data, q, category.value);
  const duration = performance.now() - start;
  results.replaceChildren();
  let count = 0;
  for (const group of GROUPS) {
    if (category.value && category.value !== group) continue;
    const rows = found[group];
    count += rows.length;
    const section = document.createElement("section");
    if (group === "unitPrice") {
      const services = new Map();
      for (const row of rows) {
        const matches = services.get(row.serviceId) || [];
        matches.push(row);
        services.set(row.serviceId, matches);
      }
      section.append(element("h2", labels[group] + "（" + rows.length.toLocaleString("ja-JP") +
        "件 / " + services.size.toLocaleString("ja-JP") + "サービス）"));
      for (const matches of [...services.values()].slice(0, 20)) {
        const first = matches[0];
        const card = document.createElement("article"); card.className = "result";
        card.append(internalLink(first.serviceLabel, resultHref(group, first, q)));
        card.append(element("p", matches.length + "区分が検索条件に一致 / " +
          matches.slice(0, 3).map((r) => r.regionClass + "：" + r.unitPrice.toFixed(2) + "円").join("、") +
          (matches.length > 3 ? " ほか" : "")));
        card.append(element("p", "現行性：公開条件を満たした現行資料" +
          (first.checkedAt ? " / 公式表示確認日：" + first.checkedAt : "")));
        appendSource(card, first.sourceUrl);
        section.append(card);
      }
      if (!rows.length) section.append(element("p", "現在の公開範囲では一致なし"));
      if (services.size > 20) section.append(element("p", "上位20サービスを表示しています。"));
      results.append(section);
      continue;
    }
    section.append(element("h2", labels[group] + "（" + rows.length.toLocaleString("ja-JP") + "件）"));
    for (const row of rows.slice(0, 10)) {
      const card = document.createElement("article");
      card.className = "result";
      // This prototype does not include destination pages. Keep navigation on
      // the current site, and do not trust a row with an off-origin URL.
      card.append(internalLink(row.title, resultHref(group, row, q)));
      const excerpt = Number.isInteger(row.excerptField) ? row.fields[row.excerptField]?.value : row.excerpt;
      if (excerpt) card.append(element("p", databaseSearchExcerpt(excerpt, q)));
      if (row.statusText) card.append(element("p", row.statusText));
      appendSource(card, row.sourceUrl);
      section.append(card);
    }
    if (!rows.length) section.append(element("p", "現在の公開範囲では一致なし"));
    if (rows.length > 10) section.append(element("p", "上位10件を表示しています。"));
    results.append(section);
  }
  status.textContent = count.toLocaleString("ja-JP") + "件見つかりました。";
  status.dataset.searchMs = String(duration);
}

function handleError(error) {
  results.replaceChildren(); status.textContent = error.message || "検索できませんでした。";
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const params = new URLSearchParams();
  if (query.value.trim()) params.set("q", query.value.trim());
  if (service.value) params.set("service", service.value);
  if (category.value) params.set("category", category.value);
  history.replaceState(null, "", location.pathname + (params.size ? "?" + params : ""));
  display().catch(handleError);
});

try {
  services = await json("services.json");
  for (const item of services) {
    const option = element("option", item.label); option.value = item.id; service.append(option);
  }
  const params = new URLSearchParams(location.search);
  query.value = params.get("q") || "";
  const requestedService = params.get("service") || "";
  if (requestedService && !services.some((x) => x.id === requestedService)) {
    const unknown = element("option", "指定されたサービスは検索対象ではありません");
    unknown.value = requestedService;
    service.append(unknown);
  }
  service.value = requestedService;
  const requestedCategory = params.get("category") || "";
  category.value = GROUPS.includes(requestedCategory) ? requestedCategory : "";
  await display();
} catch (error) { handleError(error); }
