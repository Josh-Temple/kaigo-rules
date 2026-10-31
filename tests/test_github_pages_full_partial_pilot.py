"""End-to-end checks for the unpublished, still incomplete static experiment."""
import importlib.util
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from tests.test_github_pages_handbook_pilot import check_local_links

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("full_partial_pilot", ROOT / "scripts/build_github_pages_integrated_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class FullPartialPilotTest(unittest.TestCase):
    def test_private_integrated_details_and_links(self):
        if os.environ.get("KAIGO_RUN_STATIC_DETAILS") != "1":
            self.skipTest("Full integrated test runs in the dedicated post-build step")
        if not (ROOT / ".next/BUILD_ID").is_file() or not (ROOT / "node_modules/next/dist/bin/next").is_file():
            self.fail("Validated Next.js application missing")
        summary = pilot.build_with_details()
        out = Path(summary["directory"])
        try:
            self.assertGreater(summary["handbook_services"], 0)
            self.assertGreater(summary["handbook_chapters"], 0)
            self.assertEqual(summary["qa_details"]["detail_pages"],
                             2 * (summary["qa_details"]["records"] + summary["qa_details"]["aliases"]))
            self.assertGreater(summary["legal_details"]["scoped_pages"], 0)
            self.assertFalse((out / "handbook-preview").exists())
            checked = check_local_links(self, out)
            self.assertGreater(checked, 0)
            report = {key: value for key, value in summary.items() if key != "directory"}
            report["local_links_checked"] = checked
            print("FULL_PARTIAL_PRIVATE_PILOT: " + json.dumps(report, ensure_ascii=False), flush=True)
            browser = subprocess.run(
                ["node", "scripts/test_github_pages_full_partial_browser.mjs", str(out)],
                cwd=ROOT, text=True, capture_output=True, timeout=180,
            )
            self.assertEqual(browser.returncode, 0, browser.stderr[-4000:])
            self.assertEqual(browser.stdout.count("FULL_PARTIAL_CHROME:"), 2)
            print(browser.stdout, end="")
        finally:
            shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
