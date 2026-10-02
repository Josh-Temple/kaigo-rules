#!/usr/bin/env python3
"""Validate pinned homevisit Rouki 25 historical-source audit provenance."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "data/homevisit-rouki25-historical-independent-audit.json"


def fail(message: str) -> None:
    raise SystemExit(
        "homevisit Rouki 25 historical audit validation failed: " + message
    )


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def blob(path: Path) -> str:
    body = path.read_bytes()
    return hashlib.sha1(
        f"blob {len(body)}\0".encode("ascii") + body
    ).hexdigest()


def main() -> None:
    if not RECEIPT.exists():
        fail("receipt missing")
    receipt = load(RECEIPT)
    if (
        receipt.get("scope")
        != "homevisit-rouki25-official-historical-html-section"
        or receipt.get("audit_kind")
        != "INDEPENDENT_HOMEVISIT_ROUKI25_HISTORICAL_SOURCE_AUDIT"
        or receipt.get("audit_result") != "PASS"
    ):
        fail("unexpected identity/result")

    run = receipt.get("audit_run", {})
    if not isinstance(run.get("run_id"), int) or run["run_id"] <= 0:
        fail("invalid run")
    if not re.fullmatch(r"[0-9a-f]{40}", str(run.get("head_sha") or "")):
        fail("invalid head sha")
    if not re.fullmatch(
        r"[0-9a-f]{64}",
        str(run.get("verification_report_sha256") or ""),
    ):
        fail("invalid report sha")

    checks = receipt.get("checks", [])
    if (
        len(checks) != 35
        or any(
            item.get("result") != "PASS"
            or item.get("differences") != []
            for item in checks
        )
    ):
        fail("item checks not clean")
    if receipt.get("coverage") != {
        "principal_items": 35,
        "items_passed": 35,
    }:
        fail("coverage changed")

    safety = receipt.get("safety", {})
    if (
        safety.get("historical_source_only") is not True
        or safety.get("current_integrated_text") is not False
        or safety.get("human_verified") is not False
        or safety.get("verified_current") is not False
        or safety.get("automatic_promotion_allowed") is not False
    ):
        fail("unsafe state")

    dataset = load(
        ROOT / "data/services/homevisit/rouki25-historical.generated.json"
    )
    if dataset.get("item_count") != 35:
        fail("dataset item count changed")
    if dataset.get("source", {}).get("sha256") != receipt.get(
        "source", {}
    ).get("sha256"):
        fail("source hash mismatch between dataset and audit")

    for relative_path, expected in receipt.get(
        "input_git_blob_shas_at_audit", {}
    ).items():
        path = ROOT / relative_path
        if not path.exists() or blob(path) != expected:
            fail(f"pinned input changed: {relative_path}")

    print(
        "homevisit Rouki 25 historical audit: OK "
        "(35/35 PASS; currentness remains GAP)"
    )


if __name__ == "__main__":
    main()
