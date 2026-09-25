import Link from "next/link";
import registryData from "../../data/verification-registry.json";

type Layer = {
  id: string;
  content_verification?: { status?: string };
  currentness?: { status?: string };
  human_review?: { status?: string };
};

const registry = registryData as any;
const layers = new Map<string, Layer>(
  (registry.layers || []).map((layer: Layer) => [layer.id, layer])
);

const sourceRows = [
  { number: "01", title: "介護保険法", href: "/law", layerId: "care-insurance-act", role: "サービスの定義、保険給付、指定、更新、監督など制度の骨格を確認します。" },
  { number: "02", title: "基準省令", href: "/rules", layerId: "ordinance37", role: "人員、設備、運営など、事業所が満たすべき基準を確認します。" },
  { number: "03", title: "解釈通知", href: "/notices", layerId: "rouki25-dayservice", role: "基準省令を実務でどう読むか、具体的な取扱いを確認します。" },
  { number: "04", title: "報酬告示", href: "/fees", layerId: "remuneration-notices", role: "基本報酬、加算・減算、算定方法に関する告示を確認します。" },
  { number: "05", title: "算定上の留意事項", href: "/fees/guidance", layerId: "rouki36-dayservice", role: "報酬告示を実務で適用する際の取扱いを、老企第36号から確認します。" },
  { number: "06", title: "一単位単価・地域区分", href: "/fees/unit-price", layerId: "unit-price", role: "地域区分ごとの一単位単価と自治体の区分を確認します。" },
  { number: "07", title: "厚生労働省Q&A", href: "/qa", layerId: "qa-corpus", role: "個別の疑問について、国が示した過去の具体的な取扱いを確認します。" },
];

const label = (value?: string) => {
  const labels: Record<string, string> = {
    PASS: "独立確認済み",
    HOLD: "未確定",
    LIVE_SOURCE_REPARSE_SCHEDULED: "継続監視",
    MONITORED_NOT_HUMAN_VERIFIED: "継続監視",
    NOT_REVIEWED: "未実施",
    NOT_STARTED: "未実施",
    IMPORTED_NEEDS_HUMAN_CHECK: "確認待ち",
    INGESTED_UNREVIEWED: "確認待ち",
  };
  return value ? labels[value] || value : "—";
};

export default function OverviewPage() {
  return (
    <article className="answer-page wide-page foundation-page">
      <p className="eyebrow">INFORMATION FOUNDATION</p>
      <h1>制度の見取り図</h1>
      <p className="lead">
        介護サービスの制度は、一つの資料だけでは完結しません。
        上位法、基準省令、解釈通知、報酬、国Q&Aを役割ごとに分け、
        必要な根拠へ順番にたどれるように整理しています。
      </p>
      <p className="scope-note">
        現在公開している制度データは通所介護が中心です。サイト全体は、居宅系・地域密着型と
        ケアマネジメントへ順次広げる前提で構成しています。
      </p>

      <section className="section">
        <p className="eyebrow">SOURCE LAYERS</p>
        <h2>制度からたどる</h2>
        <div className="foundation-list">
          {sourceRows.map((row) => (
            <Link className="foundation-row" href={row.href} key={row.number}>
              <span className="foundation-number">{row.number}</span>
              <span className="foundation-main">
                <strong>{row.title}</strong>
                <small>{row.role}</small>
              </span>
              <span className="foundation-arrow">→</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <p className="eyebrow">RELATION GRAPH</p>
        <h2>資料同士をつなぐ</h2>
        <p>
          基準の準用、上位法から基準への委任、報酬の委任・参照、FAQから根拠への接続など
          <strong>{registry.relation_verification?.inventory_relations || 0}件</strong>の関係を保持しています。
          この関係を、画面の横断導線と将来のAI検索・回答生成で共通利用します。
        </p>
        <p><Link href="/rules/93">例：人員基準から関連情報をたどる →</Link></p>
      </section>

      <section className="section">
        <p className="eyebrow">PRACTICAL QUESTIONS</p>
        <h2>実務FAQは、制度情報への入口</h2>
        <p>
          FAQは網羅を目指して増やすのではなく、事業所から繰り返し寄せられる質問、
          判断を誤ると影響が大きい論点、複数資料を見ないと分かりにくい論点を優先します。
          回答だけで終わらせず、基準・通知・Q&Aなどの根拠へ戻れる形にします。
        </p>
        <p><Link href="/search">実務の疑問から横断検索する →</Link></p>
      </section>

      <details className="verification-overview">
        <summary>データの確認状態を見る</summary>
        <div className="verification-overview-body">
          <p>
            本文の独立確認、現行性、人手確認は別々に管理しています。管理上の状態を通常の閲覧より
            前面に出さず、必要なときに確認できるようにしています。
          </p>
          <div className="verification-table">
            {sourceRows.map((row) => {
              const layer = layers.get(row.layerId);
              return (
                <div className="verification-row" key={row.layerId}>
                  <strong>{row.title}</strong>
                  <span>本文 {label(layer?.content_verification?.status)}</span>
                  <span>現行性 {label(layer?.currentness?.status)}</span>
                  <span>人手 {label(layer?.human_review?.status)}</span>
                </div>
              );
            })}
          </div>
        </div>
      </details>

      <section className="section">
        <h2>このサイトが目指さないもの</h2>
        <p>
          厚生労働省やe-Govの資料を置き換えることや、FAQの件数を増やすこと自体は目的にしません。
          公式情報の関係を整理し、実務上の疑問から必要な根拠へ短くたどれることを優先します。
        </p>
      </section>
    </article>
  );
}
