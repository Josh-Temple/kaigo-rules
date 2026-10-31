#!/usr/bin/env python3
"""Combine private handbook and DB-search experiments, without deploying.

This is a partial site, not a release candidate. Its search data includes
currently published but not fully reviewed material; it must remain private.
"""
from __future__ import annotations

import hashlib
import gzip
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_github_pages_handbook_all_pilot as handbook
import build_github_pages_qa_details_pilot as qa_details
import build_github_pages_legal_details_pilot as legal_details
import localize_github_pages_links_pilot as navigation
import build_github_pages_information_pilot as information

ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = {
    "index.html", "app.mjs", "search.mjs", "rank-core.mjs", "style.css",
    "services.json", "global.json", "global.json.gz", "load-json.mjs", "qa.html", "qa-app.mjs", "qa-projection.mjs",
    "qa-core.mjs", "qa-options.json",
}
GROUPS = {"law", "ordinance", "unitPrice", "delegated", "notice", "qa"}
ROW_FIELDS = {"id", "title", "href", "excerpt", "excerptField", "sourceUrl", "serviceId",
              "serviceLabel", "regionClass", "unitPrice", "checkedAt", "statusText", "fields",
              "serviceCode", "scope", "currentServiceScope", "issuedSource", "number"}
SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\b(?:ghp_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})\b"),
    re.compile(rb"\bsk-(?:proj-|live-)?[A-Za-z0-9_-]{30,}\b"),
    re.compile(rb"\bAKIA[A-Z0-9]{16}\b"),
    re.compile(rb"\bAIza[0-9A-Za-z_-]{35}\b"),
]


def _outside_source(path: Path) -> Path:
    resolved = path.resolve(strict=True)
    temp_root = Path(tempfile.gettempdir()).resolve()
    if resolved == ROOT or ROOT in resolved.parents:
        raise RuntimeError("Pilot output cannot be inside the repository")
    if resolved != temp_root and temp_root not in resolved.parents:
        raise RuntimeError("Pilot output must stay in the temporary directory")
    if not resolved.is_dir() or path.is_symlink():
        raise RuntimeError("Invalid pilot directory")
    return resolved


