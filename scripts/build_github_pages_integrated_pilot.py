#!/usr/bin/env python3
"""Combine private handbook and DB-search experiments, without deploying.

This is a partial site, not a release candidate. Its search data includes
currently published but not fully reviewed material; it must remain private.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_github_pages_handbook_all_pilot as handbook

ROOT = Path(__file__).resolve().parents[1]
STATIC_FILES = {
    "index.html", "app.mjs", "search.mjs", "rank-core.mjs", "style.css",
    "services.json", "global.json", "qa.html", "qa-app.mjs", "qa-projection.mjs",
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


def integrate(handbook_dir: Path, search_dir: Path) -> dict:
    out = _outside_source(handbook_dir)
    source = _outside_source(search_dir)
    if out == source or out in source.parents or source in out.parents:
        raise RuntimeError("Pilot directories must be separate")
    if not (out / "index.html").is_file() or not (out / "handbook").is_dir():
        raise RuntimeError("Incomplete handbook experiment")
    entries = list(source.iterdir())
    if any(p.is_symlink() or not p.is_file() or
           (p.name not in STATIC_FILES and not re.fullmatch(r"service-[a-z0-9-]+\.json", p.name))
           for p in entries):
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
    expected = STATIC_FILES | set(service_files)
    actual = {p.name for p in entries}
    if actual != expected:
        raise RuntimeError("Unexpected file or link in search experiment")
    existing = list(out.rglob("*"))
    if any(p.is_symlink() for p in existing):
        raise RuntimeError("Symbolic link in handbook experiment")
    scanned = [p for p in existing if p.is_file()] + entries
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
    for name in sorted(expected):
        shutil.copyfile(source / name, target / name)
    root_page = out / "index.html"
    text = root_page.read_text(encoding="utf-8")
    if text.count("</article>") != 1:
        raise RuntimeError("Unexpected handbook index structure")
    root_page.write_text(text.replace("</article>", '<p><a href="./databases/search/index.html">制度DB横断検索を試す</a> / <a href="./databases/search/qa.html">国Q&Aを探す</a></p></article>'), encoding="utf-8")
    search_page = target / "index.html"
    text = search_page.read_text(encoding="utf-8")
    if text.count("<h1>") != 1:
        raise RuntimeError("Unexpected search index structure")
    search_page.write_text(text.replace("<h1>", '<p><a href="../../index.html">サービス別手引へ</a> / <a href="./qa.html">国Q&Aを探す</a></p><h1>'), encoding="utf-8")
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
        result = integrate(Path(handbook_result["directory"]), search_dir)
        result.update({"handbook_services": handbook_result["services"],
                       "handbook_chapters": handbook_result["chapters"]})
        return result
    except BaseException:
        shutil.rmtree(handbook_result["directory"], ignore_errors=True)
        raise
    finally:
        if search_dir:
            shutil.rmtree(search_dir, ignore_errors=True)


if __name__ == "__main__":
    print(json.dumps(build(), ensure_ascii=False))
