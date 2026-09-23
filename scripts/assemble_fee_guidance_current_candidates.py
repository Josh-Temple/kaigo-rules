#!/usr/bin/env python3
import hashlib
import json
import pathlib
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[1]
SNAPSHOTS_PATH = ROOT / "data" / "fee-guidance-source-snapshots.json"
ASSEMBLY_PATH = ROOT / "data" / "fee-guidance-current-assembly.json"
SKELETON_PATH = ROOT / "data" / "fee-guidance-current-skeleton.json"
REPLAY_PATH = ROOT / "data" / "fee-guidance-replay-coverage.json"
SUPPLEMENTS_PATH = ROOT / "data" / "fee-guidance-verified-text-supplements.json"

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

def insert_before_normalized(value: str, anchor: str, insertion: str) -> str:
    normalized_value, positions = normalize_with_map(value)
    needle = normalized(anchor)
    start = normalized_value.find(needle)
    if start < 0:
        raise RuntimeError(f"Assembly anchor not found: {anchor}")
    if normalized_value.find(needle, start + 1) >= 0:
        raise RuntimeError(f"Assembly anchor is not unique: {anchor}")
    source_index = positions[start]
    prefix = value[:source_index].rstrip()
    suffix = value[source_index:].lstrip()
    return prefix + "\n" + insertion.strip() + "\n" + suffix

def replace_normalized_once(value: str, before: str, after: str, label: str) -> str:
    normalized_value, positions = normalize_with_map(value)
    needle = normalized(before)
    first = normalized_value.find(needle)
    if first < 0:
        raise RuntimeError(f"{label}: replacement marker not found: {before}")
    second = normalized_value.find(needle, first + len(needle))
    if second >= 0:
        raise RuntimeError(f"{label}: replacement marker is not unique: {before}")
    start_original = positions[first]
    end_normalized = first + len(needle) - 1
    end_original = positions[end_normalized] + 1
    return value[:start_original] + after + value[end_original:]

def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def main() -> None:
    snapshots = json.loads(SNAPSHOTS_PATH.read_text(encoding="utf-8"))
    assembly = json.loads(ASSEMBLY_PATH.read_text(encoding="utf-8"))
    skeleton = json.loads(SKELETON_PATH.read_text(encoding="utf-8"))
    replay = json.loads(REPLAY_PATH.read_text(encoding="utf-8"))
    supplements = json.loads(SUPPLEMENTS_PATH.read_text(encoding="utf-8"))

    if int(snapshots.get("format_version", 0)) < 3:
        raise RuntimeError("fee-guidance-source-snapshots.json format_version >= 3 is required")

    snapshot_by_id = {item["id"]: item for item in snapshots["segments"]}
    guidance_by_id = {item["id"]: item for item in skeleton}
    replay_by_id = {item["guidance_id"]: item for item in replay}
    supplements_by_guidance = {}
    for supplement in supplements.get("supplements", []):
        supplements_by_guidance.setdefault(supplement["guidance_id"], []).append(supplement)

    output = []
    seen = set()

    for item in assembly["items"]:
        guidance_id = item["guidance_id"]
        if guidance_id in seen:
            raise RuntimeError(f"Duplicate assembly guidance_id: {guidance_id}")
        seen.add(guidance_id)

        guidance = guidance_by_id.get(guidance_id)
        coverage = replay_by_id.get(guidance_id)
        if not guidance:
            raise RuntimeError(f"Missing guidance node: {guidance_id}")
        if not coverage:
            raise RuntimeError(f"Missing replay coverage: {guidance_id}")

        baseline_id = item["baseline_snapshot_id"]
        baseline = snapshot_by_id.get(baseline_id)
        if not baseline or not baseline.get("item_text"):
            raise RuntimeError(f"Missing baseline item text: {baseline_id}")

        candidate_text = baseline["item_text"].strip() + "\n"
        evidence = [{
            "snapshot_id": baseline_id,
            "source_id": baseline["source_id"],
            "role": "baseline",
            "page_start": baseline["page_start"],
            "page_end": baseline["page_end"],
            "item_text_sha256": baseline["item_text_sha256"]
        }]

        for patch in item.get("patches", []):
            patch_snapshot = snapshot_by_id.get(patch["snapshot_id"])
            if not patch_snapshot:
                raise RuntimeError(f"Missing patch snapshot: {patch['snapshot_id']}")
            patch_field = patch.get("patch_field", "patch_text")
            patch_text = patch_snapshot.get(patch_field)
            if not patch_text:
                raise RuntimeError(f"Missing patch field {patch_field}: {patch['snapshot_id']}")
            if patch["operation"] != "insert_before":
                raise RuntimeError(f"Unsupported patch operation: {patch['operation']}")

            candidate_text = insert_before_normalized(
                candidate_text,
                patch["baseline_anchor"],
                patch_text
            ).strip() + "\n"

            evidence.append({
                "snapshot_id": patch["snapshot_id"],
                "source_id": patch_snapshot["source_id"],
                "role": "patch",
                "page_start": patch_snapshot["page_start"],
                "page_end": patch_snapshot["page_end"],
                "patch_text_sha256": patch_snapshot.get("patch_text_sha256"),
                "operation": patch["operation"],
                "baseline_anchor": patch["baseline_anchor"],
                "note": patch.get("note")
            })

        for supplement in supplements_by_guidance.get(guidance_id, []):
            for index, replacement in enumerate(supplement.get("replacements", []), start=1):
                candidate_text = replace_normalized_once(
                    candidate_text,
                    replacement["before"],
                    replacement["after"],
                    f"{supplement['id']} replacement {index}"
                )
            candidate_text = candidate_text.strip() + "\n"
            evidence.append({
                "supplement_id": supplement["id"],
                "role": "verified_text_supplement",
                "source_ids": supplement["source_ids"],
                "source_urls": supplement.get("source_urls", []),
                "page_ranges": supplement.get("page_ranges", []),
                "verified_at": supplement["verified_at"],
                "note": supplement.get("note"),
                "replacement_sha256": sha256_text(
                    "\n".join(
                        replacement["after"]
                        for replacement in supplement.get("replacements", [])
                    )
                )
            })

        output.append({
            "guidance_id": guidance_id,
            "number_path": guidance["number_path"],
            "title": guidance["title"],
            "effective_as_of": assembly["effective_as_of"],
            "baseline_snapshot_id": baseline_id,
            "patch_snapshot_ids": [patch["snapshot_id"] for patch in item.get("patches", [])],
            "replay_status": coverage["replay_status"],
            "replay_coverage_as_of": coverage["coverage_as_of"],
            "reconstruction_status": assembly["reconstruction_status"],
            "human_verification_status": "NOT_REVIEWED",
            "evidence": evidence,
            "candidate_text_sha256": sha256_text(candidate_text),
            "candidate_text": candidate_text
        })

    expected = {item["guidance_id"] for item in assembly["items"]}
    if {item["guidance_id"] for item in output} != expected:
        raise RuntimeError("Assembly output guidance IDs do not match config")

    result = {
        "format_version": 1,
        "generator": "scripts/assemble_fee_guidance_current_candidates.py",
        "policy": assembly["policy"],
        "effective_as_of": assembly["effective_as_of"],
        "reconstruction_status": assembly["reconstruction_status"],
        "items": output
    }

    output_path = ROOT / assembly["output_path"]
    output_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    print(f"Wrote {output_path.relative_to(ROOT)}: {len(output)} current-text candidates")

if __name__ == "__main__":
    main()
