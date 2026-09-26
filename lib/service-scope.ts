import careActScopeData from "../data/care-insurance-act-scope.json" with { type: "json" };
import homevisitCareActIndexData from "../data/services/homevisit/care-insurance-act-index.generated.json" with { type: "json" };
import homevisitOrdinance37IndexData from "../data/services/homevisit/ordinance37-index.generated.json" with { type: "json" };
import ordinance37ScopeData from "../data/ordinance37-scope.json" with { type: "json" };
import serviceCatalogData from "../data/services/catalog.generated.json" with { type: "json" };

export type ServiceScopeLayer = "ordinance37" | "care_insurance_act";

export type ServiceApplicabilityBasis =
  | "DIRECT_SCOPE"
  | "INCORPORATED_SCOPE"
  | "SERVICE_SCOPE"
  | "SERVICE_DEFINITION_INDEX"
  | "SHARED_CORE_INDEX";

export type ServiceScopeMembership = {
  service_id: string;
  basis: ServiceApplicabilityBasis;
};

export type ServiceScopeResolution = {
  layer: ServiceScopeLayer;
  record_id: string;
  service_ids: string[];
  memberships: ServiceScopeMembership[];
  sharing: "EXCLUSIVE" | "SHARED" | "UNRESOLVED";
};

export type ServiceApplicabilityDecision = ServiceScopeResolution & {
  service_id: string;
  applicable: boolean;
  basis: ServiceApplicabilityBasis | null;
  reason:
    | "APPLICABLE"
    | "UNKNOWN_SERVICE"
    | "NO_COMMITTED_SCOPE_EVIDENCE"
    | "OUTSIDE_SERVICE_SCOPE";
};

type Ordinance37Scope = {
  direct_articles?: string[];
  incorporated_articles?: string[];
};

type CareActScope = {
  articles?: string[];
};

type HomevisitCareActIndex = {
  node_ids?: {
    service_definition?: string[];
    shared_core?: string[];
    all?: string[];
  };
};

type HomevisitOrdinance37Index = {
  node_ids?: string[];
};

const ordinance37Scope = ordinance37ScopeData as Ordinance37Scope;
const careActScope = careActScopeData as CareActScope;
const homevisitCareActIndex =
  homevisitCareActIndexData as HomevisitCareActIndex;
const homevisitOrdinance37Index =
  homevisitOrdinance37IndexData as HomevisitOrdinance37Index;

const ordinance37DayserviceDirect = new Set(
  (ordinance37Scope.direct_articles || []).map(String),
);
const ordinance37DayserviceIncorporated = new Set(
  (ordinance37Scope.incorporated_articles || []).map(String),
);
const ordinance37HomevisitNodeIds = new Set(
  (homevisitOrdinance37Index.node_ids || []).map(String),
);

const careActDayserviceArticles = new Set(
  (careActScope.articles || []).map(String),
);
const careActHomevisitDefinitionNodeIds = new Set(
  (homevisitCareActIndex.node_ids?.service_definition || []).map(String),
);
const careActHomevisitSharedCoreNodeIds = new Set(
  (homevisitCareActIndex.node_ids?.shared_core || []).map(String),
);

const articleNumber = (
  layer: ServiceScopeLayer,
  recordId: string,
): string | null => {
  const prefix =
    layer === "ordinance37" ? "ordinance37.article." : "careact.article.";
  if (!recordId.startsWith(prefix)) return null;
  const suffix = recordId.slice(prefix.length);
  const match = suffix.match(/^([0-9]+(?:-[0-9]+)?)(?:\.|$)/);
  return match?.[1] || null;
};

const knownServiceIds = new Set(
  (serviceCatalogData.services || []).map((service) => service.service_id),
);

const isKnownService = (serviceId: string) => knownServiceIds.has(serviceId);

const addMembership = (
  memberships: Map<string, ServiceApplicabilityBasis>,
  serviceId: string,
  basis: ServiceApplicabilityBasis,
) => {
  const existing = memberships.get(serviceId);
  if (existing && existing !== basis) {
    throw new Error(
      `Ambiguous service scope for ${serviceId}: ${existing} vs ${basis}`,
    );
  }
  memberships.set(serviceId, basis);
};

