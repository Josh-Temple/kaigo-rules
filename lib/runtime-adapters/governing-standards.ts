import ordinanceMetaData from "../../data/ordinance37-meta.json" with { type: "json" };
import ordinanceNodesData from "../../data/ordinance37-nodes.json" with { type: "json" };
import preventiveMetaData from "../../data/shared/standards/preventive-services-standards/meta.json" with { type: "json" };
import preventiveNodesData from "../../data/shared/standards/preventive-services-standards/nodes.json" with { type: "json" };
import communityBasedMetaData from "../../data/shared/standards/community-based-standards/meta.json" with { type: "json" };
import communityBasedNodesData from "../../data/shared/standards/community-based-standards/nodes.json" with { type: "json" };
import careManagementMetaData from "../../data/shared/standards/care-management-standards/meta.json" with { type: "json" };
import careManagementNodesData from "../../data/shared/standards/care-management-standards/nodes.json" with { type: "json" };
import preventiveSupportMetaData from "../../data/shared/standards/preventive-support-standards/meta.json" with { type: "json" };
import preventiveSupportNodesData from "../../data/shared/standards/preventive-support-standards/nodes.json" with { type: "json" };
import elderlyWelfareFacilityMetaData from "../../data/shared/standards/elderly-welfare-facility-standards/meta.json" with { type: "json" };
import elderlyWelfareFacilityNodesData from "../../data/shared/standards/elderly-welfare-facility-standards/nodes.json" with { type: "json" };
import geriatricHealthFacilityMetaData from "../../data/shared/standards/geriatric-health-services-facility-standards/meta.json" with { type: "json" };
import geriatricHealthFacilityNodesData from "../../data/shared/standards/geriatric-health-services-facility-standards/nodes.json" with { type: "json" };
import careMedicalFacilityMetaData from "../../data/shared/standards/long-term-care-medical-facility-standards/meta.json" with { type: "json" };
import careMedicalFacilityNodesData from "../../data/shared/standards/long-term-care-medical-facility-standards/nodes.json" with { type: "json" };
import preventiveCommunityMetaData from "../../data/shared/standards/preventive-community-based-standards/meta.json" with { type: "json" };
import preventiveCommunityNodesData from "../../data/shared/standards/preventive-community-based-standards/nodes.json" with { type: "json" };
import {
  GOVERNING_STANDARDS_SOURCE_FAMILY,
  applicabilityProof,
  commonPromotionSafety,
  sourceIdentity,
  type RuntimePromotion,
  type RuntimeSourceAdapter,
  type RuntimeSourceRecord,
} from "./types.ts";

function normalizeRuleNodes(data: any): RuntimeSourceRecord[] {
  if (Array.isArray(data)) return data as RuntimeSourceRecord[];
  return Array.isArray(data?.nodes)
    ? (data.nodes as RuntimeSourceRecord[])
    : [];
}

function articleNumberFromRecordId(
  recordId: string,
  nodePrefix: string,
) {
  const escapedPrefix = nodePrefix.replace(
    /[.*+?^$()|[\]\\]/g,
    "\\$&",
  );
  const match = recordId.match(
    new RegExp(
      "^" +
        escapedPrefix +
        "\\.article\\.([0-9]+(?:-[0-9]+)?)(?:\\.|$)",
    ),
  );
  return match?.[1] || null;
}

function articleKey(value: string) {
  return value
    .split("-")
    .map((part) => Number.parseInt(part, 10) || 0);
}

function compareArticleNumber(a: string, b: string) {
  const ak = articleKey(a);
  const bk = articleKey(b);
  for (
    let i = 0;
    i < Math.max(ak.length, bk.length);
    i += 1
  ) {
    const diff = (ak[i] || 0) - (bk[i] || 0);
    if (diff) return diff;
  }
  return 0;
}

const ordinanceMeta = ordinanceMetaData as any;
const preventiveMeta = preventiveMetaData as any;
const ordinanceNodes = normalizeRuleNodes(ordinanceNodesData);
const preventiveNodes = normalizeRuleNodes(preventiveNodesData);

