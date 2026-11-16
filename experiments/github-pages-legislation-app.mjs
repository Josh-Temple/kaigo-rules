// Client-side version of the existing public /legislation browse-and-filter page.
// Every text node uses textContent; links use locally generated opaque filenames.
const form = document.querySelector("#legal-form");
const service = document.querySelector("#service");
const category = document.querySelector("#category");
const documentSelect = document.querySelector("#document");
const q = document.querySelector("#q");
const results = document.querySelector("#legal-results");
const summary = document.querySelector("#legal-summary");
const pagination = document.querySelector("#legal-pagination");
const pageSize = 30;
let docs = [];
let records = [];
let services = [];
let page = 1;

function node(tag, content) {
  const el = document.createElement(tag);
  if (content !== undefined) el.textContent = content;
  return el;
}
function option(value, label) {
  const el = node("option", label); el.value = value; return el;
}
function validUrl(key) {
  return typeof key === "string" && /^[a-f0-9]{64}\.html$/.test(key);
}
function populate() {
  const categories = {
    law: "介護保険法", standards: "基準省令",
    notices: "基準解釈通知", remuneration: "報酬基準",
    guidance: "算定上の留意事項", criteria: "報酬算定基準（別告示）",
  };
  for (const [id, label] of Object.entries(categories)) category.append(option(id, label));
  for (const row of services) service.append(option(row.id, row.label));
  refreshDocuments();
}
function refreshDocuments() {
  const choice = documentSelect.value;
  documentSelect.replaceChildren(option("", "すべての法令・通知"));
  for (const item of docs.filter(d => !category.value || d.category === category.value))
    documentSelect.append(option(item.id, item.title));
  if ([...documentSelect.options].some(x => x.value === choice)) documentSelect.value = choice;
}
function normalized(s) {
  return String(s || "").normalize("NFKC").toLocaleLowerCase("ja");
}
function matched() {
  const terms = normalized(q.value).trim().split(/\s+/u).filter(Boolean);
  const doc = documentSelect.value;
  return records.filter(row => {
    if (service.value && !row.services.includes(service.value)) return false;
    if (category.value && row.category !== category.value) return false;
    if (doc && row.document !== doc) return false;
    const haystack = normalized([row.id, row.label, row.title, row.locator, row.text,
      row.document_title].join(" "));
    return terms.every(term => haystack.includes(term));
  });
}
function updateUrl() {
  const params = new URLSearchParams();
  for (const [name, value] of [["service", service.value], ["category", category.value],
    ["document", documentSelect.value], ["q", q.value.trim()]]) if (value) params.set(name, value);
  if (page > 1) params.set("page", String(page));
  history.replaceState(null, "", location.pathname + (params.size ? "?" + params : ""));
}
function render() {
  const matches = matched();
  const totalPages = Math.max(1, Math.ceil(matches.length / pageSize));
  page = Math.min(totalPages, Math.max(1, page));
  summary.textContent = matches.length.toLocaleString("ja-JP") +
    "件の収載資料（原典掲載順・現行性や適用条件は原典を確認）";
  results.replaceChildren();
  if (!matches.length) {
    results.append(node("p", "該当する収載資料がありません。条件を変更してください。"));
  }
  for (const row of matches.slice((page-1)*pageSize, page*pageSize)) {
    const entry = node("section"); entry.className = "legal-row";
    const heading = node("h2");
    const title = node("a", row.label || row.title || "法令等の詳細");
    if (!validUrl(row.file)) throw new Error("不正な法令レコードの参照が見つかりました。");
    title.href = "./record/" + row.file;
    heading.append(title); entry.append(heading);
    const description = node("p", row.document_title + " / " + (row.title || row.locator));
    description.className = "source";
    entry.append(description);
    const excerpt = node("p", row.text.length > 260 ? row.text.slice(0, 260) + "…" : row.text);
    excerpt.className = "excerpt";
    entry.append(excerpt);
    results.append(entry);
  }
  pagination.replaceChildren();
  const previous = node("button", "前の30件"); previous.type = "button";
  previous.disabled = page === 1;
  previous.addEventListener("click", () => { page--; render(); updateUrl(); });
  const following = node("button", "次の30件"); following.type = "button";
  following.disabled = page >= totalPages;
  following.addEventListener("click", () => { page++; render(); updateUrl(); });
  pagination.append(previous, node("span", page + " / " + totalPages + "ページ"), following);
}
function loadQuery() {
  const params = new URLSearchParams(location.search);
  for (const [control, name] of [[service,"service"],[category,"category"],
    [documentSelect,"document"],[q,"q"]]) {
    const value = params.get(name) || "";
    if (control === q || [...control.options].some(x => x.value === value))
      control.value = value;
  }
  const requested = Number(params.get("page"));
  page = Number.isInteger(requested) && requested > 0 ? requested : 1;
}
try {
  const response = await fetch("./records.json", {cache: "no-store"});
  if (!response.ok) throw new Error("法令データを取得できませんでした。");
  const data = await response.json();
  if (!Array.isArray(data.docs) || !Array.isArray(data.records) || !Array.isArray(data.services))
    throw new Error("法令データの形式を確認できませんでした。");
  docs = data.docs; records = data.records; services = data.services;
  populate(); loadQuery(); refreshDocuments(); render();
  form.addEventListener("submit", event => { event.preventDefault(); page=1; render(); updateUrl(); });
  category.addEventListener("change", () => {documentSelect.value=""; refreshDocuments();});
  window.addEventListener("popstate", () => { loadQuery(); render(); });
} catch (error) {
  summary.textContent = error.message || "法令データを読み込めませんでした。";
}
