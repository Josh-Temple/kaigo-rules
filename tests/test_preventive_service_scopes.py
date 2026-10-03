from __future__ import annotations
import importlib.util,json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"scripts/validate_preventive_service_scopes.py"
spec=importlib.util.spec_from_file_location("preventive_scope_validator",SCRIPT)
validator=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(validator)
class PreventiveServiceScopeTests(unittest.TestCase):
    def setUp(self):
        manifest=json.loads((ROOT/"data/services/manifest.json").read_text(encoding="utf-8"))
        self.targets=[x for x in manifest["services"] if x["service_class"]=="PREVENTIVE_SERVICE"]
    def test_validator(self): validator.validate()
    def test_target_set_is_manifest_driven_and_complete(self):
        self.assertGreater(len(self.targets),0)
        for row in self.targets:
            cfg=json.loads((ROOT/row["config"]).read_text(encoding="utf-8")); keys=cfg["scope_files"]
            for key in ("care_insurance_act","standards_index","remuneration","delegated_remuneration_criteria","unit_price_regional_classification"): self.assertIn(key,keys)
            self.assertFalse(cfg["publication_gate"]["public_routes_enabled"]); self.assertFalse(cfg["publication_gate"]["human_review_complete"])
    def test_equipment_sale_explicit_not_applicable(self):
        p=ROOT/"data/services/specific-preventive-welfare-equipment-sale/remuneration-scope.json"; s=json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual("NOT_APPLICABLE",s["remuneration_notification"]["state"])
        self.assertEqual("NOT_APPLICABLE_TO_NOTICE127_CHAIN",s["delegated_remuneration_criteria"]["state"])
        self.assertEqual("NOT_APPLICABLE",s["unit_price_regional_classification"]["state"])
    def test_unresolved_wrappers_fail_closed(self):
        for row in self.targets:
            p=ROOT/"data/services"/row["service_id"]/"standards-scope.json"; s=json.loads(p.read_text(encoding="utf-8"))
            for w in s["incorporation_wrappers"]:
                self.assertEqual("NOT_EXPANDED_FAIL_CLOSED",w["target_resolution_state"]); self.assertNotIn("target_node_ids",w)
if __name__=="__main__": unittest.main()
