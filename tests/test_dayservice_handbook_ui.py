"""Checks for the *local-only* C UI prototype. Browser/device QA is separate."""
import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"docs/prototypes/dayservice-handbook.html"
HTML=FILE.read_text(encoding="utf-8")

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.scripts=[]
        self.external=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if "id" in a:
            if a["id"] in self.ids:
                raise AssertionError("duplicate element id "+a["id"])
            self.ids.add(a["id"])
        if tag=="script":
            self.scripts.append(a)
            if a.get("src"):self.external.append(a["src"])
        if tag in ("iframe","object","embed","form"):self.external.append(tag)

class DayserviceHandbookUITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=Elements()
        cls.p.feed(HTML)
        cls.js=re.search(r"<script>\s*(.*?)\s*</script>",HTML,re.S).group(1)
        cls.chapters=json.loads(re.search(r"const CHAPTERS=(\[.*?\]);\s*const BASE=",HTML,re.S).group(1))
        cls.items=json.loads(re.search(r"const CANDIDATES=(\[.*?\]);\s*const CANDIDATE_SOURCE_BLOBS=",HTML,re.S).group(1))
    def test_syntax(self):
        p=subprocess.run(["node","--check","--input-type=commonjs"],input=self.js,text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_unchanged_baseline(self):
        self.assertEqual(len(self.chapters),15)
        self.assertEqual(len(self.items),27)
        self.assertEqual(len({x["chapter_id"] for x in self.items}),11)
    def test_local_only_no_network(self):
        self.assertIn("connect-src 'none'",HTML)
        self.assertIn("default-src 'none'",HTML)
        self.assertIn("noindex,nofollow,noarchive",HTML)
        self.assertNotIn("fetch(",self.js)
        self.assertNotIn("XMLHttpRequest",self.js)
        self.assertNotIn("sendBeacon",self.js)
        self.assertEqual(self.p.external,[])
    def test_dom_text_only(self):
        self.assertNotIn("innerHTML",HTML)
        self.assertIn("textContent=value",self.js)
        self.assertIn("replaceChildren",self.js)
        self.assertEqual(len(self.p.scripts),3)
        self.assertEqual([x.get("type") for x in self.p.scripts[:2]],["application/json"]*2)
    def test_mobile_and_a11y(self):
        for text in ["max-width:760px","max-width:430px","max-width:360px",
                     ":focus-visible","skip-link","chapter-start","candidate-filter","kind-filter","progress-filter"]:
            self.assertIn(text,HTML)
        for element in ["menu","source-preview","draft-preview","candidate-filter","kind-filter","progress-filter"]:
            self.assertIn(element,self.p.ids)
    def test_progress_and_json_export(self):
        self.assertIn('const progressOptions=["未着手","原典を開いた","要再確認"]',self.js)
        self.assertIn('candidate_progress:Object.fromEntries',self.js)
        self.assertIn('review_completed:false',self.js)
        self.assertNotIn('review_completed:true',self.js)
        self.assertIn('JSON.stringify(data,null,2)',self.js)
    def test_fail_closed_embedded_data(self):
        self.assertIn('service_id!=="dayservice"',self.js)
        self.assertIn('value.base_pr_head',self.js)
        self.assertIn('rows.length>500',self.js)
        self.assertIn('statement.kind==="PROVISIONAL_EXPLANATION"&&!recordIds.length',self.js)
        self.assertIn('DRAFT_UNREVIEWED / HUMAN_REVIEW_NOT_DONE',self.js)
    def test_url_allowlist(self):
        self.assertIn('u.protocol!=="https:"',self.js)
        self.assertIn('u.username||u.password',self.js)
        self.assertIn('host==="elaws.e-gov.go.jp"',self.js)
        self.assertIn('a.rel="noopener noreferrer"',self.js)
    def test_all_notes_exported_not_promoted(self):
        self.assertIn('Object.fromEntries(CHAPTERS.map',self.js)
        self.assertIn('source:"local_handbook_trial"',self.js)
        self.assertNotIn('HUMAN_REVIEW_ACCEPTED',self.js)
    def test_original_candidate_ids_persist(self):
        self.assertIn('entry.chapter_id+"::"+entry.record_id',self.js)
        self.assertIn('progress[rowKey]=select.value',self.js)
    def test_clear_resets_memo_and_candidate_progress(self):
        self.assertIn('delete notes[current]',self.js)
        self.assertIn('delete progress[entry.chapter_id+"::"+entry.record_id]',self.js)
        self.assertIn('localStorage.setItem(progressKey,JSON.stringify(progress))',self.js)
    def test_untrusted_supplement_does_not_extend_known_record_ids(self):
        self.assertIn('const KNOWN_RECORD_IDS=new Set(CANDIDATES.map',self.js)
        self.assertNotIn('refs.add(rid)',self.js)
    def test_excerpts_collapsible(self):
        self.assertIn('document.createElement("details")',self.js)
        self.assertIn('document.createElement("summary")',self.js)
        self.assertIn('quote.textContent=entry.excerpt',self.js)



RUNTIME_HARNESS = '// Worker D independent UI runtime boundary regression harness, 2026-10-14.\n// Usage: node test_dayservice_boundaries.cjs /path/to/kaigo-rules\n// Requires the exact files recorded in D_independent_reacceptance_20261014.md.\nconst fs=require(\'node:fs\'),path=require(\'node:path\');\nlet exportDenied=false;\nclass MockURL extends URL { static createObjectURL(){if(exportDenied)throw Error(\'denied\');return \'blob:local-test\'} static revokeObjectURL(){} }\nconst root=process.argv[2]||process.cwd();\nconst loadFile=p=>fs.readFileSync(path.join(root,p),\'utf8\');\nconst html=loadFile(\'docs/prototypes/dayservice-handbook.html\');\nconst fixed=name=>JSON.parse(html.match(new RegExp(\'const \'+name+\'=(.*);\\\\n\'))[1]);\nconst fixture=(file,name)=>fs.existsSync(path.join(root,file))?JSON.parse(loadFile(file)):fixed(name);\nconst A=fixture(\'docs/prototypes/data/dayservice-handbook-source-candidates.v2.json\',\'PINNED_A\');\nconst B=fixture(\'docs/prototypes/data/dayservice-handbook-drafts.v1.json\',\'PINNED_B\');\nconst start=html.indexOf(\'\\n<script>\'),end=html.lastIndexOf(\'</script>\');\nif(start<0||end<start) throw new Error(\'inline script missing\');\nconst js=html.slice(start+9,end);\nfunction node(tag=\'div\'){return {tagName:tag,children:[],textContent:\'\',value:\'\',listeners:{},append(...a){this.children.push(...a)},replaceChildren(...a){this.children=a},addEventListener(k,v){this.listeners[k]=v},setAttribute(){},focus(){},click(){},remove(){}}}\nfunction instance(source,draft,storageDenied=false){\n const elements={};for(const id of [\'handbook-sources-json\',\'handbook-drafts-json\',\'filter\',\'candidate-filter\',\'kind-filter\',\'progress-filter\',\'chapter-no\',\'title\',\'summary\',\'links\',\'candidate-count\',\'candidates\',\'memo\',\'msg\',\'menu\',\'source-preview\',\'draft-preview\',\'export\',\'clear\'])elements[id]=node();\n elements[\'handbook-sources-json\'].textContent=source?JSON.stringify(source):\'\';\n elements[\'handbook-drafts-json\'].textContent=draft?JSON.stringify(draft):\'\';\n elements[\'kind-filter\'].value=\'all\';elements[\'progress-filter\'].value=\'all\';\n const backing=new Map();let exported=null;\n const document={getElementById:id=>elements[id],createElement:node,body:{append(){}}};\n const localStorage={getItem:k=>{if(storageDenied)throw Error(\'denied\');return backing.get(k)||null},setItem:(k,v)=>{if(storageDenied)throw Error(\'denied\');backing.set(k,v)}};\n const app=new Function(\'document\',\'localStorage\',\'URL\',\'Blob\',\'setTimeout\',js+\'\\nreturn {show,CHAPTERS,CANDIDATES,EXTRA_SOURCES,EXTRA_DRAFTS,notes,safeOfficialUrl};\')(document,localStorage,MockURL,function(parts){exported=JSON.parse(parts[0])},fn=>fn());\n return {app,elements,exported:()=>exported};\n}\nfunction texts(doc,id=\'staffing\'){\n const x=instance(null,doc);x.app.show(id);\n return x.elements[\'draft-preview\'].children.flatMap(n=>n.children).map(n=>n.textContent);\n}\nconst base=\'c6e61a44a8287f020d56e1c22d63ad2b74a08b89\';\nconst example=B.sections.find(s=>s.section_id===\'staffing\').draft_statements[0];\nconst other=B.sections.find(s=>s.section_id===\'applicability\').draft_statements[0].candidate_record_ids[0];\nconst payload=(s=example,over={})=>({service_id:\'dayservice\',base_pr_head:base,sections:[{section_id:\'staffing\',draft_statements:[s]}],...over});\nconst mod=(txt,extra={})=>({...example,statement_id:\'test-\'+txt,text:txt,...extra});\nconst has=(p,s=example.text)=>texts(p).includes(s);\nconst cases=[],check=(id,expected,actual)=>cases.push({case:id,expected,actual,pass:actual===expected});\nconst fresh=instance(A,B);\ncheck(\'P01 B canonical 15 sections accepted\',15,fresh.app.EXTRA_DRAFTS.length);\ncheck(\'P02 A canonical 11 candidates accepted\',11,fresh.app.EXTRA_SOURCES.length);\ncheck(\'N01 wrong service rejected\',false,has(payload(example,{service_id:\'dayrehab\'})));\ncheck(\'N02 wrong base HEAD rejected\',false,has(payload(example,{base_pr_head:\'f\'.repeat(40)})));\nconst missing=payload();delete missing.base_pr_head;check(\'N03 missing base HEAD rejected\',false,has(missing));\ncheck(\'N04 other-chapter record rejected\',false,has(payload(mod(\'cross-chapter\',{candidate_record_ids:[other]})),\'cross-chapter\'));\ncheck(\'N05 claimed human-reviewed text rejected\',false,has(payload(mod(\'人手レビュー済みの確定本文\',{review_state:\'HUMAN_REVIEW_ACCEPTED\'})),\'人手レビュー済みの確定本文\'));\ncheck(\'N06 claimed publication text rejected\',false,has(payload(mod(\'公開確定済み内容\'),{publication_state:\'PUBLICATION_READY\',human_review_state:\'ACCEPTED\'}),\'公開確定済み内容\'));\ncheck(\'N07 unsupported provisional explanation rejected\',false,has(payload(mod(\'no-evidence\',{candidate_record_ids:[]})),\'no-evidence\'));\ncheck(\'N08 fictional record rejected\',false,has(payload(mod(\'fictional\',{candidate_record_ids:[\'fiction.id\']})),\'fictional\'));\nconst xx=instance(null,payload(mod(\'<img src=x onerror=alert(1)>\')));xx.app.show(\'staffing\');\ncheck(\'N09 XSS no img element\',false,xx.elements[\'draft-preview\'].children.some(z=>z.children.some(q=>q.tagName===\'img\')));\ncheck(\'N10 illegal statement kind rejected\',false,has(payload(mod(\'bad-kind\',{kind:\'VERIFIED\'})),\'bad-kind\'));\nconst noReview=mod(\'no-review\');delete noReview.review_state;\ncheck(\'N11 missing review state rejected\',false,has(payload(noReview),\'no-review\'));\ncheck(\'N12 statement/section ID mismatch rejected\',false,has(payload(mod(\'section-mismatch\',{section_id:\'operations\'})),\'section-mismatch\'));\nlet large=payload();large.padding=\'x\'.repeat(500100);check(\'N13 large document rejected\',0,instance(null,large).app.EXTRA_DRAFTS.length);\ncheck(\'N14 malformed sections rejected\',0,instance(null,{service_id:\'dayservice\',sections:{}}).app.EXTRA_DRAFTS.length);\ncheck(\'N15 denied browser storage nonfatal\',15,instance(null,null,true).app.CHAPTERS.length);\nconst n=instance();n.elements.memo.value=\'note A\';n.elements.memo.listeners.input();n.app.show(\'staffing\');n.elements.memo.value=\'note B\';n.elements.memo.listeners.input();n.app.show(\'applicability\');\ncheck(\'N16 notes do not cross chapters\',\'note A\',n.elements.memo.value);\nn.elements.export.listeners.click();check(\'N17 export review false\',false,n.exported().review_completed);\ncheck(\'N18 fake hostname rejected\',null,fresh.app.safeOfficialUrl(\'https://mhlw.go.jp.bad.example/\'));\ncheck(\'N19 data URL rejected\',null,fresh.app.safeOfficialUrl(\'data:text/html,<script>\'));\ncheck(\'N20 unverifiable official URL rejected\',null,fresh.app.safeOfficialUrl(\'https://www.mhlw.go.jp/forged-not-real.html\'));\ncheck(\'N21 official e-Gov URL accepted\',true,fresh.app.safeOfficialUrl(\'https://laws.e-gov.go.jp/law/409AC0000000123\')!==null);\n\nconst clone=x=>JSON.parse(JSON.stringify(x));\nconst mutation=(name,doc,fn,source=false)=>{const x=clone(doc);fn(x);check(\'C-\'+name,0,instance(source?x:null,source?null:x).app[source?\'EXTRA_SOURCES\':\'EXTRA_DRAFTS\'].length);};\nmutation(\'A wrong hierarchy\',A,x=>{x.candidates=x.sections.flatMap(s=>s.candidates);delete x.sections},true);\nmutation(\'A missing sections\',A,x=>delete x.sections,true);\nmutation(\'A duplicate candidate\',A,x=>x.sections[0].candidates.push(clone(x.sections[0].candidates[0])),true);\nmutation(\'A unknown source\',A,x=>x.sections[0].candidates[0].source_id=\'fiction\',true);\nmutation(\'A mismatched section\',A,x=>x.sections[0].candidates[0].section_id=\'staffing\',true);\nmutation(\'A false service\',A,x=>x.service_id=\'dayrehab\',true);\nmutation(\'A invented record\',A,x=>x.sections[0].candidates[0].record_id=\'fake.record\',true);\nmutation(\'A missing blob\',A,x=>delete x.sections[0].candidates[0].repository_blob_sha,true);\nmutation(\'A forged blob\',A,x=>x.sections[0].candidates[0].repository_blob_sha=\'f\'.repeat(40),true);\nmutation(\'A invented version\',A,x=>x.sections[0].candidates[0].source_version=\'2099-current\',true);\nmutation(\'A invented locator\',A,x=>x.sections[0].candidates[0].source_locator=\'article.999\',true);\nmutation(\'A forged registered-host URL\',A,x=>x.sections[0].candidates[0].source_url=\'https://www.mhlw.go.jp/forged\',true);\nmutation(\'A historical promoted\',A,x=>x.sections[2].candidates[0].candidate_status=\'CURRENT\',true);\nmutation(\'A approval self-claim\',A,x=>x.human_review_status=\'ACCEPTED\',true);\nmutation(\'A publication self-claim\',A,x=>x.publication_status=\'PUBLICATION_READY\',true);\nmutation(\'A missing base\',A,x=>delete x.base_pr_head,true);\nmutation(\'A top-level verified\',A,x=>x.verified=true,true);\nmutation(\'B missing base\',B,x=>delete x.base_pr_head);\nmutation(\'B wrong base\',B,x=>x.base_pr_head=\'f\'.repeat(40));\nmutation(\'B chapter mismatch\',B,x=>x.sections[2].draft_statements[0].section_id=\'operations\');\nmutation(\'B other chapter reference\',B,x=>x.sections[2].draft_statements[0].candidate_record_ids=[other]);\nmutation(\'B missing review\',B,x=>delete x.sections[2].draft_statements[0].review_state);\nmutation(\'B invalid review\',B,x=>x.sections[2].draft_statements[0].review_state=\'REVIEWED\');\nmutation(\'B self-claimed human approval\',B,x=>x.human_review_state=\'HUMAN_REVIEW_ACCEPTED\');\nmutation(\'B self-claimed publication\',B,x=>x.publication_state=\'PUBLICATION_READY\');\nmutation(\'B ungrounded assertion\',B,x=>x.sections[2].draft_statements[0].text=\'人員基準は満たしており加算の算定を保証する\');\nmutation(\'B unknown reference\',B,x=>x.sections[2].draft_statements[0].candidate_record_ids=[\'fake\']);\nmutation(\'B duplicate reference\',B,x=>x.sections[2].draft_statements[0].candidate_record_ids.push(x.sections[2].draft_statements[0].candidate_record_ids[0]));\nmutation(\'B duplicate statement\',B,x=>x.sections[2].draft_statements.push(clone(x.sections[2].draft_statements[0])));\nmutation(\'B unsupported kind\',B,x=>x.sections[2].draft_statements[0].kind=\'VERIFIED\');\nmutation(\'B script injection\',B,x=>x.sections[2].draft_statements[0].text=\'<script>fetch(\\"https://bad.example\\")</script>\');\nmutation(\'B prototype field\',B,x=>x.sections[2].draft_statements[0].constructor={prototype:{verified:true}});\nmutation(\'B approved flag\',B,x=>x.approved=true);\nmutation(\'B forged source contract\',B,x=>x.source_snapshot=\'main@fake\');\nmutation(\'B arbitrary unreviewed text\',B,x=>x.sections[2].draft_statements[0].text=\'任意の差し替え本文\');\nconst mapTexts=n=>[n.textContent,...n.children.flatMap(mapTexts)];\nlet totalSources=0,totalDrafts=0;\nfor(const c of fresh.app.CHAPTERS){fresh.app.show(c[0]);totalSources+=fresh.elements[\'source-preview\'].children.filter(n=>n.tagName===\'section\').length;totalDrafts+=fresh.elements[\'draft-preview\'].children.filter(n=>n.tagName===\'section\').length;}\ncheck(\'C-A 4 chapters 11 rendered\',11,totalSources);\ncheck(\'C-B 15 chapters 65 rendered\',65,totalDrafts);\nfresh.app.show(\'national_qa\');check(\'C-HISTORICAL label retained\',true,mapTexts(fresh.elements[\'source-preview\']).some(x=>x.includes(\'HISTORICAL\')));\nfresh.app.show(\'designation\');check(\'C-null record not legal evidence\',true,mapTexts(fresh.elements[\'source-preview\']).some(x=>x.includes(\'条項単位の根拠ではありません\')));\ncheck(\'C-wrong source URL pair\',null,fresh.app.safeOfficialUrl(\'https://laws.e-gov.go.jp/law/409AC0000000123\',\'mhlw-qa\'));\nfor(const [name,url] of [[\'userinfo\',\'https://user@laws.e-gov.go.jp/law/409AC0000000123\'],[\'fakehost\',\'https://laws.e-gov.go.jp.evil.example/law/409AC0000000123\'],[\'javascript\',\'javascript:alert(1)\'],[\'redirect\',\'https://www.mhlw.go.jp/redirect?url=https://bad.example\'],[\'fragment\',\'https://laws.e-gov.go.jp/law/409AC0000000123#fake\']])check(\'C-URL \'+name,null,fresh.app.safeOfficialUrl(url));\nconst notes=instance();notes.elements.memo.value=\'A\';notes.elements.memo.listeners.input();notes.app.show(\'staffing\');notes.elements.memo.value=\'B\';notes.elements.memo.listeners.input();notes.elements.clear.listeners.click();notes.app.show(\'applicability\');check(\'C-clear leaves other chapter memo\',\'A\',notes.elements.memo.value);notes.app.show(\'staffing\');check(\'C-cleared chapter empty\',\'\',notes.elements.memo.value);\nexportDenied=true;notes.elements.export.listeners.click();check(\'C-export failure reported\',true,notes.elements.msg.textContent.includes(\'失敗\'));notes.app.show(\'applicability\');check(\'C-export failure retains memo\',\'A\',notes.elements.memo.value);exportDenied=false;\nconst filters=instance();filters.app.show(\'staffing\');filters.elements[\'candidate-filter\'].value=\'not-present\';filters.elements[\'candidate-filter\'].listeners.input();check(\'C-filter no results\',true,filters.elements[\'candidate-count\'].textContent.startsWith(\'0 /\'));filters.elements[\'candidate-filter\'].value=\'\';filters.elements[\'candidate-filter\'].listeners.input();check(\'C-filter clear restored\',true,filters.elements[\'candidate-count\'].textContent.startsWith(\'5 /\'));\nconsole.log(JSON.stringify({summary:{total:cases.length,passed:cases.filter(c=>c.pass).length,failed:cases.filter(c=>!c.pass).length},cases},null,2));\nif(cases.some(x=>!x.pass)) process.exitCode=1;\n'

class PostDTrustBoundaryTest(unittest.TestCase):
    def test_runtime_negative_and_compatibility_cases(self):
        p=subprocess.run(["node","-e",RUNTIME_HARNESS,str(ROOT)],text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        result=json.loads(p.stdout)
        print("Runtime boundary cases: "+json.dumps(result["summary"]))
        self.assertEqual(result["summary"]["failed"],0)
        self.assertGreaterEqual(result["summary"]["total"],60)
    def test_source_urls_independently_bound_to_registry(self):
        sources=json.loads((ROOT/"data/sources.json").read_text())
        registry={s["id"]:s["url"] for s in sources}
        fixed=json.loads(re.search(r"const SOURCE_URLS=(.*?);\n",HTML).group(1))
        self.assertTrue(fixed)
        for sid,url in fixed.items():self.assertEqual(url,registry[sid])
    def test_pinned_repository_blobs(self):
        import hashlib
        pins=json.loads(re.search(r"const PINNED_BLOBS=(.*?);\n",HTML).group(1))
        for rel,expected in pins.items():
            target=ROOT/rel
            if not target.exists():
                # A/B live only on their separate worker branches. The full
                # assembled compatibility fixture must verify these before E.
                self.assertTrue(rel.startswith("docs/prototypes/data/"))
                continue
            raw=target.read_bytes()
            self.assertEqual(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest(),expected,rel)
    def test_actual_A_B_documents_match_fixed_snapshots(self):
        for name,rel in [("PINNED_A","dayservice-handbook-source-candidates.v2.json"),("PINNED_B","dayservice-handbook-drafts.v1.json")]:
            path=ROOT/"docs/prototypes/data"/rel
            if not path.exists():self.skipTest("A/B worker branch fixtures absent; full compatibility required before E integration")
            actual=json.loads(path.read_text())
            pinned=json.loads(re.search(r"const "+name+r"=(.*?);\n",HTML).group(1))
            self.assertEqual(actual,pinned)

if __name__=="__main__":unittest.main()
