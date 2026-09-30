#!/usr/bin/env python3
"""Build the pinned audit record for dayrehab Ordinance 37 independent verification."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "dayrehab-ordinance37-independent-audit.json"

PINNED_INPUTS = [
    "data/ordinance37-scope.json",
    "data/ordinance37-nodes.json",
    "data/ordinance37-relations.json",
    "data/ordinance37-meta.json",
    "data/services/dayrehab/ordinance37-scope.json",
    "data/services/dayrehab/ordinance37-index.generated.json",
    "scripts/verify_dayrehab_ordinance37_independent.py",
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
        raise SystemExit("cannot pin a non-PASS dayrehab verification report")

    report_bytes = args.verification_report.read_bytes()
    payload = {
        "format_version": 1,
        "service_id": "dayrehab",
        "layer": "ordinance37",
        "audit_kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
        "audit_result": "PASS",
        "audited_at": date.today().isoformat(),
        "audit_run": {
            "workflow": "Refresh dayrehab e-Gov corpus once",
            "run_id": int(args.run_id),
            "head_sha": args.head_sha,
            "parser": report["parser"],
            "verification_report_sha256": hashlib.sha256(report_bytes).hexdigest(),
        },
        "source": {
            "law_id": "411M50000100037",
            "url": report["source_url"],
            "observed_xml_sha256": report["observed_xml_sha256"],
            "current_revision_id": report["current_revision_id"],
        },
        "target_articles": report["target_articles"],
        "observed": report["observed"],
        "input_git_blob_shas_at_audit": {
            relative: git_blob_sha1(ROOT / relative) for relative in PINNED_INPUTS
        },
        "conclusion": (
            "The dayrehab Chapter 8 slice in the shared Ordinance 37 corpus "
            "matched live e-Gov XML using an independent minidom reparse."
        ),
        "limitations": [
            "This audit covers source-derived dayrehab text and containment only.",
            "Semantic/cross-layer relations are not audited here.",
            "PASS does not mean HUMAN_VERIFIED.",
            "PASS does not independently establish exhaustive future/uncommenced amendment history.",
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
