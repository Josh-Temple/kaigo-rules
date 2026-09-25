import VerificationSummary from "../../../components/verification-summary";
import Link from "next/link";
import { notFound } from "next/navigation";
import nodesData from "../../../data/ordinance37-nodes.json";
import relationsData from "../../../data/ordinance37-relations.json";
import applicationData from "../../../data/ordinance37-application-rules.json";
import metaData from "../../../data/ordinance37-meta.json";
import noticeNodesData from "../../../data/notice-current-skeleton.json";
import feeNodesData from "../../../data/remuneration-current-skeleton.json";
import questionsData from "../../../data/questions.json";
import careActNodesData from "../../../data/care-insurance-act-nodes.json";
import { incomingEdges } from "../../../lib/knowledge-relations";

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
  service_scope: string;
  applicable_via?: string | null;
  source_url: string;
  source_locator: string;
  verification_status: string;
  parent_id?: string | null;
};

const nodes = nodesData as RuleNode[];
const relations = relationsData as Array<{ from: string; relation: string; to: string }>;
const applications = applicationData as Array<any>;
const meta = metaData as any;
const noticeNodes = noticeNodesData as Array<any>;
const feeNodes = feeNodesData as Array<any>;
const questions = questionsData as Array<any>;
const careActNodes = careActNodesData as Array<any>;

export function generateStaticParams() {
  return nodes
    .filter((node) => node.node_type === "article")
    .map((node) => ({ article: node.article_num }));
}

const levelRank: Record<string, number> = { p: 0, i: 1, s1: 2, s2: 3, s3: 4, s4: 5, s5: 6 };

function nodeSortKey(node: RuleNode) {
  const prefix = `ordinance37.article.${node.article_num}`;
  const suffix = node.id.slice(prefix.length).split(".").filter(Boolean);
  const key: number[] = [];
  for (let i = 0; i < suffix.length; i += 2) {
    const kind = suffix[i];
    const value = suffix[i + 1] || "0";
    const [major, minor = "0"] = value.split("-");
    key.push(levelRank[kind] ?? 9, Number(major) || 0, Number(minor) || 0);
  }
  return key;
}

