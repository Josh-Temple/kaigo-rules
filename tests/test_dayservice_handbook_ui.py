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
        self.assertIn('rows.length<=500',self.js)
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
    def test_excerpts_collapsible(self):
        self.assertIn('document.createElement("details")',self.js)
        self.assertIn('document.createElement("summary")',self.js)
        self.assertIn('quote.textContent=entry.excerpt',self.js)
if __name__=="__main__":unittest.main()
