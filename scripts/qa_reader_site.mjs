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
  '/handbook/dayservice/equipment', '/handbook/dayservice/operations', '/handbook/dayservice/remuneration', '/handbook/dayservice/additions',
  '/questions/nurse-staffing', '/qa?service=16&q=看護職員', '/qa?reader=1&service=16&q=看護職員', '/sources', '/handbook-sources'];
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
      jobs.set(route + ':390', { ...jobs.get(route + ':390'), route, width: 390, chapter: true });
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
            roles: [...document.querySelectorAll('.handbook-role>h2,.handbook-role>h3,.handbook-role>h4')].map(el => el.textContent),
            municipalHandbookLinks: [...document.querySelectorAll('main a[href]')].filter(a => /city\.yokohama|yokohama.*tebiki/i.test(a.href)).length,
            municipalText: /横浜市/.test(text),
            inlineNationalQa: document.querySelectorAll('.dayservice-qa').length,
            nationalQaTopics: [...document.querySelectorAll('.dayservice-qa-topic')].map(el => el.textContent),
            feeTables: document.querySelectorAll('.dayservice-fee-table').length,
            feeTableRows: document.querySelectorAll('.dayservice-fee-table tbody tr').length,
            feeTableCells: document.querySelectorAll('.dayservice-fee-table tbody td').length,
            inlineCriteria: document.querySelectorAll('[data-source-id^="criteria95."]').length,
            appliedViews: document.querySelectorAll('.dayservice-applied-text').length,
            untranslatedAppliedViews: [...document.querySelectorAll('.dayservice-applied-text')].filter(el => /指定訪問(?:入浴)?介護|訪問介護員等/u.test(el.innerText)).length,
            longSourceLocators: [...document.querySelectorAll('.dayservice-excerpt-label span')].filter(el => el.textContent.length > 100).length,
            emptySourceParagraphs: [...document.querySelectorAll('.dayservice-original p')].filter(el => !el.textContent.trim()).length,
            repeatedCriteriaLabels: document.querySelectorAll('[data-source-id^="criteria95."] .dayservice-excerpt-label strong').length,
            chapterSequenceCount: document.querySelectorAll('nav[aria-label="前後の章"]').length,
            chapterCount: document.querySelectorAll('.handbook-chapter').length,
            readingGuides: document.querySelectorAll('.staffing-reading-guide').length,
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
        if (!baseline && (job.route === '/services/dayservice' || job.route.startsWith('/handbook/dayservice/'))) {
          if (record.municipalHandbookLinks || record.municipalText) record.errors.push('MUNICIPAL_HANDBOOK_REFERENCE_VISIBLE');
          if ((job.route === '/services/dayservice' || job.route === '/handbook/dayservice/staffing') && record.inlineNationalQa < 5) record.errors.push('ROLE_QA_NOT_INLINE');
          if (job.route === '/handbook/dayservice/additions' && record.nationalQaTopics.filter(topic => topic === '入浴介助加算（Ⅱ）').length !== 2) record.errors.push('BATHING_QA_APPLICABILITY_LOST');
          if (record.longSourceLocators) record.errors.push('SOURCE_LOCATOR_REPEATS_BODY');
          if (record.emptySourceParagraphs) record.errors.push('EMPTY_SOURCE_PARAGRAPH');
          if (record.repeatedCriteriaLabels) record.errors.push('CRITERIA_HEADING_REPEATED');
          if (job.route.startsWith('/handbook/dayservice/') && record.chapterSequenceCount !== 1) record.errors.push('CHAPTER_NAVIGATION_DUPLICATED_OR_MISSING');
          if (record.untranslatedAppliedViews) record.errors.push('READ_ACROSS_SERVICE_NAME_UNCHANGED');
          if (job.route === '/handbook/dayservice/remuneration' && (record.feeTables !== 3 || record.feeTableRows !== 18 || record.feeTableCells !== 90)) record.errors.push('BASIC_FEE_TABLE_INCOMPLETE');
          if (job.route === '/handbook/dayservice/additions' && record.inlineCriteria !== 11) record.errors.push('INLINE_MINISTERIAL_CRITERIA_MISSING');
          if (job.route === '/handbook/dayservice/operations' && record.appliedViews < 15) record.errors.push('READ_ACROSS_VIEW_MISSING');
        }
        if (!baseline) {
          const pilotService = pilots.some(s => job.route === '/services/' + s || job.route === '/handbook/' + s + '/staffing');
          if (record.readingGuides !== (pilotService ? 1 : 0)) record.errors.push('READING_GUIDE_OUTSIDE_STAFFING');
        }
        if (/^\/services\/[^/?]+$/.test(job.route) && record.chapterCount !== 15) record.errors.push('CHAPTER_COUNT_CHANGED');
        if ((job.width === 390 && (job.key || job.service)) || (job.width === 1280 && job.key)) {
          const filename = job.route.split('?')[0].replaceAll('/', '_') || '_home';
          const shot = filename + '-' + job.width + '.png';
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
    for (const width of [360, 390]) {
      await page.setViewportSize({ width, height: 844 });
      await page.goto(origin + '/handbook/dayservice/staffing');
      const firstStaffingTopic = await page.locator('.dayservice-reading-topic').first().getAttribute('id');
      for (const role of ['life-counselor', 'care-worker']) {
        const targetId = `staffing-role-${role}-example`;
        await page.locator(`#staffing-role-navigation a[href="#${targetId}"]`).click();
        await page.waitForFunction(id => {
          const top = document.getElementById(id)?.getBoundingClientRect().top;
          return top !== undefined && top >= -2 && top < innerHeight / 2;
        }, targetId, { timeout: 5000 });
        const example = page.locator(`#${targetId}`);
        const text = await example.innerText();
        const fits = await example.evaluate(element => [...element.querySelectorAll('figure,table,[role="img"],.dayservice-service-period')].every(child => {
          const rect = child.getBoundingClientRect();
          return rect.left >= 0 && rect.right <= innerWidth && child.scrollWidth <= child.clientWidth + 1;
        }));
        const numbers = role === 'life-counselor' ? text.includes('3時間＋5時間＝8時間') && text.includes('合計8時間') && text.includes('12時〜13時はサービス提供なし') && text.includes('3時間＋4時間＝7時間') && text.includes('1時間足りません') && text.includes('17〜18時') && await example.locator('.dayservice-counselor-comparison .dayservice-missing-hour').count() === 1
          : text.includes('20人全員が5時間利用') && text.includes('10時間') && text.includes('常時1人以上');
        report.interactions.push({ flow: `${width}px staffing → ${role} calculation on screen`, status: firstStaffingTopic === 'staffing-unit' && fits && numbers ? 'PASS' : 'FAIL' });
        if (role === 'life-counselor') {
          await page.screenshot({ path: path.join(output, `dayservice-counselor-example-${width}.png`) });
          await example.locator('a[href="#staffing-role-life-counselor-interpretation"]').click();
          await page.waitForFunction(() => {
            const caution = document.querySelector('#staffing-role-life-counselor-interpretation .dayservice-source-caution');
            const rect = caution?.getBoundingClientRect();
            return rect && rect.top >= 0 && rect.bottom <= innerHeight;
          }, undefined, { timeout: 5000 });
          report.interactions.push({ flow: `${width}px counselor calculation → source caution on screen`, status: 'PASS' });
        }
      }
      // Reader-first content added in PR #583: check the actual rendered chapter, not only the data table.
      await page.goto(origin + '/handbook/dayservice/staffing');
      const staffingRows = page.locator('.dayservice-staffing-overview tbody tr');
      report.interactions.push({
        flow: `${width}px staffing → five role summaries with in-page legal details`,
        status: await staffingRows.count() === 5 &&
          await staffingRows.filter({ hasText: '生活相談員' }).count() === 1 &&
          await page.locator('.dayservice-staffing-overview tbody a[href="#staffing-role-manager"]').count() === 1 ? 'PASS' : 'FAIL',
      });
      for (const role of ['nurse', 'care-worker']) {
        const item = page.locator(`#staffing-role-${role}`);
        const checks = item.locator('.dayservice-reader-questions li');
        const qaSearch = item.locator('.dayservice-qa-search-link a');
        const href = await qaSearch.getAttribute('href');
        report.interactions.push({
          flow: `${width}px ${role} → three practical questions and related national Q&A search`,
          status: await checks.count() === 3 && Boolean(href?.startsWith('/qa?reader=1&service=16&q=')) &&
            (await item.locator('.dayservice-reader-questions > .dayservice-reader-question-note').innerText()).includes('国の基準') ? 'PASS' : 'FAIL',
        });
      }
      await page.goto(origin + '/handbook/dayservice/additions');
      report.interactions.push({
        flow: `${width}px additions → two priority topics linked before full source text`,
        status: await page.locator('.dayservice-priority-additions a[href$="#fee-note-13"]').count() === 1 &&
          await page.locator('.dayservice-priority-additions a[href$="#fee-note-6"]').count() === 1 ? 'PASS' : 'FAIL',
      });
      const training = page.locator('#fee-note-13');
      const trainingSummary = await training.locator('.dayservice-reader-overview').innerText();
      const trainingDiagram = await training.locator('.dayservice-timing-example').innerText();
      report.interactions.push({
        flow: `${width}px training → summary, exceptions and overlapping hours diagram`,
        status: trainingSummary.includes('外部機関') && trainingDiagram.includes('10〜12時') &&
          trainingDiagram.includes('（Ⅰ）ロ') &&
          await training.locator('.dayservice-reader-questions li').count() === 3 ? 'PASS' : 'FAIL',
      });
      const trainingQa = training.locator('.dayservice-official-qa-links li a');
      const trainingLinks = await trainingQa.evaluateAll(nodes => nodes.map(node => node.getAttribute('href')));
      const qaPages = [34, 34, 35];
      report.interactions.push({
        flow: `${width}px training addition → Q&A 55–57 official original pages`,
        status: await training.locator('.dayservice-reader-questions li').count() === 3 &&
          trainingLinks.length === 3 &&
          trainingLinks.every((href, i) => href?.startsWith('https://www.mhlw.go.jp/content/12300000/001230308.pdf#page=') &&
            href.endsWith(`#page=${qaPages[i]}`)) &&
          (await training.locator('.dayservice-official-qa-links > p').innerText()).includes('未確認') ? 'PASS' : 'FAIL',
      });
      const treatment = page.locator('#fee-treatment-improvement');
      const amendment = treatment.locator('.dayservice-regulatory-update');
      const amendmentText = await amendment.innerText();
      report.interactions.push({
        flow: `${width}px treatment improvement → 2026 amendment warning before historical fee source`,
        status: amendmentText.includes('令和8年厚生労働省告示第87号') &&
          amendmentText.includes('請求・届出') &&
          amendmentText.includes('4月・5月と6月以降') &&
          await amendment.locator('a[href="https://www.mhlw.go.jp/content/12404000/001675895.pdf#page=7"]').count() === 1 &&
          await amendment.locator('a[href="https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=3"]').count() === 1 &&
          await amendment.locator('a[href="https://www.mhlw.go.jp/content/12404000/001675724.pdf#page=18"]').count() === 1 &&
          await amendment.locator('a[href="https://www.mhlw.go.jp/content/12404000/001675711.pdf"]').count() === 1 &&
          await amendment.locator('a[href="https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00073.html"]').count() === 1 ? 'PASS' : 'FAIL',
      });
      const extension = page.locator('#fee-note-6');
      const extensionText = await extension.innerText();
      report.interactions.push({
        flow: `${width}px extension → same-day overnight warning and 2015 questions`,
        status: extensionText.includes('宿泊サービス') &&
          extensionText.includes('問59') && extensionText.includes('問56') &&
          extensionText.includes('9時間30分') &&
          await extension.locator('.dayservice-official-qa-links li').count() === 5 &&
          extensionText.includes('Q&A Vol.4・問5') ? 'PASS' : 'FAIL',
      });
      report.interactions.push({
        flow: `${width}px extension addition → original fee and Q&A search`,
        status: await extension.locator('.dayservice-reader-questions li').count() === 3 &&
          (await extension.locator('.dayservice-reader-questions').innerText()).includes('8時間以上9時間未満') &&
          (await extension.locator('.dayservice-qa-search-link a').getAttribute('href'))?.startsWith('/qa?reader=1&service=16&q=') ? 'PASS' : 'FAIL',
      });
      await page.locator('#additions-topic-navigation a[href="#fee-note-13"]').click();
      await page.screenshot({ path: path.join(output, `dayservice-training-${width}.png`) });
      for (const suffix of ['criteria', 'qa']) {
        const targetId = `fee-note-13-${suffix}`;
        await training.locator(`.dayservice-source-navigation a[href="#${targetId}"]`).click();
        await page.waitForFunction(id => {
          const target = document.getElementById(id);
          const top = target?.getBoundingClientRect().top;
          return top !== undefined && top >= -2 && top < innerHeight / 2;
        }, targetId, { timeout: 5000 });
        report.interactions.push({ flow: `${width}px addition → ${suffix} on screen`, status: 'PASS' });
        if (suffix === 'criteria' && width === 390) await page.screenshot({ path: path.join(output, 'dayservice-training-criteria-390.png') });
      }
      await page.goto(origin + '/qa?reader=1&service=16&q=看護職員');
      const qaReaderText = await page.locator('main').innerText();
      report.interactions.push({
        flow: `${width}px related Q&A search → reader-friendly page`,
        status: (await page.locator('h1').innerText()).includes('関連Q&A') &&
          !qaReaderText.includes('現在の収載範囲') &&
          !qaReaderText.includes('「収載」と「現行性確認」') &&
          !(await page.locator('main').innerText()).includes('2019年以降の分類') &&
          await page.locator('.qa-list .qa-row').count() > 0 ? 'PASS' : 'FAIL',
      });
      const qaDetailLink = page.locator('.qa-list .qa-row h2 a').first();
      const qaDetailHref = await qaDetailLink.getAttribute('href');
      if (qaDetailHref?.includes('?reader=1')) {
        await qaDetailLink.click();
        await page.waitForURL(url => url.pathname.startsWith('/qa/') && url.searchParams.get('reader') === '1', { timeout: 15000 });
        await page.locator('main a[href*="mhlw.go.jp"]').first().waitFor({ state: 'attached', timeout: 15000 });
        const qaDetailText = await page.locator('main').innerText();
        report.interactions.push({
          flow: `${width}px related Q&A → individual answer and government source without editor data`,
          status: qaDetailText.includes('質問') && qaDetailText.includes('回答') &&
            !qaDetailText.includes('2019年以降のサービス分類') &&
            !qaDetailText.includes('出典・参照先の確認日') &&
            await page.locator('main a[href*="mhlw.go.jp"]').count() > 0 &&
            await page.locator('main .qa-corpus-meta').count() === 0 ? 'PASS' : 'FAIL',
        });
      } else {
        report.interactions.push({ flow: `${width}px reader Q&A individual detail link`, status: 'FAIL' });
      }
      await page.goto(origin + '/handbook/dayservice/remuneration#basic-fee');
      const tableRegion = page.locator('.dayservice-table-scroll').first();
      await tableRegion.evaluate(element => { element.scrollLeft = element.scrollWidth - element.clientWidth; });
      const geometry = await tableRegion.evaluate(element => {
        const region = element.getBoundingClientRect();
        const row = element.querySelector('tbody tr');
        const label = row.querySelector('th').getBoundingClientRect();
        const last = row.querySelector('td:last-child').getBoundingClientRect();
        const caption = element.querySelector('caption span').getBoundingClientRect();
        const previousHeading = element.querySelector('thead th:nth-last-child(2)').getBoundingClientRect();
        return { moved: element.scrollLeft > 0, labelVisible: label.left >= region.left - 2 && label.right < region.right,
          lastValueVisible: last.left >= label.right && last.right <= region.right + 2,
          modelTitleVisible: caption.left >= region.left - 2 && caption.right <= region.right + 2,
          careLevelHeadingsVisible: previousHeading.left >= label.right - 2 && previousHeading.right <= region.right + 2 };
      });
      report.interactions.push({ flow: `${width}px fee table → horizontal scroll keeps time and last care level visible`, status: Object.values(geometry).every(Boolean) ? 'PASS' : 'FAIL', geometry });
      await page.screenshot({ path: path.join(output, `dayservice-fee-scroll-${width}.png`) });
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(origin + '/services/dayservice');
    await page.locator('.handbook-staffing-entry a').click();
    await page.locator('#staffing .handbook-role-navigation a[href="#staffing-role-nurse"]').click();
    await page.screenshot({ path: path.join(output, 'dayservice-nurse-390.png') });
    const nurseQa = page.locator('#staffing-role-nurse-qa');
    const nurseContractQa = nurseQa.locator('[data-qa-id="qa.mhlw.d9a7f5b49c1ba8a9326e"]');
    const question = await nurseContractQa.locator('.dayservice-qa-question').innerText();
    const answer = await nurseContractQa.locator('.dayservice-qa-answer').innerText();
    report.interactions.push({ flow: 'service → nurse → inline national question and answer', status: question.includes('どの程度の従事時間') && answer.includes('利用者全員') ? 'PASS' : 'FAIL' });
    await page.locator('#staffing-role-nurse .handbook-role-return a').click();
    await page.goto(origin + '/handbook/dayservice/national-qa');
    await page.locator('a[href="/handbook/dayservice/staffing#staffing-role-nurse-qa-qa.mhlw.d9a7f5b49c1ba8a9326e"]').click();
    await page.waitForURL('**/handbook/dayservice/staffing#staffing-role-nurse-qa-qa.mhlw.d9a7f5b49c1ba8a9326e', { timeout: 15000 });
    // The target must be on screen, not merely present in the DOM with a changed URL.
    const qaTargetVisible = () => {
      const target = document.getElementById('staffing-role-nurse-qa-qa.mhlw.d9a7f5b49c1ba8a9326e');
      const top = target?.getBoundingClientRect().top;
      return top !== undefined && top >= -2 && top < innerHeight / 2;
    };
    await page.waitForFunction(qaTargetVisible, null, { timeout: 5000 });
    report.interactions.push({ flow: 'national Q&A index → question under its staffing topic', status: (await page.locator('[data-qa-id="qa.mhlw.d9a7f5b49c1ba8a9326e"] .dayservice-qa-answer').innerText()).includes('契約') ? 'PASS' : 'FAIL' });
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.waitForFunction(qaTargetVisible, null, { timeout: 5000 });
    report.interactions.push({ flow: 'reloading a Q&A fragment keeps its question on screen', status: 'PASS' });
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
