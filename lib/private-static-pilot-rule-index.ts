// Only used while generating the unpublished static pilot. The normal
// application continues to evaluate the existing publication policy directly.
// Cache the *results* of the original publication policy for each immutable
// service/source corpus, never replace that policy with an independent rule.
import {
  filterProgressivePublishedRules,
  getProgressiveSourceRecords,
  listProgressivePublicationServices,
} from "./publication-policy.ts";

type Service = ReturnType<typeof listProgressivePublicationServices>[number];
type RuleRecord = ReturnType<typeof getProgressiveSourceRecords>[number];
type ServiceIndex = { records: RuleRecord[]; permittedIds: Set<string> };

const byService = new Map<string, ServiceIndex>();
let byRecord: Map<string, Service[]> | undefined;

function sourceIndex(serviceId: string): ServiceIndex {
  const cached = byService.get(serviceId);
  if (cached) return cached;
  const records = getProgressiveSourceRecords(serviceId);
  const seen = new Set<string>();
  for (const record of records) {
    if (seen.has(record.id)) {
      throw new Error("Duplicate publication record ID; cannot safely build pilot index");
    }
    seen.add(record.id);
  }
  const permitted = filterProgressivePublishedRules(
    serviceId, records, (record) => record.id,
  );
  const result = {
    records,
    permittedIds: new Set(permitted.map((record) => record.id)),
  };
  byService.set(serviceId, result);
  return result;
}

export function privateStaticPilotSourceRecords(serviceId: string): RuleRecord[] {
  return sourceIndex(serviceId).records;
}

export function privateStaticPilotRulePublished(serviceId: string, recordId: string): boolean {
  return sourceIndex(serviceId).permittedIds.has(recordId);
}

export function privateStaticPilotFilterPublishedRules<T>(
  serviceId: string, records: readonly T[], recordId: (record: T) => string,
): T[] {
  const permitted = sourceIndex(serviceId).permittedIds;
  return records.filter((record) => permitted.has(recordId(record)));
}

export function privateStaticPilotServicesForRule(recordId: string): Service[] {
  if (!byRecord) {
    const built = new Map<string, Service[]>();
    for (const service of listProgressivePublicationServices()) {
      const { permittedIds } = sourceIndex(service.service_id);
      for (const id of permittedIds) {
        const services = built.get(id) || [];
        services.push(service);
        built.set(id, services);
      }
    }
    byRecord = built;
  }
  return (byRecord.get(recordId) || []).map((service) => ({ ...service }));
}
