import { NextResponse } from "next/server";
import {
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  listProgressivePublicationCells,
  projectProgressiveRecords,
} from "../../../../../../lib/publication-policy";

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
      };
    })
    .filter(Boolean);

  if (!sources.length) {
    return NextResponse.json(
      { error: "SERVICE_SOURCE_CONTEXT_NOT_PUBLISHED" },
      { status: 404 },
    );
  }

  return NextResponse.json({
    service: {
      id: serviceId,
      label: cells[0].label,
    },
    sources,
  });
}
