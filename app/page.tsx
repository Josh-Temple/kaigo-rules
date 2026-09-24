import Link from "next/link";
import QuestionSearch from "../components/question-search";
import { getDefaultService } from "../lib/service-catalog";

const foundationLinks = [
  { label: "介護保険法", detail: "制度の定義・指定・給付", href: "/law" },
  { label: "基準省令", detail: "人員・設備・運営", href: "/rules" },
  { label: "解釈通知", detail: "基準の具体的な読み方", href: "/notices" },
  { label: "報酬", detail: "単位・加算減算・算定", href: "/fees" },
  { label: "国Q&A", detail: "個別論点の行政解釈", href: "/qa" },
];

export default function HomePage() {
  const service = getDefaultService();

  return (
    <>
      <section className="hero foundation-hero">
        <p className="eyebrow">{service.label} / 制度情報基盤</p>
        <h1>介護制度を、<br />根拠からたどれるように。</h1>
        <p className="lead">
          法令、基準省令、解釈通知、報酬、国Q&Aを分断せず、
          {service.label}の実務で必要な範囲を関係付けて整理します。
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
            <span>これから通所介護を始めたい</span>
            <small>開設準備の順番を確認する →</small>
          </Link>
        </div>
      </section>
    </>
  );
}
