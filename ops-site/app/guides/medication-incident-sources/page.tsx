import type { Metadata } from "next";
import { buildPublicPageMetadata } from "../../../lib/site-metadata";

export const metadata: Metadata = buildPublicPageMetadata({
  path: "/guides/medication-incident-sources",
  title: "服薬事故が起きたときの注意と公的資料 | 介護業務改善",
  description:
    "誤薬・与薬漏れの初動、医療職への連絡、市町村への事故報告、法的責任を、公的資料の適用範囲とともに整理します。個別判断は行いません。",
  type: "article",
});

const sourceLinks = [
  {
    id: "mhlw2025",
    name: "厚生労働省「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」",
    detail: "2025年11月／冊子25〜27・38〜39頁。事故発生時の初動、報告経路、誤薬・与薬漏れの事故予防。施設中心のガイドライン。",
    href: "https://www.mhlw.go.jp/content/001591418.pdf",
  },
  {
    id: "mhlw2017",
    name: "厚生労働省掲載「高齢者向け住まいにおける事故予防及び虐待予防の対応方策に関する調査研究事業 報告書」",
    detail: "2017年3月／Ⅰ編45頁（PDFの57ページ目）。高齢者向け住まいにおける、本人が飲むべきでない薬を飲ませた場合の受診に関する推奨。研究事業報告書であり、全介護サービス共通の法令ではありません。",
    href: "https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf",
  },
  {
    id: "mhlw2024",
    name: "厚生労働省「介護保険施設等における事故の報告様式等について」介護保険最新情報 Vol.1332",
    detail: "2024年11月29日／通知本文2〜3頁。市町村への報告対象、報告期限の目安、サービス範囲。その他の事故は自治体の取扱いによります。",
    href: "https://www.mhlw.go.jp/content/001574219.pdf",
  },
  {
    id: "pmda",
    name: "PMDA「くすり相談窓口」",
    detail: "薬の飲み合わせ、使い方に関する相談の案内。診断・治療の判断は行わない窓口であり、個別の心配事は医師・薬剤師への相談を案内しています。",
    href: "https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html",
  },
  {
    id: "penalcode",
    name: "e-Gov法令検索「刑法」第211条（業務上過失致死傷等）",
    detail: "業務上必要な注意義務違反による死傷を対象とする条文。誤薬の発生だけで刑事責任が確定するとは定めていません。",
    href: "https://laws.e-gov.go.jp/law/140AC0000000045",
  },
] as const;

function Citation({ id, label }: { id: (typeof sourceLinks)[number]["id"]; label: string }) {
  return <a href={`#source-${id}`} aria-label={`${label}の出典へ`}>{label}</a>;
}

