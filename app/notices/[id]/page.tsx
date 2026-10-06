import Link from "next/link";
import { notFound } from "next/navigation";
import notices from "../../../data/notice-nodes.json";
import sources from "../../../data/sources.json";
import VerificationSummary from "../../../components/verification-summary";
import { resolveNoticeSourceLinks } from "../../../lib/question-authority-expansion";
export default async function NoticeDetail({params}: {params: Promise<{id: string}>}) {
  const {id} = await params; const item = notices.find(row => row.id === id);
  if (!item) notFound();
  const links = resolveNoticeSourceLinks(item, sources);
  return <article className="answer-page">
    <p className="eyebrow">通所介護に適用する解釈通知</p><h1>{item.path.join(" ＞ ")}</h1>
    <p>{item.document}</p>
    <div className="notice">出典別の部分資料です。現行統合本文ではありません。現行性は確認中で、人手確認は未実施です。</div>
    <p>{item.editorial_summary}</p><p className="meta">上記は当サイトの要約です。原文は次の出典で確認してください。</p>
    {links.map(source => <section className="section" key={source.sourceId}><h2>{source.title}</h2><p className="meta">{source.locator || item.path.join(" ＞ ")}</p><p>{source.note}</p><a href={source.url} target="_blank" rel="noreferrer">公式一次資料の該当箇所を確認</a></section>)}
    <VerificationSummary layerId="rouki25-dayservice" />
    <p><Link href="/notices">解釈通知DBの再構成・現行性を見る →</Link></p>
  </article>;
}
