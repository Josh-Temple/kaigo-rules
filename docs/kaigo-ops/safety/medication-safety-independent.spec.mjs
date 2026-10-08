import { test, expect } from "@playwright/test";

// Independent D-only test suite. Synthetic enum values, no identities or incident data.
// Executed exclusively at localhost in GitHub Actions, against pinned C commit.
// No HAR, tracing, screenshots, recordings or PDF artifacts are uploaded.
const route = "/tools/medication-safety-preview";
const markerValues = ["record-handover", "not-applicable", "needs-review", "not-prepared"];
const stage = page => page.getByRole("combobox", { name: "点検する工程" });
const questions = page => page.locator(".medicationQuestions select");
const result = page => page.locator(".medicationResult");

test("D-R01/R02/R07/R08: incident safety boundary and no free-text intake", async ({page}) => {
  const response = await page.goto(route);
  expect(response?.status()).toBe(200);
  await expect(page.getByRole("heading", {name:"服薬業務の安全点検シート"})).toBeVisible();
  const text = await page.locator("main").innerText();
  expect(text).toMatch(/事故や服薬上の疑義/);
  expect(text).toMatch(/管理者/);
  expect(text).toMatch(/医療専門職/);
  expect(text).toMatch(/事故報告の要否・期限/);
  expect(await page.locator('input[type="text"], textarea, input[type="file"], [contenteditable="true"]').count()).toBe(0);
  expect(await page.locator("form").count()).toBe(0);
});

test("D-R03/R09: all-confirmed and all-not-applicable cannot certify safety", async ({page}) => {
  await page.goto(route);
  await stage(page).selectOption("preparation");
  const qs = questions(page);
  expect(await qs.count()).toBe(6);
  for (let i=0;i<6;i++) await qs.nth(i).selectOption("confirmed");
  await expect(result(page)).toContainText(/自己申告/);
  await expect(result(page)).toContainText(/保証しません/);
  for (let i=0;i<6;i++) await qs.nth(i).selectOption("not-applicable");
  await expect(result(page).locator("li")).toHaveCount(6);
  await expect(result(page)).toContainText(/担当権限を責任者/);
  await expect(result(page)).toContainText(/安全性、医療判断、制度適合/);
  await page.reload();
  await expect(stage(page)).toHaveValue("unselected");
  await expect(result(page)).toContainText(/工程が未選択/);
});

test("D-R04/R05/R06/R15: service, responsibility and dignity warnings remain visible", async ({page}) => {
  await page.goto(route);
  const text=await page.locator("main").innerText();
  expect(text).toMatch(/訪問・通所・居住系/);
  expect(text).toMatch(/職種の権限/);
  expect(text).toMatch(/本人の意思/);
  expect(text).toMatch(/職員の業務負担/);
  expect(text).not.toMatch(/事故ゼロ|安全を認証します|必ず二人で/);
});

test("D-P01/P02/P03/P04/P06/R11/R12: synthetic selections not leaked to network, URL, history, cookie or storage", async ({page}) => {
  const requests=[];
  page.on("request", r => requests.push({url:r.url(),method:r.method(),headers:r.headers(),postData:r.postData()}));
  await page.goto(route);
  await stage(page).selectOption("record-handover");
  const qs=questions(page);
  await qs.nth(0).selectOption("not-applicable");
  await qs.nth(1).selectOption("needs-review");
  await qs.nth(2).selectOption("not-prepared");
  await expect(result(page)).toContainText(/担当権限を責任者/);
  await page.waitForTimeout(500);
  const browser = await page.evaluate(async () => ({
    url:location.href,
    historyState:history.state,
    local:Object.entries(localStorage),
    session:Object.entries(sessionStorage),
    cookie:document.cookie,
    dbs: typeof indexedDB.databases==="function" ? (await indexedDB.databases()).map(db=>db.name) : "UNSUPPORTED",
  }));
  const observable=JSON.stringify({requests,browser});
  for(const value of markerValues) expect(observable).not.toContain(value);
  expect(new URL(browser.url).search).toBe("");
  expect(new URL(browser.url).hash).toBe("");
  expect(browser.dbs).not.toBe("UNSUPPORTED");
  expect(browser.dbs).toEqual([]);
  // Ordinary script delivery and pageviews are allowed; answer-bearing payloads are not.
});

test("D-P03/P04: browser back, revisit and reload do not persist selections", async ({page}) => {
  await page.goto(route);
  await stage(page).selectOption("instruction-update");
  await questions(page).first().selectOption("needs-review");
  await page.reload();
  await expect(stage(page)).toHaveValue("unselected");
  await expect(questions(page).first()).toHaveValue("unknown");
  await page.goto("/");
  await page.goBack();
  await page.goto(route);
  await expect(stage(page)).toHaveValue("unselected");
  const url=new URL(page.url());
  expect(url.search).toBe("");
  expect(url.hash).toBe("");
});

test("D-P05/R13: cancel, confirm reset and print-media content stay bounded", async ({page}) => {
  await page.goto(route);
  await stage(page).selectOption("instruction-update");
  page.once("dialog", d=>d.dismiss());
  await page.getByRole("button",{name:"選択内容を消去"}).click();
  await expect(stage(page)).toHaveValue("instruction-update");
  page.once("dialog", d=>d.accept());
  await page.getByRole("button",{name:"選択内容を消去"}).click();
  await expect(stage(page)).toHaveValue("unselected");
  await page.emulateMedia({media:"print"});
  await expect(page.locator(".medicationPrint")).toBeVisible();
  await expect(page.locator(".medicationPrint")).toContainText(/未検証の試作/);
  await expect(page.locator(".medicationPrint")).toContainText(/保証しません/);
  const pdf=await page.pdf();
  expect(pdf.subarray(0,4).toString()).toBe("%PDF");
});

