#!/usr/bin/env python3
"""Pin an independently verified live e-Gov scoped-content audit."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
VERIFIER = ROOT / "scripts/verify_egov_content_independent.py"
OUTPUT = DATA / "egov-content-independent-audit.json"

FILES = {
    "ordinance37": {
        "scope": "ordinance37-scope.json",
        "nodes": "ordinance37-nodes.json",
        "relations": "ordinance37-relations.json",
        "meta": "ordinance37-meta.json",
    },
    "care-insurance-act": {
        "scope": "care-insurance-act-scope.json",
        "nodes": "care-insurance-act-nodes.json",
        "relations": "care-insurance-act-relations.json",
        "meta": "care-insurance-act-meta.json",
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(f"blob {len(body)}\0".encode("ascii") + body).hexdigest()


def fail(message: str) -> None:
    raise SystemExit("cannot pin e-Gov content audit: " + message)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--workflow", required=True)
    args = parser.parse_args()

    report = load(args.report)
    if report.get("verification_kind") != "INDEPENDENT_EGOV_CONTENT_REPARSE":
        fail("unexpected verification kind")
    if report.get("parser") != "python_xml_dom_minidom":
        fail("unexpected parser")
    if report.get("result") != "PASS" or report.get("errors") != []:
        fail("independent verifier did not pass cleanly")
    checks = report.get("checks", [])
    if {row.get("id") for row in checks} != set(FILES):
        fail("expected ordinance37 and care-insurance-act checks")
    if any(row.get("result") != "PASS" or row.get("differences") for row in checks):
        fail("one or more e-Gov checks contain differences")

    input_blobs = {}
    for layer_files in FILES.values():
        for name in layer_files.values():
            path = DATA / name
            input_blobs[str(path.relative_to(ROOT))] = blob(path)
    input_blobs[str(VERIFIER.relative_to(ROOT))] = blob(VERIFIER)

    report_sha = hashlib.sha256(args.report.read_bytes()).hexdigest()
    record = {
        "format_version": 1,
        "scope": "egov-scoped-content-ordinance37-care-insurance-act",
        "audit_kind": "INDEPENDENT_EGOV_CONTENT_REPARSE",
        "audit_result": "PASS",
        "audited_at": date.today().isoformat(),
        "audit_run": {
            "workflow": args.workflow,
            "run_id": args.run_id,
            "head_sha": args.head_sha,
            "parser": "python_xml_dom_minidom",
            "result": "PASS",
            "verification_report_sha256": report_sha,
        },
        "checks": checks,
        "input_git_blob_shas_at_audit": input_blobs,
        "conclusion": (
            "Scoped official text, node IDs, parent structure and source-derived "
            "containment matched live e-Gov XML for Ordinance 37 and the Care "
            "Insurance Act using an independent XML parser. Ordinance 37 now "
            "includes the bounded shortstay-life Chapter 9 current-text slice "
            "without fabricating deleted Article 140-16 through 140-25 bodies."
        ),
        "limitations": [
            "The audit covers source-derived scoped text and containment only.",
            "Deleted article slots are scope metadata and no deleted historical bodies are reconstructed.",
            "Hand-authored legal-semantic, incorporation, and cross-layer relations are excluded and remain separately reviewable.",
            "Independent machine verification is not HUMAN_VERIFIED or VERIFIED_CURRENT.",
            "Later source/data/verifier changes require refresh of this record.",
        ],
        "safety": {
            "human_verified": False,
            "verified_current": False,
            "automatic_promotion_allowed": False,
        },
    }
    OUTPUT.write_text(
        json.dumps(record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
