#!/usr/bin/env python3
"""Materialize the national delegated-remuneration corpus from canonical MHLW pages.

This importer reads only the source documents already registered in the
repository for the delegated-remuneration slice (Notice 27 and Notice 95).
It builds one national top-level section corpus. Existing legacy dayservice
text is referenced rather than copied when the live section is semantically
identical.

Writing the corpus does not establish currentness, human review, publication,
route exposure, or service applicability beyond separately maintained mapping.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "shared" / "remuneration-delegated" / "national-corpus.json"
IDENTITY = DATA / "shared" / "remuneration-delegated" / "node-identity-map.json"
LEGACY_NODES = DATA / "remuneration-delegated-nodes.json"
SOURCES = DATA / "sources.json"

SOURCE_SPECS = (
    {
        "source_id": "mhlw-fee-notice27-base",
        "data_id": "82aa0261",
        "expected_pages": 3,
        "id_prefix": "notice27.item.",
    },
    {
        "source_id": "mhlw-fee-criteria95-current",
        "data_id": "82ab4584",
        "expected_pages": 4,
        "id_prefix": "notice95.item.",
    },
)

TOP_HEADING = re.compile(
    r"^([一二三四五六七八九十百千]+(?:の[一二三四五六七八九十百千]+)?"
    r"(?:及び[一二三四五六七八九十百千]+(?:の[一二三四五六七八九十百千]+)?)?)\s+(.+)$"
)
PAGE_COUNT = re.compile(r"該当ページ数[:：]\s*(\d+)ページ中(\d+)ページ")
STOP_PREFIXES = ("改正文", "附則")
KANJI_DIGITS = {"〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
KANJI_UNITS = {"十": 10, "百": 100, "千": 1000}


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.suppressed_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "rt", "rp"}:
            self.suppressed_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "rt", "rp"} and self.suppressed_depth:
            self.suppressed_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.suppressed_depth:
            return
        value = clean(data)
        if value:
            self.fragments.append(value)


def clean(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", str(value)).split())


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "kaigo-rules-national-delegated-corpus/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
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
    parser = VisibleTextParser()
    parser.feed(html)
    parser.close()
    return parser.fragments


def page_body(lines: list[str]) -> list[str]:
    attachment_markers = [
        index for index, line in enumerate(lines)
        if line == "添付画像はありません"
    ]
    if not attachment_markers:
        raise RuntimeError("MHLW page attachment/navigation boundary not found")
    body = lines[attachment_markers[-1] + 1:]
    result = []
    for line in body:
        if any(line.startswith(prefix) for prefix in STOP_PREFIXES):
            break
        result.append(line)
    return result


def parse_page_count(lines: list[str], expected_current: int) -> int:
    for line in lines:
        match = PAGE_COUNT.search(line)
        if match:
            total, current = int(match.group(1)), int(match.group(2))
            if current != expected_current:
                raise RuntimeError(f"unexpected current page marker: expected {expected_current}, got {current}")
            return total
    raise RuntimeError("MHLW page-count marker not found")


def kanji_number(value: str) -> int:
    if value.isdigit():
        return int(value)
    total = 0
    current_digit = 0
    for char in value:
        if char in KANJI_DIGITS:
            current_digit = KANJI_DIGITS[char]
        elif char in KANJI_UNITS:
            unit = KANJI_UNITS[char]
            total += (current_digit or 1) * unit
            current_digit = 0
        else:
            raise ValueError(f"unsupported Japanese numeral: {value}")
    return total + current_digit


def single_label_key(value: str) -> str:
    return "-".join(str(kanji_number(part)) for part in value.split("の"))


def label_key(value: str) -> str:
    return "-and-".join(single_label_key(part) for part in value.split("及び"))


def build_live(observed_date: str | None = None) -> dict[str, Any]:
    observed_date = observed_date or date.today().isoformat()
    sources = load(SOURCES)
    source_by_id = {row["id"]: row for row in sources}
    identity_rows = load(IDENTITY).get("nodes", [])
    legacy_nodes = {row["id"]: row for row in load(LEGACY_NODES)}
    legacy_by_canonical = {
        row["canonical_node_id"]: row["legacy_node_id"]
        for row in identity_rows
        if row["legacy_node_id"] not in {
            "calc27.dayservice.1.capacity",
            "calc27.dayservice.1.staffing",
        }
    }

    documents = []
    nodes = []

    for spec in SOURCE_SPECS:
        source_id = spec["source_id"]
        source = source_by_id.get(source_id)
        if not source:
            raise RuntimeError(f"canonical source missing from data/sources.json: {source_id}")

        tagged_lines: list[tuple[int, str]] = []
        pages = []
        for page_number in range(1, spec["expected_pages"] + 1):
            url = f"https://www.mhlw.go.jp/web/t_doc?dataId={spec['data_id']}&dataType=0&pageNo={page_number}"
            payload, html = fetch(url)
            lines = visible_fragments(html)
            total = parse_page_count(lines, page_number)
            if total != spec["expected_pages"]:
                raise RuntimeError(
                    f"{source_id}: official page count changed: expected {spec['expected_pages']}, got {total}"
                )
            body = page_body(lines)
            if not body:
                raise RuntimeError(f"{source_id}: page {page_number} body is empty")
            tagged_lines.extend((page_number, line) for line in body)
            pages.append({
                "page": page_number,
                "url": url,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "body_fragment_count": len(body),
            })

        headings: list[tuple[int, str, str]] = []
        for index, (_, line) in enumerate(tagged_lines):
            match = TOP_HEADING.match(line)
            if match:
                headings.append((index, match.group(1), line))

        if not headings:
            raise RuntimeError(f"{source_id}: no top-level headings found")
        canonical_ids = []
        for position, (start, raw_label, heading) in enumerate(headings):
            end = headings[position + 1][0] if position + 1 < len(headings) else len(tagged_lines)
            section = tagged_lines[start:end]
            section_text = "\n".join(line for _, line in section).strip()
            if not section_text:
                raise RuntimeError(f"{source_id}: empty section at {heading}")
            canonical_id = spec["id_prefix"] + label_key(raw_label)
            canonical_ids.append(canonical_id)
            page_numbers = []
            for page_number, _ in section:
                if page_number not in page_numbers:
                    page_numbers.append(page_number)

            node = {
                "canonical_node_id": canonical_id,
                "source_id": source_id,
                "item_label": raw_label,
                "heading": heading,
                "parent_canonical_node_id": None,
                "source_locator": {
                    "pages": page_numbers,
                    "heading": heading,
                },
                "text_sha256": sha256_text(section_text),
                "effective_context": {
                    "observed_date": observed_date,
                    "currentness_state": "NOT_ESTABLISHED",
                    "human_review": "NOT_REVIEWED",
                },
            }

            legacy_id = legacy_by_canonical.get(canonical_id)
            if legacy_id:
                legacy_text = legacy_nodes[legacy_id]["official_text"]
                if compact(legacy_text) != compact(section_text):
                    raise RuntimeError(
                        f"{canonical_id}: live national section differs from legacy compatibility text"
                    )
                node["text_storage"] = {
                    "kind": "LEGACY_REFERENCE",
                    "legacy_node_id": legacy_id,
                    "path": "data/remuneration-delegated-nodes.json",
                }
            else:
                node["text_storage"] = {"kind": "INLINE_SHARED_CORPUS"}
                node["official_text"] = section_text
            nodes.append(node)

        if len(canonical_ids) != len(set(canonical_ids)):
            raise RuntimeError(f"{source_id}: duplicate canonical top-level IDs")
        documents.append({
            "source_id": source_id,
            "title": source.get("title"),
            "publisher": source.get("publisher"),
            "official_url": source.get("url"),
            "expected_pages": spec["expected_pages"],
            "observed_pages": len(pages),
            "pages": pages,
            "top_level_node_count": len(canonical_ids),
        })

    ids = [row["canonical_node_id"] for row in nodes]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate canonical node IDs across national corpus")

    return {
        "format_version": 1,
        "corpus_id": "delegated-remuneration-national",
        "source_family": "delegated_remuneration_criteria",
        "scope_kind": "SHARED_NATIONAL_CORPUS",
        "observed_date": observed_date,
        "source_selection": {
            "basis": "canonical source IDs already registered in data/sources.json",
            "included_source_ids": [spec["source_id"] for spec in SOURCE_SPECS],
            "unregistered_notice_numbers_inferred": False,
        },
        "coverage": {
            "source_documents": len(documents),
            "source_pages": sum(row["observed_pages"] for row in documents),
            "top_level_nodes": len(nodes),
            "legacy_text_references": sum(
                1 for row in nodes
                if row["text_storage"]["kind"] == "LEGACY_REFERENCE"
            ),
            "inline_shared_nodes": sum(
                1 for row in nodes
                if row["text_storage"]["kind"] == "INLINE_SHARED_CORPUS"
            ),
            "coverage_kind": "FULL_TOP_LEVEL_SECTIONS_OF_REGISTERED_CANONICAL_SOURCES",
        },
        "documents": documents,
        "nodes": nodes,
        "assurance": {
            "item_body_verification": "NOT_ESTABLISHED",
            "currentness": "NOT_ESTABLISHED",
            "service_applicability_verification": "NOT_ESTABLISHED",
            "service_relation_verification": "NOT_ESTABLISHED",
            "human_review": "NOT_REVIEWED",
            "publication": "BLOCKED",
            "route_exposure": "BLOCKED",
            "automatic_promotion_allowed": False,
        },
    }


def validate_committed(corpus: dict[str, Any]) -> None:
    if corpus.get("corpus_id") != "delegated-remuneration-national":
        raise RuntimeError("unexpected corpus_id")
    if corpus.get("scope_kind") != "SHARED_NATIONAL_CORPUS":
        raise RuntimeError("unexpected scope_kind")
    coverage = corpus.get("coverage") or {}
    if coverage.get("source_documents") != len(SOURCE_SPECS):
        raise RuntimeError("source document coverage mismatch")
    if coverage.get("source_pages") != sum(spec["expected_pages"] for spec in SOURCE_SPECS):
        raise RuntimeError("source page coverage mismatch")
    nodes = corpus.get("nodes") or []
    if coverage.get("top_level_nodes") != len(nodes):
        raise RuntimeError("node count mismatch")
    ids = [row.get("canonical_node_id") for row in nodes]
    if None in ids or len(ids) != len(set(ids)):
        raise RuntimeError("canonical node IDs missing or duplicated")
    if len(nodes) <= len(load(LEGACY_NODES)):
        raise RuntimeError("national corpus did not expand beyond legacy dayservice fragments")
    for row in nodes:
        storage = row.get("text_storage") or {}
        kind = storage.get("kind")
        if kind == "LEGACY_REFERENCE":
            if "official_text" in row:
                raise RuntimeError(f"{row['canonical_node_id']}: legacy reference duplicates official_text")
            legacy_id = storage.get("legacy_node_id")
            if legacy_id not in {node["id"] for node in load(LEGACY_NODES)}:
                raise RuntimeError(f"{row['canonical_node_id']}: legacy reference target missing")
        elif kind == "INLINE_SHARED_CORPUS":
            if not row.get("official_text"):
                raise RuntimeError(f"{row['canonical_node_id']}: shared text missing")
        else:
            raise RuntimeError(f"{row['canonical_node_id']}: invalid text storage kind")
    assurance = corpus.get("assurance") or {}
    for key in (
        "item_body_verification",
        "currentness",
        "service_applicability_verification",
        "service_relation_verification",
    ):
        if assurance.get(key) != "NOT_ESTABLISHED":
            raise RuntimeError(f"automatic assurance promotion detected: {key}")
    if assurance.get("automatic_promotion_allowed") is not False:
        raise RuntimeError("automatic promotion must remain disabled")


def comparable(corpus: dict[str, Any]) -> dict[str, Any]:
    value = json.loads(json.dumps(corpus))
    value["observed_date"] = None
    for node in value.get("nodes", []):
        context = node.get("effective_context") or {}
        context["observed_date"] = None
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--verify-live", action="store_true")
    args = parser.parse_args()

    if args.check and args.verify_live:
        raise SystemExit("choose either --check or --verify-live")

    if args.check:
        if not OUT.exists():
            raise SystemExit("national delegated-remuneration corpus missing")
        committed = load(OUT)
        validate_committed(committed)
        print(
            "delegated remuneration national corpus: PASS "
            f"({committed['coverage']['source_documents']} documents, "
            f"{committed['coverage']['source_pages']} pages, "
            f"{committed['coverage']['top_level_nodes']} top-level nodes)"
        )
        return

    if args.verify_live:
        if not OUT.exists():
            raise SystemExit("national delegated-remuneration corpus missing")
        committed = load(OUT)
        validate_committed(committed)
        observed = build_live(observed_date=committed.get("observed_date"))
        if comparable(observed) != comparable(committed):
            raise SystemExit("live MHLW delegated-remuneration corpus differs from committed snapshot")
        print("delegated remuneration national corpus live reparse: PASS")
        return

    corpus = build_live()
    validate_committed(corpus)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(corpus, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"wrote {OUT.relative_to(ROOT)} "
        f"({corpus['coverage']['source_documents']} documents, "
        f"{corpus['coverage']['source_pages']} pages, "
        f"{corpus['coverage']['top_level_nodes']} top-level nodes)"
    )


if __name__ == "__main__":
    main()
