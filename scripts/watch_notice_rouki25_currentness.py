#!/usr/bin/env python3
"""Read-only watch for new evidence that could affect 老企第25号 currentness.

This watcher is intentionally narrow. It does not prove that no amendment exists.
It detects configured signals that require the currentness ledger to be reviewed.
"""

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
CONFIG_PATH = ROOT / "data" / "notice-rouki25-watch-config.json"


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
            text = " ".join("".join(self._text).split())
            self.links.append({"href": self._href, "text": text})
            self._href = None
            self._text = []


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-rouki25-currentness-watch/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def html_text(data: bytes) -> str:
    raw = data.decode("utf-8", errors="replace")
    return " ".join(re.sub(r"<[^>]+>", " ", raw).split())


def anchors(page_url: str, data: bytes) -> list[dict[str, str]]:
    parser = AnchorParser()
    parser.feed(data.decode("utf-8", errors="replace"))
    parser.close()
    result = []
    for row in parser.links:
        result.append(
            {
                "url": urllib.parse.urljoin(page_url, row["href"]),
                "text": row["text"],
            }
        )
    return result


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


def extract_text(url: str, data: bytes) -> str:
    if data.startswith(b"%PDF"):
        return pdf_text(data)
    return html_text(data)


def matching_terms(text: str, terms: list[str]) -> list[str]:
    compact = re.sub(r"\s+", "", text)
    return [term for term in terms if re.sub(r"\s+", "", term) in compact]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for JSON report")
    args = parser.parse_args()

    config = load_json(CONFIG_PATH)
    ledger_path = ROOT / config["baseline"]["currentness_ledger"]
    ledger = load_json(ledger_path)
    terms = list(config["targets"]["exact_terms"])
    pages = config["targets"]["official_pages"]
    baseline_volume = int(config["baseline"]["latest_confirmed_kaigo_info_volume"])

    report: dict = {
        "format_version": 1,
        "verification_kind": "ROUKI25_CURRENTNESS_WATCH",
        "baseline": config["baseline"],
        "result": "PASS",
        "source_errors": [],
        "pinned_pdf_checks": [],
        "new_kaigo_info_entries": [],
        "page_term_checks": [],
        "law_database_amendment_lists": [],
        "review_triggers": [],
        "limitations": [
            "PASS means only that configured watch signals were not detected.",
            "The watcher does not prove completeness of MHLW indexes or absence of unindexed amendments.",
            "HUMAN_VERIFIED and VERIFIED_CURRENT are never changed by this script.",
        ],
    }

    # Detect silent replacement of official PDFs already pinned by the currentness ledger.
    pinned = [
        {
            "label": "R6 redline",
            "url": ledger["checkpoint"]["pdf_url"],
            "expected_sha256": ledger["checkpoint"]["pdf_sha256"],
        },
        {
            "label": "secondary reference",
            "url": ledger["secondary_reference_context"]["url"],
            "expected_sha256": ledger["secondary_reference_context"]["sha256"],
        },
    ]
    for item in pinned:
        try:
            data = fetch(item["url"])
            observed = sha256(data)
            row = {**item, "observed_sha256": observed, "match": observed == item["expected_sha256"]}
            report["pinned_pdf_checks"].append(row)
            if not row["match"]:
                report["review_triggers"].append(
                    {
                        "kind": "PINNED_PDF_HASH_CHANGED",
                        "label": item["label"],
                        "url": item["url"],
                        "expected_sha256": item["expected_sha256"],
                        "observed_sha256": observed,
                    }
                )
        except Exception as exc:
            report["source_errors"].append(
                {"source": item["url"], "stage": "pinned_pdf_fetch", "error": str(exc)}
            )

    # Scan newly listed 介護保険最新情報 items after the last volume checked by the ledger.
    try:
        index_bytes = fetch(pages["kaigo_latest_info"])
        index_links = anchors(pages["kaigo_latest_info"], index_bytes)
        by_volume: dict[int, dict[str, str]] = {}
        for row in index_links:
            match = re.search(r"(?:介護保険最新情報)?\s*[Vv]ol\.?\s*(\d+)", row["text"], re.I)
            if not match:
                continue
            volume = int(match.group(1))
            if volume > baseline_volume and volume not in by_volume:
                by_volume[volume] = row

        for volume in sorted(by_volume):
            row = by_volume[volume]
            entry = {
                "volume": volume,
                "title": row["text"],
                "url": row["url"],
                "term_matches_in_title": matching_terms(row["text"], terms),
                "term_matches_in_body": [],
                "body_scan": "NOT_RUN",
            }
            try:
                body = fetch(row["url"])
                text = extract_text(row["url"], body)
                entry["term_matches_in_body"] = matching_terms(text, terms)
                entry["body_scan"] = "OK"
            except Exception as exc:
                entry["body_scan"] = "ERROR"
                entry["body_error"] = str(exc)
                report["source_errors"].append(
                    {
                        "source": row["url"],
                        "stage": f"kaigo_info_vol_{volume}_body_scan",
                        "error": str(exc),
                    }
                )
            report["new_kaigo_info_entries"].append(entry)

            matches = sorted(set(entry["term_matches_in_title"] + entry["term_matches_in_body"]))
            if matches:
                report["review_triggers"].append(
                    {
                        "kind": "TARGET_TERM_IN_NEW_KAIGO_INFO",
                        "volume": volume,
                        "url": row["url"],
                        "title": row["text"],
                        "matches": matches,
                    }
                )
    except Exception as exc:
        report["source_errors"].append(
            {"source": pages["kaigo_latest_info"], "stage": "kaigo_info_index_scan", "error": str(exc)}
        )

    # Watch official pages where a direct amendment could be newly listed.
    for key in ("r8_reform_notifications", "notification_new_index"):
        url = pages[key]
        try:
            data = fetch(url)
            text = extract_text(url, data)
            matches = matching_terms(text, terms)
            report["page_term_checks"].append(
                {"page": key, "url": url, "matches": matches}
            )
            if matches:
                report["review_triggers"].append(
                    {
                        "kind": "TARGET_TERM_ON_WATCHED_OFFICIAL_PAGE",
                        "page": key,
                        "url": url,
                        "matches": matches,
                    }
                )
        except Exception as exc:
            report["source_errors"].append(
                {"source": url, "stage": f"{key}_scan", "error": str(exc)}
            )

    # Scan the latest MHLW law-database notification amendment list(s).
    # This is supporting-only because the database itself is documented as covering the ministry's "主な" notifications.
    update_url = pages.get("law_database_update")
    if update_url:
        try:
            update_bytes = fetch(update_url)
            update_links = anchors(update_url, update_bytes)
            amendment_urls = sorted(
                {
                    row["url"]
                    for row in update_links
                    if re.search(r"/hourei/new/update/kai\\d+t\\.pdf$", row["url"])
                }
            )
            if not amendment_urls:
                raise RuntimeError("no notification amendment-list PDF link found on MHLW update page")
            for amendment_url in amendment_urls:
                entry = {
                    "url": amendment_url,
                    "matches": [],
                    "scan": "NOT_RUN",
                    "scope_limit": "MHLW notification database covers 主な notifications; a clean scan is supporting-only.",
                }
                try:
                    body = fetch(amendment_url)
                    text = extract_text(amendment_url, body)
                    entry["matches"] = matching_terms(text, terms)
                    entry["scan"] = "OK"
                except Exception as exc:
                    entry["scan"] = "ERROR"
                    entry["error"] = str(exc)
                    report["source_errors"].append(
                        {
                            "source": amendment_url,
                            "stage": "law_database_amendment_list_scan",
                            "error": str(exc),
                        }
                    )
                report["law_database_amendment_lists"].append(entry)
                if entry["matches"]:
                    report["review_triggers"].append(
                        {
                            "kind": "TARGET_TERM_IN_LAW_DATABASE_AMENDMENT_LIST",
                            "url": amendment_url,
                            "matches": entry["matches"],
                        }
                    )
        except Exception as exc:
            report["source_errors"].append(
                {"source": update_url, "stage": "law_database_update_scan", "error": str(exc)}
            )

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
