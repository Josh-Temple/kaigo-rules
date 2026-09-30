import Link from "next/link";
import { notFound } from "next/navigation";
import VerificationSummary from "../../../../../components/verification-summary";
import nodesData from "../../../../../data/ordinance37-nodes.json";
import metaData from "../../../../../data/ordinance37-meta.json";
import {
  filterRecordsForService,
  findRecordForService,
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
  p: 0,
  i: 1,
  s1: 2,
  s2: 3,
  s3: 4,
  s4: 5,
  s5: 6,
  s6: 7,
  s7: 8,
  s8: 9,
  s9: 10,
  s10: 11,
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

export default async function DayrehabRuleArticlePage({
  params,
}: {
  params: Promise<{ article: string }>;
}) {
  const { article } = await params;
  const articleNode = findRecordForService(
    "dayrehab",
    "ordinance37",
    nodes,
    (node) => node.id,
    (node) => node.node_type === "article" && node.article_num === article,
  );
  if (!articleNode) notFound();

  const children = filterRecordsForService(
    "dayrehab",
    "ordinance37",
    nodes.filter(
      (node) => node.article_num === article && node.node_type !== "article",
    ),
    (node) => node.id,
  ).sort(compareNodes);

  const revision = meta.current_revision || {};

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">通所リハビリテーション / {articleNode.path[1] || "第八章"}</p>
      <h1>{articleNode.article_title} {articleNode.caption || ""}</h1>
      <p className="meta">{articleNode.path.join(" ＞ ")}</p>

      <div className="notice">
        <strong>e-Gov本文・構造を独立再照合済み</strong><br />
        共有コーパスへ取り込んだ本文を、別のXMLパーサでlive e-Govから再構成して一致を確認しています。人手確認はまだ実施していません。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab" />

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
          <p className="law-text">{articleNode.official_text}</p>
        )}
      </section>

      {article === "119" ? (
        <section className="section">
          <h2>準用規定について</h2>
          <p>
            第119条は他章の規定を通所リハビリテーションへ準用する条文です。このページでは第119条自体のe-Gov本文を表示しています。
            準用先の各条文を通所リハの適用規定として展開するrelationは、明示的な検証が完了したものから別途接続します。
          </p>
        </section>
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
