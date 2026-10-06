import VerificationSummary from "../../components/verification-summary";
import ServiceContextLinks from "../../components/service-context-links";
import Link from "next/link";
import nodesData from "../../data/ordinance37-nodes.json";
import metaData from "../../data/ordinance37-meta.json";
import { listServices } from "../../lib/service-catalog";
import {
  filterProgressivePublishedRules,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  isProgressiveRouteCell,
  listProgressivePublicationServices,
  publicationServicePresentationGroup,
} from "../../lib/publication-policy";
import {
  filterRecordsForService,
  resolveServiceScope,
  serviceApplicability,
} from "../../lib/service-scope";

type RuleNode = {
  id: string;
  node_type: string;
  article_num: string;
  article_title?: string;
  caption?: string;
  path: string[];
  official_text: string;
};

const nodes = nodesData as RuleNode[];
const meta = metaData as any;

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

const articles = nodes
  .filter((node) => node.node_type === "article")
  .sort(compareArticle);

const catalogServices = listServices();
const legacyFilterServices = catalogServices.filter(
  (service) =>
    service.routing.current_mode === "LEGACY_ROOT" ||
    service.routing.future_service_base_enabled,
);
const progressiveFilterServices = listProgressivePublicationServices();
const filterServices = [
  ...legacyFilterServices,
  ...progressiveFilterServices.filter(
    (service) =>
      !legacyFilterServices.some(
        (legacy) => legacy.service_id === service.service_id,
      ),
  ),
].sort((a, b) => {
  const groupA = publicationServicePresentationGroup(a.service_id);
  const groupB = publicationServicePresentationGroup(b.service_id);
  if (groupA !== groupB) return groupA.localeCompare(groupB, "en");
  if (a.service_id === groupA) return -1;
  if (b.service_id === groupB) return 1;
  return a.label.localeCompare(b.label, "ja");
});
const filterServiceIds = new Set(filterServices.map((service) => service.service_id));
const serviceLabel = new Map(
  catalogServices.map((service) => [service.service_id, service.label]),
);

function basisLabel(basis: string) {
  if (basis === "DIRECT_SCOPE") return "直接規定";
  if (basis === "INCORPORATED_SCOPE") return "準用";
  return "適用scope";
}

function chapterOf(node: RuleNode) {
  return node.path.find((part) => /第.+章/.test(part)) || node.path[0] || "章未設定";
}

function articleStatus(node: RuleNode, selectedServiceId?: string) {
  if (selectedServiceId && isProgressiveRouteCell(selectedServiceId)) {
    return "現行本文・適用範囲を確認済み";
  }
  if (selectedServiceId) {
    const decision = serviceApplicability(
      selectedServiceId,
      "ordinance37",
      node.id,
    );
    return decision.applicable ? basisLabel(decision.basis || "") : "scope外";
  }

  const memberships = resolveServiceScope("ordinance37", node.id).memberships
    .filter((membership) => filterServiceIds.has(membership.service_id))
    .map(
      (membership) =>
        `${serviceLabel.get(membership.service_id) || membership.service_id}・${basisLabel(membership.basis)}`,
    );

  return memberships.length ? memberships.join(" / ") : "共有コーパス収載";
}

function ArticleList({
  items,
  selectedServiceId,
}: {
  items: RuleNode[];
  selectedServiceId?: string;
}) {
  const suffix = selectedServiceId
    ? `?service=${encodeURIComponent(selectedServiceId)}`
    : "";

  return (
    <div className="rules-list">
      {items.map((node) => (
        <Link
          className="rule-row"
          href={`/rules/${node.article_num}${suffix}`}
          key={node.id}
        >
          <span className="rule-number">{node.article_title}</span>
          <span className="rule-title">{node.caption || "題名なし"}</span>
          <span className="rule-status">
            {articleStatus(node, selectedServiceId)}
          </span>
        </Link>
      ))}
    </div>
  );
}

