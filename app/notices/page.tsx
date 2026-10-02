import Link from "next/link";
import ServiceContextLinks from "../../components/service-context-links";
import VerificationSummary from "../../components/verification-summary";
import {
  filterPublicNotices,
  noticeServiceCount,
  publicNoticePublishedServiceCount,
  publicNoticeRecords,
  publicNoticeRegisteredServiceCount,
  publicNoticeServiceOptions,
  type PublicNoticeEvidence,
  type PublicNoticeRecord,
  type PublicNoticeServiceOption,
} from "../../lib/notice-database";
import currentnessLedgerData from "../../data/notice-rouki25-currentness-ledger.json";
import chainData from "../../data/notice-source-chain.json";
import sourcesData from "../../data/sources.json";
import dayrehabData from "../../data/services/dayrehab/rouki25-historical.generated.json";

const currentnessLedger = currentnessLedgerData as any;
const chain = chainData as Array<any>;
const sources = sourcesData as Array<any>;
const dayrehab = dayrehabData as any;

const pageLabel = (evidence: PublicNoticeEvidence) => {
  if (!evidence.page_start) return "";
  return evidence.page_end && evidence.page_end !== evidence.page_start
    ? ` p.${evidence.page_start}–${evidence.page_end}`
    : ` p.${evidence.page_start}`;
};

const sourceStateLabel = (record: PublicNoticeRecord) =>
  record.source_state === "RECONSTRUCTED_CANDIDATE"
    ? "再構成本文候補"
    : "公式旧HTML";

const currentnessLabel = (record: PublicNoticeRecord) =>
  record.currentness_state === "HOLD" ? "現行性HOLD" : "現行性GAP";

function groupedRecords(records: PublicNoticeRecord[]) {
  return records.reduce((groups, record) => {
    const key = `${record.service_id}::${record.section}`;
    const existing = groups.get(key) || [];
    existing.push(record);
    groups.set(key, existing);
    return groups;
  }, new Map<string, PublicNoticeRecord[]>());
}

const noticeStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    RECONSTRUCTED_CANDIDATES_PUBLISHED_CURRENTNESS_HOLD:
      "再構成本文候補を公開・現行性HOLD",
    HISTORICAL_SOURCE_TEXT_PUBLISHED_CURRENTNESS_GAP:
      "公式旧資料の本文を公開・現行性GAP",
    SCOPE_DEFINED_NOT_RECONSTRUCTED:
      "通知scope定義済み・本文未再構成",
    WORK_CONTROL_ACCEPTED_NOT_REPOSITORY_INGESTED:
      "Work Control成果受理済み・Repository未統合",
    NOT_REPOSITORY_INGESTED:
      "Repositoryへの通知本文取り込み前",
  };
  return labels[status] || status;
};

function VerificationPanels({
  service,
}: {
  service?: PublicNoticeServiceOption;
}) {
  const services = service
    ? [service]
    : publicNoticeServiceOptions.filter((option) => option.record_count > 0);
  const layerIds = [
    ...new Set(
      services
        .map((option) => option.verification_layer_id)
        .filter((layerId): layerId is string => Boolean(layerId)),
    ),
  ];

  if (!layerIds.length) return null;

  return (
    <div className="notice-verification-stack">
      {layerIds.map((layerId) => (
        <VerificationSummary layerId={layerId} key={layerId} />
      ))}
    </div>
  );
}

