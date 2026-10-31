#!/usr/bin/env python3
"""Private Q&A detail experiment, derived from the existing rendered pages.

The complete corpus includes material whose currentness and human review are
unconfirmed. This output is strictly an unpublished experiment, not a Pages
release. The upstream server must be the locally built, loopback Next.js app.
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.request import HTTPRedirectHandler, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_github_pages_handbook_pilot as pilot

ROOT = Path(__file__).resolve().parents[1]
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,120}$")
QA_PATH = re.compile(r"^/qa/([A-Za-z0-9][A-Za-z0-9._-]{0,120})/?$")
PRELINE = "qa-answer-preline"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError("Unexpected redirect in local Q&A page")


class ArticleSnapshot(HTMLParser):
    """Independently capture visible text and hrefs of the Q&A article."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.done = False
        self.text = []
        self.links = []
        self.drop = 0

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        attrs = dict(attrs)
        if not self.depth:
            if tag != "article" or "answer-page" not in attrs.get("class", "").split():
                return
            self.depth = 1
        elif tag == "article":
            self.depth += 1
        if tag in {"script", "style", "noscript", "template"}:
            self.drop += 1
        if not self.drop and tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])

    def handle_endtag(self, tag):
        if not self.depth or self.done:
            return
        if tag in {"script", "style", "noscript", "template"} and self.drop:
            self.drop -= 1
            return
        if not self.drop and tag == "article":
            self.depth -= 1
            if not self.depth:
                self.done = True

    def handle_data(self, data):
        if self.depth and not self.drop and not self.done:
            self.text.append(data)


class QaSanitizer(pilot.ArticleSanitizer):
    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if not self.collecting:
            if tag != "article" or "answer-page" not in attr.get("class", "").split():
                return
            attrs = [(k, (v + " handbook-page") if k == "class" else v) for k, v in attrs]
        if tag == "p" and attr.get("style", "").replace(" ", "").rstrip(";") == "white-space:pre-line":
            attrs = [(k, v) for k, v in attrs if k not in {"style", "class"}]
            attrs.append(("class", (attr.get("class", "") + " " + PRELINE).strip()))
        super().handle_starttag(tag, attrs)


def safe_id(value):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value) or value in {".", ".."}:
        raise RuntimeError("Unsafe Q&A identifier")
    return value


def rewrite_link(href, known_ids, local_service_anchors=None):
    parts = urlsplit(href)
    if parts.path.startswith("/handbook-preview"):
        raise RuntimeError("Preview routes are not allowed in the private pilot")
    if parts.netloc and not parts.scheme:
        return None
    if parts.netloc or parts.scheme:
        return pilot.link_target(href)
    if parts.path.rstrip("/") == "/qa":
        return "../../qa.html" + (("?" + parts.query) if parts.query else "") + (("#" + parts.fragment) if parts.fragment else "")
    service = re.fullmatch(r"/services/([a-z0-9-]+)/?", parts.path)
    if service and parts.query:
        # The legacy fallback silently discarded query parameters for
        # /services/dayservice. Never turn an unknown query into a local link.
        return pilot.link_target("https://kaigo-rules.vercel.app" + href)
    if service and local_service_anchors and service.group(1) in local_service_anchors:
        # This is a link from databases/search/qa-details/<id>/reader.html
        # into the independently generated handbook service index. Retain a
        # fragment only when that local HTML actually defines the target ID.
        service_id = service.group(1)
        anchors = local_service_anchors[service_id]
        fragment = parts.fragment if parts.fragment in anchors else ""
        return "../../../../services/" + service_id + "/index.html" + (("#" + fragment) if fragment else "")
    match = QA_PATH.fullmatch(parts.path)
    if match and match.group(1) in known_ids:
        reader = parts.query == "reader=1"
        if parts.query and not reader:
            return pilot.link_target(href)
        return "../" + match.group(1) + ("/reader.html" if reader else "/index.html") + (("#" + parts.fragment) if parts.fragment else "")
    return pilot.link_target(href)


def render_article(source_html, title, link_rewriter, css_path="../../styles.css"):
    original = ArticleSnapshot()
    original.feed(source_html)
    if not original.done:
        raise RuntimeError("Rendered article is missing")
    sanitized = QaSanitizer(link_rewriter=link_rewriter)
    sanitized.feed(source_html)
    if not sanitized.finished or sanitized.article_depth:
        raise RuntimeError("Incomplete article")
    body = "".join(sanitized.chunks)
    rendered = pilot.html_page(title, body, css_path)
    snapshot = ArticleSnapshot()
    snapshot.feed(rendered)
    expected_links = [link_rewriter(link) for link in original.links]
    if None in expected_links or "".join(original.text) != "".join(snapshot.text) or expected_links != snapshot.links:
        raise RuntimeError("Article text or links differ from original rendering")
    return rendered, original


def render_detail(source_html, item, identifier, reader, known_ids, local_service_anchors=None):
    link_rewriter = lambda href: rewrite_link(href, known_ids, local_service_anchors)
    rendered, original = render_article(source_html, item.get("topic") or identifier, link_rewriter)
    full_text = "".join(original.text)
    if item.get("question", "") not in full_text or item.get("answer", "") not in full_text:
        raise RuntimeError("Q&A detail omitted the original question or answer")
    if item.get("answer") and PRELINE not in rendered:
        raise RuntimeError("Q&A answer line breaks were not preserved")
    return rendered, len(original.links)


