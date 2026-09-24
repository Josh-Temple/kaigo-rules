import catalogData from "../data/services/catalog.generated.json";

export type ServiceConfig = {
  service_id: string;
  label: string;
  status: string;
  routing: {
    current_mode?: string;
    legacy_base_path?: string;
    legacy_entry_points?: string[];
    future_service_base_path: string;
    future_service_base_enabled: boolean;
  };
  id_namespaces: Record<string, string>;
};

type ServiceCatalog = {
  format_version: number;
  generated_by: string;
  default_service_id: string;
  services: ServiceConfig[];
};

const catalog = catalogData as ServiceCatalog;
const byId = new Map(catalog.services.map((service) => [service.service_id, service]));

export const DEFAULT_SERVICE_ID = catalog.default_service_id;

export function getService(serviceId: string): ServiceConfig {
  const service = byId.get(serviceId);
  if (!service) {
    throw new Error(`Unknown service_id: ${serviceId}`);
  }
  return service;
}

export function getDefaultService(): ServiceConfig {
  return getService(DEFAULT_SERVICE_ID);
}

export function serviceBasePath(serviceId: string): string {
  const service = getService(serviceId);
  if (
    serviceId === DEFAULT_SERVICE_ID &&
    service.routing.current_mode === "LEGACY_ROOT"
  ) {
    return service.routing.legacy_base_path || "/";
  }
  if (!service.routing.future_service_base_enabled) {
    throw new Error(`Service route is not enabled: ${serviceId}`);
  }
  return service.routing.future_service_base_path;
}

export function servicePath(serviceId: string, path: string): string {
  const clean = path.startsWith("/") ? path : `/${path}`;
  const base = serviceBasePath(serviceId);
  if (base === "/") return clean;
  return `${base}${clean}`;
}

export function stripServiceNamespace(
  serviceId: string,
  namespace: string,
  value: string
): string {
  const prefix = getService(serviceId).id_namespaces[namespace];
  if (!prefix) {
    throw new Error(`Service ${serviceId} has no namespace ${namespace}`);
  }
  if (!value.startsWith(prefix)) {
    throw new Error(`ID ${value} is outside ${serviceId}/${namespace}`);
  }
  return value.slice(prefix.length);
}

export function feeHref(serviceId: string, feeId: string): string {
  return servicePath(
    serviceId,
    `/fees/${stripServiceNamespace(serviceId, "fee", feeId)}`
  );
}
