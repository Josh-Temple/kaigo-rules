import Link from "next/link";
import SiteFeedbackLink from "./site-feedback-link";

const links = [
  { href: "/databases", label: "DB一覧" },
  { href: "/services", label: "サービス別" },
  { href: "/overview", label: "制度の見取り図" },
  { href: "/sources", label: "根拠資料" },
];

export default function ServiceNavigation() {
  return (
    <nav aria-label="サイト共通ナビゲーション">
      {links.map((link) => (
        <Link href={link.href} key={link.href}>{link.label}</Link>
      ))}
      <SiteFeedbackLink label="フィードバック" />
    </nav>
  );
}