export default async function RulesPage({
  searchParams,
}: {
  searchParams: Promise<{ service?: string }>;
}) {
  const { service = "" } = await searchParams;
  const selectedService = filterServices.find(
    (item) => item.service_id === service,
  );
  const selectedServiceId = selectedService?.service_id;
  const progressiveSelection = Boolean(
    selectedServiceId && isProgressiveRouteCell(selectedServiceId),
  );
  const publicationTrust =
    progressiveSelection && selectedServiceId
      ? getProgressivePublicationTrust(selectedServiceId)
      : null;
  const selectedSourceRecords =
    progressiveSelection && selectedServiceId
      ? (getProgressiveSourceRecords(selectedServiceId) as RuleNode[])
      : nodes;
  const selectedSourceArticles = selectedSourceRecords
    .filter((node) => node.node_type === "article")
    .sort(compareArticle);

  const displayedArticles = selectedServiceId
    ? progressiveSelection
      ? filterProgressivePublishedRules(
          selectedServiceId,
          selectedSourceArticles,
          (node) => node.id,
        )
      : filterRecordsForService(
          selectedServiceId,
          "ordinance37",
          articles,
          (node) => node.id,
        )
    : articles;

  const chapters = [...new Set(displayedArticles.map(chapterOf))];
  const revision = meta.current_revision || {};
  const verificationLayerId =
    selectedServiceId === "dayrehab" ? "ordinance37-dayrehab" : "ordinance37";

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">ORDINANCE DATABASE</p>
      <h1>基準省令DB</h1>
      <p className="lead">
        基準省令の共有コーパスを表示し、サービスを選ぶと、そのサービスについて公開条件を満たした法令本文へ絞り込みます。
        介護予防サービスを選んだ場合は、対応する介護予防サービス基準のコーパスへ切り替えます。
      </p>

      <div className="notice">
        <strong>「すべて」は指定居宅サービス等基準の共有コーパスです。</strong><br />
        サービス別フィルタでは、各サービスに対応する法令コーパスへ切り替え、適用範囲と公開条件を確認できた条文だけを表示します。
      </div>

      <nav className="rules-filter" aria-label="サービスで基準省令を絞り込む">
        <Link
          className={!selectedServiceId ? "rules-filter-active" : ""}
          href="/rules"
        >
          すべて
        </Link>
        {filterServices.map((item) => (
          <Link
            className={
              selectedServiceId === item.service_id ? "rules-filter-active" : ""
            }
            href={`/rules?service=${item.service_id}`}
            key={item.service_id}
          >
            {item.label}
          </Link>
        ))}
      </nav>

      {selectedServiceId === "dayservice" || selectedServiceId === "dayrehab" ? (
        <ServiceContextLinks serviceId={selectedServiceId} />
      ) : null}

      <p className="scope-note">
        {selectedService
          ? `${selectedService.label}で絞り込み中。直接規定と準用規定を含みます。`
          : "全共有コーパスを表示中。サービスを選ぶと、公開条件を満たした範囲だけに絞り込みます。"}
      </p>

      {progressiveSelection ? (
        <div className="notice">
          <strong>現行のe-Gov本文と、このサービスへの直接適用範囲を確認済みです。</strong><br />
          ここでは公式本文と出典のみを表示し、未確認の制度間関係や解釈は加えていません。
        </div>
      ) : (
        <VerificationSummary layerId={verificationLayerId} />
      )}

      <section className="rules-stats" aria-label="基準DBの収載状況">
        <div><strong>{selectedSourceRecords.length}</strong><span>共有コーパスノード</span></div>
        <div><strong>{selectedSourceArticles.length}</strong><span>共有コーパス条文</span></div>
        <div><strong>{displayedArticles.length}</strong><span>表示中の条文</span></div>
        <div><strong>{filterServices.length}</strong><span>公開中サービスフィルタ</span></div>
      </section>

      <section className="section">
        <h2>現在の取得元</h2>
        <dl className="rule-meta">
          <div><dt>法令</dt><dd>{publicationTrust?.source_title || meta.law_title}</dd></div>
          {publicationTrust ? (
            <>
              <div><dt>版</dt><dd>{publicationTrust.source_version || "—"}</dd></div>
              <div><dt>施行日</dt><dd>{publicationTrust.effective_date || "—"}</dd></div>
              <div><dt>確認日時</dt><dd>{publicationTrust.checked_at || "—"}</dd></div>
            </>
          ) : (
            <>
              <div><dt>現行改正</dt><dd>{revision.amendment_law_num || "—"}</dd></div>
              <div><dt>施行日</dt><dd>{revision.amendment_enforcement_date || "—"}</dd></div>
              <div><dt>e-Gov状態</dt><dd>{revision.current_revision_status || "—"}</dd></div>
            </>
          )}
        </dl>
        <p>
          <a
            href={publicationTrust?.source_url || meta.source_page}
            target="_blank"
            rel="noreferrer"
          >
            e-Gov法令検索で原文を確認
          </a>
        </p>
      </section>

      {chapters.map((chapter) => {
        const items = displayedArticles.filter((node) => chapterOf(node) === chapter);
        return (
          <section className="section" key={chapter}>
            <p className="eyebrow">{selectedService ? selectedService.label : "ALL SERVICES"}</p>
            <h2>{chapter}</h2>
            <p className="meta">{items.length}条</p>
            <ArticleList items={items} selectedServiceId={selectedServiceId} />
          </section>
        );
      })}
    </article>
  );
}
