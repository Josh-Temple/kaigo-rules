#!/usr/bin/env python3
"""Independently re-fetch official sources referenced by a standards-interpretation staging dataset.

This bounded check proves source availability/extractability and a service anchor.
It does not prove item-body equality, currentness, omitted-text completeness, or
publication readiness.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "kaigo-rules-standards-interpretation-source-inventory/1.0"


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "rt", "rp"}:
            self.suppressed += 1
        elif tag.lower() in {"br", "div", "li", "p", "section", "table", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "rt", "rp"} and self.suppressed:
            self.suppressed -= 1
        elif tag.lower() in {"div", "li", "p", "section", "table", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.suppressed:
            self.parts.append(data)


def normalize(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFKC", html.unescape(value)),
    ).strip()


def fetch(url: str, service_id: str) -> tuple[bytes, str | None]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": f"{USER_AGENT} {service_id}",
            "Cache-Control": "no-cache",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), response.headers.get_content_type()


def pdf_text(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as source:
        source.write(payload)
        source.flush()
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", source.name, "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    return normalize(result.stdout)


def html_text(payload: bytes) -> str:
    decoded = None
    for encoding in ("utf-8", "cp932", "shift_jis", "euc_jp"):
        try:
            decoded = payload.decode(encoding)
            break
        except UnicodeDecodeError:
            pass
    if decoded is None:
        decoded = payload.decode("utf-8", errors="replace")
    parser = VisibleText()
    parser.feed(decoded)
    parser.close()
    return normalize(" ".join(parser.parts))


def extract_text(payload: bytes, url: str, content_type: str | None) -> str:
    looks_pdf = url.lower().split("?", 1)[0].endswith(".pdf")
    if content_type == "application/pdf" or looks_pdf or payload.startswith(b"%PDF"):
        return pdf_text(payload)
    return html_text(payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--expected-items", type=int, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    service_id = args.service_id
    scope = json.loads(
        (ROOT / f"data/services/{service_id}/standards-interpretation-scope.json").read_text(
            encoding="utf-8"
        )
    )
    staging = json.loads(
        (ROOT / f"data/services/{service_id}/standards-interpretation-staging.json").read_text(
            encoding="utf-8"
        )
    )

    differences: list[str] = []
    config = scope.get("independent_source_inventory", {})
    if config.get("check_level") != "SOURCE_AVAILABILITY_AND_SERVICE_ANCHOR_ONLY":
        differences.append("scope independent source-inventory check level is missing or unexpected")
    if config.get("proves_item_body_match") is not False:
        differences.append("scope overclaims item-body verification")
    if config.get("proves_currentness") is not False:
        differences.append("scope overclaims currentness")
    if config.get("permits_publication") is not False:
        differences.append("scope source-inventory check must not permit publication")

    items = staging.get("items", [])
    declared_count = staging.get("item_count", staging.get("task_count"))
    if len(items) != args.expected_items or declared_count != args.expected_items:
        differences.append(
            f"staging count mismatch: declared={declared_count} observed={len(items)} "
            f"expected={args.expected_items}"
        )

    referenced_urls = sorted(
        {
            url
            for item in items
            for url in item.get("source_urls", [])
            if isinstance(url, str) and url
        }
    )
    manifest_rows = {
        row.get("url"): row
        for row in scope.get("source_manifest", [])
        if isinstance(row, dict) and row.get("url")
    }
    pinned_urls = set(manifest_rows)
    pinned_urls.update(
        url for url in scope.get("source_urls", []) if isinstance(url, str) and url
    )
    unpinned = sorted(set(referenced_urls) - pinned_urls)
    if unpinned:
        differences.append(f"staging references unpinned source URLs: {unpinned}")

    anchor = normalize(str(config.get("service_anchor", "")))
    if not anchor:
        differences.append("service anchor is missing")

    source_reports = []
    anchor_matches = 0
    for url in referenced_urls:
        source_report = {"url": url}
        try:
            payload, content_type = fetch(url, service_id)
            extracted = extract_text(payload, url, content_type)
            contains_anchor = bool(anchor and anchor in extracted)
            if contains_anchor:
                anchor_matches += 1
            source_report.update(
                {
                    "fetch": "PASS",
                    "content_type": content_type,
                    "bytes": len(payload),
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "extracted_chars": len(extracted),
                    "service_anchor_found": contains_anchor,
                }
            )
            if len(payload) < 100 or len(extracted) < 50:
                differences.append(f"source extraction unexpectedly small: {url}")
        except Exception as exc:
            required = manifest_rows.get(url, {}).get(
                "required_for_source_inventory", True
            )
            source_report.update(
                {
                    "fetch": "FAIL",
                    "error": str(exc),
                    "required_for_source_inventory": required,
                }
            )
            if required:
                differences.append(f"required source fetch/extraction failed: {url}: {exc}")
        if "required_for_source_inventory" not in source_report:
            source_report["required_for_source_inventory"] = manifest_rows.get(
                url, {}
            ).get("required_for_source_inventory", True)
        source_reports.append(source_report)

    if config.get("require_all_required_sources_fetchable") is True:
        failed = [
            row["url"]
            for row in source_reports
            if row.get("required_for_source_inventory") is True
            and row.get("fetch") != "PASS"
        ]
        if failed:
            differences.append(f"not all required sources were fetchable: {failed}")

    if config.get("require_anchor_in_at_least_one_source") is True and anchor_matches < 1:
        differences.append(f"service anchor was not found in any referenced source: {anchor}")

    result = "PASS_BOUNDED_SCOPE_ONLY" if not differences else "FAIL"
    report = {
        "audit_kind": "INDEPENDENT_STANDARDS_INTERPRETATION_SOURCE_INVENTORY",
        "audit_result": result,
        "service_id": service_id,
        "source_family": scope.get("source_family"),
        "check_level": config.get("check_level"),
        "coverage": {
            "expected_staging_items_or_tasks": args.expected_items,
            "observed_staging_items_or_tasks": len(items),
            "referenced_sources": len(referenced_urls),
            "sources_fetchable": sum(1 for row in source_reports if row.get("fetch") == "PASS"),
            "required_sources": sum(
                1
                for row in source_reports
                if row.get("required_for_source_inventory") is True
            ),
            "required_sources_fetchable": sum(
                1
                for row in source_reports
                if row.get("required_for_source_inventory") is True
                and row.get("fetch") == "PASS"
            ),
            "supplemental_sources_unavailable": sum(
                1
                for row in source_reports
                if row.get("required_for_source_inventory") is False
                and row.get("fetch") != "PASS"
            ),
            "sources_with_service_anchor": anchor_matches,
        },
        "sources": source_reports,
        "safety": {
            "item_body_match_proven": False,
            "currentness_promoted": False,
            "human_review_promoted": False,
            "omitted_text_reconstructed": False,
            "publication_permitted": False,
        },
        "differences": differences,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    return 0 if result == "PASS_BOUNDED_SCOPE_ONLY" else 1


if __name__ == "__main__":
    sys.exit(main())
