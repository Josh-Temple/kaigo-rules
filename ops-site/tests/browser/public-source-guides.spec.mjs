import { test, expect } from '@playwright/test';

// These tests cover public information navigation only, not clinical accuracy.
// No care records, drug names, incident descriptions, or patient data are entered.
const guidePath = '/guides/medication-incident-sources';
const fallPath = '/guides/fall-prevention-sources';
const publicUrl = 'https://ops-site-pi.vercel.app';

test('home links to the source-only guide; headings, metadata and sources are accessible', async ({ page }) => {
  const home = await page.goto('/');
  expect(home?.status()).toBe(200);
  await expect(page.locator(`a[href="${guidePath}"]`)).toBeVisible();

  const response = await page.goto(guidePath);
  expect(response?.status()).toBe(200);
  await expect(page.locator('article h1')).toHaveCount(1);
  await expect(page.getByRole('heading', { name: /事故の疑いがあるときは/ })).toBeVisible();
  await expect(page.getByText('実在の医療専門職による個別審査を受けたものではありません。')).toBeVisible();
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', `${publicUrl}${guidePath}`);
  await expect(page.locator('meta[property="og:url"]')).toHaveAttribute('content', `${publicUrl}${guidePath}`);

  const contents = page.getByRole('navigation', { name: 'この記事の目次' });
  await expect(contents.getByRole('link')).toHaveCount(6);
  await contents.getByRole('link', { name: '出典を確認する' }).click();
  await expect(page).toHaveURL(/#sources$/);
  await expect(page.getByRole('heading', { name: '原文を読む' })).toBeVisible();

  const citations = page.locator('article .sourceGuideCitation');
  expect(await citations.count()).toBeGreaterThan(0);
  for (const citation of await citations.all()) {
    const indexLink = citation.locator('a[href^="#source-"]');
    const href = await indexLink.getAttribute('href');
    expect(href).toMatch(/^#source-[a-z0-9]+$/);
    const source = page.locator(href);
    await expect(source).toHaveCount(1);
    // The citation must have a direct link to exactly the same official source
    // as the source list; no second-step navigation is required.
    const originalHref = await source.getAttribute('href');
    const directLink = citation.getByRole('link', { name: /原文を新しいタブで開く/ });
    // Direct links may point into the PDF via #page, while the list retains the document URL.
    const directHref = await directLink.getAttribute('href');
    expect(directHref === originalHref || directHref.startsWith(`${originalHref}#page=`)).toBe(true);
    await expect(directLink).toHaveAttribute('target', '_blank');
    await expect(directLink).toHaveAttribute('rel', /noreferrer/);
  }

  const sources = page.locator('#sources .sourceRow');
  await expect(sources).toHaveCount(5);
  for (const source of await sources.all()) {
    expect(await source.getAttribute('href')).toMatch(/^https:\/\//);
    await expect(source).toHaveAttribute('rel', /noreferrer/);
  }
  await expect(page.locator('article input, article textarea, article select, article button')).toHaveCount(0);
  await expect(page.locator('a[href="/tools/medication-safety-preview"]')).toHaveCount(0);
});

test('390px mobile layout and keyboard guide navigation do not lose access to sources', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(guidePath);
  await expect(page.locator('#sources .sourceRow')).toHaveCount(5);
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  expect(overflow, 'source guide must not overflow 390px').toBe(false);

  const firstEntry = page.getByRole('navigation', { name: 'この記事の目次' }).getByRole('link').first();
  await firstEntry.focus();
  await expect(firstEntry).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page).toHaveURL(/#first-step$/);
});

test('200% CSS zoom simulation preserves readable guide and sources', async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto(guidePath);
  // CSS zoom is an automated proxy; native Android/browser 200% zoom remains NOT_RUN.
  await page.evaluate(() => { document.documentElement.style.zoom = '2'; });
  await expect(page.locator('article h1')).toBeVisible();
  await expect(page.locator('#sources .sourceRow').first()).toBeVisible();
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);
  expect(overflow, '200% CSS zoom proxy must not overflow').toBe(false);
});

test('print layout retains source metadata and hides navigation without printing private inputs', async ({ page }) => {
  await page.goto(guidePath);
  await page.emulateMedia({ media: 'print' });
  await expect(page.locator('#sources .sourceRow')).toHaveCount(5);
  const headerDisplay = await page.locator('.sourceGuidePage .siteHeader').evaluate(el => getComputedStyle(el).display);
  const navDisplay = await page.locator('.sourceGuideContents').evaluate(el => getComputedStyle(el).display);
  expect(headerDisplay).toBe('none');
  expect(navDisplay).toBe('none');
  await expect(page.getByRole('heading', { name: '原文を読む' })).toHaveCount(1);
  // Printing must retain the document URL, not just an unlabeled outgoing icon.
  const printedSource = page.locator('#sources .sourceRow').first();
  const printedHref = await printedSource.getAttribute('href');
  expect(printedHref.startsWith('https://')).toBe(true);
  const generatedContent = await printedSource.evaluate((el) => getComputedStyle(el, '::after').content);
  expect(generatedContent.includes('attr(href)') || generatedContent.includes('https://')).toBe(true);
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

test('B-reviewed medication changes put immediate safety before contents and limit legal/reporting claims', async ({ page }) => {
  await page.goto(guidePath);
  const lead = page.locator('.issueHero .lead');
  const priority = page.locator('.issueHero .sourceGuidePriority');
  await expect(priority).toContainText('実際に事故が起きている場合');
  expect(await lead.evaluate(el => el.compareDocumentPosition(document.querySelector('.sourceGuidePriority')) & Node.DOCUMENT_POSITION_FOLLOWING)).toBeTruthy();
  await expect(page.getByRole('heading', { name: '服薬の間違いだけで、刑事責任が決まるわけではありません。' })).toBeVisible();
  await expect(page.locator('section[aria-labelledby="report"]')).toContainText('対象サービスには違いがあります');
  await expect(page.locator('section[aria-labelledby="report"]')).toContainText('様式の活用');
  await expect(page.locator('section[aria-labelledby="report"]')).toContainText('目安');
  await expect(page.locator('section[aria-labelledby="minor"]')).toContainText('高齢者向け住まいに関する研究報告書');
  await expect(page.locator('section[aria-labelledby="report"] a[href$="#page=4"]')).toHaveCount(1);
  await expect(page.locator('section[aria-labelledby="report"] a[href$="#page=2"]')).toHaveCount(1);
  await expect(page.locator('#minor a[href$="#page=57"]')).toHaveCount(1);
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
