#!/usr/bin/env python3
"""Independent item-body verifier for care-management standards interpretation staging.

This verifier is deliberately service-specific. It checks the committed audit receipt
against the staging dataset and, with --live, re-fetches the cited official MHLW
sources and verifies short evidence anchors. It does not establish currentness,
human review, or publication readiness.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "care-management"
EXPECTED_ITEMS = 32
STAGING = ROOT / "data/services/care-management/standards-interpretation-staging.json"
RECEIPT = ROOT / "data/verification/standards-interpretation-item-body/care-management.json"


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip:
            self.parts.append(data)


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", "", text)


def fetch_bytes(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-care-management-item-body-verifier/1.0"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def extract_text(url: str, body: bytes) -> str:
    if url.lower().endswith(".pdf"):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = Path(tmp) / "source.pdf"
            txt = Path(tmp) / "source.txt"
            pdf.write_bytes(body)
            proc = subprocess.run(
                ["pdftotext", "-layout", str(pdf), str(txt)],
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError(f"pdftotext failed for {url}: {proc.stderr.strip()}")
            return txt.read_text(encoding="utf-8", errors="replace")
    parser = _TextHTMLParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    return "\n".join(parser.parts)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"care-management item-body verification failed: {message}")


def validate_receipt(staging: dict, receipt: dict) -> None:
    if receipt.get("service_id") != SERVICE_ID:
        fail("service_id mismatch")
    if receipt.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_ITEM_BODY_AUDIT":
        fail("audit_kind mismatch")
    checks = receipt.get("checks", [])
    if len(checks) != EXPECTED_ITEMS:
        fail(f"expected {EXPECTED_ITEMS} checks, got {len(checks)}")
    staging_ids = [item["id"] for item in staging.get("items", [])]
    check_ids = [item["id"] for item in checks]
    if staging_ids != check_ids:
        fail("receipt item order/identity differs from staging")
    counts = {"PASS": 0, "PARTIAL": 0, "GAP": 0, "FAIL": 0}
    for item in checks:
        status = item.get("result")
        if status not in counts:
            fail(f"invalid result for {item.get('id')}: {status}")
        counts[status] += 1
        if not item.get("source_evidence"):
            fail(f"missing source_evidence for {item.get('id')}")
    if receipt.get("result_counts") != counts:
        fail(f"result_counts mismatch: expected {counts}")
    safety = receipt.get("safety", {})
    required_false = [
        "currentness_established",
        "human_review_completed",
        "publication_ready",
        "route_enabled",
        "automatic_promotion_allowed",
    ]
    if any(safety.get(key) is not False for key in required_false):
        fail("unsafe assurance state")
    if safety.get("content_evidence_match_only") is not True:
        fail("content_evidence_match_only must be true")


def run_live(receipt: dict) -> None:
    sources = {source["id"]: source for source in receipt["sources"]}
    cache: dict[str, str] = {}
    for check in receipt["checks"]:
        for evidence in check["source_evidence"]:
            source_id = evidence["source_id"]
            anchors = evidence.get("anchors", [])
            if not anchors:
                continue
            if source_id not in sources:
                fail(f"{check['id']}: unknown source {source_id}")
            if source_id not in cache:
                source = sources[source_id]
                body = fetch_bytes(source["url"])
                cache[source_id] = normalize(extract_text(source["url"], body))
            haystack = cache[source_id]
            missing = [anchor for anchor in anchors if normalize(anchor) not in haystack]
            if missing:
                fail(f"{check['id']}: missing anchors in {source_id}: {missing}")
    print("care-management item-body live anchors: OK")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="re-fetch MHLW sources and verify anchors")
    args = parser.parse_args()
    staging = load_json(STAGING)
    receipt = load_json(RECEIPT)
    if staging.get("service_id") != SERVICE_ID or staging.get("task_count") != EXPECTED_ITEMS:
        fail("unexpected staging identity/count")
    validate_receipt(staging, receipt)
    if args.live:
        run_live(receipt)
    counts = receipt["result_counts"]
    print(
        "care-management item-body audit: OK "
        f"({EXPECTED_ITEMS} items; PASS={counts['PASS']} PARTIAL={counts['PARTIAL']} "
        f"GAP={counts['GAP']} FAIL={counts['FAIL']}; currentness not established)"
    )


if __name__ == "__main__":
    main()
