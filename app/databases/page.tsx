import Link from "next/link";
import lawMetaData from "../../data/care-insurance-act-meta.json";
import ordinanceMetaData from "../../data/ordinance37-meta.json";
import qaMetaData from "../../data/qa-corpus-meta.json";
import {
  publicNoticePublishedServiceCount,
  publicNoticeRecords,
} from "../../lib/notice-database";

const lawMeta = lawMetaData as any;
const ordinanceMeta = ordinanceMetaData as any;
const qaMeta = qaMetaData as any;

const databases = [
  {
    id: "care-insurance-act",
    number: "01",
    title: "介護保険法DB",
    detail: "制度の定義・給付・指定・監督など。共有コーパスを全体表示し、公開済みサービスは絞り込みできます。",
    href: "/law",
    status: `${lawMeta.counts?.articles_total || 0}条 / 共有コーパス`,
  },
  {
    id: "ordinance37",
    number: "02",
    title: "基準省令DB",
    detail: "人員・設備・運営基準。共有コーパスを全体表示し、サービスの直接規定・準用規定へ絞り込めます。",
    href: "/rules",
    status: `${ordinanceMeta.counts?.articles_total || 0}条 / 全体表示`,
  },
  {
    id: "notices",
    number: "03",
    title: "基準解釈通知DB",
    detail: "公開済みサービスの解釈通知を一つの画面で表示し、サービス別に絞り込みます。",
    href: "/notices",
    status: `${publicNoticeRecords.length}項目 / ${publicNoticePublishedServiceCount}サービス本文公開`,
  },
  {
    id: "qa",
    number: "04",
    title: "国Q&A DB",
    detail: "厚生労働省Q&Aを検索します。公式XLSXでサービス種別コードが付いたQ&Aを全分類で収載し、主分類から絞り込めます。",
    href: "/qa",
    status: `${qaMeta.rows_included?.toLocaleString("ja-JP") || 0}件 / 全サービス分類`,
  },
];

export default function DatabasesPage() {
  return (
    <article className="answer-page wide-page foundation-page">
      <p className="eyebrow">制度DB</p>
      <h1>介護制度DB</h1>
      <p className="lead">
        サービスを一つ選ばなくても、介護保険法・基準省令・解釈通知・国Q&AをDB単位で確認できます。
        キーワード検索から始めることも、必要なDBを選んで原文へ進むこともできます。
      </p>

      <div className="notice">
        <strong>DBごとに公開範囲が異なります。</strong><br />
        各ページで出典・対象範囲・確認情報を確認できます。未確認の範囲を確認済みとして表示しません。
      </div>

      <section className="section">
        <p className="eyebrow">DATABASE-WIDE SEARCH</p>
        <h2>4つの共有DBを全体横断検索</h2>
        <p>
          介護保険法、基準省令、公開済みの基準解釈通知、国Q&Aを、
          サービスを先に選ばず同じキーワードで検索します。
        </p>
        <form className="global-search-form" method="get" action="/databases/search">
          <label>
            <span>キーワード</span>
            <input
              name="q"
              placeholder="例：業務継続計画、認知症、通所リハ"
            />
          </label>
          <button type="submit">全体から検索する</button>
        </form>
        <p className="meta">
          報酬基準・算定上の留意事項はサービス別の確認状態を保持するため、全体検索には混ぜません。
        </p>
      </section>

      <section className="section">
        <h2>全体から見られるDB</h2>
        <div className="foundation-list">
          {databases.map((item) => (
            <Link className="foundation-row" href={item.href} key={item.id}>
              <span className="foundation-number">{item.number}</span>
              <span className="foundation-main">
                <strong>{item.title}</strong>
                <small>{item.detail}</small>
              </span>
              <span className="foundation-state"><small>{item.status}</small></span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section" id="remuneration">
        <p className="eyebrow">SERVICE-SPECIFIC DATABASE</p>
        <h2>報酬基準DB</h2>
        <p>
          報酬はサービスごとに構造と確認状態が異なるため、現時点では無理に一つの本文へ統合しません。
          DBの入口だけ共通化し、確認済みのサービス別データへ進みます。
        </p>
        <div className="entry-links">
          <Link className="entry-row" href="/fees">
            <span>通所介護</span>
            <small>報酬基準DB →</small>
          </Link>
          <Link className="entry-row" href="/services/dayrehab/remuneration">
            <span>通所リハビリテーション</span>
            <small>報酬基準DB →</small>
          </Link>
        </div>
      </section>

      <section className="section" id="fee-guidance">
        <p className="eyebrow">SERVICE-SPECIFIC DATABASE</p>
        <h2>算定上の留意事項</h2>
        <p>
          版・省略箇所・現行性の確認状況がサービスごとに異なるため、サービス固有の状態を保持したまま公開します。
        </p>
        <div className="entry-links">
          <Link className="entry-row" href="/fees/guidance">
            <span>通所介護</span>
            <small>算定上の留意事項 →</small>
          </Link>
          <Link className="entry-row" href="/services/dayrehab/remuneration/guidance">
            <span>通所リハビリテーション</span>
            <small>算定上の留意事項 →</small>
          </Link>
        </div>
      </section>

      <section className="section" id="unit-price">
        <p className="eyebrow">SERVICE-SPECIFIC DATABASE</p>
        <h2>一単位単価・地域区分</h2>
        <p>
          厚生労働省の単価告示について、公開条件を満たすサービスを選び、
          地域区分・一単位単価・市区町村名から確認します。
          現行性と地域割当の人手確認は別の状態として表示します。
        </p>
        <p><Link href="/fees/unit-price">公開済みサービスの単価を検索する →</Link></p>
      </section>

      <section className="section">
        <h2>サービスから見る場合</h2>
        <p>
          特定サービスの制度情報だけを確認したい場合は、サービス別ページから検索・基準・通知・報酬へ進めます。
        </p>
        <p><Link href="/services">サービス別の公開情報を見る →</Link></p>
      </section>
    </article>
  );
}
