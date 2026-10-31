import { searchQaEntries } from "./search-core.mjs";

const form = document.querySelector("#search-form");
const status = document.querySelector("#status");
const results = document.querySelector("#results");
const prev = document.querySelector("#prev");
const next = document.querySelector("#next");
const pagination = document.querySelector("#pagination");
let entries = [];
let current = { q: "", service: "", standard: "", page: 1 };

function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}

function populateOptions(rows) {
  const services = new Map();
  const standards = new Set();
  rows.forEach((row) => {
    services.set(row.service_code, row.scope || row.service_label || row.service_code);
    if (row.standard_label) standards.add(row.standard_label);
  });
  const serviceSelect = form.elements.namedItem("service");
  const standardSelect = form.elements.namedItem("standard");
  [...services.entries()].sort(([a], [b]) => a.localeCompare(b)).forEach(([code, label]) => {
    const option = document.createElement("option");
    option.value = code;
    option.textContent = label;
    serviceSelect.append(option);
  });
  [...standards].sort((a, b) => a.localeCompare(b, "ja")).forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    standardSelect.append(option);
  });
}

function render() {
  const matches = searchQaEntries(entries, current);
  status.textContent = matches.total.toLocaleString("ja-JP") + "件見つかりました。";
  pagination.textContent = matches.page + " / " + matches.totalPages + "ページ";
  prev.disabled = matches.page <= 1;
  next.disabled = matches.page >= matches.totalPages;
  current.page = matches.page;
  results.replaceChildren();
  if (matches.total === 0) {
    results.append(el("p", "該当するQ&Aがありません。語を短くするか条件を変えてください。"));
    return;
  }
  const fragment = document.createDocumentFragment();
  for (const item of matches.visible) {
    const article = document.createElement("article");
    article.append(el("p", (item.scope || item.service_label || "") + " ・ " + (item.standard_label || "基準種別なし"), "meta"));
    if (item.topic) article.append(el("p", item.topic, "meta"));
    const heading = el("h2");
    const link = el("a", item.question);
    link.href = "https://kaigo-rules.vercel.app/qa/" + encodeURIComponent(item.id) + "?reader=1";
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    heading.append(link);
    article.append(heading);
    article.append(el("p", item.answer));
    article.append(el("p", [item.issued_source, item.number].filter(Boolean).join(" / "), "meta"));
    article.append(el("p", "収載済み・現行性未確認", "meta"));
    fragment.append(article);
  }
  results.append(fragment);
}

function setPage(page) {
  current.page = page;
  render();
}
form.addEventListener("submit", (event) => {
  event.preventDefault();
  current = {
    q: form.elements.namedItem("q").value,
    service: form.elements.namedItem("service").value,
    standard: form.elements.namedItem("standard").value,
    page: 1,
  };
  render();
});
prev.addEventListener("click", () => setPage(current.page - 1));
next.addEventListener("click", () => setPage(current.page + 1));

try {
  const response = await fetch(new URL("./qa-dayservice.json", import.meta.url));
  if (!response.ok) throw new Error("HTTP " + response.status);
  entries = await response.json();
  populateOptions(entries);
  render();
} catch {
  status.textContent = "検索データを読み込めませんでした。公開用の静的データが作成されているか確認してください。";
}
