import { NextResponse } from "next/server";
import {
  PROGRESSIVE_SOURCE_FAMILY,
  filterProgressivePublishedRules,
  getProgressiveSourceRecords,
  listProgressivePublicationServices,
  projectProgressiveRule,
} from "../../../../../../lib/publication-policy";
import { verifiedRelatedPrimarySourcesForRecords } from "../../../../../../lib/verified-related-sources";

type Params = Promise<{ serviceId: string }>;


export async function GET(
  request: Request,
  { params }: { params: Params },
) {
  const { serviceId } = await params;
  const service = listProgressivePublicationServices().find(
    (item) => item.service_id === serviceId,
  );

  if (!service) {
    return NextResponse.json(
      { error: "SERVICE_RULE_CONTEXT_NOT_PUBLISHED" },
      { status: 404 },
    );
  }

  const nodes = getProgressiveSourceRecords(serviceId) as Array<any>;
  if (!nodes.length) {
    return NextResponse.json(
      { error: "SOURCE_RULE_CONTEXT_NOT_PUBLISHED" },
      { status: 404 },
    );
  }

  const url = new URL(request.url);
  const article = (url.searchParams.get("article") || "").trim();
  const published = filterProgressivePublishedRules(
    serviceId,
    nodes,
    (node) => node.id,
  );
  const selected = article
    ? published.filter((node) => node.article_num === article)
    : published.filter((node) => node.node_type === "article");

  if (article && selected.length === 0) {
    return NextResponse.json(
      { error: "ARTICLE_NOT_PUBLISHED_FOR_SERVICE" },
      { status: 404 },
    );
  }

  const response = NextResponse.json({
    service: {
      id: service.service_id,
      label: service.label,
    },
    source_family: PROGRESSIVE_SOURCE_FAMILY,
    related_primary_sources:
      verifiedRelatedPrimarySourcesForRecords(
        serviceId,
        PROGRESSIVE_SOURCE_FAMILY,
        selected,
      ),
    items: selected
      .map((node) => projectProgressiveRule(serviceId, node))
      .filter(Boolean),
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
