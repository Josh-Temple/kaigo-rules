import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { buildPublicPageMetadata } from "../../../lib/site-metadata";
import styles from "./sources.module.css";

// DRAFT / HOLD: contents are viewable only on a local test server.
// Vercel-hosted preview and production must return 404 until a new
// D/E-approved release commit deliberately replaces this guard.
export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  ...buildPublicPageMetadata({
    path: "/guides/accident-medication-sources",
    title: "事故防止・服薬安全の公的資料を探す | 介護業務改善",
    description:
      "転倒・転落、服薬安全、事故報告について公的な元資料を探す入口。個別の医療・報告判断は行いません。",
    type: "article",
  }),
  robots: { index: false, follow: false },
};

type OfficialSource = {
  id: string;
  title: string;
  issuer: string;
  kind: string;
  date: string;
  audience: string;
  purpose: string;
  limitation: string;
  pages: string;
  url: string;
};

// Existing A source-claim ledger §8/§9 and B draft #466 §9 support only
// these four references. The new high-elderly-medication/polypharmacy
// materials proposed for this Wave remain excluded until A adoption
// AND B's finalized, version-pinned guide wording are obtained.
// Date of this editorial source-set snapshot: 2026-10-12.
// This does NOT claim a fresh full-text recheck of external sources.
const sources: readonly OfficialSource[] = [
  {
    id: "g25",
    title: "介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン",
    issuer: "厚生労働省",
    kind: "ガイドライン",
    date: "2025年11月",
    audience: "主として介護保険施設を対象とする資料",
    purpose: "転倒・転落の多様な要因、ベッド周辺の環境、誤薬等の事故予防や事故発生時の対応を確認するための資料。",
    limitation: "施設向けの推奨・事例を、すべての介護サービスに共通する義務や事故防止効果の保証として扱えません。",
    pages: "転倒・転落：冊子30・32頁（PDF通し33・35頁）。誤薬等：冊子38〜39頁（PDF通し41〜42頁）。",
    url: "https://www.mhlw.go.jp/content/001591418.pdf",
  },
  {
    id: "r17",
    title: "高齢者向け住まいにおける事故予防及び虐待予防の対応方策に関する調査研究事業 報告書",
    issuer: "厚生労働省掲載",
    kind: "調査研究報告書",
    date: "2017年3月",
    audience: "高齢者向け住まいに関する研究",
    purpose: "高齢者向け住まいにおける服薬事故に関する研究上の推奨を確認するための資料。",
    limitation: "研究上の推奨は、全介護サービスに共通する法的受診義務を示すものではありません。",
    pages: "Ⅰ編45頁（PDF通し57頁）。",
    url: "https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf",
  },
  {
    id: "pmda",
    title: "くすり相談窓口",
    issuer: "独立行政法人 医薬品医療機器総合機構（PMDA）",
    kind: "一般向け相談案内（Webページ）",
    date: "発行・改訂日：未確認（更新型Webページ）",
    audience: "一般向けの薬に関する相談・情報案内",
    purpose: "薬の一般的な相談先を確認するための案内。",
    limitation: "医師の診断、再投与・服薬中止の判断、事故時の救急対応や緊急連絡の代わりにはなりません。",
    pages: "Webページのため該当頁番号なし。",
    url: "https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html",
  },
  {
    id: "n24",
    title: "介護保険施設等における事故の報告様式等について（介護保険最新情報 Vol.1332）",
    issuer: "厚生労働省",
    kind: "2024年の通知",
    date: "2024年11月29日",
    audience: "介護保険施設等。報告対象と別紙報告様式の主な対象サービスは区別が必要",
    purpose: "国通知における事故報告対象、第1報の提出の目安、別紙様式の対象をそれぞれ確認するための資料。",
    limitation: "第1報の5日以内は国通知の目安です。すべての自治体・サービスの法定期限や個別事故の報告要否は、このページでは判断できません。",
    pages: "旧通知廃止：本文1頁／PDF通し2頁。報告対象・第1報の目安：本文2頁／PDF通し3頁。別紙様式：本文3頁／PDF通し4頁。",
    url: "https://www.mhlw.go.jp/content/001574219.pdf",
  },
];

const topics = [
  { id: "fall", title: "転倒・転落", detail: "主として施設向けの事故予防資料の入口", sources: ["g25"] },
  { id: "medication", title: "服薬・医薬品適正使用", detail: "服薬事故の資料と、薬についての一般相談の入口。処方の見直しを介護職が独断で行う手順ではありません。", sources: ["g25", "r17", "pmda"] },
  { id: "reporting", title: "事故報告", detail: "国通知と自治体ごとの運用を区別して調べる入口", sources: ["n24"] },
] as const;

