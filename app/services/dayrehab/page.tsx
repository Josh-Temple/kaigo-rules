import Link from "next/link";
import VerificationSummary from "../../../components/verification-summary";
import standardsData from "../../../data/services/dayrehab/standards-index.json";

const standards = standardsData as any;

export default function DayrehabPage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY REHABILITATION / PREVIEW</p>
      <h1>通所リハビリテーション</h1>
      <p className="lead">
        通所リハビリテーションの制度情報を、サービス固有の確認状態を保ったまま公開していきます。現在は基準省令の第110条〜第119条（第118条の2を含む）11条をインデックス公開しています。
      </p>

      <div className="notice">
        <strong>公開プレビューです。</strong><br />
        Cycle 3でCommitter受理済みの一次資料抽出を使っていますが、通所リハとしての独立e-Gov再照合と現行性確認は未完了です。通所介護の検証状態は継承していません。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab-preview" />

      <section className="rules-stats" aria-label="通所リハビリテーション公開状況">
        <div><strong>{standards.article_count}</strong><span>基準省令・公開インデックス</span></div>
        <div><strong>0</strong><span>独立e-Gov再照合済み</span></div>
        <div><strong>0</strong><span>人手確認済み</span></div>
        <div><strong>4</strong><span>収集済み・公開統合前レイヤー</span></div>
      </section>

      <div className="entry-links">
        <Link className="entry-row" href="/services/dayrehab/rules">
          <span>基準省令11条を見る</span>
          <small>第110条〜第119条 →</small>
        </Link>
      </div>

      <section className="section">
        <h2>このプレビューでまだ公開していないもの</h2>
        <p>
          介護保険法、基準解釈通知、報酬基準、算定上の留意事項はWork Controlで収集・Committer確認済みですが、service-specificな公開データへの統合はまだ行っていません。
        </p>
        <p className="meta">
          収集済みであることと、公開サイトで現行・確認済みとして扱えることは分けて管理します。
        </p>
      </section>

      <p><Link href="/services">サービス一覧へ戻る</Link></p>
    </article>
  );
}
