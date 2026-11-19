"""Run the repository data checks in their established order."""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    ('python', 'scripts/build_careact_service_indexes.py', '--check'),
    ('python', 'scripts/build_service_catalog.py', '--check'),
    ('python', 'scripts/build_homevisit_careact_index.py', '--check'),
    ('python', 'scripts/build_homevisit_ordinance37_index.py', '--check'),
    ('python', 'scripts/build_dayrehab_article119_relations.py', '--check'),
    ('python', 'scripts/build_dayrehab_ordinance37_index.py', '--check'),
    ('node', 'scripts/validate-data.mjs'),
    ('python', 'scripts/build_notice_review_packet.py', '--check'),
    ('python', 'scripts/validate_notice_review.py'),
    ('python', 'scripts/build_notice_rouki25_audit_report.py', '--check'),
    ('python', 'scripts/validate_notice_rouki25_audit.py'),
    ('python', 'scripts/validate_notice_currentness_investigation.py'),
    ('python', 'scripts/validate_notice_rouki25_currentness_ledger.py'),
    ('python', 'scripts/validate_notice_rouki25_watch_receipt.py'),
    ('python', 'scripts/validate_existing_service_currentness_wave.py'),
    ('python', 'scripts/validate_fee_guidance_independent_verification.py'),
    ('python', 'scripts/validate_shared_fee_guidance.py'),
    ('python', 'scripts/validate_fee_guidance_item_body_assurance.py'),
    ('python', 'scripts/validate_other_national_materials.py'),
    ('python', 'scripts/validate_remuneration_independent_audit.py'),
    ('python', 'scripts/validate_remuneration_notification_assurance.py'),
    ('python', 'scripts/import_delegated_remuneration_national_corpus.py', '--check'),
    ('python', 'scripts/build_delegated_remuneration_shared_corpus.py', '--check'),
    ('python', 'scripts/validate_delegated_remuneration_item_body_assurance.py'),
    ('python', 'scripts/validate_unit_price_service_multipliers.py'),
    ('python', 'scripts/validate_unit_price_independent_audit.py'),
    ('python', 'scripts/build_remuneration_source_link_derived_audit.py', '--check'),
    ('python', 'scripts/validate_fee_guidance_relation_independent_audit.py'),
    ('python', 'scripts/build_notice_ordinance_explicit_reference_derived_audit.py', '--check'),
    ('python', 'scripts/validate_remuneration_source_link_independent_audit.py'),
    ('python', 'scripts/build_careact_service_identity_derived_audit.py', '--check'),
    ('python', 'scripts/build_relation_verification_queue.py', '--check'),
    ('python', 'scripts/build_relation_human_review_packet.py', '--check'),
    ('python', 'scripts/build_relation_human_review_evidence_pack.py', '--check'),
    ('python', 'scripts/build_relation_human_review_pilot.py', '--check'),
    ('python', 'scripts/build_relation_human_review_batches.py', '--check'),
    ('python', 'scripts/validate_relation_human_review_decisions.py'),
    ('python', 'scripts/build_relation_human_review_decision_effects.py', '--check'),
    ('python', 'scripts/validate_bounded_currentness_closure.py'),
    ('python', 'scripts/validate_governing_standards_residual_currentness_worker_a.py'),
    ('python', 'scripts/validate_high_value_currentness_closure.py'),
    ('python', 'scripts/validate_high_value_currentness_expansion_worker_c.py'),
    ('python', 'scripts/build_verification_registry.py', '--check'),
    ('python', 'scripts/validate_dayrehab_fee_layers.py'),
    ('python', 'scripts/build_database_coverage_matrix.py', '--check'),
    ('python', 'scripts/validate_database_coverage_matrix.py'),
    ('python', 'scripts/build_publication_requirement_scoping.py', '--check'),
    ('python', 'scripts/validate_publication_requirement_scoping.py'),
    ('python', 'scripts/build_publication_readiness.py', '--check'),
    ('python', 'scripts/validate_publication_readiness.py'),
    ('python', 'scripts/build_bounded_publication_allowlist.py', '--check'),
    ('python', 'scripts/validate_bounded_publication_allowlist.py'),
    ('python', 'scripts/build_product_value_snapshot.py', '--check'),
    ('python', 'scripts/build_question_context_packages.py', '--check'),
    ('python', 'scripts/validate_faq_evidence_support.py'),
    ('python', 'scripts/validate_service_manifest.py'),
    ('python', 'scripts/build_shared_standards_service_relations.py', '--check'),
    ('python', 'scripts/validate_shared_standards.py'),
    ('python', 'scripts/validate_egov_content_independent_audit.py'),
    ('python', 'scripts/validate_dayrehab_ordinance37_independent_audit.py'),
    ('python', 'scripts/validate_dayrehab_article119_relation_audit.py'),
    ('python', 'scripts/validate_dayrehab_rouki25_historical_audit.py'),
    ('python', 'scripts/validate_homevisit_rouki25_historical_audit.py'),
    ('python', 'scripts/validate_rouki25_historical_service_audit.py', '--service-id', 'homebath', '--expected-items', '13'),
    ('python', 'scripts/validate_rouki25_historical_service_audit.py', '--service-id', 'homenursing', '--expected-items', '12'),
    ('python', 'scripts/validate_rouki25_historical_service_audit.py', '--service-id', 'homerehab', '--expected-items', '7'),
    ('python', 'scripts/validate_rouki25_historical_service_audit.py', '--service-id', 'homecaremanagement', '--expected-items', '9'),
    ('python', 'scripts/validate_rouki25_historical_service_audit.py', '--service-id', 'shortstay-life', '--expected-items', '34'),
    ('python', 'scripts/validate_standards_interpretation_staging.py', '--service-id', 'night-homevisit', '--expected-items', '25'),
    ('python', 'scripts/validate_standards_interpretation_staging.py', '--service-id', 'regular-round', '--expected-items', '21'),
    ('python', 'scripts/validate_standards_interpretation_staging.py', '--service-id', 'community-dayservice', '--expected-items', '21'),
    ('python', 'scripts/validate_standards_interpretation_staging.py', '--service-id', 'care-management', '--expected-items', '32'),
    ('python', 'scripts/validate_standards_interpretation_staging.py', '--service-id', 'preventive-support', '--expected-items', '34'),
    ('python', 'scripts/validate_standards_interpretation_source_inventory.py', '--service-id', 'preventive-support', '--expected-items', '34'),
    ('python', 'scripts/validate_standards_interpretation_source_inventory.py', '--service-id', 'care-management', '--expected-items', '32'),
    ('python', 'scripts/validate_standards_interpretation_source_inventory.py', '--service-id', 'night-homevisit', '--expected-items', '25'),
    ('python', 'scripts/validate_standards_interpretation_source_inventory.py', '--service-id', 'regular-round', '--expected-items', '21'),
    ('python', 'scripts/validate_standards_interpretation_source_inventory.py', '--service-id', 'community-dayservice', '--expected-items', '21'),
    ('python', 'scripts/validate_standards_interpretation_item_body.py', '--all'),
    ('python', 'scripts/validate_standards_interpretation_currentness.py'),
    ('python', 'scripts/validate_qa_corpus_independent_audit.py'),
    ('python', 'scripts/validate_qa_service_mapping.py'),
    ('python', 'scripts/validate_relation_semantic_independent_audit.py'),
    ('python', 'scripts/validate_careact_internal_relation_independent_audit.py'),
    ('python', 'scripts/validate_cross_layer_source_chain_independent_audit.py'),
    ('python', 'scripts/validate_remuneration_delegation_relation_independent_audit.py'),
    ('python', 'scripts/validate_kaigo_ops_field_validation.py'),
    ('python', 'scripts/validate_machine_retrieval_benchmark.py'),
    ('npm', 'run', 'test:service-scope'),
    ('npm', 'run', 'test:service-scope-surfaces'),
    ('npm', 'run', 'test:question-search'),
    ('npm', 'run', 'test:database-search'),
    ('python', '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'),
    ('python', 'scripts/build_qa_service_relations.py', '--check'),
    ('python', 'scripts/validate_qa_service_relations.py'),
)


def main() -> int:
    for number, command in enumerate(CHECKS, 1):
        label = shlex.join(command)
        print(f"[{number}/{len(CHECKS)}] {label}", flush=True)
        try:
            result = subprocess.run(command, cwd=ROOT, check=False)
        except OSError as error:
            print(f"Could not run {label}: {error}", flush=True)
            return 1
        if result.returncode:
            print(f"Failed [{number}/{len(CHECKS)}]: {label} (exit {result.returncode})", flush=True)
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
