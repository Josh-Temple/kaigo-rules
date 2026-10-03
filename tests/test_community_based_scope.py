import json,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CommunityBasedScopeTests(unittest.TestCase):
    def test_validator_passes(self):
        p=subprocess.run([sys.executable,str(ROOT/"scripts/validate_community_based_scope.py")],cwd=ROOT,text=True,capture_output=True)
        self.assertEqual(0,p.returncode,p.stdout+"\n"+p.stderr)
        out=json.loads(p.stdout.strip())
        manifest=json.loads((ROOT/"data/services/manifest.json").read_text(encoding="utf-8"))
        n=sum(1 for x in manifest["services"] if x.get("service_class")=="COMMUNITY_BASED_SERVICE")
        self.assertEqual(n,out["services"])
        for k in ("care_act_scopes","standards_scopes","remuneration_scopes","delegated_scopes","unit_price_scopes","unresolved_scopes"): self.assertEqual(n,out[k])
        self.assertEqual(n*5,out["applicability_verification_unfinished"])
if __name__=="__main__": unittest.main()
