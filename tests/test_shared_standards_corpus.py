import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/shared/standards"

class SharedStandardsCorpusTests(unittest.TestCase):
    def test_inventory_contains_current_law_families_and_separates_repealed(self):
        m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(9,len(m["corpora"]))
        self.assertEqual({
          "411M50000100037","418M60000100034","418M60000100035","418M60000100036",
          "411M50000100038","418M60000100037","411M50000100039","411M50000100040","430M60000100005"
        },{x["law_id"] for x in m["corpora"]})
        hist={x["law_id"]:x for x in m["historical_or_special"]}
        self.assertEqual("HISTORICAL_REPEALED_NOT_CURRENT_BASELINE",hist["411M50000100041"]["status"])
        self.assertFalse(m["policies"]["automatic_verification_promotion_allowed"])

    def test_current_main_services_have_only_structural_law_family_mapping(self):
        manifest=json.loads((ROOT/"data/services/manifest.json").read_text(encoding="utf-8"))
        mapping=json.loads((BASE/"service-ordinance-map.json").read_text(encoding="utf-8"))
        self.assertEqual({x["service_id"] for x in manifest["services"]},{x["service_id"] for x in mapping["relations"]})
        self.assertTrue(all(x["verification_status"]=="NOT_SERVICE_VERIFIED" for x in mapping["relations"]))
        self.assertFalse(mapping["automatic_verification_promotion_allowed"])

    def test_new_source_corpora_do_not_embed_service_applicability(self):
        m=json.loads((BASE/"manifest.json").read_text(encoding="utf-8"))
        for entry in m["corpora"]:
            if entry["corpus_id"]=="ordinance37": continue
            nodes=json.loads((BASE/entry["corpus_id"]/"nodes.json").read_text(encoding="utf-8"))
            self.assertTrue(nodes)
            self.assertTrue(all("service_scope" not in row and "applicable_via" not in row for row in nodes))
            self.assertTrue(all(row["id"].startswith(entry["node_prefix"]+".article.") for row in nodes))

    def test_service_relation_projection_does_not_promote_verification(self):
        data=json.loads((BASE/"service-relations.generated.json").read_text(encoding="utf-8"))
        self.assertFalse(data["source_text_duplicated"])
        self.assertFalse(data["safety"]["service_applicability_verified"])
        states={x["service_id"]:x["scope_status"] for x in data["service_scope_states"]}
        self.assertEqual(39,len(states))
        self.assertTrue(all(state=="SCOPE_DEFINED" for state in states.values()))
        self.assertEqual("SCOPE_DEFINED",states["community-dayservice"])
        self.assertTrue(all(x["verification_status"]=="NOT_SERVICE_VERIFIED" for x in data["relations"]))

if __name__=="__main__": unittest.main()
