import Link from "next/link";
import {
  UNIT_PRICE_SOURCE_FAMILY,
  publicSourceFamiliesForService,
} from "../lib/public-source-navigation";

export default function ServiceContextLinks({
  serviceId,
}: {
  serviceId: "dayservice" | "dayrehab";
}) {
  const dayrehab = serviceId === "dayrehab";
  const label = dayrehab ? "通所リハビリテーション" : "通所介護";
  const publishedFamilies = publicSourceFamiliesForService(serviceId);
  const hasProgressiveSources = publishedFamilies.length > 0;
  const hasUnitPrice = publishedFamilies.some(
    (item) => item.source_family === UNIT_PRICE_SOURCE_FAMILY,
  );
  const links: Array<[string, string]> = dayrehab
    ? [
        [
          hasProgressiveSources
            ? "/databases/search?service=dayrehab"
            : "/services/dayrehab/search",
          "横断検索",
        ],
        ["/rules?service=dayrehab", "基準DB"],
        ["/notices?service=dayrehab", "通知DB"],
        ["/services/dayrehab/remuneration", "報酬DB"],
        ["/services/dayrehab/remuneration/guidance", "算定上の留意事項"],
      ]
    : [
        [
          hasProgressiveSources
            ? "/databases/search?service=dayservice"
            : "/search",
          "横断検索",
        ],
        ["/rules?service=dayservice", "基準DB"],
        ["/notices?service=dayservice", "通知DB"],
        ["/fees", "報酬DB"],
        ["/fees/guidance", "算定上の留意事項"],
      ];

  if (!dayrehab && hasUnitPrice) {
    links.push(["/fees/unit-price", "単価・地域区分"]);
  }

  return (
    <nav className="rules-filter" aria-label={`${label}のデータベース内ナビゲーション`}>
      {links.map(([href, text]) => (
        <Link href={href} key={href}>{text}</Link>
      ))}
    </nav>
  );
}
