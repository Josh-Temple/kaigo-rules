#!/usr/bin/env python3
"""Build a pinned cross-layer source-chain audit record from a fresh verifier report."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "cross-layer-source-chain-independent-audit.json"

# data/sources.json is intentionally not byte-pinned here. The validator checks
# the Notice 19 source row semantically, so unrelated source-registry additions
# must not invalidate this audit lane.
PINNED_INPUTS = [
    "data/care-insurance-act-relations.json",
    "data/care-insurance-act-nodes.json",
    "data/careact-internal-relation-independent-audit.json",
    "data/relation-semantic-independent-audit.json",
    "data/ordinance37-meta.json",
    "data/ordinance37-scope.json",
    "data/remuneration-current-skeleton.json",
    "scripts/verify_cross_layer_source_chains_independent.py",
    "data/care-insurance-act-meta.json",
    "data/remuneration-current-text-meta.json",
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
        raise SystemExit("cannot pin a non-PASS cross-layer report")
    if len(report.get("checks", [])) != 2:
        raise SystemExit("expected exactly two cross-layer source-chain checks")

    report_bytes = args.verification_report.read_bytes()
    payload = {
        "format_version": 1,
        "scope": "careact-to-remuneration-and-ordinance37-source-chains",
        "audit_kind": "INDEPENDENT_CROSS_LAYER_SOURCE_CHAIN_AUDIT",
        "audit_result": "PASS",
        "audited_at": date.today().isoformat(),
        "audit_run": {
            "workflow": "Verify cross-layer source chains independently",
            "run_id": int(args.run_id),
            "head_sha": args.head_sha,
            "result": "PASS",
            "parsers": report["parsers"],
            "verification_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        },
        "checks": report["checks"],
        "coverage": report["coverage"],
        "input_git_blob_shas_at_audit": {
            relative: git_blob_sha1(ROOT / relative) for relative in PINNED_INPUTS
        },
        "conclusion": (
            "One Care Insurance Act fee-authority relation and 17 Article 74 to "
            "Ordinance 37 direct day-service standard relations matched fresh primary-source chains."
        ),
        "limitations": [
            "PASS is source-chain consistency, not a human legal interpretation.",
            "The Article 74 lane remains limited to the 17 committed dayservice direct-article targets.",
            "Other semantic or cross-layer relations remain outside this lane unless separately audited.",
            "This audit does not promote HUMAN_VERIFIED or VERIFIED_CURRENT.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
            "promotes_other_semantic_mappings": False,
        },
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
