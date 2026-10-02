import Link from "next/link";
import QuestionSearch from "../components/question-search";
import { DEFAULT_SERVICE_ID, listServices, publishedLayerLabels } from "../lib/service-catalog";

const foundationLayers = [
  { label: "介護保険法", detail: "制度の定義・指定・給付" },
  { label: "基準省令", detail: "人員・設備・運営" },
  { label: "解釈通知", detail: "基準の具体的な読み方" },
  { label: "報酬", detail: "単位・加算減算・算定" },
  { label: "国Q&A", detail: "個別論点の行政解釈" },
];

const targetScopes = [
  "居宅サービス（対応する介護予防サービスを含む）",
  "地域密着型サービス（対応する地域密着型介護予防サービスを含む）",
  "居宅介護支援",
  "介護予防支援",
];

const publicServices = listServices().filter(
  (service) =>
    service.service_id === DEFAULT_SERVICE_ID ||
    service.routing.future_service_base_enabled,
);
const publicServiceLabels = publicServices.map((service) => service.label).join("・");

export default function HomePage() {
  return (
    <>
      <section className="hero foundation-hero">
        <p className="eyebrow">介護制度 / 情報基盤</p>
        <h1>介護制度を、<br />根拠からたどれるように。</h1>
        <p className="lead">
          介護保険法、基準省令、解釈通知、報酬、国Q&Aを分断せず、
          サービスごとに公開範囲と確認状態を分けて整理します。現在は{publicServiceLabels}を公開しています。
        </p>
        <div className="entry-links foundation-entry-links">
          <Link className="entry-row" href="/services">
            <span>サービスを選んで調べる</span>
            <small>公開中のサービス一覧 →</small>
          </Link>
          <Link className="entry-row" href="/overview">
            <span>制度情報の構造を確認する</span>
            <small>制度の見取り図 →</small>
          </Link>
          <Link className="entry-row" href="/sources">
            <span>根拠資料と出典を確認する</span>
            <small>根拠資料 →</small>
          </Link>
        </div>
      </section>

      <section className="home-section">
        <p className="eyebrow">SOURCE LAYERS</p>
        <h2>制度資料を、サービスごとにつなぐ</h2>
        <p className="lead">
          一つの資料だけで判断せず、対象サービスを起点に上位法から通知・Q&Aまでたどれる構造にします。
        </p>
        <div className="foundation-list">
          {foundationLayers.map((item, index) => (
            <div className="foundation-row foundation-row-static" key={item.label}>
              <span className="foundation-number">{String(index + 1).padStart(2, "0")}</span>
              <span className="foundation-main">
                <strong>{item.label}</strong>
                <small>{item.detail}</small>
              </span>
              <span className="foundation-state"><small>サービス別に公開</small></span>
            </div>
          ))}
        </div>
        <p className="home-more-link"><Link href="/services">サービス別の公開情報を見る →</Link></p>
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
          通所介護は複数レイヤーを公開中です。通所リハビリテーションは{publishedLayerLabels("dayrehab").join("・")}を公開しています。
          未整備のサービスを確認済みとして表示したり、あるサービスの検証結果を別サービスへ流用したりしません。
        </p>
      </section>

      <section className="home-section practical-entry">
        <p className="eyebrow">CURATED PRACTICAL QUESTIONS / DAY SERVICE</p>
        <h2>通所介護でよく迷う論点</h2>
        <p className="lead">
          実務FAQは現在、通所介護を中心に公開しています。回答だけで終わらせず、公式の根拠へ戻れる論点だけを掲載します。
          他サービスは各サービスページの公開範囲に合わせて追加します。
        </p>
        <QuestionSearch initialLimit={6} />
        <p className="home-more-link"><Link href="/services/dayservice">通所介護の公開情報を見る →</Link></p>
      </section>
    </>
  );
}
