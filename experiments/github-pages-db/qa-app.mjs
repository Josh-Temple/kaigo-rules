import { searchQaEntries } from "./qa-core.mjs";
import { qaFromSearchRow } from "./qa-projection.mjs";
import { loadJson } from "./load-json.mjs";

const form = document.querySelector("#qa-search");
const query = document.querySelector("#qa-query");
const service = document.querySelector("#qa-service");
const standard = document.querySelector("#qa-standard");
const status = document.querySelector("#qa-status");
const results = document.querySelector("#qa-results");
const pageLabel = document.querySelector("#qa-page");
const prev = document.querySelector("#qa-prev");
const next = document.querySelector("#qa-next");
const localDetails = document.querySelector('meta[name="kaigo-qa-local-details"]')?.content === "true";
const params = new URLSearchParams(location.search);
let current = { q: params.get("q") || "", service: params.get("service") || "",
  standard: params.get("standard") || "", page: params.get("page") || "1",
  reader: params.get("reader") === "1" };
let entries = [];

function element(tag, text) {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}
function addOption(select, code, label) {
  const option = element("option", label);
  option.value = code;
  select.append(option);
}
function retainUnknown(select, value) {
  if (value && ![...select.options].some((option) => option.value === value)) {
    addOption(select, value, "指定された条件");
  }
  select.value = value;
}
function writeUrl() {
  const nextParams = new URLSearchParams();
  if (current.q.trim()) nextParams.set("q", current.q.trim());
  if (current.service) nextParams.set("service", current.service);
  if (current.standard) nextParams.set("standard", current.standard);
  if (current.reader) nextParams.set("reader", "1");
  if (current.page > 1) nextParams.set("page", String(current.page));
  history.replaceState(null, "", location.pathname + (nextParams.size ? "?" + nextParams : ""));
}
function render() {
  const found = searchQaEntries(entries, current);
  current.page = found.page;
  status.textContent = found.total.toLocaleString("ja-JP") + "件見つかりました。";
  pageLabel.textContent = found.page + " / " + found.totalPages + "ページ";
  prev.disabled = found.page <= 1;
  next.disabled = found.page >= found.totalPages;
  results.replaceChildren();
  if (!found.total) {
    results.append(element("p", "該当するQ&Aがありません。語や条件を変えて検索してください。"));
    return;
  }
  for (const item of found.visible) {
    const card = document.createElement("section"); card.className = "result";
    const details = current.reader ? (item.standard_label || "介護サービスに関するQ&A") :
      (item.scope + " ・ " + (item.standard_label || "基準種別なし") +
       (item.current_service_scope ? " / 2019年以降の分類：" + item.current_service_scope : ""));
    card.append(element("p", details));
    if (item.topic) card.append(element("p", item.topic));
    const title = document.createElement("h2");
    const link = element("a", item.question);
    link.href = localDetails
      ? "./qa-details/" + encodeURIComponent(item.id) + (current.reader ? "/reader.html" : "/index.html")
      : "https://kaigo-rules.vercel.app/qa/" + encodeURIComponent(item.id) + (current.reader ? "?reader=1" : "");
    title.append(link); card.append(title);
    card.append(element("p", item.answer));
    card.append(element("p", [item.issued_source, item.number].filter(Boolean).join(" / ")));
    card.append(element("p", "収載済み・現行性未確認"));
    results.append(card);
  }
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  current = { ...current, q: query.value, service: service.value, standard: standard.value, page: 1 };
  render(); writeUrl();
});
prev.addEventListener("click", () => { current.page -= 1; render(); writeUrl(); });
next.addEventListener("click", () => { current.page += 1; render(); writeUrl(); });

try {
  if (current.reader) document.querySelector("h1").textContent = "通所介護の関連Q&Aを探す";
  const [data, optionsResponse] = await Promise.all([loadJson("./global.json"), fetch("./qa-options.json")]);
  if (!optionsResponse.ok) throw new Error("検索データを読み込めませんでした。");
  const options = await optionsResponse.json();
  entries = data.qa.map(qaFromSearchRow);
  options.sort(([a], [b]) => {
    const an = Number(a), bn = Number(b);
    if (Number.isFinite(an) && Number.isFinite(bn)) return an - bn;
    if (Number.isFinite(an)) return -1;
    if (Number.isFinite(bn)) return 1;
    return a.localeCompare(b, "ja");
  });
  for (const [code, label] of options) addOption(service, code, label);
  for (const value of [...new Set(entries.map((item) => item.standard_label).filter(Boolean))].sort((a, b) => a.localeCompare(b, "ja"))) {
    addOption(standard, value, value);
  }
  query.value = current.q;
  retainUnknown(service, current.service);
  retainUnknown(standard, current.standard);
  render();
} catch (error) {
  results.replaceChildren();
  status.textContent = error.message || "検索データを読み込めませんでした。";
}
