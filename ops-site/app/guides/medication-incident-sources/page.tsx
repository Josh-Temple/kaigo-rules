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
    detail: "2024年11月29日／通知本文2〜3頁（PDF通し3〜4頁）。事故報告の対象と期限の目安、別紙様式の主な対象サービス。各サービスの報告義務とは区別が必要です。",
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
    detail: "業務上必要な注意義務違反による人の死傷に関する条文。誤薬の発生だけで刑事責任が決まるものではありません。",
    href: "https://laws.e-gov.go.jp/law/140AC0000000045",
  },
] as const;

function Citation({ id, label, page }: { id: (typeof sourceLinks)[number]["id"]; label: string; page?: number }) {
  // The in-page source index remains available, but the cited paragraph also
  // links directly to the same published original without adding any new claims.
  const source = sourceLinks.find((entry) => entry.id === id);
  if (!source) return null;
  const originalUrl = page ? `${source.href}#page=${page}` : source.href;
  return (
    <span className="sourceGuideCitation">
      <a href={`#source-${id}`} aria-label={`${label}の出典へ`}>{label}</a>
      {" / "}
      <a href={originalUrl} target="_blank" rel="noreferrer"
        aria-label={`${label}の原文を新しいタブで開く`}>原文（別タブ） ↗</a>
    </span>
  );
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
          <p className="sourceGuidePriority"><strong>実際に事故が起きている場合は、このページの閲覧よりも、本人の安全確保と所属先の正式な事故対応手順、必要な医療職・緊急対応を優先してください。</strong> このページは、薬の影響、服薬・再投与、受診・搬送の要否、個別の事故報告を判断するものではありません。</p>
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
            厚生労働省は、これらの連絡方法を平時から手順書・フロー図に定めることを推奨しています（<Citation id="mhlw2025" label="厚労省ガイドライン・施設中心・冊子25〜26頁／PDF28〜29頁" page={28} />）。
          </p>
          <p>
            <strong>このページを読み進めるために、現に発生している事故への対応を遅らせないでください。</strong>
            このサイトは薬の影響、再投与の要否、服薬継続の可否、救急搬送の要否を判定しません。
          </p>
        </section>

        <section className="section" aria-labelledby="minor">
          <p className="eyebrow">軽微に見えても</p>
          <h2 id="minor">別の人の薬を飲ませたとき、職員だけで「様子見でよい」と決めない。</h2>
          {/* MED-A02: 2017年の高齢者向け住まいの研究推奨に限定。 */}
          <p>
            厚生労働省が掲載する2017年の<strong>高齢者向け住まいに関する研究報告書</strong>は、
            本人が飲むべきでない薬を飲ませた事例について、影響が少ないと思われても現場の自己判断だけで
            経過観察とせず、受診につなげることを勧めています。
            <strong>これは対象を限定した研究報告書の推奨であり、すべての誤薬や介護サービスに法律上の一律受診義務を設けるものではありません。</strong>
            施設・事業所の正式手順と医療職の判断を確認してください。
            （<Citation id="mhlw2017" label="2017年研究報告書・Ⅰ編45頁／PDF57頁・高齢者向け住まい" page={57} />）
          </p>
          {/* MED-A03: PMDAは一般相談窓口であり個別事故の診断先ではない。 */}
          <p>
            薬に関する一般的な相談先の情報として、PMDAの「くすり相談窓口」があります。
            ただし、同窓口の説明は個別事故の診断、治療、受診・搬送の要否をサイトが判断する根拠にはなりません。
            （<Citation id="pmda" label="PMDAくすり相談窓口・更新型の公的案内" />）
          </p>
        </section>

        <section className="section muted" aria-labelledby="report">
          <p className="eyebrow">事故報告</p>
          <h2 id="report">医療職への相談と、市町村への事故報告は別に確認する。</h2>
          {/* MED-A04: 2024年国通知における報告対象の記述。 */}
          <p>
            医療職への連絡や受診に関する相談と、市町村への事故報告は別の手続です。
            厚生労働省の2024年通知は、死亡に至った事故と、医師の診断を受け投薬・処置等の治療が必要となった事故を、
            原則としてすべて報告するものと示しています。その他の事故は各自治体の取扱いによります。
            （<Citation id="mhlw2024" label="2024年通知・本文2頁／PDF3頁・報告対象" page={3} />）
          </p>
          {/* MED-A05: 5日以内は通知上の目安。 */}
          <p>
            同通知では、第1報の提出を事故発生後速やかに、遅くとも5日以内を<strong>目安</strong>としています。
            一律の法定期限と読み替えず、事業所の正式手順と自治体の現行の取扱いを確認してください。
            なお、この通知は2021年の旧通知を廃止しています。
            （<Citation id="mhlw2024" label="2024年通知・本文2頁／PDF3頁・報告期限" page={3} />／
            <Citation id="mhlw2024" label="同通知・本文1頁／PDF2頁・旧通知の廃止" page={2} />）
          </p>
          {/* MED-A04/05, X-02: 様式の主対象と各サービスの法的報告義務は別。 */}
          <p>
            <strong>対象サービスには違いがあります。</strong> 同通知の別紙報告様式は、
            介護保険施設、認知症対応型共同生活介護、特定施設入居者生活介護、有料老人ホーム、
            サービス付き高齢者向け住宅、養護老人ホーム、軽費老人ホームにおける事故を中心に作られています。
            認知症対応型共同生活介護には介護予防を、特定施設入居者生活介護には地域密着型・介護予防を含みます。
            その他の居宅等の介護サービスにも可能な限り様式の活用が求められています。
            <strong>この列挙だけで、個別事故の報告要否・報告先・期限を確定することはできません。</strong>
            （<Citation id="mhlw2024" label="2024年通知・本文3頁／PDF4頁・対象サービス" page={4} />）
          </p>
        </section>

        <section className="section" aria-labelledby="prevent">
          <p className="eyebrow">再発防止</p>
          <h2 id="prevent">個人の不注意だけに原因を求めず、手順と業務環境を見直す。</h2>
          <p>
            以下は、主として<strong>介護保険施設を対象とした厚生労働省ガイドラインの推奨・事例</strong>です。
            配薬の確認、業務中断を減らす工夫、職員間の情報共有などを示していますが、
            全サービス・全職種に同じ工程や二人確認を法律上義務付けるものではありません。
            事例にある取組の事故減少効果を、別施設でも成立する数値として紹介しません。
            （<Citation id="mhlw2025" label="2025年ガイドライン・冊子38〜39頁／PDF41〜42頁・施設中心" page={41} />）
          </p>
          <p>
            原因分析と再発防止は、発見した職員だけで完結させず、管理者・関係する職種を交えて行う考え方が示されています
            （<Citation id="mhlw2025" label="2025年ガイドライン・冊子27頁／PDF30頁・施設中心" page={30} />）。
          </p>
        </section>

        <section className="section" aria-labelledby="law">
          <p className="eyebrow">法的責任との関係</p>
          <h2 id="law">服薬の間違いだけで、刑事責任が決まるわけではありません。</h2>
          {/* MED-A07: 刑法211条の限定した要旨。施行版全文の独立直読はA/Dで未確立。 */}
          <p>
            刑法第211条には、業務上必要な注意を怠り、その結果、人を死傷させた場合などについての規定があります。
            <strong>誤薬が発生しただけで、直ちにこの条文による犯罪や刑罰が確定するわけではありません。</strong>
            具体的な法的責任は事案ごとの事実と法的要件を踏まえて判断されます。
            事故時の医療職への連絡や報告を、刑事責任の有無について職員が予測して決めないでください。
            （<Citation id="penalcode" label="刑法第211条・e-Gov法令検索" />）
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
          <p>関連資料：<a href="/guides/fall-prevention-sources">転倒・転落の予防について公的資料を確認する →</a></p>
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
