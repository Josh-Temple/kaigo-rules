import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

function deferred() {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

async function setup() {
  const nodes = new Map();
  function node() {
    return { value: '', textContent: '', dataset: {}, children: [], listeners: {},
      append(...items) { this.children.push(...items); },
      replaceChildren(...items) { this.children = items; },
      addEventListener(name, fn) { this.listeners[name] = fn; } };
  }
  for (const name of ['search', 'query', 'service', 'category', 'status', 'results']) nodes.set('#' + name, node());
  const requests = new Map();
  const calls = [];
  const context = vm.createContext({
    document: { querySelector: (name) => nodes.get(name) || null, createElement: node },
    location: { pathname: '/search/', search: '' }, history: { replaceState() {} },
    URL, URLSearchParams, performance,
    GROUPS: ['law', 'qa'],
    runSearch(data, q, category) { calls.push({ data, q, category }); return { law: [], qa: [] }; },
    resultHref() {}, databaseSearchExcerpt() {},
    loadJson(file) {
      if (file === './services.json') return Promise.resolve([{ id: 'a', file: 'a.json', label: 'A' }, { id: 'b', file: 'b.json', label: 'B' }]);
      const d = deferred(); requests.set(file, d); return d.promise;
    },
  });
  const source = fs.readFileSync(new URL('../experiments/github-pages-db/app.mjs', import.meta.url), 'utf8')
    .replace(/^import .*;\n/gm, '');
  await vm.runInContext(`(async () => {\n${source}\n})()`, context);
  function submit(q, service, category) {
    nodes.get('#query').value = q; nodes.get('#service').value = service; nodes.get('#category').value = category;
    nodes.get('#search').listeners.submit({ preventDefault() {} });
  }
  return { nodes, requests, calls, submit };
}
const flush = () => new Promise((resolve) => setImmediate(resolve));

test('an earlier failed request does not erase the newer search', async () => {
  const x = await setup();
  x.submit('古い検索', 'a', 'law');
  x.submit('新しい検索', 'b', 'qa');
  x.requests.get('./b.json').resolve({});
  await flush();
  assert.equal(x.nodes.get('#status').textContent, '0件見つかりました。');
  x.requests.get('./a.json').reject(new Error('古い通信の失敗'));
  await flush();
  assert.equal(x.nodes.get('#status').textContent, '0件見つかりました。');
  assert.equal(x.nodes.get('#results').children.length, 1);
  assert.equal(x.calls.length, 1);
  assert.equal(x.calls[0].q, '新しい検索');
});

test('search uses the category selected when it was submitted', async () => {
  const x = await setup();
  x.submit('介護', 'a', 'law');
  x.nodes.get('#category').value = 'qa';
  x.requests.get('./a.json').resolve({});
  await flush();
  assert.equal(x.calls[0].category, 'law');
  assert.equal(x.nodes.get('#results').children[0].children[0].textContent, '介護保険法（0件）');
});

test('the current request still shows an error', async () => {
  const x = await setup();
  x.submit('介護', 'a', 'law');
  x.requests.get('./a.json').reject(new Error('読み込み失敗'));
  await flush();
  assert.equal(x.nodes.get('#status').textContent, '読み込み失敗');
});
