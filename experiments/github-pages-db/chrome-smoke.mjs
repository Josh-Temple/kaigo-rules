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

export async function chromeSmoke(dir, requestedWidth) {
  assert.ok(chromePath, "Chrome is unavailable");
  const types = { ".html": "text/html; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8", ".css": "text/css; charset=utf-8" };
  const server = http.createServer((req, res) => {
    const name = new URL(req.url, "http://127.0.0.1").pathname.replace(/^\//, "") || "index.html";
    if (!/^[a-zA-Z0-9._-]+$/.test(name) || name.includes("..")) { res.writeHead(404).end(); return; }
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
    ], { stdio: "ignore" });
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
    const url = "http://127.0.0.1:" + server.address().port + "/?" + params;
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
    await client.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    await client.send("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    const focused = await value(client, "document.activeElement && document.activeElement.id");
    assert.equal(focused, "query", "Keyboard focus did not reach the search input");
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
    return { requestedWidth, actualWidth: result.width, scrollWidth: result.scrollWidth,
      searchMs: result.searchMs, readyMs: result.readyMs, heapBytes: result.heapBytes,
      keyboard: true, touch: true, unitGroups, pinchScale, printed: true };
  } finally {
    if (client) client.close();
    if (child && child.exitCode === null) {
      child.kill("SIGTERM");
      await Promise.race([new Promise((resolve) => child.once("exit", resolve)), pause(3000)]);
      if (child.exitCode === null) child.kill("SIGKILL");
    }
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(profile, { recursive: true, force: true });
  }
}
