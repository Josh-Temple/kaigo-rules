// A lightweight DOM test for progressive results; no static build or Actions.
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
    this.dataset = {};
    this.handlers = {};
  }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  addEventListener(name, callback) { this.handlers[name] = callback; }
  click() { this.handlers.click?.({ preventDefault() {} }); }
}

test("static search reveals all matches in ordered, bounded batches", async () => {
  const ids = ["#search", "#query", "#service", "#category", "#status", "#results",
    'meta[name="kaigo-legal-local-details"]', 'meta[name="kaigo-qa-local-details"]'];
  const elements = Object.fromEntries(ids.map((key) => [key, new Element()]));
  elements['meta[name="kaigo-qa-local-details"]'].content = "true";
  const groups = ["law", "ordinance", "unitPrice", "delegated", "notice", "qa"];
  const dataset = Object.fromEntries(groups.map((group) => [group,
    group === "qa"
      ? Array.from({ length: 23 }, (_, i) => ({
          id: "qa-" + i, title: "質問" + i, href: "/qa/qa-" + i,
          excerpt: "看護職員", sourceUrl: "",
        }))
      : group === "unitPrice"
      ? Array.from({ length: 21 }, (_, i) => ({
          id: "unit-" + i, href: "/fees/unit-price", serviceId: "s" + i,
          serviceLabel: "サービス" + i, regionClass: "地域", unitPrice: 10, sourceUrl: "",
        })) : []]));
  const source = fs.readFileSync(
    new URL("../experiments/github-pages-db/app.mjs", import.meta.url), "utf8")
    .replace(/^import .*;\n/gm, "");
  await vm.runInNewContext("(async () => {\n" + source + "\n})()", {
    document: { querySelector: (name) => elements[name] || null,
      createElement: (tag) => new Element(tag) },
    location: { pathname: "/databases/search/index.html", search: "?q=看護" },
    history: { replaceState() {} },
    URL, URLSearchParams, performance: { now: () => 0 },
    runSearch: () => dataset, resultHref: (_group, row) => row.href,
    GROUPS: groups, databaseSearchExcerpt: (value) => value,
    loadJson: async (path) => path.includes("services.json") ? [] : dataset,
  });
  assert.match(elements["#status"].textContent, /44件/);
  const sections = elements["#results"].children;
  assert.equal(sections.length, 6);
  const units = sections[2];
  const qa = sections[5];
  assert.equal(units.children[1].children.length, 20);
  assert.equal(qa.children[1].children.length, 10);
  units.children[2].click();
  qa.children[2].click();
  assert.equal(units.children[1].children.length, 21);
  assert.equal(qa.children[1].children.length, 20);
  qa.children[2].click();
  assert.equal(qa.children[1].children.length, 23);
  assert.equal(qa.children[2].hidden, true);
  assert.equal(qa.children[1].children.at(-1).children[0].textContent, "質問22");
});
