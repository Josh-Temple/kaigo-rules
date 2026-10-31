// Optional headless Chrome smoke check. It serves the private experiment on
// loopback only and does not store screenshots or deploy any output.
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

export async function chromeSmoke(dir, requestedWidth) {
  assert.ok(chromePath, "Chrome is unavailable");
  const injection = `<script>
document.addEventListener("DOMContentLoaded",()=>{
 const status=document.querySelector("#status");
 const measure=()=>{document.documentElement.dataset.testViewport=String(window.innerWidth);
 document.documentElement.dataset.testScrollWidth=String(document.documentElement.scrollWidth)};
 new MutationObserver(measure).observe(status,{childList:true,subtree:true,characterData:true});
 measure();
});
</script>`;
  const types = { ".html": "text/html; charset=utf-8", ".mjs": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8", ".css": "text/css; charset=utf-8" };
  const server = http.createServer((req, res) => {
    const name = new URL(req.url, "http://127.0.0.1").pathname.replace(/^\//, "") || "index.html";
    if (!/^[a-zA-Z0-9._-]+$/.test(name) || name.includes("..")) { res.writeHead(404).end(); return; }
    try {
      let body = fs.readFileSync(path.join(dir, name));
      if (name === "index.html") body = Buffer.from(body.toString("utf8").replace("</head>", injection + "</head>"));
      res.writeHead(200, { "Content-Type": types[path.extname(name)] || "application/octet-stream" });
      res.end(body);
    } catch { res.writeHead(404).end(); }
  });
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "kaigo-chrome-profile-"));
  try {
    const params = new URLSearchParams({ q: "看護職員" });
    const url = "http://127.0.0.1:" + server.address().port + "/?" + params;
    const args = [
      "--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage",
      "--disable-background-networking", "--no-first-run", "--no-default-browser-check",
      "--user-data-dir=" + profile, "--window-size=" + requestedWidth + ",900",
      "--virtual-time-budget=12000", "--dump-dom", url,
    ];
    const output = await new Promise((resolve, reject) => {
      const child = spawn(chromePath, args, { stdio: ["ignore", "pipe", "ignore"] });
      let stdout = "";
      const timer = setTimeout(() => { child.kill("SIGKILL"); reject(new Error("Chrome timed out")); }, 45000);
      child.stdout.on("data", (chunk) => { stdout += chunk; if (stdout.length > 3000000) child.kill("SIGKILL"); });
      child.on("error", (error) => { clearTimeout(timer); reject(error); });
      child.on("close", (code) => { clearTimeout(timer); code === 0 ? resolve(stdout) : reject(new Error("Chrome exited " + code)); });
    });
    // Do not print page content into CI logs if a check fails.
    assert.ok(/件見つかりました/.test(output), "Chrome did not finish the search");
    assert.ok(/data-search-ms="[0-9.]+"/.test(output), "Search timing is absent");
    assert.ok(/https:\/\/kaigo-rules\.vercel\.app\/qa\//.test(output), "Q&A destination is absent");
    const width = Number(output.match(/data-test-viewport="(\d+)"/)?.[1]);
    const scrollWidth = Number(output.match(/data-test-scroll-width="(\d+)"/)?.[1]);
    assert.ok(width > 0 && scrollWidth > 0, "Missing viewport measurements");
    assert.ok(scrollWidth <= width, "Page overflows horizontally: " + scrollWidth + " > " + width);
    return { requestedWidth, actualWidth: width, scrollWidth };
  } finally {
    await new Promise((resolve) => server.close(resolve));
    fs.rmSync(profile, { recursive: true, force: true });
  }
}
