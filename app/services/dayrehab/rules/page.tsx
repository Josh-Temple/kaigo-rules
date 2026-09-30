import Link from "next/link";
import VerificationSummary from "../../../../components/verification-summary";
import nodesData from "../../../../data/ordinance37-nodes.json";
import metaData from "../../../../data/ordinance37-meta.json";
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
const articles = filterRecordsForService(
  "dayrehab",
  "ordinance37",
  nodes.filter((node) => node.node_type === "article"),
  (node) => node.id,
);

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
        第八章「通所リハビリテーション」の第110条から第119条までを、e-Gov法令XMLから条・項・号単位で構造化しています。
      </p>

      <div className="notice">
        <strong>本文・構造は独立再照合済みです。</strong><br />
        共有コーパスとは別のXMLパーサでlive e-Govから第八章を再構成し、{articles.length}条の本文・node構造・包含関係が一致することを確認しました。人手確認とは別の状態です。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab" />

      <section className="rules-stats" aria-label="基準省令DBの状態">
        <div><strong>{articles.length}</strong><span>対象条文</span></div>
        <div><strong>{articles.length}</strong><span>独立再照合済み</span></div>
        <div><strong>0</strong><span>人手確認済み</span></div>
        <div><strong>{meta.counts.nodes_total}</strong><span>共有コーパスノード</span></div>
      </section>

      {sectionOrder.map((section) => {
        const items = articles.filter((item) => sectionOf(item) === section);
        if (!items.length) return null;
        return (
          <section className="section" key={section}>
            <h2>{section}</h2>
            <div className="rules-list">
              {items.map((item) => (
                <Link
                  className="rule-row"
                  href={`/services/dayrehab/rules/${item.article_num}`}
                  key={item.id}
                >
                  <span className="rule-number">{item.article_title}</span>
                  <span className="rule-title">{item.caption || "題名なし"}</span>
                  <span className="rule-status">
                    {serviceApplicability("dayrehab", "ordinance37", item.id).basis === "DIRECT_SCOPE"
                      ? "第八章・直接規定"
                      : "scope確認待ち"}
                  </span>
                </Link>
              ))}
            </div>
          </section>
        );
      })}

      <section className="section">
        <h2>取得元・版</h2>
        <dl className="rule-meta">
          <div><dt>法令</dt><dd>{meta.law_title}</dd></div>
          <div><dt>e-Gov revision</dt><dd>{revision.law_revision_id || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
          <div><dt>e-Gov状態</dt><dd>{revision.current_revision_status || "—"}</dd></div>
        </dl>
        <p><a href={meta.source_page} target="_blank" rel="noreferrer">e-Gov法令検索で原文を確認</a></p>
        <p className="meta">第119条が準用する他章規定の展開は、別のrelation検証工程で扱います。</p>
      </section>

      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
