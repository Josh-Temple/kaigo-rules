import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SCRIPTS=ROOT/"scripts"; sys.path.insert(0,str(SCRIPTS))
from validate_community_preventive_scope import TARGETS,validation_errors
class CommunityPreventiveScopeTests(unittest.TestCase):
 def test_scope_bundle_validates_fail_closed(self):self.assertEqual([],validation_errors(ROOT))
 def test_scope_work_does_not_enable_routes_or_publication(self):
  for sid in TARGETS:
   cfg=json.loads((ROOT/f"data/services/{sid}.json").read_text(encoding="utf-8"))
   self.assertFalse(cfg["routing"]["future_service_base_enabled"]); self.assertTrue(all(v is False for v in cfg["publication_gate"].values()))
 def test_verification_currentness_not_promoted(self):
  for sid in TARGETS:
   for n in ("care-insurance-act-scope.json","standards36-scope.json","remuneration-scope.json","unit-price-scope.json"):
    d=json.loads((ROOT/f"data/services/{sid}/{n}").read_text(encoding="utf-8"))
    self.assertEqual("NOT_SERVICE_VERIFIED",d["applicability_verification"]); self.assertEqual("NOT_ESTABLISHED",d["currentness"]["status"]); self.assertFalse(d["automatic_verification_promotion_allowed"])
if __name__=="__main__":unittest.main()
