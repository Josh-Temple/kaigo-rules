import { test, expect } from "@playwright/test";

const route = "/tools/medication-safety-preview";
const enabled = process.env.MEDICATION_SAFETY_PREVIEW === "enabled";

test("medication safety draft is unreachable when the flag is absent", async ({ page }) => {
  test.skip(enabled, "Explicitly enabled preview must use the guarded interaction tests.");
  const response = await page.goto(route);
  expect(response?.status()).toBe(404);
});

test.describe("explicitly enabled medication safety preview", () => {
  test.skip(!enabled, "Preview is disabled by default. Test by setting MEDICATION_SAFETY_PREVIEW=enabled on a preview-only server.");

  test("anonymous statuses, unknown and not-applicable, synthetic example, print and reset", async ({ page }) => {
    const requests = [];
    page.on("request", request => requests.push({
      url: request.url(),
      method: request.method(),
      payload: request.postData(),
    }));

    const response = await page.goto(route);
    expect(response?.status()).toBe(200);
    await expect(page.locator('meta[name="robots"]')).toHaveAttribute("content", /noindex/);
    await expect(page.getByRole("heading", { name: "服薬業務の安全点検シート" })).toBeVisible();
    const result = page.locator(".medicationResult");
    await expect(result).toContainText("工程が未選択");
    await expect(result).toContainText("事故確率");

    const stage = page.getByRole("combobox", { name: "点検する工程" });
    await stage.selectOption("record-handover");
    const procedure = page.getByRole("combobox", { name: /業務手順が文書化され/ });
    await procedure.selectOption("not-applicable");
    await expect(result).toContainText("担当権限を責任者・関係職種に確認");
    await expect(result).not.toContainText("安全が確認できました");

    page.once("dialog", async dialog => {
      expect(dialog.type()).toBe("confirm");
      await dialog.accept();
    });
    await page.getByRole("button", { name: "架空例を読み込む" }).click();
    await expect(page.getByRole("status")).toContainText("架空");
    await expect(result).toContainText("変更情報");
    await expect(result).not.toContainText("再投与");

    await page.evaluate(() => {
      window.__previewPrintCount = 0;
      window.print = () => { window.__previewPrintCount += 1; };
    });
    await page.getByRole("button", { name: "画面を印刷" }).click();
    await expect.poll(() => page.evaluate(() => window.__previewPrintCount)).toBe(1);
    await expect(page.locator(".medicationPrint")).toContainText("匿名");

    page.once("dialog", async dialog => dialog.accept());
    await page.getByRole("button", { name: "選択内容を消去" }).click();
    await expect(stage).toHaveValue("unselected");
    await expect(procedure).toHaveValue("unknown");

    const serialized = JSON.stringify(requests);
    for (const value of ["needs-review", "not-applicable", "not-prepared", "record-handover"]) {
      expect(serialized).not.toContain(value);
    }
    const storage = await page.evaluate(() => ({ local: Object.keys(localStorage), session: Object.keys(sessionStorage) }));
    expect(storage.local).toHaveLength(0);
    expect(storage.session).toHaveLength(0);
  });

  test("390px keyboard-operable checklist without horizontal overflow", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(route);
    const select = page.getByRole("combobox", { name: "点検する工程" });
    await select.focus();
    await expect(select).toBeFocused();
    await select.selectOption("instruction-update");
    await expect(page.locator(".medicationResult")).toContainText("変更情報");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
    expect(overflow).toBe(false);
  });
});


test("all-confirmed and all-not-applicable never produce a safety approval", async ({ page }) => {
  test.skip(!enabled, "Restricted local preview only.");
  await page.goto(route);
  await page.getByRole("combobox", { name: "点検する工程" }).selectOption("preparation");
  const fields = page.locator(".medicationQuestions select");
  expect(await fields.count()).toBe(6);
  for (let i = 0; i < 6; i += 1) await fields.nth(i).selectOption("confirmed");
  await expect(page.locator(".medicationResult")).toContainText("安全性、事故防止、実施権限、制度適合を保証しません");
  await expect(page.locator(".medicationResult")).toContainText("事故報告の要否を判定しません");
  await expect(page.locator(".medicationResult")).not.toContainText("安全が確認");
  for (let i = 0; i < 6; i += 1) await fields.nth(i).selectOption("not-applicable");
  await expect(page.locator(".medicationResult li")).toHaveCount(6);
  await expect(page.locator(".medicationResult")).toContainText("工程の有無と担当権限を責任者・関係職種に確認");
  await expect(page.locator(".medicationResult")).toContainText("安全性、医療判断、制度適合、実施権限を評価・認証するものではありません");
});