def add_details(search_dir, base_url, corpus, direct, max_seconds=600, local_service_anchors=None):
    out = search_dir.resolve(strict=True)
    temp_root = Path(tempfile.gettempdir()).resolve()
    if out == ROOT or ROOT in out.parents or temp_root not in out.parents:
        raise RuntimeError("Q&A experiment must be outside the repository in the temp directory")
    if search_dir.is_symlink() or any(p.is_symlink() for p in out.rglob("*")) or not (out / "qa.html").is_file() or (out / "qa-details").exists():
        raise RuntimeError("Invalid or already populated Q&A experiment")
    url = urlsplit(base_url)
    if (url.scheme != "http" or url.hostname != "127.0.0.1" or not url.port or url.path not in {"", "/"}
            or url.username or url.password or url.query or url.fragment):
        raise RuntimeError("Only the local Next.js server is allowed")
    by_id = {}
    for row in corpus:
        key = safe_id(row.get("id"))
        if key in by_id or not isinstance(row.get("question"), str) or not isinstance(row.get("answer"), str):
            raise RuntimeError("Invalid Q&A corpus")
        by_id[key] = row
    for key, evidence in direct.items():
        safe_id(key)
        source_id = safe_id(evidence.get("corpus_id") or key)
        if source_id not in by_id:
            raise RuntimeError("Q&A alias does not resolve to the corpus")
        by_id[key] = by_id[source_id]
    if not by_id:
        raise RuntimeError("Empty Q&A corpus")
    known_ids = frozenset(by_id)
    local_service_anchors = local_service_anchors or {}
    if any(not re.fullmatch(r"[a-z0-9-]+", key) or not isinstance(ids, set) or
           any(not re.fullmatch(r"[A-Za-z0-9_-]+", anchor) for anchor in ids)
           for key, ids in local_service_anchors.items()):
        raise RuntimeError("Unsafe local handbook service navigation manifest")
    jobs = [(key, mode) for key in by_id for mode in (False, True)]
    start = time.monotonic()
    opener = build_opener(NoRedirect())

    def process(job):
        identifier, reader = job
        if time.monotonic() - start > max_seconds:
            raise TimeoutError("Q&A detail generation exceeded its time budget")
        suffix = "?reader=1" if reader else ""
        try:
            with opener.open(base_url.rstrip("/") + "/qa/" + quote(identifier, safe="") + suffix, timeout=25) as response:
                if response.status != 200:
                    raise RuntimeError("Local Q&A route failed")
                source = response.read(3_000_001)
                if len(source) > 3_000_000:
                    raise RuntimeError("Unexpectedly large Q&A response")
        except (OSError, RuntimeError) as error:
            raise RuntimeError("Q&A source fetch failed for " + identifier + " reader=" + str(reader)) from error
        try:
            rendered, links = render_detail(
                source.decode("utf-8"), by_id[identifier], identifier, reader,
                known_ids, local_service_anchors,
            )
        except (UnicodeError, RuntimeError) as error:
            raise RuntimeError("Q&A detail parity failed for " + identifier + " reader=" + str(reader)) from error
        dest = out / "qa-details" / identifier / ("reader.html" if reader else "index.html")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")
        return links

    links = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(process, job) for job in jobs]
        try:
            for number, future in enumerate(futures, 1):
                links += future.result()
                if number % 1000 == 0:
                    print("Private Q&A details checked: " + str(number) + " / " + str(len(jobs)), flush=True)
        except BaseException:
            for future in futures:
                future.cancel()
            raise
    (out / "styles.css").write_text(pilot.STYLES + "\n." + PRELINE + "{white-space:pre-line}\n", encoding="utf-8")
    (out / "print.js").write_text(pilot.PRINT_JS, encoding="utf-8")
    qa_page = out / "qa.html"
    html = qa_page.read_text(encoding="utf-8")
    if html.count("<head>") != 1 or "kaigo-qa-local-details" in html:
        raise RuntimeError("Unexpected Q&A search page")
    qa_page.write_text(html.replace("<head>", '<head><meta name="kaigo-qa-local-details" content="true">'), encoding="utf-8")
    files = [p for p in out.rglob("*") if p.is_file()]
    return {"records": len(corpus), "aliases": len(by_id) - len(corpus), "detail_pages": len(jobs),
            "links_checked": links, "files": len(files), "bytes": sum(p.stat().st_size for p in files),
            "elapsed_seconds": round(time.monotonic() - start, 2)}


def start_next(pilot_optimized=False):
    binary = ROOT / "node_modules/next/dist/bin/next"
    if not binary.is_file() or not (ROOT / ".next/BUILD_ID").is_file():
        raise RuntimeError("A validated Next.js build is required")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    environment = os.environ.copy()
    if pilot_optimized:
        environment["KAIGO_PRIVATE_STATIC_PILOT"] = "1"
    else:
        environment.pop("KAIGO_PRIVATE_STATIC_PILOT", None)
    child = subprocess.Popen(["node", str(binary), "start", "--hostname", "127.0.0.1", "--port", str(port)],
                             cwd=ROOT, env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = "http://127.0.0.1:" + str(port)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline and child.poll() is None:
        try:
            with build_opener(NoRedirect()).open(base + "/api/version", timeout=2) as response:
                if response.status == 200:
                    return child, base
        except OSError:
            time.sleep(0.2)
    child.terminate()
    child.wait(timeout=5)
    raise RuntimeError("Local Next.js server did not start")