function compareNodes(a: RuleNode, b: RuleNode) {
  const ak = nodeSortKey(a);
  const bk = nodeSortKey(b);
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

export default async function RuleArticlePage({ params }: { params: Promise<{ article: string }> }) {
  const { article } = await params;
  const articleNode = nodes.find(
    (node) => node.node_type === "article" && node.article_num === article
  );
  if (!articleNode) notFound();

  const children = nodes
    .filter((node) => node.article_num === article && node.node_type !== "article")
    .sort(compareNodes);

  const incorporationTargets = relations
    .filter((relation) => relation.from === articleNode.id && relation.relation === "incorporates_by_reference")
    .map((relation) => nodes.find((node) => node.id === relation.to))
    .filter(Boolean) as RuleNode[];

  const readAs = applications.filter((rule) => rule.target_article_id === articleNode.id);
  const relationEdges = incomingEdges(articleNode.id);
  const relatedNotices = relationEdges
    .filter((edge) => edge.source_id.startsWith("notice."))
    .map((edge) => ({ edge, node: noticeNodes.find((item) => item.id === edge.source_id) }))
    .filter((item) => item.node);
  const relatedFees = relationEdges
    .filter((edge) => edge.source_id.startsWith("fee.dayservice."))
    .map((edge) => ({ edge, node: feeNodes.find((item) => item.id === edge.source_id) }))
    .filter((item) => item.node);
  const relatedQuestions = relationEdges
    .filter((edge) => edge.source_id.startsWith("question:"))
    .map((edge) => ({
      edge,
      question: questions.find((item) => `question:${item.slug}` === edge.source_id),
    }))
    .filter((item) => item.question);
  const relatedLaw = relationEdges
    .filter((edge) => edge.source_id.startsWith("careact.article."))
    .map((edge) => ({
      edge,
      node: careActNodes.find((item) => item.id === edge.source_id),
    }))
    .filter((item) => item.node);

  const revision = meta.current_revision || {};

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">{articleNode.service_scope}</p>
      <h1>{articleNode.article_title} {articleNode.caption || ""}</h1>
      <p className="meta">{articleNode.path.join(" ＞ ")}</p>

      <div className="notice">
        <strong>取込済み・人手確認待ち</strong><br />
        e-Gov現行XMLから取得した本文です。構造検証は済んでいますが、この条文を人手で原文照合したという意味ではありません。
      </div>

      <VerificationSummary layerId="ordinance37" />

      {articleNode.applicable_via ? (
        <section className="rule-application-note">
          <strong>通所介護への適用：</strong>
          <Link href="/rules/105">第105条</Link>により準用される規定です。
        </section>
      ) : null}

      {readAs.length ? (
        <section className="section">
          <h2>第105条による読替え</h2>
          {readAs.map((rule) => (
            <div className="read-as-rule" key={rule.id}>
              <p className="meta">
                対象：
                {rule.target_paragraph ? `第${rule.target_paragraph}項` : "条全体"}
                {rule.target_item ? ` / 第${rule.target_item.join("・")}号` : ""}
              </p>
              {rule.substitutions.map((item: any) => (
                <p key={item.from}><code>{item.from}</code> → <code>{item.to}</code></p>
              ))}
            </div>
          ))}
        </section>
      ) : null}

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
        ) : (
          <p>{articleNode.official_text}</p>
        )}
      </section>

      {incorporationTargets.length ? (
        <section className="section">
          <h2>この条文から準用される規定</h2>
          <div className="rules-list">
            {incorporationTargets.map((target) => (
              <Link className="rule-row" href={`/rules/${target.article_num}`} key={target.id}>
                <span className="rule-number">{target.article_title}</span>
                <span className="rule-title">{target.caption || "題名なし"}</span>
                <span className="rule-status">第105条で準用</span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      {(relatedLaw.length || relatedNotices.length || relatedFees.length || relatedQuestions.length) ? (
        <section className="section">
          <h2>この条文につながる情報</h2>
          <p className="meta">
            relationデータから逆引きしています。独立監査済みの関係と、構造上の対応付けで確認待ちの関係を区別して表示します。
          </p>
          <div className="knowledge-link-list">
            {relatedLaw.map(({ edge, node }: any) => (
              <Link className="knowledge-link-row" href={`/law/${node.article_num}`} key={`law-${edge.source_id}-${edge.relation}`}>
                <span className="knowledge-kind">上位法</span>
                <span><strong>{node.article_title} {node.caption || ""}</strong><small>介護保険法からこの基準への委任関係</small></span>
                <span className={edge.independent_verification.status === "PASS" ? "knowledge-status verified" : "knowledge-status"}>{edge.independent_verification.status === "PASS" ? "独立監査済み" : "関係付け確認待ち"}</span>
              </Link>
            ))}
            {relatedNotices.map(({ edge, node }: any) => (
              <Link className="knowledge-link-row" href={`/notices#${node.id}`} key={`notice-${edge.source_id}-${edge.relation}`}>
                <span className="knowledge-kind">解釈通知</span>
                <span><strong>{node.title}</strong><small>{node.number_path?.join(" / ")}</small></span>
                <span className={edge.independent_verification.status === "PASS" ? "knowledge-status verified" : "knowledge-status"}>{edge.independent_verification.status === "PASS" ? "独立監査済み" : "関係付け確認待ち"}</span>
              </Link>
            ))}
            {relatedFees.map(({ edge, node }: any) => (
              <Link className="knowledge-link-row" href={`/fees/${node.id.replace("fee.dayservice.", "")}`} key={`fee-${edge.source_id}-${edge.relation}`}>
                <span className="knowledge-kind">報酬</span>
                <span><strong>{node.title}</strong><small>{node.number_path?.join(" / ")}</small></span>
                <span className={edge.independent_verification.status === "PASS" ? "knowledge-status verified" : "knowledge-status"}>{edge.independent_verification.status === "PASS" ? "独立監査済み" : "関係付け確認待ち"}</span>
              </Link>
            ))}
            {relatedQuestions.map(({ edge, question }: any) => (
              <Link className="knowledge-link-row" href={`/questions/${question.slug}`} key={`question-${edge.source_id}-${edge.relation}`}>
                <span className="knowledge-kind">実務FAQ</span>
                <span><strong>{question.title}</strong><small>{question.category}</small></span>
                <span className="knowledge-status">{question.status === "verified" ? "FAQ根拠確認済み" : "根拠確認中"}</span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      <section className="section">
        <h2>出典・版</h2>
        <dl className="rule-meta">
          <div><dt>取得元</dt><dd>e-Gov法令API / e-Gov法令検索</dd></div>
          <div><dt>現行改正</dt><dd>{revision.amendment_law_num || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
          <div><dt>本文SHA-256</dt><dd className="hash">{articleNode.text_sha256}</dd></div>
        </dl>
        <p><a href={articleNode.source_url} target="_blank" rel="noreferrer">e-Govで原文を確認</a></p>
      </section>

      <p><Link href="/rules">基準DB一覧へ戻る</Link></p>
    </article>
  );
}