function publishedRuleArticles(
  promotion: RuntimePromotion,
  nodePrefix: string,
  mode: "TARGET_ARTICLES" | "RANGES",
) {
  const proof = applicabilityProof(promotion);
  if (mode === "TARGET_ARTICLES") {
    return new Set(
      (proof.target_articles || []).map(String),
    );
  }

  const selected = new Set<string>();
  for (const nodeId of proof.common_source_node_ids || []) {
    const article = articleNumberFromRecordId(
      String(nodeId),
      nodePrefix,
    );
    if (article) selected.add(article);
  }

  const ranges = [
    proof.primary_range,
    ...(proof.variant_ranges || []),
  ].filter(Boolean) as Array<{
    from_node_id?: string;
    through_node_id?: string;
  }>;

  const nodes =
    nodePrefix === "standards35"
      ? preventiveNodes
      : ordinanceNodes;

  for (const range of ranges) {
    const from = range.from_node_id
      ? articleNumberFromRecordId(
          range.from_node_id,
          nodePrefix,
        )
      : null;
    const through = range.through_node_id
      ? articleNumberFromRecordId(
          range.through_node_id,
          nodePrefix,
        )
      : null;
    if (!from || !through) continue;
    for (const node of nodes) {
      if (node.node_type !== "article") continue;
      const article = String(node.article_num || "");
      if (
        article &&
        compareArticleNumber(article, from) >= 0 &&
        compareArticleNumber(article, through) <= 0
      ) {
        selected.add(article);
      }
    }
  }

  return selected;
}

function recordArticleNumber(
  record: RuntimeSourceRecord,
  nodePrefix: string,
) {
  return (
    record.article_num ||
    articleNumberFromRecordId(
      String(record.id || ""),
      nodePrefix,
    )
  );
}

