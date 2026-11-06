"""Release gate rejects unapproved, stale or incomplete static migrations."""
import importlib.util
import unittest
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts/check_github_pages_release_gate.py"
spec = importlib.util.spec_from_file_location("pages_release_gate", path)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

SHA = "a" * 40


class ReleaseGateTest(unittest.TestCase):
    def good(self):
        report = {
            "total_bytes": 79_000_000,
            "pages_budget_bytes": 1_000_000_000,
            "html_count": 9607,
            "blockers": {k: 0 for k in (
                "production_fallback_links", "root_relative_links",
                "missing_local_links", "unsafe_or_invalid_links",
                "javascript_references_to_production",
            )},
        }
        acceptance = {
            "source_sha": SHA, "decision": "APPROVED_FOR_PUBLICATION",
            "reviewer": "independent-reviewer",
            **{k: True for k in gate.REQUIRED_REVIEWS},
        }
        return report, acceptance

    def test_complete_signed_matching_candidate_can_pass(self):
        report, acceptance = self.good()
        self.assertEqual(gate.errors_for(report, acceptance, SHA), [])

    def test_private_preview_allowed_only_before_public_conversion(self):
        report, approval = self.good()
        report["blockers"]["private_preview_pages"] = 9607
        report["blockers"]["noindex_pages"] = 9607
        self.assertEqual(gate.errors_for(report, approval, SHA, allow_private_preview=True), [])
        self.assertTrue(gate.errors_for(report, approval, SHA))
        report["blockers"]["production_fallback_links"] = 13119
        self.assertTrue(gate.errors_for(report, approval, SHA, allow_private_preview=True))

    def test_rejects_missing_acceptance_and_unreviewed_data(self):
        report, acceptance = self.good()
        report["blockers"]["production_fallback_links"] = 13119
        acceptance.pop("fee_2026_revision_integrated")
        acceptance["source_sha"] = "b" * 40
        issues = gate.errors_for(report, acceptance, SHA)
        self.assertTrue(any("13119" in issue for issue in issues))
        self.assertTrue(any("fee_2026" in issue for issue in issues))
        self.assertTrue(any("source SHA" in issue for issue in issues))

    def test_rejects_malformed_size_and_unapproved_decision(self):
        report, acceptance = self.good()
        report["total_bytes"] = 1_000_000_001
        acceptance["decision"] = "HOLD"
        self.assertGreaterEqual(len(gate.errors_for(report, acceptance, SHA)), 2)


if __name__ == "__main__":
    unittest.main()
