import noticeOrdinanceAuditData from "../data/notice-ordinance-explicit-reference-derived-audit.json" with { type: "json" };
import remunerationDelegationAuditData from "../data/remuneration-delegation-relation-independent-audit.json" with { type: "json" };
import remunerationSourceLinkAuditData from "../data/remuneration-source-link-independent-audit.json" with { type: "json" };
import feeNodesData from "../data/remuneration-current-skeleton.json" with { type: "json" };
import sourcesData from "../data/sources.json" with { type: "json" };
import { publicNoticeRecords } from "./notice-database.ts";
import {
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  GOVERNING_STANDARDS_SOURCE_FAMILY,
  UNIT_PRICE_SOURCE_FAMILY,
  type RuntimeSourceRecord,
} from "./publication-runtime-adapters.ts";

export type VerifiedPrimarySourceRelation = {
  relation_direction: "REFERENCES" | "REFERENCED_BY";
  relation_kind: "EXPLICIT_REFERENCE";
  label: string;
  related_record_id: string;
  title: string;
  href: string;
  source_url: string;
  source_locator: string;
};

const noticeOrdinanceAudit = noticeOrdinanceAuditData as any;
const remunerationDelegationAudit =
  remunerationDelegationAuditData as any;
const remunerationSourceLinkAudit =
  remunerationSourceLinkAuditData as any;
const feeNodes = feeNodesData as any[];
const sources = sourcesData as any[];

function sourceUrl(sourceId: string) {
  const source = sources.find((row) => row.id === sourceId);
  return String(source?.url || "");
}

function feeRelation(
  feeId: string,
  label: string,
): VerifiedPrimarySourceRelation | null {
  const fee = feeNodes.find((row) => row.id === feeId);
  if (!fee) return null;
  return {
    relation_direction: "REFERENCED_BY",
    relation_kind: "EXPLICIT_REFERENCE",
    label,
    related_record_id: feeId,
    title: String(fee.title || feeId),
    href: "/fees#" + feeId,
    source_url: sourceUrl(String(fee.source_id || "")),
    source_locator: String(fee.source_locator || ""),
  };
}

function verifiedNoticeRelationsForRule(
  serviceId: string,
  recordId: string,
): VerifiedPrimarySourceRelation[] {
  if (
    serviceId !== "dayservice" ||
    noticeOrdinanceAudit.audit_result !== "PASS"
  ) {
    return [];
  }

  return (noticeOrdinanceAudit.checks || [])
    .filter(
      (check: any) =>
        check.result === "PASS" &&
        check.basis_independent_verification === "PASS" &&
        check.to_ordinance_id === recordId,
    )
    .map((check: any) => {
      const notice = publicNoticeRecords.find(
        (row) =>
          row.service_id === serviceId &&
          row.id === check.from_notice_id,
      );
      if (!notice) return null;
      const primary = (notice.source_evidence || []).find(
        (evidence) => Boolean(evidence.source_url),
      );
      return {
        relation_direction: "REFERENCED_BY",
        relation_kind: "EXPLICIT_REFERENCE",
        label: "この条文を参照している基準解釈通知",
        related_record_id: notice.id,
        title: notice.title,
        href:
          "/notices?service=" +
          encodeURIComponent(serviceId) +
          "#" +
          notice.id,
        source_url: String(primary?.source_url || ""),
        source_locator: [
          ...(notice.number_path || []),
          notice.title,
        ]
          .filter(Boolean)
          .join(" / "),
      } satisfies VerifiedPrimarySourceRelation;
    })
    .filter(
      (
        relation: VerifiedPrimarySourceRelation | null,
      ): relation is VerifiedPrimarySourceRelation =>
        Boolean(relation),
    );
}

function verifiedDelegatedRelations(
  serviceId: string,
  record: RuntimeSourceRecord,
): VerifiedPrimarySourceRelation[] {
  if (
    serviceId !== "dayservice" ||
    remunerationDelegationAudit.audit_result !== "PASS"
  ) {
    return [];
  }

  const legacyNodeId = String(record.legacy_node_id || "");
  if (!legacyNodeId) return [];

  return (remunerationDelegationAudit.checks || [])
    .filter(
      (check: any) =>
        check.result === "PASS" &&
        check.to_id === legacyNodeId,
    )
    .map((check: any) =>
      feeRelation(
        String(check.from_id || ""),
        "この基準を参照している報酬告示",
      ),
    )
    .filter(
      (
        relation: VerifiedPrimarySourceRelation | null,
      ): relation is VerifiedPrimarySourceRelation =>
        Boolean(relation),
    );
}

function verifiedUnitPriceRelations(
  serviceId: string,
  record: RuntimeSourceRecord,
): VerifiedPrimarySourceRelation[] {
  if (
    serviceId !== "dayservice" ||
    remunerationSourceLinkAudit.audit_result !== "PASS" ||
    record.source_id !== "mhlw-unit-price-current"
  ) {
    return [];
  }

  return (remunerationSourceLinkAudit.checks || [])
    .filter(
      (check: any) =>
        check.result === "PASS" &&
        check.to_source_id === "mhlw-unit-price-current" &&
        check.evidence_kind === "unit_price",
    )
    .map((check: any) =>
      feeRelation(
        String(check.from_id || ""),
        "この単価告示を参照している報酬告示",
      ),
    )
    .filter(
      (
        relation: VerifiedPrimarySourceRelation | null,
      ): relation is VerifiedPrimarySourceRelation =>
        Boolean(relation),
    );
}

export function verifiedRelatedPrimarySources(
  serviceId: string,
  sourceFamily: string,
  record: RuntimeSourceRecord,
): VerifiedPrimarySourceRelation[] {
  if (sourceFamily === GOVERNING_STANDARDS_SOURCE_FAMILY) {
    return verifiedNoticeRelationsForRule(serviceId, record.id);
  }
  if (sourceFamily === DELEGATED_REMUNERATION_SOURCE_FAMILY) {
    return verifiedDelegatedRelations(serviceId, record);
  }
  if (sourceFamily === UNIT_PRICE_SOURCE_FAMILY) {
    return verifiedUnitPriceRelations(serviceId, record);
  }
  return [];
}

export function verifiedRelatedPrimarySourcesForRecords(
  serviceId: string,
  sourceFamily: string,
  records: readonly RuntimeSourceRecord[],
) {
  const unique = new Map<string, VerifiedPrimarySourceRelation>();
  for (const record of records) {
    for (const relation of verifiedRelatedPrimarySources(
      serviceId,
      sourceFamily,
      record,
    )) {
      const key = [
        relation.relation_direction,
        relation.related_record_id,
        relation.href,
      ].join("|");
      if (!unique.has(key)) unique.set(key, relation);
    }
  }
  return [...unique.values()];
}
