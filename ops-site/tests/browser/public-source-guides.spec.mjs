import { test, expect } from '@playwright/test';

// These tests cover public information navigation only, not clinical accuracy.
// No care records, drug names, incident descriptions, or patient data are entered.
const guidePath = '/guides/medication-incident-sources';
const fallPath = '/guides/fall-prevention-sources';
const publicUrl = 'https://ops-site-pi.vercel.app';


test('legacy medication guide remains unchanged with five existing sources', async ({ page }) => {
  const response = await page.goto(guidePath);
  expect(response?.status()).toBe(200);
  await expect(page.locator('article h1')).toHaveCount(1);
  await expect(page.getByRole('heading', { name: /事故の疑いがあるときは/ })).toBeVisible();
  await expect(page.locator('#sources .sourceRow')).toHaveCount(5);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', publicUrl + guidePath);
  await expect(page.locator('meta[property="og:url"]')).toHaveAttribute('content', publicUrl + guidePath);
  await expect(page.locator('.sourceGuidePriority, .sourceGuideContents')).toHaveCount(0);
  await expect(page.locator('a[href="/guides/fall-prevention-sources"]')).toHaveCount(0);
  await expect(page.locator('article input, article textarea, article select, article button')).toHaveCount(0);
  await expect(page.locator('a[href="/tools/medication-safety-preview"]')).toHaveCount(0);
});

test('legacy medication guide retains its current official reference links', async ({ page }) => {
  const home = await page.goto('/');
  expect(home?.status()).toBe(200);
  await expect(page.locator('a[href="/guides/medication-incident-sources"]')).toBeVisible();
  await page.goto(guidePath);
  const urls = [
    'https://www.mhlw.go.jp/content/001591418.pdf',
    'https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf',
    'https://www.mhlw.go.jp/content/001574219.pdf',
    'https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html',
    'https://laws.e-gov.go.jp/law/140AC0000000045',
  ];
  for (const url of urls) {
    await expect(page.locator('#sources a.sourceRow[href="' + url + '"]')).toHaveCount(1);
  }
});

test('sitemap, robots and the held interactive preview remain separate', async ({ request }) => {
  const sitemap = await request.get('/sitemap.xml');
  expect(sitemap.status()).toBe(200);
  const xml = await sitemap.text();
  expect(xml).toContain(`${publicUrl}${guidePath}`);
  expect(xml).toContain(`${publicUrl}${fallPath}`);
  expect(xml).not.toContain('/tools/medication-safety-preview');

  const robots = await request.get('/robots.txt');
  expect(robots.status()).toBe(200);
  expect(await robots.text()).toContain(`${publicUrl}/sitemap.xml`);

  const hidden = await request.get('/tools/medication-safety-preview');
  expect(hidden.status()).toBe(404);
});


test('fall source guide is static, directly cited, and separate from unpublished prototype', async ({ page }) => {
  const home = await page.goto('/');
  expect(home?.status()).toBe(200);
  await expect(page.locator(`a[href="${fallPath}"]`)).toBeVisible();
  const response = await page.goto(fallPath);
  expect(response?.status()).toBe(200);
  await expect(page.locator('article h1')).toHaveCount(1);
  await expect(page.locator('.issueHero .sourceGuidePriority')).toContainText('事故が現に起きている場合');
  await expect(page.getByRole('heading', { name: '原文を読む' })).toHaveCount(1);
  await expect(page.locator('#sources .sourceRow')).toHaveCount(2);
  await expect(page.locator('section[aria-labelledby="factors"] a[href$="#page=33"]')).toHaveCount(1);
  await expect(page.locator('section[aria-labelledby="dignity"] a[href$="#page=33"]')).toHaveCount(1);
  await expect(page.locator('section[aria-labelledby="bed"] a[href$="#page=35"]')).toHaveCount(1);
  await expect(page.locator('section[aria-labelledby="report"] a[href$="#page=3"]')).toHaveCount(1);
  await expect(page.locator('section[aria-labelledby="report"] a[href$="#page=4"]')).toHaveCount(1);
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', `${publicUrl}${fallPath}`);
  await expect(page.locator('meta[property="og:url"]')).toHaveAttribute('content', `${publicUrl}${fallPath}`);
  await expect(page.locator('article input, article textarea, article select, article button')).toHaveCount(0);
  await expect(page.locator('a[href="/tools/medication-safety-preview"]')).toHaveCount(0);
  for (const citation of await page.locator('article .sourceGuideCitation').all()) {
    const original = citation.locator('a[target="_blank"]');
    await expect(original).toHaveAttribute('rel', /noreferrer/);
    const direct = await original.getAttribute('href');
    expect(direct).toMatch(/^https:\/\/www\.mhlw\.go\.jp\/content\/[0-9]+\.pdf#page=[0-9]+$/);
  }
});

test('fall page 390px, keyboard, CSS 200% proxy, reduced motion and print URLs', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(fallPath);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)).toBe(false);
  const first = page.getByRole('navigation', { name: 'この記事の目次' }).getByRole('link').first();
  await first.focus();
  await expect(first).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#factors$/);
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
  expect(await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1)).toBe(false);
  await page.evaluate(() => { document.documentElement.style.zoom = '1'; });
  await page.emulateMedia({ media: 'print' });
  expect(await page.locator('.sourceGuideContents').evaluate(el => getComputedStyle(el).display)).toBe('none');
  const source = page.locator('#sources .sourceRow').first();
  const printContent = await source.evaluate(el => getComputedStyle(el, '::after').content);
  const href = await source.getAttribute('href');
  expect(printContent.includes('attr(href)') || printContent.includes(href)).toBe(true);
});
