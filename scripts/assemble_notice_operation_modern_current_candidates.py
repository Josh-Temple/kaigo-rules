#!/usr/bin/env python3
import hashlib
import json
import pathlib
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOTS_PATH = ROOT / "data" / "notice-operation-modern-source-snapshots.json"
ASSEMBLY_PATH = ROOT / "data" / "notice-operation-modern-current-assembly.json"
SKELETON_PATH = ROOT / "data" / "notice-current-skeleton.json"
REPLAY_PATH = ROOT / "data" / "notice-operation-modern-replay-coverage.json"

def normalize_with_map(value: str):
    chars = []
    positions = []
    for index, source_char in enumerate(value):
        for char in unicodedata.normalize("NFKC", source_char):
            if char.isspace():
                continue
            chars.append(char)
            positions.append(index)
    return "".join(chars), positions

def normalized(value: str) -> str:
    return normalize_with_map(value)[0]

def replace_between_normalized(value: str, start_anchor: str, end_anchor: str, replacement: str) -> str:
    normalized_value, positions = normalize_with_map(value)
    start_needle = normalized(start_anchor)
    end_needle = normalized(end_anchor)
    start = normalized_value.find(start_needle)
    if start < 0:
        raise RuntimeError(f"Patch start anchor not found: {start_anchor}")
    if normalized_value.find(start_needle, start + 1) >= 0:
        raise RuntimeError(f"Patch start anchor is not unique: {start_anchor}")
    end = normalized_value.find(end_needle, start + len(start_needle))
    if end < 0:
        raise RuntimeError(f"Patch end anchor not found after start: {end_anchor}")
    source_start = positions[start]
    source_end = positions[end]
    return value[:source_start].rstrip() + replacement.strip() + value[source_end:]

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
        baseline = snapshot_by_id.get(spec["baseline_snapshot_id"])
        if not node:
            raise RuntimeError(f"Missing notice skeleton node: {notice_id}")
        if not coverage:
            raise RuntimeError(f"Missing replay coverage: {notice_id}")
        if not baseline or not baseline.get("body_text"):
            raise RuntimeError(f"Missing source body snapshot: {spec['baseline_snapshot_id']}")
        if baseline["notice_id"] != notice_id:
            raise RuntimeError(f"Snapshot notice_id mismatch: {baseline['id']}")

        candidate_text = baseline["body_text"].strip()
        evidence = [{
            "snapshot_id": baseline["id"],
            "source_id": baseline["source_id"],
            "role": "baseline",
            "page_start": baseline["page_start"],
            "page_end": baseline["page_end"],
            "body_text_sha256": baseline["body_text_sha256"],
        }]

        for patch in spec.get("patches", []):
            snapshot = snapshot_by_id.get(patch["snapshot_id"])
            if not snapshot or not snapshot.get("body_text"):
                raise RuntimeError(f"Missing patch body snapshot: {patch['snapshot_id']}")
            if snapshot["notice_id"] != notice_id:
                raise RuntimeError(f"Patch notice_id mismatch: {snapshot['id']}")
            if patch["operation"] != "replace_between":
                raise RuntimeError(f"Unsupported patch operation: {patch['operation']}")
            candidate_text = replace_between_normalized(
                candidate_text,
                patch["start_anchor"],
                patch["end_anchor"],
                snapshot["body_text"],
            )
            evidence.append({
                "snapshot_id": snapshot["id"],
                "source_id": snapshot["source_id"],
                "role": "patch",
                "page_start": snapshot["page_start"],
                "page_end": snapshot["page_end"],
                "body_text_sha256": snapshot["body_text_sha256"],
                "operation": patch["operation"],
                "start_anchor": patch["start_anchor"],
                "end_anchor": patch["end_anchor"],
                "note": patch.get("note"),
            })

        candidate_text = candidate_text.strip() + "\n"
        output.append({
            "notice_id": notice_id,
            "number_path": node["number_path"],
            "title": node["title"],
            "effective_as_of": assembly["effective_as_of"],
            "baseline_snapshot_id": baseline["id"],
            "patch_snapshot_ids": [patch["snapshot_id"] for patch in spec.get("patches", [])],
            "replay_status": coverage["replay_status"],
            "replay_coverage_as_of": coverage["coverage_as_of"],
            "reconstruction_status": assembly["reconstruction_status"],
            "human_verification_status": "NOT_REVIEWED",
            "evidence": evidence,
            "candidate_text_sha256": sha256_text(candidate_text),
            "candidate_text": candidate_text,
        })

    result = {
        "format_version": 1,
        "generator": "scripts/assemble_notice_operation_modern_current_candidates.py",
        "policy": assembly["policy"],
        "effective_as_of": assembly["effective_as_of"],
        "reconstruction_status": assembly["reconstruction_status"],
        "items": output,
    }
    output_path = ROOT / assembly["output_path"]
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}: {len(output)} operation-modern current-text candidates")

if __name__ == "__main__":
    main()
