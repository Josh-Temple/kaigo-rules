#!/usr/bin/env python3
"""Read-only watcher for new 老企第36号 evidence after the independent audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data" / "fee-guidance-currentness-watch-config.json"


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href:
            self._href = href
            self._text = []

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "a" and self._href is not None:
            self.links.append({
                "href": self._href,
                "text": " ".join("".join(self._text).split()),
            })
            self._href = None
            self._text = []


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-rouki36-currentness-watch/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_links(page_url: str, data: bytes) -> list[dict[str, str]]:
    parser = AnchorParser()
    parser.feed(data.decode("utf-8", errors="replace"))
    parser.close()
    return [
        {
            "url": urllib.parse.urljoin(page_url, row["href"]),
            "text": row["text"],
        }
        for row in parser.links
    ]


def pdf_text(data: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
        handle.write(data)
        handle.flush()
        completed = subprocess.run(
            ["pdftotext", "-layout", handle.name, "-"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    if completed.returncode != 0:
        raise RuntimeError(
            "pdftotext failed: " + completed.stderr.decode("utf-8", errors="replace")[:500]
        )
    return completed.stdout.decode("utf-8", errors="replace")


def extract_text(data: bytes) -> str:
    if data.startswith(b"%PDF"):
        return pdf_text(data)
    raw = data.decode("utf-8", errors="replace")
    return re.sub(r"<[^>]+>", " ", raw)


def matches(text: str, terms: list[str]) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    return [term for term in terms if re.sub(r"\s+", "", term) in compact]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional JSON report path")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    baseline_volume = int(config["baseline"]["latest_confirmed_kaigo_info_volume"])
    terms = list(config["targets"]["exact_terms"])
    index_url = config["targets"]["kaigo_latest_info"]

    report = {
        "format_version": 1,
        "verification_kind": "ROUKI36_CURRENTNESS_WATCH",
        "baseline": config["baseline"],
        "result": "PASS",
        "pinned_source_checks": [],
        "new_kaigo_info_entries": [],
        "review_triggers": [],
        "source_errors": [],
        "limitations": [
            "PASS means only that configured watch signals were not detected.",
            "The MHLW index is not treated as a complete amendment register.",
            "This watcher never changes HUMAN_VERIFIED, VERIFIED_CURRENT, or candidate text.",
        ],
    }

    for source in config["pinned_sources"]:
        try:
            data = fetch(source["url"])
            observed = sha256(data)
            row = {
                "source_id": source["source_id"],
                "url": source["url"],
                "expected_sha256": source["sha256"],
                "observed_sha256": observed,
                "match": observed == source["sha256"],
            }
            report["pinned_source_checks"].append(row)
            if not row["match"]:
                report["review_triggers"].append({
                    "kind": "PINNED_PDF_HASH_CHANGED",
                    **row,
                })
        except Exception as exc:
            report["source_errors"].append({
                "source": source["url"],
                "stage": "pinned_source_fetch",
                "error": str(exc),
            })

    try:
        index_bytes = fetch(index_url)
        links = parse_links(index_url, index_bytes)
        new_by_volume: dict[int, dict[str, str]] = {}
        for row in links:
            match = re.search(r"(?:介護保険最新情報)?\s*[Vv]ol\.?\s*(\d+)", row["text"], re.I)
            if not match:
                continue
            volume = int(match.group(1))
            if volume > baseline_volume and volume not in new_by_volume:
                new_by_volume[volume] = row

        for volume in sorted(new_by_volume):
            row = new_by_volume[volume]
            entry = {
                "volume": volume,
                "title": row["text"],
                "url": row["url"],
                "title_matches": matches(row["text"], terms),
                "body_matches": [],
                "body_scan": "NOT_RUN",
            }
            try:
                body = fetch(row["url"])
                text = extract_text(body)
                entry["body_matches"] = matches(text, terms)
                entry["body_scan"] = "OK"
            except Exception as exc:
                entry["body_scan"] = "ERROR"
                entry["body_error"] = str(exc)
                report["source_errors"].append({
                    "source": row["url"],
                    "stage": f"kaigo_info_vol_{volume}_body_scan",
                    "error": str(exc),
                })
            report["new_kaigo_info_entries"].append(entry)

            found = sorted(set(entry["title_matches"] + entry["body_matches"]))
            if found:
                report["review_triggers"].append({
                    "kind": "TARGET_TERM_IN_NEW_KAIGO_INFO",
                    "volume": volume,
                    "url": row["url"],
                    "title": row["text"],
                    "matches": found,
                })
    except Exception as exc:
        report["source_errors"].append({
            "source": index_url,
            "stage": "kaigo_info_index_scan",
            "error": str(exc),
        })

    if report["source_errors"]:
        report["result"] = "SOURCE_ACCESS_OR_PARSE_ERROR"
    elif report["review_triggers"]:
        report["result"] = "REVIEW_REQUIRED"

    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
