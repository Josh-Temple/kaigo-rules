#!/usr/bin/env python3
"""Validate Other National material body assurance without cross-axis promotion."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/shared/other-national-materials"
MANIFEST = BASE / "manifest.json"
CORPUS = BASE / "national-corpus.json"
BODY = BASE / "canonical-body-items.json"
ASSURANCE = BASE / "item-body-assurance.json"
APPLICABILITY = BASE / "service-applicability.json"
SERVICES = ROOT / "data/services/manifest.json"

ALLOWED_STATES = {"PASS", "PARTIAL", "NOT_ESTABLISHED"}
OFFICIAL_HOSTS = {"www.mhlw.go.jp", "mhlw.go.jp", "www.kaigokensaku.mhlw.go.jp", "kaigokensaku.mhlw.go.jp"}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def fingerprint(payload) -> str:
    raw = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def service_ids(raw):
    return {
        item if isinstance(item, str) else item.get("service_id")
        for item in (raw or [])
        if (item if isinstance(item, str) else item.get("service_id"))
    }


def main() -> None:
    manifest = load(MANIFEST)
    corpus = load(CORPUS)
    body = load(BODY)
    assurance = load(ASSURANCE)
    applicability = load(APPLICABILITY)
    services = load(SERVICES)

    errors: list[str] = []

    if manifest.get("item_body_assurance") != "data/shared/other-national-materials/item-body-assurance.json":
        errors.append("manifest item_body_assurance pointer mismatch")
    if manifest.get("canonical_body_store") != "data/shared/other-national-materials/canonical-body-items.json":
        errors.append("manifest canonical_body_store pointer mismatch")
    if manifest.get("assurance", {}).get("item_body_verification") != "PARTIAL":
        errors.append("manifest must expose only PARTIAL family-level item-body assurance")

    corpus_sources = {row["source_id"]: row for row in corpus.get("sources", [])}
    body_sources = {row["canonical_source_id"]: row for row in body.get("sources", [])}
    source_verifications = {
        row["canonical_source_id"]: row
        for row in assurance.get("source_verifications", [])
    }
    if set(source_verifications) != set(corpus_sources):
        errors.append("source assurance set must equal canonical corpus source set")

    for source_id, row in source_verifications.items():
        state = row.get("result")
        if state not in ALLOWED_STATES:
            errors.append(f"{source_id}: invalid source assurance state {state}")
            continue
        if row.get("currentness_claimed") is not False:
            errors.append(f"{source_id}: item-body assurance must not claim currentness")
        if row.get("source_bytes_sha256") is not None:
            errors.append(f"{source_id}: source byte hash must not be invented")

        canonical = corpus_sources[source_id]
        corpus_state = canonical.get("assurance", {}).get("item_body_verification")
        if corpus_state != state:
            errors.append(f"{source_id}: corpus/source assurance mismatch {corpus_state} != {state}")

        body_row = body_sources.get(source_id)
        if state in {"PASS", "PARTIAL"}:
            if not body_row:
                errors.append(f"{source_id}: verified source missing canonical body record")
                continue
            expected = fingerprint(body_row.get("fingerprint_payload"))
            if expected != body_row.get("canonical_body_fingerprint_sha256"):
                errors.append(f"{source_id}: canonical body fingerprint is not reproducible")
            if expected != row.get("canonical_body_fingerprint_sha256"):
                errors.append(f"{source_id}: assurance fingerprint does not match canonical body")
            item_ids = {item.get("canonical_item_id") for item in body_row.get("items", [])}
            verified_ids = set(row.get("verified_canonical_item_ids", []))
            if not verified_ids or not verified_ids.issubset(item_ids):
                errors.append(f"{source_id}: verified item IDs are empty or outside canonical body store")
            for item in body_row.get("items", []):
                host = urlparse(item.get("official_url", "")).hostname
                if host not in OFFICIAL_HOSTS:
                    errors.append(f"{source_id}: body item uses non-official host {host}")
                page = item.get("pdf_page")
                pages = item.get("pdf_pages")
                single_page_ok = isinstance(page, int) and page >= 1
                page_range_ok = (
                    isinstance(pages, list)
                    and bool(pages)
                    and all(isinstance(value, int) and value >= 1 for value in pages)
                )
                if not (single_page_ok or page_range_ok):
                    errors.append(f"{source_id}: body item missing exact PDF page locator")
                if not item.get("locator"):
                    errors.append(f"{source_id}: body item missing native locator")

        if state == "PASS":
            if row.get("coverage_kind") != "ALL_DECLARED_CANONICAL_BODY_ITEMS_IN_BOUND_DOCUMENT":
                errors.append(f"{source_id}: PASS requires full declared body-item coverage")
            if not body_row or body_row.get("body_coverage_state") != "PASS":
                errors.append(f"{source_id}: PASS source lacks PASS canonical body record")
            if body_row and body_row.get("unresolved_body_scope"):
                errors.append(f"{source_id}: PASS source still has unresolved body scope")
            if body_row:
                item_ids = {item.get("canonical_item_id") for item in body_row.get("items", [])}
                if set(row.get("verified_canonical_item_ids", [])) != item_ids:
                    errors.append(f"{source_id}: PASS does not cover every declared canonical body item")

        if state == "PARTIAL":
            if not row.get("remaining_body_gap"):
                errors.append(f"{source_id}: PARTIAL requires an explicit remaining body gap")
            if not body_row or body_row.get("body_coverage_state") != "PARTIAL":
                errors.append(f"{source_id}: PARTIAL source lacks PARTIAL canonical body record")

        if state == "NOT_ESTABLISHED" and row.get("verified_canonical_item_ids"):
            errors.append(f"{source_id}: NOT_ESTABLISHED source has verified item IDs")

    service_universe = {row["service_id"] for row in services.get("services", [])}
    projections = {
        row["service_id"]: row
        for row in assurance.get("service_projections", [])
    }
    if set(projections) != service_universe:
        errors.append("service projection set must exactly match the 39-service manifest")

    applicability_rows = {
        row["canonical_source_id"]: row
        for row in applicability.get("sources", [])
    }
    source_states = {
        source_id: row.get("result")
        for source_id, row in source_verifications.items()
    }

    for service_id in sorted(service_universe):
        mapped: set[str] = set()
        conditional: set[str] = set()
        not_applicable: set[str] = set()
        for source_id, row in applicability_rows.items():
            if service_id in set(row.get("mapped_service_ids", [])):
                mapped.add(source_id)
            if service_id in service_ids(row.get("conditional_service_ids")):
                conditional.add(source_id)
            if service_id in service_ids(row.get("not_applicable_service_ids")):
                not_applicable.add(source_id)

        evaluated = (mapped | conditional) - not_applicable
        states = [source_states.get(source_id, "NOT_ESTABLISHED") for source_id in evaluated]
        if not states:
            expected = "NOT_ESTABLISHED"
        elif all(state == "PASS" for state in states):
            expected = "PASS"
        elif any(state in {"PASS", "PARTIAL"} for state in states):
            expected = "PARTIAL"
        else:
            expected = "NOT_ESTABLISHED"

        projection = projections[service_id]
        if set(projection.get("mapped_source_ids", [])) != mapped:
            errors.append(f"{service_id}: mapped source projection mismatch")
        if set(projection.get("conditional_source_ids", [])) != conditional:
            errors.append(f"{service_id}: conditional source projection mismatch")
        if set(projection.get("explicitly_not_applicable_source_ids", [])) != not_applicable:
            errors.append(f"{service_id}: not-applicable source projection mismatch")
        if projection.get("service_level_item_body") != expected:
            errors.append(
                f"{service_id}: unsafe item-body projection "
                f"{projection.get('service_level_item_body')} != {expected}"
            )
        for axis in (
            "currentness_promoted",
            "human_review_promoted",
            "publication_promoted",
            "route_exposure_promoted",
        ):
            if projection.get(axis) is not False:
                errors.append(f"{service_id}: cross-axis promotion detected at {axis}")

    summary = assurance.get("service_summary", {})
    actual = {"PASS": 0, "PARTIAL": 0, "NOT_ESTABLISHED": 0}
    for row in projections.values():
        actual[row["service_level_item_body"]] += 1
    if summary != {key: value for key, value in actual.items() if value}:
        errors.append(f"service summary mismatch: {summary} != {actual}")

    if actual["PASS"] != 0 or actual["PARTIAL"] != 39:
        errors.append(
            "current bounded evidence must remain fail-closed: "
            f"PASS={actual['PASS']} PARTIAL={actual['PARTIAL']}"
        )

    boundaries = assurance.get("assurance_boundaries", {})
    if boundaries.get("currentness") != "UNCHANGED_BY_THIS_ARTIFACT":
        errors.append("item-body artifact improperly changes currentness")
    if boundaries.get("human_review") != "NOT_REVIEWED":
        errors.append("item-body artifact improperly changes human review")
    if boundaries.get("publication") != "BLOCKED" or boundaries.get("route_exposure") != "BLOCKED":
        errors.append("item-body artifact improperly changes publication/route")
    if boundaries.get("automatic_cross_axis_promotion_allowed") is not False:
        errors.append("automatic cross-axis promotion must stay disabled")

    if errors:
        raise SystemExit("\n".join(f"ERROR: {message}" for message in errors))

    source_summary = assurance.get("source_summary", {})
    print(
        "Other National item-body assurance: PASS "
        f"(sources={source_summary}; services=PARTIAL {actual['PARTIAL']}/39; "
        "currentness/human-review/publication/route unchanged)"
    )


if __name__ == "__main__":
    main()
