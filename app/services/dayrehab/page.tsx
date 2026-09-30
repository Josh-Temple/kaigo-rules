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
        基準省令の直接規定、現行第119条の準用関係、基準解釈通知の公式旧HTMLを、確認状態を分離したまま公開しています。
      </p>

      <div className="notice">
        <strong>確認済みの範囲だけを広げています。</strong><br />
        第八章11条の本文は独立再照合済み、第119条の25の準用relationも独立監査済みです。
        解釈通知9項目は公式旧HTMLとの本文一致まで確認していますが、現行統合本文ではなくcurrentness GAPです。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab" />

      <section className="rules-stats" aria-label="通所リハビリテーション公開状況">
        <div><strong>{index.counts.direct_articles}</strong><span>第八章・直接本文</span></div>
        <div><strong>{index.counts.incorporated_articles_total}</strong><span>第119条・準用relation</span></div>
        <div><strong>{notice.item_count}</strong><span>解釈通知・旧HTML項目</span></div>
        <div><strong>3</strong><span>収集済み・公開統合前レイヤー</span></div>
      </section>

      <div className="entry-links">
        <Link className="entry-row" href="/services/dayrehab/rules">
          <span>基準省令と第119条の準用関係を見る</span>
          <small>直接11条 + 準用25条 →</small>
        </Link>
        <Link className="entry-row" href="/services/dayrehab/notices">
          <span>基準解釈通知を見る</span>
          <small>公式旧HTML 9項目 / 現行性GAP →</small>
        </Link>
      </div>

      <section className="section">
        <h2>まだ公開統合していないもの</h2>
        <p>
          介護保険法、報酬基準、算定上の留意事項はWork Controlで収集・Committer確認済みですが、service-specificな公開データへの統合はまだ行っていません。
        </p>
        <p className="meta">
          基準解釈通知は公開しましたが、公式旧HTMLと令和6年度新旧対照を統合した「現行全文」としては扱っていません。
        </p>
      </section>
      <p><Link href="/services">サービス一覧へ戻る</Link></p>
    </article>
  );
}
