#!/usr/bin/env python3
"""Validate the preventive-support standards-interpretation item-body audit.

This verifier is deliberately service-specific so parallel item-body workers do not
modify shared validators or package wiring.  It validates the durable audit receipt
against the exact staging inputs.  Optional --refetch-sources only checks that the
official source roles remain independently accessible; it does not compose an
integrated current notice text.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import tempfile
import unicodedata
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICE_ID = "preventive-support"
AUDIT_PATH = (
    ROOT
    / "data/verification/standards-interpretation-item-body/preventive-support.json"
)
STAGING_PATH = (
    ROOT
    / "data/services/preventive-support/standards-interpretation-staging.json"
)
SCOPE_PATH = (
    ROOT
    / "data/services/preventive-support/standards-interpretation-scope.json"
)
SERVICE_PATH = ROOT / "data/services/preventive-support.json"
SOURCE_INVENTORY_PATH = (
    ROOT
    / "data/verification/standards-interpretation-source-inventory/preventive-support.json"
)
EXPECTED_COUNTS = {"PASS": 33, "PARTIAL": 1, "GAP": 0, "FAIL": 0}
EXPECTED_TASKS = 34
EXPECTED_CHILD_UNITS = 55
USER_AGENT = "kaigo-rules-preventive-support-item-body/1.0"


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


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise SystemExit("preventive-support item-body audit invalid: " + message)


def normalize(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        unicodedata.normalize("NFKC", html.unescape(value)),
    ).strip()


def fetch(url: str) -> tuple[bytes, str | None]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read(), response.headers.get_content_type()


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
            pass
    if decoded is None:
        decoded = payload.decode("utf-8", errors="replace")
    parser = VisibleText()
    parser.feed(decoded)
    parser.close()
    return normalize(" ".join(parser.parts))


def extract(payload: bytes, url: str, content_type: str | None) -> str:
    if (
        content_type == "application/pdf"
        or url.lower().split("?", 1)[0].endswith(".pdf")
        or payload.startswith(b"%PDF")
    ):
        return extract_pdf(payload)
    return extract_html(payload)


def validate_receipt() -> tuple[dict, dict]:
    audit = load(AUDIT_PATH)
    staging = load(STAGING_PATH)
    scope = load(SCOPE_PATH)
    service = load(SERVICE_PATH)

    if audit.get("service_id") != SERVICE_ID:
        fail("service mismatch")
    if audit.get("audit_kind") != "INDEPENDENT_STANDARDS_INTERPRETATION_ITEM_BODY_VERIFICATION":
        fail("unexpected audit kind")
    if audit.get("audit_result") != "PARTIAL_WITH_GAPS":
        fail("unexpected overall result")
    if audit.get("scope_boundary") != "EXISTING_STAGING_TASKS_ONLY":
        fail("scope boundary was widened")

    coverage = audit.get("coverage", {})
    if coverage.get("task_total") != EXPECTED_TASKS:
        fail("task coverage mismatch")
    if coverage.get("numbered_child_units_checked") != EXPECTED_CHILD_UNITS:
        fail("child-unit coverage mismatch")
    if coverage.get("verdicts") != EXPECTED_COUNTS:
        fail("verdict counts changed")

    if len(staging.get("items", [])) != EXPECTED_TASKS:
        fail("staging count changed")
    rows = audit.get("items", [])
    if len(rows) != EXPECTED_TASKS:
        fail("audit row count changed")

    staging_by_task = {row["task_id"]: row for row in staging["items"]}
    if set(staging_by_task) != {row.get("task_id") for row in rows}:
        fail("task identity set differs from staging")

    manifest_by_url = {
        row["url"]: row["id"]
        for row in scope.get("source_manifest", [])
        if row.get("url") and row.get("id")
    }
    counted_children = 0
    counted_verdicts = {key: 0 for key in EXPECTED_COUNTS}
    for row in rows:
        task_id = row["task_id"]
        source = staging_by_task[task_id]
        for key in ("path", "heading", "source_locator"):
            if row.get(key) != source.get(key):
                fail(f"{task_id}: {key} differs from staging")
        if row.get("staging_id") != source.get("id"):
            fail(f"{task_id}: staging id differs")
        if row.get("stored_source_urls") != source.get("source_urls"):
            fail(f"{task_id}: stored source URLs differ")
        expected_source_ids = [manifest_by_url[url] for url in source["source_urls"]]
        if row.get("stored_source_manifest_ids") != expected_source_ids:
            fail(f"{task_id}: source manifest bindings differ")
        verdict = row.get("verdict")
        if verdict not in counted_verdicts:
            fail(f"{task_id}: unknown verdict {verdict}")
        counted_verdicts[verdict] += 1
        children = row.get("checked_child_locators", [])
        if row.get("numbered_child_units_checked") != len(children) or not children:
            fail(f"{task_id}: child-unit evidence mismatch")
        counted_children += len(children)
        if row.get("current_integrated_notice_body_claimed") is not False:
            fail(f"{task_id}: integrated current notice was overclaimed")

    if counted_children != EXPECTED_CHILD_UNITS:
        fail("recounted child-unit coverage mismatch")
    if counted_verdicts != EXPECTED_COUNTS:
        fail("recounted verdict totals mismatch")

    safety = audit.get("safety", {})
    if not safety or any(value is not False for value in safety.values()):
        fail("fail-closed safety boundary weakened")
    if staging.get("publication_state") != "NOT_PUBLIC":
        fail("publication state promoted")
    if staging.get("currentness_state") != "NOT_ESTABLISHED":
        fail("currentness promoted")
    if staging.get("human_review_state") != "NOT_REVIEWED":
        fail("human review promoted")
    if staging.get("service_package_state") != "SEPARATE_PRECHECK_BLOCKER_PRESERVED":
        fail("package blocker separation changed")

    publication = service.get("publication_gate", {})
    for key in (
        "public_routes_enabled",
        "content_ingested",
        "independent_verification_complete",
        "human_review_complete",
    ):
        if publication.get(key) is not False:
            fail(f"service publication gate promoted: {key}")

    if [
        row["task_id"]
        for row in rows
        if row.get("verdict") == "GAP"
    ]:
        fail("unexpected GAP set")
    if any(row.get("verdict") == "FAIL" for row in rows):
        fail("unexpected FAIL was introduced")

    promoted_version_separated = {
        "KR2-10-B004", "KR2-10-B008", "KR2-10-B012", "KR2-10-B014",
        "KR2-10-B018", "KR2-10-B020", "KR2-10-B022", "KR2-10-B025",
        "KR2-10-B027", "KR2-10-B029", "KR2-10-B031", "KR2-10-B033",
    }
    rows_by_task = {row["task_id"]: row for row in rows}
    manifest_ids = {row.get("id") for row in scope.get("source_manifest", [])}
    for task_id in promoted_version_separated:
        row = rows_by_task[task_id]
        if row.get("verdict") != "PASS":
            fail(f"{task_id}: expected version-separated PASS")
        evidence = row.get("version_separated_item_body_evidence", [])
        if not evidence or not any(
            item.get("directly_supports_staging_summary") is True
            and item.get("source_manifest_id") in manifest_ids
            for item in evidence
        ):
            fail(f"{task_id}: direct notice-body evidence missing")
        if any(item.get("proves_currentness") is not False for item in evidence):
            fail(f"{task_id}: currentness was inferred from version-separated evidence")
    b008_children = rows_by_task["KR2-10-B008"].get("child_item_body_evidence", [])
    if len(b008_children) != 12:
        fail("KR2-10-B008: expected 12 child item-body evidence rows")
    if any(
        item.get("directly_supports_child_item_body") is not True
        or item.get("proves_currentness") is not False
        or item.get("source_manifest_id") not in manifest_ids
        or not item.get("later_final_version_locator")
        for item in b008_children
    ):
        fail("KR2-10-B008: child item-body evidence boundary invalid")
    for item in b008_children:
        if item.get("source_manifest_id") == "work-control-source-4" and not item.get("earlier_version_locator"):
            fail("KR2-10-B008: historical child evidence lacks earlier-version locator")
    remaining_partial = {
        row["task_id"] for row in rows if row.get("verdict") == "PARTIAL"
    }
    if remaining_partial != {"KR2-10-B016"}:
        fail(f"unexpected remaining PARTIAL set: {sorted(remaining_partial)}")

    work_control = audit.get("work_control_observation", {})
    if work_control.get("task_id") != "KR2-10-E006":
        fail("package blocker task binding changed")
    if work_control.get("observed_status") != "BLOCKED":
        fail("package blocker was not preserved in the audit observation")

    observations = audit.get("out_of_staging_source_observations", [])
    if len(observations) != 1 or "㉗" not in observations[0].get("locator", ""):
        fail("R6 out-of-staging observation missing")
    if observations[0].get("action") != "INTEGRATOR_FOLLOWUP_ONLY_NO_SCOPE_EXPANSION_IN_THIS_BRANCH":
        fail("R6 observation was improperly promoted into scope")

    return audit, scope


def refetch_sources(scope: dict) -> None:
    expected_anchors = {
        "r6-final-comparison": "介護予防支援",
        "r6-additional-official-evidence": "介護予防支援",
        "r6-amendment-page": "令和6年度介護報酬改定",
        "work-control-source-4": "介護予防支援",
        "work-control-source-5": "介護予防支援",
        "additional-official-item1-evidence": "内容及び手続きの説明及び同意",
    }
    rows = scope.get("source_manifest", [])
    if set(expected_anchors) != {row.get("id") for row in rows}:
        fail("source manifest role set changed")
    for row in rows:
        source_id = row["id"]
        payload, content_type = fetch(row["url"])
        if len(payload) < 100:
            fail(f"{source_id}: fetched payload unexpectedly small")
        text = extract(payload, row["url"], content_type)
        anchor = normalize(expected_anchors[source_id])
        if anchor not in text:
            fail(f"{source_id}: expected official-source anchor not found")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refetch-sources",
        action="store_true",
        help="Re-fetch all manifest sources and check bounded anchors.",
    )
    args = parser.parse_args()
    audit, scope = validate_receipt()
    if args.refetch_sources:
        refetch_sources(scope)

    counts = audit["coverage"]["verdicts"]
    print(
        "preventive-support item-body audit: PARTIAL_WITH_GAPS "
        f"({audit['coverage']['task_total']} tasks; "
        f"{audit['coverage']['numbered_child_units_checked']} child units; "
        f"PASS {counts['PASS']} / PARTIAL {counts['PARTIAL']} / "
        f"GAP {counts['GAP']} / FAIL {counts['FAIL']})"
    )


if __name__ == "__main__":
    main()
