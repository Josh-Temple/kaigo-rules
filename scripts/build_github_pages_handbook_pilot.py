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
               "label input button").split())
VOID = {"br", "hr", "input"}
DROP_CONTENT = {"script", "style", "svg", "iframe", "noscript", "template", "canvas", "object"}
ALLOWED_ATTRS = {"class", "id", "aria-label", "aria-current", "aria-hidden", "aria-labelledby",
                 "aria-describedby", "aria-controls", "aria-expanded", "role", "scope",
                 "colspan", "rowspan", "title", "tabindex", "open", "for", "headers"}
PRINT_JS = 'document.addEventListener("click",function(e){if(e.target.closest("[data-handbook-print]"))window.print()});\n'
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
.dayservice-service-timeline{display:grid;grid-template-columns:3fr 1fr 5fr;font-size:.9rem;line-height:1.6;margin-top:14px}
.dayservice-service-period{display:grid;align-content:center;gap:4px;text-align:center;padding:10px 4px;background:#c7ded1;border:1px solid #597b6e}
.dayservice-service-gap{border-block:1px dashed #8a978f;background:repeating-linear-gradient(135deg,transparent,transparent 5px,#dce4de 5px,#dce4de 7px)}
.dayservice-counselor-comparison{display:grid;grid-template-columns:3fr 1fr 4fr 1fr;gap:2px;margin-top:10px;font-size:.78rem}
.dayservice-counselor-comparison span{background:#dce9e0;border:1px solid #9baca2;padding:8px 4px;text-align:center;min-width:0;overflow-wrap:anywhere}
.dayservice-counselor-comparison strong{display:block}.dayservice-counselor-comparison .dayservice-missing-hour{background:#faf0e8;border-color:#ac725a}
input[type=checkbox]{width:1.2rem;height:1.2rem;margin-inline-end:.5rem}button{font:inherit;padding:.6rem;cursor:pointer}
a:focus-visible,summary:focus-visible,input:focus-visible,button:focus-visible{outline:3px solid #ba7000;outline-offset:2px}
.pilot-banner{max-width:1050px;margin:0 auto;border-color:#6b756b}
@media print{body,main{background:#fff}nav,.pilot-banner,button{display:none}details{display:block}}
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
    def __init__(self, link_rewriter=link_target) -> None:
        super().__init__(convert_charrefs=True)
        self.collecting = False
        self.finished = False
        self.article_depth = 0
        self.drop_stack: list[str] = []
        self.chunks: list[str] = []
        self.link_count = 0
        self.button_text = None
        self.link_rewriter = link_rewriter

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
        if tag in {"svg", "canvas", "iframe", "object", "img"}:
            raise RuntimeError(f"Unsupported interactive or graphical element: {tag}")
        if tag in DROP_CONTENT:
            self.drop_stack.append(tag)
            return
        if tag not in ALLOWED:
            return
        if tag == "input" and attrs_map.get("type") != "checkbox":
            raise RuntimeError("Unsupported input in handbook article")
        if tag == "button":
            if self.button_text is not None:
                raise RuntimeError("Nested buttons are unsupported")
            self.button_text = []
        safe = ['type="button"', 'data-handbook-print="true"'] if tag == "button" else []
        for key, value in attrs:
            if value is None:
                if tag == "details" and key == "open":
                    safe.append("open")
                if tag == "input" and key in {"checked", "disabled"}:
                    safe.append(key)
                continue
            if key == "href" and tag == "a":
                target = self.link_rewriter(value)
                if target is None:
                    continue
                safe.append(f'href="{escape(target)}"')
                self.link_count += 1
            elif key in ALLOWED_ATTRS:
                safe.append(f'{key}="{escape(value)}"')
            elif tag == "input" and key == "type" and value == "checkbox":
                safe.append('type="checkbox"')
            elif tag == "input" and key in {"checked", "disabled"}:
                safe.append(key)
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
        if tag == "button":
            if self.button_text is None or "".join(self.button_text).strip() not in {
                "この章のページを印刷・PDF保存", "この章を印刷・PDF保存",
            }:
                raise RuntimeError("Unknown handbook button; refusing to guess its behavior")
            self.button_text = None
        if tag in ALLOWED and tag not in VOID:
            self.chunks.append("</" + tag + ">")
        if tag == "article":
            self.article_depth -= 1
            if self.article_depth == 0:
                self.collecting = False
                self.finished = True

    def handle_data(self, data):
        if self.collecting and not self.drop_stack and not self.finished:
            if self.button_text is not None:
                self.button_text.append(data)
            self.chunks.append(html.escape(data, quote=False))


def html_page(title: str, body: str, css_path: str) -> str:
    return (f'<!doctype html><html lang="ja"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="robots" content="noindex,nofollow,noarchive">'
            f'<title>{escape(title)} — 静的移行検証</title>'
            f'<link rel="stylesheet" href="{css_path}">'
            f'<script defer src="{css_path.replace("styles.css", "print.js")}"></script></head><body>'
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
    (OUT / "print.js").write_text(PRINT_JS, encoding="utf-8")
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
            "Only sanitized article HTML is copied; React scripts and RSC hydration data are discarded. A fixed local script enables the original print action.",
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
        "- Excludes Next hydration state, preview and all other routes; only a fixed local print script is included.",
        "- Remaining: legal/content parity, presentation parity, mobile performance, complete routing/API and search.",
        "- Status: HOLD_NO_DEPLOY / NO_MERGE",
    ]
    (OUT / "measurement.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return summary


if __name__ == "__main__":
    build()
