import Link from "next/link";
import relationshipsData from "../data/relationships.json";
import ruleNodesData from "../data/rule-nodes.json";
import noticeNodesData from "../data/notice-nodes.json";
import qaItemsData from "../data/qa-items.json";
import feeNodesData from "../data/remuneration-current-skeleton.json";
import { expandQuestionAuthorities } from "../lib/question-authority-expansion";
import { feeHref } from "../lib/service-catalog";

const relationships = relationshipsData as Array<any>;
const ruleNodes = ruleNodesData as Array<any>;
const noticeNodes = noticeNodesData as Array<any>;
const qaItems = qaItemsData as Array<any>;
const feeNodes = feeNodesData as Array<any>;

const kindLabel: Record<string, string> = {
  standard: "基準省令",
  notice: "解釈通知",
  qa: "国Q&A",
  fee: "報酬告示",
};

const ruleHref = (id: string) => {
  const match = id.match(/^ordinance37\.article([0-9-]+)/);
  return match ? `/rules/${match[1]}` : null;
};

const qaHref = (item: any) => {
  const query = item.source_number || item.topic?.[0] || item.question_summary || "";
  return `/qa?q=${encodeURIComponent(query)}&service=16`;
};

const authorityHref = (kind: string, record: any, serviceId: string) => {
  if (kind === "standard") return ruleHref(record.id);
  if (kind === "notice") return "/notices";
  if (kind === "qa") return qaHref(record);
  if (kind === "fee") return feeHref(serviceId, record.id);
  return null;
};

const authorityTitle = (kind: string, record: any) => {
  if (kind === "standard") return (record.path || []).join(" ＞ ") || record.id;
  if (kind === "notice") return (record.path || []).join(" ＞ ") || record.document || record.id;
  if (kind === "qa") {
    return [record.source_document, record.source_number].filter(Boolean).join(" / ") || record.id;
  }
  if (kind === "fee") return record.title || record.id;
  return record.id;
};

export default function QuestionAuthorityPanel({
  questions,
  serviceId,
}: {
  questions: Array<any>;
  serviceId: string;
}) {
  const groups = expandQuestionAuthorities({
    questions,
    relations: relationships,
    rules: ruleNodes,
    notices: noticeNodes,
    qaItems,
    feeNodes: feeNodes.filter((node) => node.service_scope === "通所介護"),
  });

  if (!groups.length) return null;

  return (
    <section className="section">
      <h2>実務FAQからたどれる根拠</h2>
      <p className="meta">
        FAQの検索一致とは別に、既存の明示relationだけを展開しています。
        ここで表示すること自体は、relationの検証状態や各資料の現行性を自動的に引き上げるものではありません。
      </p>
      <div className="source-chain">
        {groups.map((group) => (
          <div className="source-card" key={group.questionSlug}>
            <p>
              <strong>{group.questionTitle}</strong>
            </p>
            <ul className="source-list">
              {group.authorities.map((authority) => {
                const href = authorityHref(authority.kind, authority.record, serviceId);
                const title = authorityTitle(authority.kind, authority.record);
                return (
                  <li key={authority.targetId}>
                    <span className="source-kind">{kindLabel[authority.kind]}</span>{" "}
                    {href ? <Link href={href}>{title}</Link> : title}
                    <span className="meta"> / 明示relation: {authority.relation}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </section>
  );
}
