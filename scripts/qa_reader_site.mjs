/** Rendered reader audit. Run against a production build; it never changes legal data. */
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
import { execFileSync, spawn } from 'node:child_process';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core');
const root = process.cwd();
const output = path.resolve(process.env.READER_QA_OUTPUT || 'artifacts/reader-qa');
fs.mkdirSync(output, { recursive: true });
const baseline = process.argv.includes('--baseline');
const full = process.argv.includes('--full');
const origin = process.env.READER_QA_ORIGIN || 'http://127.0.0.1:3100';
let server;
if (process.argv.includes('--serve')) {
  const log = fs.openSync(path.join(output, 'server.log'), 'w');
  server = spawn(process.execPath, [require.resolve('next/dist/bin/next'), 'start', '--hostname', '127.0.0.1', '--port', new URL(origin).port || '3100'],
    { cwd: root, stdio: ['ignore', log, log] });
  let ready = false;
  for (let i = 0; i < 80; i++) {
    try { if ((await fetch(origin)).ok) { ready = true; break; } } catch {}
    if (server.exitCode !== null) throw Error('NEXT_SERVER_EXITED');
    await new Promise(resolve => setTimeout(resolve, 250));
  }
  if (!ready) { server.kill(); throw Error('NEXT_SERVER_NOT_READY'); }
}
const data = JSON.parse(fs.readFileSync('data/handbook.generated.json', 'utf8'));
const pilots = ['dayservice', 'dayrehab', 'homevisit'];
const keyRoutes = ['/', '/services', ...pilots.flatMap(s => ['/services/' + s, '/handbook/' + s + '/staffing']),
  '/handbook/dayservice/equipment', '/handbook/dayservice/operations', '/handbook/dayservice/remuneration',
  '/questions/nurse-staffing', '/qa?service=16&q=看護職員', '/sources', '/handbook-sources'];
const report = { head: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  tree: execFileSync('git', ['write-tree'], { encoding: 'utf8' }).trim(),
  baseline, full, started: new Date().toISOString(), cases: [], interactions: [], screenshots: [] };
const executablePath = process.env.CHROME_PATH;
const browser = await chromium.launch({ ...(executablePath ? { executablePath } : { channel: 'chrome' }),
  headless: true, args: ['--no-sandbox'] });
