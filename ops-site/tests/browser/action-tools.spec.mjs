import { test, expect } from '@playwright/test';

// All test values are fictional task categories and aggregate times; never use care records.
const tools = [
  ['/tools/information-inventory', '/issues/information-search'],
  ['/tools/documentation-review', '/issues/documentation'],
  ['/tools/training-handover-inventory', '/issues/training-handover'],
  ['/tools/communication-review', '/issues/communication-collaboration'],
  ['/tools/work-time-review', '/issues/productivity-utilization'],
];

async function checkFollowThrough(page, issue) {
  await expect(page.locator(`header.siteHeader a[href="${issue}"]`)).toBeVisible();
  const links = page.locator('.issueFollowThroughLinks');
  await expect(links.locator(`a[href="${issue}#evidence"]`)).toBeVisible();
  await expect(links.locator('a[href^="https://kaigo-rules.vercel.app/"]')).toBeVisible();
  await expect(links.locator('a[href^="https://github.com/"]')).toBeVisible();
}

async function checkPrint(page) {
  // Do not open OS print UI or write a PDF during CI.
  await page.evaluate(() => {
    window.__browserTestPrintCount = 0;
    window.print = () => { window.__browserTestPrintCount += 1; };
  });
  await page.getByRole('button', { name: '印刷・PDF保存' }).click();
  await expect.poll(() => page.evaluate(() => window.__browserTestPrintCount)).toBe(1);
}

async function confirmNext(page, accept) {
  page.once('dialog', async dialog => {
    expect(dialog.type()).toBe('confirm');
    if (accept) await dialog.accept();
    else await dialog.dismiss();
  });
}

test('all five action tools expose their issue, evidence, Rules, and feedback routes', async ({ page }) => {
  for (const [tool, issue] of tools) {
    const response = await page.goto(tool);
    expect(response?.status()).toBe(200);
    await expect(page.getByRole('main')).toBeVisible();
    await checkFollowThrough(page, issue);
    await expect(page.getByRole('button', { name: '印刷・PDF保存' })).toBeVisible();
  }
});

test('information inventory: entered values, add/remove, print and confirmed reset', async ({ page }) => {
  await page.goto('/tools/information-inventory');
  const scope = page.getByRole('textbox', { name: '今回棚卸しする範囲' });
  await scope.fill('架空の業務手順の所在');
  const first = page.locator('.actionRow').first();
  await first.getByRole('textbox', { name: 'よく探す情報' }).fill('架空の業務マニュアル');
  await first.getByRole('textbox', { name: '現在の正本' }).fill('承認済み手順一覧');
  await expect(scope).toHaveValue('架空の業務手順の所在');
  await expect(page.locator('.actionToolPrint')).toContainText('架空の業務マニュアル');
  await page.getByRole('button', { name: '行を追加' }).click();
  await expect(page.locator('.actionRow')).toHaveCount(4);
  await page.locator('.actionRow').last().getByRole('button', { name: 'この行を削除' }).click();
  await expect(page.locator('.actionRow')).toHaveCount(3);
  await checkPrint(page);
  await confirmNext(page, false);
  await page.getByRole('button', { name: '入力を消去' }).click();
  await expect(scope).toHaveValue('架空の業務手順の所在');
  await confirmNext(page, true);
  await page.getByRole('button', { name: '入力を消去' }).click();
  await expect(scope).toBeEmpty();
  await expect(first.getByRole('textbox', { name: 'よく探す情報' })).toBeEmpty();
  await expect(page.locator('.actionRow')).toHaveCount(3);
});

test('handover inventory: synthetic fields and select values persist until reset', async ({ page }) => {
  await page.goto('/tools/training-handover-inventory');
  const first = page.locator('.actionRow').first();
  await page.getByRole('textbox', { name: '今回棚卸しする職種・場面' }).fill('架空の新人研修');
  await first.getByRole('textbox', { name: '新任者が最初に必要な情報' }).fill('架空の引き継ぎ項目');
  await first.getByRole('combobox', { name: '知識の種類' }).selectOption('文書化できる知識');
  await first.getByRole('combobox', { name: '正本の状態' }).selectOption('候補はあるが要確認');
  await expect(page.locator('.actionToolPrint')).toContainText('架空の引き継ぎ項目');
  await expect(first.getByRole('combobox', { name: '正本の状態' })).toHaveValue('候補はあるが要確認');
  await checkPrint(page);
  await confirmNext(page, true);
  await page.getByRole('button', { name: '入力を消去' }).click();
  await expect(first.getByRole('textbox', { name: '新任者が最初に必要な情報' })).toBeEmpty();
  await expect(first.getByRole('combobox', { name: '知識の種類' })).toHaveValue('');
});

