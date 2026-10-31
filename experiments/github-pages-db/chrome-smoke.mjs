// Private Chrome smoke test: loopback server and temporary browser profile only.
// CDP sets the actual CSS viewport; --window-size alone has a 500px minimum.
import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { spawn } from "node:child_process";

const candidates = [
  process.env.CHROME_BIN, "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable",
  "/usr/bin/chromium", "/usr/bin/chromium-browser",
].filter(Boolean);
export const chromePath = candidates.find((p) => fs.existsSync(p));
const pause = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function httpJson(port, requestPath) {
  return new Promise((resolve, reject) => {
    const req = http.request({ hostname: "127.0.0.1", port, path: requestPath, method: "PUT" }, (res) => {
      let body = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => { body += chunk; });
      res.on("end", () => {
        if (res.statusCode !== 200) return reject(new Error("Chrome target request failed"));
        try { resolve(JSON.parse(body)); } catch (error) { reject(error); }
      });
    });
    req.on("error", reject);
    req.end();
  });
}

async function connect(url) {
  const ws = new WebSocket(url);
  await new Promise((resolve, reject) => {
    ws.addEventListener("open", resolve, { once: true });
    ws.addEventListener("error", reject, { once: true });
  });
  let sequence = 0;
  const pending = new Map();
  ws.addEventListener("message", (event) => {
    const message = JSON.parse(String(event.data));
    const current = pending.get(message.id);
    if (!current) return;
    pending.delete(message.id);
    clearTimeout(current.timer);
    if (message.error) current.reject(new Error(message.error.message));
    else current.resolve(message.result);
  });
  const send = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => { pending.delete(id); reject(new Error("Chrome command timed out: " + method)); }, 15000);
    pending.set(id, { resolve, reject, timer });
    ws.send(JSON.stringify({ id, method, params }));
  });
  return { send, close: () => ws.close() };
}

async function value(client, expression) {
  const result = await client.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error("Chrome evaluation failed");
  return result.result.value;
}

