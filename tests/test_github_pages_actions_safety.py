"""Fail-closed regression checks for CI cost and beta publication boundaries.

These tests are intentionally dependency-free and inspect workflow source.
They do not replace GitHub Actions event dispatch tests or release acceptance.
"""
from pathlib import Path
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

    def test_validate_build_does_not_cancel_manual_audits(self):
        text = workflow("validate-build.yml")
        self.assertIn("format('validate-build-pr-{0}'", text)
        self.assertIn("format('validate-build-push-{0}'", text)
        self.assertIn("format('validate-build-manual-{0}', github.run_id)", text)
        self.assertIn("cancel-in-progress: ${{ github.event_name != 'workflow_dispatch' }}", text)
        self.assertIn("npm run build", text)

    def test_publication_readiness_stays_on_for_data_and_legal_changes(self):
        text = workflow("verify-publication-readiness-integration.yml")
        self.assertIn('      - "data/**"', text)
        self.assertIn('      - "scripts/**"', text)
        self.assertIn('      - "!scripts/prepare_github_pages_beta.py"', text)
        self.assertIn("build_publication_readiness.py", text)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", text)

    def test_scope_gate_is_mandatory_before_pages_upload(self):
        beta = workflow("kaigo-pages-continuous-beta.yml")
        self.assertIn("if [[ -s .github/pages-beta-approved-scope.json ]]; then", beta)
        self.assertIn("scope_inspect(root", beta)
        self.assertIn("PASS_SCOPED_BYTES_ONLY", beta)
        self.assertLess(beta.index("scope_inspect(root"), beta.index("actions/upload-pages-artifact@v4"))
        release = workflow("kaigo-pages-release.yml")
        self.assertIn("pages-distribution-approval.json", release)
        self.assertIn("pages-public-distribution-approval.json", release)
        self.assertLess(release.index("--mode private"), release.index("prepare_github_pages_public_candidate.py"))
        self.assertLess(release.index("--mode public"), release.index("actions/upload-pages-artifact@v4"))

    def test_scope_regressions_stay_on_lightweight_pr_checks(self):
        beta = workflow("kaigo-pages-continuous-beta.yml")
        feasibility = workflow("github-pages-feasibility.yml")
        self.assertIn("tests/test_github_pages_scope_gate.py", beta)
        self.assertIn("tests/test_github_pages_scope_gate.py", feasibility)
        self.assertRegex(feasibility, r"(?m)^  measure:\\n(?:.*\\n){0,6}    if: github.event_name == 'workflow_dispatch'")

    def test_formal_release_keeps_independent_approval(self):
        text = workflow("kaigo-pages-release.yml")
        self.assertIn("acceptance_commit:", text)
        self.assertIn("check_github_pages_release_gate.py", text)
        self.assertIn("github.ref == 'refs/heads/main'", text)
        self.assertIn("cancel-in-progress: false", text)


if __name__ == "__main__":
    unittest.main()
