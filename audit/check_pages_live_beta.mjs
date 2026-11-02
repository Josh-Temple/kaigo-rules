import assert from "node:assert/strict";
import { chromium } from "playwright";

const base="https://josh-temple.github.io/kaigo-rules";
const browser=await chromium.launch({channel:"chrome",headless:true,args:["--no-sandbox"]});
const findings=[];
const page=await browser.newPage({viewport:{width:390,height:844}});
const errors=[];
page.on("pageerror",error=>errors.push(String(error).slice(0,160)));

async function navigate(path) {
 const response=await page.goto(base+path,{waitUntil:"domcontentloaded",timeout:60000});
 assert.equal(response?.status(),200,"HTTP for "+path);
 await page.locator("body aside[role=note]").first().waitFor({state:"visible",timeout:20000});
 const banner=await page.locator("body aside[role=note]").first().innerText();
 assert.ok(banner.includes("試験公開版")&&banner.includes("指定権者"),"beta caution missing: "+path);
 const robots=await page.locator('meta[name="robots"]').getAttribute("content");
 assert.ok(robots?.includes("noindex"),"noindex missing: "+path);
 findings.push({route:path,http:response.status(),banner:true,noindex:true});
}

try {
 await navigate("/index.html");
 await navigate("/services/dayservice/index.html");
 await navigate("/handbook/dayservice/staffing.html");
 const check=page.locator('input[type="checkbox"]').first();
 assert.ok(await check.count()>0,"handbook checklist missing");
 await check.check();
 assert.equal(await check.isChecked(),true);
 await page.evaluate(()=>{window.__printUsed=false;window.print=()=>{window.__printUsed=true;}});
 const print=page.locator("[data-handbook-print]").first();
 assert.ok(await print.count()>0,"print control missing");
 await print.click();
 assert.equal(await page.evaluate(()=>window.__printUsed),true);
 const pdf=await page.pdf({format:"A4",printBackground:true});
 assert.equal(pdf.subarray(0,5).toString(),"%PDF-");
 findings.push({interaction:"handbook-check-and-print",ok:true,pdfBytes:pdf.length});

 await navigate("/databases/search/index.html");
 await page.locator("#query").fill("看護職員");
 await page.locator('#search button[type="submit"], #search button').first().click();
 await page.waitForFunction(()=>document.querySelector("#status")?.textContent?.includes("件見つかりました"),null,{timeout:30000});
 assert.ok(await page.locator("#results article.result").count()>0,"DB results missing");
 findings.push({interaction:"database-search",ok:true,results:await page.locator("#results article.result").count()});

 await navigate("/databases/search/qa.html?reader=1&service=16&q="+encodeURIComponent("看護職員"));
 await page.waitForFunction(()=>document.querySelector("#qa-status")?.textContent?.includes("件見つかりました"),null,{timeout:30000});
 assert.ok(await page.locator("#qa-results article.result, #qa-results section.result").count()>0,"Q&A search results missing");
 const first=page.locator("#qa-results h2 a").first();
 const href=await first.getAttribute("href");
 assert.ok(href?.includes("qa-details/")&&!href.includes("vercel.app"),"QA did not stay local");
 await first.click();
 await page.locator("article.answer-page").first().waitFor({state:"visible",timeout:30000});
 assert.ok((await page.locator("article.answer-page").innerText()).length>100);
 findings.push({interaction:"qa-search-detail",ok:true});

 await navigate("/legislation/index.html");
 await page.waitForFunction(()=>document.querySelector("#legal-summary")?.textContent?.includes("件の収載資料"),null,{timeout:30000});
 await page.locator("#q").fill("人員");
 await page.locator('#legal-form button[type="submit"]').click();
 await page.waitForFunction(()=>document.querySelector("#legal-results a")!==null,null,{timeout:30000});
 const link=await page.locator("#legal-results a").first().getAttribute("href");
 assert.ok(link?.startsWith("./record/")&&link.endsWith(".html"),"Static legal detail missing");
 await page.locator("#legal-results a").first().click();
 await page.locator("article.handbook-page").first().waitFor({state:"visible",timeout:30000});
 findings.push({interaction:"legislation-query-detail",ok:true});

 assert.equal(errors.length,0,"Unhandled browser errors: "+JSON.stringify(errors));
 console.log("PUBLIC_BETA_LIVE_BROWSER:",JSON.stringify(findings));
} catch(error) {
 console.error("PUBLIC_BETA_LIVE_BROWSER_FAILED:",String(error));
 process.exitCode=1;
} finally {
 await browser.close();
}
