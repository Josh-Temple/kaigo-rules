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
    section.append(element("h2", labels[group] + "（" + rows.length.toLocaleString("ja-JP") + "件）"));
    for (const row of rows.slice(0, 10)) {
      const card = document.createElement("article");
      card.className = "result";
      const link = element("a", row.title);
      // This prototype does not include destination pages. Keep navigation on
      // the current site, and do not trust a row with an off-origin URL.
      const href = resultHref(group, row, q);
      if (!href.startsWith("/") || href.startsWith("//")) throw new Error("不正なリンクを検出しました。");
      const destination = new URL(href, "https://kaigo-rules.vercel.app");
      if (destination.origin !== "https://kaigo-rules.vercel.app") throw new Error("不正なリンクを検出しました。");
      link.href = destination.href;
      card.append(link);
      const excerpt = Number.isInteger(row.excerptField) ? row.fields[row.excerptField]?.value : row.excerpt;
      if (excerpt) card.append(element("p", databaseSearchExcerpt(excerpt, q)));
      if (row.statusText) card.append(element("p", row.statusText));
      if (row.sourceUrl) {
        const source = new URL(row.sourceUrl);
        if (!["https:", "http:"].includes(source.protocol)) throw new Error("不正な原典リンクを検出しました。");
        const original = element("a", "原典を見る");
        original.href = source.href;
        original.rel = "noopener noreferrer";
        card.append(original);
      }
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