export default function MedicationIncidentSourcesPage() {
  return (
    <main className="sourceGuidePage">
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="/">トップ</a>
          <a href="#sources">出典一覧</a>
          <a href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">介護ルール ↗</a>
        </nav>
      </header>

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">公的資料から確認する注意点</p>
          <h1>服薬事故が起きたとき、<br />自己判断で済ませないために。</h1>
          <p className="lead">
            誤薬・与薬漏れの危険、初動時の連絡、事故報告の範囲を、公的資料に沿って整理します。
            このページは個別事故の判定や医療上の指示をするものではありません。
          </p>
          <div className="issueMeta">
            <span>資料確認：2026-10-09</span>
            <span>対象：介護施設等で働く人への情報提供</span>
            <span>個別医療判断・事故報告判定なし</span>
          </div>
        </section>

        <nav className="sourceGuideContents" aria-label="この記事の目次">
          <strong>このページの内容</strong>
          <a href="#first-step">事故の疑いがあるとき</a>
          <a href="#minor">自己判断を避ける</a>
          <a href="#report">事故報告の範囲</a>
          <a href="#prevent">再発防止</a>
          <a href="#law">法的責任の限界</a>
          <a href="#sources">出典を確認する</a>
        </nav>

        <section className="section issueSummary" aria-labelledby="first-step">
          <p className="eyebrow">最初に確認すること</p>
          <h2 id="first-step">事故の疑いがあるときは、目の前の安全確保と正式な連絡経路を優先する。</h2>
          <p>
            利用者の救命・安全確保を最優先にし、現場リーダーや上司に速やかに伝えます。
            本人の状態の把握には看護職員等と連携し、医療機関への連絡・受診や緊急時の対応は、
            所属する施設・事業所の手順と医療専門職の判断に従います。
            緊急を要する状況では、救急要請を含めて適切な対応をとってください。
            厚生労働省は、これらの連絡方法を平時から手順書・フロー図に定めることを推奨しています（<Citation id="mhlw2025" label="出典1・25〜26頁" />）。
          </p>
          <p>
            <strong>このページを読み進めるために、現に発生している事故への対応を遅らせないでください。</strong>
            このサイトは薬の影響、再投与の要否、服薬継続の可否、救急搬送の要否を判定しません。
          </p>
        </section>

        <section className="section" aria-labelledby="minor">
          <p className="eyebrow">軽微に見えても</p>
          <h2 id="minor">別の人の薬を飲ませたとき、職員だけで「様子見でよい」と決めない。</h2>
          <p>
            厚生労働省が掲載する2017年の高齢者向け住まいの調査研究報告書では、
            本人が飲むべきではない薬を飲ませたケースについて、影響が少ない薬と思われても
            自己判断で経過観察にせず、受診につなげることを推奨しています（<Citation id="mhlw2017" label="出典2・Ⅰ編45頁" />）。
          </p>
          <p>
            これは<strong>高齢者向け住まいを対象とした研究報告書内の推奨</strong>です。
            全種類の誤薬について「法律上、必ずかかりつけ医へ電話する義務がある」と定めたものではありません。
            連絡先や受診の手順は、実際の施設・事業所の正式手順と医療専門職の指示を確認してください。
          </p>
          <p>
            服用した薬の影響や飲み合わせを、薬の名前や見た目だけで職員が判断することは避けてください。
            PMDAは薬の飲み合わせ等の相談を受け付け、本人の薬について心配がある場合には、
            医師や薬剤師への相談を案内しています（<Citation id="pmda" label="出典4" />）。
          </p>
        </section>

        <section className="section muted" aria-labelledby="report">
          <p className="eyebrow">事故報告</p>
          <h2 id="report">医療職への相談と、市町村への事故報告は別に確認する。</h2>
          <p>
            厚生労働省の2024年通知では、死亡に至った事故と、
            医師の診断を受け投薬・処置等の治療が必要となった事故について、
            原則としてすべて市町村へ報告するよう示しています。
            それ以外の事故は自治体の取扱いによります（<Citation id="mhlw2024" label="出典3・2頁" />）。
          </p>
          <p>
            同通知の第1報は事故発生後速やかに、遅くとも5日以内を目安としています。
            これは国通知の<strong>報告の目安</strong>であり、すべての事案に一律に適用できる法定期限とは限りません。
            サービス種類と自治体の現行ルール、事業所内の報告手順を確認してください。
          </p>
          <p>
            医師への相談や受診をしたことと、市町村への報告義務の有無は同じ判断ではありません。
            このページは個別の報告要否や期限を判定しません。
          </p>
        </section>

        <section className="section" aria-labelledby="prevent">
          <p className="eyebrow">再発防止</p>
          <h2 id="prevent">個人の不注意だけに原因を求めず、手順と業務環境を見直す。</h2>
          <p>
            厚生労働省の2025年ガイドラインは、配薬準備と配薬時を分けた確認、
            中断が起きにくい業務環境、職員間の連携、手順書の整備などを例示しています
            （<Citation id="mhlw2025" label="出典1・38〜39頁" />）。
            これらは施設等の事故防止に関する推奨・事例であり、
            全サービス・全職種に同一の配薬工程や「必ず二人で確認する」義務を課す根拠ではありません。
          </p>
          <p>
            原因分析と再発防止は、発見した職員だけで完結させず、管理者・関係する職種を交えて行う考え方が示されています
            （<Citation id="mhlw2025" label="出典1・27頁" />）。
          </p>
        </section>

        <section className="section" aria-labelledby="law">
          <p className="eyebrow">法的責任との関係</p>
          <h2 id="law">重大な結果と注意義務違反があれば、刑事責任が問題になる場合もある。</h2>
          <p>
            刑法第211条は、業務上必要な注意を怠り、その結果、人を死傷させた場合などを対象としています
            （<Citation id="penalcode" label="出典5" />）。
            <strong>服薬の間違いが起きただけで、直ちに刑事罰が科されるという意味ではありません。</strong>
            個々の事案の責任は、注意義務、結果、因果関係などの事実を踏まえて判断されます。
            事故後の連絡や医療上の対応を、刑事罰の有無を職員が予測して決めるべきではありません。
          </p>
        </section>

        <section className="section boundary" aria-labelledby="scope">
          <p className="eyebrow">掲載範囲と注意</p>
          <h2 id="scope">根拠の種類と適用範囲を確認して利用してください。</h2>
          <p>
            本ページは公的資料と法令への入口であり、個別の医療判断、服薬指示、専門職の権限判断、
            個別事故の報告要否・期限の確定、施設の正式手順の代行はしません。
            特に高齢者向け住まいの事例・施設向けガイドラインを、
            通所・訪問・居宅介護支援などにそのまま当てはめることはできません。
          </p>
          <p>
            施設・事業所で使用する手順は、管理者、担当する医療職、適用される制度・自治体の運用を確認して整備してください。
            ここに書いた要約は、実在の医療専門職による個別審査を受けたものではありません。
            事故の詳細、薬剤名、利用者や職員の個人情報をこのサイトへ入力する機能はありません。
          </p>
        </section>

        <section className="section" id="sources" aria-labelledby="sources-head">
          <div className="sectionHead">
            <p className="eyebrow">出典と元資料</p>
            <h2 id="sources-head">原文を読む</h2>
            <p>
              本ページは各資料の内容を要約しており、資料全文の転載ではありません。
              発行年と対象、該当ページ、法令・通知・ガイドライン・研究報告書の違いを併記しています。
            </p>
          </div>
          <div className="sourceList">
            {sourceLinks.map((source, index) => (
              <a
                id={`source-${source.id}`}
                key={source.id}
                className="sourceRow"
                href={source.href}
                target="_blank"
                rel="noreferrer"
              >
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div><strong>{source.name}</strong><p>{source.detail}</p></div>
                <span aria-hidden="true">↗</span>
              </a>
            ))}
          </div>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — 出典の適用範囲を確認するための資料</span>
        <a href="/">トップに戻る</a>
      </footer>
    </main>
  );
}