test('communication review: guarded synthetic example, escalation check, print and reset', async ({ page }) => {
  await page.goto('/tools/communication-review');
  const scope = page.getByRole('textbox', { name: '棚卸しする範囲' });
  await scope.fill('架空の窓口業務');
  await confirmNext(page, false);
  await page.getByRole('button', { name: '架空例を読み込む' }).click();
  await expect(scope).toHaveValue('架空の窓口業務');
  await confirmNext(page, true);
  await page.getByRole('button', { name: '架空例を読み込む' }).click();
  await expect(page.getByRole('status')).toContainText('架空の記入例');
  await expect(scope).toHaveValue(/架空例/);
  const first = page.locator('.worksheetPhases fieldset').first();
  await first.getByRole('textbox', { name: '問い合わせの種類' }).fill('架空の受付区分');
  await first.getByRole('combobox', { name: '定型様式にできるか' }).selectOption('一部できる');
  await expect(first.getByRole('combobox', { name: '定型様式にできるか' })).toHaveValue('一部できる');
  const humanRoute = page.getByRole('checkbox', { name: /すぐ人へつなぐ経路/ });
  await humanRoute.check();
  await expect(page.locator('.worksheetResult .worksheetNotice')).toContainText('試行条件として');
  await checkPrint(page);
  await confirmNext(page, true);
  await page.getByRole('button', { name: '入力を消去' }).click();
  await expect(scope).toBeEmpty();
  await expect(humanRoute).not.toBeChecked();
  await expect(page.getByRole('status')).toHaveCount(0);
});

test('documentation review: example, before/after, invalid input, checks, print and reset', async ({ page }) => {
  await page.goto('/tools/documentation-review');
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await page.getByRole('button', { name: '架空例を読み込む' }).click();
  await expect(page.getByRole('status')).toContainText('実測結果や効果の実証ではありません');
  await expect(page.locator('.worksheetTotals')).toContainText('変更前の1件当たり');
  await expect(page.locator('.worksheetTotals')).toContainText('7.5分');
  const before = page.locator('.worksheetPhases fieldset').first();
  const count = before.locator('input[type="number"]').first();
  await count.fill('0');
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await expect(page.locator('.worksheetResult')).toContainText('0件は比較しません');
  await count.fill('20');
  const record = before.locator('input[type="number"]').nth(1);
  await record.fill('-1');
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await record.fill('60');
  await expect(page.locator('.worksheetTotals')).toBeVisible();
  await page.getByRole('checkbox', { name: /サービス・業務・1件の単位/ }).check();
  await page.getByRole('checkbox', { name: /記録漏れや品質/ }).check();
  await expect(page.locator('.worksheetResult .worksheetNotice')).toContainText('因果効果');
  await checkPrint(page);
  await confirmNext(page, true);
  await page.getByRole('button', { name: '入力を消去' }).click();
  await expect(count).toBeEmpty();
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await expect(page.getByRole('status')).toHaveCount(0);
});

test('work-time review: example, aggregate comparison, invalid input, quality and safety', async ({ page }) => {
  await page.goto('/tools/work-time-review');
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await page.getByRole('button', { name: '架空例を読み込む' }).click();
  await expect(page.getByRole('status')).toContainText('実測結果や改善効果ではありません');
  await expect(page.locator('.worksheetTotals')).toContainText('240分');
  const before = page.locator('.worksheetPhases fieldset').first();
  const directCare = before.locator('input[type="number"]').first();
  await directCare.fill('');
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await directCare.fill('-1');
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await directCare.fill('110');
  await expect(page.locator('.worksheetTotals')).toBeVisible();
  await page.getByRole('checkbox', { name: /個人評価・個人ランキングではなく/ }).check();
  await page.getByRole('checkbox', { name: /前後を比較できる条件/ }).check();
  await page.getByRole('checkbox', { name: /ケア・記録・手戻り/ }).check();
  await page.getByRole('checkbox', { name: /急変対応、相談、休憩/ }).check();
  await expect(page.locator('.worksheetResult .worksheetNotice')).toContainText('因果効果');
  await checkPrint(page);
  await confirmNext(page, true);
  await page.getByRole('button', { name: '入力を消去' }).click();
  await expect(directCare).toBeEmpty();
  await expect(page.locator('.worksheetTotals')).toHaveCount(0);
  await expect(page.getByRole('status')).toHaveCount(0);
});

test('mobile 390px: five tools remain operable without horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  for (const [route] of tools) {
    await page.goto(route);
    await expect(page.getByRole('button', { name: '印刷・PDF保存' })).toBeVisible();
    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > window.innerWidth + 1
    );
    expect(overflow, `${route} overflows 390px viewport`).toBe(false);
  }
});
