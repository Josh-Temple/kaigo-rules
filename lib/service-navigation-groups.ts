import navigationData from "../data/public-service-navigation.json" with { type: "json" };
import { getService, listServices } from "./service-catalog";

type NavigationUnitData = {
  service_ids: string[];
};

type NavigationGroupData = {
  id: string;
  label: string;
  description: string;
  units: NavigationUnitData[];
};

type NavigationData = {
  format_version: number;
  purpose: string;
  groups: NavigationGroupData[];
};

const navigation = navigationData as NavigationData;

export type PublicServiceNavigationEntry = {
  service_id: string;
  label: string;
};

export type PublicServiceNavigationUnit = {
  service_ids: string[];
  services: PublicServiceNavigationEntry[];
};

export type PublicServiceNavigationGroup = {
  id: string;
  label: string;
  description: string;
  units: PublicServiceNavigationUnit[];
};

export const publicServiceNavigationPurpose = navigation.purpose;

export function publicServiceNavigationGroups(
  visibleServiceIds?: ReadonlySet<string>,
): PublicServiceNavigationGroup[] {
  return navigation.groups
    .map((group) => ({
      ...group,
      units: group.units
        .map((unit) => {
          const serviceIds = unit.service_ids.filter(
            (serviceId) => !visibleServiceIds || visibleServiceIds.has(serviceId),
          );
          return {
            service_ids: serviceIds,
            services: serviceIds.map((serviceId) => {
              const service = getService(serviceId);
              return { service_id: service.service_id, label: service.label };
            }),
          };
        })
        .filter((unit) => unit.services.length > 0),
    }))
    .filter((group) => group.units.length > 0);
}

export function validatePublicServiceNavigation() {
  const catalogIds = new Set(listServices().map((service) => service.service_id));
  const navigationIds = navigation.groups.flatMap((group) =>
    group.units.flatMap((unit) => unit.service_ids),
  );
  const uniqueNavigationIds = new Set(navigationIds);

  if (navigationIds.length !== uniqueNavigationIds.size) {
    throw new Error("public service navigation contains duplicate service ids");
  }
  if (
    catalogIds.size !== uniqueNavigationIds.size ||
    [...catalogIds].some((serviceId) => !uniqueNavigationIds.has(serviceId))
  ) {
    throw new Error("public service navigation must cover the service catalog exactly once");
  }

  const preventiveSupportUnit = navigation.groups
    .flatMap((group) => group.units)
    .find((unit) => unit.service_ids.includes("preventive-support"));
  if (
    !preventiveSupportUnit ||
    preventiveSupportUnit.service_ids.length !== 1
  ) {
    throw new Error("preventive-support must remain an independent navigation entry");
  }

  return {
    groups: navigation.groups.length,
    units: navigation.groups.reduce((count, group) => count + group.units.length, 0),
    service_entries: navigationIds.length,
  };
}
