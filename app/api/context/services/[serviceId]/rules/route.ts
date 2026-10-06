import { NextResponse } from "next/server";
import ordinanceNodesData from "../../../../../../data/ordinance37-nodes.json";
import {
  PROGRESSIVE_SOURCE_FAMILY,
  filterProgressivePublishedRules,
  listProgressivePublicationServices,
  projectProgressiveRule,
} from "../../../../../../lib/publication-policy";

type Params = Promise<{ serviceId: string }>;

const nodes = ordinanceNodesData as Array<any>;

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

  return NextResponse.json({
    service: {
      id: service.service_id,
      label: service.label,
    },
    source_family: PROGRESSIVE_SOURCE_FAMILY,
    items: selected
      .map((node) => projectProgressiveRule(serviceId, node))
      .filter(Boolean),
  });
}
