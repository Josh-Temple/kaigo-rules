import reviewPacketData from "../data/notice-review-packet.json" with { type: "json" };
import homevisitData from "../data/services/homevisit/rouki25-historical.generated.json" with { type: "json" };
import homebathData from "../data/services/homebath/rouki25-historical.generated.json" with { type: "json" };
import dayrehabData from "../data/services/dayrehab/rouki25-historical.generated.json" with { type: "json" };
import serviceCatalogData from "../data/services/catalog.generated.json" with { type: "json" };

export type PublicNoticeServiceId = string;

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
  verification_layer_id: string;
  source_evidence: PublicNoticeEvidence[];
};

export type PublicNoticeServiceOption = {
  service_id: PublicNoticeServiceId;
  label: string;
  service_status: string;
  route_enabled: boolean;
  record_count: number;
  notice_status: string;
  notice_note?: string;
  verification_layer_id?: string;
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

type HistoricalNoticeDataset = {
  source_section?: string;
  source?: {
    url?: string;
  };
  amendment_evidence?: {
    source_url?: string;
    source_label?: string;
    policy?: string;
  };
  items?: Array<{
    id: string;
    group_number: string;
    group_heading: string;
    marker: string;
    title: string;
    body_text: string;
    source_url?: string;
    source_locator?: string;
  }>;
};

type CatalogService = {
  service_id: string;
  label: string;
  status: string;
  routing?: {
    future_service_base_enabled?: boolean;
  };
  verification_layer_ids?: string[];
  ingestion_layers?: {
    rouki25?: {
      status?: string;
      note?: string;
    };
    work_control?: {
      status?: string;
      note?: string;
    };
  };
};

const dayserviceReview = reviewPacketData as { items?: ReviewItem[] };
const homevisit = homevisitData as HistoricalNoticeDataset;
const homebath = homebathData as HistoricalNoticeDataset;
const dayrehab = dayrehabData as HistoricalNoticeDataset;
const serviceCatalog = serviceCatalogData as { services?: CatalogService[] };

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

function historicalNoticeRecords(
  data: HistoricalNoticeDataset,
  {
    serviceId,
    serviceLabel,
    verificationLayerId,
    evidencePrefix,
  }: {
    serviceId: string;
    serviceLabel: string;
    verificationLayerId: string;
    evidencePrefix: string;
  },
): PublicNoticeRecord[] {
  return (data.items || []).map((item) => ({
    id: item.id,
    service_id: serviceId,
    service_label: serviceLabel,
    section: item.group_heading,
    number_path: [
      data.source_section || "",
      `${item.group_number} ${item.group_heading}`,
      item.marker,
    ],
    title: item.title,
    body_text: item.body_text,
    source_state: "OFFICIAL_HISTORICAL_HTML",
    content_verification: "PASS",
    currentness_state: "GAP",
    human_review_state: "NOT_REVIEWED",
    verification_layer_id: verificationLayerId,
    source_evidence: [
      {
        source_id: `${evidencePrefix}-historical-html`,
        source_title: "厚生労働省 公式旧HTML",
        source_url: item.source_url || data.source?.url || "",
        role: "historical_source_text",
        note: item.source_locator,
      },
      ...(data.amendment_evidence?.source_url
        ? [
            {
              source_id: `${evidencePrefix}-r6-comparison`,
              source_title:
                data.amendment_evidence.source_label ||
                "令和6年度 居宅サービス基準解釈通知 新旧対照表",
              source_url: data.amendment_evidence.source_url,
              role: "amendment_evidence",
              note: data.amendment_evidence.policy,
            },
          ]
        : []),
    ],
  }));
}

const homevisitRecords = historicalNoticeRecords(homevisit, {
  serviceId: "homevisit",
  serviceLabel: "訪問介護",
  verificationLayerId: "rouki25-homevisit",
  evidencePrefix: "homevisit-rouki25",
});

const homebathRecords = historicalNoticeRecords(homebath, {
  serviceId: "homebath",
  serviceLabel: "訪問入浴介護",
  verificationLayerId: "rouki25-homebath",
  evidencePrefix: "homebath-rouki25",
});

const dayrehabRecords = historicalNoticeRecords(dayrehab, {
  serviceId: "dayrehab",
  serviceLabel: "通所リハビリテーション",
  verificationLayerId: "rouki25-dayrehab",
  evidencePrefix: "dayrehab-rouki25",
});

export const publicNoticeRecords: PublicNoticeRecord[] = [
  ...dayserviceRecords,
  ...homevisitRecords,
  ...homebathRecords,
  ...dayrehabRecords,
];

const noticeStateForService = (service: CatalogService, recordCount: number) => {
  const noticeLayer = service.ingestion_layers?.rouki25;
  if (noticeLayer?.status) {
    return {
      status: noticeLayer.status,
      note: noticeLayer.note,
    };
  }

  const workControl = service.ingestion_layers?.work_control;
  if (
    workControl?.status === "ACCEPTED_RESULTS_NOT_REPOSITORY_INGESTED"
  ) {
    return {
      status: "WORK_CONTROL_ACCEPTED_NOT_REPOSITORY_INGESTED",
      note: workControl.note,
    };
  }

  if (recordCount > 0) {
    return {
      status: "PUBLISHED_RECORDS_STATUS_UNSPECIFIED",
      note: undefined,
    };
  }

  return {
    status: "NOT_REPOSITORY_INGESTED",
    note: undefined,
  };
};

export const publicNoticeServiceOptions: PublicNoticeServiceOption[] = (
  serviceCatalog.services || []
).map((service) => {
  const recordCount = publicNoticeRecords.filter(
    (record) => record.service_id === service.service_id,
  ).length;
  const noticeState = noticeStateForService(service, recordCount);
  return {
    service_id: service.service_id,
    label: service.label,
    service_status: service.status,
    route_enabled:
      service.service_id === "dayservice" ||
      Boolean(service.routing?.future_service_base_enabled),
    record_count: recordCount,
    notice_status: noticeState.status,
    notice_note: noticeState.note,
    verification_layer_id: (service.verification_layer_ids || []).find(
      (layerId) => layerId.startsWith("rouki25-"),
    ),
  };
});

export const publicNoticeRegisteredServiceCount =
  publicNoticeServiceOptions.length;

export const publicNoticePublishedServiceCount =
  publicNoticeServiceOptions.filter((service) => service.record_count > 0).length;

export function findPublicNoticeService(serviceId?: string) {
  if (!serviceId) return undefined;
  return publicNoticeServiceOptions.find(
    (service) => service.service_id === serviceId,
  );
}

export function filterPublicNotices(serviceId?: string): PublicNoticeRecord[] {
  if (!serviceId) return publicNoticeRecords;
  if (!findPublicNoticeService(serviceId)) return [];
  return publicNoticeRecords.filter((record) => record.service_id === serviceId);
}

export function noticeServiceCount(serviceId: string): number {
  return publicNoticeRecords.filter((record) => record.service_id === serviceId)
    .length;
}
