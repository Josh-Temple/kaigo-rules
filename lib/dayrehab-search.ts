import ordinanceNodes from "../data/ordinance37-nodes.json";
import noticeData from "../data/services/dayrehab/rouki25-historical.generated.json";
import remunerationData from "../data/services/dayrehab/remuneration-index.json";
import guidanceData from "../data/services/dayrehab/fee-guidance-index.json";
import ordinanceIndexData from "../data/services/dayrehab/ordinance37-index.generated.json";

export type DayrehabSearchLayer =
  | "ordinance37"
  | "rouki25"
  | "remuneration"
  | "fee-guidance";

export type DayrehabSearchResult = {
  id: string;
  layer: DayrehabSearchLayer;
  layerLabel: string;
  title: string;
  meta: string;
  excerpt: string;
  href: string;
  verificationLayerId: string;
  scopeBasis?: string;
};

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

const synonymGroups = [
  ["リハマネ", "リハビリテーションマネジメント"],
  ["看護師", "看護職員", "准看護師"],
  ["pt", "理学療法士"],
  ["ot", "作業療法士"],
  ["st", "言語聴覚士"],
  ["bcp", "業務継続計画"],
  ["入浴", "入浴介助"],
  ["送迎", "送迎を行わない"],
  ["処遇改善", "介護職員等処遇改善"],
] as const;

function expand(term: string): string[] {
  const value = normalize(term);
  const group = synonymGroups.find((items) =>
    items.some((item) => normalize(item) === value),
  );
  return group ? group.map((item) => normalize(item)) : [value];
}

function matches(value: string, expandedTerms: string[][]): boolean {
  const haystack = normalize(value);
  return expandedTerms.every((alternatives) =>
    alternatives.some((term) => haystack.includes(term)),
  );
}

function excerpt(value: string, max = 150): string {
  const clean = value.replace(/\s+/g, " ").trim();
  return clean.length > max ? clean.slice(0, max) + "…" : clean;
}

const allOrdinanceNodes = ordinanceNodes as Array<any>;
const ordinanceIndex = ordinanceIndexData as any;
const directNodeIds = new Set(
  (ordinanceIndex.node_ids_by_basis?.direct || []).map(String),
);
const incorporatedNodeIds = new Set(
  (ordinanceIndex.node_ids_by_basis?.incorporated || []).map(String),
);
const scopedNodeIds = new Set([...directNodeIds, ...incorporatedNodeIds]);
const scopedOrdinanceNodes = allOrdinanceNodes.filter((node) =>
  scopedNodeIds.has(String(node.id)),
);

function ordinanceResults(expandedTerms: string[][]): DayrehabSearchResult[] {
  const articles = scopedOrdinanceNodes.filter(
    (node) => node.node_type === "article",
  );
  return articles
    .filter((article) => {
      const children = scopedOrdinanceNodes.filter(
        (node) => node.article_num === article.article_num,
      );
      const text = [
        article.article_title || "",
        article.caption || "",
        article.official_text || "",
        ...children.map((node) => node.official_text || ""),
      ].join(" ");
      return matches(text, expandedTerms);
    })
    .map((article) => {
      const basis = directNodeIds.has(String(article.id))
        ? "DIRECT_SCOPE"
        : "INCORPORATED_SCOPE";
      return {
        id: article.id,
        layer: "ordinance37" as const,
        layerLabel: "基準省令",
        title: `${article.article_title} ${article.caption || ""}`.trim(),
        meta:
          basis === "DIRECT_SCOPE"
            ? "第八章・直接規定"
            : "第119条・準用規定（relation独立監査済み）",
        excerpt: excerpt(article.official_text || ""),
        href: `/services/dayrehab/rules/${article.article_num}`,
        verificationLayerId:
          basis === "DIRECT_SCOPE"
            ? "ordinance37-dayrehab"
            : "ordinance37",
        scopeBasis: basis,
      };
    });
}

function noticeResults(expandedTerms: string[][]): DayrehabSearchResult[] {
  const data = noticeData as any;
  return data.items
    .filter((item: any) =>
      matches(
        [
          item.group_heading || "",
          item.marker || "",
          item.title || "",
          item.body_text || "",
          item.source_locator || "",
        ].join(" "),
        expandedTerms,
      ),
    )
    .map((item: any) => ({
      id: item.id,
      layer: "rouki25" as const,
      layerLabel: "基準解釈通知",
      title: `${item.marker} ${item.title}`,
      meta: `${item.group_number} ${item.group_heading} / 公式旧HTML`,
      excerpt: excerpt(item.body_text || ""),
      href: `/services/dayrehab/notices#${encodeURIComponent(item.id)}`,
      verificationLayerId: "rouki25-dayrehab",
    }));
}

function remunerationResults(expandedTerms: string[][]): DayrehabSearchResult[] {
  const data = remunerationData as any;
  return data.items
    .filter((item: any) => {
      const rates = (item.rates || [])
        .map((rate: any) => `要介護${rate.care_level} ${rate.units} ${rate.unit}`)
        .join(" ");
      return matches(
        [
          item.marker || "",
          item.title || "",
          item.group_title || "",
          item.duration || "",
          item.summary || "",
          rates,
          item.source_locator || "",
        ].join(" "),
        expandedTerms,
      );
    })
    .map((item: any) => ({
      id: item.id,
      layer: "remuneration" as const,
      layerLabel: "報酬基準",
      title: `${item.marker} ${item.title}`,
      meta: item.duration || item.kind || "",
      excerpt: excerpt(
        item.summary ||
          (item.rates || [])
            .map((rate: any) => `要介護${rate.care_level} ${rate.units}${rate.unit}`)
            .join(" / "),
      ),
      href: `/services/dayrehab/remuneration#${encodeURIComponent(item.id)}`,
      verificationLayerId: "remuneration-dayrehab",
    }));
}

function guidanceResults(expandedTerms: string[][]): DayrehabSearchResult[] {
  const data = guidanceData as any;
  return data.items
    .filter((item: any) => {
      const children = (item.children || [])
        .map(
          (child: any) =>
            `${child.marker || ""} ${child.state || ""} ${child.locator || ""}`,
        )
        .join(" ");
      return matches(
        [
          item.slot || "",
          item.title || "",
          item.r6_source_state || "",
          item.source_locator || "",
          children,
        ].join(" "),
        expandedTerms,
      );
    })
    .map((item: any) => ({
      id: item.id,
      layer: "fee-guidance" as const,
      layerLabel: "算定上の留意事項",
      title: `${item.slot} ${item.title}`,
      meta: item.r6_source_state || "",
      excerpt: excerpt(
        (item.children || []).length
          ? `確認できた子項目 ${item.children.length}件: ${item.children
              .slice(0, 6)
              .map((child: any) => child.marker)
              .join(" / ")}`
          : item.source_locator || "",
      ),
      href: `/services/dayrehab/remuneration/guidance#${encodeURIComponent(item.id)}`,
      verificationLayerId: "fee-guidance-dayrehab",
    }));
}

export function searchDayrehabPublicLayers(query: string): DayrehabSearchResult[] {
  const terms = normalize(query).split(" ").filter(Boolean);
  if (!terms.length) return [];
  const expandedTerms = terms.map(expand);
  return [
    ...ordinanceResults(expandedTerms),
    ...noticeResults(expandedTerms),
    ...remunerationResults(expandedTerms),
    ...guidanceResults(expandedTerms),
  ];
}
