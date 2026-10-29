import Link from "next/link";
import SiteFeedbackLink from "./site-feedback-link";

const links = [
  { href: "/services", label: "サービス別手引" },
  { href: "/qa", label: "国Q&A" },
  { href: "/legislation", label: "法令等" },
  { href: "/databases", label: "資料を探す" },
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
