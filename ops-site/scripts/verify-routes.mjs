import assert from 'node:assert/strict';
import { issueRegistry } from '../app/issues/registry.ts';
import { actionToolRoutes } from '../lib/action-tools.ts';
import { issueFollowThrough, RULES_HOME_HREF } from '../lib/issue-follow-through.ts';
const base = process.argv[2] || 'http://localhost:3000';
const home = await fetch(`${base}/`);
assert.equal(home.status, 200, 'home route');
const homeText = await home.text();
assert.ok(homeText.includes('href="/guides/medication-incident-sources"'), 'medication source page reachable from homepage');
const medicationGuide = await fetch(`${base}/guides/medication-incident-sources`);
assert.equal(medicationGuide.status, 200, 'source-only medication guide route');
const medicationGuideHtml = await medicationGuide.text();
for (const text of [
  '事故の疑いがあるときは',
  '自己判断で済ませない',
  '自治体の取扱い',
  '刑事罰',
  '個別の医療判断',
  'このページを読み進めるために',
]) {
  assert.ok(medicationGuideHtml.includes(text), `medication guide: ${text}`);
}
for (const sourceUrl of [
  'https://www.mhlw.go.jp/content/001591418.pdf',
  'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf',
  'https://www.mhlw.go.jp/content/001574219.pdf',
  'https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html',
  'https://laws.e-gov.go.jp/law/140AC0000000045',
]) {
  assert.ok(medicationGuideHtml.includes(sourceUrl), `medication guide source: ${sourceUrl}`);
}
assert.ok(!medicationGuideHtml.includes('服薬業務の安全点検シートを開く'), 'unapproved interactive preview remains isolated');
console.log('PASS /guides/medication-incident-sources');

const fallGuidePath = '/guides/fall-prevention-sources';
assert.ok(homeText.includes(`href="${fallGuidePath}"`), 'fall guide must have a homepage entry');
const fallGuide = await fetch(`${base}${fallGuidePath}`);
assert.equal(fallGuide.status, 200, 'static fall source guide route');
const fallHtml = await fallGuide.text();
for (const text of [
  '転倒・転落の予防を、公的資料から考える',
  '事故が現に起きている場合',
  '身体拘束',
  '第1報',
  'このページはそれらを個別に判定しません',
  '原文を読む',
  'https://www.mhlw.go.jp/content/001591418.pdf#page=33',
  'https://www.mhlw.go.jp/content/001591418.pdf#page=35',
  'https://www.mhlw.go.jp/content/001574219.pdf#page=3',
  'https://www.mhlw.go.jp/content/001574219.pdf#page=4',
]) {
  assert.ok(fallHtml.includes(text), `fall guide: ${text}`);
}
for (const banned of ['<form', '<input', '<textarea', 'href="/tools/medication-safety-preview"']) {
  assert.ok(!fallHtml.includes(banned), `fall guide must not contain ${banned}`);
}
const heldPreview = await fetch(`${base}/tools/medication-safety-preview`);
assert.equal(heldPreview.status, 404, 'unapproved interactive medication preview stays 404');
const sitemapResponse = await fetch(`${base}/sitemap.xml`);
assert.equal(sitemapResponse.status, 200, 'sitemap');
const sitemapBody = await sitemapResponse.text();
assert.ok(sitemapBody.includes('/guides/medication-incident-sources'), 'sitemap medication');
assert.ok(sitemapBody.includes('/guides/fall-prevention-sources'), 'sitemap fall');
assert.ok(!sitemapBody.includes('/tools/medication-safety-preview'), 'sitemap held prototype');
const robotsResponse = await fetch(`${base}/robots.txt`);
assert.equal(robotsResponse.status, 200, 'robots');
console.log('PASS /guides/fall-prevention-sources and held preview 404 / sitemap / robots');