export default function OfficialAccidentMedicationSourcesPage() {
  if (process.env.KAIGO_OPS_SOURCE_GUIDE_REVIEW !== "local" || process.env.VERCEL) {
    notFound();
  }

  return (
    <main className={styles.page}>
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="このページのナビゲーション">
          <a href="#topics">探したい資料</a>
          <a href="#originals">公的資料一覧</a>
        </nav>
      </header>

      <article>
        <section className={styles.intro} aria-labelledby="source-guide-title">
          <p className="eyebrow">公的資料を探す</p>
          <h1 id="source-guide-title">事故防止・服薬安全の公的資料を探す</h1>
          <p className={styles.lead}>転倒・転落、服薬、事故報告について、発行者や資料の対象を確かめながら原典に進める案内です。既存記事を複製するものではありません。</p>
        </section>

        <section className={styles.warning} aria-labelledby="source-safety">
          <h2 id="source-safety">事故が現に起きている場合</h2>
          <p><strong>このページの閲覧よりも、本人の安全確保と所属先の正式な事故対応手順、必要な医療職・緊急対応を優先してください。</strong></p>
          <p>このページは医療行為、薬の選択・中止・再投与、救急受診・搬送、個別の事故報告要否・期限、法的責任を判断しません。原典の対象と所属先・自治体の現行手順を確認してください。</p>
        </section>

        <section id="topics" className={styles.section} aria-labelledby="topics-title">
          <h2 id="topics-title">何を調べたいですか</h2>
          <div className={styles.topicIndex}>
            {topics.map((topic, i) => (
              <a key={topic.id} href={"#" + topic.id} className={styles.topicEntry}>
                <span className={styles.serial}>{"0" + (i + 1)}</span>
                <span><strong>{topic.title}</strong><small>{topic.detail}</small></span>
                <span aria-hidden="true">↓</span>
              </a>
            ))}
            <a href="#originals" className={styles.topicEntry}>
              <span className={styles.serial}>04</span>
              <span><strong>公的ガイドライン・資料一覧</strong><small>文書の種類・対象・発行年をまとめて確認</small></span>
              <span aria-hidden="true">↓</span>
            </a>
          </div>
        </section>

        <section className={styles.section} aria-labelledby="topic-details">
          <h2 id="topic-details">分野から元資料へ</h2>
          {topics.map((topic) => (
            <section id={topic.id} key={topic.id} className={styles.topicDetail} aria-labelledby={topic.id + "-title"}>
              <h3 id={topic.id + "-title"}>{topic.title}</h3>
              <p>{topic.detail}</p>
              <ul>
                {topic.sources.map((sourceId) => {
                  const source = sources.find((item) => item.id === sourceId);
                  if (!source) return null;
                  return <li key={sourceId}><a href={"#source-" + source.id}>{source.issuer}：{source.title}（出典の位置付けを見る）</a></li>;
                })}
              </ul>
            </section>
          ))}
        </section>

        <section id="originals" className={styles.section} aria-labelledby="originals-title">
          <h2 id="originals-title">公的資料一覧と原典</h2>
          <p>掲載の順番は法的な優先順位ではありません。国の通知、ガイドライン、研究報告書、一般相談の案内は役割が異なります。各資料の利用に当たっては原文を確認してください。</p>
          <div className={styles.sources}>
            {sources.map((source) => (
              <section key={source.id} id={"source-" + source.id} className={styles.source} aria-labelledby={source.id + "-title"}>
                <p className="eyebrow">{source.kind}</p>
                <h3 id={source.id + "-title"}>{source.title}</h3>
                <dl className={styles.details}>
                  <div><dt>発行・掲載者</dt><dd>{source.issuer}</dd></div>
                  <div><dt>発行・改訂</dt><dd>{source.date}</dd></div>
                  <div><dt>資料の対象</dt><dd>{source.audience}</dd></div>
                  <div><dt>確認できること</dt><dd>{source.purpose}</dd></div>
                  <div><dt>この資料だけでは判断できないこと</dt><dd>{source.limitation}</dd></div>
                  <div><dt>原典の該当箇所</dt><dd>{source.pages} PDF内の頁指定が開けない場合は、この番号で探してください。</dd></div>
                </dl>
                <a className={styles.originalLink} href={source.url} target="_blank" rel="noopener noreferrer">
                  原典を開く（外部サイト） <span aria-hidden="true">↗</span>
                </a>
                <p className={styles.fullUrl}>原典URL：{source.url}</p>
              </section>
            ))}
          </div>
        </section>

        <section className={styles.boundary} aria-labelledby="limitations-title">
          <h2 id="limitations-title">掲載範囲について</h2>
          <p>各資料は発行機関が公開した原典です。このページが厚生労働省・PMDAの監修を受けたことを意味しません。施設向けの推奨をすべての介護サービスの義務に読み替えたり、国通知だけで自治体ごとの報告要否を決めたりしないでください。</p>
          <p>新たな医薬品適正使用の指針・普及啓発資料は、原典の版・対象と掲載文の採否が確定するまで、この候補には含めていません。利用者・職員の個人情報や処方・事故記録を入力する機能はありません。</p>
          <p className={styles.snapshot}>出典の説明は既存A出典台帳・B編集稿の採用済み範囲を基礎とする下書きです。公開用の人手受入と、各原典の実ブラウザ閲覧確認は未実施です。</p>
        </section>
      </article>

      <footer><span>介護業務改善 — 公的資料案内（公開前審査中）</span><a href="/">トップに戻る</a></footer>
    </main>
  );
}
