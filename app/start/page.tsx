import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("開設・運営ガイド", "介護事業の開設・運営に関する実務の流れから、関連する制度資料へ進めます。", "/start");

import Link from "next/link";
import sources from "../../data/sources.json";
import steps from "../../data/startup-steps.json";

export default function StartPage() {
  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">開設・運営ガイド</p>
      <h1>通所介護を始めたい。<br />何から手を付ける？</h1>
      <p className="lead">
        通所介護の開設を例に、最初につまずきやすい順番を全国共通の制度から整理します。
        申請先や事前相談の運用は自治体によって異なるため、最終的には予定地の指定権者を確認してください。
      </p>
      <div className="notice">物件契約や大きな改修、人材採用を確定する前に、サービス区分・設備基準・指定権者を確認する方が手戻りを減らせます。</div>
      <div className="step-list">
        {steps.map((step) => (
          <section className="step" key={step.id}>
            <span className="step-number">{String(step.order).padStart(2, "0")}</span>
            <div>
              <h2>{step.title}</h2>
              <p>{step.summary}</p>
              {step.source_ids.map((sourceId) => {
                const source = sources.find((s) => s.id === sourceId);
                return source ? <a key={sourceId} href={source.url} target="_blank" rel="noreferrer">公式資料を確認</a> : null;
              })}
            </div>
          </section>
        ))}
      </div>
      <section className="section">
        <h2>制度本文も確認する</h2>
        <p>
          ガイドだけで判断せず、必要に応じて制度DBから法令・基準・通知・Q&Aの原文を確認できます。
        </p>
        <p><Link href="/databases/search">制度DBを横断検索する →</Link></p>
      </section>
    </article>
  );
}
