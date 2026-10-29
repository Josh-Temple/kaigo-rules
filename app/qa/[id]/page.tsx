import Link from "next/link";
import { notFound } from "next/navigation";
import corpus from "../../../data/qa-corpus.json";
import direct from "../../../data/qa-direct-evidence.json";
import meta from "../../../data/qa-corpus-meta.json";
import VerificationSummary from "../../../components/verification-summary";
import { qaDetailHref } from "../../../lib/evidence-navigation";
import { serviceHandbooks } from "../../../lib/working-handbook";
import { safeHandbookEvidenceUrl } from "../../../lib/handbook/reader-content";
export default async function QaDetail({params}: {params: Promise<{id: string}>}) {
  const {id} = await params;
  const evidence = (direct as Record<string, any>)[id];
  const item = corpus.find(row => row.id === (evidence?.corpus_id || id));
  if (!item) notFound();
  const relatedServices = serviceHandbooks.filter(service => service.qa_direct_codes.includes(item.service_code));
  const officialUrl = safeHandbookEvidenceUrl(evidence?.url) || safeHandbookEvidenceUrl(meta.source_workbook);
  return <article className="answer-page">
    <p className="eyebrow">{item.scope} / 国Q&A</p>
    {item.current_service_scope ? <p className="meta">2019年以降のサービス分類：{item.current_service_scope}</p> : null}
    <h1>{evidence?.number || item.number || "問番号未収載"} {item.topic}</h1>
    <p>{item.issued_source}</p>
    <p className="scope-note">{evidence?.source_locator || "公式Q&A集 / " + item.scope + " / " + item.topic}</p>
    {evidence?.revised_by ? <div className="notice">旧資料・修正あり。この問50だけを現在の回答として使わないでください。<p><Link href={qaDetailHref(evidence.revised_by)}>令和6年問59の修正後資料へ →</Link></p></div> : <div className="notice">出典別のQ&A本文です。現在も有効かどうかは未確定で、担当者による確認も未実施です。</div>}
    <nav className="handbook-topic-navigation" aria-label="関連する手引">
      {relatedServices.map(service => <Link key={service.service_id} href={`/services/${service.service_id}#national_qa`}>{service.label}の手引に戻る</Link>)}
      {!relatedServices.length ? <Link href="/services">サービス別の手引を選ぶ</Link> : null}
    </nav>
    <section className="section"><h2>質問</h2><p>{item.question}</p><h2>回答（公式Q&A集収載本文）</h2><p style={{whiteSpace: "pre-line"}}>{item.answer}</p></section>
    {officialUrl ? <p><a href={officialUrl} target="_blank" rel="noopener noreferrer">公式一次資料の該当箇所を確認</a></p> : <p>公式資料のURLは確認中です。</p>}
    <p className="meta">{evidence?.source_locator || "公式Excel内の上記サービス・論点・発出資料で確認してください。問番号欠落は推測補完していません。"}</p>
    {evidence?.checked_at ? <p className="meta">出典・参照先の確認日：{evidence.checked_at}（現行性・人手確認日ではありません）</p> : null}
    <VerificationSummary layerId="qa-corpus" />
    <p><Link href="/qa">国Q&A一覧へ</Link></p>
  </article>;
}
