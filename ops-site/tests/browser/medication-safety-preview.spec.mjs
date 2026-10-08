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
    await expect(result).toContainText("対象外にできる範囲");
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
    await expect(page.locator(".medicationResult")).toContainText("指示変更");
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1);
    expect(overflow).toBe(false);
  });
});
