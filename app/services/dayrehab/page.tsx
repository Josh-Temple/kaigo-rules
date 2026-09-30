import Link from "next/link";
import VerificationSummary from "../../../components/verification-summary";
import indexData from "../../../data/services/dayrehab/ordinance37-index.generated.json";

const index = indexData as any;

export default function DayrehabPage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY REHABILITATION / PREVIEW</p>
      <h1>通所リハビリテーション</h1>
      <p className="lead">
        通所リハビリテーションの制度情報を、サービス固有の確認状態を保ったまま公開しています。現在は基準省令の第110条〜第119条（第118条の2を含む）11条について、e-Gov本文まで公開しています。
      </p>

      <div className="notice">
        <strong>基準省令本文は独立再照合済みです。</strong><br />
        共有コーパスへ取り込んだ第八章の本文・構造を、別のXMLパーサでlive e-Govから再構成して一致を確認しています。人手による法務確認ではなく、後続のsource更新は継続監視します。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab" />

      <section className="rules-stats" aria-label="通所リハビリテーション公開状況">
        <div><strong>{index.counts.selected_articles}</strong><span>基準省令・本文公開</span></div>
        <div><strong>{index.counts.selected_articles}</strong><span>独立e-Gov再照合済み</span></div>
        <div><strong>0</strong><span>人手確認済み</span></div>
        <div><strong>4</strong><span>収集済み・公開統合前レイヤー</span></div>
      </section>

      <div className="entry-links">
        <Link className="entry-row" href="/services/dayrehab/rules">
          <span>基準省令11条の本文を見る</span>
          <small>第110条〜第119条 →</small>
        </Link>
      </div>

      <section className="section">
        <h2>このプレビューでまだ公開していないもの</h2>
        <p>
          介護保険法、基準解釈通知、報酬基準、算定上の留意事項はWork Controlで収集・Committer確認済みですが、service-specificな公開データへの統合はまだ行っていません。
        </p>
        <p className="meta">
          また、第119条が準用する他章の規定は、明示relationとしての展開・検証が完了するまで、この11条の本文とは別に扱います。
        </p>
      </section>

      <p><Link href="/services">サービス一覧へ戻る</Link></p>
    </article>
  );
}
