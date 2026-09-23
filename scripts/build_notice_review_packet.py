#!/usr/bin/env python3
"""Build a deterministic human-review packet for the 22 reconstructed 老企第25号 day-service items."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

from verify_notice_rouki25_independent import EXPECTED_SOURCE_SHA256, SOURCE_URLS

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = DATA / "notice-review-packet.json"

FAMILIES = (
    {
        "family": "personnel",
        "section": "人員に関する基準",
        "candidate": "notice-personnel-current-text-candidates.json",
        "manifest": "notice-personnel-source-manifest.json",
        "snapshots": "notice-personnel-source-snapshots.json",
        "assembly": "notice-personnel-current-assembly.json",
    },
    {
        "family": "equipment",
        "section": "設備に関する基準",
        "candidate": "notice-equipment-current-text-candidates.json",
        "manifest": "notice-equipment-source-manifest.json",
        "snapshots": "notice-equipment-source-snapshots.json",
        "assembly": "notice-equipment-current-assembly.json",
    },
    {
        "family": "operation_legacy",
        "section": "運営に関する基準",
        "candidate": "notice-operation-legacy-current-text-candidates.json",
        "manifest": "notice-operation-legacy-source-manifest.json",
        "snapshots": "notice-operation-legacy-source-snapshots.json",
        "assembly": "notice-operation-legacy-current-assembly.json",
    },
    {
        "family": "operation_modern",
        "section": "運営に関する基準",
        "candidate": "notice-operation-modern-current-text-candidates.json",
        "manifest": "notice-operation-modern-source-manifest.json",
        "snapshots": "notice-operation-modern-source-snapshots.json",
        "assembly": "notice-operation-modern-current-assembly.json",
    },
)

REVIEWER_CHECKLIST = [
    "candidate本文が一次資料の該当箇所と一致する",
    "baselineとpatchの適用順序が妥当である",
    "後続改正で当該項目が変更されていないことを確認した",
    "独立機械照合の対象hashと現在のcandidate hashが一致する",
]


def load_json(name: str):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def build_packet() -> dict:
    sources = {item["id"]: item for item in load_json("sources.json")}
    review = load_json("notice-current-review.json")
    review_by_notice = {
        item["notice_id"]: item
        for item in review.get("reviewed_nodes", [])
        if item.get("notice_id")
    }
    independent = load_json("notice-rouki25-independent-verification.json")
    independent_hashes = independent.get("candidate_sha256", {})

    items = []
    for family in FAMILIES:
        candidates = load_json(family["candidate"])
        manifest = load_json(family["manifest"])
        snapshots = load_json(family["snapshots"])
        assembly = load_json(family["assembly"])

        manifest_by_id = {item["id"]: item for item in manifest.get("segments", [])}
        snapshot_by_id = {item["id"]: item for item in snapshots.get("segments", [])}
        source_snapshot_by_id = {item["source_id"]: item for item in snapshots.get("sources", [])}
        assembly_by_notice = {item["notice_id"]: item for item in assembly.get("items", [])}

        for candidate in candidates.get("items", []):
            notice_id = candidate["notice_id"]
            assembled = assembly_by_notice.get(notice_id)
            if not assembled:
                raise ValueError(f"{notice_id}: missing assembly entry")

            baseline_id = assembled["baseline_snapshot_id"]
            replay_order = [{"step": 0, "snapshot_id": baseline_id, "operation": "baseline"}]
            for step, patch in enumerate(assembled.get("patches", []), start=1):
                replay_order.append(
                    {
                        "step": step,
                        "snapshot_id": patch["snapshot_id"],
                        "operation": patch["operation"],
                        "note": patch.get("note"),
                    }
                )

            evidence = []
            for ev in candidate.get("evidence", []):
                snapshot_id = ev["snapshot_id"]
                manifest_segment = manifest_by_id.get(snapshot_id)
                snapshot_segment = snapshot_by_id.get(snapshot_id)
                if not manifest_segment or not snapshot_segment:
                    raise ValueError(f"{notice_id}: missing manifest/snapshot for {snapshot_id}")
                if snapshot_segment.get("body_text_sha256") != ev.get("body_text_sha256"):
                    raise ValueError(f"{notice_id}: body hash mismatch for {snapshot_id}")

                source_id = ev["source_id"]
                source_snapshot = source_snapshot_by_id.get(source_id)
                if not source_snapshot:
                    raise ValueError(f"{notice_id}: missing source snapshot for {source_id}")

                expected_sha = EXPECTED_SOURCE_SHA256.get(source_id)
                expected_url = SOURCE_URLS.get(source_id)
                if expected_sha and source_snapshot.get("sha256") != expected_sha:
                    raise ValueError(f"{notice_id}: independent source SHA mismatch for {source_id}")
                if expected_url and source_snapshot.get("url") != expected_url:
                    raise ValueError(f"{notice_id}: independent source URL mismatch for {source_id}")

                registry = sources.get(source_id, {})
                evidence.append(
                    {
                        "snapshot_id": snapshot_id,
                        "role": ev.get("role", manifest_segment.get("role")),
                        "source_id": source_id,
                        "source_title": registry.get("title"),
                        "publisher": registry.get("publisher"),
                        "source_url": source_snapshot.get("url"),
                        "page_start": ev.get("page_start", snapshot_segment.get("page_start")),
                        "page_end": ev.get("page_end", snapshot_segment.get("page_end")),
                        "source_pdf_sha256": source_snapshot.get("sha256"),
                        "snapshot_body_sha256": snapshot_segment.get("body_text_sha256"),
                        "operation": ev.get("operation"),
                        "note": ev.get("note", manifest_segment.get("note")),
                    }
                )

            recorded_hash = independent_hashes.get(notice_id)
            independent_result = "PASS" if recorded_hash == candidate["candidate_text_sha256"] and independent.get("result") == "PASS" else "STALE_OR_UNVERIFIED"

            existing_review = review_by_notice.get(notice_id, {})
            items.append(
                {
                    "notice_id": notice_id,
                    "family": family["family"],
                    "section": family["section"],
                    "title": candidate["title"],
                    "number_path": candidate["number_path"],
                    "effective_as_of": candidate.get("effective_as_of"),
                    "candidate_text": candidate["candidate_text"],
                    "candidate_text_sha256": candidate["candidate_text_sha256"],
                    "reconstruction_status": candidate["reconstruction_status"],
                    "human_verification_status": candidate["human_verification_status"],
                    "baseline_snapshot_id": baseline_id,
                    "replay_order": replay_order,
                    "source_evidence": evidence,
                    "independent_verification": {
                        "result": independent_result,
                        "recorded_candidate_sha256": recorded_hash,
                        "verifier": independent.get("verifier"),
                        "workflow": independent.get("workflow"),
                        "workflow_run_url": independent.get("workflow_run_url"),
                        "verified_at": independent.get("verified_at"),
                        "verified_main_sha": independent.get("verified_main_sha"),
                    },
                    "reviewer_checklist": REVIEWER_CHECKLIST,
                    "reviewer_decision": existing_review.get("reviewer_decision"),
                    "reviewer_note": existing_review.get("reviewer_note"),
                    "reviewed_at": existing_review.get("reviewed_at"),
                    "reviewed_candidate_sha256": existing_review.get("reviewed_candidate_sha256"),
                }
            )

    if len(items) != 22:
        raise ValueError(f"expected 22 review items, got {len(items)}")
    ids = [item["notice_id"] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate notice_id in review packet")

    return {
        "format_version": 1,
        "scope": "rouki25-dayservice-22",
        "policy": "Machine reconstruction and independent machine verification do not constitute human verification. Human review state remains separate and is invalidated when the reviewed candidate hash no longer matches.",
        "independent_verification_record": {
            "result": independent.get("result"),
            "verifier": independent.get("verifier"),
            "workflow": independent.get("workflow"),
            "workflow_run_url": independent.get("workflow_run_url"),
            "verified_at": independent.get("verified_at"),
            "verified_main_sha": independent.get("verified_main_sha"),
        },
        "items": items,
    }


def render(packet: dict) -> str:
    return json.dumps(packet, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if committed packet is stale")
    args = parser.parse_args()

    expected = render(build_packet())
    if args.check:
        if not OUTPUT.exists():
            print(f"missing {OUTPUT.relative_to(ROOT)}", file=sys.stderr)
            return 1
        actual = OUTPUT.read_text(encoding="utf-8")
        if actual != expected:
            print("notice-review-packet.json is stale; run scripts/build_notice_review_packet.py", file=sys.stderr)
            return 1
        print("notice review packet: current")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
