#!/usr/bin/env python3
"""Verify bounded currentness for day-service unit-price data.

This verifier composes the existing independently pinned live-data reparse with
source-identity markers from the official MHLW current display.  It supports
only the exact dayservice::unit_price_regional_classification candidate and
does not promote human review or family-wide currentness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

import verify_unit_price_independent as independent

ROOT = Path(__file__).resolve().parents[1]
CURRENT_URL = "https://www.mhlw.go.jp/web/t_doc?dataId=82ab4582&dataType=0"
BOUNDED_IDENTITY = "dayservice::unit_price_regional_classification"

MARKERS = {
    "title": ("厚生労働大臣が定める一単位の単価",),
    "notice_identity": ("厚生労働省告示第九十三号", "厚生労働省告示第93号"),
    "effective_reference_date": ("令和六年四月一日", "令和6年4月1日"),
    "service_identity": ("通所介護",),
}


class TextCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        value = independent.clean(data)
        if value:
            self.parts.append(value)


def marker_check(html: str) -> dict:
    parser = TextCollector()
    parser.feed(html)
    parser.close()
    visible = independent.clean(" ".join(parser.parts))
    observed: dict[str, str] = {}
    missing: list[str] = []
    for key, alternatives in MARKERS.items():
        match = next((value for value in alternatives if value in visible), None)
        if match is None:
            missing.append(key)
        else:
            observed[key] = match
    return {"observed_markers": observed, "missing_markers": missing}


def compare() -> dict:
    independent_report = independent.compare()
    index_payload, index_html = independent.fetch(CURRENT_URL)
    identity = marker_check(index_html)

    pinned_hashes_match_live = (
        independent_report.get("result") == "PASS"
        and not (independent_report.get("differences") or {}).get("metadata")
    )
    source_identity_observed = not identity["missing_markers"]
    result = "PASS" if pinned_hashes_match_live and source_identity_observed else "FAIL"

    return {
        "format_version": 1,
        "verification_kind": "BOUNDED_CURRENT_OFFICIAL_DISPLAY_REPARSE",
        "bounded_identity": BOUNDED_IDENTITY,
        "official_current_url": CURRENT_URL,
        "official_current_page_sha256": hashlib.sha256(index_payload).hexdigest(),
        "source_identity": identity,
        "independent_reparse_result": independent_report.get("result"),
        "live_page_sha256": independent_report.get("source_sha256"),
        "differences": independent_report.get("differences"),
        "result": result,
        "currentness_evidence": {
            "official_current_display_identity_observed": source_identity_observed,
            "canonical_source_hashes_match_current_live_source": pinned_hashes_match_live,
            "supports_bounded_currentness": result == "PASS",
        },
        "safety": {
            "promotes_human_review": False,
            "promotes_global_family_currentness": False,
            "supports_bounded_currentness": result == "PASS",
            "bounded_scope": BOUNDED_IDENTITY,
            "note": (
                "PASS is limited to the exact dayservice unit-price source slice on the "
                "official MHLW current display. It does not establish human review, "
                "cross-layer relation semantics, or family-wide currentness."
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for the JSON verification report")
    args = parser.parse_args()

    report = compare()
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")

    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
