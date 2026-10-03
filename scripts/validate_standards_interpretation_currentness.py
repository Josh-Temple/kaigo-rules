#!/usr/bin/env python3
"""Validate normalized standards-interpretation gate state across five services.

This validator does not reinterpret legal sources. It cross-checks the existing
service-specific receipts and fail-closed repository state while preserving the
independence of item-body, currentness, human-review, publication, and routing.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "data/verification/standards-interpretation-gates.json"
SERVICES = (
    "community-dayservice",
    "regular-round",
    "night-homevisit",
    "care-management",
    "preventive-support",
)
CURRENTNESS_KEYS = {
    "community-dayservice": ("conclusion", "currentness_state"),
    "regular-round": ("conclusion", "currentness"),
    "night-homevisit": ("conclusion", "state"),
    "care-management": ("conclusion", "currentness"),
    "preventive-support": ("conclusion", "currentness"),
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nested(data: dict, path: tuple[str, ...]):
    value = data
    for key in path:
        value = value[key]
    return value


def validate() -> list[str]:
    errors: list[str] = []
    state = load(STATE)
    rows = {row["service_id"]: row for row in state.get("services", [])}
    if set(rows) != set(SERVICES):
        errors.append("gate-state service set mismatch")
        return errors

    independence = state.get("layer_independence", {})
    for key in (
        "item_body_pass_does_not_establish_currentness",
        "currentness_pass_does_not_complete_human_review",
        "human_review_does_not_allow_publication_automatically",
        "publication_allowed_does_not_enable_route_automatically",
    ):
        if independence.get(key) is not True:
            errors.append(f"layer independence missing: {key}")

    for service_id in SERVICES:
        row = rows[service_id]
        service = load(ROOT / f"data/services/{service_id}.json")
        scope = load(ROOT / f"data/services/{service_id}/standards-interpretation-scope.json")
        staging = load(ROOT / f"data/services/{service_id}/standards-interpretation-staging.json")
        inventory = load(ROOT / row["source_inventory"]["receipt"])
        item_body = load(ROOT / row["item_body"]["receipt"])
        item_summary = item_body.get("integration_summary", {})

        if row["source_inventory"].get("state") != "PASS_BOUNDED_SCOPE_ONLY":
            errors.append(f"{service_id}: normalized source-inventory state drifted")
        if inventory.get("audit_result") != "PASS_BOUNDED_SCOPE_ONLY":
            errors.append(f"{service_id}: source-inventory receipt not bounded PASS")

        if item_summary.get("verification_status") != row["item_body"].get("state"):
            errors.append(f"{service_id}: item-body status mismatch")
        if item_summary.get("counts") != row["item_body"].get("counts"):
            errors.append(f"{service_id}: item-body counts mismatch")
        if item_summary.get("source_inventory_state") != "PASS_BOUNDED_SCOPE_ONLY":
            errors.append(f"{service_id}: item-body/source-inventory boundary drifted")
        if item_summary.get("currentness_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: item-body unexpectedly establishes currentness")
        if item_summary.get("human_review_state") != "NOT_REVIEWED":
            errors.append(f"{service_id}: item-body unexpectedly completes human review")
        if item_summary.get("publication_allowed") is not False:
            errors.append(f"{service_id}: item-body unexpectedly allows publication")
        if item_summary.get("public_route_enabled") is not False:
            errors.append(f"{service_id}: item-body unexpectedly enables route")

        current = row["currentness"]
        if current.get("state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: normalized currentness must remain NOT_ESTABLISHED")
        if current.get("verification_performed"):
            receipt_path = current.get("receipt")
            verifier_path = current.get("verifier")
            if not receipt_path or not (ROOT / receipt_path).exists():
                errors.append(f"{service_id}: currentness receipt missing")
            else:
                receipt = load(ROOT / receipt_path)
                key_path = CURRENTNESS_KEYS.get(service_id)
                if not key_path or nested(receipt, key_path) != "NOT_ESTABLISHED":
                    errors.append(f"{service_id}: currentness receipt result mismatch")
            if not verifier_path or not (ROOT / verifier_path).exists():
                errors.append(f"{service_id}: currentness verifier missing")
        else:
            if current.get("receipt") is not None or current.get("verifier") is not None:
                errors.append(f"{service_id}: unperformed currentness has receipt/verifier")
            expected_path = ROOT / f"data/verification/standards-interpretation-currentness/{service_id}.json"
            if expected_path.exists():
                errors.append(f"{service_id}: currentness receipt exists but state says unperformed")

        if scope.get("currentness_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: scope currentness promoted")
        if staging.get("currentness_state") != "NOT_ESTABLISHED":
            errors.append(f"{service_id}: staging currentness promoted")
        if staging.get("human_review_state") != "NOT_REVIEWED":
            errors.append(f"{service_id}: staging human review promoted")
        if staging.get("publication_state") != "NOT_PUBLIC":
            errors.append(f"{service_id}: staging publication promoted")

        if row["human_review"].get("state") != "NOT_REVIEWED":
            errors.append(f"{service_id}: normalized human review promoted")
        if row["publication"].get("allowed") is not False:
            errors.append(f"{service_id}: normalized publication promoted")
        if row["route"].get("enabled") is not False:
            errors.append(f"{service_id}: normalized route promoted")

        gate = service.get("publication_gate", {})
        for key in (
            "public_routes_enabled",
            "content_ingested",
            "independent_verification_complete",
            "human_review_complete",
        ):
            if gate.get(key) is not False:
                errors.append(f"{service_id}: publication_gate.{key} promoted")
        if service.get("routing", {}).get("future_service_base_enabled") is not False:
            errors.append(f"{service_id}: service route enabled")

        if item_summary.get("package_blocker_state") != row["package"].get("blocker_state"):
            errors.append(f"{service_id}: PACKAGE blocker state mismatch")

    preventive = rows["preventive-support"]
    if preventive["item_body"]["counts"] != {"PASS": 32, "PARTIAL": 2, "GAP": 0, "FAIL": 0}:
        errors.append("preventive-support: residual item-body counts changed")
    if preventive["package"].get("blocker_task_id") != "KR2-10-E006":
        errors.append("preventive-support: KR2-10-E006 blocker not preserved")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print("FAIL standards-interpretation gates:", error)
        return 1
    print("PASS standards-interpretation gates: layers remain explicit and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