report.browser = browser.version();
try {
  const jobs = new Map();
  for (const route of keyRoutes) for (const width of [360, 390, 1280]) jobs.set(route + ':' + width, { route, width, key: true });
  if (full) for (const service of data.services) {
    for (const width of [360, 390, 1280]) jobs.set('/services/' + service.service_id + ':' + width, { route: '/services/' + service.service_id, width, service: true });
    for (const chapter of service.chapters) {
      const route = '/handbook/' + service.service_id + '/' + chapter.section_id.replaceAll('_', '-');
      jobs.set(route + ':390', { route, width: 390, chapter: true });
    }
  }
  const queue = [...jobs.values()];
  await Promise.all(Array.from({ length: 3 }, async () => {
    const context = await browser.newContext();
    const page = await context.newPage();
    // Analytics is irrelevant to reader acceptance and should not send test traffic.
    await page.route('**/_vercel/insights/**', route => route.abort());
    while (queue.length) {
      const job = queue.shift();
      const record = { ...job, errors: [] };
      try {
        await page.setViewportSize({ width: job.width, height: 844 });
        const response = await page.goto(origin + job.route, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.locator('h1').waitFor();
        Object.assign(record, await page.evaluate(() => {
          const main = document.querySelector('main');
          const text = main?.innerText || '';
          const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
          const anchors = [...document.querySelectorAll('a[href^="#"]')].map(el => el.getAttribute('href').slice(1)).filter(Boolean);
          return { title: document.querySelector('h1')?.textContent,
            h1: document.querySelectorAll('h1').length, width: document.documentElement.scrollWidth,
            canonical: document.querySelector('link[rel="canonical"]')?.href,
            robots: document.querySelector('meta[name="robots"]')?.content,
            duplicateIds: ids.filter((x, i) => ids.indexOf(x) !== i),
            brokenAnchors: anchors.filter(x => !document.getElementById(decodeURIComponent(x))),
            noise: (text.match(/\bJSON\b|EVIDENCE_GAP|Research Mesh|\bscope\b|(?:data|docs|scripts|tests)\/[A-Za-z0-9_./-]+\.(?:json|md|ts|txt)|canonical ID:|corpus ID:/gu) || []),
            warnings: (text.match(/未確認|確認中|未照合|未確定|未審査|確認前/gu) || []).length,
            roles: [...document.querySelectorAll('.handbook-role>h4')].map(el => el.textContent),
            chapterCount: document.querySelectorAll('.handbook-chapter').length,
            textLength: text.length,
            unsafeLinks: [...document.querySelectorAll('main a[href]')].filter(a => /^\s*(?:javascript|data|file):/iu.test(a.getAttribute('href'))).length };
        }));
        record.http = response?.status();
        if (record.http !== 200) record.errors.push('HTTP_NOT_200');
        if (record.h1 !== 1) record.errors.push('H1_NOT_ONE');
        if (record.width > job.width + 3) record.errors.push('HORIZONTAL_OVERFLOW');
        if (record.duplicateIds.length) record.errors.push('DUPLICATE_IDS');
        if (record.brokenAnchors.length) record.errors.push('BROKEN_ANCHORS');
        if (record.unsafeLinks) record.errors.push('UNSAFE_LINK');
        if ((job.route.startsWith('/handbook/') || /^\/services\/[^/?]+$/.test(job.route)) && !record.robots?.includes('noindex')) record.errors.push('NOINDEX_MISSING');
        if (!baseline && record.noise.length) record.errors.push('INTERNAL_TEXT_VISIBLE');
        if (/^\/services\/[^/?]+$/.test(job.route) && record.chapterCount !== 15) record.errors.push('CHAPTER_COUNT_CHANGED');
        if (job.width === 390 && (job.key || job.service)) {
          const filename = job.route.split('?')[0].replaceAll('/', '_') || '_home';
          const shot = filename + '-390.png';
          await page.screenshot({ path: path.join(output, shot), animations: 'disabled' });
          report.screenshots.push(shot);
        }
      } catch (e) { record.errors.push(String(e).slice(0, 300)); }
      record.status = record.errors.length ? 'FAIL' : 'PASS';
      report.cases.push(record);
    }
    await context.close();
  }));
  if (!baseline) {
    const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await page.goto(origin + '/services/dayservice');
    await page.locator('.handbook-staffing-entry a').click();
    await page.locator('#staffing .handbook-role-navigation a[href="#staffing-role-nurse"]').click();
    await page.screenshot({ path: path.join(output, 'dayservice-nurse-390.png') });
    await page.locator('#staffing-role-nurse a[href="/questions/nurse-staffing"]').click();
    await page.locator('a[href="/services/dayservice#staffing-role-nurse"]').click();
    report.interactions.push({ flow: 'service → nurse → Q&A → same role', status: page.url().endsWith('#staffing-role-nurse') ? 'PASS' : 'FAIL' });
    await page.goto(origin + '/handbook/dayservice/staffing');
    const checkbox = page.locator('input[type="checkbox"]').first();
    await checkbox.check();
    const checked = await checkbox.isChecked();
    await checkbox.press('Space');
    const keyboard = !await checkbox.isChecked();
    await checkbox.check();
    await page.reload();
    report.interactions.push({ flow: 'labelled checklist, keyboard and reload reset', status: checked && keyboard && !await checkbox.isChecked() ? 'PASS' : 'FAIL' });
    await page.emulateMedia({ media: 'print' });
    await page.pdf({ path: path.join(output, 'dayservice-staffing.pdf'), format: 'A4', printBackground: true });
    report.pdf = 'dayservice-staffing.pdf';
    await page.close();
  }
} finally {
  await browser.close();
  server?.kill();
  report.finished = new Date().toISOString();
  report.failures = report.cases.filter(x => x.status === 'FAIL').map(x => ({ route: x.route, width: x.width, errors: x.errors }));
  fs.writeFileSync(path.join(output, 'report.json'), JSON.stringify(report, null, 2));
}
console.log(JSON.stringify({ head: report.head, browser: report.browser, cases: report.cases.length,
  failures: report.failures.length, interactions: report.interactions, output }));
if (!baseline && (report.failures.length || report.interactions.some(x => x.status !== 'PASS'))) process.exitCode = 1;
