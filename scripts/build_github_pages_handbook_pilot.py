#!/usr/bin/env python3
"""Produce an unpublished, sanitized static snapshot of already pre-rendered dayservice handbook pages.

This is a migration experiment, not an equivalent replacement of Next.js or
an approval to publish. We use the existing rendered public-facing article,
not source prototype data or React hydration payloads.
"""
from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".github-pages-handbook-pilot"
CHAPTERS = OUT / "handbook" / "dayservice"
SOURCE = ROOT / ".next" / "server" / "app" / "handbook" / "dayservice"
ALLOWED = set(("article nav section aside header footer main div span p h1 h2 h3 h4 h5 h6 "
               "a ul ol li dl dt dd strong b em i u blockquote table caption thead tbody tfoot "
               "tr th td figure figcaption details summary small time pre code br hr sup sub "
               "label input").split())
VOID = {"br", "hr", "input"}
DROP_CONTENT = {"script", "style", "svg", "iframe", "noscript", "template", "canvas", "object"}
ALLOWED_ATTRS = {"class", "id", "aria-label", "aria-current", "role", "scope", "colspan",
                 "rowspan", "title", "tabindex", "open"}
STYLES = """
*{box-sizing:border-box}html{scroll-behavior:smooth}body{font-family:system-ui,-apple-system,"Noto Sans JP",sans-serif;margin:0;line-height:1.75;color:#25332d;background:#f6f8f7}
main{max-width:1050px;margin:0 auto;padding:16px 18px 80px;background:#fff}
h1{font-size:clamp(1.6rem,4vw,2.1rem)}h2{font-size:1.35rem;margin-top:2rem}h3{font-size:1.16rem;margin-top:1.5rem}
section,article,aside,blockquote{max-width:100%}p,li,td,th{overflow-wrap:anywhere}a{color:#005a47;text-underline-offset:3px}
a:focus-visible,summary:focus-visible{outline:3px solid #ba7000;outline-offset:2px}
table{border-collapse:collapse;display:block;overflow-x:auto;width:100%;margin:16px 0}th,td{border:1px solid #c6d1cc;padding:7px 10px;text-align:left;min-width:75px}
th{background:#f0f6f2}caption{text-align:left;font-weight:bold}.handbook-role,.dayservice-reading-topic,.section{margin:14px 0;padding:12px 0;border-bottom:1px solid #d9e3dd}
.handbook-working-note,.handbook-role-warning,.dayservice-source-caution,.notice,.pilot-banner{border-left:4px solid #927500;background:#fffbea;padding:12px 16px;margin:12px 0}
.dayservice-original,blockquote{white-space:pre-wrap}.dayservice-original p{white-space:pre-wrap}blockquote{margin:10px 0;padding:14px;background:#f5f7f5}
.dayservice-excerpt{padding:12px;margin:12px 0;border:1px solid #dae4dd;border-radius:8px}
nav ul{display:flex;gap:6px 18px;flex-wrap:wrap;list-style:none;padding-left:0}
nav li{margin:4px 0}.dayservice-source-block{margin:12px 0 22px}details{margin:10px 0;padding:8px;border:1px solid #d5dfd8;border-radius:6px}
figure{max-width:100%;margin:18px 0}figcaption{font-weight:650}.meta,.eyebrow{font-size:.88rem;color:#54665b}
.pilot-banner{max-width:1050px;margin:0 auto;border-color:#6b756b}
@media print{body,main{background:#fff}nav,.pilot-banner{display:none}details{display:block}}
""".strip()


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def link_target(href: str) -> str | None:
    if not href or any(ord(c) < 32 or ord(c) == 127 for c in href):
        return None
    if href.startswith("#"):
        return href
    if href.startswith("/"):
        parts = urlsplit(href)
        if parts.path.startswith("/handbook/dayservice/"):
            slug = parts.path[len("/handbook/dayservice/"):].strip("/")
            if re.fullmatch(r"[a-z0-9-]+", slug):
                return f"./{slug}.html" + (("?" + parts.query) if parts.query else "") + (("#" + parts.fragment) if parts.fragment else "")
        if parts.path == "/services/dayservice":
            return "../../index.html" + (("#" + parts.fragment) if parts.fragment else "")
        # A transition-only link to the unchanged production website.
        return "https://kaigo-rules.vercel.app" + href
    try:
        parts = urlsplit(href)
        if parts.scheme not in {"http", "https"} or not parts.netloc or parts.username or parts.password:
            return None
        return href
    except ValueError:
        return None


class ArticleSanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.collecting = False
        self.finished = False
        self.article_depth = 0
        self.drop_stack: list[str] = []
        self.chunks: list[str] = []
        self.link_count = 0

    def handle_starttag(self, tag, attrs):
        if self.finished:
            return
        attrs_map = dict(attrs)
        if not self.collecting:
            if tag != "article" or "handbook-page" not in attrs_map.get("class", "").split():
                return
            self.collecting = True
        if tag == "article":
            self.article_depth += 1
        if self.drop_stack:
            if tag in DROP_CONTENT:
                self.drop_stack.append(tag)
            return
        if tag in DROP_CONTENT:
            self.drop_stack.append(tag)
            return
        if tag not in ALLOWED:
            return
        safe = []
        for key, value in attrs:
            if value is None:
                if tag == "details" and key == "open":
                    safe.append("open")
                continue
            if key == "href" and tag == "a":
                target = link_target(value)
                if target is None:
                    continue
                safe.append(f'href="{escape(target)}"')
                self.link_count += 1
            elif key in ALLOWED_ATTRS:
                safe.append(f'{key}="{escape(value)}"')
            elif tag == "input" and key == "type" and value == "checkbox":
                safe.extend(['type="checkbox"', "disabled"])
        self.chunks.append("<" + tag + (" " + " ".join(safe) if safe else "") + ">")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if not self.collecting or self.finished:
            return
        if self.drop_stack:
            if tag == self.drop_stack[-1]:
                self.drop_stack.pop()
            return
        if tag in ALLOWED and tag not in VOID:
            self.chunks.append("</" + tag + ">")
        if tag == "article":
            self.article_depth -= 1
            if self.article_depth == 0:
                self.collecting = False
                self.finished = True

    def handle_data(self, data):
        if self.collecting and not self.drop_stack and not self.finished:
            self.chunks.append(html.escape(data, quote=False))