def integrate(handbook_dir: Path, search_dir: Path, *, with_information: bool = False) -> dict:
    out = _outside_source(handbook_dir)
    source = _outside_source(search_dir)
    if out == source or out in source.parents or source in out.parents:
        raise RuntimeError("Pilot directories must be separate")
    if not (out / "index.html").is_file() or not (out / "handbook").is_dir():
        raise RuntimeError("Incomplete handbook experiment")
    entries = list(source.iterdir())
    detail_dirs = {p.name for p in entries if p.is_dir()}
    if detail_dirs - {"qa-details", "legal"} or any(p.is_symlink() for p in source.rglob("*")):
        raise RuntimeError("Unexpected file or link in search experiment")
    if any(not p.is_dir() and (not p.is_file() or
           (p.name not in STATIC_FILES and p.name not in {"styles.css", "print.js"}
            and not re.fullmatch(r"service-[a-z0-9-]+\.json", p.name))) for p in entries):
        raise RuntimeError("Unexpected file or link in search experiment")
    services = json.loads((source / "services.json").read_text(encoding="utf-8"))
    if not isinstance(services, list) or not services:
        raise RuntimeError("Missing search service manifest")
    service_files = []
    for item in services:
        sid, file = item.get("id"), item.get("file")
        if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9-]+", sid) or file != f"service-{sid}.json":
            raise RuntimeError("Invalid search service manifest")
        service_files.append(file)
    if len(set(service_files)) != len(service_files):
        raise RuntimeError("Duplicate search service files")
    qa_options = json.loads((source / "qa-options.json").read_text(encoding="utf-8"))
    if not isinstance(qa_options, list) or any(
        not isinstance(item, list) or len(item) != 2 or
        not all(isinstance(value, str) for value in item) for item in qa_options
    ):
        raise RuntimeError("Invalid Q&A service options")
    expected = STATIC_FILES | set(service_files) | ({"styles.css", "print.js"} if detail_dirs else set())
    actual = {p.name for p in entries if p.is_file()}
    if actual != expected:
        raise RuntimeError("Unexpected file or link in search experiment")
    raw_global = (source / "global.json").read_bytes()
    try:
        with gzip.open(source / "global.json.gz", "rb") as stream:
            inflated = stream.read(len(raw_global) + 1)
    except (OSError, EOFError) as error:
        raise RuntimeError("Invalid compressed search dataset") from error
    if inflated != raw_global:
        raise RuntimeError("Compressed search dataset does not match the scanned original")
    nested_expected = set()
    if "qa-details" in detail_dirs:
        rows = json.loads((source / "global.json").read_text(encoding="utf-8"))["qa"]
        ids = {qa_details.safe_id(row["id"]) for row in rows}
        direct = json.loads((ROOT / "data/qa-direct-evidence.json").read_text(encoding="utf-8"))
        for alias, item in direct.items():
            if (item.get("corpus_id") or alias) in ids:
                ids.add(qa_details.safe_id(alias))
        for identifier in ids:
            for name in ("index.html", "reader.html"):
                nested_expected.add(f"qa-details/{identifier}/{name}")
    if "legal" in detail_dirs:
        routes, _ = legal_details.collect_routes(source)
        nested_expected.update(legal_details.local_path(key) for key in routes)
    nested_actual = {str(p.relative_to(source)) for name in detail_dirs
                     for p in (source / name).rglob("*") if p.is_file()}
    if nested_actual != nested_expected:
        raise RuntimeError("Missing or unexpected detail page")
    expected_dirs = set()
    for name in nested_expected:
        parent = Path(name).parent
        while str(parent) != ".":
            expected_dirs.add(str(parent))
            parent = parent.parent
    actual_dirs = {str(p.relative_to(source)) for p in source.rglob("*") if p.is_dir()}
    if actual_dirs != expected_dirs:
        raise RuntimeError("Unexpected detail directory")
    for name, marker, directory in [
        ("qa.html", "kaigo-qa-local-details", "qa-details"),
        ("index.html", "kaigo-legal-local-details", "legal"),
    ]:
        count = (source / name).read_text(encoding="utf-8").count(marker)
        if count != (1 if directory in detail_dirs else 0):
            raise RuntimeError("Detail navigation does not match available pages")
    if detail_dirs:
        styles = (source / "styles.css").read_text(encoding="utf-8")
        expected_styles = handbook.pilot.STYLES + "\n" + (
            "." + qa_details.PRELINE + "{white-space:pre-line}\n" if "qa-details" in detail_dirs else ""
        )
        if styles != expected_styles or (source / "print.js").read_text(encoding="utf-8") != handbook.pilot.PRINT_JS:
            raise RuntimeError("Unexpected detail styles or script")
    existing = list(out.rglob("*"))
    if any(p.is_symlink() for p in existing):
        raise RuntimeError("Symbolic link in handbook experiment")
    search_files = [source / name for name in expected] + [source / name for name in nested_expected]
    scanned = [p for p in existing if p.is_file()] + search_files
    for file in scanned:
        data = file.read_bytes()
        if any(pattern.search(data) for pattern in SECRET_PATTERNS):
            raise RuntimeError("Secret-like material detected in private pilot")
    for name in ["global.json", *service_files]:
        groups = json.loads((source / name).read_text(encoding="utf-8"))
        if not isinstance(groups, dict) or set(groups) != GROUPS:
            raise RuntimeError("Unexpected search dataset groups")
        for rows in groups.values():
            if not isinstance(rows, list):
                raise RuntimeError("Unexpected search rows")
            for row in rows:
                if not isinstance(row, dict) or not set(row).issubset(ROW_FIELDS):
                    raise RuntimeError("Unexpected search record field")
                href = row.get("href")
                if not isinstance(href, str) or not href.startswith("/") or href.startswith("//") or "\\" in href:
                    raise RuntimeError("Invalid search destination")
                if not isinstance(row.get("fields"), list) or any(
                    not isinstance(field, dict) or set(field) != {"value", "weight"}
                    or not isinstance(field["value"], str) or not isinstance(field["weight"], (int, float))
                    for field in row["fields"]
                ):
                    raise RuntimeError("Unexpected search field structure")
    target = out / "databases/search"
    if target.exists():
        raise RuntimeError("Integrated search directory already exists")
    target.mkdir(parents=True)
    for name in sorted(expected | nested_expected):
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, destination)
    # The original prebuild tests exercise integrate() before .next exists.
    # Only post-build pilots opt into extracting validated prerendered pages.
    information_report = information.add_pages(out) if with_information else {
        "pages": 0, "bytes": 0, "routes": [],
    }
    # The information pages did not exist during the first source-data scan.
    # Scan every newly generated page before reporting any private safety pass.
    if with_information:
        for name in information.PAGES:
            added = out / name / "index.html"
            if not added.is_file() or added.is_symlink():
                raise RuntimeError("Missing or symbolic-link reader page")
            data = added.read_bytes()
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                raise RuntimeError("Secret-like material in reader information page")
            scanned.append(added)
    root_page = out / "index.html"
    text = root_page.read_text(encoding="utf-8")
    if text.count("</article>") != 1:
        raise RuntimeError("Unexpected handbook index structure")
    information_links = (
        '<p><a href="./start/index.html">はじめての方へ</a> / '
        '<a href="./overview/index.html">制度の全体像</a> / '
        '<a href="./guide/index.html">使い方ガイド</a> / '
        '<a href="./sources/index.html">公式資料と出典</a> / '
        '<a href="./handbook-sources/index.html">手引の出典</a> / '
        '<a href="./fees/guidance/index.html">報酬案内</a></p>'
        if with_information else ""
    )
    root_page.write_text(text.replace("</article>", '<p><a href="./databases/search/index.html">制度DB横断検索を試す</a> / <a href="./databases/search/qa.html">国Q&Aを探す</a></p>' + information_links + '</article>'), encoding="utf-8")
    search_page = target / "index.html"
    text = search_page.read_text(encoding="utf-8")
    if text.count("<h1>") != 1:
        raise RuntimeError("Unexpected search index structure")
    search_page.write_text(text.replace("<h1>", '<p><a href="../../index.html">サービス別手引へ</a> / <a href="./qa.html">国Q&Aを探す</a></p><h1>'), encoding="utf-8")
    navigation_report = navigation.localize(out)
    all_paths = list(out.rglob("*"))
    if any(p.is_symlink() for p in all_paths):
        raise RuntimeError("Symbolic link in integrated output")
    files = [p for p in all_paths if p.is_file()]
    by_suffix = {}
    hashes = {}
    duplicate_files = 0
    duplicate_bytes = 0
    for file in files:
        suffix = file.suffix.lower() or "(none)"
        by_suffix.setdefault(suffix, {"files": 0, "bytes": 0})
        by_suffix[suffix]["files"] += 1
        by_suffix[suffix]["bytes"] += file.stat().st_size
        digest = hashlib.sha256(file.read_bytes()).hexdigest()
        if digest in hashes:
            duplicate_files += 1
            duplicate_bytes += file.stat().st_size
        else:
            hashes[digest] = file
    largest = sorted(
        ({"path": str(file.relative_to(out)), "bytes": file.stat().st_size} for file in files),
        key=lambda item: item["bytes"], reverse=True,
    )[:10]
    return {"directory": str(out), "files": len(files), "bytes": sum(p.stat().st_size for p in files),
            "navigation": navigation_report, "information_pages": information_report,
            "by_suffix": by_suffix, "largest": largest,
            "identical_duplicate_files": duplicate_files, "identical_duplicate_bytes": duplicate_bytes,
            "secret_scan_files": len(scanned), "search_services": len(service_files)}


