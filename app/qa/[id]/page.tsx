import Link from "next/link";
import { notFound } from "next/navigation";
import corpus from "../../../data/qa-corpus.json";
import direct from "../../../data/qa-direct-evidence.json";
import meta from "../../../data/qa-corpus-meta.json";
import VerificationSummary from "../../../components/verification-summary";
import { qaDetailHref } from "../../../lib/evidence-navigation";
import { serviceHandbooks } from "../../../lib/working-handbook";
import { safeHandbookEvidenceUrl } from "../../../lib/handbook/reader-content";
export default async function QaDetail({params, searchParams}: {params: Promise<{id: string}>; searchParams: Promise<{reader?: string}>}) {
  const {id} = await params;
  const reader = (await searchParams).reader === "1";
  const evidence = (direct as Record<string, any>)[id];
  const item = corpus.find(row => row.id === (evidence?.corpus_id || id));
  if (!item) notFound();
  const relatedServices = serviceHandbooks.filter(service => service.qa_direct_codes.includes(item.service_code));
  const officialUrl = safeHandbookEvidenceUrl(evidence?.url) || safeHandbookEvidenceUrl(meta.source_workbook);
  return <article className="answer-page">
    <p className="eyebrow">{reader ? "厚生労働省のQ&A" : `${item.scope} / 国Q&A`}</p>
    {!reader && item.current_service_scope ? <p className="meta">2019年以降のサービス分類：{item.current_service_scope}</p> : null}
    <h1>{evidence?.number || item.number || "問番号未収載"} {item.topic}</h1>
    <p>{item.issued_source}</p>
    {!reader ? <p className="scope-note">{evidence?.source_locator || "公式Q&A集 / " + item.scope + " / " + item.topic}</p> : null}
    {evidence?.revised_by ? <div className="notice">{reader ? "修正後のQ&Aがあります。この回答だけを現在の取扱いとして使わないでください。" : "旧資料・修正あり。この問50だけを現在の回答として使わないでください。"}<p><Link href={reader ? `${qaDetailHref(evidence.revised_by)}?reader=1` : qaDetailHref(evidence.revised_by)}>令和6年問59の修正後資料へ →</Link></p></div> : <div className="notice">{reader ? "発出当時の回答です。改正後も適用できるかは未確認です。算定・配置の判断前に最新の国の資料を確認してください。" : "出典別のQ&A本文です。現在も有効かどうかは未確定で、担当者による確認も未実施です。"}</div>}
    <nav className="handbook-topic-navigation" aria-label="関連する手引">
      {relatedServices.map(service => <Link key={service.service_id} href={`/services/${service.service_id}#national_qa`}>{service.label}の手引に戻る</Link>)}
      {!relatedServices.length ? <Link href="/services">サービス別の手引を選ぶ</Link> : null}
    </nav>
    <section className="section"><h2>質問</h2><p>{item.question}</p><h2>回答（公式Q&A集収載本文）</h2><p style={{whiteSpace: "pre-line"}}>{item.answer}</p></section>
    {officialUrl ? <p><a href={officialUrl} target="_blank" rel="noopener noreferrer">厚生労働省のQ&A原資料を確認</a></p> : <p>公式資料のURLは確認中です。</p>}
    {!reader ? <p className="meta">{evidence?.source_locator || "公式Excel内の上記サービス・論点・発出資料で確認してください。問番号欠落は推測補完していません。"}</p> : null}
    {!reader && evidence?.checked_at ? <p className="meta">出典・参照先の確認日：{evidence.checked_at}（現行性・人手確認日ではありません）</p> : null}
    {!reader ? <VerificationSummary layerId="qa-corpus" /> : null}
    <p><Link href={reader ? "/qa?reader=1" : "/qa"}>国Q&A一覧へ戻る</Link></p>
  </article>;
}
