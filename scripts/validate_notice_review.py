#!/usr/bin/env python3
"""Validate the rouki25 human-review packet and fail closed on stale human review."""

from __future__ import annotations

import json
import pathlib
import sys

from build_notice_review_packet import DATA, OUTPUT, build_packet, render

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    errors = []
    expected_packet = build_packet()

    if not OUTPUT.exists():
        errors.append("notice review: missing data/notice-review-packet.json")
        actual_packet = None
    else:
        actual_text = OUTPUT.read_text(encoding="utf-8")
        expected_text = render(expected_packet)
        if actual_text != expected_text:
            errors.append("notice review: committed review packet is stale")
        try:
            actual_packet = json.loads(actual_text)
        except json.JSONDecodeError as exc:
            errors.append(f"notice review: invalid packet JSON: {exc}")
            actual_packet = None

    items = expected_packet.get("items", [])
    if len(items) != 22:
        errors.append(f"notice review: expected 22 packet items, got {len(items)}")

    candidate_hashes = {item["notice_id"]: item["candidate_text_sha256"] for item in items}

    for item in items:
        if item.get("reconstruction_status") != "MACHINE_RECONSTRUCTED_NEEDS_HUMAN_CHECK":
            errors.append(f"notice review {item['notice_id']}: unsafe reconstruction status")
        if item.get("human_verification_status") != "NOT_REVIEWED":
            errors.append(f"notice review {item['notice_id']}: candidate file must not self-promote human verification")
        if item.get("independent_verification", {}).get("result") != "PASS":
            errors.append(f"notice review {item['notice_id']}: independent verification record is stale")

    review = json.loads((DATA / "notice-current-review.json").read_text(encoding="utf-8"))
    for entry in review.get("reviewed_nodes", []):
        notice_id = entry.get("notice_id")
        if notice_id not in candidate_hashes:
            continue
        reviewed_hash = entry.get("reviewed_candidate_sha256")
        if not reviewed_hash:
            errors.append(f"notice review {notice_id}: reviewed node missing reviewed_candidate_sha256")
        elif reviewed_hash != candidate_hashes[notice_id]:
            errors.append(f"notice review {notice_id}: stale human review hash")
        if not entry.get("reviewed_at"):
            errors.append(f"notice review {notice_id}: reviewed node missing reviewed_at")

    if actual_packet is not None and actual_packet.get("items") != expected_packet.get("items"):
        errors.append("notice review: packet item content differs from deterministic build")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("notice review validation: OK (22 items; independent hashes current; human-review hashes not stale)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
