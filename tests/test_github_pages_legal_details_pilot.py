"""Private legal detail source-parity and route-boundary checks."""
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("legal_details_pilot", ROOT / "scripts/build_github_pages_legal_details_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class LegalDetailPilotTest(unittest.TestCase):
    def test_route_validation_and_range_number(self):
        key = pilot.key_from_href("/rules/156:173?service=dayservice")
        self.assertEqual(key, ("rules", "156:173", "dayservice"))
        self.assertEqual(pilot.local_path(key), "legal/rules/dayservice/156__range__173.html")
        self.assertIsNone(pilot.key_from_href("//outside.example/rules/10"))
        self.assertIsNone(pilot.key_from_href("/rules/10?service=../../secret"))
        self.assertIsNone(pilot.route_link("//outside.example/rules/10", key, {key}))

    def test_local_rendering_preserves_conditions_links_and_scopes(self):
        requested = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                requested.append(self.path)
                parts = urlsplit(self.path)
                page = ('<html><body><article class="answer-page rules-page"><h1>条文</h1>'
                        '<p>原則・条件・例外</p><p>' + unquote(parts.path) + " " + parts.query + '</p>'
                        '<a href="/law/8">法</a><a href="/rules/156:173">基準</a>'
                        '<a href="/rules/93?service=dayservice">サービス別</a>'
                        '<a href="https://example.gov/original">原典</a></article></body></html>').encode("utf-8")
                self.send_response(200)
                self.end_headers()
                self.wfile.write(page)
            def log_message(self, *_args):
                pass
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                out = Path(tmp) / "search"
                out.mkdir()
                (out / "index.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
                (out / "services.json").write_text(json.dumps([{"id": "dayservice", "file": "service-dayservice.json"}]), encoding="utf-8")
                (out / "global.json").write_text(json.dumps({
                    "law": [{"href": "/law/8", "title": "介護保険法"}],
                    "ordinance": [{"href": "/rules/156:173", "title": "基準"}],
                }), encoding="utf-8")
                (out / "service-dayservice.json").write_text(json.dumps({
                    "ordinance": [{"href": "/rules/93?service=dayservice", "title": "通所介護"}],
                }), encoding="utf-8")
                result = pilot.add_details(out, "http://127.0.0.1:" + str(server.server_port))
                self.assertEqual((result["detail_pages"], result["scoped_pages"]), (3, 1))
                self.assertIn("/rules/156:173", requested)
                page = (out / "legal/rules/dayservice/93.html").read_text(encoding="utf-8")
                self.assertIn("原則・条件・例外", page)
                self.assertIn("../../law/all/8.html", page)
                self.assertIn("../all/156__range__173.html", page)
                self.assertIn("https://example.gov/original", page)
                self.assertIn("kaigo-legal-local-details", (out / "index.html").read_text(encoding="utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_full_existing_next_legal_details(self):
        if os.environ.get("KAIGO_RUN_STATIC_DETAILS") != "1":
            self.skipTest("Full rendered-page test runs in the dedicated post-build step")
        if not (ROOT / ".next/BUILD_ID").is_file() or not (ROOT / "node_modules/next/dist/bin/next").is_file():
            self.fail("Validated Next.js application missing")
        result = subprocess.run(
            ["node", "--import", "./experiments/github-pages-db/register.mjs", "experiments/github-pages-db/build.mjs"],
            cwd=ROOT, text=True, capture_output=True, timeout=180, check=True,
        )
        out = Path(json.loads(result.stdout)["dir"])
        child = None
        try:
            child, base = pilot.qa.start_next(pilot_optimized=True)
            summary = pilot.add_details(out, base, max_seconds=360)
            self.assertGreater(summary["by_kind"]["law"], 0)
            self.assertGreater(summary["by_kind"]["rules"], 0)
            self.assertGreater(summary["scoped_pages"], 0)
            self.assertFalse(any(path.is_symlink() for path in out.rglob("*")))
            print("LEGAL_DETAILS_PRIVATE_PILOT: " + json.dumps(summary, ensure_ascii=False))
            browser = subprocess.run(
                ["node", "scripts/test_github_pages_legal_details_browser.mjs", str(out)],
                cwd=ROOT, text=True, capture_output=True, timeout=180,
            )
            self.assertEqual(browser.returncode, 0, browser.stderr[-4000:])
            self.assertEqual(browser.stdout.count("LEGAL_DETAILS_CHROME:"), 2)
            print(browser.stdout, end="")
        finally:
            if child and child.poll() is None:
                child.terminate()
                try:
                    child.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    child.kill()
                    child.wait(timeout=5)
            shutil.rmtree(out, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
