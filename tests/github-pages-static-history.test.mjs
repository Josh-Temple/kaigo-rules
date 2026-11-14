// Build-free DOM simulation for Back/Forward on the two static search screens.
// Does not replace an independent Chromium or Android acceptance test.
import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import vm from "node:vm";

class Element {
  constructor(tag = "div") {
    this.tag = tag;
    this.children = [];
    this.value = "";
    this.textContent = "";
    this.handlers = {};
    this.disabled = false;
  }
  get options() { return this.children.filter((item) => item.tag === "option"); }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  addEventListener(name, handler) { this.handlers[name] = handler; }
  fire(name) { this.handlers[name]?.({ preventDefault() {} }); }
}

function environment(selectors, search = "") {
  const nodes = Object.fromEntries(selectors.map((id) => [id, new Element()]));
  const doc = {
    createElement: (tag) => new Element(tag),
    querySelector: (selector) => nodes[selector] || null,
  };
  for (const selector of selectors.filter((id) => /-service$|-standard$|^#category$|^#document$/.test(id))) {
    nodes[selector].append(new Element("option"));
  }
  const location = { pathname: "/qa.html", search };
  const history = {
    pushes: 0,
    pushState(_state, _title, path) {
      this.pushes++;
      location.search = path.includes("?") ? "?" + path.split("?").slice(1).join("?") : "";
    },
  };
  const window = { handlers: {}, addEventListener(name, callback) { this.handlers[name] = callback; } };
  return { nodes, document: doc, location, history, window };
}

async function runSource(path, context) {
  const source = fs.readFileSync(new URL(path, import.meta.url), "utf8");
  await vm.runInNewContext("(async () => {\n" + source + "\n})()", context);
}

test("static legislation filters restore the correct document on browser Back", async () => {
  const env = environment(["#legal-form", "#service", "#category", "#document", "#q",
    "#legal-results", "#legal-summary", "#legal-pagination"],
    "?category=standards&document=standards-1&q=人員");
  env.location.pathname = "/legislation/index.html";
  const data = {
    docs: [{ id: "standards-1", title: "基準省令", category: "standards" },
      { id: "notices-1", title: "基準解釈通知", category: "notices" }],
    services: [{ id: "dayservice", label: "通所介護" }],
    records: [
      { id: "a", category: "standards", document: "standards-1", services: [],
        label: "人員", document_title: "基準省令", title: "人員", text: "人員",
        file: "a".repeat(64) + ".html" },
      { id: "b", category: "notices", document: "notices-1", services: [],
        label: "通知", document_title: "通知", title: "通知", text: "通知",
        file: "b".repeat(64) + ".html" },
    ],
  };
  const context = { ...env, URLSearchParams, fetch: async () => ({ ok: true, json: async () => data }) };
  await runSource("../experiments/github-pages-legislation-app.mjs", context);
  assert.equal(env.nodes["#category"].value, "standards");
  assert.equal(env.nodes["#document"].value, "standards-1");
  env.nodes["#category"].value = "notices";
  env.nodes["#category"].fire("change");
  env.nodes["#document"].value = "notices-1";
  env.nodes["#q"].value = "";
  env.nodes["#legal-form"].fire("submit");
  assert.equal(env.history.pushes, 1);
  assert.match(env.location.search, /document=notices-1/);
  env.location.search = "?category=standards&document=standards-1&q=%E4%BA%BA%E5%93%A1";
  env.window.handlers.popstate();
  assert.equal(env.nodes["#category"].value, "standards");
  assert.equal(env.nodes["#document"].value, "standards-1");
  assert.equal(env.nodes["#q"].value, "人員");
});

test("static Q&A pagination and reader mode restore on browser Back", async () => {
  const env = environment(["#qa-search", "#qa-query", "#qa-service", "#qa-standard",
    "#qa-status", "#qa-results", "#qa-page", "#qa-prev", "#qa-next",
    'meta[name="kaigo-qa-local-details"]', "h1"], "?q=%E7%9C%8B%E8%AD%B7");
  env.nodes['meta[name="kaigo-qa-local-details"]'].content = "true";
  const entries = Array.from({ length: 24 }, (_, i) => ({
    id: "q." + i, question: "看護について" + i, answer: "回答",
    service: "dayservice", standard_label: "基準省令", scope: "scope",
    issued_source: "国", number: "" + i,
  }));
  const searchQaEntries = (rows, state) => {
    const filtered = rows.filter((item) => item.question.includes(state.q));
    const totalPages = Math.max(1, Math.ceil(filtered.length / 10));
    const page = Math.min(totalPages, Math.max(1, Number(state.page) || 1));
    return { visible: filtered.slice((page - 1) * 10, page * 10),
      total: filtered.length, totalPages, page };
  };
  const context = { ...env, URLSearchParams, encodeURIComponent, searchQaEntries,
    qaFromSearchRow: (item) => item,
    loadJson: async () => ({ qa: entries }),
    fetch: async () => ({ ok: true, json: async () => [["dayservice", "通所介護"]] }) };
  // Remove import declarations only: the named dependencies above are mocked.
  const original = fs.readFileSync(new URL("../experiments/github-pages-db/qa-app.mjs", import.meta.url), "utf8");
  const source = original.replace(/^import .*;\n/gm, "");
  await vm.runInNewContext("(async () => {\n" + source + "\n})()", context);
  assert.equal(env.nodes["#qa-page"].textContent, "1 / 3ページ");
  env.nodes["#qa-next"].fire("click");
  assert.equal(env.nodes["#qa-page"].textContent, "2 / 3ページ");
  assert.match(env.location.search, /page=2/);
  env.location.search = "?q=%E7%9C%8B%E8%AD%B7&reader=1";
  env.window.handlers.popstate();
  assert.equal(env.nodes["#qa-page"].textContent, "1 / 3ページ");
  assert.equal(env.nodes["h1"].textContent, "通所介護の関連Q&Aを探す");
});

test("static database search filters restore on browser Back", async () => {
  const env = environment(["#search", "#query", "#service", "#category", "#status", "#results",
    'meta[name="kaigo-legal-local-details"]', 'meta[name="kaigo-qa-local-details"]'],
    "?q=%E7%9C%8B%E8%AD%B7&service=dayservice&category=standards");
  env.location.pathname = "/databases/search/index.html";
  const servicesData = [{ id: "dayservice", label: "通所介護" }];
  const groups = ["law", "ordinance", "unitPrice", "delegated", "notice", "qa"];
  const dataset = Object.fromEntries(groups.map((group) => [group, []]));
  const context = {
    ...env,
    URL, URLSearchParams, performance: { now: () => 0 },
    runSearch: () => dataset, resultHref: (_group, row) => row.href || "",
    GROUPS: groups, databaseSearchExcerpt: (value) => value,
    loadJson: async (path) => path.includes("services.json") ? servicesData : dataset,
  };
  const original = fs.readFileSync(new URL("../experiments/github-pages-db/app.mjs", import.meta.url), "utf8");
  const source = original.replace(/^import .*;\n/gm, "");
  await vm.runInNewContext("(async () => {\n" + source + "\n})()", context);
  assert.equal(env.nodes["#query"].value, "看護");
  assert.equal(env.nodes["#service"].value, "dayservice");
  assert.equal(env.nodes["#category"].value, "ordinance");

  env.location.search = "?q=%E7%94%9F%E6%B4%BB%E7%9B%B8%E8%AB%87%E5%93%A1&service=dayservice&category=guidance";
  env.window.handlers.popstate();
  assert.equal(env.nodes["#query"].value, "生活相談員");
  assert.equal(env.nodes["#category"].value, "notice");
});

