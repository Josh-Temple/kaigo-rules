#!/usr/bin/env python3
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOTS_PATH = ROOT / "data" / "notice-equipment-source-snapshots.json"
ASSEMBLY_PATH = ROOT / "data" / "notice-equipment-current-assembly.json"
SKELETON_PATH = ROOT / "data" / "notice-current-skeleton.json"
REPLAY_PATH = ROOT / "data" / "notice-equipment-replay-coverage.json"

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def main() -> None:
    snapshots = json.loads(SNAPSHOTS_PATH.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY_PATH.read_text(encoding="utf-8"))
    skeleton = json.loads(SKELETON_PATH.read_text(encoding="utf-8"))
    replay = json.loads(REPLAY_PATH.read_text(encoding="utf-8"))

    snapshot_by_id = {item["id"]: item for item in snapshots["segments"]}
    skeleton_by_id = {item["id"]: item for item in skeleton}
    replay_by_id = {item["notice_id"]: item for item in replay}

    output = []
    seen = set()
    for spec in assembly["items"]:
        notice_id = spec["notice_id"]
        if notice_id in seen:
            raise RuntimeError(f"Duplicate notice_id in assembly: {notice_id}")
        seen.add(notice_id)

        node = skeleton_by_id.get(notice_id)
        coverage = replay_by_id.get(notice_id)
        snapshot = snapshot_by_id.get(spec["baseline_snapshot_id"])
        if not node:
            raise RuntimeError(f"Missing notice skeleton node: {notice_id}")
        if not coverage:
            raise RuntimeError(f"Missing replay coverage: {notice_id}")
        if not snapshot or not snapshot.get("body_text"):
            raise RuntimeError(f"Missing source body snapshot: {spec['baseline_snapshot_id']}")
        if snapshot["notice_id"] != notice_id:
            raise RuntimeError(f"Snapshot notice_id mismatch: {snapshot['id']}")

        candidate_text = snapshot["body_text"].strip() + "\n"
        output.append({
            "notice_id": notice_id,
            "number_path": node["number_path"],
            "title": node["title"],
            "effective_as_of": assembly["effective_as_of"],
            "baseline_snapshot_id": snapshot["id"],
            "replay_status": coverage["replay_status"],
            "replay_coverage_as_of": coverage["coverage_as_of"],
            "reconstruction_status": assembly["reconstruction_status"],
            "human_verification_status": "NOT_REVIEWED",
            "evidence": [{
                "snapshot_id": snapshot["id"],
                "source_id": snapshot["source_id"],
                "page_start": snapshot["page_start"],
                "page_end": snapshot["page_end"],
                "body_text_sha256": snapshot["body_text_sha256"],
            }],
            "candidate_text_sha256": sha256_text(candidate_text),
            "candidate_text": candidate_text,
        })

    result = {
        "format_version": 1,
        "generator": "scripts/assemble_notice_equipment_current_candidates.py",
        "policy": assembly["policy"],
        "effective_as_of": assembly["effective_as_of"],
        "reconstruction_status": assembly["reconstruction_status"],
        "items": output,
    }
    output_path = ROOT / assembly["output_path"]
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}: {len(output)} equipment current-text candidates")

if __name__ == "__main__":
    main()
