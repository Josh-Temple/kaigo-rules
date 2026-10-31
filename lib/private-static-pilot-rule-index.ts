// Only used while generating the unpublished static pilot. The normal
// application continues to evaluate the existing publication policy directly.
import {
  filterProgressivePublishedRules,
  getProgressiveSourceRecords,
  listProgressivePublicationServices,
} from "./publication-policy.ts";

type Service = ReturnType<typeof listProgressivePublicationServices>[number];
let index: Map<string, Service[]> | undefined;

export function privateStaticPilotServicesForRule(recordId: string): Service[] {
  if (!index) {
    const built = new Map<string, Service[]>();
    for (const service of listProgressivePublicationServices()) {
      const records = getProgressiveSourceRecords(service.service_id);
      const seen = new Set<string>();
      for (const record of records) {
        if (seen.has(record.id)) throw new Error("Duplicate publication record ID; cannot safely build pilot index");
        seen.add(record.id);
      }
      const permitted = filterProgressivePublishedRules(service.service_id, records, (record) => record.id);
      for (const record of permitted) {
        const services = built.get(record.id) || [];
        services.push(service);
        built.set(record.id, services);
      }
    }
    index = built;
  }
  return (index.get(recordId) || []).map((service) => ({ ...service }));
}