function ruleAdapter(args: {
  canonicalSourceId: string;
  meta: any;
  nodes: RuntimeSourceRecord[];
  nodePrefix: string;
  applicabilityState: string;
  verifiedFlag:
    | "direct_service_chapter_verified"
    | "direct_service_scope_verified";
  scopeMode: "TARGET_ARTICLES" | "RANGES";
  label: (serviceLabel: string) => string;
}): RuntimeSourceAdapter {
  const {
    canonicalSourceId,
    meta,
    nodes,
    nodePrefix,
    applicabilityState,
    verifiedFlag,
    scopeMode,
    label,
  } = args;

  const supportsPromotion = (
    promotion: RuntimePromotion,
  ) => {
    if (
      !commonPromotionSafety(promotion) ||
      promotion.source_version_contains_scope !== true ||
      promotion.source_family !==
        GOVERNING_STANDARDS_SOURCE_FAMILY
    ) {
      return false;
    }

    const source = sourceIdentity(promotion);
    const proof = applicabilityProof(promotion);
    const sourceLawId = String(source.law_id || "");
    const adapterLawId = String(meta?.law_id || "");
    const sourceVersion = String(
      source.version_id || "",
    );
    const adapterVersion = String(
      meta?.current_revision?.law_revision_id || "",
    );

    if (
      source.canonical_source_id !==
        canonicalSourceId ||
      !sourceLawId ||
      !adapterLawId ||
      sourceLawId !== adapterLawId ||
      !sourceVersion ||
      !adapterVersion ||
      sourceVersion !== adapterVersion
    ) {
      return false;
    }

    if (
      proof.state !== applicabilityState ||
      proof[verifiedFlag] !== true ||
      proof.discrepancies !== 0
    ) {
      return false;
    }

    return (
      publishedRuleArticles(
        promotion,
        nodePrefix,
        scopeMode,
      ).size > 0
    );
  };

  const recordIsPublished = (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => {
    if (!supportsPromotion(promotion)) return false;
    const article = recordArticleNumber(record, nodePrefix);
    return Boolean(
      article &&
        publishedRuleArticles(
          promotion,
          nodePrefix,
          scopeMode,
        ).has(String(article)),
    );
  };

  return {
    canonicalSourceId,
    sourceFamily: GOVERNING_STANDARDS_SOURCE_FAMILY,
    nodePrefix,
    recordKind: "RULE",
    supportsPromotion,
    recordsForPromotion: (promotion) => {
      if (!supportsPromotion(promotion)) return [];
      const articles = publishedRuleArticles(
        promotion,
        nodePrefix,
        scopeMode,
      );
      return nodes.filter((record) => {
        const article = recordArticleNumber(record, nodePrefix);
        return Boolean(article && articles.has(String(article)));
      });
    },
    recordIsPublished,
    sourceTitle: () =>
      String(meta?.law_title || ""),
    defaultSourceUrl: (promotion) =>
      String(
        sourceIdentity(promotion).official_source_url ||
          meta?.source_page ||
          "",
      ),
    applicabilityLabel: label,
    currentnessLabel:
      "現行のe-Gov本文を確認済み",
    projectItemBody: (record) => ({
      article_num: String(record.article_num || ""),
      article_title: String(
        record.article_title || "",
      ),
      caption: String(record.caption || ""),
      label: String(record.label || ""),
      path: Array.isArray(record.path)
        ? record.path.map(String)
        : [],
    }),
    sourceText: (record) =>
      String(record.official_text || ""),
    sourceLocator: (record, promotion) => ({
      url: String(
        record.source_url ||
          sourceIdentity(promotion)
            .official_source_url ||
          meta?.source_page ||
          "",
      ),
      locator: String(record.source_locator || ""),
    }),
  };
}

const communityBasedMeta = communityBasedMetaData as any;
const communityBasedNodes = normalizeRuleNodes(communityBasedNodesData);
const careManagementMeta = careManagementMetaData as any;
const careManagementNodes = normalizeRuleNodes(careManagementNodesData);
const preventiveSupportMeta = preventiveSupportMetaData as any;
const preventiveSupportNodes = normalizeRuleNodes(preventiveSupportNodesData);
const elderlyWelfareFacilityMeta = elderlyWelfareFacilityMetaData as any;
const elderlyWelfareFacilityNodes = normalizeRuleNodes(
  elderlyWelfareFacilityNodesData,
);
const geriatricHealthFacilityMeta = geriatricHealthFacilityMetaData as any;
const geriatricHealthFacilityNodes = normalizeRuleNodes(
  geriatricHealthFacilityNodesData,
);
const careMedicalFacilityMeta = careMedicalFacilityMetaData as any;
const careMedicalFacilityNodes = normalizeRuleNodes(
  careMedicalFacilityNodesData,
);
const preventiveCommunityMeta = preventiveCommunityMetaData as any;
const preventiveCommunityNodes = normalizeRuleNodes(
  preventiveCommunityNodesData,
);

function boundedDirectScopeRuleAdapter(args: {
  canonicalSourceId: string;
  meta: any;
  nodes: RuntimeSourceRecord[];
  nodePrefix: string;
}): RuntimeSourceAdapter {
  const { canonicalSourceId, meta, nodes, nodePrefix } = args;
  const availableArticles = new Set(
    nodes
      .filter((record) => record.node_type === "article")
      .map((record) => String(record.article_num || ""))
      .filter(Boolean),
  );

  const supportsPromotion = (
    promotion: RuntimePromotion,
  ) => {
    if (
      !commonPromotionSafety(promotion) ||
      promotion.source_version_contains_scope !== true ||
      promotion.source_family !==
        GOVERNING_STANDARDS_SOURCE_FAMILY ||
      promotion.canonical_source_id !== canonicalSourceId ||
      promotion.decision !== "PROMOTE_PASS_BOUNDED" ||
      promotion.blocker !== null
    ) {
      return false;
    }

    const source = sourceIdentity(promotion);
    const proof = applicabilityProof(promotion);
    const gate = promotion.projection_gate || {};
    const serviceId = String(promotion.service_id || "");
    const directArticles = (
      proof.direct_article_numbers || []
    ).map(String);

    if (
      source.canonical_source_id !== canonicalSourceId ||
      source.source_form !== "OFFICIAL_VERSIONED_CURRENT_TEXT" ||
      !source.law_id ||
      source.law_id !== String(meta?.law_id || "") ||
      !source.version_id ||
      source.version_id !==
        String(meta?.current_revision?.law_revision_id || "") ||
      source.official_source_url !==
        String(meta?.source_page || "") ||
      source.effective_date !==
        String(
          meta?.current_revision
            ?.amendment_enforcement_date || "",
        )
    ) {
      return false;
    }

    if (
      proof.state !== "PASS_DIRECT_SCOPE_CURRENT_VERSION" ||
      proof.scope_identity_present !== true ||
      proof.regular_preventive_inheritance_used !== false ||
      proof.incorporation_or_read_as_semantics_promoted !==
        false ||
      !proof.scope_path ||
      !directArticles.length ||
      new Set(directArticles).size !== directArticles.length ||
      !directArticles.every((article) =>
        availableArticles.has(article),
      )
    ) {
      return false;
    }

    return (
      gate.kind === "EXPLICIT_BOUNDED_ALLOWLIST" &&
      gate.allowed === true &&
      gate.identity ===
        serviceId +
          "::" +
          GOVERNING_STANDARDS_SOURCE_FAMILY &&
      gate.scope === "currentness_only"
    );
  };

  const recordIsPublished = (
    promotion: RuntimePromotion,
    record: RuntimeSourceRecord,
  ) => {
    if (!supportsPromotion(promotion)) return false;
    const directArticles = new Set(
      (applicabilityProof(promotion)
        .direct_article_numbers || []).map(String),
    );
    const article = recordArticleNumber(record, nodePrefix);
    return Boolean(
      article && directArticles.has(String(article)),
    );
  };

  return {
    canonicalSourceId,
    sourceFamily: GOVERNING_STANDARDS_SOURCE_FAMILY,
    nodePrefix,
    recordKind: "RULE",
    supportsPromotion,
    recordsForPromotion: (promotion) => {
      if (!supportsPromotion(promotion)) return [];
      const directArticles = new Set(
        (applicabilityProof(promotion)
          .direct_article_numbers || []).map(String),
      );
      return nodes.filter((record) => {
        const article = recordArticleNumber(record, nodePrefix);
        return Boolean(article && directArticles.has(String(article)));
      });
    },
    recordIsPublished,
    sourceTitle: () =>
      String(meta?.law_title || ""),
    defaultSourceUrl: (promotion) =>
      String(
        sourceIdentity(promotion).official_source_url ||
          meta?.source_page ||
          "",
      ),
    applicabilityLabel: (serviceLabel) =>
      serviceLabel +
      "の検証済み直接適用範囲に含まれる条文として確認済み",
    currentnessLabel:
      "現行のe-Gov本文を確認済み",
    projectItemBody: (record) => ({
      article_num: String(record.article_num || ""),
      article_title: String(
        record.article_title || "",
      ),
      caption: String(record.caption || ""),
      label: String(record.label || ""),
      path: Array.isArray(record.path)
        ? record.path.map(String)
        : [],
    }),
    sourceText: (record) =>
      String(record.official_text || ""),
    sourceLocator: (record, promotion) => ({
      url: String(
        record.source_url ||
          sourceIdentity(promotion)
            .official_source_url ||
          meta?.source_page ||
          "",
      ),
      locator: String(record.source_locator || ""),
    }),
  };
}

export const GOVERNING_STANDARDS_ADAPTERS: Record<
  string,
  RuntimeSourceAdapter
> = {
  ordinance37: ruleAdapter({
    canonicalSourceId: "ordinance37",
    meta: ordinanceMeta,
    nodes: ordinanceNodes,
    nodePrefix: "ordinance37",
    applicabilityState:
      "PASS_DIRECT_SERVICE_CHAPTER",
    verifiedFlag:
      "direct_service_chapter_verified",
    scopeMode: "TARGET_ARTICLES",
    label: (serviceLabel) =>
      serviceLabel +
      "の直接適用章に含まれる条文として確認済み",
  }),
  "preventive-services-standards": ruleAdapter({
    canonicalSourceId:
      "preventive-services-standards",
    meta: preventiveMeta,
    nodes: preventiveNodes,
    nodePrefix: "standards35",
    applicabilityState:
      "PASS_DIRECT_SERVICE_SCOPE",
    verifiedFlag:
      "direct_service_scope_verified",
    scopeMode: "RANGES",
    label: (serviceLabel) =>
      serviceLabel +
      "の直接適用範囲に含まれる条文として確認済み",
  }),
  "community-based-standards": boundedDirectScopeRuleAdapter({
    canonicalSourceId: "community-based-standards",
    meta: communityBasedMeta,
    nodes: communityBasedNodes,
    nodePrefix: "standards34",
  }),
  "care-management-standards": boundedDirectScopeRuleAdapter({
    canonicalSourceId: "care-management-standards",
    meta: careManagementMeta,
    nodes: careManagementNodes,
    nodePrefix: "standards38",
  }),
  "preventive-support-standards": boundedDirectScopeRuleAdapter({
    canonicalSourceId: "preventive-support-standards",
    meta: preventiveSupportMeta,
    nodes: preventiveSupportNodes,
    nodePrefix: "standards-preventive-support",
  }),
  "elderly-welfare-facility-standards": boundedDirectScopeRuleAdapter({
    canonicalSourceId: "elderly-welfare-facility-standards",
    meta: elderlyWelfareFacilityMeta,
    nodes: elderlyWelfareFacilityNodes,
    nodePrefix: "standards39",
  }),
  "geriatric-health-services-facility-standards":
    boundedDirectScopeRuleAdapter({
      canonicalSourceId:
        "geriatric-health-services-facility-standards",
      meta: geriatricHealthFacilityMeta,
      nodes: geriatricHealthFacilityNodes,
      nodePrefix: "standards40",
    }),
  "long-term-care-medical-facility-standards":
    boundedDirectScopeRuleAdapter({
      canonicalSourceId:
        "long-term-care-medical-facility-standards",
      meta: careMedicalFacilityMeta,
      nodes: careMedicalFacilityNodes,
      nodePrefix: "standards-medical-facility",
    }),
  "preventive-community-based-standards":
    boundedDirectScopeRuleAdapter({
      canonicalSourceId:
        "preventive-community-based-standards",
      meta: preventiveCommunityMeta,
      nodes: preventiveCommunityNodes,
      nodePrefix: "standards36",
    }),
};
