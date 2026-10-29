import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("出典資料一覧", "介護ルールが参照する公式資料の出典や収載範囲を確認できます。", "/sources");

import sources from "../../data/sources.json";
import Link from "next/link";
import { safeHandbookEvidenceUrl } from "../../lib/handbook/reader-content";

export default function SourcesPage() {
  return (
    <article className="answer-page">
      <p className="eyebrow">出典</p>
      <h1>根拠資料を確認する</h1>
      <p className="lead">
        当サイトが参照している公的資料の一覧です。資料名を選ぶと、発行元のページが開きます。
        掲載されていても、現在有効な全文や、個々の事業所への適用を確認できているとは限りません。
      </p>
      <p><Link href="/services">サービス別の手引に戻る →</Link></p>
      <section className="section"><h2>資料の種類を読み分ける</h2>
        <dl className="reader-source-types">
          <div><dt>国の法令・基準省令・告示</dt><dd>適用する条文、施行日、改正内容を確認します。</dd></div>
          <div><dt>国の解釈通知・Q&A</dt><dd>法令の解釈や個別の取扱いを確認します。省令とは資料の性格が異なります。</dd></div>
          <div><dt>自治体の条例・規則</dt><dd>事業所の所在地に適用する基準を確認します。地域によって法的な効力を持つ規定があります。</dd></div>
          <div><dt>自治体の運営手引</dt><dd>地域の取扱いや説明を確認する参考資料です。他の地域へそのまま適用しないでください。</dd></div>
        </dl>
      </section>
      <div className="question-list">
        {sources.map((source) => (
          <article className="question" key={source.id}>
            <span className="meta">{source.layer}</span>
            {safeHandbookEvidenceUrl(source.url) ? <a href={safeHandbookEvidenceUrl(source.url)!} target="_blank" rel="noopener noreferrer">{source.title}</a> : <span>{source.title}（原典URLは確認中）</span>}
            <span className="status">{source.publisher}</span>
          </article>
        ))}
      </div>
      <section className="section">
        <h2>確認できていない箇所の扱い</h2>
        <p>
          解釈通知は、改正資料と元の通知を照合して整理しています。本文や改正経過を確認できていない箇所は、未確認として残しています。
          各ページの出典・適用版・確認状況と、発行元の最新情報を併せて確認してください。
        </p>
      </section>
    </article>
  );
}
