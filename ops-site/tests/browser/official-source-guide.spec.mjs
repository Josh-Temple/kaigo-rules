import { test, expect } from "@playwright/test";

const route = "/guides/accident-medication-sources";
test("local-only review route has warning before navigational links and four distinct origins", async ({ page }) => {
  const response = await page.goto(route);
  expect(response?.status()).toBe(200);
  await expect(page.getByRole("heading", { level: 1 })).toContainText("公的資料を探す");
  const warning = page.getByRole("heading", { name: "事故が現に起きている場合" });
  await expect(warning).toBeVisible();
  expect(await page.evaluate(() => {
    const notice = document.getElementById("source-safety");
    const navigation = document.querySelector('nav[aria-label="このページのナビゲーション"]');
    return Boolean(notice && navigation && (notice.compareDocumentPosition(navigation) & Node.DOCUMENT_POSITION_FOLLOWING));
  })).toBe(true);
  const headings = await page.locator("h1, h2").allTextContents();
  expect(headings.indexOf("事故が現に起きている場合")).toBeLessThan(headings.indexOf("何を調べたいですか"));
  await expect(page.locator("a[href^='https://www.mhlw.go.jp/content/']")).toHaveCount(2);
  await expect(page.locator("a[href^='https://www.pmda.go.jp/']")).toHaveCount(1);
  await expect(page.locator("a[href^='https://www.mhlw.go.jp/file/']")).toHaveCount(1);
  await expect(page.getByText("原典URL：", { exact: false })).toHaveCount(4);
  await expect(page.locator("input, textarea, form")).toHaveCount(0);
  await expect(page.locator("a[href='/guides/medication-incident-sources'], a[href='/guides/fall-prevention-sources']")).toHaveCount(0);
  await expect(page.locator("a[href*='medication-safety']")).toHaveCount(0);
});

test("review page mobile width, keyboard focus and 200%-CSS proxy without horizontal overflow", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(route);
  await page.keyboard.press("Tab");
  await expect(page.locator("a.brand")).toBeFocused();
  await expect(page.getByRole("link", { name: "探したい資料" })).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  await page.evaluate(() => { document.body.style.zoom = "2"; });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1)).toBe(true);
  // CSS zoom is a proxy only, NOT the required Android Chrome native-200% review.
});

test("print rules retain warning and visible source URLs; metadata remains noindex", async ({ page }) => {
  await page.goto(route);
  const robots = await page.locator('meta[name="robots"]').getAttribute("content");
  expect(robots).toContain("noindex");
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute("href", /accident-medication-sources/);
  await expect(page.locator('meta[property="og:url"]')).toHaveAttribute("content", /accident-medication-sources/);
  await page.emulateMedia({ media: "print", reducedMotion: "reduce" });
  await expect(page.getByRole("heading", { name: "事故が現に起きている場合" })).toBeVisible();
  await expect(page.getByText("原典URL：", { exact: false }).first()).toBeVisible();
  // Headless print CSS is NOT a physical print or PDF-viewer deep-link acceptance.
});
