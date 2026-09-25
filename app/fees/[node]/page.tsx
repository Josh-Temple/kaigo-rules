import VerificationSummary from "../../../components/verification-summary";
import Link from "next/link";
import { notFound } from "next/navigation";
import nodesData from "../../../data/remuneration-current-skeleton.json";
import textData from "../../../data/remuneration-current-text.json";
import textMetaData from "../../../data/remuneration-current-text-meta.json";
import reviewData from "../../../data/remuneration-review.json";
import relationsData from "../../../data/remuneration-relations.json";
import sourcesData from "../../../data/sources.json";
import delegatedData from "../../../data/remuneration-delegated-nodes.json";
import delegatedRelationsData from "../../../data/remuneration-delegated-relations.json";

const nodes = nodesData as Array<any>;
const texts = textData as Array<any>;
const textMeta = textMetaData as any;
const review = reviewData as any;
const relations = relationsData as Array<any>;
const sources = sourcesData as Array<any>;
const delegated = delegatedData as Array<any>;
const delegatedRelations = delegatedRelationsData as Array<any>;

const routeKey = (id: string) => id.replace("fee.dayservice.", "");

const relationLabel: Record<string,string> = {
  defined_service_by: "サービス定義",
  staffing_calculation_delegated_to: "利用者数・人員欠如等の算定方法",
  operational_basis_related_to: "運営基準との関係",
  related_to: "関連する基準",
  currency_conversion_uses: "一単位単価",
  latest_interpretation_amendment_evidence: "最新の留意事項改正",
  delegated_criteria_to: "厚生労働大臣基準への委任",
  historically_interpreted_by: "過去の留意事項通知"
};

export function generateStaticParams() {
  return nodes
    .filter((node) => node.parent_id === "fee.dayservice.root")
    .map((node) => ({ node: routeKey(node.id) }));
}

export default async function FeeDetailPage({ params }: { params: Promise<{ node: string }> }) {
  const { node: key } = await params;
  const feeId = `fee.dayservice.${key}`;
  const node = nodes.find((item) => item.id === feeId);
  if (!node) notFound();

  const currentText = texts.find((item) => item.fee_id === feeId);
  const reviewed = (review.reviewed_nodes || []).find((item:any) =>
    item.fee_id === feeId && currentText && item.text_sha256 === currentText.text_sha256
  );
  const source = currentText
    ? sources.find((item) => item.id === currentText.source_id)
    : sources.find((item) => item.id === node.source_id);
  const linkedRelations = relations.filter((item) => item.from_fee_id === feeId);
  const isOutOfCore = node.verification_status === "OUT_OF_CORE_SCOPE";
  const delegatedTargets = delegatedRelations
    .filter((item) => item.from_id === feeId)
    .map((item) => delegated.find((target) => target.id === item.to_id))
    .filter(Boolean);

  const ordinanceHref = (id: string) => {
    const match = String(id).match(/^ordinance37\.article\.([0-9-]+)/);
    return match ? `/rules/${match[1]}` : "/rules";
  };

  return (
    <article className="answer-page rules-page fee-detail-page">
      <p className="eyebrow">{node.service_scope}</p>
      <h1>{node.title}</h1>
      <p className="meta">{node.number_path.join(" / ")} / {node.id}</p>

      {isOutOfCore ? (
        <div className="notice">
          <strong>この項目は指定通所介護のコア範囲外です。</strong><br/>
          共生型通所介護に固有の取扱いとして保持しています。通常の指定通所介護と混同しないでください。
        </div>
      ) : reviewed ? (
        <div className="notice fee-reviewed-notice">
          <strong>人手確認済み</strong><br/>
          公式資料との照合記録があります。
        </div>
      ) : (
        <div className="notice">
          <strong>現行公式本文を取込済み・人手確認待ち</strong><br/>
          厚生労働省の現行HTMLから機械抽出した本文です。単位数や率を含め、まだ人手による原文照合は完了していません。
        </div>
      )}

      <VerificationSummary layerId="remuneration-notices" />

      <section className="section">
        <h2>現行公式本文</h2>
        {currentText ? (
          <>
            <div className="fee-official-text">{currentText.official_text}</div>
            <p className="meta">取込状態：{currentText.import_status}</p>
          </>
        ) : (
          <p className="notice-hole">現行本文の機械取込がありません。</p>
        )}
      </section>

      {delegatedTargets.length ? (
        <section className="section">
          <h2>別告示で定める基準</h2>
          <p>報酬告示本文から委任される基準です。報酬本文とは別法源として保持しています。</p>
          <div className="relation-list">
            {delegatedTargets.map((target:any) => (
              <div className="relation-row" key={target.id}>
                <span className="meta">{target.source_id}</span>
                <div>
                  <Link href={`/fees/criteria#${encodeURIComponent(target.id)}`}>{target.heading}</Link>
                  <p className="meta">取込済み・人手確認待ち</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {linkedRelations.length ? (
        <section className="section">
          <h2>関連する制度ノード</h2>
          <div className="relation-list">
            {linkedRelations.map((relation, index) => (
              <div className="relation-row" key={`${relation.relation}-${index}`}>
                <span className="meta">{relationLabel[relation.relation] || relation.relation}</span>
                <div>
                  {relation.to_id ? (
                    <Link href={ordinanceHref(relation.to_id)}>
                      {relation.to_id.replace("ordinance37.article.", "基準省令 第")}条
                    </Link>
                  ) : relation.to_source_id ? (() => {
                    const linkedSource = sources.find((item) => item.id === relation.to_source_id);
                    return linkedSource
                      ? <a href={linkedSource.url} target="_blank" rel="noreferrer">{linkedSource.title}</a>
                      : <span>{relation.to_source_id}</span>;
                  })() : null}
                  <p className="meta">{relation.status}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {node.latest_amendment_evidence?.length ? (
        <section className="section">
          <h2>最新改定の証跡</h2>
          {node.latest_amendment_evidence.map((evidence:any, index:number) => {
            const evidenceSource = sources.find((item) => item.id === evidence.source_id);
            return (
              <p key={index}>
                {evidenceSource
                  ? <a href={evidenceSource.url} target="_blank" rel="noreferrer">{evidenceSource.title}</a>
                  : evidence.source_id}
                <br/><span className="meta">{evidence.locator} / {evidence.evidence_type}</span>
              </p>
            );
          })}
        </section>
      ) : null}

      <section className="section">
        <h2>取得証跡</h2>
        <dl className="rule-meta">
          <div><dt>取得元</dt><dd>{source?.title || currentText?.source_id || node.source_id}</dd></div>
          <div><dt>最新改正</dt><dd>{textMeta.current_amendment || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{textMeta.current_amendment_effective_from || "—"}</dd></div>
          <div><dt>本文SHA-256</dt><dd className="hash">{currentText?.text_sha256 || "—"}</dd></div>
          <div><dt>人手確認</dt><dd>{reviewed ? "確認済み" : "未確認"}</dd></div>
        </dl>
        {source ? <p><a href={source.url} target="_blank" rel="noreferrer">厚生労働省の原文を確認</a></p> : null}
      </section>

      <p><Link href="/fees">報酬DB一覧へ戻る</Link></p>
    </article>
  );
}
