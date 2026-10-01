import reviewPacketData from "../data/notice-review-packet.json" with { type: "json" };
import dayrehabData from "../data/services/dayrehab/rouki25-historical.generated.json" with { type: "json" };

export type PublicNoticeServiceId = "dayservice" | "dayrehab";

export type PublicNoticeEvidence = {
  source_id: string;
  source_title: string;
  source_url: string;
  page_start?: number | null;
  page_end?: number | null;
  role?: string;
  note?: string;
};

export type PublicNoticeRecord = {
  id: string;
  service_id: PublicNoticeServiceId;
  service_label: string;
  section: string;
  number_path: string[];
  title: string;
  body_text: string;
  source_state: "RECONSTRUCTED_CANDIDATE" | "OFFICIAL_HISTORICAL_HTML";
  content_verification: "PASS";
  currentness_state: "HOLD" | "GAP";
  human_review_state: "NOT_REVIEWED";
  verification_layer_id: "rouki25-dayservice" | "rouki25-dayrehab";
  source_evidence: PublicNoticeEvidence[];
};

type ReviewItem = {
  notice_id: string;
  section: string;
  title: string;
  number_path: string[];
  candidate_text: string;
  human_verification_status: string;
  source_evidence: PublicNoticeEvidence[];
  independent_verification?: { result?: string };
};

const dayserviceReview = reviewPacketData as { items?: ReviewItem[] };
const dayrehab = dayrehabData as any;

const dayserviceRecords: PublicNoticeRecord[] = (dayserviceReview.items || []).map(
  (item) => ({
    id: item.notice_id,
    service_id: "dayservice",
    service_label: "通所介護",
    section: item.section,
    number_path: item.number_path,
    title: item.title,
    body_text: item.candidate_text,
    source_state: "RECONSTRUCTED_CANDIDATE",
    content_verification: "PASS",
    currentness_state: "HOLD",
    human_review_state: "NOT_REVIEWED",
    verification_layer_id: "rouki25-dayservice",
    source_evidence: item.source_evidence || [],
  }),
);

const dayrehabRecords: PublicNoticeRecord[] = (dayrehab.items || []).map(
  (item: any) => ({
    id: item.id,
    service_id: "dayrehab",
    service_label: "通所リハビリテーション",
    section: item.group_heading,
    number_path: [
      dayrehab.source_section || "第九 通所リハビリテーション",
      `${item.group_number} ${item.group_heading}`,
      item.marker,
    ],
    title: item.title,
    body_text: item.body_text,
    source_state: "OFFICIAL_HISTORICAL_HTML",
    content_verification: "PASS",
    currentness_state: "GAP",
    human_review_state: "NOT_REVIEWED",
    verification_layer_id: "rouki25-dayrehab",
    source_evidence: [
      {
        source_id: "dayrehab-rouki25-historical-html",
        source_title: "厚生労働省 公式旧HTML",
        source_url: item.source_url || dayrehab.source?.url,
        role: "historical_source_text",
        note: item.source_locator,
      },
      ...(dayrehab.amendment_evidence?.source_url
        ? [
            {
              source_id: "dayrehab-rouki25-r6-comparison",
              source_title:
                dayrehab.amendment_evidence.source_label ||
                "令和6年度 居宅サービス基準解釈通知 新旧対照表",
              source_url: dayrehab.amendment_evidence.source_url,
              role: "amendment_evidence",
              note: dayrehab.amendment_evidence.policy,
            },
          ]
        : []),
    ],
  }),
);

export const publicNoticeRecords: PublicNoticeRecord[] = [
  ...dayserviceRecords,
  ...dayrehabRecords,
];

export const publicNoticeServiceOptions = [
  { service_id: "dayservice" as const, label: "通所介護" },
  { service_id: "dayrehab" as const, label: "通所リハビリテーション" },
];

export function filterPublicNotices(serviceId?: string): PublicNoticeRecord[] {
  if (!serviceId) return publicNoticeRecords;
  if (serviceId !== "dayservice" && serviceId !== "dayrehab") {
    return publicNoticeRecords;
  }
  return publicNoticeRecords.filter((record) => record.service_id === serviceId);
}

export function noticeServiceCount(serviceId: PublicNoticeServiceId): number {
  return publicNoticeRecords.filter((record) => record.service_id === serviceId).length;
}
