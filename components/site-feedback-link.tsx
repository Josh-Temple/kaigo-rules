"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function SiteFeedbackLink({
  label = "内容の誤り・更新漏れを報告",
}: {
  label?: string;
}) {
  const pathname = usePathname();

  if (pathname === "/feedback") return null;

  return (
    <Link href={"/feedback?from=" + encodeURIComponent(pathname)}>
      {label}
    </Link>
  );
}
