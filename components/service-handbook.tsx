import Link from "next/link";
import { chapterRecords, handbookChapterHref, legalHref, type HandbookChapter, type ServiceHandbookData } from "../lib/working-handbook";
import LegalRecordView from "./legal-record";

export function HandbookChapterContent({ service, chapter, full = false }: {
  service: ServiceHandbookData;
  chapter: HandbookChapter;
  full?: boolean;
}) {
  const records = chapterRecords(chapter);
  const shown = full ? records : records.slice(0, 3);
  const detailHref = handbookChapterHref(service.service_id, chapter.section_id);
  return (
    <section className="section handbook-chapter" id={chapter.section_id}>
      <p className="eyebrow">第{String(chapter.number).padStart(2, "0")}章</p>
      <h2>{full ? chapter.title : <Link href={detailHref}>{chapter.title}</Link>}</h2>
      <p>{chapter.summary}</p>
      {chapter.paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      <h3>確認すること</h3>
      <ul className="handbook-checkpoints">{chapter.checkpoints.map((point, index) => <li key={index}>{point}</li>)}</ul>
      {chapter.section_id === "national_qa" ? <>
        <h3>関連する国Q&A</h3>
        <p>サービス個別・共通分類の候補を合わせて{service.qa_count.toLocaleString("ja-JP")}件収載しています。共通分類は各問の条件を確認してください。</p>
        <div className="handbook-inline-links">
          {service.qa_codes.map(code => <Link key={code} href={`/qa?service=${code}`}>{service.qa_direct_codes.includes(code) ? "サービス個別" : "共通分類"}（{code}）→</Link>)}
          <Link href="/qa">国Q&A全体を見る →</Link>
        </div>
      </> : <>
        <h3>関連する条文・資料 <small>（{records.length}件）</small></h3>
        {full ? <p className="meta">登録済みのサービス対応と見出しを使って配置した確認候補です。準用先の本文は、読替え前の原文を表示します。</p> : null}
        {shown.length ? shown.map(record => <LegalRecordView key={record.id} record={record} serviceId={service.service_id} />)
          : <p className="handbook-empty">この章への個別資料の対応付けは追記できます。収載済みの資料全体からも探せます。</p>}
      </>}
      <div className="handbook-inline-links">
        {!full ? <Link href={detailHref}>この章を詳しく読む{records.length > shown.length ? `（関連資料${records.length}件）` : ""} →</Link> : null}
        <Link href={legalHref({ service: service.service_id })}>このサービスの法令等を見る →</Link>
      </div>
    </section>
  );
}

export default function ServiceHandbook({ service }: { service: ServiceHandbookData }) {
  return (
    <article className="answer-page wide-page handbook-page">
      <p className="eyebrow"><Link href="/services">サービス別手引</Link> ／ 全15章</p>
      <h1>{service.label}の手引</h1>
      <p className="lead">開設、人員・設備、日常運営、報酬までを章ごとにまとめています。概要と確認項目から、関連する条文・通知・Q&Aへ進めます。</p>
      <p className="handbook-working-note">作成中の手引です。確認前の解説・条文対応も掲載し、内容を随時追加・調整しています。資料ごとの版と確認状況は、本文を開くと確認できます。</p>
      <div className="handbook-summary" aria-label="収載状況">
        <span><strong>15</strong>章</span>
        <span><strong>{service.source_record_count.toLocaleString("ja-JP")}</strong>条文・資料</span>
        <span><strong>{service.qa_count.toLocaleString("ja-JP")}</strong>関連Q&A候補</span>
      </div>
      <div className="handbook-inline-links handbook-top-links">
        <Link href={legalHref({ service: service.service_id })}>法令等を条文順で読む →</Link>
        <Link href="/services">別のサービスを選ぶ →</Link>
      </div>
      <nav className="handbook-toc" aria-label="手引の目次">
        {service.chapters.map(chapter => <a key={chapter.section_id} href={`#${chapter.section_id}`}>
          <span>{String(chapter.number).padStart(2, "0")}</span>{chapter.title}
        </a>)}
      </nav>
      {service.chapters.map(chapter => <HandbookChapterContent key={chapter.section_id} service={service} chapter={chapter} />)}
      <p><Link href="/services">サービス一覧へ戻る →</Link></p>
    </article>
  );
}
