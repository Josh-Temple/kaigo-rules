#!/usr/bin/env python3
"""Independently verify Notice 27 currentness against the live official MHLW display."""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "data/shared/remuneration-delegated"
SOURCE_ID = "mhlw-fee-notice27-base"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-notice27-currentness-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = response.read()
        charset = response.headers.get_content_charset()
    for encoding in (charset, "utf-8", "cp932", "shift_jis"):
        if not encoding:
            continue
        try:
            return payload, payload.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return payload, payload.decode("utf-8", errors="replace")


def main() -> None:
    contract = load(SHARED / "currentness-source-contract.json")
    receipt = load(SHARED / "item-body-verification.json")
    evidence = load(SHARED / "notice27-currentness-evidence.json")
    sources = {row["id"]: row for row in load(ROOT / "data/sources.json")}

    source_contract = next(
        row for row in contract["source_contracts"]
        if row["canonical_source_id"] == SOURCE_ID
    )
    receipt_source = next(
        row for row in receipt["source_verifications"]
        if row["source_id"] == SOURCE_ID
    )
    registry = sources[SOURCE_ID]

    if source_contract["official_source_url"] != receipt_source["official_url"]:
        raise SystemExit("Notice 27 contract URL differs from item-body receipt")
    if source_contract["official_source_url"] != registry["url"]:
        raise SystemExit("Notice 27 contract URL differs from canonical source registry")
    if source_contract.get("currentness_state") != "PASS" or source_contract.get("promotion_eligible") is not True:
        raise SystemExit("Notice 27 source contract is not explicit PASS")
    if registry.get("status") != "current_official_source":
        raise SystemExit("Notice 27 canonical source registry is not current_official_source")
    if evidence.get("decision") != "PASS" or evidence.get("promotion_eligible") is not True:
        raise SystemExit("Notice 27 evidence artifact is not PASS")

    snapshots = (source_contract.get("version_model") or {}).get("page_snapshots")
    if snapshots != receipt_source.get("page_snapshots"):
        raise SystemExit("Notice 27 currentness fingerprint differs from item-body fingerprint")

    all_text: list[str] = []
    for page in snapshots:
        page_no = int(page["page"])
        url = f"{source_contract['official_source_url']}&pageNo={page_no}"
        payload, html = fetch(url)
        actual_sha = hashlib.sha256(payload).hexdigest()
        if actual_sha != page["sha256"]:
            raise SystemExit(
                f"Notice 27 live page {page_no} SHA changed: "
                f"{actual_sha} != {page['sha256']}"
            )
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "style", "rt", "rp"]):
            tag.decompose()
        all_text.extend(str(value) for value in soup.stripped_strings)

    body = compact("\n".join(all_text))
    required_markers = [
        "厚生労働大臣が定める利用者等の数の基準及び看護職員等の員数の基準並びに通所介護費等の算定方法",
        "平成十二年二月十日",
        "厚生省告示第二十七号",
        "令和六年三月十五日厚生労働省告示第八五号",
        "令和六年三月十五日厚生労働省告示第八六号",
    ]
    missing = [marker for marker in required_markers if compact(marker) not in body]
    if missing:
        raise SystemExit(f"Notice 27 official current-display identity/amendment markers missing: {missing}")

    latest = (
        evidence.get("base_and_amendment_relationship", {})
        .get("latest_amendments_shown", [])
    )
    if [row.get("instrument") for row in latest] != [
        "令和6年厚生労働省告示第85号",
        "令和6年厚生労働省告示第86号",
    ]:
        raise SystemExit("Notice 27 evidence amendment lineage drifted")

    print(
        "Notice 27 live currentness verification: PASS "
        "(official current consolidated display, exact page SHA set, title identity, "
        "and latest displayed amendment lineage all match)"
    )


if __name__ == "__main__":
    main()
