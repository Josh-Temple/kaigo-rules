export const GOVERNING_STANDARDS_SOURCE_FAMILY =
  "governing_standards_ordinance";
export const UNIT_PRICE_SOURCE_FAMILY =
  "unit_price_regional_classification";
export const DELEGATED_REMUNERATION_SOURCE_FAMILY =
  "delegated_remuneration_criteria";
export const DELEGATED_REMUNERATION_CANONICAL_SOURCE_ID =
  "delegated-remuneration-national";

export type RuntimeSourceRecord = {
  id: string;
  node_type?: string;
  article_num?: string;
  article_title?: string;
  caption?: string;
  label?: string;
  path?: string[];
  official_text?: string;
  source_url?: string;
  source_locator?: string;
  region_class?: string;
  service?: string;
  ratio_text?: string;
  ratio_per_thousand?: number;
  unit_price_yen?: number;
  source_id?: string;
  canonical_node_id?: string;
  legacy_node_id?: string;
  item_label?: string;
  heading?: string;
  source_document_title?: string;
};

export type RuntimeSourceIdentity = {
  canonical_source_id?: string;
  law_id?: string;
  title?: string;
  official_source_url?: string;
  official_page_urls?: string[];
  version_id?: string;
  effective_date?: string;
  verified_at?: string;
  current_official_display_observed_on?: string;
  currentness_class?: string;
  expected_page_sha256?: string[];
  source_form?: string;
};

export type RuntimeApplicabilityProof = {
  state?: string;
  inherited_from_sibling_service?: boolean;
  direct_service_chapter_verified?: boolean;
  direct_service_scope_verified?: boolean;
  target_articles?: string[];
  common_source_node_ids?: string[];
  primary_range?: {
    from_node_id?: string;
    through_node_id?: string;
    include_inserted_articles?: boolean;
  };
  variant_ranges?: Array<{
    from_node_id?: string;
    through_node_id?: string;
  }>;
  discrepancies?: number;
  official_service_name?: string;
  multiplier_profile_id?: string;
  source_locator?: string;
  mapped_item_count?: number;
  scope_identity_present?: boolean;
  regular_preventive_inheritance_used?: boolean;
  incorporation_or_read_as_semantics_promoted?: boolean;
  direct_article_numbers?: string[];
  scope_path?: string;
};

export type RuntimePromotion = {
  service_id?: string;
  source_family?: string;
  canonical_source_id?: string;
  scope_path?: string;
  decision?: string;
  blocker?: string | null;
  source_identity?: RuntimeSourceIdentity;
  canonical_source_identity?: RuntimeSourceIdentity;
  applicability_proof?: RuntimeApplicabilityProof;
  service_applicability_evidence?: RuntimeApplicabilityProof;
  currentness_evidence?: {
    official_source_locator?: string;
    observed_on?: string;
    effective_date?: string;
    supersession_check?: string;
    live_verifier?: string;
    workflow?: string;
  };
  allowed_publication_units?: string[];
  mapped_node_count?: number;
  mapped_node_ids?: string[];
  mapped_source_ids?: string[];
  source_currentness_evidence?: string[];
  source_identity_matches_item_body_source?: boolean;
  projection_gate?: {
    kind?: string;
    allowed?: boolean;
    identity?: string;
    scope?: string;
  };
  source_version_contains_scope?: boolean;
  ingestion_state?: string;
  item_body_state?: string;
  projected_currentness_state?: string;
  promotion_applied?: boolean;
};

export type RuntimeProjectionTrust = {
  service_id: string;
  service_label: string;
  source_family: string;
  canonical_source_id: string;
  source_title: string;
  source_url: string;
  source_version: string;
  effective_date: string;
  checked_at: string;
};

export type RuntimeSourceAdapter = {
  canonicalSourceId: string;
  sourceFamily: string;
  nodePrefix: string;
  recordKind: "RULE" | "UNIT_PRICE" | "DELEGATED_CRITERIA";
  supportsPromotion: (promotion: RuntimePromotion) => boolean;
  recordsForPromotion: (
    promotion: RuntimePromotion,
  ) => RuntimeSourceRecord[];
  recordIsPublished: (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => boolean;
  sourceTitle: (promotion: RuntimePromotion) => string;
  defaultSourceUrl: (promotion: RuntimePromotion) => string;
  applicabilityLabel: (serviceLabel: string) => string;
  currentnessLabel: string;
  projectItemBody: (
    record: RuntimeSourceRecord,
  ) => Record<string, unknown>;
  sourceText: (record: RuntimeSourceRecord) => string;
  sourceLocator: (
    record: RuntimeSourceRecord,
    promotion: RuntimePromotion,
  ) => { url: string; locator: string };
};

export function sourceIdentity(promotion: RuntimePromotion) {
  return (
    promotion.source_identity ||
    promotion.canonical_source_identity ||
    {}
  );
}

export function applicabilityProof(promotion: RuntimePromotion) {
  return (
    promotion.applicability_proof ||
    promotion.service_applicability_evidence ||
    {}
  );
}

export function commonPromotionSafety(
  promotion: RuntimePromotion,
) {
  return (
    promotion.promotion_applied === true &&
    promotion.projected_currentness_state === "PASS" &&
    promotion.ingestion_state === "INGESTED" &&
    promotion.item_body_state === "PASS"
  );
}
