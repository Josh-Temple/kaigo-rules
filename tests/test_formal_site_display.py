"""Test the Pages deployment's public-facing text transformation."""
import json
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/kaigo-pages-public-beta-main.yml"
NOTICE = ("試験公開版です。未確認の法令情報や旧サイトへのリンクが含まれます。"
          "制度の現行性・適用条件は必ず国の原典と指定権者に確認してください。")
PILOT = ('<div class="pilot-banner"><strong>Kaigo Rules 試験公開版</strong>'
         '<p>現在の本番とは別の試作品です。法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。'
         'この試作品では印刷・対話操作やサイト内リンクの一部が本番と異なる場合があります。</p></div>')


def page(title, body):
    return (f'<html><head><meta name="robots" content="noindex"><title>{title}</title></head>'
            f'<body><aside><strong>Kaigo Rules 試験公開版</strong>：{NOTICE}</aside>{body}</body></html>')


def run_transformation(root, count):
    workflow = WORKFLOW.read_text(encoding="utf-8")
    start = workflow.index("          previous_label=")
    end = workflow.index("          post=inspect(root)", start)
    code = textwrap.dedent(workflow[start:end])
    exec(code, {"root": root, "pre": {"html_count": count}, "json": json})


class FormalSiteDisplayTest(unittest.TestCase):
    def make_fixture(self, root):
        pages = {
            "index.html": page("サービス別手引 — 静的移行検証", PILOT + '<a href="./databases/search/index.html">制度DB横断検索を試す</a>'),
            "databases/search/index.html": page("制度DB検索・非公開の移行検証", '<strong>検索の移行検証用・公開不可</strong><p>検索対象には現行性や人手確認が未完了の資料があります。リンク先は現行サイトです。制度の適用は原典で確認してください。</p>'),
            "databases/search/qa.html": page("国Q&A検索・非公開の移行検証", '<strong>国Q&A検索の移行検証用・公開不可</strong><p>発出当時の回答を含みます。現在の取扱いは未確認のものがあるため、判断前に最新の国の資料を確認してください。</p>'),
        }
        for name, content in pages.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        return pages

    def test_public_text_changes_keep_warnings_and_navigation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = self.make_fixture(root)
            run_transformation(root, len(pages))
            contents = {name: (root / name).read_text(encoding="utf-8") for name in pages}
            for content in contents.values():
                self.assertIn('name="robots" content="noindex', content)
                self.assertIn("制度の現行性・適用条件は必ず国の原典と指定権者に確認してください。", content)
                self.assertNotIn("一般公開していません", content)
                self.assertNotIn("現在の本番とは別の試作品です。", content)
            self.assertIn('href="./databases/search/index.html"', contents["index.html"])
            self.assertIn("検索対象には現行性や人手確認が未完了", contents["databases/search/index.html"])
            self.assertIn("現在の取扱いは未確認", contents["databases/search/qa.html"])
            self.assertNotIn("公開不可", contents["databases/search/qa.html"])

    def test_missing_search_notice_stops_deployment(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = self.make_fixture(root)
            search = root / "databases/search/index.html"
            search.write_text(search.read_text().replace("検索の移行検証用・公開不可", "予期しない表示"))
            with self.assertRaisesRegex(RuntimeError, "Unexpected database search copy"):
                run_transformation(root, len(pages))


if __name__ == "__main__":
    unittest.main()