for (const issue of issueRegistry) {
  assert.ok(homeText.includes(`href="${issue.href}"`), `${issue.href}: homepage link`);
  const response = await fetch(`${base}${issue.href}`);
  assert.equal(response.status, 200, issue.href);
  const html = await response.text();
  assert.ok(html.includes('<h1>'), `${issue.href}: heading`);
  assert.ok(html.includes('id="evidence"'), `${issue.href}: evidence anchor`);
  assert.ok(html.includes('class="sourceRow"'), `${issue.href}: source links`);
  const followThrough = issueFollowThrough[issue.href];
  assert.ok(followThrough, `${issue.href}: follow-through config`);
  assert.ok(html.includes(`href="${followThrough.rulesHref}"`), `${issue.href}: contextual Rules link`);
  assert.ok(html.includes(`href="${RULES_HOME_HREF}"`), `${issue.href}: generic Rules link`);
  assert.ok(html.includes('GitHub Issuesでフィードバックする'), `${issue.href}: feedback link`);
  for (const text of ['何を試したか', 'どこで止まったか', '何が足りなかったか', '介護記録']) {
    assert.ok(html.includes(text), `${issue.href}: follow-through ${text}`);
  }
  console.log(`PASS ${issue.href}`);
}
for (const tool of actionToolRoutes) {
  const issueHtml = await (await fetch(`${base}${tool.issueHref}`)).text();
  assert.ok(issueHtml.includes(`href="${tool.href}"`), `${tool.issueHref}: action tool link`);

  const response = await fetch(`${base}${tool.href}`);
  assert.equal(response.status, 200, tool.href);
  const html = await response.text();
  assert.ok(html.includes(tool.title), `${tool.href}: title`);
  assert.ok(html.includes('個人名'), `${tool.href}: privacy boundary`);
  assert.ok(html.includes('送信・自動保存されません'), `${tool.href}: no persistence notice`);
  assert.ok(html.includes('改善効果'), `${tool.href}: non-effect guard`);
  assert.ok(html.includes(`href="${tool.evidenceHref}"`), `${tool.href}: evidence return`);
  for (const text of ['記入後の次の1手', '何を試したか', 'どこで止まったか', '何が足りなかったか', '公開・保存されます']) {
    assert.ok(html.includes(text), `${tool.href}: tool follow-through ${text}`);
  }
  assert.ok(html.includes('GitHub Issuesでフィードバックする'), `${tool.href}: tool feedback link`);
  console.log(`PASS ${tool.href}`);
}

const documentation = await (await fetch(`${base}/issues/documentation`)).text();
assert.ok(documentation.includes('href="/tools/documentation-review"'), 'worksheet reachable from documentation');
assert.ok(!documentation.includes('/questions/care-plan-content'), 'documentation does not hard-code a day-service-only Rules route');
const worksheet = await fetch(`${base}/tools/documentation-review`);
assert.equal(worksheet.status, 200, 'worksheet route');
const worksheetText = await worksheet.text();
for (const text of ['記録業務の', '確認・修正', '架空例を読み込む', '印刷・PDF保存', '送信・自動保存されません']) assert.ok(worksheetText.includes(text), `worksheet: ${text}`);
assert.ok(worksheetText.includes('href="https://kaigo-rules.vercel.app/databases/search"'), 'worksheet: generic Kaigo Rules search link');
assert.ok(!worksheetText.includes('/questions/care-plan-content'), 'worksheet: no day-service-only fixed Rules link');
assert.ok(worksheetText.includes('サービス種別に合う資料を探し'), 'worksheet: user selects the applicable service and sources');
assert.ok(worksheetText.includes('このシートでは制度適合を判定しません'), 'worksheet: no automated regulation verdict');
console.log('PASS /tools/documentation-review');
const actionTools = [
  {
    issue: '/issues/communication-collaboration',
    route: '/tools/communication-review',
    link: 'href="/tools/communication-review"',
    texts: ['問い合わせ・確認往復の', '送信・自動保存されません', '個人名', '例外時のエスカレーション', '急変・事故・専門判断'],
  },
  {
    issue: '/issues/productivity-utilization',
    route: '/tools/work-time-review',
    link: 'href="/tools/work-time-review"',
    texts: ['業務時間・待ち・間接業務の', '送信・自動保存されません', '職員個人の監視・ランキング', '直接ケア', '時間差だけで改善成功とは判定しません'],
  },
];

for (const tool of actionTools) {
  const issueHtml = await (await fetch(`${base}${tool.issue}`)).text();
  assert.ok(issueHtml.includes(tool.link), `${tool.issue}: action tool link`);
  const response = await fetch(`${base}${tool.route}`);
  assert.equal(response.status, 200, tool.route);
  const html = await response.text();
  for (const expected of tool.texts) {
    assert.ok(html.includes(expected), `${tool.route}: ${expected}`);
  }
  assert.ok(html.includes('https://kaigo-rules.vercel.app/'), `${tool.route}: rules link`);
  console.log(`PASS ${tool.route}`);
}
