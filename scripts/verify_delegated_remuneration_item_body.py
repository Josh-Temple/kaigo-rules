#!/usr/bin/env python3
"""Independently re-fetch and compare the delegated-remuneration shared corpus.

The canonical importer uses Python's HTMLParser. This verifier intentionally
uses BeautifulSoup and independently reconstructs source sections before
comparing normalized full item bodies. It does not promote currentness or any
other assurance axis.
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SHARED = DATA / "shared" / "remuneration-delegated"

TOP_HEADING = re.compile(
    r"^([一二三四五六七八九十百千]+(?:の[一二三四五六七八九十百千]+)*"
    r"(?:及び[一二三四五六七八九十百千]+(?:の[一二三四五六七八九十百千]+)*)?)\s+(.+)$"
)
STOP_PREFIXES = ("改正文", "附則")
KANJI_DIGITS = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
KANJI_UNITS = {"十": 10, "百": 100, "千": 1000}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def clean(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value)).split())


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-delegated-item-body-verifier/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
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


def visible_fragments(html: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(["script", "style", "rt", "rp"]):
        tag.decompose()
    return [clean(value) for value in soup.stripped_strings if clean(value)]


def page_body(lines: list[str]) -> list[str]:
    markers = [index for index, value in enumerate(lines) if value == "添付画像はありません"]
    if not markers:
        raise RuntimeError("MHLW page body boundary not found")
    body: list[str] = []
    for value in lines[markers[-1] + 1:]:
        if any(value.startswith(prefix) for prefix in STOP_PREFIXES):
            break
        body.append(value)
    if not body:
        raise RuntimeError("MHLW page body is empty")
    return body


def kanji_number(value: str) -> int:
    if value.isdigit():
        return int(value)
    total = 0
    current = 0
    for char in value:
        if char in KANJI_DIGITS:
            current = KANJI_DIGITS[char]
        elif char in KANJI_UNITS:
            total += (current or 1) * KANJI_UNITS[char]
            current = 0
        else:
            raise ValueError(f"unsupported Japanese numeral: {value}")
    return total + current


def single_label_key(value: str) -> str:
    return "-".join(str(kanji_number(part)) for part in value.split("の"))


def label_key(value: str) -> str:
    return "-and-".join(single_label_key(part) for part in value.split("及び"))


def reconstruct_source(source_id: str, official_url: str, page_rows: list[dict]) -> dict[str, str]:
    tagged: list[tuple[int, str]] = []
    for page in page_rows:
        page_no = int(page["page"])
        url = f"{official_url}&pageNo={page_no}"
        payload, html = fetch(url)
        actual_sha = hashlib.sha256(payload).hexdigest()
        if actual_sha != page["sha256"]:
            raise RuntimeError(
                f"{source_id} page {page_no}: official snapshot SHA changed "
                f"{actual_sha} != {page['sha256']}"
            )
        tagged.extend((page_no, value) for value in page_body(visible_fragments(html)))

    candidates: list[tuple[int, str, str]] = []
    for index, (_, value) in enumerate(tagged):
        match = TOP_HEADING.match(value)
        if match:
            candidates.append((index, match.group(1), value))

    headings: list[tuple[int, str, str]] = []
    last_key: tuple[int, ...] | None = None
    for candidate in candidates:
        first = candidate[1].split("及び", 1)[0]
        key = tuple(kanji_number(part) for part in first.split("の"))
        if last_key is None or key > last_key:
            headings.append(candidate)
            last_key = key

    if not headings:
        raise RuntimeError(f"{source_id}: no top-level headings found by independent parser")

    prefix = {
        "mhlw-fee-notice27-base": "notice27.item.",
        "mhlw-fee-criteria95-current": "notice95.item.",
        "mhlw-fee-facility-criteria96-current": "notice96.item.",
    }[source_id]

    result: dict[str, str] = {}
    for position, (start, raw_label, _) in enumerate(headings):
        end = headings[position + 1][0] if position + 1 < len(headings) else len(tagged)
        result[prefix + label_key(raw_label)] = "\n".join(value for _, value in tagged[start:end]).strip()
    return result


def main() -> None:
    corpus = load(SHARED / "national-corpus.json")
    receipt = load(SHARED / "item-body-verification.json")
    identity = load(SHARED / "node-identity-map.json")
    legacy = {row["id"]: row for row in load(DATA / "remuneration-delegated-nodes.json")}

    identity_by_canonical = {
        row["canonical_node_id"]: row for row in identity.get("nodes", [])
    }
    canonical_by_id = {
        row["canonical_node_id"]: row for row in corpus.get("nodes", [])
    }

    live_by_id: dict[str, str] = {}
    for source in receipt.get("source_verifications", []):
        if source.get("result") != "PASS":
            raise SystemExit(f"{source.get('source_id')}: receipt is not PASS")
        observed = reconstruct_source(
            source["source_id"],
            source["official_url"],
            source["page_snapshots"],
        )
        expected_ids = {
            node_id for node_id, node in canonical_by_id.items()
            if node.get("source_id") == source["source_id"]
        }
        if set(observed) != expected_ids:
            missing = sorted(expected_ids - set(observed))
            extra = sorted(set(observed) - expected_ids)
            raise SystemExit(
                f"{source['source_id']}: canonical node identity mismatch "
                f"missing={missing[:10]} extra={extra[:10]}"
            )
        if len(observed) != source.get("canonical_node_count"):
            raise SystemExit(f"{source['source_id']}: receipt node count mismatch")
        live_by_id.update(observed)

    mismatches: list[str] = []
    for canonical_id, node in canonical_by_id.items():
        storage = node.get("text_storage") or {}
        if storage.get("kind") == "INLINE_SHARED_CORPUS":
            canonical_text = str(node.get("official_text") or "")
        elif storage.get("kind") == "LEGACY_REFERENCE":
            legacy_id = storage.get("legacy_node_id")
            canonical_text = str((legacy.get(legacy_id) or {}).get("official_text") or "")
        else:
            mismatches.append(f"{canonical_id}: unsupported text storage")
            continue
        if not canonical_text:
            mismatches.append(f"{canonical_id}: canonical item body missing")
            continue
        exact_hash = hashlib.sha256(canonical_text.encode("utf-8")).hexdigest()
        if exact_hash != node.get("text_sha256"):
            mismatches.append(f"{canonical_id}: canonical text_sha256 mismatch")
            continue
        if compact(canonical_text) != compact(live_by_id.get(canonical_id, "")):
            mismatches.append(f"{canonical_id}: official body comparison mismatch")

    compatibility_pass = 0
    for check in receipt.get("compatibility_node_verifications", []):
        canonical_id = check["canonical_node_id"]
        legacy_id = check["legacy_node_id"]
        parent_id = check["parent_canonical_node_id"]
        legacy_text = str((legacy.get(legacy_id) or {}).get("official_text") or "")
        parent_live = live_by_id.get(parent_id, "")
        identity_row = identity_by_canonical.get(canonical_id) or {}
        if check.get("result") != "PASS":
            mismatches.append(f"{canonical_id}: compatibility receipt not PASS")
            continue
        if not legacy_text or compact(legacy_text) not in compact(parent_live):
            mismatches.append(f"{canonical_id}: compatibility body not found in official parent")
            continue
        if hashlib.sha256(legacy_text.encode("utf-8")).hexdigest() != identity_row.get("text_sha256"):
            mismatches.append(f"{canonical_id}: compatibility text hash mismatch")
            continue
        compatibility_pass += 1

    if mismatches:
        raise SystemExit("\n".join(f"ERROR: {value}" for value in mismatches))

    expected = receipt.get("coverage", {}).get("verified_canonical_top_level_nodes")
    if len(canonical_by_id) != expected:
        raise SystemExit(f"verified node count mismatch: {len(canonical_by_id)} != {expected}")

    print(
        "delegated remuneration independent item-body verification: PASS "
        f"({len(canonical_by_id)} canonical nodes, {compatibility_pass} compatibility subnodes, "
        f"{len(receipt.get('source_verifications', []))} official source documents)"
    )


if __name__ == "__main__":
    main()