test("D-P07: preview has no feedback prefill or form containing answers", async ({page}) => {
  await page.goto(route);
  const links=await page.locator("a").evaluateAll(nodes=>nodes.map(n=>n.href));
  expect(links.filter(link=>/feedback/i.test(link))).toEqual([]);
  expect(await page.locator("form, textarea").count()).toBe(0);
});

test("D-U01/R14: 390px mobile viewport contains accessible safety boundaries and controls", async ({page}) => {
  await page.setViewportSize({width:390,height:844});
  await page.goto(route);
  await expect(page.locator(".medicationBoundary").first()).toBeVisible();
  await stage(page).selectOption("record-handover");
  await expect(result(page)).toContainText(/記録・引き継ぎ/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);
  expect(overflow).toBe(false);
});

test("D-U01: CSS-simulated 200% zoom, distinct from native browser zoom", async ({page}) => {
  await page.setViewportSize({width:1280,height:900});
  await page.goto(route);
  await page.evaluate(()=>document.documentElement.style.zoom="200%");
  await stage(page).focus();
  await expect(stage(page)).toBeFocused();
  await stage(page).selectOption("preparation");
  await expect(result(page)).toContainText(/配薬準備の運用/);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1)).toBe(false);
});

test("D-U02/U03: labeled keyboard-operable controls and announced result", async ({page}) => {
  await page.goto(route);
  const select=stage(page);
  await select.focus();
  await expect(select).toBeFocused();
  await page.keyboard.press("ArrowDown");
  await page.keyboard.press("Tab");
  await expect(result(page)).toHaveAttribute("aria-live","polite");
  for (const input of await page.locator(".medicationQuestions select").all()) {
    expect(await input.evaluate(el=>Boolean(el.closest("label")))).toBe(true);
  }
});

test("D-U04: print summary keeps safety disclaimer", async ({page}) => {
  await page.goto(route);
  await stage(page).selectOption("record-handover");
  await questions(page).first().selectOption("needs-review");
  await page.emulateMedia({media:"print"});
  const summary=await page.locator(".medicationPrint").innerText();
  expect(summary).toContain("記録・引き継ぎ");
  expect(summary).toContain("確認・相談する事項");
  expect(summary).toContain("保証しません");
});

test("D-R10/U03: invalid forged select state must not yield a valid safety result", async ({page}) => {
  await page.goto(route);
  await page.evaluate(()=>{
    const node=document.querySelector(".medicationQuestions select");
    node.add(new Option("forged","FORGED_INVALID_STATE"));
    node.value="FORGED_INVALID_STATE";
    node.dispatchEvent(new Event("change",{bubbles:true}));
  });
  await expect(result(page)).toContainText(/入力の形式を確認できません|不正な選択値を安全な判断として処理しません/);
});

test("D-U06: existing public home remains reachable in the isolated local server", async ({page}) => {
  const resp=await page.goto("/");
  expect(resp?.status()).toBe(200);
  await expect(page.getByRole("main")).toBeVisible();
});


test("D-R09/R15/U03: all unknown and mixed statuses remain consultations, not a score", async ({page}) => {
  await page.goto(route);
  await expect(result(page)).toContainText(/点検する工程が未選択/);
  await expect(result(page).locator("li")).toHaveCount(7);
  await stage(page).selectOption("record-handover");
  const qs=questions(page);
  const mixed=["confirmed","needs-review","not-prepared","not-applicable","unknown","confirmed"];
  for(let i=0;i<mixed.length;i++) await qs.nth(i).selectOption(mixed[i]);
  await expect(result(page)).toContainText(/相談したい点/);
  await expect(result(page)).toContainText(/取り決めが見つからない/);
  await expect(result(page)).toContainText(/担当権限を責任者/);
  await expect(result(page)).toContainText(/正式な手順の所在/);
  const output=await result(page).innerText();
  expect(output).not.toMatch(/事故ゼロ|合格|安全が確認できました|法令適合済/);
  await page.getByRole("button",{name:"架空例を読み込む"}).click();
  await expect(page.getByRole("status")).toContainText(/架空の業務例/);
  await expect(result(page)).toContainText(/自己申告/);
});

test("D-P01/P05/U04: print uses only enum-driven labels and retains incident boundary", async ({page}) => {
  await page.goto(route);
  await stage(page).selectOption("record-handover");
  const qs=questions(page);
  await qs.nth(0).selectOption("needs-review");
  await qs.nth(1).selectOption("not-applicable");
  await page.emulateMedia({media:"print"});
  const printed=await page.locator(".medicationPrint").innerText();
  expect(printed).toContain("自己申告・未検証");
  expect(printed).toContain("事故・服薬上の疑義");
  expect(printed).toContain("再投与・事故報告要否は判定しません");
  expect(printed).toContain("確認・相談する事項");
  expect(printed).toContain("担当範囲では扱わない");
  expect(printed).not.toMatch(/安全を認証|事故ゼロ|個別の投薬を指示/);
});
