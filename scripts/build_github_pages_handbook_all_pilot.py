#!/usr/bin/env python3
"""Generate a *private*, non-deployable snapshot of prerendered handbooks.

Only the article from routes enumerated by the existing handbook manifest is
read. No preview route, raw data directory, or React hydration payload is
copied. This experiment is not a visual, legal, accessibility, or release pass.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_github_pages_handbook_pilot as pilot

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-z0-9-]+$")


def build(root: Path = ROOT) -> dict:
    root = root.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    if temp_root == root or root in temp_root.parents:
        raise RuntimeError("Temporary output cannot be inside the source repository")
    source = root / ".next/server/app/handbook"
    master = root / "data/handbook.generated.json"
    if not master.is_file() or not source.is_dir():
        raise RuntimeError("Existing handbook manifest and Next.js rendered pages are required")
    data = json.loads(master.read_text(encoding="utf-8"))
    services = data.get("services")
    if not isinstance(services, list) or not services:
        raise RuntimeError("Missing handbook services")
    routes = {}
    for service in services:
        service_id = str(service.get("service_id", ""))
        chapters = service.get("chapters")
        if not ID.fullmatch(service_id) or service_id in routes or not isinstance(chapters, list) or not chapters:
            raise RuntimeError("Invalid or duplicate handbook service")
        slugs = []
        for chapter in chapters:
            slug = str(chapter.get("section_id", "")).replace("_", "-")
            if not ID.fullmatch(slug) or slug in slugs:
                raise RuntimeError("Invalid or duplicate handbook chapter")
            slugs.append(slug)
        routes[service_id] = set(slugs)
    out = Path(tempfile.mkdtemp(prefix="kaigo-handbook-private-", dir=temp_root))
    pages = []
    root_links = []
    try:
        (out / "styles.css").write_text(pilot.STYLES + "\n", encoding="utf-8")
        (out / "print.js").write_text(pilot.PRINT_JS, encoding="utf-8")
        for service in services:
            service_id = service["service_id"]
            service_label = str(service.get("label") or service_id)
            chapter_links = []

            def rewrite(href: str) -> str | None:
                if not href or any(ord(c) < 32 or ord(c) == 127 for c in href):
                    return None
                parts = urlsplit(href)
                if parts.netloc and not parts.scheme:
                    return None
                if parts.path.startswith("/handbook-preview"):
                    raise RuntimeError("Preview route must not be linked from the pilot")
                suffix = ("?" + parts.query if parts.query else "") + ("#" + parts.fragment if parts.fragment else "")
                if parts.path.rstrip("/") == "/services":
                    return "../../index.html" + suffix
                match = re.fullmatch(r"/handbook/([a-z0-9-]+)/([a-z0-9-]+)/?", parts.path)
                if match:
                    sid, slug = match.groups()
                    if sid not in routes or slug not in routes[sid]:
                        raise RuntimeError("Handbook link is outside the generated manifest")
                    return f"../../handbook/{sid}/{slug}.html" + suffix
                match = re.fullmatch(r"/services/([a-z0-9-]+)/?", parts.path)
                if match and match.group(1) in routes:
                    return f"../../services/{match.group(1)}/index.html" + suffix
                return pilot.link_target(href)

            for chapter in service["chapters"]:
                slug = chapter["section_id"].replace("_", "-")
                title = str(chapter.get("title", ""))
                src = source / service_id / (slug + ".html")
                if not title or not src.is_file():
                    raise RuntimeError("A prerendered chapter is missing")
                parser = pilot.ArticleSanitizer(link_rewriter=rewrite)
                parser.feed(src.read_text(encoding="utf-8"))
                if not parser.finished or parser.article_depth != 0:
                    raise RuntimeError("A complete handbook article was not found")
                article = "".join(parser.chunks)
                if pilot.html.escape(title, quote=False) not in article or "<script" in article or "__next" in article:
                    raise RuntimeError("Handbook content or sanitization mismatch")
                dest = out / "handbook" / service_id / (slug + ".html")
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(pilot.html_page(title, article, "../../styles.css"), encoding="utf-8")
                pages.append({"service": service_id, "chapter": slug, "links": parser.link_count})
                chapter_links.append(
                    f'<li id="{pilot.escape(chapter["section_id"])}"><a href="../../handbook/{service_id}/{slug}.html">'
                    f'{pilot.escape(title)}</a></li>'
                )
            dest = out / "services" / service_id / "index.html"
            dest.parent.mkdir(parents=True, exist_ok=True)
            body = ('<article class="handbook-page"><h1>' + pilot.escape(service_label) +
                    'の手引</h1><p>未確認の説明を含みます。条件と原典を確認してください。</p>'
                    '<nav aria-label="章の目次"><ol>' + "".join(chapter_links) +
                    '</ol></nav></article>')
            dest.write_text(pilot.html_page(service_label, body, "../../styles.css"), encoding="utf-8")
            root_links.append(f'<li><a href="./services/{service_id}/index.html">{pilot.escape(service_label)}</a></li>')
        index = ('<article class="handbook-page"><h1>サービス別手引</h1>'
                 '<nav aria-label="サービス一覧"><ul>' + "".join(root_links) + '</ul></nav></article>')
        (out / "index.html").write_text(pilot.html_page("サービス別手引", index, "./styles.css"), encoding="utf-8")
        files = [p for p in out.rglob("*") if p.is_file()]
        return {"directory": str(out), "services": len(services), "chapters": len(pages),
                "files": len(files), "bytes": sum(p.stat().st_size for p in files),
                "links": sum(x["links"] for x in pages), "pages": pages}
    except BaseException:
        shutil.rmtree(out, ignore_errors=True)
        raise


if __name__ == "__main__":
    result = build()
    print(json.dumps({key: value for key, value in result.items() if key != "pages"}, ensure_ascii=False))
