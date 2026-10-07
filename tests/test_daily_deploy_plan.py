"""Regression tests for daily deployment change detection."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.plan_daily_vercel_deploy import changed_paths, needs_deploy


class DailyDeployPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "CI Test")
        self.git("config", "user.email", "ci@example.test")
        self.write("app/page.tsx", "initial")
        self.git("add", ".")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

    def write(self, path, content):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")

    def commit(self):
        self.git("add", "-A")
        self.git("commit", "-qm", "change")
        return self.git("rev-parse", "HEAD")

    def plan(self, rules_base=None, ops_base=None):
        head = self.git("rev-parse", "HEAD")
        return needs_deploy(
            changed_paths(str(self.repo), rules_base if rules_base is not None else self.base, head),
            changed_paths(str(self.repo), ops_base if ops_base is not None else self.base, head),
        )

    def test_no_changes(self):
        self.assertEqual(self.plan(), (False, False))

    def test_lib_only_changes_rules(self):
        self.write("lib/publication-policy.ts", "changed")
        self.commit()
        self.assertEqual(self.plan(), (True, False))

    def test_data_and_new_build_config_are_caught(self):
        self.write("data/qa-corpus.json", "{}")
        self.write("future-build-config.toml", "modified")
        self.commit()
        self.assertEqual(self.plan(), (True, False))

    def test_ops_only_does_not_deploy_rules(self):
        self.write("ops-site/app/page.tsx", "changed")
        self.commit()
        self.assertEqual(self.plan(), (False, True))

    def test_both_targets(self):
        self.write("lib/database-search.ts", "changed")
        self.write("ops-site/app/page.tsx", "changed")
        self.commit()
        self.assertEqual(self.plan(), (True, True))

    def test_deleted_rules_file_detected(self):
        self.git("rm", "app/page.tsx")
        self.git("commit", "-qm", "delete")
        self.assertEqual(self.plan(), (True, False))

    def test_missing_marker_forces_deploy(self):
        self.assertEqual(changed_paths(str(self.repo), "", self.base), None)
        self.assertEqual(changed_paths(str(self.repo), "no-such-ref", self.base), None)
        self.assertEqual(needs_deploy(None, set()), (True, False))
        self.assertEqual(needs_deploy(set(), None), (False, True))

    def test_manual_force(self):
        self.assertEqual(needs_deploy(set(), set(), force_rules=True), (True, False))
        self.assertEqual(needs_deploy(set(), set(), force_ops=True), (False, True))

    def test_baseline_tree_comparison_not_merge_base(self):
        self.write("lib/a.ts", "A")
        a = self.commit()
        self.write("lib/a.ts", "B")
        b = self.commit()
        self.git("checkout", "-q", a)
        self.write("lib/a.ts", "C")
        c = self.commit()
        self.assertEqual(changed_paths(str(self.repo), b, c), {"lib/a.ts"})


if __name__ == "__main__":
    unittest.main()
