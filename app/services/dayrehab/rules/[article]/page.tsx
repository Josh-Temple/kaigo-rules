import Link from "next/link";
import { notFound } from "next/navigation";
import VerificationSummary from "../../../../../components/verification-summary";
import nodesData from "../../../../../data/ordinance37-nodes.json";
import metaData from "../../../../../data/ordinance37-meta.json";
import relationData from "../../../../../data/services/dayrehab/ordinance37-relations.generated.json";
import relationAuditData from "../../../../../data/dayrehab-article119-relation-independent-audit.json";
import scopeData from "../../../../../data/services/dayrehab/ordinance37-scope.json";
import {
  filterRecordsForService,
  findRecordForService,
  serviceApplicability,
} from "../../../../../lib/service-scope";

type RuleNode = {
  id: string;
  node_type: "article" | "paragraph" | "item" | "subitem";
  article_num: string;
  paragraph_num?: string;
  item_level?: string;
  item_num?: string;
  article_title?: string;
  caption?: string;
  label?: string;
  path: string[];
  official_text: string;
  text_sha256: string;
  source_url: string;
  source_locator: string;
  parent_id?: string | null;
};

const nodes = nodesData as RuleNode[];
const meta = metaData as any;
const relations = relationData as Array<any>;
const relationAudit = relationAuditData as any;
const scope = scopeData as any;
const dayrehabArticles = filterRecordsForService(
  "dayrehab",
  "ordinance37",
  nodes.filter((node) => node.node_type === "article"),
  (node) => node.id,
);

export function generateStaticParams() {
  return dayrehabArticles.map((node) => ({ article: node.article_num }));
}

const levelRank: Record<string, number> = {
  p: 0, i: 1, s1: 2, s2: 3, s3: 4, s4: 5, s5: 6, s6: 7, s7: 8, s8: 9, s9: 10, s10: 11,
};
function nodeSortKey(node: RuleNode) {
  const prefix = `ordinance37.article.${node.article_num}`;
  const suffix = node.id.slice(prefix.length).split(".").filter(Boolean);
  const key: number[] = [];
  for (let i = 0; i < suffix.length; i += 2) {
    const kind = suffix[i];
    const value = suffix[i + 1] || "0";
    const [major, minor = "0"] = value.split("-");
    key.push(levelRank[kind] ?? 99, Number(major) || 0, Number(minor) || 0);
  }
  return key;
}
function compareNodes(a: RuleNode, b: RuleNode) {
  const ak = nodeSortKey(a); const bk = nodeSortKey(b);
  for (let i = 0; i < Math.max(ak.length, bk.length); i += 1) {
    const diff = (ak[i] ?? -1) - (bk[i] ?? -1);
    if (diff) return diff;
  }
  return 0;
}
function NodeLabel({ node }: { node: RuleNode }) {
  if (node.node_type === "paragraph") return <span>第{node.paragraph_num}項</span>;
  return <span>{node.label || node.item_num}</span>;
}

