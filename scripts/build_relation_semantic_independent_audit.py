#!/usr/bin/env python3
"""Build a pinned audit record from a fresh explicit legal-reference verifier report."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "relation-semantic-independent-audit.json"

PINNED_INPUTS = [
    "data/ordinance37-nodes.json",
    "data/ordinance37-relations.json",
    "data/care-insurance-act-relations.json",
    "data/fee-guidance-relations.json",
    "data/notice-ordinance-relations.json",
    "data/relationships.json",
    "data/remuneration-delegated-relations.json",
    "data/remuneration-relations.json",
    "scripts/verify_relation_semantics_independent.py",
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
        raise SystemExit("cannot pin a non-PASS explicit relation report")
    if len(report.get("checks", [])) != 1:
        raise SystemExit("expected exactly one explicit relation check")

    report_bytes = args.verification_report.read_bytes()
    payload = {
        "format_version": 1,
        "scope": "explicit-legal-reference-relations-ordinance37-article105",
        "audit_kind": "INDEPENDENT_EXPLICIT_LEGAL_REFERENCE_AUDIT",
        "audit_result": "PASS",
        "audited_at": date.today().isoformat(),
        "audit_run": {
            "workflow": "Verify explicit legal-reference relations independently",
            "run_id": int(args.run_id),
            "head_sha": args.head_sha,
            "parser": report["parser"],
            "result": "PASS",
            "verification_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        },
        "checks": report["checks"],
        "coverage": report["coverage"],
        "input_git_blob_shas_at_audit": {
            relative: git_blob_sha1(ROOT / relative) for relative in PINNED_INPUTS
        },
        "conclusion": (
            "The 23 explicit Article 105 incorporates_by_reference targets matched "
            "an independent parse of live e-Gov Article 105 text."
        ),
        "limitations": [
            "PASS applies only to the 23 explicit Article 105 incorporates_by_reference relations.",
            "Other semantic or cross-layer relations remain outside this audit lane.",
            "This audit does not promote HUMAN_VERIFIED or VERIFIED_CURRENT.",
            "Structural contains relations may grow as the shared corpus expands without becoming semantic verification.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
            "promotes_unverified_semantic_mappings": False,
        },
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
