import VerificationSummary from "../../../components/verification-summary";
import ServiceContextLinks from "../../../components/service-context-links";
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
import { listServices } from "../../../lib/service-catalog";
import {
  PROGRESSIVE_SOURCE_FAMILY,
  filterProgressivePublishedRules,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  isProgressiveRouteCell,
  isProgressiveRulePublished,
  listProgressivePublicationServices,
  progressiveServicesForRule,
} from "../../../lib/publication-policy";
import {
  filterRecordsForService,
  isRecordApplicableToService,
  resolveServiceScope,
  serviceApplicability,
} from "../../../lib/service-scope";
import { verifiedRelatedPrimarySources } from "../../../lib/verified-related-sources";

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
const relations = relationsData as Array<{ from: string; relation: string; to: string }>;
const applications = applicationData as Array<any>;
const meta = metaData as any;
const noticeNodes = noticeNodesData as Array<any>;
const feeNodes = feeNodesData as Array<any>;
const questions = questionsData as Array<any>;
const careActNodes = careActNodesData as Array<any>;

const catalogServices = listServices();
const legacyPublicFilterServices = catalogServices.filter(
  (service) =>
    service.routing.current_mode === "LEGACY_ROOT" ||
    service.routing.future_service_base_enabled,
);
const progressivePublicFilterServices = listProgressivePublicationServices();
const publicFilterServices = [
  ...legacyPublicFilterServices,
  ...progressivePublicFilterServices.filter(
    (service) =>
      !legacyPublicFilterServices.some(
        (legacy) => legacy.service_id === service.service_id,
      ),
  ),
];
const publicFilterIds = new Set(publicFilterServices.map((service) => service.service_id));
const serviceById = new Map(
  catalogServices.map((service) => [service.service_id, service]),
);

export function generateStaticParams() {
  const publicArticleNumbers = new Set(
    [
      ...nodes,
      ...listProgressivePublicationServices().flatMap((service) =>
        getProgressiveSourceRecords(service.service_id),
      ),
    ]
      .filter((node) => node.node_type === "article")
      .map((node) => node.article_num),
  );
  return [...publicArticleNumbers].map((article) => ({ article }));
}

const levelRank: Record<string, number> = {
  p: 0, i: 1, s1: 2, s2: 3, s3: 4, s4: 5, s5: 6, s6: 7, s7: 8,
};

