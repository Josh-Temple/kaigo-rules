import Link from "next/link";
import ServiceContextLinks from "../../../components/service-context-links";
import { publishedLayerLabels } from "../../../lib/service-catalog";

export default function DayservicePage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY SERVICE</p>
      <h1>通所介護</h1>
      <p className="lead">
        通所介護について公開している制度情報を、このページからまとめてたどれます。
        {publishedLayerLabels("dayservice").join("・")}を、出典と確認状態を分けて整理しています。
      </p>

      <div className="notice">
        このページは通所介護のサービス入口です。サイト共通メニューでは特定サービスを既定にせず、
        検索や各DBはここから通所介護の範囲へ入ります。
      </div>

      <ServiceContextLinks serviceId="dayservice" />

      <section className="section">
        <h2>制度の全体像と実務の入口</h2>
        <div className="entry-links">
          <Link className="entry-row" href="/overview">
            <span>制度資料の関係を確認する</span>
            <small>制度の見取り図 →</small>
          </Link>
          <Link className="entry-row" href="/law?service=dayservice">
            <span>介護保険法を見る</span>
            <small>定義・指定・給付・監督 →</small>
          </Link>
          <Link className="entry-row" href="/qa?service=16">
            <span>厚生労働省Q&Aを見る</span>
            <small>個別論点の行政解釈 →</small>
          </Link>
          <Link className="entry-row" href="/start">
            <span>開設準備の入口を見る</span>
            <small>現在公開中の開設ガイド →</small>
          </Link>
        </div>
      </section>

      <p><Link href="/services">サービス一覧へ戻る</Link></p>
    </article>
  );
}
