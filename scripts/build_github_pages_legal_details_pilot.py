#!/usr/bin/env python3
"""Private legal detail experiment, never a deployable Pages output."""
from __future__ import annotations

import concurrent.futures
import json
import posixpath
import re
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit
from urllib.request import build_opener

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_github_pages_handbook_pilot as pilot
import build_github_pages_qa_details_pilot as qa

ROOT = Path(__file__).resolve().parents[1]
NUMBER = r"[0-9]+(?:-[0-9]+)*(?::[0-9]+(?:-[0-9]+)*)?"
ROUTE = re.compile(r"^/(law|rules)/(" + NUMBER + r")/?$")
SERVICE = re.compile(r"^[a-z0-9-]+$")


def key_from_href(href):
    parts = urlsplit(href)
    if parts.scheme or parts.netloc or parts.fragment:
        return None
    match = ROUTE.fullmatch(unquote(parts.path))
    if not match:
        return None
    query = parse_qs(parts.query, keep_blank_values=True, strict_parsing=True)
    if set(query) - {"service"} or len(query.get("service", [])) > 1:
        return None
    service = query.get("service", [""])[0]
    if service and not SERVICE.fullmatch(service):
        return None
    return match.group(1), match.group(2), service


def local_path(key):
    kind, number, service = key
    return "legal/" + kind + "/" + (service or "all") + "/" + number.replace(":", "__range__") + ".html"


def route_link(href, current, known):
    parts = urlsplit(href)
    if parts.path.startswith("/handbook-preview"):
        raise RuntimeError("Preview routes are not allowed in the private pilot")
    if parts.netloc and not parts.scheme:
        return None
    if parts.netloc or parts.scheme:
        return pilot.link_target(href)
    without_fragment = parts.path + (("?" + parts.query) if parts.query else "")
    try:
        key = key_from_href(without_fragment)
    except ValueError:
        key = None
    if key in known:
        relative = posixpath.relpath(local_path(key), posixpath.dirname(local_path(current)))
        return relative + (("#" + parts.fragment) if parts.fragment else "")
    return pilot.link_target(href)


def collect_routes(out):
    groups = json.loads((out / "global.json").read_text(encoding="utf-8"))
    services = json.loads((out / "services.json").read_text(encoding="utf-8"))
    candidates = list(groups["law"]) + list(groups["ordinance"])
    for service in services:
        sid, name = service["id"], service["file"]
        if not SERVICE.fullmatch(sid) or name != "service-" + sid + ".json":
            raise RuntimeError("Invalid service search manifest")
        rows = json.loads((out / name).read_text(encoding="utf-8"))
        candidates.extend(rows["ordinance"])
    routes = {}
    for row in candidates:
        key = key_from_href(row["href"])
        if not key:
            raise RuntimeError("Invalid legal search destination")
        if not isinstance(row.get("title"), str) or not row["title"]:
            raise RuntimeError("Missing legal search title")
        routes.setdefault(key, row["title"])
    if not routes:
        raise RuntimeError("No legal routes")
    return routes, len(candidates)