export default async function NoticesPage({
  searchParams,
}: {
  searchParams: Promise<{ service?: string }>;
}) {
  const { service = "" } = await searchParams;
  const selectedService = publicNoticeServiceOptions.find(
    (option) => option.service_id === service,
  );
  const selectedServiceId = selectedService?.service_id;
  const records = service ? filterPublicNotices(service) : filterPublicNotices();
  const grouped = groupedRecords(records);
  const currentnessHold =
    currentnessLedger.final_audit_classification?.counts?.HOLD || 0;

  return (
    <article className="answer-page notice-reader-page">
      <p className="eyebrow">INTERPRETATION NOTICE DATABASE</p>
      <h1>基準解釈通知DB</h1>
      <p className="lead">
        老企第25号「指定居宅サービス等及び指定介護予防サービス等に関する基準について」を、
        service catalogに登録されたサービスを前提に一つのDBとして扱います。本文がRepositoryへ
        取り込まれているサービスは本文を表示し、未収録のサービスも整備状態を隠さず表示します。
      </p>

      <div className="notice">
        <strong>サービス登録、本文収録、本文照合、現行性、人手確認は別々に管理します。</strong><br />
        「すべて」に表示されることやservice catalogへ登録されていること自体は、
        そのサービスの通知本文が収録済み・現行・人手確認済みであることを意味しません。
      </div>

      <nav className="rules-filter" aria-label="サービスで基準解釈通知を絞り込む">
        <Link
          className={!service ? "rules-filter-active" : ""}
          href="/notices"
        >
          すべて
        </Link>
        {publicNoticeServiceOptions.map((option) => (
          <Link
            className={
              selectedServiceId === option.service_id ? "rules-filter-active" : ""
            }
            href={`/notices?service=${option.service_id}`}
            key={option.service_id}
          >
            {option.label}{option.record_count === 0 ? "（本文未収録）" : ""}
          </Link>
        ))}
      </nav>

      {selectedServiceId === "dayservice" || selectedServiceId === "dayrehab" ? (
        <ServiceContextLinks serviceId={selectedServiceId} />
      ) : null}

      <p className="scope-note">
        {selectedService
          ? `${selectedService.label}で絞り込み中。通知DBの状態：${noticeStatusLabel(selectedService.notice_status)}。`
          : `${publicNoticeRegisteredServiceCount}サービスをservice catalogに登録済み。本文公開済みは${publicNoticePublishedServiceCount}サービスです。「共通」や他サービスへの適用は自動推定しません。`}
      </p>

      {service && !selectedService ? (
        <div className="notice">
          指定されたサービスはservice catalogに登録されていません。
        </div>
      ) : null}

      {selectedService && selectedService.record_count === 0 ? (
        <div className="notice">
          <strong>{selectedService.label}の基準解釈通知本文は、まだRepositoryで公開していません。</strong><br />
          {noticeStatusLabel(selectedService.notice_status)}
          {selectedService.notice_note ? ` / ${selectedService.notice_note}` : ""}
        </div>
      ) : null}

      <VerificationPanels service={selectedService} />

      <section className="rules-stats" aria-label="基準解釈通知DBの収載状況">
        <div><strong>{publicNoticeRecords.length}</strong><span>公開通知項目</span></div>
        <div><strong>{publicNoticeRegisteredServiceCount}</strong><span>登録サービス</span></div>
        <div><strong>{publicNoticePublishedServiceCount}</strong><span>本文公開サービス</span></div>
        <div><strong>{records.length}</strong><span>表示中の項目</span></div>
      </section>

      {records.length ? (
        <nav className="notice-reader-nav" aria-label="解釈通知の目次">
          <p className="eyebrow">CONTENTS</p>
          {[...grouped.entries()].map(([key, sectionItems]) => (
            <div className="notice-reader-nav-group" key={key}>
              <strong>
                {sectionItems[0].service_label} / {sectionItems[0].section}
              </strong>
              <div>
                {sectionItems.map((item) => (
                  <a href={`#${item.id}`} key={item.id}>
                    {item.number_path.at(-1)} {item.title}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </nav>
      ) : null}

      {[...grouped.entries()].map(([key, sectionItems]) => {
        const first = sectionItems[0];
        return (
          <section className="notice-reader-section" key={key}>
            <p className="eyebrow">{first.service_label}</p>
            <h2>{first.section}</h2>
            <p className="meta">
              {sourceStateLabel(first)} / {currentnessLabel(first)} / 人手確認未実施
            </p>

            {sectionItems.map((item) => (
              <article className="notice-reader-item" id={item.id} key={item.id}>
                <header className="notice-reader-item-head">
                  <p className="meta">{item.number_path.join(" / ")}</p>
                  <h3>{item.title}</h3>
                  <p className="meta">
                    {item.service_label} / {sourceStateLabel(item)} / 本文照合PASS / {currentnessLabel(item)}
                  </p>
                </header>

                <div className="notice-reader-text">
                  {item.body_text.trim().split("\n").map((line, index) => (
                    <p key={index}>{line}</p>
                  ))}
                </div>

                <details className="notice-item-details">
                  <summary>根拠と確認状態</summary>
                  <div className="notice-item-details-body">
                    <p className="meta">
                      本文の独立機械照合：<strong>一致</strong>
                      {" / "}現行性：<strong>{item.currentness_state}</strong>
                      {" / "}人手確認：<strong>未実施</strong>
                    </p>

                    <div className="notice-evidence-list">
                      {item.source_evidence.map((evidence) => (
                        <p key={`${item.id}-${evidence.source_id}-${evidence.role || ""}`}>
                          <a href={evidence.source_url} target="_blank" rel="noreferrer">
                            {evidence.source_title}
                          </a>
                          <span className="meta">
                            {pageLabel(evidence)}
                            {evidence.note ? ` / ${evidence.note}` : ""}
                          </span>
                        </p>
                      ))}
                    </div>
                  </div>
                </details>
              </article>
            ))}
          </section>
        );
      })}

      {!service || selectedServiceId === "dayservice" ? (
        <details className="notice-audit-details">
          <summary>通所介護22項目の再構成・監査情報</summary>
          <div className="notice-audit-body">
            <section className="section">
              <h2>確認状況</h2>
              <p>
                通所介護の本文候補は{noticeServiceCount("dayservice")}項目で、
                独立機械照合は全項目PASSです。現行性は{currentnessHold}項目がHOLDです。
                本文候補の整合性と、現在有効な本文であることの証明を分けています。
              </p>
              <p><Link href="/notices/review">22項目の監査・人手レビュー画面を見る →</Link></p>
            </section>

            <section className="section">
              <h2>再構成の考え方</h2>
              <div className="reconstruction-flow">
                <span>1 最新の骨格</span><b>→</b><span>2 過去資料で穴埋め</span><b>→</b>
                <span>3 改正を順方向に再生</span><b>→</b><span>4 人手確認</span>
              </div>
            </section>

            <section className="section">
              <h2>資料チェーン</h2>
              <div className="source-chain">
                {chain.map((entry) => {
                  const source = sources.find((item) => item.id === entry.source_id);
                  return (
                    <div className="source-chain-row" key={entry.source_id}>
                      <span className="meta">{entry.issued_period}</span>
                      <div>
                        <strong>{source?.title || entry.source_id}</strong>
                        <p>{entry.use}</p>
                        {entry.warning ? <p className="meta">注意：{entry.warning}</p> : null}
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>
          </div>
        </details>
      ) : null}

      {!service || selectedServiceId === "dayrehab" ? (
        <details className="notice-audit-details">
          <summary>通所リハ9項目の旧HTML・改正証拠</summary>
          <div className="notice-audit-body">
            <section className="section">
              <h2>現行統合本文ではありません</h2>
              <p>
                公式旧HTMLとの本文一致は独立照合済みですが、令和6年度新旧対照の
                「略」「新設」「削る」を旧HTMLへ機械適用していません。
                現行性はGAP、人手確認は未実施です。
              </p>
              <p>
                <a href={dayrehab.source?.url} target="_blank" rel="noreferrer">
                  厚生労働省の公式旧HTMLを確認
                </a>
              </p>
              {dayrehab.amendment_evidence?.source_url ? (
                <p>
                  <a href={dayrehab.amendment_evidence.source_url} target="_blank" rel="noreferrer">
                    令和6年度新旧対照表を確認
                  </a>
                </p>
              ) : null}
            </section>
          </div>
        </details>
      ) : null}
    </article>
  );
}
