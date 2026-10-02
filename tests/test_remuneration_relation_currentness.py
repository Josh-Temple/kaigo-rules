import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RemunerationRelationCurrentnessTest(unittest.TestCase):
    def test_latest_guidance_amendment_relation_uses_may_2026_source(self):
        relations = json.loads(
            (ROOT / "data/remuneration-relations.json").read_text(encoding="utf-8")
        )
        sources = {
            row["id"]: row
            for row in json.loads(
                (ROOT / "data/sources.json").read_text(encoding="utf-8")
            )
        }
        matches = [
            row for row in relations
            if row.get("relation") == "latest_interpretation_amendment_evidence"
        ]
        self.assertEqual(len(matches), 1)
        relation = matches[0]
        self.assertEqual(
            relation["to_source_id"],
            "mhlw-r8-fee-guidance-may-amendment",
        )
        self.assertEqual(
            sources[relation["to_source_id"]]["status"],
            "current_amendment",
        )
        self.assertNotEqual(
            relation["to_source_id"],
            "mhlw-r8-fee-interpretation-amendment",
        )


if __name__ == "__main__":
    unittest.main()
