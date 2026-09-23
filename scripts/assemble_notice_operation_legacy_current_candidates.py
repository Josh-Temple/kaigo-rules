#!/usr/bin/env python3
import hashlib
import json
import pathlib
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOTS_PATH = ROOT / "data" / "notice-operation-legacy-source-snapshots.json"
ASSEMBLY_PATH = ROOT / "data" / "notice-operation-legacy-current-assembly.json"
SKELETON_PATH = ROOT / "data" / "notice-current-skeleton.json"
REPLAY_PATH = ROOT / "data" / "notice-operation-legacy-replay-coverage.json"

def normalize_with_map(value: str):
    chars, positions = [], []
    for index, source_char in enumerate(value):
        for char in unicodedata.normalize("NFKC", source_char):
            if char.isspace():
                continue
            chars.append(char)
            positions.append(index)
    return "".join(chars), positions

def normalized(value: str) -> str:
    return normalize_with_map(value)[0]

def find_unique_span(value: str, needle: str):
    nvalue, positions = normalize_with_map(value)
    nneedle = normalized(needle)
    start = nvalue.find(nneedle)
    if start < 0:
        raise RuntimeError(f"Anchor not found: {needle}")
    if nvalue.find(nneedle, start + 1) >= 0:
        raise RuntimeError(f"Anchor is not unique: {needle}")
    return positions[start], positions[start + len(nneedle) - 1] + 1

def replace_between(value: str, start_anchor: str, end_anchor: str, replacement: str) -> str:
    nvalue, positions = normalize_with_map(value)
    start_n = normalized(start_anchor)
    end_n = normalized(end_anchor)
    start = nvalue.find(start_n)
    if start < 0:
        raise RuntimeError(f"Patch start anchor not found: {start_anchor}")
    if nvalue.find(start_n, start + 1) >= 0:
        raise RuntimeError(f"Patch start anchor is not unique: {start_anchor}")
    end = nvalue.find(end_n, start + len(start_n))
    if end < 0:
        raise RuntimeError(f"Patch end anchor not found after start: {end_anchor}")
    return value[:positions[start]].rstrip() + replacement.strip() + value[positions[end]:]

def replace_to_end(value: str, start_anchor: str, replacement: str) -> str:
    start, _ = find_unique_span(value, start_anchor)
    return value[:start].rstrip() + replacement.strip()

def replace_literal(value: str, old_text: str, new_text: str) -> str:
    start, end = find_unique_span(value, old_text)
    return value[:start] + new_text + value[end:]

def insert_before(value: str, anchor: str, insertion: str) -> str:
    start, _ = find_unique_span(value, anchor)
    return value[:start].rstrip() + insertion.strip() + value[start:]

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
    for spec in assembly["items"]:
        notice_id = spec["notice_id"]
        node = skeleton_by_id.get(notice_id)
        coverage = replay_by_id.get(notice_id)
        baseline = snapshot_by_id.get(spec["baseline_snapshot_id"])
        if not node or not coverage or not baseline or not baseline.get("body_text"):
            raise RuntimeError(f"Incomplete assembly inputs for {notice_id}")
        candidate = baseline["body_text"].strip()
        evidence = [{
            "snapshot_id": baseline["id"], "source_id": baseline["source_id"], "role": "baseline",
            "page_start": baseline["page_start"], "page_end": baseline["page_end"],
            "body_text_sha256": baseline["body_text_sha256"],
        }]
        patch_ids = []
        for patch in spec.get("patches", []):
            snapshot = snapshot_by_id.get(patch["snapshot_id"])
            if not snapshot or snapshot["notice_id"] != notice_id or not snapshot.get("body_text"):
                raise RuntimeError(f"Invalid patch snapshot: {patch['snapshot_id']}")
            operation = patch["operation"]
            if operation == "replace_between":
                candidate = replace_between(candidate, patch["start_anchor"], patch["end_anchor"], snapshot["body_text"])
            elif operation == "replace_to_end":
                candidate = replace_to_end(candidate, patch["start_anchor"], snapshot["body_text"])
            elif operation == "replace_literal":
                candidate = replace_literal(candidate, patch["old_text"], patch["new_text"])
            elif operation == "insert_before":
                candidate = insert_before(candidate, patch["anchor"], snapshot["body_text"])
            elif operation == "append":
                candidate = candidate.rstrip() + snapshot["body_text"].strip()
            else:
                raise RuntimeError(f"Unsupported patch operation: {operation}")
            if snapshot["id"] not in patch_ids:
                patch_ids.append(snapshot["id"])
            evidence.append({
                "snapshot_id": snapshot["id"], "source_id": snapshot["source_id"], "role": "patch",
                "page_start": snapshot["page_start"], "page_end": snapshot["page_end"],
                "body_text_sha256": snapshot["body_text_sha256"], "operation": operation,
                "note": patch.get("note"),
            })
        candidate = candidate.strip() + "\n"
        output.append({
            "notice_id": notice_id,
            "number_path": node["number_path"],
            "title": node["title"],
            "effective_as_of": assembly["effective_as_of"],
            "baseline_snapshot_id": baseline["id"],
            "patch_snapshot_ids": patch_ids,
            "replay_status": coverage["replay_status"],
            "replay_coverage_as_of": coverage["coverage_as_of"],
            "reconstruction_status": assembly["reconstruction_status"],
            "human_verification_status": "NOT_REVIEWED",
            "evidence": evidence,
            "candidate_text_sha256": sha256_text(candidate),
            "candidate_text": candidate,
        })

    result = {
        "format_version": 1,
        "generator": "scripts/assemble_notice_operation_legacy_current_candidates.py",
        "policy": assembly["policy"],
        "effective_as_of": assembly["effective_as_of"],
        "reconstruction_status": assembly["reconstruction_status"],
        "items": output,
    }
    output_path = ROOT / assembly["output_path"]
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}: {len(output)} operation-legacy current-text candidates")

if __name__ == "__main__":
    main()
