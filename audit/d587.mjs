import { chromium } from 'playwright';
import fs from 'node:fs/promises';
const out='evidence'; await fs.mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true});
const routes=['/handbook/dayservice/additions#fee-treatment-improvement','/fees/treatment-improvement','/fees','/search?q='+encodeURIComponent('処遇改善加算'),'/handbook/dayservice/staffing','/handbook/dayservice/remuneration','/qa?reader=1&service=16&q='+encodeURIComponent('個別機能訓練加算')];
const results=[];
for(const width of [360,390,1280]) {
 const page=await browser.newPage({viewport:{width,height:900},deviceScaleFactor:1});
 for(let i=0;i<routes.length;i++) {
  const errors=[]; page.on('pageerror', e=>errors.push(String(e)));
  try {
   const response=await page.goto('http://127.0.0.1:3000'+routes[i],{waitUntil:'networkidle',timeout:60000});
   const info=await page.evaluate(()=>({title:document.title,h1:[...document.querySelectorAll('h1')].map(e=>e.innerText),text:document.body.innerText,overflow:document.documentElement.scrollWidth>innerWidth,details:[...document.querySelectorAll('details')].map(d=>({summary:d.querySelector('summary')?.innerText,open:d.open})),links:[...document.querySelectorAll('a')].map(a=>({text:a.innerText,href:a.href})).filter(a=>a.text||a.href)}));
   const keyboard=[];
   for(const d of await page.locator('details:visible').all()) {
     const summary=d.locator('summary').first(); if(!await summary.count()) continue;
     const before=await d.evaluate(e=>e.open); await summary.focus(); const focused=await summary.evaluate(e=>document.activeElement===e); await page.keyboard.press('Enter'); const after=await d.evaluate(e=>e.open);
     keyboard.push({text:await summary.innerText(),before,after,focused}); if(before!==after) await page.keyboard.press('Enter'); if(keyboard.length>=3) break;
   }
   info.keyboard=keyboard;
   info.accessibility=await page.evaluate(()=>({missingNames:[...document.querySelectorAll('button,a,input')].filter(e=>!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby')&&!e.innerText?.trim()&&!e.getAttribute('title')&&!(e.labels?.length)).length,imagesWithoutAlt:document.querySelectorAll('img:not([alt])').length}));
   await page.screenshot({path:`${out}/${width}-${i}.png`,fullPage:true});
   if(width===390 && i<2) {
    await page.locator('details').evaluateAll(ds=>ds.forEach(d=>d.open=true));
    await page.pdf({path:`${out}/print-${i}.pdf`,format:'A4',printBackground:true});
   }
   results.push({width,route:routes[i],status:response?.status(),errors, ...info});
  } catch(e){results.push({width,route:routes[i],error:String(e)});}
 }
 await page.close();
}
await fs.writeFile(out+'/results.json',JSON.stringify(results,null,2));
await browser.close();
if(results.some(r=>r.error||r.status!==200)) process.exitCode=1;
