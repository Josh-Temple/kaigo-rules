#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import time
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCES_PATH = ROOT / "data" / "sources.json"
MANIFEST_PATH = ROOT / "data" / "fee-guidance-source-manifest.json"

def normalized(value: str) -> str:
    return "".join(unicodedata.normalize("NFKC", value).split())

def clean_text(raw: bytes) -> str:
    text = raw.decode("utf-8", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")

def download(url: str, attempts: int = 3) -> bytes:
    last = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "kaigo-rules-source-snapshot/1.1 (+https://github.com/Josh-Temple/kaigo-rules)"}
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                data = response.read()
            if not data.startswith(b"%PDF"):
                raise RuntimeError(f"Downloaded content is not a PDF: {url}")
            return data
        except Exception as exc:
            last = exc
            if attempt + 1 < attempts:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Failed to download {url}: {last}")

def require_poppler() -> None:
    for command in ("pdftotext", "pdfinfo"):
        if shutil.which(command) is None:
            raise RuntimeError(f"{command} is required (install poppler-utils)")

def extract_pages(pdf_path: pathlib.Path, first: int, last: int) -> str:
    proc = subprocess.run(
        [
            "pdftotext",
            "-f", str(first),
            "-l", str(last),
            "-layout",
            "-enc", "UTF-8",
            str(pdf_path),
            "-"
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return clean_text(proc.stdout)

def page_size_points(pdf_path: pathlib.Path, page: int) -> tuple[float, float]:
    proc = subprocess.run(
        ["pdfinfo", "-f", str(page), "-l", str(page), str(pdf_path)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    info = proc.stdout.decode("utf-8", errors="strict")
    patterns = [
        rf"Page\s+{page}\s+size:\s*([0-9.]+)\s+x\s+([0-9.]+)\s+pts",
        r"Page size:\s*([0-9.]+)\s+x\s+([0-9.]+)\s+pts",
    ]
    for pattern in patterns:
        match = re.search(pattern, info)
        if match:
            return float(match.group(1)), float(match.group(2))
    raise RuntimeError(f"Could not determine page size for {pdf_path} page {page}")

def normalize_with_map(value: str) -> tuple[str, list[int]]:
    chars = []
    positions = []
    for index, source_char in enumerate(value):
        for char in unicodedata.normalize("NFKC", source_char):
            if char.isspace():
                continue
            chars.append(char)
            positions.append(index)
    return "".join(chars), positions

def slice_by_normalized_markers(value: str, start_marker: str, end_marker: str) -> str:
    normalized_value, positions = normalize_with_map(value)
    start_needle = normalized(start_marker)
    end_needle = normalized(end_marker)
    start = normalized_value.find(start_needle)
    if start < 0:
        raise RuntimeError(f"Start marker not found: {start_marker}")
    end = normalized_value.find(end_needle, start + len(start_needle))
    if end < 0:
        raise RuntimeError(f"End marker not found after start: {end_marker}")
    next_start = normalized_value.find(start_needle, start + len(start_needle))
    if next_start >= 0 and next_start < end:
        raise RuntimeError(
            f"Ambiguous item boundary: start marker repeats before end marker: {start_marker}"
        )
    start_original = positions[start]
    end_original = positions[end]
    return value[start_original:end_original].strip() + "\n"

def clean_item_text(value: str) -> str:
    lines = []
    for line in value.replace("\f", "").split("\n"):
        stripped = line.strip()
        if re.fullmatch(r"\d{1,3}", stripped or ""):
            continue
        lines.append(line.rstrip())
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")

def extract_current_column(
    pdf_path: pathlib.Path,
    first: int,
    last: int,
    column: str,
    gutter_points: float = 4.0
) -> str:
    if column not in {"left", "right"}:
        raise RuntimeError(f"Unexpected current column: {column}")

    width, height = page_size_points(pdf_path, first)
    half = width / 2.0
    gutter = min(gutter_points, half / 10.0)

    if column == "left":
        x = 0
        crop_width = max(1, int(round(half - gutter)))
    else:
        x = int(round(half + gutter))
        crop_width = max(1, int(round(width - x)))

    proc = subprocess.run(
        [
            "pdftotext",
            "-r", "72",
            "-f", str(first),
            "-l", str(last),
            "-layout",
            "-x", str(int(round(x))),
            "-y", "0",
            "-W", str(crop_width),
            "-H", str(int(round(height))),
            "-enc", "UTF-8",
            str(pdf_path),
            "-"
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return clean_text(proc.stdout)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Override output path from manifest")
    args = parser.parse_args()

    require_poppler()

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    source_by_id = {item["id"]: item for item in sources}
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    output_path = ROOT / (args.output or manifest["output_path"])
    segments = manifest["segments"]
    source_layouts = manifest.get("source_layouts", {})

    source_ids = sorted({segment["source_id"] for segment in segments})
    missing = [source_id for source_id in source_ids if source_id not in source_by_id]
    if missing:
        raise RuntimeError("Missing source registry entries: " + ", ".join(missing))

    missing_layouts = [source_id for source_id in source_ids if source_id not in source_layouts]
    if missing_layouts:
        raise RuntimeError("Missing source layout declarations: " + ", ".join(missing_layouts))

    source_records = []
    segment_records = []

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        pdf_paths = {}

        for source_id in source_ids:
            source = source_by_id[source_id]
            layout = source_layouts[source_id]
            data = download(source["url"])
            sha = hashlib.sha256(data).hexdigest()
            pdf_path = tmpdir / f"{source_id}.pdf"
            pdf_path.write_bytes(data)
            pdf_paths[source_id] = pdf_path
            source_records.append({
                "source_id": source_id,
                "url": source["url"],
                "sha256": sha,
                "byte_length": len(data),
                "current_column": layout["current_column"],
                "header_semantics": layout.get("header_semantics")
            })

        for segment in segments:
            source_id = segment["source_id"]
            current_column = source_layouts[source_id]["current_column"]
            first = int(segment["page_start"])
            last = int(segment["page_end"])

            full_text = extract_pages(pdf_paths[source_id], first, last)
            current_side_text = extract_current_column(
                pdf_paths[source_id],
                first,
                last,
                current_column
            )

            normalized_side = normalized(current_side_text)
            missing_anchors = [
                anchor for anchor in segment.get("must_contain", [])
                if normalized(anchor) not in normalized_side
            ]
            if missing_anchors:
                raise RuntimeError(
                    f"{segment['id']}: expected anchors not found in declared current-side "
                    f"{current_column} column, pages {first}-{last}: {missing_anchors}"
                )

            item_text = clean_item_text(slice_by_normalized_markers(
                current_side_text,
                segment["item_start"],
                segment["item_end"]
            ))

            record = {
                "id": segment["id"],
                "guidance_ids": segment["guidance_ids"],
                "source_id": source_id,
                "role": segment["role"],
                "page_start": first,
                "page_end": last,
                "note": segment.get("note"),
                "current_column": current_column,
                "text_sha256": hashlib.sha256(full_text.encode("utf-8")).hexdigest(),
                "current_side_text_sha256": hashlib.sha256(current_side_text.encode("utf-8")).hexdigest(),
                "item_text_sha256": hashlib.sha256(item_text.encode("utf-8")).hexdigest(),
                "verification_status": "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK",
                "text": full_text,
                "current_side_text": current_side_text,
                "item_text": item_text
            }

            if segment.get("patch_start") and segment.get("patch_end"):
                patch_text = clean_item_text(slice_by_normalized_markers(
                    current_side_text,
                    segment["patch_start"],
                    segment["patch_end"]
                ))
                record["patch_text_sha256"] = hashlib.sha256(patch_text.encode("utf-8")).hexdigest()
                record["patch_text"] = patch_text

            segment_records.append(record)

    result = {
        "format_version": 3,
        "generator": "scripts/import_fee_guidance_snapshots.py",
        "extraction_engine": "pdftotext -layout + declared-column crop + normalized item boundaries",
        "policy": manifest["policy"],
        "sources": source_records,
        "segments": segment_records
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(
        f"Wrote {output_path.relative_to(ROOT)}: "
        f"{len(segment_records)} segments from {len(source_records)} sources "
        f"with current-side column extraction"
    )

if __name__ == "__main__":
    main()