def html_page(title: str, body: str, css_path: str) -> str:
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow,noarchive">'
            f'<title>{escape(title)} — 静的移行検証</title>'
            f'<link rel="stylesheet" href="{css_path}"></head><body>'
            '<div class="pilot-banner"><strong>静的移行の検証版（一般公開していません）</strong>'
            '<p>現在の本番とは別の試作品です。法令の現行性・適用条件・自治体の基準を必ず原典で確認してください。'
            'この試作品では印刷・対話操作やサイト内リンクの一部が本番と異なる場合があります。</p></div>'
            f'<main>{body}</main></body></html>')


def build() -> dict:
    master = ROOT / "data" / "handbook.generated.json"
    if not master.is_file():
        raise RuntimeError("Generated handbook not found: run existing prebuild and law QA checks")
    data = json.loads(master.read_text(encoding="utf-8"))
    service = next((s for s in data["services"] if s["service_id"] == "dayservice"), None)
    if not service or len(service.get("chapters", [])) != 15:
        raise RuntimeError("Expected exactly 15 existing public dayservice chapters")
    if not SOURCE.exists():
        raise RuntimeError("Next.js did not prerender public dayservice handbook routes")
    CHAPTERS.mkdir(parents=True, exist_ok=True)
    (OUT / "styles.css").write_text(STYLES + "\n", encoding="utf-8")
    output = []
    links = []
    for chapter in service["chapters"]:
        slug = chapter["section_id"].replace("_", "-")
        if not re.fullmatch(r"[a-z0-9-]+", slug):
            raise RuntimeError("Unexpected chapter route")
        source = SOURCE / f"{slug}.html"
        if not source.is_file():
            raise RuntimeError(f"Missing Next.js prerendered public chapter: {source}")
        parser = ArticleSanitizer()
        parser.feed(source.read_text(encoding="utf-8"))
        if not parser.finished or parser.article_depth != 0:
            raise RuntimeError(f"Could not locate complete public article: {slug}")
        article = "".join(parser.chunks)
        if not article or "<script" in article or "__next" in article or "<iframe" in article:
            raise RuntimeError(f"Unsafe output: {slug}")
        if escape(chapter["title"]) not in article:
            raise RuntimeError(f"Original chapter title missing: {slug}")
        rendered = html_page(chapter["title"], article, "../../styles.css")
        dest = CHAPTERS / f"{slug}.html"
        dest.write_text(rendered, encoding="utf-8")
        output.append({
            "chapter": slug, "title": chapter["title"],
            "source_html_bytes": source.stat().st_size,
            "static_html_bytes": dest.stat().st_size,
            "source_links": parser.link_count,
        })
        links.append(f'<li><a href="./handbook/dayservice/{slug}.html">第{chapter["number"]}章：{escape(chapter["title"])}</a></li>')
    overview = html_page("通所介護の手引", '<article class="handbook-page"><h1>通所介護の手引</h1>'
                         '<p>公開済みの15章を、既存Next.jsから静的HTMLへ抽出した検証用目次です。'
                         '未確認の説明を含むため、原典と適用地域を確認してください。</p>'
                         '<nav aria-label="15章の目次"><ol>' + "".join(links) + '</ol></nav></article>',
                         "./styles.css")
    (OUT / "index.html").write_text(overview, encoding="utf-8")
    site_files = [p for p in OUT.rglob("*") if p.is_file()]
    site_bytes = sum(p.stat().st_size for p in site_files)
    if site_bytes >= 1_000_000_000:
        raise RuntimeError("Isolated static pilot exceeds 1GB")
    summary = {
        "status": "HOLD_NO_DEPLOY",
        "prerendered_public_chapters": len(output),
        "static_html_bytes": sum(x["static_html_bytes"] for x in output),
        "static_output_bytes": site_bytes,
        "file_count": len(site_files),
        "article_link_count": sum(x["source_links"] for x in output),
        "pages": output,
        "notes": [
            "This is an isolated static HTML snapshot of *existing public prerendered articles*, not a complete equivalent of the current site.",
            "Only sanitized article HTML is copied: all React scripts, RSC hydration data and unknown tags/attributes are discarded.",
            "Links outside this prototype point to the existing Vercel site.",
            "Interactive functions, visual parity, real browser tests, legal review and complete static export are not approved.",
            "No publishing or site domain changes."
        ],
    }
    (OUT / "measurement.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    report = [
        "# Dayservice handbook static HTML pilot (not deployed)",
        "",
        f"- Existing public handbook chapters: {len(output)}/15",
        f"- Static output: {site_bytes:,} bytes ({site_bytes / 1_000_000:.3f} MB) across {len(site_files)} files (plus local measurement files).",
        f"- Links in sanitized articles: {summary['article_link_count']}",
        "- Source: pre-rendered *public* handbook articles from existing validated Next.js build",
        "- Excludes scripts, Next hydration state, preview and all other routes; source JSON never deployed.",
        "- Remaining: legal/content parity, presentation parity, mobile performance, complete routing/API and search.",
        "- Status: HOLD_NO_DEPLOY / NO_MERGE",
    ]
    (OUT / "measurement.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return summary


if __name__ == "__main__":
    build()
