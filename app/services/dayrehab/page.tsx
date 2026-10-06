import Link from "next/link";
import VerificationSummary from "../../../components/verification-summary";
import indexData from "../../../data/services/dayrehab/ordinance37-index.generated.json";
import noticeData from "../../../data/services/dayrehab/rouki25-historical.generated.json";

const index = indexData as any;
const notice = noticeData as any;

export default function DayrehabPage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY REHABILITATION / PREVIEW</p>
      <h1>通所リハビリテーション</h1>
      <p className="lead">
        基準省令の直接規定、第119条の準用関係、基準解釈通知の公式旧HTMLを、出典と確認状況を分けて公開しています。
      </p>

      <div className="notice">
        <strong>確認済みの範囲だけを広げています。</strong><br />
        第八章11条の本文は独立再照合済みで、第119条による25条文の準用関係も確認済みです。
        解釈通知は公式旧HTMLの旧版資料です。報酬基準と算定上の留意事項は、出典別の項目・改正差分を公開し、現行性は確認中です。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab" />

      <section className="rules-stats" aria-label="通所リハビリテーション公開状況">
        <div><strong>{index.counts.direct_articles}</strong><span>第八章・直接本文</span></div>
        <div><strong>{index.counts.incorporated_articles_total}</strong><span>第119条・準用条文</span></div>
        <div><strong>{notice.item_count}</strong><span>解釈通知・旧HTML項目</span></div>
        <div><strong>1</strong><span>収集済み・未公開の資料群</span></div>
      </section>

      <div className="entry-links">
        <Link className="entry-row" href="/services/dayrehab/search">
          <span>公開中の4資料群を横断検索</span>
          <small>基準省令・解釈通知・報酬基準・算定留意事項 →</small>
        </Link>
        <Link className="entry-row" href="/rules?service=dayrehab">
          <span>基準省令と第119条の準用関係を見る</span>
          <small>直接11条 + 準用25条 →</small>
        </Link>
        <Link className="entry-row" href="/notices?service=dayrehab">
          <span>基準解釈通知を見る</span>
          <small>公式旧HTML 9項目 / 現行性確認中 →</small>
        </Link>
        <Link className="entry-row" href="/services/dayrehab/remuneration">
          <span>報酬基準を見る</span>
          <small>42項目 / 令和8告示差分は別表示 / 現行性確認中 →</small>
        </Link>
        <Link className="entry-row" href="/services/dayrehab/remuneration/guidance">
          <span>算定上の留意事項を見る</span>
          <small>令和6対照表 33項目・88子項目 / 現行性確認中 →</small>
        </Link>
      </div>

      <section className="section">
        <h2>まだ公開統合していないもの</h2>
        <p>
          介護保険法の関連資料は収集済みですが、通所リハビリテーションのサービス別ページへの統合はまだ行っていません。
        </p>
        <p className="meta">
          各資料群は出典・版・確認状況を分けています。報酬基準の掲載表示と令和8年差分、留意事項の令和6年対照表と令和8年対照表を結合した「現行全文」は作成していません。
        </p>
      </section>
      <p><Link href="/services">サービス一覧へ戻る</Link></p>
    </article>
  );
}
