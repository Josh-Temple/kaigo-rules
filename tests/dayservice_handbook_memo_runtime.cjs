// D-POST-E-01 runtime test of real inline application JS with a mocked DOM.
// This is not a Chromium or device test.
'use strict';
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=process.argv[2]||process.cwd();
const html=fs.readFileSync(path.join(root,'docs/prototypes/dayservice-handbook.html'),'utf8');
const match=html.match(/<script>\s*([\s\S]*?)\s*<\/script><\/body><\/html>/);
assert.ok(match,'inline script missing');
const js=match[1],key='kaigo-handbook-dayservice-local-draft-v1',pkey='kaigo-handbook-dayservice-source-progress-v1';
const cases=[],test=(label,ok)=>cases.push({label,pass:!!ok});
function node(tag='div'){return {tagName:tag,textContent:'',value:'',children:[],listeners:{},
append(...a){this.children.push(...a)},replaceChildren(...a){this.children=a},
addEventListener(n,f){this.listeners[n]=f},setAttribute(){},focus(){},click(){},remove(){}}}
function instance(backing=new Map(),fail={}){
 let exported=null;
 const ids=['handbook-sources-json','handbook-drafts-json','filter','candidate-filter','kind-filter','progress-filter','chapter-no','title','summary','links','candidate-count','candidates','memo','msg','menu','source-preview','draft-preview','export','clear'];
 const els=Object.fromEntries(ids.map(id=>[id,node()]));
 els['kind-filter'].value='all';els['progress-filter'].value='all';
 const document={getElementById:id=>els[id]||(els[id]=node()),createElement:node,body:{append(){}}};
 const localStorage={getItem:k=>{if(fail.read)throw Error('denied');return backing.get(k)??null},
  setItem:(k,v)=>{if(fail.write)throw Object.assign(Error('quota'),{name:'QuotaExceededError'});backing.set(k,v)}};
 class U extends URL {static createObjectURL(blob){if(fail.export)throw Error('export denied');exported=JSON.parse(blob.data);return 'blob:local'}static revokeObjectURL(){}}
 class B {constructor(parts){this.data=parts.join('')}}
 const app=new Function('document','localStorage','URL','Blob','setTimeout',js+'\nreturn {show,CHAPTERS,notes,progress};')(document,localStorage,U,B,f=>f());
 return {app,els,getExport:()=>exported};
}
const input=(x,s)=>{x.els.memo.value=s;x.els.memo.listeners.input()};
for(const n of [7999,8000,8001,12000]){
 const store=new Map(),s='字'.repeat(n),a=instance(store);
 input(a,s);
 test(n+' input',a.els.memo.value===s);
 test(n+' storage',JSON.parse(store.get(key)).applicability===s);
 a.app.show('staffing');a.app.show('applicability');
 test(n+' switch',a.els.memo.value===s);
 const b=instance(store);test(n+' reload',b.els.memo.value===s);
 b.els.export.listeners.click();test(n+' export',b.getExport().notes.applicability===s);
}
{
 const s='漢字\n日本語🙂\n',store=new Map(),a=instance(store);input(a,s);
 const b=instance(store);b.els.export.listeners.click();
 test('emoji utf16 two units','🙂'.length===2);
 test('unicode reload',b.els.memo.value===s);
 test('unicode export',b.getExport().notes.applicability===s);
}
{
 const a=instance(new Map(),{write:true});input(a,'unsaved');
 test('quota message',a.els.msg.textContent.includes('保存できません'));
 a.app.show('staffing');test('quota warning survives switch',a.els.msg.textContent.includes('保存できません'));
 a.els.export.listeners.click();test('quota export',a.getExport().notes.applicability==='unsaved');
}
{
 const a=instance(new Map(),{read:true});input(a,'new unsaved');
 test('read denied visible',a.els.msg.textContent.includes('読み込めません'));
 a.els.export.listeners.click();test('read denied export',a.getExport().notes.applicability==='new unsaved');
}
{
 const store=new Map([[key,'{invalid json']]),a=instance(store);
 test('corrupt warning',a.els.msg.textContent.includes('読み込めません'));
 input(a,'replacement');test('corrupt original retained',store.get(key)==='{invalid json');
 a.els.export.listeners.click();
 test('corrupt original included',a.getExport().unparsed_saved_data.notes==='{invalid json');
 test('new text included',a.getExport().notes.applicability==='replacement');
}
{
 const a=instance(new Map([[pkey,'[]']]));
 test('corrupt progress warning',a.els.msg.textContent.includes('読み込めません'));
 a.els.export.listeners.click();test('corrupt progress exported',a.getExport().unparsed_saved_data.progress==='[]');
}
{
 const a=instance(new Map(),{export:true});input(a,'keep');a.els.export.listeners.click();
 test('export failure visible',a.els.msg.textContent.includes('失敗'));
 test('export failure retains data',a.els.memo.value==='keep');
}
{
 const store=new Map(),a=instance(store);input(a,'A');a.app.show('staffing');input(a,'B');
 a.els.clear.listeners.click();const b=instance(store);
 test('other section retained',b.els.memo.value==='A');
 b.app.show('staffing');test('only current cleared',b.els.memo.value==='');
 b.els.export.listeners.click();
 test('not legal review',b.getExport().review_completed===false);
 test('27 existing progress entries',Object.keys(b.getExport().candidate_progress).length===27);
}
test('CSP retained',html.includes("connect-src 'none'"));
test('no innerHTML',!html.includes('innerHTML'));
test('no fetch',!js.includes('fetch('));
const summary={total:cases.length,passed:cases.filter(x=>x.pass).length,failed:cases.filter(x=>!x.pass).length};
process.stdout.write(JSON.stringify({summary,cases},null,2)+'\n');
if(summary.failed)process.exitCode=1;
