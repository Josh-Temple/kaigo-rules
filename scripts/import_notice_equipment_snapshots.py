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
MANIFEST_PATH = ROOT / "data" / "notice-equipment-source-manifest.json"

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
                headers={"User-Agent": "kaigo-rules-notice-snapshot/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"}
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

def page_size_points(pdf_path: pathlib.Path, page: int) -> tuple[float, float]:
    proc = subprocess.run(
        ["pdfinfo", "-f", str(page), "-l", str(page), str(pdf_path)],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    info = proc.stdout.decode("utf-8", errors="strict")
    for pattern in (
        rf"Page\s+{page}\s+size:\s*([0-9.]+)\s+x\s+([0-9.]+)\s+pts",
        r"Page size:\s*([0-9.]+)\s+x\s*([0-9.]+)\s+pts",
    ):
        match = re.search(pattern, info)
        if match:
            return float(match.group(1)), float(match.group(2))
    raise RuntimeError(f"Could not determine page size for page {page}")

def extract_column(pdf_path: pathlib.Path, first: int, last: int, column: str, gutter_points: float = 4.0) -> str:
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
            "pdftotext", "-r", "72",
            "-f", str(first), "-l", str(last),
            "-layout",
            "-x", str(int(round(x))), "-y", "0",
            "-W", str(crop_width), "-H", str(int(round(height))),
            "-enc", "UTF-8", str(pdf_path), "-"
        ],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    return clean_text(proc.stdout)

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
    second = normalized_value.find(start_needle, start + len(start_needle))
    if second >= 0 and second < end:
        raise RuntimeError(f"Ambiguous body boundary: {start_marker}")
    return value[positions[start]:positions[end]].strip() + "\n"

def clean_body_text(value: str) -> str:
    lines = []
    for line in value.replace("\f", "").split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if re.fullmatch(r"(?:-\s*)?\d{1,3}\s*-?", stripped):
            continue
        if "指定居宅サービス等及び指定介護予防サービス等に関する基準について（抄）" in stripped:
            continue
        if stripped in {"新", "旧", "改正後", "改正前"}:
            continue
        lines.append(stripped)
    # PDF line wrapping and column layout insert whitespace inside Japanese legal text.
    # Store a layout-independent character stream; source page/column hashes remain evidence.
    compact = re.sub(r"\s+", "", "".join(lines))
    return compact + ("\n" if compact else "")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Override output path from manifest")
    args = parser.parse_args()
    require_poppler()

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    source_by_id = {item["id"]: item for item in sources}
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    output_path = ROOT / (args.output or manifest["output_path"])
    layouts = manifest["source_layouts"]
    segments = manifest["segments"]

    source_ids = sorted({segment["source_id"] for segment in segments})
    for source_id in source_ids:
        if source_id not in source_by_id:
            raise RuntimeError(f"Missing source registry entry: {source_id}")
        if source_id not in layouts:
            raise RuntimeError(f"Missing source layout: {source_id}")

    source_records = []
    segment_records = []

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        pdf_paths = {}
        for source_id in source_ids:
            source = source_by_id[source_id]
            data = download(source["url"])
            pdf_path = tmpdir / f"{source_id}.pdf"
            pdf_path.write_bytes(data)
            pdf_paths[source_id] = pdf_path
            source_records.append({
                "source_id": source_id,
                "url": source["url"],
                "sha256": hashlib.sha256(data).hexdigest(),
                "byte_length": len(data),
                "current_column": layouts[source_id]["current_column"],
                "header_semantics": layouts[source_id]["header_semantics"],
            })

        for segment in segments:
            source_id = segment["source_id"]
            first = int(segment["page_start"])
            last = int(segment["page_end"])
            current_column = layouts[source_id]["current_column"]
            column_text = extract_column(pdf_paths[source_id], first, last, current_column)
            normalized_column = normalized(column_text)
            missing = [
                anchor for anchor in segment.get("must_contain", [])
                if normalized(anchor) not in normalized_column
            ]
            if missing:
                raise RuntimeError(
                    f"{segment['id']}: anchors absent from {current_column} column "
                    f"pages {first}-{last}: {missing}"
                )
            body_text = clean_body_text(slice_by_normalized_markers(
                column_text, segment["body_start"], segment["body_end"]
            ))
            segment_records.append({
                "id": segment["id"],
                "notice_id": segment["notice_id"],
                "source_id": source_id,
                "role": segment["role"],
                "page_start": first,
                "page_end": last,
                "current_column": current_column,
                "note": segment.get("note"),
                "column_text_sha256": hashlib.sha256(column_text.encode("utf-8")).hexdigest(),
                "body_text_sha256": hashlib.sha256(body_text.encode("utf-8")).hexdigest(),
                "verification_status": "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK",
                "body_text": body_text,
            })

    result = {
        "format_version": 1,
        "generator": "scripts/import_notice_equipment_snapshots.py",
        "extraction_engine": "pdftotext -layout + declared-column crop + normalized body boundaries",
        "policy": manifest["policy"],
        "sources": source_records,
        "segments": segment_records,
    }
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}: {len(segment_records)} equipment source segments")

if __name__ == "__main__":
    main()
