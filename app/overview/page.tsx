import Link from "next/link";
import registryData from "../../data/verification-registry.json";

const registry = registryData as any;

const sourceRows = [
  { number: "01", title: "介護保険法", role: "サービスの定義、保険給付、指定、更新、監督など制度の骨格を確認します。" },
  { number: "02", title: "基準省令", role: "人員、設備、運営など、事業所が満たすべき基準を確認します。" },
  { number: "03", title: "解釈通知", role: "基準省令を実務でどう読むか、具体的な取扱いを確認します。" },
  { number: "04", title: "報酬告示", role: "基本報酬、加算・減算、算定方法に関する告示を確認します。" },
  { number: "05", title: "算定上の留意事項", role: "報酬告示を実務で適用する際の具体的な取扱いを確認します。" },
  { number: "06", title: "一単位単価・地域区分", role: "地域区分ごとの一単位単価と自治体の区分を確認します。" },
  { number: "07", title: "厚生労働省Q&A", role: "個別の疑問について、国が示した具体的な取扱いを確認します。" },
];

export default function OverviewPage() {
  return (
    <article className="answer-page wide-page foundation-page">
      <p className="eyebrow">INFORMATION FOUNDATION</p>
      <h1>制度の見取り図</h1>
      <p className="lead">
        介護サービスの制度は、一つの資料だけでは完結しません。
        上位法、基準省令、解釈通知、報酬、国Q&Aを役割ごとに分け、
        各サービスのページから必要な根拠へ順番にたどれるように整理します。
      </p>
      <p className="scope-note">
        このページは特定サービスの入口ではなく、サイト全体で共通する情報構造を示します。
        実際の本文・検索・確認状態は、サービスごとの公開ページで確認してください。
      </p>

      <section className="section">
        <p className="eyebrow">SOURCE LAYERS</p>
        <h2>制度からたどる</h2>
        <div className="foundation-list">
          {sourceRows.map((row) => (
            <div className="foundation-row foundation-row-static" key={row.number}>
              <span className="foundation-number">{row.number}</span>
              <span className="foundation-main">
                <strong>{row.title}</strong>
                <small>{row.role}</small>
              </span>
              <span className="foundation-state"><small>資料レイヤー</small></span>
            </div>
          ))}
        </div>
        <p className="home-more-link"><Link href="/databases">制度DBをまとめて見る →</Link></p>
      </section>

      <section className="section">
        <p className="eyebrow">RELATION GRAPH</p>
        <h2>資料同士をつなぐ</h2>
        <p>
          基準の準用、上位法から基準への委任、報酬の委任・参照、FAQから根拠への接続など
          <strong>{registry.relation_verification?.inventory_relations || 0}件</strong>の関係を保持しています。
          この関係を、画面の横断導線と将来のAI検索・回答生成で共通利用します。
        </p>
      </section>

      <section className="section">
        <p className="eyebrow">SERVICE CONTEXT</p>
        <h2>確認状態はサービスごとに分ける</h2>
        <p>
          同じ法令や通知を参照していても、適用範囲、準用関係、報酬体系、現行性の確認状態はサービスによって異なります。
          そのため、確認済み・確認待ち・GAPなどの状態はサービス単位で扱い、別サービスへ自動的に流用しません。
        </p>
        <p>
          各サービスでは、本文の照合、現行性、人手確認を別々に表示します。
          「独立確認済み」は本文の独立照合が完了したことを示し、現行性や人手確認まで完了した意味ではありません。
        </p>
        <p><Link href="/services">対象サービスを選ぶ →</Link></p>
      </section>

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
