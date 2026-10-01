import Link from "next/link";

export default function ServiceContextLinks({
  serviceId,
}: {
  serviceId: "dayservice" | "dayrehab";
}) {
  const dayrehab = serviceId === "dayrehab";
  const label = dayrehab ? "通所リハビリテーション" : "通所介護";
  const links = dayrehab
    ? [
        ["/services/dayrehab/search", "横断検索"],
        ["/rules?service=dayrehab", "基準DB"],
        ["/notices?service=dayrehab", "通知DB"],
        ["/services/dayrehab/remuneration", "報酬DB"],
        ["/services/dayrehab/remuneration/guidance", "算定上の留意事項"],
      ]
    : [
        ["/search", "横断検索"],
        ["/rules?service=dayservice", "基準DB"],
        ["/notices?service=dayservice", "通知DB"],
        ["/fees", "報酬DB"],
        ["/fees/guidance", "算定上の留意事項"],
      ];

  return (
    <nav className="rules-filter" aria-label={`${label}のデータベース内ナビゲーション`}>
      {links.map(([href, text]) => (
        <Link href={href} key={href}>{text}</Link>
      ))}
    </nav>
  );
}