export default async function DayrehabRuleArticlePage({ params }: { params: Promise<{ article: string }> }) {
  const { article } = await params;
  const articleNode = findRecordForService(
    "dayrehab", "ordinance37", nodes, (node) => node.id,
    (node) => node.node_type === "article" && node.article_num === article,
  );
  if (!articleNode) notFound();

  const decision = serviceApplicability("dayrehab", "ordinance37", articleNode.id);
  const isDirect = decision.basis === "DIRECT_SCOPE";
  const isIncorporated = decision.basis === "INCORPORATED_SCOPE";
  const children = filterRecordsForService(
    "dayrehab", "ordinance37",
    nodes.filter((node) => node.article_num === article && node.node_type !== "article"),
    (node) => node.id,
  ).sort(compareNodes);
  const revision = meta.current_revision || {};
  const incorporationTargets = article === "119" ? relations : [];

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">
        通所リハビリテーション / {isDirect ? "第八章・直接規定" : "第119条・準用規定"}
      </p>
      <h1>{articleNode.article_title} {articleNode.caption || ""}</h1>
      <p className="meta">{articleNode.path.join(" ＞ ")}</p>

      {isDirect ? (
        <>
          <div className="notice">
            <strong>e-Gov本文・構造を独立再照合済み</strong><br />
            第八章の直接規定として、共有コーパス本文を別XMLパーサでlive e-Govから再構成して一致を確認しています。人手確認は未実施です。
          </div>
          <VerificationSummary layerId="ordinance37-dayrehab" />
        </>
      ) : (
        <>
          <div className="notice">
            <strong>第119条による準用関係を独立監査済み</strong><br />
            この条文本文は共有省令37号コーパスから表示し、通所リハへの適用根拠は現行e-Gov第119条から独立抽出した25件のrelationで確認しています。
            relation PASSは人手による法解釈確認を意味しません。
          </div>
          <VerificationSummary layerId="ordinance37" />
          <section className="rule-application-note">
            <strong>通所リハへの適用：</strong>
            <Link href="/services/dayrehab/rules/119">第119条</Link>による準用。
            relation audit: {relationAudit.audit_result}
          </section>
        </>
      )}

      <section className="section">
        <h2>条文</h2>
        {children.length ? (
          <div className="rule-tree">
            {children.map((node) => (
              <section className={`rule-node rule-node-${node.node_type}`} key={node.id}>
                <p className="rule-node-label"><NodeLabel node={node} /></p>
                <p>{node.official_text}</p>
                <p className="meta">{node.id}</p>
              </section>
            ))}
          </div>
        ) : <p className="law-text">{articleNode.official_text}</p>}
      </section>

      {article === "119" ? (
        <>
          <section className="section">
            <h2>現行の準用先</h2>
            <p>
              live e-Gov第119条から独立parserで抽出した25条と、canonical relation 25件が一致しています。
              旧HTML解釈通知の準用リストはこの現行scopeの根拠に使っていません。
            </p>
            <div className="rules-list">
              {incorporationTargets.map((relation: any) => {
                const target = nodes.find((node) => node.id === relation.to);
                const number = String(relation.to).replace("ordinance37.article.", "");
                return target ? (
                  <Link className="rule-row" href={`/services/dayrehab/rules/${number}`} key={relation.to}>
                    <span className="rule-number">{target.article_title}</span>
                    <span className="rule-title">{target.caption || "題名なし"}</span>
                    <span className="rule-status">準用relation・独立監査済み</span>
                  </Link>
                ) : (
                  <a className="rule-row" href={meta.source_page} target="_blank" rel="noreferrer" key={relation.to}>
                    <span className="rule-number">第{number}条</span>
                    <span className="rule-title">共有コーパス未収載</span>
                    <span className="rule-status">e-Gov原文へ</span>
                  </a>
                );
              })}
            </div>
          </section>
          <section className="section">
            <h2>第119条の読み替え</h2>
            {scope.incorporated_scope.read_as_rules.map((rule: any, index: number) => (
              <div className="read-as-rule" key={index}>
                <p className="meta">
                  対象：
                  {rule.scope === "all_incorporated_provisions_where_term_occurs"
                    ? "準用規定中の該当語"
                    : `第${rule.target_article}条${rule.target_paragraph ? `第${rule.target_paragraph}項` : ""}${rule.target_paragraphs ? `第${rule.target_paragraphs.join("・")}項` : ""}`}
                </p>
                {rule.substitutions.map((item: any) => (
                  <p key={item.from}><code>{item.from}</code> → <code>{item.to}</code></p>
                ))}
              </div>
            ))}
          </section>
        </>
      ) : null}

      <section className="section">
        <h2>出典・版</h2>
        <dl className="rule-meta">
          <div><dt>取得元</dt><dd>e-Gov法令API / e-Gov法令検索</dd></div>
          <div><dt>revision</dt><dd>{revision.law_revision_id || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
          <div><dt>e-Gov状態</dt><dd>{revision.current_revision_status || "—"}</dd></div>
          <div><dt>本文SHA-256</dt><dd className="hash">{articleNode.text_sha256}</dd></div>
        </dl>
        <p><a href={articleNode.source_url} target="_blank" rel="noreferrer">e-Govで原文を確認</a></p>
        <p className="meta">{articleNode.source_locator}</p>
      </section>
      <p><Link href="/services/dayrehab/rules">基準省令一覧へ戻る</Link></p>
    </article>
  );
}
