"""E integration guard: only fixed local A/B previews; no legal approval or publication."""
import hashlib, json, re, unittest
from pathlib import Path
from html.parser import HTMLParser
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/"docs/prototypes/dayservice-handbook.html").read_text(encoding="utf-8")
PATHS={
"docs/prototypes/data/dayservice-handbook-source-candidates.v2.json":"9cb420b80dfeb5407ceb1fea49aae06a065d978d",
"docs/prototypes/data/dayservice-handbook-drafts.v1.json":"0383262867e38e9a0bf20ad07463b575ab8531a8",
"data/sources.json":"0f23469ce8a5e8a4c892d820be9d40565b8712f2",
"data/care-insurance-act-scope.json":"8af02781b721c811b377ff0525f74ba64646181d",
"data/qa-items.json":"1b07808d1afe66ed4799fce4053c5cd8412b37a0",
"data/notice-current-skeleton.json":"77f656242eb2d5c9a5bd1d6e5d0d581813e51630",
"data/rule-nodes.json":"c713520e3ec0f6234d92be26c969a575863d4549",
"data/remuneration-current-skeleton.json":"4caef5d7c34c1658e442db137fed20944ebfeb06",
}
def blob(b):return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
class IntegrationTest(unittest.TestCase):
 def test_fixed_repository_source_identity(self):
  for path,expected in PATHS.items():
   with self.subTest(path=path):self.assertEqual(blob((ROOT/path).read_bytes()),expected)
 def test_integrated_documents_exact(self):
  for name,path,variable in [
   ("sources","docs/prototypes/data/dayservice-handbook-source-candidates.v2.json","PINNED_A"),
   ("drafts","docs/prototypes/data/dayservice-handbook-drafts.v1.json","PINNED_B")]:
   with self.subTest(name=name):
    m=re.findall(r'<script id="handbook-'+name+r'-json" type="application/json">(.*?)</script>',HTML,re.S)
    self.assertEqual(len(m),1);self.assertNotIn("<",m[0])
    raw=json.loads((ROOT/path).read_text(encoding="utf-8"))
    self.assertEqual(json.loads(m[0]),raw)
    pinned=re.search(r'^const '+variable+r'=(.*);$',HTML,re.M)
    self.assertIsNotNone(pinned);self.assertEqual(json.loads(pinned.group(1)),raw)
 def test_local_only(self):
  self.assertIn("connect-src 'none'",HTML)
  self.assertIn('review_completed:false',HTML)
  self.assertIn('noindex,nofollow,noarchive',HTML)
  for s in ['fetch(', 'innerHTML','XMLHttpRequest','sendBeacon','HUMAN_REVIEW_ACCEPTED']:
   self.assertNotIn(s,HTML)
 def test_counts_unreviewed(self):
  a=json.loads((ROOT/"docs/prototypes/data/dayservice-handbook-source-candidates.v2.json").read_text())
  b=json.loads((ROOT/"docs/prototypes/data/dayservice-handbook-drafts.v1.json").read_text())
  self.assertEqual(sum(len(s['candidates']) for s in a['sections']),11)
  self.assertEqual(sum(len(s['draft_statements']) for s in b['sections']),65)
  self.assertEqual(a['sections'][2]['candidates'][0]['candidate_status'],'HISTORICAL')
  self.assertEqual(a['publication_status'],'PUBLICATION_BLOCKED')
  self.assertEqual(b['human_review_state'],'HUMAN_REVIEW_NOT_DONE')
  self.assertEqual(b['legal_explanations_accepted'],0)
if __name__=="__main__":unittest.main()