export async function chromeSmoke(dir, requestedWidth, options = {}) {
  assert.ok(chromePath, "Chrome is unavailable");
  const types = { ".html": "text/html; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
    ".js": "text/javascript; charset=utf-8", ".json": "application/json; charset=utf-8",
    ".css": "text/css; charset=utf-8" };
  const server = http.createServer((req, res) => {
    const name = new URL(req.url, "http://127.0.0.1").pathname.replace(/^\//, "") || "index.html";
    if (name.split("/").some((part) => !/^[a-zA-Z0-9._-]+$/.test(part) || part === "." || part === "..")) {
      res.writeHead(404).end(); return;
    }
    try {
      const body = fs.readFileSync(path.join(dir, name));
      res.writeHead(200, { "Content-Type": types[path.extname(name)] || "application/octet-stream" });
      res.end(body);
    } catch { res.writeHead(404).end(); }
  });
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "kaigo-chrome-profile-"));
  let child, client;
  try {
    child = spawn(chromePath, [
      "--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage",
      "--disable-background-networking", "--no-first-run", "--no-default-browser-check",
      "--enable-precise-memory-info", "--remote-debugging-address=127.0.0.1",
      "--remote-debugging-port=0", "--remote-allow-origins=*",
      "--user-data-dir=" + profile, "about:blank",
    ], { stdio: "ignore", detached: process.platform !== "win32" });
    child.on("error", () => {});
    const activePort = path.join(profile, "DevToolsActivePort");
    const startupDeadline = Date.now() + 15000;
    while (!fs.existsSync(activePort) && Date.now() < startupDeadline && child.exitCode === null) await pause(100);
    assert.ok(fs.existsSync(activePort), "Chrome did not start its local debugging endpoint");
    const port = Number(fs.readFileSync(activePort, "utf8").split("\n")[0]);
    const target = await httpJson(port, "/json/new?about:blank");
    client = await connect(target.webSocketDebuggerUrl);
    await client.send("Page.enable");
    await client.send("Runtime.enable");
    await client.send("Emulation.setDeviceMetricsOverride", {
      width: requestedWidth, height: 900, deviceScaleFactor: 1, mobile: true,
    });
    await client.send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 1 });
    const params = new URLSearchParams({ q: "看護職員" });
    const base = options.base || "/";
    if (!/^\/(?:[a-z0-9-]+\/)*$/.test(base)) throw new Error("Invalid test base path");
    const origin = "http://127.0.0.1:" + server.address().port;
    const url = origin + base + "index.html?" + params;
    await client.send("Page.navigate", { url });
    const expression = "(() => { const s=document.querySelector('#status');" +
      "if(!s || !s.dataset.searchMs || !s.textContent.includes('件見つかりました')) return null;" +
      "return {width:innerWidth,scrollWidth:document.documentElement.scrollWidth," +
      "qa:!!document.querySelector('a[href^=\"https://kaigo-rules.vercel.app/qa/\"]')," +
      "searchMs:Number(s.dataset.searchMs),readyMs:performance.now()," +
      "heapBytes:performance.memory ? performance.memory.usedJSHeapSize : null}; })()";
    let result = null;
    const searchDeadline = Date.now() + 30000;
    while (!result && Date.now() < searchDeadline) {
      result = await value(client, expression);
      if (!result) await pause(100);
    }
    assert.ok(result, "Chrome did not finish the search");
    assert.equal(result.width, requestedWidth, "Requested CSS viewport was not applied");
    assert.ok(result.scrollWidth <= result.width, "Page overflows horizontally");
    assert.ok(result.qa, "Q&A destination is absent");

    // Confirm actual keyboard focus progression and a touch-generated submit.
    // The integrated page has navigation links before the form. Verify that
    // Tab actually reaches the input rather than assuming it is the first stop.
    let focused = "";
    let keyboardSteps = 0;
    while (focused !== "query" && keyboardSteps < 12) {
      await client.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      await client.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      focused = await value(client, "document.activeElement && document.activeElement.id");
      keyboardSteps += 1;
    }
    assert.equal(focused, "query", "Keyboard focus did not reach the search input within 12 Tab presses");
    const point = await value(client, "(() => { window.__smokeSubmits=0; document.querySelector('#search').addEventListener('submit',()=>window.__smokeSubmits++); const r=document.querySelector('button').getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2}; })()");
    await client.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [point] });
    await client.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    await pause(300);
    assert.equal(await value(client, "window.__smokeSubmits"), 1, "Touch did not submit the form");

    await value(client, "document.querySelector('#query').value='地域区分'");
    await client.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [point] });
    await client.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
    let unitGroups = 0;
    const groupDeadline = Date.now() + 10000;
    while (!unitGroups && Date.now() < groupDeadline) {
      unitGroups = await value(client, "document.querySelectorAll('a[href^=\"https://kaigo-rules.vercel.app/fees/unit-price?\"]').length");
      if (!unitGroups) await pause(100);
    }
    assert.ok(unitGroups > 0 && unitGroups <= 20, "Unit prices were not grouped by service");

    await client.send("Emulation.setPageScaleFactor", { pageScaleFactor: 2 });
    const pinchScale = await value(client, "visualViewport.scale");
    assert.equal(pinchScale, 2, "200% pinch zoom was not applied");
    const pdf = await client.send("Page.printToPDF", { printBackground: true });
    assert.equal(Buffer.from(pdf.data, "base64").subarray(0, 5).toString(), "%PDF-", "Print did not produce a PDF");
    await client.send("Emulation.setPageScaleFactor", { pageScaleFactor: 1 });
    const qaParams = new URLSearchParams({ service: "16", page: "2", reader: "1" });
    await client.send("Page.navigate", { url: origin + base + "qa.html?" + qaParams });
    const qaExpression = "(() => { const s=document.querySelector('#qa-status'); if(!s || !s.textContent.includes('件見つかりました')) return null;" +
      "const links=[...document.querySelectorAll('#qa-results a')]; return {rows:links.length,page:document.querySelector('#qa-page').textContent," +
      "reader:links.every(a=>a.href.includes('reader=1')),width:innerWidth,scroll:document.documentElement.scrollWidth}; })()";
    let qaResult = null;
    const qaDeadline = Date.now() + 30000;
    while (!qaResult && Date.now() < qaDeadline) {
      try { qaResult = await value(client, qaExpression); } catch { /* navigation in progress */ }
      if (!qaResult) await pause(100);
    }
    assert.ok(qaResult && qaResult.rows === 30 && qaResult.page.startsWith("2 /") && qaResult.reader,
      "Full Q&A service filter or pagination did not work");
    assert.equal(qaResult.width, requestedWidth);
    assert.ok(qaResult.scroll <= qaResult.width, "Q&A page overflows horizontally");
    let handbook = null;
    if (options.handbook) {
      if (!/^\/handbook\/[a-z0-9-]+\/[a-z0-9-]+\.html$/.test(options.handbook)) throw new Error("Invalid handbook path");
      await client.send("Page.navigate", { url: origin + options.handbook });
      const deadline = Date.now() + 30000;
      while (!handbook && Date.now() < deadline) {
        try {
          handbook = await value(client, "(() => { const c=document.querySelector('input[type=checkbox]'); const b=document.querySelector('[data-handbook-print]'); if(document.readyState!=='complete'||!c||!b)return null; return {width:innerWidth,scroll:document.documentElement.scrollWidth}; })()");
        } catch { /* navigation in progress */ }
        if (!handbook) await pause(100);
      }
      assert.ok(handbook, "Handbook controls did not load");
      assert.equal(handbook.width, requestedWidth);
      assert.ok(handbook.scroll <= handbook.width, "Handbook page overflows horizontally");
      const checkbox = await value(client, "(() => {const c=document.querySelector('input[type=checkbox]'); c.scrollIntoView({block:'center',behavior:'instant'}); const r=c.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2,initial:c.checked};})()");
      await client.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x: checkbox.x, y: checkbox.y }] });
      await client.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
      await pause(100);
      assert.notEqual(await value(client, "document.querySelector('input[type=checkbox]').checked"), checkbox.initial,
        "Handbook checkbox did not respond to touch");
      const printButton = await value(client, "(() => {window.__handbookPrint=false; window.print=()=>window.__handbookPrint=true; const b=document.querySelector('[data-handbook-print]'); b.scrollIntoView({block:'center',behavior:'instant'}); const r=b.getBoundingClientRect(); return {x:r.left+r.width/2,y:r.top+r.height/2};})()");
      await client.send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [printButton] });
      await client.send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
      await pause(100);
      assert.equal(await value(client, "window.__handbookPrint"), true, "Handbook print button did not respond to touch");
      const handbookPdf = await client.send("Page.printToPDF", { printBackground: true });
      assert.equal(Buffer.from(handbookPdf.data, "base64").subarray(0, 5).toString(), "%PDF-");
    }
    return { requestedWidth, actualWidth: result.width, scrollWidth: result.scrollWidth,
      searchMs: result.searchMs, readyMs: result.readyMs, heapBytes: result.heapBytes,
      keyboard: true, keyboardSteps, touch: true, unitGroups, pinchScale, printed: true, qaRows: qaResult.rows, qaPage: qaResult.page,
      handbook: handbook ? { checkbox: true, printButton: true, printed: true } : null };
  } finally {
    if (client) client.close();
    if (child?.pid) {
      try {
        if (process.platform === "win32") child.kill("SIGTERM");
        else process.kill(-child.pid, "SIGTERM");
      } catch { /* already exited */ }
      if (child.exitCode === null) {
        await Promise.race([new Promise((resolve) => child.once("exit", resolve)), pause(3000)]);
      }
      try {
        if (process.platform === "win32") child.kill("SIGKILL");
        else process.kill(-child.pid, "SIGKILL");
      } catch { /* already exited */ }
      await pause(200);
    }
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(profile, { recursive: true, force: true, maxRetries: 12, retryDelay: 250 });
  }
}
