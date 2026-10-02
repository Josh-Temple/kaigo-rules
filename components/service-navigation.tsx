import Link from "next/link";

const links = [
  { href: "/services", label: "サービス別" },
  { href: "/rules", label: "基準DB" },
  { href: "/notices", label: "通知DB" },
  { href: "/overview", label: "制度の見取り図" },
  { href: "/sources", label: "根拠資料" },
];

export default function ServiceNavigation() {
  return (
    <nav aria-label="サイト共通ナビゲーション">
      {links.map((link) => (
        <Link href={link.href} key={link.href}>{link.label}</Link>
      ))}
    </nav>
  );
}