function nodeSortKey(node: RuleNode) {
  const marker = `.article.${node.article_num}`;
  const markerIndex = node.id.indexOf(marker);
  const suffix = (
    markerIndex >= 0
      ? node.id.slice(markerIndex + marker.length)
      : node.id
  ).split(".").filter(Boolean);
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

function basisLabel(basis: string) {
  if (basis === "DIRECT_SCOPE") return "直接規定";
  if (basis === "INCORPORATED_SCOPE") return "準用";
  return "適用scope";
}

export default async function RuleArticlePage({
  params,
  searchParams,
}: {
  params: Promise<{ article: string }>;
  searchParams: Promise<{ service?: string }>;
}) {
  const { article } = await params;
  const { service = "" } = await searchParams;

  const selectedService = publicFilterServices.find(
    (item) => item.service_id === service,
  );
  const selectedServiceId = selectedService?.service_id;
  const progressiveSelection = Boolean(
    selectedServiceId && isProgressiveRouteCell(selectedServiceId),
  );
  const sourceNodes =
    progressiveSelection && selectedServiceId
      ? (getProgressiveSourceRecords(selectedServiceId) as RuleNode[])
      : nodes;

  const articleNode = sourceNodes.find(
    (node) => node.node_type === "article" && node.article_num === article,
  );
  if (!articleNode) notFound();

  if (
    selectedServiceId &&
    !(
      progressiveSelection
        ? isProgressiveRulePublished(selectedServiceId, articleNode.id)
        : isRecordApplicableToService(
            selectedServiceId,
            "ordinance37",
            articleNode.id,
          )
    )
  ) {
    notFound();
  }

  const articleNodes = sourceNodes.filter(
    (node) => node.article_num === article && node.node_type !== "article",
  );
  const children = (
    selectedServiceId
      ? progressiveSelection
        ? filterProgressivePublishedRules(
            selectedServiceId,
            articleNodes,
            (node) => node.id,
          )
        : filterRecordsForService(
            selectedServiceId,
            "ordinance37",
            articleNodes,
            (node) => node.id,
          )
      : articleNodes
  ).sort(compareNodes);

  const scope = progressiveSelection
    ? { memberships: [] as Array<{ service_id: string; basis: string }> }
    : resolveServiceScope("ordinance37", articleNode.id);
  const publicMemberships = scope.memberships.filter((membership) =>
    publicFilterIds.has(membership.service_id),
  );
  const progressiveMemberships = progressiveServicesForRule(articleNode.id).map(
    (service) => ({
      service_id: service.service_id,
      basis: "DIRECT_SCOPE" as const,
    }),
  );
  const displayMemberships = [
    ...publicMemberships,
    ...progressiveMemberships.filter(
      (membership) =>
        !publicMemberships.some(
          (existing) => existing.service_id === membership.service_id,
        ),
    ),
  ];

  const selectedDecision = selectedServiceId
    ? progressiveSelection
      ? { applicable: true, basis: "DIRECT_SCOPE" as const }
      : serviceApplicability(
          selectedServiceId,
          "ordinance37",
          articleNode.id,
        )
    : undefined;

  const dayserviceContext = !selectedServiceId || selectedServiceId === "dayservice";
  const dayserviceApplicable =
    !progressiveSelection &&
    isRecordApplicableToService(
      "dayservice",
      "ordinance37",
      articleNode.id,
    );

  const incorporationTargets =
    selectedServiceId === "dayservice"
      ? filterRecordsForService(
          "dayservice",
          "ordinance37",
          relations
            .filter(
              (relation) =>
                relation.from === articleNode.id &&
                relation.relation === "incorporates_by_reference",
            )
            .map((relation) => nodes.find((node) => node.id === relation.to))
            .filter(Boolean) as RuleNode[],
          (node) => node.id,
        )
      : [];

  const readAs =
    selectedServiceId === "dayservice"
      ? applications.filter((rule) => rule.target_article_id === articleNode.id)
      : [];

  const relationEdges = dayserviceContext && dayserviceApplicable
    ? incomingEdges(articleNode.id).filter(
        (edge) =>
          edge.independent_verification.status === "PASS",
      )
    : [];

  const verifiedRelatedSources =
    progressiveSelection && selectedServiceId
      ? verifiedRelatedPrimarySources(
          selectedServiceId,
          PROGRESSIVE_SOURCE_FAMILY,
          articleNode,
        )
      : [];

  const relatedNotices = relationEdges
    .filter((edge) => edge.source_id.startsWith("notice."))
    .map((edge) => ({
      edge,
      node: noticeNodes.find((item) => item.id === edge.source_id),
    }))
    .filter((item) => item.node);

  const relatedFees = relationEdges
    .filter((edge) => edge.source_id.startsWith("fee.dayservice."))
    .map((edge) => ({
      edge,
      node: feeNodes.find((item) => item.id === edge.source_id),
    }))
    .filter((item) => item.node);

  const relatedQuestions = relationEdges
    .filter((edge) => edge.source_id.startsWith("question:"))
    .map((edge) => ({
      edge,
      question: questions.find(
        (item) => `question:${item.slug}` === edge.source_id,
      ),
    }))
    .filter((item) => item.question);

  const relatedLaw = relationEdges
    .filter((edge) => edge.source_id.startsWith("careact.article."))
    .map((edge) => ({
      edge,
      node: careActNodes.find((item) => item.id === edge.source_id),
    }))
    .filter(
      (item) =>
        item.node &&
        isRecordApplicableToService(
          "dayservice",
          "care_insurance_act",
          item.node.id,
        ),
    );

  const publicationTrust =
    progressiveSelection && selectedServiceId
      ? getProgressivePublicationTrust(selectedServiceId)
      : null;
  const revision = meta.current_revision || {};
  const verificationLayerId =
    selectedServiceId === "dayrehab" ? "ordinance37-dayrehab" : "ordinance37";
  const backHref = selectedServiceId
    ? `/rules?service=${encodeURIComponent(selectedServiceId)}`
    : "/rules";

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">
        {selectedService
          ? `${selectedService.label} / ORDINANCE DATABASE`
          : "ORDINANCE DATABASE / SHARED CORPUS"}
      </p>
      <h1>{articleNode.article_title} {articleNode.caption || ""}</h1>
      <p className="meta">{articleNode.path.join(" ＞ ")}</p>

      <div className="notice">
        <strong>
          {selectedService
            ? `${selectedService.label}の適用scopeで表示しています。`
            : "共有法令コーパスの条文を表示しています。"}
        </strong><br />
        e-Gov現行XMLから取得した本文です。サービス別表示では、公開条件を満たした範囲だけを表示します。
      </div>

      <nav className="rules-filter" aria-label="この条文をサービス別に見る">
        <Link
          className={!selectedServiceId ? "rules-filter-active" : ""}
          href={`/rules/${article}`}
        >
          すべて
        </Link>
        {displayMemberships.map((membership) => {
          const item = serviceById.get(membership.service_id);
          return (
            <Link
              className={
                selectedServiceId === membership.service_id
                  ? "rules-filter-active"
                  : ""
              }
              href={`/rules/${article}?service=${membership.service_id}`}
              key={membership.service_id}
            >
              {item?.label || membership.service_id}
            </Link>
          );
        })}
      </nav>

      {selectedServiceId === "dayservice" || selectedServiceId === "dayrehab" ? (
        <ServiceContextLinks serviceId={selectedServiceId} />
      ) : null}

      <section className="rule-application-note">
        {selectedService && selectedDecision?.applicable ? (
          <>
            {selectedServiceId === "dayservice" ? (
              <strong>通所介護への適用：</strong>
            ) : selectedServiceId === "dayrehab" ? (
              <strong>通所リハビリテーションへの適用：</strong>
            ) : (
              <strong>選択したサービスへの適用：</strong>
            )}
            {basisLabel(selectedDecision.basis || "")}
            {selectedServiceId === "dayservice" &&
            selectedDecision.basis === "INCORPORATED_SCOPE" ? (
              <>（<Link href="/rules/105?service=dayservice">第105条</Link>による準用）</>
            ) : null}
            {selectedServiceId === "dayrehab" &&
            selectedDecision.basis === "INCORPORATED_SCOPE" ? (
              <>（<Link href="/rules/119?service=dayrehab">第119条</Link>による準用）</>
            ) : null}
          </>
        ) : displayMemberships.length ? (
          <>
            <strong>公開中サービスでの適用：</strong>
            {publicMemberships.map((membership, index) => (
              <span key={membership.service_id}>
                {index ? " / " : ""}
                {serviceById.get(membership.service_id)?.label || membership.service_id}
                ・{basisLabel(membership.basis)}
              </span>
            ))}
          </>
        ) : (
          <>
            <strong>サービス別表示：</strong>
            この条文は共有コーパスに収載されていますが、現在公開中のサービスフィルタには含まれていません。
          </>
        )}
      </section>

      {progressiveSelection ? (
        <div className="notice">
          <strong>現行のe-Gov本文と、このサービスへの直接適用範囲を確認済みです。</strong><br />
          未確認の制度間関係や、複数資料を組み合わせた解釈はこの表示に含めていません。
        </div>
      ) : (
        <VerificationSummary layerId={verificationLayerId} />
      )}

      {selectedServiceId === "dayrehab" ? (
        <p className="scope-note">
          通所リハの準用relation・読み替えを含む詳細表示は
          <Link href={`/services/dayrehab/rules/${article}`}>サービス別ページ</Link>
          でも確認できます。
        </p>
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
              <section
                className={`rule-node rule-node-${node.node_type}`}
                key={node.id}
              >
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
              <Link
                className="rule-row"
                href={`/rules/${target.article_num}?service=dayservice`}
                key={target.id}
              >
                <span className="rule-number">{target.article_title}</span>
                <span className="rule-title">{target.caption || "題名なし"}</span>
                <span className="rule-status">第105条で準用</span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      {verifiedRelatedSources.length ? (
        <section className="section">
          <h2>関連する一次資料</h2>
          <p className="meta">
            独立検証済みの参照関係だけを表示しています。
          </p>
          <div className="knowledge-link-list">
            {verifiedRelatedSources.map((relation) => (
              <Link
                className="knowledge-link-row"
                href={relation.href}
                key={
                  relation.relation_direction +
                  "|" +
                  relation.related_record_id
                }
              >
                <span className="knowledge-kind">
                  一次資料
                </span>
                <span>
                  <strong>{relation.title}</strong>
                  <small>{relation.label}</small>
                </span>
                <span className="knowledge-status verified">
                  参照関係を確認済み
                </span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      {(relatedLaw.length ||
        relatedNotices.length ||
        relatedFees.length ||
        relatedQuestions.length) ? (
        <section className="section">
          <h2>この条文につながる情報</h2>
          <p className="meta">
            独立検証済みの参照関係だけを表示しています。サービスを通所リハで絞り込んだ場合は表示しません。
          </p>
          <div className="knowledge-link-list">
            {relatedLaw.map(({ edge, node }: any) => (
              <Link
                className="knowledge-link-row"
                href={`/law/${node.article_num}`}
                key={`law-${edge.source_id}-${edge.relation}`}
              >
                <span className="knowledge-kind">上位法</span>
                <span><strong>{node.article_title} {node.caption || ""}</strong><small>介護保険法からこの基準への委任関係</small></span>
                <span className={edge.independent_verification.status === "PASS" ? "knowledge-status verified" : "knowledge-status"}>
                  参照関係を確認済み
                </span>
              </Link>
            ))}
            {relatedNotices.map(({ edge, node }: any) => (
              <Link
                className="knowledge-link-row"
                href={`/notices#${node.id}`}
                key={`notice-${edge.source_id}-${edge.relation}`}
              >
                <span className="knowledge-kind">解釈通知</span>
                <span><strong>{node.title}</strong><small>{node.number_path?.join(" / ")}</small></span>
                <span className={edge.independent_verification.status === "PASS" ? "knowledge-status verified" : "knowledge-status"}>
                  参照関係を確認済み
                </span>
              </Link>
            ))}
            {relatedFees.map(({ edge, node }: any) => (
              <Link
                className="knowledge-link-row"
                href={`/fees/${node.id.replace("fee.dayservice.", "")}`}
                key={`fee-${edge.source_id}-${edge.relation}`}
              >
                <span className="knowledge-kind">報酬</span>
                <span><strong>{node.title}</strong><small>{node.number_path?.join(" / ")}</small></span>
                <span className={edge.independent_verification.status === "PASS" ? "knowledge-status verified" : "knowledge-status"}>
                  参照関係を確認済み
                </span>
              </Link>
            ))}
            {relatedQuestions.map(({ edge, question }: any) => (
              <Link
                className="knowledge-link-row"
                href={`/questions/${question.slug}`}
                key={`question-${edge.source_id}-${edge.relation}`}
              >
                <span className="knowledge-kind">実務FAQ</span>
                <span><strong>{question.title}</strong><small>{question.category}</small></span>
                <span className="knowledge-status">
                  {question.status === "verified" ? "FAQ根拠確認済み" : "根拠確認中"}
                </span>
              </Link>
            ))}
          </div>
        </section>
      ) : null}

      {publicationTrust ? (
        <section className="section">
          <h2>出典・確認情報</h2>
          <dl className="rule-meta">
            <div><dt>取得元</dt><dd>{publicationTrust.source_title}</dd></div>
            <div><dt>施行日</dt><dd>{publicationTrust.effective_date || "—"}</dd></div>
            <div><dt>確認日時</dt><dd>{publicationTrust.checked_at || "—"}</dd></div>
          </dl>
          <p>
            <a href={publicationTrust.source_url} target="_blank" rel="noreferrer">
              e-Govで原文を確認
            </a>
          </p>
        </section>
      ) : (
        <section className="section">
          <h2>出典・版</h2>
          <dl className="rule-meta">
            <div><dt>取得元</dt><dd>e-Gov法令API / e-Gov法令検索</dd></div>
            <div><dt>現行改正</dt><dd>{revision.amendment_law_num || "—"}</dd></div>
            <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
            <div><dt>本文SHA-256</dt><dd className="hash">{articleNode.text_sha256}</dd></div>
          </dl>
          <p className="meta">canonical ID: {articleNode.id} / {articleNode.source_locator}</p>
          <p>
            <a
              href={`${articleNode.source_url}#Mp-At_${articleNode.article_num.replaceAll("-", "_")}`}
              target="_blank"
              rel="noreferrer"
            >
              e-Govで原文を確認
            </a>
          </p>
        </section>
      )}

      <p><Link href={backHref}>基準DB一覧へ戻る</Link></p>
    </article>
  );
}
