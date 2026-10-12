import type { Metadata } from "next";
import { buildPublicPageMetadata } from "../../../lib/site-metadata";

export const metadata: Metadata = buildPublicPageMetadata({
  path: "/guides/fall-prevention-sources",
  title: "転倒・転落の予防と公的資料 | 介護業務改善",
  description: "介護保険施設向けガイドラインを中心に、転倒・転落予防の視点と事故報告通知の対象範囲を紹介します。個別判断は行いません。",
  type: "article",
});

// Static source information only. Claim IDs appear in code for audit, not in the public UI.
export default function FallPreventionSourcesPage() {
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
          <p className="eyebrow">公的資料に基づく静的な案内</p>
          <h1>転倒・転落の予防を、公的資料から考える</h1>
          <p className="lead">
            転倒・転落の事故防止に関する厚生労働省のガイドラインを、対象範囲を示しながら紹介します。
            主として<strong>介護保険施設を対象とした資料</strong>であり、訪問、通所、居宅介護支援、介護予防支援などに、
            同じ手順や職種配置を一律に当てはめるものではありません。
            個別の対策は本人の状況と事業所の体制に応じて検討する必要があります。
          </p>
          <p className="sourceGuidePriority">
            <strong>事故が現に起きている場合は、記事の閲覧を続けず、本人の安全確保、所属先の正式な事故対応手順、必要な医療職・緊急対応を優先してください。</strong>
            このページは、けがの程度、受診・搬送の要否、身体拘束の法的該当性、市町村への事故報告の要否を判定しません。
          </p>
          <div className="issueMeta">
            <span>原典：厚生労働省2025年ガイドライン／2024年通知</span>
            <span>主な対象：介護保険施設</span>
            <span>個別の介助・医療・法的判断なし</span>
          </div>
        </section>
        <nav className="sourceGuideContents" aria-label="この記事の目次">
          <strong>このページの内容</strong>
          <a href="#factors">利用者と環境</a>
          <a href="#dignity">行動制限と尊厳</a>
          <a href="#bed">ベッド周辺</a>
          <a href="#report">報告の対象と期限</a>
          <a href="#scope">掲載範囲と注意</a>
          <a href="#sources">出典を確認する</a>
        </nav>
        {/* FALL-01: 2025 MHLW guideline book p30 / PDF p33; primarily long-term care facilities. */}
        <section className="section" aria-labelledby="factors">
          <p className="eyebrow">転倒の要因</p>
          <h2 id="factors">利用者と生活環境の両方を見る</h2>
          <p>
            厚生労働省のガイドラインは、転倒の要因には身体面・認知面・環境面などがあり、
            複数の要因が絡むことを説明しています。施設で対策を考える際には、
            利用者ごとの状態と生活環境を合わせて検討する視点を示しています。
            「すべての転倒を防げる」「転倒が起きれば必ず職員の過失」と述べたものではありません。
            （<span className="sourceGuideCitation"><a href="#source-guideline">出典1・ガイドライン／施設中心・冊子30頁／PDF33頁</a> / <a href="https://www.mhlw.go.jp/content/001591418.pdf#page=33" target="_blank" rel="noreferrer" aria-label="転倒の要因に関する原文を新しいタブで開く">原文（別タブ） ↗</a></span>）
          </p>
        </section>
        {/* FALL-02: 2025 MHLW guideline book p30 / PDF p33. */}
        <section className="section muted" aria-labelledby="dignity">
          <p className="eyebrow">本人の生活と尊厳</p>
          <h2 id="dignity">過度な行動制限にも注意する</h2>
          <p>
            同ガイドラインは、転倒を防ごうとして利用者の行動を過度に制限すると、
            身体拘束につながるおそれがあると注意しています。
            事故防止と本人の生活・尊厳をともに考える視点を示したものです。
            <strong>個別の対応が法令上の身体拘束に当たるかを、このページで判定することはできません。</strong>
            （<span className="sourceGuideCitation"><a href="#source-guideline">出典1・ガイドライン／冊子30頁／PDF33頁</a> / <a href="https://www.mhlw.go.jp/content/001591418.pdf#page=33" target="_blank" rel="noreferrer" aria-label="行動制限と尊厳に関する原文を新しいタブで開く">原文（別タブ） ↗</a></span>）
          </p>
        </section>
        {/* FALL-03: 2025 MHLW guideline book p32 / PDF p35. */}
        <section className="section" aria-labelledby="bed">
          <p className="eyebrow">転落の予防</p>
          <h2 id="bed">ベッド周辺の転落は本人の状態と環境を合わせて検討する</h2>
          <p>
            同ガイドラインは、ベッドからの転落を考える際、利用者の状態とベッド周辺の環境を踏まえた検討を示しています。
            特定のベッド柵、機器、配置や介助の方法を、全員への共通指示として紹介するものではありません。
            個別の対応は、施設・事業所の正式手順と担当する専門職の判断に基づいて検討してください。
            （<span className="sourceGuideCitation"><a href="#source-guideline">出典1・ガイドライン／冊子32頁／PDF35頁</a> / <a href="https://www.mhlw.go.jp/content/001591418.pdf#page=35" target="_blank" rel="noreferrer" aria-label="ベッド周辺の転落に関する原文を新しいタブで開く">原文（別タブ） ↗</a></span>）
          </p>
        </section>
        {/* MED-A04/A05 & X-02: 2024 MHLW accident reporting notice, body pp2-3 / PDF pp3-4. */}
        <section className="section muted" aria-labelledby="report">
          <p className="eyebrow">事故発生時の連絡と行政報告</p>
          <h2 id="report">事故発生時の連絡と市町村への報告は別の手続</h2>
          <p>
            事故への対応と医療職への相談は、所属先の正式手順と必要な専門職の判断を優先します。
            市町村への事故報告については、厚生労働省の2024年通知が、死亡に至った事故、
            医師の診断を受け投薬・処置等の治療が必要になった事故を原則として報告するものと示しています。
            それ以外は自治体の取扱いによります。第1報の「遅くとも5日以内」は<strong>目安</strong>です。
            （<span className="sourceGuideCitation"><a href="#source-notice">出典2・2024年通知／本文2頁／PDF3頁</a> / <a href="https://www.mhlw.go.jp/content/001574219.pdf#page=3" target="_blank" rel="noreferrer" aria-label="報告対象と期限に関する原文を新しいタブで開く">原文（別タブ） ↗</a></span>）
          </p>
          <p>
            同通知の別紙様式は、介護保険施設や認知症対応型共同生活介護、
            特定施設入居者生活介護、一定の高齢者向け住まい等を主に想定しています。
            他の居宅等の介護サービスでも可能な限り活用するよう示されていますが、
            具体的な報告要否・報告先・期限はサービス種類と自治体の現行の取扱いを確認する必要があります。
            このページはそれらを個別に判定しません。
            （<span className="sourceGuideCitation"><a href="#source-notice">出典2・2024年通知／本文3頁／PDF4頁</a> / <a href="https://www.mhlw.go.jp/content/001574219.pdf#page=4" target="_blank" rel="noreferrer" aria-label="様式対象サービスに関する原文を新しいタブで開く">原文（別タブ） ↗</a></span>）
          </p>
        </section>
        <section className="section boundary" aria-labelledby="scope">
          <p className="eyebrow">掲載範囲と注意</p>
          <h2 id="scope">個別の医療・介助・法的判断には使用しないでください</h2>
          <p>
            ベッド柵やセンサーの具体設定、身体拘束の適法性判断、症状別の受診・搬送判定、一律の介助工程、
            施設事例の事故削減効果・数値は掲載していません。
            本文は公的資料の要約であり、厚生労働省による監修や医療専門職による個別審査を受けたものではありません。
            <a href="/guides/medication-incident-sources">服薬事故の公的資料も確認する →</a>
          </p>
          <p>このサイトに事故内容、利用者・職員の個人情報、薬剤名を入力する機能はありません。</p>
        </section>
        <section className="section" id="sources" aria-labelledby="sources-head">
          <div className="sectionHead">
            <p className="eyebrow">出典と元資料</p>
            <h2 id="sources-head">原文を読む</h2>
            <p>本文は公的資料の要約です。資料の発行日・種類・対象・該当ページを確認し、個別の対応は所属先の正式手順で判断してください。</p>
          </div>
          <div className="sourceList">
            <a id="source-guideline" className="sourceRow" href="https://www.mhlw.go.jp/content/001591418.pdf" target="_blank" rel="noreferrer">
              <span>01</span><div><strong>厚生労働省老健局「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」</strong>
              <p>2025年11月／ガイドライン／主対象：介護保険施設／冊子30・32頁（PDF通し33・35頁）。</p></div>
              <span aria-hidden="true">↗</span>
            </a>
            <a id="source-notice" className="sourceRow" href="https://www.mhlw.go.jp/content/001574219.pdf" target="_blank" rel="noreferrer">
              <span>02</span><div><strong>厚生労働省老健局「介護保険施設等における事故の報告様式等について」介護保険最新情報Vol.1332</strong>
              <p>2024年11月29日／通知／本文2〜3頁（PDF通し3〜4頁）。報告様式の主な対象サービスと各サービスの具体的な報告義務は区別。</p></div>
              <span aria-hidden="true">↗</span>
            </a>
          </div>
        </section>
      </article>
      <footer><span>介護業務改善 — 公的資料の適用範囲を確認するための案内</span><a href="/">トップに戻る</a></footer>
    </main>
  );
}