test("selections never enter network URLs, headers, request bodies, browser URL or storage", async ({ page }) => {
  test.skip(!enabled, "Restricted local preview only.");
  const requests = [];
  page.on("request", request => requests.push({
    url: request.url(),
    headers: request.headers(),
    postData: request.postData(),
  }));
  await page.goto(route);
  await page.getByRole("combobox", { name: "点検する工程" }).selectOption("record-handover");
  await page.getByRole("combobox", { name: /業務手順が文書化され/ }).selectOption("not-applicable");
  await page.getByRole("combobox", { name: /担当と引き継ぎ先/ }).selectOption("needs-review");
  await page.getByRole("combobox", { name: /作業中断や兼務/ }).selectOption("not-prepared");
  await expect(page.locator(".medicationResult")).toContainText("担当範囲では扱わないという自己申告");
  const clientState = await page.evaluate(async () => ({
    url: location.href,
    history: JSON.stringify(history.state),
    local: [...Array(localStorage.length)].map((_, i) => {
      const key = localStorage.key(i);
      return [key, localStorage.getItem(key)];
    }),
    session: [...Array(sessionStorage.length)].map((_, i) => {
      const key = sessionStorage.key(i);
      return [key, sessionStorage.getItem(key)];
    }),
    indexedDbNames: typeof indexedDB.databases === "function"
      ? (await indexedDB.databases()).map(db => db.name)
      : "NOT_SUPPORTED",
  }));
  await page.waitForTimeout(350); // Allow pageview requests to be observed; they are not answer transmissions.
  const markers = ["record-handover", "not-applicable", "needs-review", "not-prepared"];
  const transmitted = JSON.stringify(requests);
  const persisted = JSON.stringify(clientState);
  const cookies = JSON.stringify(await page.context().cookies());
  for (const marker of markers) {
    expect(transmitted, "request URL/header/body exposed a selected state: " + marker).not.toContain(marker);
    expect(persisted, "URL/history/storage exposed a selected state: " + marker).not.toContain(marker);
    expect(cookies, "Cookie exposed a selected state: " + marker).not.toContain(marker);
  }
  expect(new URL(clientState.url).search).toBe("");
  expect(new URL(clientState.url).hash).toBe("");
  expect(clientState.indexedDbNames).not.toBe("NOT_SUPPORTED");
  expect(clientState.indexedDbNames).toEqual([]);
  // Ordinary Next.js and Vercel pageview requests are allowed; only answer-bearing requests fail.
  await page.reload();
  await expect(page.getByRole("combobox", { name: "点検する工程" })).toHaveValue("unselected");
  await expect(page.getByRole("combobox", { name: /業務手順が文書化され/ })).toHaveValue("unknown");
  await page.goto("/");
  await page.goBack();
  // Next.js browser history may restore / or the preview route; neither may contain answers.
  const afterBack = new URL(page.url());
  expect(["/", route]).toContain(afterBack.pathname);
  expect(afterBack.search).toBe("");
  expect(afterBack.hash).toBe("");
  await page.goto(route);
  await expect(page.getByRole("combobox", { name: "点検する工程" })).toHaveValue("unselected");
  await expect(page.getByRole("combobox", { name: /業務手順が文書化され/ })).toHaveValue("unknown");
});

test("cancelled reset preserves choices, repeated reset clears them, print layout has explicit boundaries", async ({ page }) => {
  test.skip(!enabled, "Restricted local preview only.");
  await page.goto(route);
  const stage = page.getByRole("combobox", { name: "点検する工程" });
  await stage.selectOption("instruction-update");
  page.once("dialog", dialog => dialog.dismiss());
  await page.getByRole("button", { name: "選択内容を消去" }).click();
  await expect(stage).toHaveValue("instruction-update");
  page.once("dialog", dialog => dialog.accept());
  await page.getByRole("button", { name: "選択内容を消去" }).click();
  await expect(stage).toHaveValue("unselected");
  page.once("dialog", dialog => dialog.accept());
  await page.getByRole("button", { name: "選択内容を消去" }).click();
  await expect(stage).toHaveValue("unselected");
  await page.emulateMedia({ media: "print" });
  await expect(page.locator(".medicationPrint")).toBeVisible();
  await expect(page.locator(".medicationWorksheet > .section").first()).toBeHidden();
  await expect(page.locator(".medicationPrint")).toContainText("安全性、制度適合、実施権限、医療上の判断を保証しません");
  await expect(page.locator(".medicationPrint")).toContainText("事故報告の要否を判定しません");
  const pdf = await page.pdf();
  expect(pdf.subarray(0, 4).toString()).toBe("%PDF");
});

test("200 percent CSS zoom emulation keeps controls and safety boundaries operable", async ({ page }) => {
  test.skip(!enabled, "Restricted local preview only.");
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto(route);
  await page.evaluate(() => { document.documentElement.style.zoom = "200%"; });
  const stage = page.getByRole("combobox", { name: "点検する工程" });
  await stage.focus();
  await expect(stage).toBeFocused();
  await stage.selectOption("record-handover");
  await expect(page.locator(".medicationResult")).toContainText("記録・引き継ぎ");
  await expect(page.locator(".medicationBoundary").first()).toBeVisible();
  await expect(page.locator(".medicationResult")).toHaveAttribute("aria-live", "polite");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
  expect(overflow, "Horizontal overflow at CSS zoom 200%").toBe(false);
});
