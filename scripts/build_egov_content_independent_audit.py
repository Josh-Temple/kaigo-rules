#!/usr/bin/env python3
"""Build the pinned independent e-Gov audit record from a fresh verifier report."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "egov-content-independent-audit.json"

PINNED_INPUTS = [
    "data/ordinance37-scope.json",
    "data/ordinance37-nodes.json",
    "data/ordinance37-relations.json",
    "data/ordinance37-meta.json",
    "data/care-insurance-act-scope.json",
    "data/care-insurance-act-nodes.json",
    "data/care-insurance-act-relations.json",
    "data/care-insurance-act-meta.json",
    "scripts/verify_egov_content_independent.py",
]


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verification-report", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--head-sha", required=True)
    args = parser.parse_args()

    report = json.loads(args.verification_report.read_text(encoding="utf-8"))
    if report.get("result") != "PASS":
        raise SystemExit("cannot pin a non-PASS e-Gov verification report")

    checks = []
    for row in report.get("checks", []):
        checks.append({
            "id": row["id"],
            "law_id": row["law_id"],
            "observed_xml_sha256": row["observed_xml_sha256"],
            "result": row["result"],
            "observed": row["observed"],
            "excluded_non_contains_relations": row.get("excluded_from_audit", {}).get("non_contains_relations", 0),
        })

    report_bytes = args.verification_report.read_bytes()
    payload = {
        "format_version": 1,
        "scope": "egov-scoped-content-ordinance37-care-insurance-act",
        "audit_kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
        "audit_result": "PASS",
        "audited_at": date.today().isoformat(),
        "audit_run": {
            "workflow": "Verify e-Gov scoped content independently",
            "run_id": int(args.run_id),
            "head_sha": args.head_sha,
            "parser": report["parser"],
            "result": "PASS",
            "verification_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        },
        "checks": checks,
        "input_git_blob_shas_at_audit": {
            relative: git_blob_sha1(ROOT / relative) for relative in PINNED_INPUTS
        },
        "conclusion": (
            "Scoped official text, node IDs, parent structure and source-derived containment "
            "matched live e-Gov XML for Ordinance 37 and the Care Insurance Act using an "
            "independent XML parser. Ordinance 37 covers the full MainProvision as one shared "
            "source corpus without collapsing service applicability or verification state."
        ),
        "limitations": [
            "The audit covers source-derived text and containment only; Ordinance 37 is full MainProvision while the Care Insurance Act remains scoped.",
            "Hand-authored legal-semantic and cross-layer relations are excluded and remain separately reviewable.",
            "Independent machine verification is not HUMAN_VERIFIED or VERIFIED_CURRENT.",
            "Later source/data/verifier changes require refresh of this record.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
        },
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