def add_details(search_dir, base_url, max_seconds=480):
    out = search_dir.resolve(strict=True)
    temp_root = Path(tempfile.gettempdir()).resolve()
    if out == ROOT or ROOT in out.parents or temp_root not in out.parents:
        raise RuntimeError("Legal experiment must be outside the repository")
    if search_dir.is_symlink() or any(p.is_symlink() for p in out.rglob("*")) or (out / "legal").exists():
        raise RuntimeError("Invalid legal experiment directory")
    url = urlsplit(base_url)
    if (url.scheme != "http" or url.hostname != "127.0.0.1" or not url.port or url.path not in {"", "/"}
            or url.username or url.password or url.query or url.fragment):
        raise RuntimeError("Only the local Next.js server is allowed")
    routes, search_rows = collect_routes(out)
    known = frozenset(routes)
    opener = build_opener(qa.NoRedirect())
    start = time.monotonic()

    def process(key, request_timeout=45):
        kind, number, service = key
        if time.monotonic() - start > max_seconds:
            raise TimeoutError("Legal detail generation exceeded its time budget")
        # ':' is a valid path character and is used verbatim by the current
        # search. Preserve it here instead of changing the baseline URL.
        href = "/" + kind + "/" + quote(number, safe=":")
        if service:
            href += "?service=" + quote(service, safe="")
        try:
            with opener.open(base_url.rstrip("/") + href, timeout=request_timeout) as response:
                if response.status != 200:
                    raise RuntimeError("Local legal route failed")
                source = response.read(3_000_001)
                if len(source) > 3_000_000:
                    raise RuntimeError("Unexpectedly large legal response")
        except (OSError, RuntimeError) as error:
            raise RuntimeError("Legal source fetch failed for " + repr(key)) from error
        try:
            rendered, original = qa.render_article(
                source.decode("utf-8"), routes[key], lambda link: route_link(link, key, known),
                "../../../styles.css",
            )
        except (UnicodeError, RuntimeError) as error:
            raise RuntimeError("Legal text/link parity failed for " + repr(key)) from error
        dest = out / local_path(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(rendered, encoding="utf-8")
        return len(original.links)

    route_keys = list(routes)
    # Warm the legal bundles and the first scoped route before parallel work.
    warm_keys = []
    for predicate in (lambda key: key[0] == "law", lambda key: key[0] == "rules" and not key[2],
                      lambda key: key[0] == "rules" and bool(key[2])):
        key = next((key for key in route_keys if predicate(key)), None)
        if key is not None and key not in warm_keys:
            warm_keys.append(key)
    links = 0
    for key in warm_keys:
        warm_started = time.monotonic()
        links += process(key, request_timeout=90)
        print("Private legal warmup: " + repr(key) + " seconds=" +
              str(round(time.monotonic() - warm_started, 2)), flush=True)
    remaining = [key for key in route_keys if key not in warm_keys]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(process, key) for key in remaining]
        try:
            for number, future in enumerate(futures, len(warm_keys) + 1):
                links += future.result()
                if number % 100 == 0:
                    print("Private legal details checked: " + str(number) + " / " + str(len(routes)), flush=True)
        except BaseException:
            for future in futures:
                future.cancel()
            raise
    styles = out / "styles.css"
    if styles.exists():
        allowed_styles = {pilot.STYLES + "\n", pilot.STYLES + "\n." + qa.PRELINE + "{white-space:pre-line}\n"}
        if styles.read_text(encoding="utf-8") not in allowed_styles:
            raise RuntimeError("Unexpected existing detail styles")
    else:
        styles.write_text(pilot.STYLES + "\n", encoding="utf-8")
    script = out / "print.js"
    if script.exists() and script.read_text(encoding="utf-8") != pilot.PRINT_JS:
        raise RuntimeError("Unexpected existing detail script")
    script.write_text(pilot.PRINT_JS, encoding="utf-8")
    index = out / "index.html"
    html = index.read_text(encoding="utf-8")
    if html.count("<head>") != 1 or "kaigo-legal-local-details" in html:
        raise RuntimeError("Unexpected database search page")
    index.write_text(html.replace("<head>", '<head><meta name="kaigo-legal-local-details" content="true">'), encoding="utf-8")
    files = [p for p in out.rglob("*") if p.is_file()]
    by_kind = {kind: sum(key[0] == kind for key in routes) for kind in ("law", "rules")}
    return {"search_rows": search_rows, "detail_pages": len(routes), "by_kind": by_kind,
            "scoped_pages": sum(bool(key[2]) for key in routes), "links_checked": links,
            "files": len(files), "bytes": sum(p.stat().st_size for p in files),
            "elapsed_seconds": round(time.monotonic() - start, 2)}
