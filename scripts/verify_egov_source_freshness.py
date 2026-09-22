#!/usr/bin/env python3
"""Read-only freshness check for e-Gov law sources used by kaigo-rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

TARGETS = [
    ("ordinance37", "ordinance37-meta.json"),
    ("care_insurance_act", "care-insurance-act-meta.json"),
]

REVISION_FIELDS = [
    "law_revision_id",
    "law_title",
    "amendment_law_id",
    "amendment_law_num",
    "amendment_promulgate_date",
    "amendment_enforcement_date",
    "amendment_scheduled_enforcement_date",
    "current_revision_status",
    "repeal_status",
    "mission",
    "updated",
]


def fetch(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-source-drift-monitor/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def revisions_from(payload):
    if isinstance(payload, dict):
        revisions = payload.get("revisions")
        if isinstance(revisions, list):
            return revisions
        result = payload.get("result")
        if isinstance(result, dict) and isinstance(result.get("revisions"), list):
            return result["revisions"]
    return []


def current_revision(revisions: list[dict]) -> dict:
    for revision in revisions:
        if revision.get("current_revision_status") == "CurrentEnforced":
            return {key: revision.get(key) for key in REVISION_FIELDS if key in revision}
    if revisions:
        revision = revisions[0]
        return {key: revision.get(key) for key in REVISION_FIELDS if key in revision}
    return {}


def check_target(name: str, meta_file: str) -> dict:
    meta = json.loads((DATA / meta_file).read_text(encoding="utf-8"))
    xml_url = meta["source_api_v1"]
    revisions_url = meta["source_revisions_v2"]

    xml_bytes = fetch(xml_url)
    revisions_bytes = fetch(revisions_url)
    xml_sha = hashlib.sha256(xml_bytes).hexdigest()
    revisions_sha = hashlib.sha256(revisions_bytes).hexdigest()

    revisions_payload = json.loads(revisions_bytes.decode("utf-8"))
    revisions = revisions_from(revisions_payload)
    live_current = current_revision(revisions)

    differences = []
    if xml_sha != meta.get("xml_sha256"):
        differences.append({
            "field": "xml_sha256",
            "expected": meta.get("xml_sha256"),
            "observed": xml_sha,
        })
    if revisions_sha != meta.get("revision_response_sha256"):
        differences.append({
            "field": "revision_response_sha256",
            "expected": meta.get("revision_response_sha256"),
            "observed": revisions_sha,
        })
    if len(revisions) != meta.get("revision_count"):
        differences.append({
            "field": "revision_count",
            "expected": meta.get("revision_count"),
            "observed": len(revisions),
        })

    stored_current = meta.get("current_revision") or {}
    if live_current != stored_current:
        differences.append({
            "field": "current_revision",
            "expected": stored_current,
            "observed": live_current,
        })

    return {
        "name": name,
        "law_id": meta.get("law_id"),
        "xml_url": xml_url,
        "revisions_url": revisions_url,
        "observed_xml_sha256": xml_sha,
        "observed_revision_response_sha256": revisions_sha,
        "observed_revision_count": len(revisions),
        "observed_current_revision": live_current,
        "result": "PASS" if not differences else "SOURCE_DRIFT_DETECTED",
        "differences": differences,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", help="Optional path for the JSON verification report")
    args = parser.parse_args()

    checks = [check_target(name, meta_file) for name, meta_file in TARGETS]
    result = "PASS" if all(check["result"] == "PASS" for check in checks) else "FAIL"

    report = {
        "format_version": 1,
        "verification_kind": "EGOV_LIVE_SOURCE_FRESHNESS",
        "result": result,
        "checks": checks,
        "safety": {
            "read_only": True,
            "updates_generated_data": False,
            "promotes_review_status": False,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")

    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")

    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
