#!/usr/bin/env python3
"""Record a successful independent e-Gov content reparse as a pinned audit receipt.

This script is intentionally separate from the verifier. It may only record a
PASS report and never promotes service applicability, human review, or
VERIFIED_CURRENT state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "egov-content-independent-audit.json"

PINNED_INPUTS = [
    "data/ordinance37-scope.json",
    "data/ordinance37-nodes.json",
    "data/ordinance37-relations.json",
    "data/ordinance37-meta.json",
    "data/care-insurance-act-corpus-scope.json",
    "data/care-insurance-act-nodes.json",
    "data/care-insurance-act-relations.json",
    "data/care-insurance-act-meta.json",
    "scripts/verify_egov_content_independent.py",
]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True)
    parser.add_argument("--run-id", required=True, type=int)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument(
        "--audited-at",
        default=datetime.now(timezone.utc).date().isoformat(),
        help="ISO date for the audit receipt; defaults to the current UTC date.",
    )
    args = parser.parse_args()

    if args.run_id <= 0:
        raise SystemExit("run id must be positive")
    if not re.fullmatch(r"[0-9a-f]{40}", args.head_sha):
        raise SystemExit("head sha must be a 40-character lowercase hex SHA")

    report_path = Path(args.report)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("verification_kind") != "INDEPENDENT_EGOV_CONTENT_REPARSE":
        raise SystemExit("unexpected verifier report kind")
    if report.get("parser") != "python_xml_dom_minidom":
        raise SystemExit("unexpected independent parser")
    if report.get("result") != "PASS":
        raise SystemExit("refusing to record a non-PASS verifier report")
    if report.get("errors"):
        raise SystemExit("refusing to record verifier report with errors")

    checks = []
    expected_ids = {"ordinance37", "care-insurance-act"}
    observed_ids = {row.get("id") for row in report.get("checks", [])}
    if observed_ids != expected_ids:
        raise SystemExit(f"unexpected verifier check set: {sorted(observed_ids)}")

    for row in report["checks"]:
        if row.get("result") != "PASS" or row.get("differences") != []:
            raise SystemExit(f"refusing dirty audit check: {row.get('id')}")
        checks.append(
            {
                "id": row["id"],
                "law_id": row["law_id"],
                "scope_file": row.get("scope_file"),
                "observed_xml_sha256": row["observed_xml_sha256"],
                "result": "PASS",
                "observed": row["observed"],
                "excluded_non_contains_relations": row.get(
                    "excluded_from_audit", {}
                ).get("non_contains_relations", 0),
            }
        )

    inputs = {}
    for relative in PINNED_INPUTS:
        path = ROOT / relative
        if not path.exists():
            raise SystemExit(f"pinned audit input missing: {relative}")
        inputs[relative] = git_blob_sha1(path)

    payload = {
        "format_version": 2,
        "scope": "egov-shared-content-ordinance37-care-insurance-act",
        "audit_kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
        "audit_result": "PASS",
        "audited_at": args.audited_at,
        "audit_run": {
            "workflow": "Update Care Insurance Act database",
            "run_id": args.run_id,
            "head_sha": args.head_sha,
            "parser": "python_xml_dom_minidom",
            "result": "PASS",
            "verification_report_sha256": sha256(report_path),
        },
        "checks": sorted(checks, key=lambda row: row["id"]),
        "input_git_blob_shas_at_audit": inputs,
        "conclusion": (
            "Source-derived official text, stable node IDs, parent structure and "
            "containment matched live e-Gov XML using an independent XML parser. "
            "The Care Insurance Act check covers the shared service-foundation corpus; "
            "service applicability remains in separate service scope/index files."
        ),
        "limitations": [
            "The audit covers source-derived selected text and containment only.",
            "Corpus presence does not establish applicability to any service.",
            "Hand-authored legal-semantic and cross-layer relations are excluded and remain separately reviewable.",
            "Independent machine verification is not HUMAN_VERIFIED or VERIFIED_CURRENT.",
            "Later source, data, scope, or verifier changes invalidate the pinned receipt and require a new independent run.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "service_applicability_verified": False,
            "automatic_promotion_allowed": False,
        },
    }

    OUTPUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
