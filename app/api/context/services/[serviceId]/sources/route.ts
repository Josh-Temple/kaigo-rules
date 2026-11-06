import { NextResponse } from "next/server";
import {
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  listProgressivePublicationCells,
  projectProgressiveRecords,
} from "../../../../../../lib/publication-policy";
import { verifiedRelatedPrimarySourcesForRecords } from "../../../../../../lib/verified-related-sources";

type Params = Promise<{ serviceId: string }>;

export async function GET(
  request: Request,
  { params }: { params: Params },
) {
  const { serviceId } = await params;
  const url = new URL(request.url);
  const requestedFamily = (
    url.searchParams.get("source_family") || ""
  ).trim();

  const cells = listProgressivePublicationCells().filter(
    (cell) =>
      cell.service_id === serviceId &&
      (!requestedFamily ||
        cell.source_family === requestedFamily),
  );

  if (!cells.length) {
    return NextResponse.json(
      { error: "SERVICE_SOURCE_CONTEXT_NOT_PUBLISHED" },
      { status: 404 },
    );
  }

  const sources = cells
    .map((cell) => {
      const records = getProgressiveSourceRecords(
        serviceId,
        cell.source_family,
      );
      const trust = getProgressivePublicationTrust(
        serviceId,
        cell.source_family,
      );
      if (!trust || !records.length) return null;

      return {
        source_family: cell.source_family,
        source: {
          canonical_source_id: trust.canonical_source_id,
          title: trust.source_title,
          url: trust.source_url,
          version: trust.source_version,
          effective_date: trust.effective_date,
          checked_at: trust.checked_at,
        },
        items: projectProgressiveRecords(
          serviceId,
          cell.source_family,
          records,
        ),
        related_primary_sources:
          verifiedRelatedPrimarySourcesForRecords(
            serviceId,
            cell.source_family,
            records,
          ),
      };
    })
    .filter(Boolean);

  if (!sources.length) {
    return NextResponse.json(
      { error: "SERVICE_SOURCE_CONTEXT_NOT_PUBLISHED" },
      { status: 404 },
    );
  }

  const response = NextResponse.json({
    service: {
      id: serviceId,
      label: cells[0].label,
    },
    sources,
  });
  // This endpoint publishes immutable, non-personalized data from the build.
  // Cache successful responses at Vercel's edge to avoid repeated Function CPU.
  // Error responses above remain uncached.
  response.headers.set("Cache-Control", "public, max-age=0");
  response.headers.set(
    "Vercel-CDN-Cache-Control",
    "public, s-maxage=3600, stale-while-revalidate=86400",
  );
  return response;
}
