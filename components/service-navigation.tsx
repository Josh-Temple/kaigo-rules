"use client";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";

export default function ServiceNavigation() {
 const pathname = usePathname();
 const searchParams = useSearchParams();
 const dayrehab =
   pathname.startsWith("/services/dayrehab") ||
   searchParams.get("service") === "dayrehab";
 const base = "/services/dayrehab";
 return <nav aria-label={dayrehab ? "通所リハビリテーションのナビゲーション" : "共通ナビゲーション"}>
   <Link href="/services">サービス別</Link>
   <Link href={dayrehab ? base + "/search" : "/search"}>横断検索{dayrehab ? "（通所リハ）" : "（通所介護）"}</Link>
   <Link href={dayrehab ? "/rules?service=dayrehab" : "/rules"}>基準DB</Link>
   <Link href={dayrehab ? "/notices?service=dayrehab" : "/notices"}>通知DB</Link>
   <Link href={dayrehab ? base + "/remuneration" : "/fees"}>報酬DB</Link>
   <Link href={dayrehab ? base + "/remuneration/guidance" : "/fees/guidance"}>算定上の留意事項</Link>
   <Link href="/overview">制度の見取り図（通所介護）</Link>
   <Link href="/start">これから始める（通所介護）</Link>
   <Link href="/qa">国Q&A（通所介護・共通）</Link>
   <Link href="/law">介護保険法（通所介護）</Link>
   <Link href="/sources">根拠資料（共通台帳）</Link>
 </nav>;
}
