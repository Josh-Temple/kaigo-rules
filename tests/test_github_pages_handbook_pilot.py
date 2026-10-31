"""Independent static handbook extraction audit. No deployment."""
import importlib.util
import contextlib
import gzip
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".github-pages-handbook-pilot"
SRC = ROOT / ".next/server/app/handbook/dayservice"

spec = importlib.util.spec_from_file_location(
    "handbook_pilot", ROOT / "scripts/build_github_pages_handbook_pilot.py"
)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
all_spec = importlib.util.spec_from_file_location(
    "all_handbook_pilot", ROOT / "scripts/build_github_pages_handbook_all_pilot.py"
)
all_pilot = importlib.util.module_from_spec(all_spec)
all_spec.loader.exec_module(all_pilot)
integrated_spec = importlib.util.spec_from_file_location(
    "integrated_handbook_search_pilot", ROOT / "scripts/build_github_pages_integrated_pilot.py"
)
integrated_pilot = importlib.util.module_from_spec(integrated_spec)
integrated_spec.loader.exec_module(integrated_pilot)


class HandbookSanitizerTest(unittest.TestCase):
    def test_native_checkbox_print_button_and_accessibility_survive(self):
        parser = pilot.ArticleSanitizer()
        parser.feed('<article class="handbook-page"><label><input type="checkbox">'
                    '<span aria-hidden="true"></span>確認</label>'
                    '<button type="button">この章のページを印刷・PDF保存</button>'
                    '<script>alert(1)</script></article>')
        output = "".join(parser.chunks)
        self.assertIn('type="checkbox"', output)
        self.assertNotIn("disabled", output)
        self.assertIn('aria-hidden="true"', output)
        self.assertIn('data-handbook-print="true"', output)
        self.assertNotIn("<script", output)
        self.assertNotIn("alert(1)", output)

    def test_unknown_controls_or_graphics_fail_closed(self):
        for fragment in ('<button>送信</button>', '<input type="text">', '<svg></svg>',
                         '<span hidden>非表示</span>', '<div style="display:none">非表示</div>',
                         '<span class="sr-only">非表示</span>'):
            parser = pilot.ArticleSanitizer()
            with self.assertRaises(RuntimeError, msg=fragment):
                parser.feed('<article class="handbook-page">' + fragment + '</article>')

    def test_synthetic_fifteen_chapter_build_keeps_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "pilot"
            source = root / "rendered"
            source.mkdir()
            (root / "data").mkdir()
            chapters = []
            for number in range(1, 16):
                slug = f"chapter-{number}"
                title = f"検証用の章{number}"
                chapters.append({"section_id": slug, "number": number, "title": title})
                (source / (slug + ".html")).write_text(
                    '<article class="handbook-page"><h1>' + title + '</h1>'
                    '<label><input type="checkbox"><span aria-hidden="true"></span>確認</label>'
                    '<button type="button">この章のページを印刷・PDF保存</button></article>',
                    encoding="utf-8",
                )
            (root / "data/handbook.generated.json").write_text(
                json.dumps({"services": [{"service_id": "dayservice", "chapters": chapters}]}),
                encoding="utf-8",
            )
            with patch.multiple(pilot, ROOT=root, OUT=out, CHAPTERS=out / "handbook/dayservice",
                                SOURCE=source), contextlib.redirect_stdout(io.StringIO()):
                summary = pilot.build()
            self.assertEqual(summary["prerendered_public_chapters"], 15)
            page = (out / "handbook/dayservice/chapter-1.html").read_text(encoding="utf-8")
            self.assertIn('data-handbook-print="true"', page)
            self.assertIn('type="checkbox"', page)
            self.assertNotIn("disabled", page)
            self.assertIn('aria-hidden="true"', page)
            self.assertIn('<script defer src="../../print.js"></script>', page)
            self.assertEqual((out / "print.js").read_text(encoding="utf-8"), pilot.PRINT_JS)

    def test_all_handbooks_build_and_link_from_public_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "source"
            (root / "data").mkdir(parents=True)
            services = []
            for sid in ["alpha", "beta"]:
                chapters = []
                source = root / ".next/server/app/handbook" / sid
                source.mkdir(parents=True)
                for number in range(1, 3):
                    slug = f"chapter-{number}"
                    title = f"{sid}の章{number}"
                    chapters.append({"section_id": slug, "title": title, "number": number})
                    (source / (slug + ".html")).write_text(
                        '<article class="handbook-page"><h1>' + title + '</h1><span id="part"></span>'
                        '<a href="/handbook/alpha/chapter-1#part">章へ</a>'
                        '<a href="/services/beta#chapter-1">目次へ</a>'
                        '<input type="checkbox"><button>この章のページを印刷・PDF保存</button>'
                        '</article>', encoding="utf-8",
                    )
                services.append({"service_id": sid, "label": sid, "chapters": chapters})
            (root / "data/handbook.generated.json").write_text(
                json.dumps({"services": services}), encoding="utf-8",
            )
            result = all_pilot.build(root)
            try:
                self.assertEqual((result["services"], result["chapters"], result["files"]), (2, 4, 9))
                out = Path(result["directory"])
                page = (out / "handbook/beta/chapter-2.html").read_text(encoding="utf-8")
                self.assertIn('../../handbook/alpha/chapter-1.html#part', page)
                self.assertIn('../../services/beta/index.html#chapter-1', page)
                self.assertIn('data-handbook-print="true"', page)
                self.assertFalse((out / "data").exists())
                self.assertFalse((out / "handbook-preview").exists())
                self.assertGreater(check_local_links(self, out), 0)
            finally:
                shutil.rmtree(result["directory"], ignore_errors=True)

    def test_integration_allows_only_expected_search_files(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            out, search = base / "handbook", base / "search"
            (out / "handbook").mkdir(parents=True)
            search.mkdir()
            (out / "index.html").write_text('<article><h1>手引</h1></article>', encoding="utf-8")
            for name in integrated_pilot.STATIC_FILES:
                (search / name).write_text("", encoding="utf-8")
            (search / "index.html").write_text('<main><h1>検索</h1></main>', encoding="utf-8")
            (search / "services.json").write_text(
                json.dumps([{"id": "dayservice", "label": "通所介護", "file": "service-dayservice.json"}]),
                encoding="utf-8",
            )
            (search / "qa-options.json").write_text("[]", encoding="utf-8")
            (search / "qa.html").write_text('<main><h1>Q&A</h1></main>', encoding="utf-8")
            groups = {group: [] for group in integrated_pilot.GROUPS}
            for name in ["global.json", "service-dayservice.json"]:
                (search / name).write_text(json.dumps(groups), encoding="utf-8")
            (search / "global.json.gz").write_bytes(gzip.compress((search / "global.json").read_bytes(), mtime=0))
            (search / "secret.txt").write_text("not public", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                integrated_pilot.integrate(out, search)
            self.assertFalse((out / "databases").exists())
            (search / "secret.txt").unlink()
            (search / "index.html").write_text('<main><h1>検索</h1>-----BEGIN PRIVATE KEY-----</main>', encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Secret-like"):
                integrated_pilot.integrate(out, search)
            self.assertFalse((out / "databases").exists())
            (search / "index.html").write_text('<main><h1>検索</h1></main>', encoding="utf-8")
            (search / "global.json.gz").write_bytes(gzip.compress(b'{}', mtime=0))
            with self.assertRaisesRegex(RuntimeError, "does not match"):
                integrated_pilot.integrate(out, search)
            (search / "global.json.gz").write_bytes(gzip.compress((search / "global.json").read_bytes(), mtime=0))
            result = integrated_pilot.integrate(out, search)
            self.assertEqual(result["search_services"], 1)
            self.assertTrue((out / "databases/search/global.json").is_file())
            self.assertGreater(check_local_links(self, out), 0)

    def test_integration_accepts_only_complete_detail_manifests(self):
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            out, search = base / "handbook", base / "search"
            (out / "handbook").mkdir(parents=True)
            search.mkdir()
            (out / "index.html").write_text('<article><h1>手引</h1></article>', encoding="utf-8")
            for name in integrated_pilot.STATIC_FILES:
                (search / name).write_text("", encoding="utf-8")
            marker = '<meta name="kaigo-legal-local-details" content="true">'
            (search / "index.html").write_text(marker + '<main><h1>検索</h1></main>', encoding="utf-8")
            marker = '<meta name="kaigo-qa-local-details" content="true">'
            (search / "qa.html").write_text(marker + '<main><h1>Q&A</h1></main>', encoding="utf-8")
            (search / "services.json").write_text(
                json.dumps([{"id": "dayservice", "label": "通所介護", "file": "service-dayservice.json"}]),
                encoding="utf-8",
            )
            (search / "qa-options.json").write_text("[]", encoding="utf-8")
            row = lambda identifier, href: {"id": identifier, "title": identifier, "href": href, "fields": []}
            groups = {group: [] for group in integrated_pilot.GROUPS}
            groups["qa"] = [row("qa.one", "/qa/qa.one")]
            groups["law"] = [row("law.8", "/law/8")]
            (search / "global.json").write_text(json.dumps(groups), encoding="utf-8")
            (search / "global.json.gz").write_bytes(gzip.compress((search / "global.json").read_bytes(), mtime=0))
            groups = {group: [] for group in integrated_pilot.GROUPS}
            groups["ordinance"] = [row("rule.93", "/rules/93?service=dayservice")]
            (search / "service-dayservice.json").write_text(json.dumps(groups), encoding="utf-8")
            (search / "styles.css").write_text(pilot.STYLES + "\n.qa-answer-preline{white-space:pre-line}\n", encoding="utf-8")
            (search / "print.js").write_text(pilot.PRINT_JS, encoding="utf-8")
            for name in ["qa-details/qa.one/index.html", "qa-details/qa.one/reader.html",
                         "legal/law/all/8.html", "legal/rules/dayservice/93.html"]:
                page = search / name
                page.parent.mkdir(parents=True, exist_ok=True)
                page.write_text("<html><body>公開範囲を確認中</body></html>", encoding="utf-8")
            extra = search / "qa-details/qa.one/unexpected.html"
            extra.write_text("unexpected", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "Missing or unexpected detail"):
                integrated_pilot.integrate(out, search)
            self.assertFalse((out / "databases").exists())
            extra.unlink()
            result = integrated_pilot.integrate(out, search)
            self.assertEqual(result["search_services"], 1)
            self.assertTrue((out / "databases/search/qa-details/qa.one/reader.html").is_file())
            self.assertTrue((out / "databases/search/legal/rules/dayservice/93.html").is_file())
            self.assertGreater(check_local_links(self, out), 0)


class VisibleText(HTMLParser):
    def __init__(self, select_article=False):
        super().__init__(convert_charrefs=True)
        self.select_article = select_article
        self.active = not select_article
        self.depth = 0
        self.banned = []
        self.words = []
        self.checkbox_count = 0
        self.disabled_checkboxes = 0
        self.button_count = 0
        self.aria_hidden_count = 0
        self.link_count = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.select_article and not self.active and tag == "article" and "handbook-page" in attrs.get("class", "").split():
            self.active = True
            self.depth = 0
        if not self.active:
            return
        if tag == "article":
            self.depth += 1
        if not self.banned:
            if tag == "input" and attrs.get("type") == "checkbox":
                self.checkbox_count += 1
                self.disabled_checkboxes += int("disabled" in attrs)
            if tag == "button":
                self.button_count += 1
            if tag == "a" and "href" in attrs:
                self.link_count += 1
            if attrs.get("aria-hidden") == "true":
                self.aria_hidden_count += 1
        if tag in {"script", "style", "svg", "iframe", "noscript", "template", "canvas", "object"}:
            self.banned.append(tag)

    def handle_endtag(self, tag):
        if not self.active:
            return
        if self.banned and self.banned[-1] == tag:
            self.banned.pop()
        if tag == "article":
            self.depth -= 1
            if self.select_article and self.depth == 0:
                self.active = False

    def handle_data(self, value):
        if self.active and not self.banned:
            self.words.append(value)

    @property
    def normalized(self):
        return re.sub(r"\s+", "", "".join(self.words))


class LinkInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links = set(), []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])


def check_local_links(testcase, root):
    documents = {}
    for page in root.rglob("*.html"):
        parser = LinkInventory()
        parser.feed(page.read_text(encoding="utf-8"))
        documents[page.resolve()] = parser
    checked = 0
    for page, parser in documents.items():
        for href in parser.links:
            parts = urlsplit(href)
            if parts.scheme or parts.netloc:
                continue
            target = (page.parent / unquote(parts.path)).resolve() if parts.path else page
            testcase.assertTrue(target == root.resolve() or root.resolve() in target.parents, href)
            testcase.assertIn(target, documents, href)
            if parts.fragment:
                testcase.assertIn(unquote(parts.fragment), documents[target].ids, (str(page), href))
            checked += 1
    return checked


@unittest.skipUnless((OUT / "measurement.json").is_file(),
                     "Pilot output is generated after the normal prebuild checks")
class HandbookStaticPilotTest(unittest.TestCase):
    def test_prerendered_articles_keep_visible_text_and_headings(self):
        report = json.loads((OUT / "measurement.json").read_text(encoding="utf-8"))
        self.assertEqual(report["prerendered_public_chapters"], 15)
        self.assertLess(report["static_output_bytes"], 1_000_000_000)
        self.assertEqual(len(report["pages"]), 15)
        for chapter in report["pages"]:
            slug = chapter["chapter"]
            source = SRC / (slug + ".html")
            generated = OUT / "handbook/dayservice" / (slug + ".html")
            self.assertTrue(source.is_file(), slug)
            self.assertTrue(generated.is_file(), slug)
            original = VisibleText(select_article=True)
            original.feed(source.read_text(encoding="utf-8"))
            output = VisibleText(select_article=True)
            output.feed(generated.read_text(encoding="utf-8"))
            self.assertTrue(original.normalized, slug)
            self.assertEqual(output.normalized, original.normalized, slug)
            self.assertEqual(output.checkbox_count, original.checkbox_count, slug)
            self.assertEqual(output.disabled_checkboxes, original.disabled_checkboxes, slug)
            self.assertEqual(output.button_count, original.button_count, slug)
            self.assertEqual(output.aria_hidden_count, original.aria_hidden_count, slug)
            self.assertEqual(output.link_count, original.link_count, slug)
            html = generated.read_text(encoding="utf-8")
            self.assertIn('name="robots" content="noindex', html)
            self.assertEqual(html.count("<script"), 1)
            self.assertIn('<script defer src="../../print.js"></script>', html)
            self.assertNotIn("__next", html)
            self.assertNotIn("handbook-preview", html)
            self.assertIn("未確認", html)

    def test_navigation_is_stable_and_security_boundaries_hold(self):
        index = (OUT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(index.count('./handbook/dayservice/'), 15)
        self.assertEqual(index.count("<script"), 1)
        self.assertIn('<script defer src="./print.js"></script>', index)
        self.assertEqual((OUT / "print.js").read_text(encoding="utf-8"), pilot.PRINT_JS)
        self.assertFalse((OUT / "data").exists())
        self.assertFalse((OUT / "handbook-preview").exists())
        report = json.loads((OUT / "measurement.json").read_text(encoding="utf-8"))
        for row in report["pages"]:
            self.assertLess(row["static_html_bytes"], row["source_html_bytes"])
            self.assertGreater(row["source_links"], 1)

    def test_all_existing_prerendered_handbook_articles(self):
        result = all_pilot.build()
        try:
            out = Path(result["directory"])
            self.assertGreater(result["services"], 1)
            self.assertEqual(result["files"], result["chapters"] + result["services"] + 3)
            self.assertFalse((out / "data").exists())
            self.assertFalse((out / "handbook-preview").exists())
            for row in result["pages"]:
                service, slug = row["service"], row["chapter"]
                source = ROOT / ".next/server/app/handbook" / service / (slug + ".html")
                generated = out / "handbook" / service / (slug + ".html")
                original, output = VisibleText(select_article=True), VisibleText(select_article=True)
                original.feed(source.read_text(encoding="utf-8"))
                output.feed(generated.read_text(encoding="utf-8"))
                self.assertTrue(original.normalized, (service, slug))
                self.assertEqual(output.normalized, original.normalized, (service, slug))
                for key in ("checkbox_count", "disabled_checkboxes", "button_count", "aria_hidden_count", "link_count"):
                    self.assertEqual(getattr(output, key), getattr(original, key), (service, slug, key))
            print(("ALL_HANDBOOK_PILOT: services={services} chapters={chapters} files={files} "
                   "bytes={bytes} links={links}").format(**result))
            run = subprocess.run(
                ["node", "--import", "./experiments/github-pages-db/register.mjs",
                 "experiments/github-pages-db/build.mjs"],
                cwd=ROOT, capture_output=True, text=True, check=True, timeout=180,
            )
            search_dir = Path(json.loads(run.stdout)["dir"])
            try:
                indexed_services = {
                    item["id"] for item in json.loads((search_dir / "services.json").read_text(encoding="utf-8"))
                }
                integrated = integrated_pilot.integrate(out, search_dir)
            finally:
                shutil.rmtree(search_dir, ignore_errors=True)
            checked = check_local_links(self, out)
            self.assertTrue(indexed_services.issubset({row["service"] for row in result["pages"]}))
            self.assertLess(integrated["bytes"], 1_000_000_000)
            print("INTEGRATED_PARTIAL_PILOT: files={files} bytes={bytes} search_services={search_services} local_links_checked=".format(**integrated) + str(checked))
            print("INTEGRATED_PARTIAL_BY_SUFFIX: " + json.dumps(integrated["by_suffix"], sort_keys=True))
            print("INTEGRATED_PARTIAL_LARGEST: " + json.dumps(integrated["largest"], ensure_ascii=False))
            print("INTEGRATED_PARTIAL_DUPLICATES: files={identical_duplicate_files} bytes={identical_duplicate_bytes}".format(**integrated))
            print("INTEGRATED_PARTIAL_SECRET_SCAN: files={secret_scan_files} matches=0".format(**integrated))
            chrome = shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
            if chrome:
                browser = subprocess.run(
                    ["node", "scripts/test_github_pages_integrated_browser.mjs", str(out)],
                    cwd=ROOT, capture_output=True, text=True, timeout=200,
                )
                self.assertEqual(browser.returncode, 0, browser.stderr[-4000:])
                self.assertEqual(browser.stdout.count("INTEGRATED_CHROME:"), 2)
                print(browser.stdout)
            elif os.environ.get("GITHUB_ACTIONS") == "true":
                self.fail("Chrome is unavailable for the integrated partial pilot")
            else:
                print("INTEGRATED_CHROME: skipped; Chrome is unavailable locally")
        finally:
            shutil.rmtree(result["directory"], ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
