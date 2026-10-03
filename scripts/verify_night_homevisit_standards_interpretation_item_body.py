#!/usr/bin/env python3
"""Validate the night-homevisit standards-interpretation item-body audit.

The receipt is the human-readable, item-level semantic verification record.
This service-specific checker binds it to the current staging dataset and,
optionally, independently re-fetches the official source roles to ensure
that their service/source anchors remain obtainable.

This does NOT prove currentness, human review, or publication readiness.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "night-homevisit"
STAGING = ROOT / "data/services/night-homevisit/standards-interpretation-staging.json"
AUDIT = ROOT / "data/verification/standards-interpretation-item-body/night-homevisit.json"
ALLOWED = {"PASS", "PARTIAL", "GAP", "FAIL"}
USER_AGENT = "kaigo-rules-night-homevisit-item-body/1.0"


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "rt", "rp"}:
            self.suppressed += 1
        elif tag.lower() in {"br", "div", "li", "p", "section", "table", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "rt", "rp"} and self.suppressed:
            self.suppressed -= 1
        elif tag.lower() in {"div", "li", "p", "section", "table", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.suppressed:
            self.parts.append(data)


def normalize(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFKC", html.unescape(value)),
    ).strip()


def extract_pdf(payload: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".pdf") as source:
        source.write(payload)
        source.flush()
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", source.name, "-"],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
    return normalize(result.stdout)


def extract_html(payload: bytes) -> str:
    decoded = None
    for encoding in ("utf-8", "cp932", "shift_jis", "euc_jp"):
        try:
            decoded = payload.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if decoded is None:
        decoded = payload.decode("utf-8", errors="replace")
    parser = VisibleText()
    parser.feed(decoded)
    parser.close()
    return normalize(" ".join(parser.parts))


def refetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = response.read()
        content_type = response.headers.get_content_type()
    if content_type == "application/pdf" or payload.startswith(b"%PDF"):
        return extract_pdf(payload)
    return extract_html(payload)


def validate_receipt() -> list[str]:
    errors: list[str] = []
    staging = json.loads(STAGING.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))

    if staging.get("service_id") != SERVICE_ID or audit.get("service_id") != SERVICE_ID:
        errors.append("service_id mismatch")
    if audit.get("audit_kind") != "INDEPENDENT_ITEM_BODY_VERIFICATION":
        errors.append("unexpected audit_kind")
    if audit.get("verification_scope") != "CONTENT_AND_EVIDENCE_MATCH_ONLY":
        errors.append("verification scope must remain content/evidence only")

    staging_items = staging.get("items", [])
    audit_items = audit.get("items", [])
    if staging.get("item_count") != 25 or len(staging_items) != 25:
        errors.append("staging must contain exactly 25 items")
    if len(audit_items) != 25:
        errors.append("audit must contain exactly 25 items")

    staging_by_id = {row.get("id"): row for row in staging_items}
    audit_by_id = {row.get("id"): row for row in audit_items}
    if set(staging_by_id) != set(audit_by_id):
        errors.append("audit item IDs do not exactly match staging item IDs")

    counts = {status: 0 for status in ("PASS", "PARTIAL", "GAP", "FAIL")}
    for item_id, row in audit_by_id.items():
        status = row.get("status")
        if status not in ALLOWED:
            errors.append(f"{item_id}: invalid status {status!r}")
            continue
        counts[status] += 1
        src = staging_by_id.get(item_id, {})
        for field in ("task_id", "path", "number", "heading"):
            if row.get(field) != src.get(field):
                errors.append(f"{item_id}: {field} does not match staging")
        if row.get("staging_content_summary") != src.get("content_summary"):
            errors.append(f"{item_id}: content_summary is not bound to staging")
        if row.get("service_scope_match") != "PASS":
            errors.append(f"{item_id}: service scope is not independently matched")
        if not row.get("content_evidence_match_reason"):
            errors.append(f"{item_id}: missing evidence-match reason")
        if not row.get("evidence"):
            errors.append(f"{item_id}: missing evidence")
        if status == "PARTIAL" and not row.get("limitation"):
            errors.append(f"{item_id}: PARTIAL requires a limitation")
        for safety_key in (
            "currentness_proven",
            "human_review_proven",
            "publication_permitted",
        ):
            if row.get(safety_key) is not False:
                errors.append(f"{item_id}: {safety_key} must remain false")

    declared_counts = audit.get("coverage", {}).get("counts", {})
    if declared_counts != counts:
        errors.append(f"declared counts {declared_counts} != observed {counts}")
    if counts != {"PASS": 25, "PARTIAL": 0, "GAP": 0, "FAIL": 0}:
        errors.append(f"unexpected bounded audit distribution: {counts}")

    source_roles = audit.get("source_roles", {})
    html_role = source_roles.get("historical-official-html", {}).get("role")
    if html_role != "ORDINANCE_TEXT_CROSSCHECK_NOT_NOTICE_BODY":
        errors.append("official HTML must be classified as ordinance cross-check, not notice body")
    if source_roles.get("r6-final-comparison", {}).get("role") != "FINAL_R6_AMENDMENT_COMPARISON":
        errors.append("R6 final comparison role is missing or altered")

    safety = audit.get("safety", {})
    required_false = (
        "currentness_proven",
        "integrated_current_text_constructed",
        "omitted_text_auto_composed",
        "human_review_promoted",
        "publication_permitted",
        "public_route_enabled",
    )
    for key in required_false:
        if safety.get(key) is not False:
            errors.append(f"audit safety.{key} must remain false")

    unresolved = {row.get("id") for row in audit.get("unresolved_gaps", [])}
    if unresolved:
        errors.append(f"unexpected unresolved gap set: {sorted(unresolved)}")

    known_sources = set(source_roles)
    for row in audit_items:
        for evidence in row.get("evidence", []):
            if evidence.get("source_id") not in known_sources:
                errors.append(
                    f"{row.get('id')}: unknown source_id {evidence.get('source_id')!r}"
                )
    return errors


def refetch_source_anchors() -> list[str]:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    expectations = {
        "r3-amendment-comparison": [
            "夜間対応型訪問介護",
            "業務継続計画の策定等",
            "虐待の防止",
            "記録の整備",
        ],
        "older-amendment-reference": [
            "夜間対応型訪問介護",
            "夜間対応型訪問介護計画",
            "緊急時等の対応",
            "勤務体制の確保等",
        ],
        "r6-final-comparison": [
            "夜間対応型訪問介護",
            "管理者",
            "指定夜間対応型訪問介護の基本的取扱方針及び具体的取扱方針",
        ],
        "historical-official-html": [
            "第二章 夜間対応型訪問介護",
            "第四条",
            "第六条",
            "第十七条",
        ],
        "h27-full-notice-comparison": [
            "二 夜間対応型訪問介護",
            "基本方針（基準第四条）",
            "定期巡回サービスを行う訪問介護員等",
            "交通事情、訪問頻度等",
        ],
    }
    errors: list[str] = []
    for source_id, terms in expectations.items():
        url = audit["source_roles"][source_id]["url"]
        try:
            text = refetch(url)
        except Exception as exc:
            errors.append(f"{source_id}: fetch/extraction failed: {exc}")
            continue
        normalized = normalize(text)
        for term in terms:
            if normalize(term) not in normalized:
                errors.append(f"{source_id}: expected anchor not found: {term}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refetch-sources",
        action="store_true",
        help="also independently re-fetch the official source roles",
    )
    args = parser.parse_args()

    errors = validate_receipt()
    if args.refetch_sources:
        errors.extend(refetch_source_anchors())

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    print(json.dumps(audit["coverage"], ensure_ascii=False))
    print("PASS: bounded item-body audit is structurally bound to staging")
    if not args.refetch_sources:
        print("NOTE: source re-fetch not requested; use --refetch-sources for network anchors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
