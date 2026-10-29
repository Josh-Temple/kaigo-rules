import Link from "next/link";
import { handbookChapterHref, type ServiceHandbookData } from "../lib/working-handbook";

const topics = [
  ["staffing", "人員基準"], ["equipment", "設備基準"], ["operations", "運営基準"],
  ["remuneration", "報酬"], ["national_qa", "国Q&A"],
] as const;

export default function HandbookNavigation({ service, current, inline = false }: {
  service: ServiceHandbookData; current?: string; inline?: boolean;
}) {
  return <nav className="handbook-topic-navigation" aria-label={`${service.label}の主な章`}>
    {topics.filter(([id]) => service.chapters.some(chapter => chapter.section_id === id)).map(([id, label]) =>
      <Link key={id} href={inline ? `#${id}` : handbookChapterHref(service.service_id, id)}
        aria-current={current === id ? "page" : undefined}>{label}</Link>)}
  </nav>;
}
