"""End-to-end checks for the unpublished, still incomplete static experiment."""
import importlib.util
import hashlib
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from urllib.request import build_opener
from urllib.error import HTTPError
from tests.test_github_pages_handbook_pilot import check_local_links

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("full_partial_pilot", ROOT / "scripts/build_github_pages_integrated_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class FullPartialPilotTest(unittest.TestCase):
    def capture_rules(self, optimized, routes):
        child, base = pilot.qa_details.start_next(pilot_optimized=optimized)
        snapshots = {}
        try:
            opener = build_opener(pilot.qa_details.NoRedirect())
            for route in routes:
                try:
                    with opener.open(base + route, timeout=60) as response:
                        source = response.read(3_000_001)
                        if len(source) > 3_000_000:
                            self.fail("Unexpectedly large legal response")
                except HTTPError as error:
                    if ":" in route:
                        alternate = route.replace(":", "%3A")
                        try:
                            with opener.open(base + alternate, timeout=60) as alternate_response:
                                alternate_status = alternate_response.status
                        except HTTPError as alternate_error:
                            alternate_status = alternate_error.code
                        print("LEGAL_RANGE_ROUTE_DIAGNOSTIC: raw=" + str(error.code) +
                              " encoded=" + str(alternate_status) + " route=" + route, flush=True)
                    raise RuntimeError("Rendered legal baseline unavailable: " + route) from error
                except OSError as error:
                    raise RuntimeError("Rendered legal baseline unavailable: " + route) from error
                parsed = pilot.qa_details.ArticleSnapshot()
                parsed.feed(source.decode("utf-8"))
                self.assertTrue(parsed.done, route)
                snapshots[route] = {
                    "text": hashlib.sha256("".join(parsed.text).encode("utf-8")).hexdigest(),
                    "links": hashlib.sha256(json.dumps(parsed.links, ensure_ascii=False).encode("utf-8")).hexdigest(),
                }
        finally:
            if child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
        return snapshots

    def test_private_integrated_details_and_links(self):
        if os.environ.get("KAIGO_RUN_STATIC_DETAILS") != "1":
            self.skipTest("Full integrated test runs in the dedicated post-build step")
        if not (ROOT / ".next/BUILD_ID").is_file() or not (ROOT / "node_modules/next/dist/bin/next").is_file():
            self.fail("Validated Next.js application missing")
        routes = ["/rules/1", "/rules/93", "/rules/100?service=dayservice",
                  "/rules/18?service=homevisit", "/rules/140-16:140-25", "/rules/156:173"]
        original = self.capture_rules(False, routes)
        optimized = self.capture_rules(True, routes)
        self.assertEqual(optimized, original, "Private index changed the rendered legal text or links")
        print("RENDERED_RULE_INDEX_PARITY: " + str(len(routes)) + " / " + str(len(routes)), flush=True)
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
