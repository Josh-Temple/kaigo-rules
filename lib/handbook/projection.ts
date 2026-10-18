/**
 * Internal, restricted handbook data adapter for Worker C/E integration.
 * Do not import it from any public page, sitemap or public API.
 * Returns metadata and source locators only; never draft paragraph text.
 */
import dayserviceBridge from "../../docs/prototypes/evidence-bridges/dayservice.json";
import dayrehabBridge from "../../docs/prototypes/evidence-bridges/dayrehab.json";
import dayserviceDraft from "../../docs/prototypes/data/dayservice-handbook-drafts.v1.json";
import dayserviceOldCandidates from "../../docs/prototypes/data/dayservice-handbook-source-candidates.v2.json";
import sources from "../../data/sources.json";
import { getService, listServices } from "../service-catalog";
import { publicSourceFamiliesForService } from "../public-source-navigation";
import {
  composeHandbookProjection,
  type BridgeInventory,
  type ExistingDraft,
  type ExistingSourceCandidates,
  type HandbookProjection,
} from "./compose";

/**
 * A recognized service with no chapter inventory returns null; an unrecognized
 * service ID is rejected by the canonical service catalog.
 * The bridge layouts are provisional and must not be extended by guessing.
 */
export function handbookSourceProjectionForService(
  serviceId: string,
): HandbookProjection | null {
  getService(serviceId);
  if (serviceId !== "dayservice" && serviceId !== "dayrehab") return null;
  const isDayservice = serviceId === "dayservice";
  return composeHandbookProjection({
    serviceId,
    registeredServiceIds: listServices().map(s => s.service_id),
    bridge: (isDayservice ? dayserviceBridge : dayrehabBridge) as unknown as BridgeInventory,
    registry: sources,
    publishedServiceRoutes: publicSourceFamiliesForService(serviceId),
    oldDraft: isDayservice ? dayserviceDraft as unknown as ExistingDraft : undefined,
    oldSourceCandidates: isDayservice
      ? dayserviceOldCandidates as unknown as ExistingSourceCandidates : undefined,
  });
}
