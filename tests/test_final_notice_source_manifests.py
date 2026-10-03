import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CASES = {
    "community-dayservice": "https://www.mhlw.go.jp/content/12300000/001227939.pdf",
    "regular-round": "https://www.mhlw.go.jp/content/12300000/001227939.pdf",
    "night-homevisit": "https://www.mhlw.go.jp/content/12300000/001227939.pdf",
    "care-management": "https://www.mhlw.go.jp/content/12300000/001227941.pdf",
    "preventive-support": "https://www.mhlw.go.jp/content/12300000/001227942.pdf",
}


class FinalNoticeSourceManifestTest(unittest.TestCase):
    def test_final_r6_amendment_evidence_is_pinned(self):
        for service_id, final_url in CASES.items():
            with self.subTest(service_id=service_id):
                scope = json.loads(
                    (
                        ROOT
                        / f"data/services/{service_id}/standards-interpretation-scope.json"
                    ).read_text(encoding="utf-8")
                )
                finals = [
                    row
                    for row in scope["source_manifest"]
                    if row["role"] == "FINAL_R6_AMENDMENT_COMPARISON"
                ]
                self.assertEqual(len(finals), 1)
                self.assertEqual(finals[0]["url"], final_url)
                assurance = scope["source_assurance"]
                self.assertTrue(assurance["final_amendment_evidence_identified"])
                self.assertFalse(assurance["integrated_current_text_established"])
                self.assertFalse(assurance["omitted_text_reconstruction_allowed"])
                self.assertFalse(assurance["publication_allowed"])


if __name__ == "__main__":
    unittest.main()
