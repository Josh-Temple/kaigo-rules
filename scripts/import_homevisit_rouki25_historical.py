#!/usr/bin/env python3
"""Import bounded historical Rouki 25 homevisit text from official MHLW HTML."""
from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCOPE_PATH = ROOT / "data/services/homevisit/rouki25-scope.json"
OUTPUT = ROOT / "data/services/homevisit/rouki25-historical.generated.json"


def norm(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).split())


class Visible(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.fragments: list[str] = []
        self.suppressed = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "rt", "rp"}:
            self.suppressed += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "rt", "rp"} and self.suppressed:
            self.suppressed -= 1

    def handle_data(self, data):
        if not self.suppressed:
            value = norm(data)
            if value:
                self.fragments.append(value)


def fetch(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "kaigo-rules-homevisit-rouki25-importer/1.0 (+https://github.com/Josh-Temple/kaigo-rules)"
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


def locate(lines: list[str], needle: str, start: int = 0, end: int | None = None) -> int:
    wanted = norm(needle)
    limit = len(lines) if end is None else end
    for index in range(start, limit):
        value = norm(lines[index])
        if value == wanted or value.startswith(wanted):
            return index
    raise ValueError(f"marker not found: {needle}")


def build() -> dict:
    scope = json.loads(SCOPE_PATH.read_text(encoding="utf-8"))
    raw, html = fetch(scope["source_url"])
    parser = Visible()
    parser.feed(html)
    parser.close()
    lines = parser.fragments

    section_start = locate(lines, scope["boundary"]["start_heading"])
    section_end = locate(
        lines, scope["boundary"]["end_before_heading"], section_start + 1
    )
    section = lines[section_start:section_end]

    group_positions: list[tuple[dict, int]] = []
    cursor = 0
    for group in scope["groups"]:
        marker = f'{group["number"]} {group["heading"]}'
        position = locate(section, marker, cursor)
        group_positions.append((group, position))
        cursor = position + 1

    items: list[dict] = []
    for group_index, (group, group_start) in enumerate(group_positions):
        group_end = (
            group_positions[group_index + 1][1]
            if group_index + 1 < len(group_positions)
            else len(section)
        )

        group_body_item = group.get("group_body_item")
        if group_body_item:
            body = "\n".join(section[group_start + 1 : group_end]).strip()
            if not body:
                raise ValueError(f"empty group body for {group_body_item['id']}")
            items.append(
                {
                    "id": group_body_item["id"],
                    "group_number": group["number"],
                    "group_heading": group["heading"],
                    "marker": group["number"],
                    "title": group_body_item["title"],
                    "body_text": body,
                    "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                    "source_locator": (
                        f'{scope["source_section"]} / {group["number"]} {group["heading"]}'
                    ),
                    "source_url": scope["source_url"],
                    "source_state": scope["source_state"],
                    "currentness_state": scope["currentness_state"],
                    "human_review_state": scope["human_review_state"],
                }
            )
            continue

        marker_positions: list[tuple[dict, int]] = []
        cursor = group_start + 1
        for item in group.get("items", []):
            position = locate(section, item["marker"], cursor, group_end)
            marker_positions.append((item, position))
            cursor = position + 1

        for item_index, (item, item_start) in enumerate(marker_positions):
            item_end = (
                marker_positions[item_index + 1][1]
                if item_index + 1 < len(marker_positions)
                else group_end
            )
            body = "\n".join(section[item_start:item_end]).strip()
            if not body:
                raise ValueError(f"empty body for {item['id']}")
            items.append(
                {
                    "id": item["id"],
                    "group_number": group["number"],
                    "group_heading": group["heading"],
                    "marker": item["marker"],
                    "title": item["title"],
                    "body_text": body,
                    "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                    "source_locator": (
                        f'{scope["source_section"]} / {group["number"]} '
                        f'{group["heading"]} / {item["marker"]}'
                    ),
                    "source_url": scope["source_url"],
                    "source_state": scope["source_state"],
                    "currentness_state": scope["currentness_state"],
                    "human_review_state": scope["human_review_state"],
                }
            )

    expected = int(scope["work_control"]["expected_principal_items"])
    if len(items) != expected:
        raise ValueError(f"expected {expected} principal items, got {len(items)}")

    return {
        "format_version": 1,
        "generated_by": "scripts/import_homevisit_rouki25_historical.py",
        "service_id": "homevisit",
        "layer": "standards_interpretation",
        "document_id": "rouki25",
        "source_section": scope["source_section"],
        "source": {
            "url": scope["source_url"],
            "sha256": hashlib.sha256(raw).hexdigest(),
            "state": scope["source_state"],
        },
        "boundary": scope["boundary"],
        "items": items,
        "item_count": len(items),
        "amendment_evidence": scope["amendment_evidence"],
        "work_control": scope["work_control"],
        "assurance": scope["safety"],
    }


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(
                "homevisit Rouki 25 historical dataset is stale; run importer"
            )
        print("homevisit Rouki 25 historical dataset: current")
        return
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
