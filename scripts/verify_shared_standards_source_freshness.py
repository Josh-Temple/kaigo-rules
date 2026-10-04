#!/usr/bin/env python3
"""Read-only freshness check for shared ministerial-standards corpora."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/shared/standards"
FIELDS = [
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
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "kaigo-rules-shared-standards-freshness/1.0 "
                "(+https://github.com/Josh-Temple/kaigo-rules)"
            )
        },
    )
    retryable = {404, 408, 429, 500, 502, 503, 504}
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in retryable or attempt == 2:
                raise
            time.sleep(2**attempt)
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(2**attempt)
    raise RuntimeError(f"e-Gov fetch failed after retries: {url}: {last_error}")


def revisions(payload):
    rows = payload.get("revisions") if isinstance(payload, dict) else None
    if (
        rows is None
        and isinstance(payload, dict)
        and isinstance(payload.get("result"), dict)
    ):
        rows = payload["result"].get("revisions")
    return rows or []


def current(rows):
    row = next(
        (x for x in rows if x.get("current_revision_status") == "CurrentEnforced"),
        rows[0] if rows else {},
    )
    return {key: row.get(key) for key in FIELDS if key in row}


def check(entry):
    corpus_id = entry["corpus_id"]
    meta_path = BASE / corpus_id / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    xml_url = meta["source_api_v1"]
    revisions_url = meta["source_revisions_v2"]

    xml_bytes = fetch(xml_url)
    revisions_bytes = fetch(revisions_url)
    rows = revisions(json.loads(revisions_bytes.decode("utf-8")))

    observed_xml = hashlib.sha256(xml_bytes).hexdigest()
    observed_revision_response = hashlib.sha256(revisions_bytes).hexdigest()
    observed_current = current(rows)

    diffs = []
    for field, expected, observed in [
        ("xml_sha256", meta.get("xml_sha256"), observed_xml),
        (
            "revision_response_sha256",
            meta.get("revision_response_sha256"),
            observed_revision_response,
        ),
        ("revision_count", meta.get("revision_count"), len(rows)),
        ("current_revision", meta.get("current_revision"), observed_current),
    ]:
        if expected != observed:
            diffs.append(
                {"field": field, "expected": expected, "observed": observed}
            )

    current_enforced = (
        observed_current.get("current_revision_status") == "CurrentEnforced"
        and observed_current.get("repeal_status") in (None, "None")
    )
    result = "PASS" if not diffs else "SOURCE_DRIFT_DETECTED"

    return {
        "id": corpus_id,
        "law_id": entry["law_id"],
        "meta_path": str(meta_path.relative_to(ROOT)),
        "xml_url": xml_url,
        "revisions_url": revisions_url,
        "observed_xml_sha256": observed_xml,
        "observed_revision_response_sha256": observed_revision_response,
        "observed_revision_count": len(rows),
        "observed_current_revision": observed_current,
        "current_enforced": current_enforced,
        "source_level_currentness_evidence": (
            "MATCHED_CURRENT_ENFORCED_REVISION_AT_CHECK"
            if result == "PASS" and current_enforced
            else "NOT_ESTABLISHED"
        ),
        "result": result,
        "differences": diffs,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report")
    args = parser.parse_args()

    manifest = json.loads((BASE / "manifest.json").read_text(encoding="utf-8"))
    checks = []
    errors = []

    for entry in manifest["corpora"]:
        # ordinance37 is checked by verify_egov_source_freshness.py to keep the
        # legacy-root corpus and shared-standards corpus from double-counting.
        if entry["corpus_id"] == "ordinance37":
            continue
        try:
            checks.append(check(entry))
        except Exception as exc:
            errors.append({"id": entry["corpus_id"], "error": str(exc)})

    result = (
        "PASS"
        if (
            not errors
            and checks
            and all(
                row["result"] == "PASS" and row["current_enforced"]
                for row in checks
            )
        )
        else "FAIL"
    )

    report = {
        "format_version": 2,
        "verification_kind": "EGOV_SHARED_STANDARDS_SOURCE_FRESHNESS",
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "result": result,
        "checks": checks,
        "errors": errors,
        "interpretation": {
            "scope": "SHARED_SOURCE_LEVEL_ONLY",
            "pass_meaning": (
                "Committed source hashes and CurrentEnforced revision metadata match "
                "live e-Gov for each current shared standards corpus at check time."
            ),
            "does_not_establish": [
                "service applicability",
                "service relation verification",
                "item-body verification for a service slice",
                "human review",
                "publication",
                "route exposure",
            ],
        },
        "safety": {
            "read_only": True,
            "updates_generated_data": False,
            "promotes_service_verification": False,
            "promotes_currentness_to_services": False,
            "promotes_human_review": False,
            "promotes_publication": False,
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
