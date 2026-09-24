import VerificationSummary from "../../components/verification-summary";
import Link from "next/link";
import nodesData from "../../data/ordinance37-nodes.json";
import metaData from "../../data/ordinance37-meta.json";
import reviewData from "../../data/ordinance37-review.json";

type RuleNode = {
  id: string;
  node_type: string;
  article_num: string;
  article_title?: string;
  caption?: string;
  path: string[];
  official_text: string;
  service_scope: string;
  verification_status: string;
};

const nodes = nodesData as RuleNode[];
const meta = metaData as any;
const review = reviewData as any;

const articleKey = (value: string) =>
  value.split("-").map((part) => Number.parseInt(part, 10) || 0);

const compareArticle = (a: RuleNode, b: RuleNode) => {
  const ak = articleKey(a.article_num);
  const bk = articleKey(b.article_num);
  for (let i = 0; i < Math.max(ak.length, bk.length); i += 1) {
    const diff = (ak[i] || 0) - (bk[i] || 0);
    if (diff) return diff;
  }
  return 0;
};

const articles = nodes.filter((node) => node.node_type === "article").sort(compareArticle);
const direct = articles.filter((node) => node.service_scope === "通所介護・直接規定");
const incorporated = articles.filter((node) => node.service_scope === "通所介護・第105条準用");

function ArticleList({ items }: { items: RuleNode[] }) {
  return (
    <div className="rules-list">
      {items.map((node) => (
        <Link className="rule-row" href={`/rules/${node.article_num}`} key={node.id}>
          <span className="rule-number">{node.article_title}</span>
          <span className="rule-title">{node.caption || "題名なし"}</span>
          <span className="rule-status">取込済み・確認待ち</span>
        </Link>
      ))}
    </div>
  );
}

export default function RulesPage() {
  const revision = meta.current_revision || {};
  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">ORDINANCE DATABASE</p>
      <h1>通所介護の基準省令DB</h1>
      <p className="lead">
        「指定居宅サービス等の事業の人員、設備及び運営に関する基準」から、
        通所介護の直接規定と第105条で準用される共通規定を、条・項・号単位で構造化しています。
      </p>

      <div className="notice">
        <strong>現在は「機械取込済み・人手確認待ち」です。</strong><br />
        e-Govの現行法令XMLから生成し、構造・参照整合は自動検査していますが、
        全182ノードの人手照合はまだ完了していません。
      </div>

      <VerificationSummary layerId="ordinance37" />

      <section className="rules-stats" aria-label="基準DBの収載状況">
        <div><strong>{meta.counts.nodes_total}</strong><span>ノード</span></div>
        <div><strong>{meta.counts.articles_total}</strong><span>対象条文</span></div>
        <div><strong>{meta.counts.direct_articles}</strong><span>直接規定</span></div>
        <div><strong>{meta.counts.incorporated_articles}</strong><span>準用規定</span></div>
      </section>

      <section className="section">
        <h2>人手チェック状況</h2>
        <p>
          確認済み：
          <strong>{(review.reviewed_articles || []).length} / {meta.counts.articles_total}条</strong>
        </p>
        <p className="meta">
          確認結果は生成データとは別のレビュー台帳に保存します。
          確認済み条文の本文SHA-256がe-Gov再取得後に変わった場合、データ検証を失敗させて再確認を要求します。
        </p>
      </section>

      <section className="section">
        <h2>現在の取得元</h2>
        <dl className="rule-meta">
          <div><dt>法令</dt><dd>{meta.law_title}</dd></div>
          <div><dt>現行改正</dt><dd>{revision.amendment_law_num || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
          <div><dt>e-Gov状態</dt><dd>{revision.current_revision_status || "—"}</dd></div>
        </dl>
        <p><a href={meta.source_page} target="_blank" rel="noreferrer">e-Gov法令検索で原文を確認</a></p>
      </section>

      <section className="section">
        <p className="eyebrow">DIRECT RULES</p>
        <h2>通所介護の直接規定</h2>
        <p>第92条から第105条までのうち、指定通所介護本体に適用される17条です。</p>
        <ArticleList items={direct} />
      </section>

      <section className="section">
        <p className="eyebrow">INCORPORATED RULES</p>
        <h2>第105条で準用される共通規定</h2>
        <p>
          訪問介護の章などに置かれている規定のうち、第105条によって通所介護にも適用される23条です。
          一部は「訪問介護員等」を「通所介護従業者」と読むなどの読替えがあります。
        </p>
        <ArticleList items={incorporated} />
      </section>

      <section className="section">
        <h2>今回の初期スコープ外</h2>
        <p>
          共生型通所介護（第105条の2・第105条の3）と基準該当通所介護（第106条〜第109条）は、
          指定通所介護本体と混同しないよう、初期DBから分離しています。
        </p>
      </section>
    </article>
  );
}
