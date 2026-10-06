"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { listServices } from "../lib/service-catalog";

const serviceLabels = new Map(
  listServices().map((service) => [service.service_id, service.label]),
);

const routeContext = (pathname: string) => {
  const routes = [
    { prefix: "/fees/guidance", db: "算定上の留意事項", sourceFamily: "算定上の留意事項" },
    { prefix: "/fees/unit-price", db: "一単位単価・地域区分", sourceFamily: "一単位単価・地域区分" },
    { prefix: "/fees", db: "報酬基準DB", sourceFamily: "報酬基準" },
    { prefix: "/rules", db: "基準省令DB", sourceFamily: "基準省令" },
    { prefix: "/notices", db: "基準解釈通知DB", sourceFamily: "基準解釈通知" },
    { prefix: "/qa", db: "国Q&A DB", sourceFamily: "国Q&A" },
    { prefix: "/law", db: "介護保険法DB", sourceFamily: "介護保険法" },
    { prefix: "/databases/search", db: "介護制度DB横断検索", sourceFamily: "" },
    { prefix: "/databases", db: "介護制度DB", sourceFamily: "" },
    { prefix: "/guide", db: "実務ガイド", sourceFamily: "" },
    { prefix: "/start", db: "実務ガイド", sourceFamily: "" },
  ];
  return routes.find((item) => pathname.startsWith(item.prefix));
};

const serviceFromPath = (pathname: string) => {
  const match = pathname.match(/^\/services\/([^/]+)/);
  if (!match) return "";
  const serviceId = decodeURIComponent(match[1]);
  return serviceLabels.get(serviceId) || "";
};

export default function SiteFeedbackLink({
  label = "内容の誤り・更新漏れを報告",
}: {
  label?: string;
}) {
  const pathname = usePathname();
  const [href, setHref] = useState(
    "/feedback?from=" + encodeURIComponent(pathname),
  );

  useEffect(() => {
    const current = new URLSearchParams(window.location.search);
    const target = new URLSearchParams();
    target.set("from", pathname);

    const query = (current.get("q") || "").trim().slice(0, 200);
    const serviceId = (current.get("service") || "").trim().slice(0, 100);
    const serviceLabel =
      serviceLabels.get(serviceId) || serviceFromPath(pathname);
    const context = routeContext(pathname);

    if (serviceLabel) target.set("service", serviceLabel);
    if (query) target.set("q", query);
    if (context?.db) target.set("db", context.db);
    if (context?.sourceFamily) {
      target.set("source_family", context.sourceFamily);
    }

    setHref("/feedback?" + target.toString());
  }, [pathname]);

  if (pathname === "/feedback") return null;

  return <Link href={href}>{label}</Link>;
}
