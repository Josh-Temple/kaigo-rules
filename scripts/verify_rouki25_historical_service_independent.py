#!/usr/bin/env python3
"""Independently verify a bounded service Rouki 25 historical dataset."""
from __future__ import annotations

import argparse
import hashlib
import html as htmlmod
import json
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


def compact(value: str) -> str:
    return re.sub(r"\s+", "", unicodedata.normalize("NFKC", value))


def fetch(url: str, service_id: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                f"kaigo-rules-{service_id}-rouki25-independent/1.0 "
                "(+https://github.com/Josh-Temple/kaigo-rules)"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        raw = response.read()
        charset = response.headers.get_content_charset()
    for encoding in [charset, "utf-8", "cp932", "shift_jis"]:
        if not encoding:
            continue
        try:
            return raw, raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            pass
    return raw, raw.decode("utf-8", errors="replace")


def independent_visible_text(raw_html: str) -> str:
    text = re.sub(r"(?is)<(script|style|rt|rp)\b.*?</\1>", " ", raw_html)
    text = re.sub(
        r"(?i)<br\s*/?>|</p\s*>|</tr\s*>|</td\s*>|</div\s*>", "\n", text
    )
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    return norm(htmlmod.unescape(text))


def expected_item_count(scope: dict) -> int:
    explicit = scope.get("work_control", {}).get("expected_principal_items")
    if explicit is not None:
        return int(explicit)
    count = 0
    for group in scope.get("groups", []):
        count += len(group.get("items", []))
        if group.get("group_body_item"):
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--service-id", required=True)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    scope_path = ROOT / f"data/services/{args.service_id}/rouki25-scope.json"
    dataset_path = args.dataset or ROOT / f"data/services/{args.service_id}/rouki25-historical.generated.json"
    scope = json.loads(scope_path.read_text(encoding="utf-8"))
    data = json.loads(dataset_path.read_text(encoding="utf-8"))
    errors: list[dict] = []
    checks: list[dict] = []

    try:
        raw, decoded = fetch(scope["source_url"], args.service_id)
        visible = independent_visible_text(decoded)
        compact_visible = compact(visible)
        live_hash = hashlib.sha256(raw).hexdigest()

        if data.get("source", {}).get("sha256") != live_hash:
            errors.append(
                {
                    "difference": "source_hash_mismatch",
                    "committed": data.get("source", {}).get("sha256"),
                    "live": live_hash,
                }
            )

        for key in ("start_heading", "end_before_heading"):
            if compact(scope["boundary"][key]) not in compact_visible:
                errors.append({"difference": f"section_boundary_missing:{key}"})

        for item in data.get("items", []):
            differences = []
            body = item.get("body_text", "")
            if not body or compact(body) not in compact_visible:
                differences.append("committed_item_text_not_found_in_live_html")
            if hashlib.sha256(body.encode("utf-8")).hexdigest() != item.get("body_sha256"):
                differences.append("committed_body_hash_mismatch")
            checks.append(
                {
                    "id": item.get("id"),
                    "result": "PASS" if not differences else "FAIL",
                    "differences": differences,
                    "body_sha256": item.get("body_sha256"),
                    "source_locator": item.get("source_locator"),
                }
            )
    except Exception as exc:
        errors.append({"difference": "verification_exception", "error": str(exc)})

    expected = expected_item_count(scope)
    passed = sum(1 for item in checks if item["result"] == "PASS")
    result = "PASS" if not errors and len(checks) == expected and passed == expected else "FAIL"
    report = {
        "format_version": 1,
        "service_id": args.service_id,
        "verification_kind": "INDEPENDENT_SERVICE_ROUKI25_HISTORICAL_SOURCE_AUDIT",
        "parser": "regex_html_text_extractor_independent_of_htmlparser_importer",
        "result": result,
        "source": {
            "url": scope["source_url"],
            "sha256": data.get("source", {}).get("sha256"),
        },
        "checks": checks,
        "errors": errors,
        "coverage": {"principal_items": expected, "items_passed": passed},
        "safety": {
            "historical_source_only": True,
            "promotes_current_integrated_text": False,
            "promotes_human_review": False,
            "promotes_verified_current": False,
        },
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(rendered, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    return 0 if result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