const resolveOrdinance37 = (recordId: string) => {
  const memberships = new Map<string, ServiceApplicabilityBasis>();
  const article = articleNumber("ordinance37", recordId);
  if (!article) return memberships;

  if (ordinance37DayserviceDirect.has(article)) {
    addMembership(memberships, "dayservice", "DIRECT_SCOPE");
  } else if (ordinance37DayserviceIncorporated.has(article)) {
    addMembership(memberships, "dayservice", "INCORPORATED_SCOPE");
  }

  if (ordinance37HomevisitNodeIds.has(recordId)) {
    addMembership(memberships, "homevisit", "DIRECT_SCOPE");
  }

  return memberships;
};

const resolveCareInsuranceAct = (recordId: string) => {
  const memberships = new Map<string, ServiceApplicabilityBasis>();
  const article = articleNumber("care_insurance_act", recordId);
  if (!article) return memberships;

  if (careActDayserviceArticles.has(article)) {
    addMembership(memberships, "dayservice", "SERVICE_SCOPE");
  }

  if (careActHomevisitDefinitionNodeIds.has(recordId)) {
    addMembership(
      memberships,
      "homevisit",
      "SERVICE_DEFINITION_INDEX",
    );
  } else if (careActHomevisitSharedCoreNodeIds.has(recordId)) {
    addMembership(memberships, "homevisit", "SHARED_CORE_INDEX");
  }

  return memberships;
};

export function resolveServiceScope(
  layer: ServiceScopeLayer,
  recordId: string,
): ServiceScopeResolution {
  const membershipMap =
    layer === "ordinance37"
      ? resolveOrdinance37(recordId)
      : resolveCareInsuranceAct(recordId);

  const memberships = [...membershipMap.entries()]
    .map(([service_id, basis]) => ({ service_id, basis }))
    .sort((a, b) => a.service_id.localeCompare(b.service_id));

  return {
    layer,
    record_id: recordId,
    service_ids: memberships.map((item) => item.service_id),
    memberships,
    sharing:
      memberships.length > 1
        ? "SHARED"
        : memberships.length === 1
          ? "EXCLUSIVE"
          : "UNRESOLVED",
  };
}

export function serviceApplicability(
  serviceId: string,
  layer: ServiceScopeLayer,
  recordId: string,
): ServiceApplicabilityDecision {
  const resolution = resolveServiceScope(layer, recordId);

  if (!isKnownService(serviceId)) {
    return {
      ...resolution,
      service_id: serviceId,
      applicable: false,
      basis: null,
      reason: "UNKNOWN_SERVICE",
    };
  }

  const membership = resolution.memberships.find(
    (item) => item.service_id === serviceId,
  );

  if (membership) {
    return {
      ...resolution,
      service_id: serviceId,
      applicable: true,
      basis: membership.basis,
      reason: "APPLICABLE",
    };
  }

  return {
    ...resolution,
    service_id: serviceId,
    applicable: false,
    basis: null,
    reason:
      resolution.sharing === "UNRESOLVED"
        ? "NO_COMMITTED_SCOPE_EVIDENCE"
        : "OUTSIDE_SERVICE_SCOPE",
  };
}

export function isRecordApplicableToService(
  serviceId: string,
  layer: ServiceScopeLayer,
  recordId: string,
): boolean {
  return serviceApplicability(serviceId, layer, recordId).applicable;
}

export function filterRecordsForService<T>(
  serviceId: string,
  layer: ServiceScopeLayer,
  records: readonly T[],
  recordId: (record: T) => string,
): T[] {
  return records.filter((record) =>
    isRecordApplicableToService(serviceId, layer, recordId(record)),
  );
}

export function findRecordForService<T>(
  serviceId: string,
  layer: ServiceScopeLayer,
  records: readonly T[],
  recordId: (record: T) => string,
  predicate: (record: T) => boolean,
): T | undefined {
  return records.find(
    (record) =>
      predicate(record) &&
      isRecordApplicableToService(serviceId, layer, recordId(record)),
  );
}
