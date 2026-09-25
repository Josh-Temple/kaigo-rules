import Link from "next/link";
import QuestionSearch from "../components/question-search";

const foundationLinks = [
  { label: "介護保険法", detail: "制度の定義・指定・給付", href: "/law" },
  { label: "基準省令", detail: "人員・設備・運営", href: "/rules" },
  { label: "解釈通知", detail: "基準の具体的な読み方", href: "/notices" },
  { label: "報酬", detail: "単位・加算減算・算定", href: "/fees" },
  { label: "国Q&A", detail: "個別論点の行政解釈", href: "/qa" },
];

const targetScopes = [
  "居宅サービス（対応する介護予防サービスを含む）",
  "地域密着型サービス（対応する地域密着型介護予防サービスを含む）",
  "居宅介護支援",
  "介護予防支援",
];

export default function HomePage() {
  return (
    <>
      <section className="hero foundation-hero">
        <p className="eyebrow">介護制度 / 情報基盤</p>
        <h1>介護制度を、<br />根拠からたどれるように。</h1>
        <p className="lead">
          介護保険法、基準省令、解釈通知、報酬、国Q&Aを分断せず、
          サービスごとに関係付けて整理します。現在は通所介護から公開範囲を広げています。
        </p>
        <div className="entry-links foundation-entry-links">
          <Link className="entry-row" href="/overview">
            <span>制度の全体像から確認する</span>
            <small>制度の見取り図 →</small>
          </Link>
          <Link className="entry-row" href="/search">
            <span>疑問から根拠を横断検索する</span>
            <small>横断検索 →</small>
          </Link>
        </div>
      </section>

      <section className="home-section">
        <p className="eyebrow">SOURCE LAYERS</p>
        <h2>制度から探す</h2>
        <p className="lead">
          一つの資料だけで判断せず、論点に応じて上位法から通知・Q&Aまでたどります。
        </p>
        <div className="foundation-list">
          {foundationLinks.map((item, index) => (
            <Link className="foundation-row" href={item.href} key={item.href}>
              <span className="foundation-number">{String(index + 1).padStart(2, "0")}</span>
              <span className="foundation-main">
                <strong>{item.label}</strong>
                <small>{item.detail}</small>
              </span>
              <span className="foundation-arrow">→</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="home-section">
        <p className="eyebrow">INITIAL SCOPE</p>
        <h2>在宅・地域生活を支えるサービスから整備</h2>
        <p className="lead">
          初期対象は、居宅系・地域密着型とケアマネジメントです。施設サービスは初期対象外とし、
          まず事業所数が多く、複数の制度資料を横断して確認する場面の多い領域を優先します。
        </p>
        <div className="scope-list">
          {targetScopes.map((scope) => <span key={scope}>{scope}</span>)}
        </div>
        <p className="meta">
          現在公開している制度データは通所介護が中心です。未整備のサービスを確認済みとして表示したり、
          通所介護の検証結果を他サービスへ流用したりしません。
        </p>
      </section>

      <section className="home-section practical-entry">
        <p className="eyebrow">CURATED PRACTICAL QUESTIONS</p>
        <h2>実務でよく迷う論点</h2>
        <p className="lead">
          FAQは網羅を目指しません。実際の問い合わせで繰り返し迷いやすい論点を絞り、
          回答から公式の根拠へ戻れるものだけを掲載します。
        </p>
        <QuestionSearch initialLimit={6} />
        <p className="home-more-link"><Link href="/search">すべての実務FAQと制度情報を検索する →</Link></p>
      </section>

      <section className="home-section">
        <div className="entry-links">
          <Link className="entry-row" href="/start">
            <span>通所介護の開設準備を見る</span>
            <small>現在公開中の開設ガイド →</small>
          </Link>
        </div>
      </section>
    </>
  );
}
