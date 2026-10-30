import Link from "next/link";
import { notFound } from "next/navigation";
import { HandbookChapterContent } from "../../../../components/service-handbook";
import { handbookChapterHref, serviceHandbook, serviceHandbooks } from "../../../../lib/working-handbook";
import { pageMetadata } from "../../../../lib/site-metadata";
import HandbookNavigation from "../../../../components/handbook-navigation";

export const dynamicParams = false;
export function generateStaticParams() {
  return serviceHandbooks.flatMap(service => service.chapters.map(chapter => ({ serviceId: service.service_id, chapter: chapter.section_id.replaceAll("_", "-") })));
}
async function chapterData(params: Promise<{ serviceId: string; chapter: string }>) {
  const input = await params;
  const service = serviceHandbook(input.serviceId);
  const chapter = service?.chapters.find(chapter => chapter.section_id.replaceAll("_", "-") === input.chapter);
  if (!service || !chapter) notFound();
  return { service, chapter };
}
export async function generateMetadata({ params }: { params: Promise<{ serviceId: string; chapter: string }> }) {
  const { service, chapter } = await chapterData(params);
  return pageMetadata(`${chapter.title}｜${service.label}の手引`, chapter.summary, handbookChapterHref(service.service_id, chapter.section_id), false);
}
export default async function ChapterPage({ params }: { params: Promise<{ serviceId: string; chapter: string }> }) {
  const { service, chapter } = await chapterData(params);
  const previous = service.chapters[chapter.number - 2];
  const next = service.chapters[chapter.number];
  return <article className="answer-page wide-page handbook-page">
    <nav className="handbook-breadcrumb" aria-label="現在位置"><Link href="/services">サービス別手引</Link><span aria-hidden="true"> / </span><Link href={`/services/${service.service_id}`}>{service.label}</Link><span aria-hidden="true"> / </span><span aria-current="page">{chapter.title}</span></nav>
    <h1>{chapter.title}</h1>
    <p className="handbook-working-note">未確認の説明を含みます。条件・例外と確認状況を読み、判断前に原典を確認してください。</p>
    <HandbookNavigation service={service} current={chapter.section_id} />
    <HandbookChapterContent service={service} chapter={chapter} full />
    <nav className={service.service_id === "dayservice" ? "handbook-inline-links handbook-chapter-sequence" : "handbook-inline-links"} aria-label="前後の章">
      {previous ? <Link href={handbookChapterHref(service.service_id, previous.section_id)}>← {previous.title}</Link> : null}
      <Link href={`/services/${service.service_id}`}>目次へ</Link>
      {next ? <Link href={handbookChapterHref(service.service_id, next.section_id)}>{next.title} →</Link> : null}
    </nav>
  </article>;
}
