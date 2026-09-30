import Link from "next/link";
import VerificationSummary from "../../../../components/verification-summary";
import nodesData from "../../../../data/ordinance37-nodes.json";
import metaData from "../../../../data/ordinance37-meta.json";
import relationData from "../../../../data/services/dayrehab/ordinance37-relations.generated.json";
import relationAuditData from "../../../../data/dayrehab-article119-relation-independent-audit.json";
import {
  filterRecordsForService,
  serviceApplicability,
} from "../../../../lib/service-scope";

type RuleNode = {
  id: string;
  node_type: string;
  article_num: string;
  article_title?: string;
  caption?: string;
  path: string[];
  source_url: string;
};

const nodes = nodesData as RuleNode[];
const meta = metaData as any;
const relations = relationData as Array<any>;
const relationAudit = relationAuditData as any;
const articles = filterRecordsForService(
  "dayrehab",
  "ordinance37",
  nodes.filter((node) => node.node_type === "article"),
  (node) => node.id,
);
const directArticles = articles.filter(
  (item) => serviceApplicability("dayrehab", "ordinance37", item.id).basis === "DIRECT_SCOPE",
);
const incorporatedArticles = articles.filter(
  (item) => serviceApplicability("dayrehab", "ordinance37", item.id).basis === "INCORPORATED_SCOPE",
);
const targetIds = relations.map((relation) => relation.to);
const missingTargets = targetIds.filter((id) => !nodes.some((node) => node.id === id));

const sectionOrder = [
  "第一節 基本方針",
  "第二節 人員に関する基準",
  "第三節 設備に関する基準",
  "第四節 運営に関する基準",
];
const sectionOf = (node: RuleNode) =>
  node.path.find((part) => /^第.+節/.test(part)) || "章内規定";

export default function DayrehabRulesPage() {
  const revision = meta.current_revision || {};
  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">DAY REHABILITATION / ORDINANCE DATABASE</p>
      <h1>通所リハビリテーションの基準省令</h1>
      <p className="lead">
        第八章の直接規定11条と、第119条が現行e-Gov本文で明示的に準用する25条を分離して表示します。
      </p>

      <div className="notice">
        <strong>直接本文と準用関係を別々に検証しています。</strong><br />
        第八章11条の本文・構造は独立再照合済みです。第119条の25の準用先は別parserでlive e-Govから抽出し、canonical relationと一致することを確認しています。
        準用先のうち共有コーパスに本文がある{incorporatedArticles.length}条はローカル閲覧でき、未収載の{missingTargets.length}条は本文を生成しません。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab" />

      <section className="rules-stats" aria-label="基準省令DBの状態">
        <div><strong>{directArticles.length}</strong><span>第八章・直接規定</span></div>
        <div><strong>{relations.length}</strong><span>第119条・準用relation</span></div>
        <div><strong>{incorporatedArticles.length}</strong><span>準用先・本文参照可</span></div>
        <div><strong>{relationAudit.audit_result}</strong><span>relation独立監査</span></div>
      </section>

      {sectionOrder.map((section) => {
        const items = directArticles.filter((item) => sectionOf(item) === section);
        if (!items.length) return null;
        return (
          <section className="section" key={section}>
            <h2>{section}</h2>
            <div className="rules-list">
              {items.map((item) => (
                <Link className="rule-row" href={`/services/dayrehab/rules/${item.article_num}`} key={item.id}>
                  <span className="rule-number">{item.article_title}</span>
                  <span className="rule-title">{item.caption || "題名なし"}</span>
                  <span className="rule-status">第八章・直接規定</span>
                </Link>
              ))}
            </div>
          </section>
        );
      })}

      <section className="section">
        <h2>第119条で準用される規定</h2>
        <p className="meta">
          現行e-Gov第119条の明示参照だけをrelation化しています。旧HTML解釈通知の古い準用リストから補完していません。
        </p>
        <div className="rules-list">
          {relations.map((relation) => {
            const target = nodes.find((node) => node.id === relation.to);
            const article = String(relation.to).replace("ordinance37.article.", "");
            return target ? (
              <Link className="rule-row" href={`/services/dayrehab/rules/${article}`} key={relation.to}>
                <span className="rule-number">{target.article_title}</span>
                <span className="rule-title">{target.caption || "題名なし"}</span>
                <span className="rule-status">第119条準用・独立監査済み</span>
              </Link>
            ) : (
              <a className="rule-row" href={meta.source_page} target="_blank" rel="noreferrer" key={relation.to}>
                <span className="rule-number">第{article}条</span>
                <span className="rule-title">共有コーパス未収載</span>
                <span className="rule-status">e-Gov原文へ</span>
              </a>
            );
          })}
        </div>
      </section>

      <section className="section">
        <h2>取得元・版</h2>
        <dl className="rule-meta">
          <div><dt>法令</dt><dd>{meta.law_title}</dd></div>
          <div><dt>e-Gov revision</dt><dd>{revision.law_revision_id || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
          <div><dt>e-Gov状態</dt><dd>{revision.current_revision_status || "—"}</dd></div>
        </dl>
        <p><a href={meta.source_page} target="_blank" rel="noreferrer">e-Gov法令検索で原文を確認</a></p>
      </section>
      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
