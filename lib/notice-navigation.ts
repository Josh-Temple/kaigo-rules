import type {
  PublicNoticeRecord,
  PublicNoticeServiceOption,
} from "./notice-database";

export type NoticeDisplayGroup = {
  id: string;
  label: string;
  companion_label?: string;
  member_ids: string[];
  services: PublicNoticeServiceOption[];
  service_class?: string;
  record_count: number;
};

export type NoticeDisplaySection = {
  serviceClass: string;
  label: string;
  groups: NoticeDisplayGroup[];
};

export const preventivePairByPrimary: Record<string, string> = {
  homebath: "preventive-homebath",
  homenursing: "preventive-homenursing",
  homerehab: "preventive-homerehab",
  homecaremanagement: "preventive-homecaremanagement",
  dayrehab: "preventive-dayrehab",
  "shortstay-life": "preventive-shortstay-life",
  "shortstay-medical": "preventive-shortstay-medical",
  "specific-facility": "preventive-specific-facility",
  "welfare-equipment-rental": "preventive-welfare-equipment-rental",
  "specific-welfare-equipment-sale": "specific-preventive-welfare-equipment-sale",
  "dementia-dayservice": "preventive-dementia-dayservice",
  "small-scale-multifunctional": "preventive-small-scale-multifunctional",
  "dementia-group-home": "preventive-dementia-group-home",
};

const pairedPreventiveIds = new Set(Object.values(preventivePairByPrimary));

export const noticeSectionOrder = [
  "HOME_SERVICE",
  "COMMUNITY_BASED_SERVICE",
  "FACILITY_SERVICE",
  "CARE_MANAGEMENT",
  "PREVENTIVE_SUPPORT",
  "OTHER",
];

export const noticeSectionLabels: Record<string, string> = {
  HOME_SERVICE: "居宅サービス",
  COMMUNITY_BASED_SERVICE: "地域密着型サービス",
  FACILITY_SERVICE: "施設サービス",
  CARE_MANAGEMENT: "居宅介護支援",
  PREVENTIVE_SUPPORT: "介護予防支援",
  OTHER: "その他",
};

export function buildNoticeDisplayGroups(
  services: PublicNoticeServiceOption[],
): NoticeDisplayGroup[] {
  const byId = new Map(services.map((service) => [service.service_id, service]));

  return services
    .filter((service) => !pairedPreventiveIds.has(service.service_id))
    .map((service) => {
      const preventiveId = preventivePairByPrimary[service.service_id];
      const preventive = preventiveId ? byId.get(preventiveId) : undefined;
      const members = preventive ? [service, preventive] : [service];

      return {
        id: service.service_id,
        label: service.label,
        companion_label: preventive?.label,
        member_ids: members.map((member) => member.service_id),
        services: members,
        service_class:
          service.service_id === "preventive-support"
            ? "PREVENTIVE_SUPPORT"
            : service.service_class || "OTHER",
        record_count: members.reduce(
          (total, member) => total + member.record_count,
          0,
        ),
      };
    });
}

export function findNoticeDisplayGroup(
  groups: NoticeDisplayGroup[],
  serviceId?: string,
) {
  if (!serviceId) return undefined;
  return groups.find((group) => group.member_ids.includes(serviceId));
}

export function buildNoticeDisplaySections(
  groups: NoticeDisplayGroup[],
): NoticeDisplaySection[] {
  return noticeSectionOrder
    .map((serviceClass) => ({
      serviceClass,
      label: noticeSectionLabels[serviceClass],
      groups: groups.filter(
        (group) => (group.service_class || "OTHER") === serviceClass,
      ),
    }))
    .filter((section) => section.groups.length > 0);
}

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

export function filterNoticeRecordsByQuery(
  records: PublicNoticeRecord[],
  query: string,
) {
  const terms = normalize(query).split(" ").filter(Boolean);
  if (!terms.length) return records;

  return records.filter((record) => {
    const haystack = normalize(
      [
        record.service_label,
        record.section,
        ...record.number_path,
        record.title,
        record.body_text,
      ].join(" "),
    );
    return terms.every((term) => haystack.includes(term));
  });
}
