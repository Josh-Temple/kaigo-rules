#!/usr/bin/env python3
"""Build the bounded publication allowlist used by every public runtime surface.

Only publication units that are READY, supported by the runtime policy, and
explicitly selected here can be exposed. Route exposure is selected separately,
even when it currently matches the publication selection.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
READINESS_PATH = ROOT / "data/publication-readiness.generated.json"
GOVERNING_CURRENTNESS_PATH = ROOT / "data/verification/bounded-currentness-closure-worker-b.json"
HIGH_VALUE_CURRENTNESS_PATH = ROOT / "data/verification/high-value-currentness-closure-worker-b.json"
HIGH_VALUE_EXPANSION_PATH = ROOT / "data/verification/high-value-currentness-expansion-worker-c.json"
GOVERNING_RESIDUAL_CURRENTNESS_PATH = (
    ROOT / "data/verification/governing-standards-residual-currentness-worker-a.json"
)
FINAL_GOVERNING_CURRENTNESS_PATH = (
    ROOT / "data/verification/final-standards-residual-relation-worker-c.json"
)
SHARED_STANDARDS_ROOT = ROOT / "data/shared/standards"
UNIT_PRICE_META_PATH = ROOT / "data/unit-price-dayservice-meta.json"
UNIT_PRICE_MAPPINGS_PATH = ROOT / "data/unit-price-service-multipliers.json"
UNIT_PRICE_ITEM_BODY_PATH = ROOT / "data/unit-price-item-body-assurance.json"
DELEGATED_MANIFEST_PATH = ROOT / "data/shared/remuneration-delegated/manifest.json"
DELEGATED_APPLICABILITY_PATH = ROOT / "data/shared/remuneration-delegated/service-applicability.json"
DELEGATED_ITEM_BODY_PATH = ROOT / "data/shared/remuneration-delegated/item-body-verification.json"
DELEGATED_CORPUS_PATH = ROOT / "data/shared/remuneration-delegated/national-corpus.json"
DELEGATED_CURRENTNESS_CONTRACT_PATH = ROOT / "data/shared/remuneration-delegated/currentness-source-contract.json"
OUTPUT_PATH = ROOT / "data/bounded-publication-allowlist.json"

SAFE_FIELDS = [
    "source_text",
    "item_body",
    "source_metadata",
    "source_locator",
    "currentness_statement",
    "service_applicability_statement",
]
FORBIDDEN_FIELDS = [
    "cross_layer_relation_assertion",
    "unverified_relation_assertion",
    "review_dependent_explanatory_text",
    "relation_rank_feature",
    "review_dependent_search_term",
]
REQUIRED_PUBLICATION_UNITS = {
    "SOURCE_TEXT_ITEM_BODY",
    "SOURCE_METADATA_LOCATOR",
    "CURRENTNESS_STATEMENT",
    "SERVICE_APPLICABILITY_STATEMENT",
}
RUNTIME_SUPPORTED_SOURCE_FAMILIES = {
    "governing_standards_ordinance",
    "unit_price_regional_classification",
    "delegated_remuneration_criteria",
}
RESIDUAL_GOVERNING_SOURCE_IDENTITIES = {
    "community-based-standards",
    "care-management-standards",
    "preventive-support-standards",
    "elderly-welfare-facility-standards",
    "geriatric-health-services-facility-standards",
    "long-term-care-medical-facility-standards",
    "preventive-community-based-standards",
}
RUNTIME_SUPPORTED_SOURCE_IDENTITIES = {
    "ordinance37",
    "preventive-services-standards",
    "mhlw-unit-price-current",
    "delegated-remuneration-national",
    *RESIDUAL_GOVERNING_SOURCE_IDENTITIES,
}
# Validation ceiling only. Publication selection is not truncated by this value;
# the generated policy records the current READY count as its dynamic bound.
MAX_PUBLICATION_CELLS = 351


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    body = path.read_bytes()
    header = f"blob {len(body)}\0".encode("utf-8")
    return hashlib.sha1(header + body).hexdigest()


def shared_standard_meta(corpus_id: str) -> dict[str, Any]:
    return load_json(SHARED_STANDARDS_ROOT / corpus_id / "meta.json")


def shared_standard_article_rows(corpus_id: str) -> list[dict[str, Any]]:
    rows = load_json(SHARED_STANDARDS_ROOT / corpus_id / "nodes.json")
    if not isinstance(rows, list):
        raise ValueError(f"shared standards nodes must be a list: {corpus_id}")
    return [row for row in rows if row.get("node_type") == "article"]


def residual_governing_direct_article_numbers(row: dict[str, Any]) -> list[str]:
    """Resolve only the direct service scope already established by Worker A.

    Incorporation-by-reference and read-as relations are intentionally excluded.
    This is a runtime binding translation, not a new currentness decision.
    """
    corpus_id = str(row.get("canonical_source_id") or "")
    service_id = str(row.get("service_id") or "")
    scope_rel = str(row.get("scope_path") or "")
    if corpus_id not in RESIDUAL_GOVERNING_SOURCE_IDENTITIES:
        raise ValueError(f"unsupported residual governing source identity: {corpus_id}")
    if not service_id or not scope_rel:
        raise ValueError("residual governing runtime binding lacks service/scope identity")

    scope_path = ROOT / scope_rel
    scope = load_json(scope_path)
    if str(scope.get("service_id") or "") != service_id:
        raise ValueError(f"residual governing scope service mismatch: {service_id}")

    meta = shared_standard_meta(corpus_id)
    rows = shared_standard_article_rows(corpus_id)
    by_num = {str(item.get("article_num") or ""): item for item in rows}

    def article_number_key(value: str) -> tuple[int, ...]:
        parts = value.split("-")
        if not value or any(not part.isdigit() for part in parts):
            raise ValueError(
                f"unsupported direct-range article number: {corpus_id}: {value}"
            )
        return tuple(int(part) for part in parts)

    sortable_article_numbers: dict[str, tuple[int, ...]] = {}
    for article_num in by_num:
        try:
            sortable_article_numbers[article_num] = article_number_key(article_num)
        except ValueError:
            # Some imported corpora contain synthetic/non-range article_num values
            # such as "48:49". They are not eligible for numeric direct-range
            # expansion, but their presence must not distort legitimate boundaries.
            continue

    selected: list[str] = []
    governing = scope.get("governing_standards_ordinance")
    if isinstance(governing, dict):
        if governing.get("corpus_id") != corpus_id:
            raise ValueError(f"residual governing scope corpus mismatch: {service_id}")
        if governing.get("law_id") != meta.get("law_id"):
            raise ValueError(f"residual governing scope law mismatch: {service_id}")
        direct_ranges = [
            item
            for item in governing.get("direct_article_ranges", [])
            if item.get("role")
            not in {"common", "common_miscellaneous_electronic_records"}
        ]
        if not direct_ranges:
            raise ValueError(f"residual governing direct range missing: {service_id}")
        for item in direct_ranges:
            start = str(item.get("from") or "")
            end = str(item.get("through") or "")
            if start not in by_num or end not in by_num:
                raise ValueError(
                    f"residual governing direct range unresolved: {service_id} {start}..{end}"
                )
            start_key = article_number_key(start)
            end_key = article_number_key(end)
            if start_key > end_key:
                raise ValueError(
                    f"residual governing direct range reversed: {service_id} {start}..{end}"
                )
            in_range = sorted(
                (
                    article_num
                    for article_num, key in sortable_article_numbers.items()
                    if start_key <= key <= end_key
                ),
                key=lambda article_num: sortable_article_numbers[article_num],
            )
            if not in_range:
                raise ValueError(
                    f"residual governing direct range empty: {service_id} {start}..{end}"
                )
            selected.extend(in_range)
    elif isinstance(scope.get("service_chapter_direct_scope"), dict):
        if scope.get("corpus_id") != corpus_id:
            raise ValueError(f"preventive governing scope corpus mismatch: {service_id}")
        if scope.get("law_id") != meta.get("law_id"):
            raise ValueError(f"preventive governing scope law mismatch: {service_id}")
        chapter = scope["service_chapter_direct_scope"]
        selected.extend(str(value) for value in chapter.get("article_numbers", []))
        source_node_ids = [str(value) for value in chapter.get("source_node_ids", [])]
        node_prefix = str(meta.get("node_prefix") or "")
        expected_node_ids = [f"{node_prefix}.article.{value}" for value in selected]
        if source_node_ids and source_node_ids != expected_node_ids:
            raise ValueError(
                f"preventive governing direct node identity mismatch: {service_id}"
            )
    else:
        shared = scope.get("shared_corpus") or {}
        if shared.get("corpus_id") != corpus_id:
            raise ValueError(f"dedicated governing scope corpus mismatch: {service_id}")
        if shared.get("law_id") != meta.get("law_id"):
            raise ValueError(f"dedicated governing scope law mismatch: {service_id}")
        selected.extend(
            str(value)
            for value in (scope.get("common_direct_scope") or {}).get(
                "article_numbers", []
            )
        )
        for variant in scope.get("service_variants", []):
            selected.extend(str(value) for value in variant.get("article_numbers", []))
            selected.extend(
                str(value)
                for value in (variant.get("direct_scope") or {}).get(
                    "article_numbers", []
                )
            )

    selected = list(dict.fromkeys(value for value in selected if value))
    if not selected:
        raise ValueError(f"residual governing direct scope empty: {service_id}")
    missing = [value for value in selected if value not in by_num]
    if missing:
        raise ValueError(
            f"residual governing direct articles missing from canonical corpus: "
            f"{service_id}: {missing}"
        )
    return selected


def normalize_governing_residual_decision(
    payload: dict[str, Any], row: dict[str, Any]
) -> dict[str, Any]:
    normalized = copy.deepcopy(row)
    source_id = str(row.get("canonical_source_id") or "")
    source_evidence = copy.deepcopy(
        (payload.get("source_evidence") or {}).get(source_id) or {}
    )
    if source_evidence.get("canonical_source_id") != source_id:
        raise ValueError(
            f"residual governing source evidence mismatch: {row.get('service_id')}"
        )
    meta = shared_standard_meta(source_id)
    source_evidence.setdefault("title", str(meta.get("law_title") or ""))
    normalized["source_identity"] = source_evidence

    proof = copy.deepcopy(row.get("applicability_proof") or {})
    if row.get("promotion_applied") is True:
        proof["direct_article_numbers"] = residual_governing_direct_article_numbers(row)
        proof["scope_path"] = str(row.get("scope_path") or "")
    normalized["applicability_proof"] = proof
    normalized["allowed_publication_units"] = sorted(REQUIRED_PUBLICATION_UNITS)
    return normalized


def normalize_final_governing_decision(
    payload: dict[str, Any], row: dict[str, Any]
) -> dict[str, Any]:
    """Translate Worker C's final-two assurance into the existing runtime contract.

    Worker C changes only currentness for the two previously deferred services.
    Runtime scope remains bound to the same canonical service-scope files and
    direct article ranges used by the residual governing publication adapter.
    """
    prior_payload = load_json(GOVERNING_RESIDUAL_CURRENTNESS_PATH)
    prior_by_service = {
        str(item.get("service_id") or ""): item
        for item in prior_payload.get("decisions", [])
    }
    service_id = str(row.get("service_id") or "")
    prior = copy.deepcopy(prior_by_service.get(service_id) or {})
    if not prior:
        raise ValueError(f"final governing decision lacks prior bounded row: {service_id}")
    if (
        prior.get("promotion_applied") is not False
        or prior.get("decision") != "DEFER"
        or row.get("decision") != "PROMOTE_PASS_BOUNDED"
        or row.get("promotion_applied") is not True
        or row.get("projected_currentness_state") != "PASS"
        or row.get("blocker") is not None
    ):
        raise ValueError(f"final governing transition is not bounded DEFER->PASS: {service_id}")

    source_id = str(row.get("canonical_source_id") or "")
    source_evidence = copy.deepcopy(
        (prior_payload.get("source_evidence") or {}).get(source_id) or {}
    )
    current_source = row.get("current_source") or {}
    if (
        source_id != prior.get("canonical_source_id")
        or source_evidence.get("canonical_source_id") != source_id
        or current_source.get("law_id") != source_evidence.get("law_id")
        or current_source.get("official_source_url")
        != source_evidence.get("official_source_url")
        or current_source.get("version_id") != source_evidence.get("version_id")
        or current_source.get("xml_sha256")
        != (source_evidence.get("fingerprint") or {}).get("xml_sha256")
        or current_source.get("current_revision_status")
        != (source_evidence.get("revision_lineage") or {}).get(
            "current_revision_status"
        )
        or current_source.get("repeal_status")
        != (source_evidence.get("revision_lineage") or {}).get("repeal_status")
    ):
        raise ValueError(f"final governing source identity drift: {service_id}")

    normalized = prior
    normalized["decision"] = "PROMOTE_PASS_BOUNDED"
    normalized["blocker"] = None
    normalized["projected_currentness_state"] = "PASS"
    normalized["promotion_applied"] = True
    normalized["source_version_contains_scope"] = True
    normalized["source_identity"] = source_evidence
    normalized["projection_gate"] = {
        "kind": "EXPLICIT_BOUNDED_ALLOWLIST",
        "identity": f"{service_id}::governing_standards_ordinance",
        "scope": "currentness_only",
        "allowed": True,
    }
    proof = copy.deepcopy(prior.get("applicability_proof") or {})
    proof.update(
        {
            "state": "PASS_DIRECT_SCOPE_CURRENT_VERSION",
            "scope_identity_present": True,
            "regular_preventive_inheritance_used": False,
            "incorporation_or_read_as_semantics_promoted": False,
            "direct_article_numbers": residual_governing_direct_article_numbers(prior),
            "scope_path": str(prior.get("scope_path") or ""),
        }
    )
    normalized["applicability_proof"] = proof
    normalized["allowed_publication_units"] = sorted(REQUIRED_PUBLICATION_UNITS)
    return normalized


def residual_governing_source_contract_supported(row: dict[str, Any]) -> bool:
    source = source_identity(row)
    proof = applicability_proof(row)
    canonical_source_id = str(source.get("canonical_source_id") or "")
    service_id = str(row.get("service_id") or "")
    if canonical_source_id not in RESIDUAL_GOVERNING_SOURCE_IDENTITIES:
        return False
    if row.get("canonical_source_id") != canonical_source_id:
        return False
    if row.get("decision") != "PROMOTE_PASS_BOUNDED" or row.get("blocker") is not None:
        return False

    gate = row.get("projection_gate") or {}
    if (
        gate.get("kind") != "EXPLICIT_BOUNDED_ALLOWLIST"
        or gate.get("allowed") is not True
        or gate.get("identity")
        != f"{service_id}::governing_standards_ordinance"
        or gate.get("scope") != "currentness_only"
    ):
        return False

    if (
        proof.get("state") != "PASS_DIRECT_SCOPE_CURRENT_VERSION"
        or proof.get("scope_identity_present") is not True
        or proof.get("regular_preventive_inheritance_used") is not False
        or proof.get("incorporation_or_read_as_semantics_promoted") is not False
    ):
        return False

    try:
        meta = shared_standard_meta(canonical_source_id)
        expected_articles = residual_governing_direct_article_numbers(row)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return False

    lineage = source.get("revision_lineage") or {}
    if (
        source.get("source_form") != "OFFICIAL_VERSIONED_CURRENT_TEXT"
        or source.get("law_id") != meta.get("law_id")
        or source.get("version_id")
        != (meta.get("current_revision") or {}).get("law_revision_id")
        or source.get("official_source_url") != meta.get("source_page")
        or lineage.get("current_revision_status") != "CurrentEnforced"
        or lineage.get("repeal_status") != "None"
    ):
        return False

    return proof.get("direct_article_numbers") == expected_articles


def cell_key(row: dict[str, Any]) -> tuple[str | None, str | None]:
    return row.get("service_id"), row.get("source_family")


def delegated_currentness_path() -> Path | None:
    """Discover at most one Worker-B currentness artifact for the delegated family.

    Worker D does not create currentness decisions.  This hook stays empty on
    main until Worker B is integrated, then binds only an artifact that
    explicitly carries delegated_remuneration_criteria promotions.  Multiple
    competing artifacts fail closed instead of choosing one implicitly.
    """
    verification_dir = ROOT / "data" / "verification"
    matches: list[Path] = []
    if not verification_dir.exists():
        return None
    for path in sorted(verification_dir.glob("*delegated*currentness*.json")):
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if any(
            row.get("source_family") == "delegated_remuneration_criteria"
            for row in payload.get("promotions", [])
        ):
            matches.append(path)
    if len(matches) > 1:
        relative = [
            str(path.relative_to(ROOT)).replace("\\", "/")
            for path in matches
        ]
        raise ValueError(
            "multiple delegated remuneration currentness artifacts: "
            + ", ".join(relative)
        )
    return matches[0] if matches else None


def currentness_paths() -> list[Path]:
    paths = [GOVERNING_CURRENTNESS_PATH, HIGH_VALUE_CURRENTNESS_PATH]
    if HIGH_VALUE_EXPANSION_PATH.exists():
        paths.append(HIGH_VALUE_EXPANSION_PATH)
    if GOVERNING_RESIDUAL_CURRENTNESS_PATH.exists():
        paths.append(GOVERNING_RESIDUAL_CURRENTNESS_PATH)
    delegated_path = delegated_currentness_path()
    if delegated_path:
        paths.append(delegated_path)
    return paths


def source_identity(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("source_identity") or row.get("canonical_source_identity") or {}


def applicability_proof(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("applicability_proof") or row.get("service_applicability_evidence") or {}


def unit_price_currentness_scope_supported(row: dict[str, Any]) -> bool:
    if row.get("source_version_contains_scope") is True:
        return True
    evidence = row.get("currentness_evidence") or {}
    units = set(row.get("allowed_publication_units") or [])
    return (
        evidence.get("supersession_check")
        == "OFFICIAL_MHLW_CONSOLIDATED_DISPLAY_REVERIFIED"
        and evidence.get("live_verifier") == "scripts/verify_unit_price_currentness.py"
        and evidence.get("effective_date") == "2024-04-01"
        and REQUIRED_PUBLICATION_UNITS.issubset(units)
    )


def delegated_runtime_binding_context(
    row: dict[str, Any],
) -> dict[str, Any] | None:
    """Validate and translate Worker-B cell evidence into a runtime binding.

    This function does not decide currentness.  It accepts only the exact
    currentness PASS source set already recorded by Worker B and proves that
    the promoted cell's mapped nodes and source identities match the canonical
    delegated-remuneration corpus.
    """
    if (
        row.get("source_family") != "delegated_remuneration_criteria"
        or not DELEGATED_CURRENTNESS_CONTRACT_PATH.exists()
    ):
        return None

    service_id = str(row.get("service_id") or "")
    applicability = load_json(DELEGATED_APPLICABILITY_PATH)
    corpus = load_json(DELEGATED_CORPUS_PATH)
    currentness_contract = load_json(DELEGATED_CURRENTNESS_CONTRACT_PATH)

    service = next(
        (
            item
            for item in applicability.get("services", [])
            if item.get("service_id") == service_id
        ),
        None,
    )
    if (
        not service
        or service.get("scope_state") != "SCOPE_DEFINED"
        or service.get("applicability_state") != "MAPPED"
        or service.get("ingestion_state") != "INGESTED"
        or (service.get("assurance") or {}).get("item_body_verification")
        != "PASS"
    ):
        return None

    expected_node_ids = [str(value) for value in service.get("mapped_node_ids", [])]
    promoted_node_ids = [str(value) for value in row.get("mapped_node_ids", [])]
    if (
        not expected_node_ids
        or promoted_node_ids != expected_node_ids
        or row.get("mapped_node_count") != len(expected_node_ids)
    ):
        return None

    node_by_id = {
        str(node.get("canonical_node_id") or ""): node
        for node in corpus.get("nodes", [])
    }
    if any(node_id not in node_by_id for node_id in expected_node_ids):
        return None

    expected_source_ids = sorted(
        {
            str(node_by_id[node_id].get("source_id") or "")
            for node_id in expected_node_ids
        }
    )
    if not all(expected_source_ids):
        return None
    promoted_source_ids = sorted(
        str(value) for value in row.get("mapped_source_ids", [])
    )
    if promoted_source_ids != expected_source_ids:
        return None

    source_contracts = {
        str(item.get("canonical_source_id") or ""): item
        for item in currentness_contract.get("source_contracts", [])
    }
    selected_contracts = [
        source_contracts.get(source_id) for source_id in expected_source_ids
    ]
    if (
        any(contract is None for contract in selected_contracts)
        or any(
            contract.get("currentness_state") != "PASS"
            or contract.get("promotion_eligible") is not True
            for contract in selected_contracts
            if contract is not None
        )
    ):
        return None

    proof = row.get("applicability_proof") or {}
    gate = row.get("projection_gate") or {}
    if (
        proof.get("state") != "PASS_EXPLICIT_CANONICAL_SERVICE_MAPPING"
        or proof.get("inherited_from_sibling_service") is not False
        or row.get("source_identity_matches_item_body_source") is not True
        or gate.get("kind") != "EXPLICIT_BOUNDED_ALLOWLIST"
        or gate.get("allowed") is not True
        or gate.get("identity")
        != f"{service_id}::delegated_remuneration_criteria"
        or gate.get("scope") != "currentness_only"
    ):
        return None

    evidence = set(str(value) for value in row.get("source_currentness_evidence", []))
    for source_id in expected_source_ids:
        expected_suffix = "#" + source_id
        if not any(value.endswith(expected_suffix) for value in evidence):
            return None

    observed_date = str(currentness_contract.get("observed_date") or "")
    official_urls = [
        str(contract.get("official_source_url") or "")
        for contract in selected_contracts
        if contract is not None
    ]
    if not observed_date or not all(official_urls):
        return None

    return {
        "source_identity": {
            "canonical_source_id": "delegated-remuneration-national",
            "title": "介護報酬の算定方法・厚生労働大臣基準（別告示）",
            "official_source_url": official_urls[0],
            "official_page_urls": official_urls,
            "current_official_display_observed_on": observed_date,
        },
        "source_version_contains_scope": True,
        "ingestion_state": "INGESTED",
        "allowed_publication_units": sorted(REQUIRED_PUBLICATION_UNITS),
    }


def normalize_runtime_promotion(row: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(row)
    source = copy.deepcopy(source_identity(row))
    proof = copy.deepcopy(applicability_proof(row))

    delegated_context = delegated_runtime_binding_context(row)
    if delegated_context is not None:
        source = copy.deepcopy(delegated_context["source_identity"])
        normalized["ingestion_state"] = delegated_context["ingestion_state"]
        normalized["allowed_publication_units"] = delegated_context[
            "allowed_publication_units"
        ]

    evidence = row.get("currentness_evidence") or {}
    if not source.get("current_official_display_observed_on") and evidence.get("observed_on"):
        source["current_official_display_observed_on"] = evidence["observed_on"]

    normalized["source_identity"] = source
    normalized["applicability_proof"] = proof
    normalized["source_version_contains_scope"] = (
        row.get("source_version_contains_scope") is True
        or delegated_context is not None
        or (
            row.get("source_family") == "unit_price_regional_classification"
            and unit_price_currentness_scope_supported(row)
        )
    )
    normalized.pop("canonical_source_identity", None)
    normalized.pop("service_applicability_evidence", None)
    return normalized


def unit_price_service_contract_supported(
    service_id: str,
    source: dict[str, Any],
    proof: dict[str, Any],
) -> bool:
    meta = load_json(UNIT_PRICE_META_PATH)
    mappings = load_json(UNIT_PRICE_MAPPINGS_PATH)
    assurance = load_json(UNIT_PRICE_ITEM_BODY_PATH)

    mapping = next(
        (
            item
            for item in mappings.get("service_mappings", [])
            if item.get("service_id") == service_id
        ),
        None,
    )
    projection = next(
        (
            item
            for item in assurance.get("service_projections", [])
            if item.get("service_id") == service_id
        ),
        None,
    )
    if (
        not mapping
        or mapping.get("applicability") != "APPLIES"
        or not projection
        or projection.get("applicability") != "APPLIES"
        or projection.get("service_level_item_body") != "PASS"
        or projection.get("multiplier_profile_id")
        != mapping.get("multiplier_profile_id")
    ):
        return False

    profile = next(
        (
            item
            for item in assurance.get("profile_verification", [])
            if item.get("profile_id") == projection.get("multiplier_profile_id")
        ),
        None,
    )
    if (
        not profile
        or profile.get("verification_state") != "PASS"
        or profile.get("mapped_item_count") != 8
        or len(profile.get("rows") or []) != 8
    ):
        return False

    expected_urls = [str(value) for value in meta.get("source_urls", [])]
    expected_hashes = [str(value) for value in meta.get("source_sha256", [])]
    if source.get("official_page_urls") != expected_urls:
        return False
    if source.get("expected_page_sha256") is not None:
        if source.get("expected_page_sha256") != expected_hashes:
            return False

    return (
        proof.get("state") == "PASS_DIRECT_SERVICE_SCOPE"
        and proof.get("official_service_name")
        == mapping.get("official_service_name")
        and proof.get("multiplier_profile_id")
        == mapping.get("multiplier_profile_id")
        and proof.get("mapped_item_count")
        == projection.get("mapped_item_count")
        and proof.get("source_locator") == projection.get("source_locator")
    )


def delegated_service_contract_supported(service_id: str) -> bool:
    manifest = load_json(DELEGATED_MANIFEST_PATH)
    applicability = load_json(DELEGATED_APPLICABILITY_PATH)
    item_body = load_json(DELEGATED_ITEM_BODY_PATH)

    if (
        manifest.get("corpus_id") != "delegated-remuneration-national"
        or manifest.get("source_family") != "delegated_remuneration_criteria"
        or (manifest.get("assurance") or {}).get("item_body_verification") != "PASS"
        or (item_body.get("assurance_boundaries") or {}).get(
            "item_body_verification"
        )
        != "PASS"
    ):
        return False

    service = next(
        (
            row
            for row in applicability.get("services", [])
            if row.get("service_id") == service_id
        ),
        None,
    )
    if not service:
        return False

    mapped_node_ids = [str(value) for value in service.get("mapped_node_ids", [])]
    return (
        service.get("scope_state") == "SCOPE_DEFINED"
        and service.get("applicability_state") == "MAPPED"
        and service.get("ingestion_state") == "INGESTED"
        and (service.get("assurance") or {}).get("item_body_verification") == "PASS"
        and bool(mapped_node_ids)
        and service.get("mapped_node_count") == len(mapped_node_ids)
    )


def source_contract_supported(row: dict[str, Any]) -> bool:
    normalized = normalize_runtime_promotion(row)
    source_family = normalized.get("source_family")
    source = normalized.get("source_identity") or {}
    proof = normalized.get("applicability_proof") or {}
    canonical_source_id = source.get("canonical_source_id")

    if canonical_source_id not in RUNTIME_SUPPORTED_SOURCE_IDENTITIES:
        return False
    if source_family not in RUNTIME_SUPPORTED_SOURCE_FAMILIES:
        return False
    if normalized.get("promotion_applied") is not True:
        return False
    if normalized.get("projected_currentness_state") != "PASS":
        return False
    if normalized.get("ingestion_state") != "INGESTED":
        return False
    if normalized.get("item_body_state") != "PASS":
        return False
    if normalized.get("source_version_contains_scope") is not True:
        return False

    if canonical_source_id == "ordinance37":
        return (
            source_family == "governing_standards_ordinance"
            and proof.get("state") == "PASS_DIRECT_SERVICE_CHAPTER"
            and proof.get("direct_service_chapter_verified") is True
            and proof.get("discrepancies") == 0
            and bool(proof.get("target_articles"))
        )

    if canonical_source_id == "preventive-services-standards":
        return (
            source_family == "governing_standards_ordinance"
            and proof.get("state") == "PASS_DIRECT_SERVICE_SCOPE"
            and proof.get("direct_service_scope_verified") is True
            and proof.get("discrepancies") == 0
            and (
                bool(proof.get("common_source_node_ids"))
                or bool((proof.get("primary_range") or {}).get("from_node_id"))
                or bool(proof.get("variant_ranges"))
            )
        )

    if canonical_source_id in RESIDUAL_GOVERNING_SOURCE_IDENTITIES:
        return (
            source_family == "governing_standards_ordinance"
            and residual_governing_source_contract_supported(normalized)
        )

    if canonical_source_id == "mhlw-unit-price-current":
        service_id = str(normalized.get("service_id") or "")
        return (
            source_family == "unit_price_regional_classification"
            and source.get("currentness_class") == "CURRENT_OFFICIAL_CONSOLIDATED"
            and bool(source.get("version_id"))
            and source.get("effective_date") == "2024-04-01"
            and unit_price_service_contract_supported(service_id, source, proof)
        )

    if canonical_source_id == "delegated-remuneration-national":
        service_id = str(normalized.get("service_id") or "")
        return (
            source_family == "delegated_remuneration_criteria"
            and delegated_runtime_binding_context(row) is not None
            and delegated_service_contract_supported(service_id)
        )

    return False


def load_promotions() -> tuple[
    dict[tuple[str | None, str | None], dict[str, Any]],
    list[dict[str, str]],
    dict[tuple[str | None, str | None], str],
]:
    sources: list[dict[str, str]] = []
    promotions: dict[tuple[str | None, str | None], dict[str, Any]] = {}
    provenance: dict[tuple[str | None, str | None], str] = {}

    for path in currentness_paths():
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        payload = load_json(path)
        sources.append(
            {
                "path": relative,
                "git_blob_sha": git_blob_sha(path),
            }
        )
        rows = payload.get("promotions", [])
        if (
            path == GOVERNING_RESIDUAL_CURRENTNESS_PATH
            and payload.get("artifact_kind")
            == "GOVERNING_STANDARDS_RESIDUAL_CURRENTNESS_CLOSURE"
        ):
            rows = [
                normalize_governing_residual_decision(payload, row)
                for row in payload.get("decisions", [])
            ]
        for row in rows:
            key = cell_key(row)
            if key in promotions:
                raise ValueError(f"duplicate currentness promotion: {key}")
            promotions[key] = row
            provenance[key] = relative

    if FINAL_GOVERNING_CURRENTNESS_PATH.exists():
        path = FINAL_GOVERNING_CURRENTNESS_PATH
        relative = str(path.relative_to(ROOT)).replace("\\", "/")
        payload = load_json(path)
        if payload.get("artifact_kind") != "FINAL_STANDARDS_AND_RESIDUAL_RELATION_ASSURANCE":
            raise ValueError("unexpected final governing currentness artifact kind")
        sources.append(
            {
                "path": relative,
                "git_blob_sha": git_blob_sha(path),
            }
        )
        for row in (payload.get("governing_standards") or {}).get("decisions", []):
            normalized = normalize_final_governing_decision(payload, row)
            key = cell_key(normalized)
            existing = promotions.get(key)
            if not existing or existing.get("promotion_applied") is not False:
                raise ValueError(
                    f"final governing decision does not replace one deferred row: {key}"
                )
            promotions[key] = normalized
            provenance[key] = relative

    return promotions, sources, provenance


def build() -> dict[str, Any]:
    readiness = load_json(READINESS_PATH)
    promotions, currentness_sources, promotion_provenance = load_promotions()

    ready = [
        row
        for row in readiness.get("cells", [])
        if row.get("readiness") == "READY_FOR_PUBLICATION_REVIEW"
        and not row.get("blocking_reasons")
    ]

    publishable: list[dict[str, Any]] = []
    for row in ready:
        if row.get("source_family") not in RUNTIME_SUPPORTED_SOURCE_FAMILIES:
            continue
        promotion = promotions.get(cell_key(row))
        if not promotion or not source_contract_supported(promotion):
            continue
        publishable.append(row)

    family_order = {
        "governing_standards_ordinance": 0,
        "unit_price_regional_classification": 1,
        "delegated_remuneration_criteria": 2,
    }
    publishable.sort(
        key=lambda row: (
            family_order.get(str(row.get("source_family") or ""), 99),
            str(row.get("service_id") or ""),
            str(row.get("source_family") or ""),
        )
    )
    publication = [
        {
            "service_id": row["service_id"],
            "source_family": row["source_family"],
        }
        for row in publishable
    ]
    routes = list(publication)
    fields = {
        f"{row['service_id']}|{row['source_family']}": SAFE_FIELDS
        for row in publishable
    }
    runtime_source_binding_by_cell = {}
    for row in publishable:
        key_tuple = cell_key(row)
        encoded = f"{row['service_id']}|{row['source_family']}"
        runtime_source_binding_by_cell[encoded] = {
            "evidence_path": promotion_provenance[key_tuple],
            "promotion": normalize_runtime_promotion(promotions[key_tuple]),
        }

    if not ready:
        decision = "NO_PUBLICATION_CHANGE"
        reason = "No READY_FOR_PUBLICATION_REVIEW cells exist after integrated readiness regeneration."
    elif publication:
        decision = "PUBLISH_BOUNDED_READY_UNITS"
        reason = (
            "READY publication units supported by the shared multi-source runtime policy are "
            "bound across UI, search, API, and machine retrieval."
        )
    else:
        decision = "DEFER_PUBLICATION_FAIL_CLOSED"
        reason = (
            "READY candidates exist, but none are supported by the currently "
            "implemented runtime publication policy."
        )

    return {
        "format_version": 5,
        "generated_by": "scripts/build_bounded_publication_allowlist.py",
        "role": "Publication Runtime Binding / Progressive Release Worker",
        "source_readiness": {
            "path": "data/publication-readiness.generated.json",
            "git_blob_sha": git_blob_sha(READINESS_PATH),
            "expected_ready_candidate_count": len(ready),
        },
        "source_currentness": {
            "path": currentness_sources[0]["path"],
            "git_blob_sha": currentness_sources[0]["git_blob_sha"],
            "additional_sources": currentness_sources[1:],
        },
        "runtime_binding": {
            "required_for_nonempty_publication": True,
            "established": True,
            "policy_module": "lib/publication-policy.ts",
            "adapter_registry_module": "lib/publication-runtime-adapters.ts",
            "supported_source_families": sorted(RUNTIME_SUPPORTED_SOURCE_FAMILIES),
            "supported_source_identities": sorted(RUNTIME_SUPPORTED_SOURCE_IDENTITIES),
            "required_surfaces": [
                "UI",
                "SEARCH",
                "API",
                "MACHINE_RETRIEVAL",
            ],
        },
        "policy": {
            "explicit_publication_allowlist_required": True,
            "explicit_route_allowlist_required": True,
            "max_publication_cells": len(ready),
            "publication_selection_mode": "READY_RUNTIME_SUPPORTED_INTERSECTION",
            "arbitrary_batch_cap_enabled": False,
            "publication_does_not_enable_route": True,
            "blocked_cells_cannot_be_published": True,
            "allowlist_must_be_subset_of_ready_candidates": True,
            "unverified_relation_assertions_forbidden": True,
            "unreviewed_explanatory_text_forbidden": True,
            "search_and_machine_retrieval_must_respect_publication_allowlist": True,
            "preventive_services_group_with_non_preventive_counterpart": True,
            "preventive_support_is_standalone": True,
            "existing_public_surfaces_must_not_be_removed_by_zero_candidate_run": True,
            "runtime_binding_required_for_nonempty_publication": True,
        },
        "safe_publication_fields": SAFE_FIELDS,
        "forbidden_publication_fields": FORBIDDEN_FIELDS,
        "summary": {
            "ready_candidates_at_selection": len(ready),
            "ready_candidate_cells": [
                {
                    "service_id": row["service_id"],
                    "source_family": row["source_family"],
                    "ready_publication_units": row.get("ready_publication_units", []),
                }
                for row in ready
            ],
            "published_cells_added": len(publication),
            "routes_added": len(routes),
            "existing_public_surfaces_changed": False,
            "decision": decision,
            "reason": reason,
            "blocker_counts_at_selection": readiness.get("summary", {}).get(
                "blocking_axis_counts", {}
            ),
        },
        "publication_cell_allowlist": publication,
        "route_allowlist": routes,
        "field_allowlist_by_cell": fields,
        "runtime_source_binding_by_cell": runtime_source_binding_by_cell,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    artifact = build()
    rendered = json.dumps(artifact, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUTPUT_PATH.exists() or OUTPUT_PATH.read_text(encoding="utf-8") != rendered:
            raise SystemExit("bounded publication allowlist is stale; run builder")
        print("bounded publication allowlist: current")
        return
    OUTPUT_PATH.write_text(rendered, encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
