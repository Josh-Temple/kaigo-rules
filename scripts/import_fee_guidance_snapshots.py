#!/usr/bin/env python3
import argparse
import hashlib
import json
import pathlib
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

def download(url: str, attempts: int = 3) -> bytes:
    last = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "kaigo-rules-source-snapshot/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"}
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

def extract_pages(pdf_path: pathlib.Path, first: int, last: int) -> str:
    if shutil.which("pdftotext") is None:
        raise RuntimeError("pdftotext is required (install poppler-utils)")
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
    text = proc.stdout.decode("utf-8", errors="strict").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", help="Override output path from manifest")
    args = parser.parse_args()

    sources = json.loads(SOURCES_PATH.read_text(encoding="utf-8"))
    source_by_id = {item["id"]: item for item in sources}
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    output_path = ROOT / (args.output or manifest["output_path"])
    segments = manifest["segments"]

    source_ids = sorted({segment["source_id"] for segment in segments})
    missing = [source_id for source_id in source_ids if source_id not in source_by_id]
    if missing:
        raise RuntimeError("Missing source registry entries: " + ", ".join(missing))

    source_records = []
    segment_records = []

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = pathlib.Path(tmp)
        pdf_paths = {}

        for source_id in source_ids:
            source = source_by_id[source_id]
            data = download(source["url"])
            sha = hashlib.sha256(data).hexdigest()
            pdf_path = tmpdir / f"{source_id}.pdf"
            pdf_path.write_bytes(data)
            pdf_paths[source_id] = pdf_path
            source_records.append({
                "source_id": source_id,
                "url": source["url"],
                "sha256": sha,
                "byte_length": len(data)
            })

        for segment in segments:
            text = extract_pages(
                pdf_paths[segment["source_id"]],
                int(segment["page_start"]),
                int(segment["page_end"])
            )
            normalized_text = normalized(text)
            missing_anchors = [
                anchor for anchor in segment.get("must_contain", [])
                if normalized(anchor) not in normalized_text
            ]
            if missing_anchors:
                raise RuntimeError(
                    f"{segment['id']}: expected anchors not found in pages "
                    f"{segment['page_start']}-{segment['page_end']}: {missing_anchors}"
                )

            segment_records.append({
                "id": segment["id"],
                "guidance_ids": segment["guidance_ids"],
                "source_id": segment["source_id"],
                "role": segment["role"],
                "page_start": segment["page_start"],
                "page_end": segment["page_end"],
                "note": segment.get("note"),
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "verification_status": "IMPORTED_OFFICIAL_PDF_NEEDS_HUMAN_CHECK",
                "text": text
            })

    result = {
        "format_version": 1,
        "generator": "scripts/import_fee_guidance_snapshots.py",
        "extraction_engine": "pdftotext -layout",
        "policy": manifest["policy"],
        "sources": source_records,
        "segments": segment_records
    }

    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {output_path.relative_to(ROOT)}: {len(segment_records)} segments from {len(source_records)} sources")

if __name__ == "__main__":
    main()
