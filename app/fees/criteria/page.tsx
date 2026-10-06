import Link from "next/link";
import VerificationSummary from "../../../components/verification-summary";
import nodesData from "../../../data/remuneration-delegated-nodes.json";
import relationsData from "../../../data/remuneration-delegated-relations.json";
import metaData from "../../../data/remuneration-delegated-meta.json";
import sourcesData from "../../../data/sources.json";
import {
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  listProgressivePublicationCells,
} from "../../../lib/publication-policy";
import { listServices } from "../../../lib/service-catalog";
import {
  verifiedRelatedPrimarySources,
  type VerifiedPrimarySourceRelation,
} from "../../../lib/verified-related-sources";

const nodes = nodesData as Array<any>;
const relations = relationsData as Array<any>;
const meta = metaData as any;
const sources = sourcesData as Array<any>;

function RelatedPrimarySources({
  items,
}: {
  items: VerifiedPrimarySourceRelation[];
}) {
  if (!items.length) return null;
  return (
    <div className="source-chain">
      {items.map((item) => (
        <div
          className="source-chain-row"
          key={
            item.relation_direction +
            "|" +
            item.related_record_id
          }
        >
          <span className="meta">確認済みの参照関係</span>
          <div>
            <strong>{item.label}</strong>
            <p>
              <Link href={item.href}>{item.title}</Link>
            </p>
            {item.source_url ? (
              <p className="meta">
                <a
                  href={item.source_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  公式資料を確認
                </a>
                {item.source_locator
                  ? " / " + item.source_locator
                  : ""}
              </p>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}

export default async function FeeCriteriaPage({
  searchParams,
}: {
  searchParams: Promise<{ service?: string }>;
}) {
  const { service = "" } = await searchParams;
  const requestedServiceId = service.trim();
  const catalogService = listServices().find(
    (item) => item.service_id === requestedServiceId,
  );
  const publicationCell = requestedServiceId
    ? listProgressivePublicationCells(
        DELEGATED_REMUNERATION_SOURCE_FAMILY,
      ).find(
        (item) => item.service_id === requestedServiceId,
      )
    : undefined;

  if (requestedServiceId && !publicationCell) {
    return (
      <article className="answer-page rules-page">
        <p className="eyebrow">
          DELEGATED REMUNERATION CRITERIA
        </p>
        <h1>
          {catalogService?.label || requestedServiceId}
          の報酬算定基準
        </h1>
        <p className="lead">
          報酬告示から参照される算定方法・厚生労働大臣基準を、
          サービスごとの公開条件を満たした範囲で表示します。
        </p>
        <div className="notice">
          <strong>
            このサービスで公開条件を満たした別告示データは、
            現在ありません。
          </strong>
          <br />
          未確認の本文・適用関係を代わりに表示することはしません。
        </div>
        <p>
          <Link href="/databases">
            公開中のデータベース一覧を見る →
          </Link>
        </p>
      </article>
    );
  }

  if (publicationCell) {
    const records = getProgressiveSourceRecords(
      publicationCell.service_id,
      DELEGATED_REMUNERATION_SOURCE_FAMILY,
    ) as Array<any>;
    const trust = getProgressivePublicationTrust(
      publicationCell.service_id,
      DELEGATED_REMUNERATION_SOURCE_FAMILY,
    );
    const sourceGroups = [
      ...new Set(
        records.map((record) =>
          String(
            record.source_document_title ||
              record.source_id ||
              "公式資料",
          ),
        ),
      ),
    ];

    return (
      <article className="answer-page rules-page">
        <p className="eyebrow">
          DELEGATED REMUNERATION CRITERIA
        </p>
        <h1>
          {publicationCell.label}の報酬算定基準
        </h1>
        <p className="lead">
          報酬告示から参照される算定方法・厚生労働大臣基準のうち、
          このサービスについて公開条件を満たした公式本文だけを表示します。
        </p>

        <div className="notice">
          <strong>
            公式本文・出典・現行性・このサービスの収載範囲を確認できた項目だけを表示しています。
          </strong>
          <br />
          未確認の制度間関係や解釈は追加していません。
        </div>

        <section className="section">
          <h2>現在の取得元</h2>
          <dl className="rule-meta">
            <div>
              <dt>資料群</dt>
              <dd>{trust?.source_title || "—"}</dd>
            </div>
            <div>
              <dt>版</dt>
              <dd>{trust?.source_version || "—"}</dd>
            </div>
            <div>
              <dt>確認日</dt>
              <dd>{trust?.checked_at || "—"}</dd>
            </div>
          </dl>
        </section>

        <section
          className="rules-stats"
          aria-label="収載状況"
        >
          <div>
            <strong>{records.length}</strong>
            <span>表示中の項目</span>
          </div>
          <div>
            <strong>{sourceGroups.length}</strong>
            <span>公式資料</span>
          </div>
        </section>

        {sourceGroups.map((sourceTitle) => {
          const items = records.filter(
            (record) =>
              String(
                record.source_document_title ||
                  record.source_id ||
                  "公式資料",
              ) === sourceTitle,
          );
          return (
            <section className="section" key={sourceTitle}>
              <h2>{sourceTitle}</h2>
              <div className="delegated-list">
                {items.map((item) => {
                  const related =
                    verifiedRelatedPrimarySources(
                      publicationCell.service_id,
                      DELEGATED_REMUNERATION_SOURCE_FAMILY,
                      item,
                    );
                  return (
                    <details
                      className="delegated-node"
                      id={item.id}
                      key={item.id}
                    >
                      <summary>
                        <span>
                          {item.heading ||
                            item.item_label ||
                            item.id}
                        </span>
                        <small>公式本文</small>
                      </summary>
                      <div className="delegated-body">
                        <p className="fee-official-text">
                          {item.official_text}
                        </p>
                        <p className="meta">
                          {item.source_locator}
                        </p>
                        <p>
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            厚生労働省の原文を確認
                          </a>
                        </p>
                        <RelatedPrimarySources
                          items={related}
                        />
                      </div>
                    </details>
                  );
                })}
              </div>
            </section>
          );
        })}
      </article>
    );
  }

  const grouped = [
    {
      title:
        "告示27号：利用者数・人員欠如等の算定方法",
      items: nodes.filter((node) =>
        node.id.startsWith("calc27."),
      ),
    },
    {
      title:
        "告示95号：厚生労働大臣が定める基準",
      items: nodes.filter((node) =>
        node.id.startsWith("criteria95."),
      ),
    },
  ];

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">
        DELEGATED REMUNERATION CRITERIA
      </p>
      <h1>通所介護の別告示DB</h1>
      <p className="lead">
        報酬告示19号から参照される算定方法告示・厚生労働大臣基準を、
        厚生労働省HTMLから構造化しています。
      </p>
      <div className="notice">
        <strong>公式資料の本文と出典を確認できます。</strong>
        <br />
        制度間の参照関係は、独立検証済みのものだけを関連資料として表示します。
      </div>

      <VerificationSummary layerId="remuneration-notices" />
      <section className="rules-stats">
        <div>
          <strong>{meta.counts?.nodes || nodes.length}</strong>
          <span>ノード</span>
        </div>
        <div>
          <strong>{meta.counts?.notice27_nodes || 0}</strong>
          <span>告示27号</span>
        </div>
        <div>
          <strong>{meta.counts?.notice95_nodes || 0}</strong>
          <span>告示95号</span>
        </div>
        <div>
          <strong>{meta.counts?.relations || relations.length}</strong>
          <span>収載関係</span>
        </div>
      </section>

      {grouped.map((group) => (
        <section className="section" key={group.title}>
          <h2>{group.title}</h2>
          <div className="delegated-list">
            {group.items.map((item) => {
              const source = sources.find(
                (row) => row.id === item.source_id,
              );
              const related =
                verifiedRelatedPrimarySources(
                  "dayservice",
                  DELEGATED_REMUNERATION_SOURCE_FAMILY,
                  {
                    id: item.id,
                    legacy_node_id: item.id,
                  },
                );
              return (
                <details
                  className="delegated-node"
                  id={item.id}
                  key={item.id}
                >
                  <summary>
                    <span>{item.heading}</span>
                    <small>公式本文</small>
                  </summary>
                  <div className="delegated-body">
                    <p className="fee-official-text">
                      {item.official_text}
                    </p>
                    {source ? (
                      <p>
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          厚生労働省の原文を確認
                        </a>
                      </p>
                    ) : null}
                    <RelatedPrimarySources items={related} />
                  </div>
                </details>
              );
            })}
          </div>
        </section>
      ))}
    </article>
  );
}