def build() -> dict:
    handbook_result = handbook.build()
    search_dir = None
    try:
        run = subprocess.run(
            ["node", "--import", "./experiments/github-pages-db/register.mjs",
             "experiments/github-pages-db/build.mjs"],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=180,
        )
        search_dir = Path(json.loads(run.stdout)["dir"])
        result = integrate(Path(handbook_result["directory"]), search_dir, with_information=True)
        result.update({"handbook_services": handbook_result["services"],
                       "handbook_chapters": handbook_result["chapters"]})
        return result
    except BaseException:
        shutil.rmtree(handbook_result["directory"], ignore_errors=True)
        raise
    finally:
        if search_dir:
            shutil.rmtree(search_dir, ignore_errors=True)


def build_with_details() -> dict:
    """Build a larger *private* partial site from the existing Next.js app."""
    handbook_result = handbook.build()
    search_dir = None
    child = None
    try:
        run = subprocess.run(
            ["node", "--import", "./experiments/github-pages-db/register.mjs",
             "experiments/github-pages-db/build.mjs"],
            cwd=ROOT, check=True, capture_output=True, text=True, timeout=180,
        )
        search_dir = Path(json.loads(run.stdout)["dir"])
        corpus = json.loads((ROOT / "data/qa-corpus.json").read_text(encoding="utf-8"))
        direct = json.loads((ROOT / "data/qa-direct-evidence.json").read_text(encoding="utf-8"))
        # QA's original related-handbook links must point to the actual
        # generated service index rather than accidentally resolving to the
        # database search index in the combined static directory.
        service_anchors = {}
        for page in (Path(handbook_result["directory"]) / "services").glob("*/index.html"):
            service_id = page.parent.name
            if not re.fullmatch(r"[a-z0-9-]+", service_id):
                raise RuntimeError("Unsafe generated handbook service ID")
            anchors = set(re.findall(r'\bid="([A-Za-z0-9_-]+)"', page.read_text(encoding="utf-8")))
            if not anchors:
                raise RuntimeError("Missing generated handbook navigation anchors")
            service_anchors[service_id] = anchors
        if len(service_anchors) != handbook_result["services"]:
            raise RuntimeError("Incomplete generated service index navigation")
        child, base = qa_details.start_next(pilot_optimized=True)
        qa_result = qa_details.add_details(
            search_dir, base, corpus, direct, max_seconds=480,
            local_service_anchors=service_anchors,
        )
        # Serve legal routes from a fresh validated Next.js process. The shared
        # process had already rendered 7,392 Q&A variants before legal extraction
        # slowed down and hit its 360-second budget (run 41198085626).
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        child = None
        child, base = qa_details.start_next(pilot_optimized=True)
        print("Private legal extraction: fresh local Next.js process started", flush=True)
        legal_result = legal_details.add_details(search_dir, base, max_seconds=360)
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        child = None
        result = integrate(Path(handbook_result["directory"]), search_dir, with_information=True)
        result.update({"handbook_services": handbook_result["services"],
                       "handbook_chapters": handbook_result["chapters"],
                       "qa_details": qa_result, "legal_details": legal_result})
        return result
    except BaseException:
        shutil.rmtree(handbook_result["directory"], ignore_errors=True)
        raise
    finally:
        if child and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=5)
        if search_dir:
            shutil.rmtree(search_dir, ignore_errors=True)


if __name__ == "__main__":
    if sys.argv[1:] not in ([], ["--with-details"]):
        raise SystemExit("Use --with-details for the larger unpublished experiment")
    result = build_with_details() if sys.argv[1:] else build()
    print(json.dumps(result, ensure_ascii=False))
