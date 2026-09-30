import Link from "next/link";
import VerificationSummary from "../../../../components/verification-summary";
import standardsData from "../../../../data/services/dayrehab/standards-index.json";

const standards = standardsData as any;
const sectionOrder = [
  "第一節 基本方針",
  "第二節 人員に関する基準",
  "第三節 設備に関する基準",
  "第四節 運営に関する基準",
];

export default function DayrehabRulesPage() {
  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">DAY REHABILITATION / ORDINANCE INDEX</p>
      <h1>通所リハビリテーションの基準省令</h1>
      <p className="lead">
        第八章「通所リハビリテーション」の第110条から第119条までを、条文単位のインデックスとして公開しています。
      </p>

      <div className="notice">
        <strong>本文全文はまだ公開していません。</strong><br />
        現在は、Committer受理済みの抽出結果から条番号・見出し・出典位置・改正表示を公開しています。共有e-Govコーパスへの統合と独立再照合が完了するまでは、現行本文として昇格しません。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab-preview" />

      <section className="rules-stats" aria-label="基準省令インデックスの状態">
        <div><strong>{standards.article_count}</strong><span>対象条文</span></div>
        <div><strong>{standards.articles.filter((item: any) => item.currentness_state === "GAP").length}</strong><span>現行性未確定</span></div>
        <div><strong>0</strong><span>独立再照合済み</span></div>
        <div><strong>0</strong><span>人手確認済み</span></div>
      </section>

      {sectionOrder.map((section) => {
        const items = standards.articles.filter((item: any) => item.section === section);
        if (!items.length) return null;
        return (
          <section className="section" key={section}>
            <h2>{section}</h2>
            <div className="rules-list">
              {items.map((item: any) => (
                <Link
                  className="rule-row"
                  href={`/services/dayrehab/rules/${item.article_number}`}
                  key={item.article_number}
                >
                  <span className="rule-number">{item.article_label}</span>
                  <span className="rule-title">{item.heading}</span>
                  <span className="rule-status">現行性確認待ち</span>
                </Link>
              ))}
            </div>
          </section>
        );
      })}

      <section className="section">
        <h2>一次資料</h2>
        <p>
          <a href="https://laws.e-gov.go.jp/law/411M50000100037" target="_blank" rel="noreferrer">e-Gov法令検索</a>
          {" / "}
          <a href="https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0" target="_blank" rel="noreferrer">厚生労働省 法令等データベース</a>
        </p>
        <p className="meta">公開インデックスの出典位置は各条文ページに記録しています。</p>
      </section>

      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
