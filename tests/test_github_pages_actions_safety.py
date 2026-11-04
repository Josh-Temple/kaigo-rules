"""Fail-closed regression checks for CI cost and beta publication boundaries.

These tests are intentionally dependency-free and inspect workflow source.
They do not replace GitHub Actions event dispatch tests or release acceptance.
"""
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def workflow(filename):
    return (WORKFLOWS / filename).read_text(encoding="utf-8")


class PagesActionsSafetyTests(unittest.TestCase):
    def test_beta_requires_independent_variable_and_mode_file(self):
        text = workflow("kaigo-pages-continuous-beta.yml")
        self.assertIn("vars.KAIGO_PAGES_BETA_APPROVED == 'true'", text)
        self.assertIn('if [[ ! -e .github/pages-beta-mode.txt ]]; then', text)
        self.assertIn('elif [[ "$(cat .github/pages-beta-mode.txt)" == "beta" ]]; then', text)
        self.assertIn("Unexpected beta mode", text)
        self.assertIn("needs.preflight.outputs.enabled == 'true'", text)
        self.assertIn("github.ref == 'refs/heads/main'", text)

    def test_beta_pr_cannot_package_or_deploy(self):
        text = workflow("kaigo-pages-continuous-beta.yml")
        self.assertRegex(text, r"(?m)^  verify:\n    name: PR safety unit tests")
        self.assertRegex(text, r"(?m)^  package:\n(?:.*\n){0,5}    if: github.event_name != 'pull_request'")
        self.assertRegex(text, r"(?m)^  deploy:\n(?:.*\n){0,5}    if: github.event_name != 'pull_request'")
        self.assertIn("noindex_pages", text)
        self.assertIn("prepare_github_pages_beta.py", text)

    def test_heavy_feasibility_is_manual_and_pr_still_checks_safety(self):
        text = workflow("github-pages-feasibility.yml")
        self.assertRegex(text, r"(?m)^  pr-safety:\n(?:.*\n){0,4}    if: github.event_name == 'pull_request'")
        self.assertRegex(text, r"(?m)^  measure:\n(?:.*\n){0,6}    if: github.event_name == 'workflow_dispatch'")
        self.assertIn("npm run build", text)
        self.assertIn("test_github_pages_release_gate.py", text)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", text)

    def test_publication_readiness_stays_on_for_data_and_legal_changes(self):
        text = workflow("verify-publication-readiness-integration.yml")
        self.assertIn('      - "data/**"', text)
        self.assertIn('      - "scripts/**"', text)
        self.assertIn('      - "!scripts/prepare_github_pages_beta.py"', text)
        self.assertIn("build_publication_readiness.py", text)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", text)

    def test_formal_release_keeps_independent_approval(self):
        text = workflow("kaigo-pages-release.yml")
        self.assertIn("acceptance_commit:", text)
        self.assertIn("check_github_pages_release_gate.py", text)
        self.assertIn("github.ref == 'refs/heads/main'", text)
        self.assertIn("cancel-in-progress: false", text)


if __name__ == "__main__":
    unittest.main()
