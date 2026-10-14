"""Focused D-POST-E-01 regression; executes the inline production script in Node."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests/dayservice_handbook_memo_runtime.cjs"
HTML = ROOT / "docs/prototypes/dayservice-handbook.html"


class DayserviceHandbookMemoIntegrityTest(unittest.TestCase):
    def test_runtime_storage_reload_export_and_failure_cases(self):
        p = subprocess.run(["node", str(HARNESS), str(ROOT)], capture_output=True, text=True, check=False)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        results = json.loads(p.stdout)
        self.assertEqual(results["summary"]["failed"], 0)
        self.assertGreaterEqual(results["summary"]["total"], 40)

    def test_no_silent_8000_character_truncation(self):
        html = HTML.read_text(encoding="utf-8")
        self.assertNotIn("notes[r[0]].slice(0,8000)", html)
        self.assertIn("unreadableSaved", html)
        self.assertIn("review_completed:false", html)


if __name__ == "__main__":
    unittest.main()
