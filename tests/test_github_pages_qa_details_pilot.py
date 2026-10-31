"""Q&A detail extraction safety and text/link parity tests."""
import html
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
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("qa_details_pilot", ROOT / "scripts/build_github_pages_qa_details_pilot.py")
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class QaDetailPilotTest(unittest.TestCase):
    def test_rejects_unknown_graphics_and_unsafe_links(self):
        item = {"question": "質問", "answer": "回答"}
        source = '<article class="answer-page"><h1>質問</h1><p style="white-space:pre-line">回答</p><img src="/x"></article>'
        with self.assertRaises(RuntimeError):
            pilot.render_detail(source, item, "qa.one", False, {"qa.one"})
        self.assertIsNone(pilot.rewrite_link("javascript:alert(1)", {"qa.one"}))
        self.assertIsNone(pilot.rewrite_link("//outside.example/qa", {"qa.one"}))
        with self.assertRaises(RuntimeError):
            pilot.safe_id("../secret")

    def test_real_http_rendering_keeps_text_links_aliases_and_reader(self):
        corpus = [
            {"id": "qa.one", "topic": "一", "question": "質問一", "answer": "一行目\n二行目"},
            {"id": "qa.two", "topic": "二", "question": "質問二", "answer": "別の回答"},
        ]
        direct = {"qa.alias": {"corpus_id": "qa.one"}}
        by_id = {row["id"]: row for row in corpus}
        by_id["qa.alias"] = by_id["qa.one"]

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                parts = urlsplit(self.path)
                key = parts.path.rsplit("/", 1)[-1]
                item = by_id.get(key)
                if not item:
                    self.send_error(404)
                    return
                reader = parts.query == "reader=1"
                page = (
                    '<html><body><article class="answer-page"><h1>' +
                    html.escape(item["topic"]) + '</h1><div class="notice">現行性未確認</div><p>' +
                    html.escape(item["question"]) + '</p><p style="white-space:pre-line">' +
                    html.escape(item["answer"]) + '</p><p>' + ("読者" if reader else "通常") +
                    '</p><a href="/qa/qa.two?reader=1">関連</a><a href="/qa?reader=1">戻る</a>'
                    '<a href="https://example.gov/qa">原典</a></article></body></html>'
                ).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
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
                (out / "qa.html").write_text("<html><head></head><body></body></html>", encoding="utf-8")
                result = pilot.add_details(out, "http://127.0.0.1:" + str(server.server_port), corpus, direct)
                self.assertEqual((result["records"], result["aliases"], result["detail_pages"]), (2, 1, 6))
                content = (out / "qa-details/qa.alias/reader.html").read_text(encoding="utf-8")
                self.assertIn("一行目\n二行目", content)
                self.assertIn("qa-answer-preline", content)
                self.assertIn('../qa.two/reader.html', content)
                self.assertIn("../../qa.html?reader=1", content)
                self.assertIn("https://example.gov/qa", content)
                self.assertIn("現行性未確認", content)
                self.assertIn("kaigo-qa-local-details", (out / "qa.html").read_text(encoding="utf-8"))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_cannot_use_production_as_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "search"
            out.mkdir()
            (out / "qa.html").write_text("<head></head>", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                pilot.add_details(out, "https://kaigo-rules.vercel.app", [], {})
            (out / "linked").symlink_to(out / "qa.html")
            with self.assertRaises(RuntimeError):
                pilot.add_details(out, "http://127.0.0.1:1234", [], {})

    def test_full_existing_next_qa_details(self):
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
            corpus = json.loads((ROOT / "data/qa-corpus.json").read_text(encoding="utf-8"))
            direct = json.loads((ROOT / "data/qa-direct-evidence.json").read_text(encoding="utf-8"))
            child, base = pilot.start_next()
            summary = pilot.add_details(out, base, corpus, direct, max_seconds=480)
            self.assertEqual(summary["records"], len(corpus))
            self.assertEqual(summary["detail_pages"], 2 * (summary["records"] + summary["aliases"]))
            self.assertFalse(any(path.is_symlink() for path in out.rglob("*")))
            print("QA_DETAILS_PRIVATE_PILOT: " + json.dumps(summary, ensure_ascii=False))
            browser = subprocess.run(
                ["node", "scripts/test_github_pages_qa_details_browser.mjs", str(out)],
                cwd=ROOT, text=True, capture_output=True, timeout=180,
            )
            self.assertEqual(browser.returncode, 0, browser.stderr[-4000:])
            self.assertEqual(browser.stdout.count("QA_DETAILS_CHROME:"), 2)
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
