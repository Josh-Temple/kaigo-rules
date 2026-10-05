import Link from "next/link";
import ServiceContextLinks from "../../components/service-context-links";
import VerificationSummary from "../../components/verification-summary";
import {
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
import homevisitData from "../../data/services/homevisit/rouki25-historical.generated.json";
import homebathData from "../../data/services/homebath/rouki25-historical.generated.json";
import dayrehabData from "../../data/services/dayrehab/rouki25-historical.generated.json";

const currentnessLedger = currentnessLedgerData as any;
const chain = chainData as Array<any>;
const sources = sourcesData as Array<any>;
const historicalNoticeDatasets = [
  {
    service_id: "homevisit",
    label: "訪問介護",
    data: homevisitData as any,
  },
  {
    service_id: "homebath",
    label: "訪問入浴介護",
    data: homebathData as any,
  },
  {
    service_id: "dayrehab",
    label: "通所リハビリテーション",
    data: dayrehabData as any,
  },
];

const preventivePairByPrimary: Record<string, string> = {
  homebath: "preventive-homebath",
  homenursing: "preventive-homenursing",
  homerehab: "preventive-homerehab",
  homecaremanagement: "preventive-homecaremanagement",
  dayrehab: "preventive-dayrehab",
  "shortstay-life": "preventive-shortstay-life",
  "shortstay-medical": "preventive-shortstay-medical",
  "specific-facility": "preventive-specific-facility",
  "welfare-equipment-rental": "preventive-welfare-equipment-rental",
  "specific-welfare-equipment-sale": "specific-preventive-welfare-equipment-sale",
  "dementia-dayservice": "preventive-dementia-dayservice",
  "small-scale-multifunctional": "preventive-small-scale-multifunctional",
  "dementia-group-home": "preventive-dementia-group-home",
};

const pairedPreventiveIds = new Set(Object.values(preventivePairByPrimary));

type NoticeDisplayGroup = {
  id: string;
  label: string;
  companion_label?: string;
  member_ids: string[];
  services: PublicNoticeServiceOption[];
  service_class?: string;
  record_count: number;
};

const sectionOrder = [
  "HOME_SERVICE",
  "COMMUNITY_BASED_SERVICE",
  "FACILITY_SERVICE",
  "CARE_MANAGEMENT",
  "PREVENTIVE_SUPPORT",
  "OTHER",
];

const sectionLabels: Record<string, string> = {
  HOME_SERVICE: "居宅サービス",
  COMMUNITY_BASED_SERVICE: "地域密着型サービス",
  FACILITY_SERVICE: "施設サービス",
  CARE_MANAGEMENT: "居宅介護支援",
  PREVENTIVE_SUPPORT: "介護予防支援",
  OTHER: "その他",
};

function buildNoticeDisplayGroups(): NoticeDisplayGroup[] {
  const byId = new Map(
    publicNoticeServiceOptions.map((service) => [service.service_id, service]),
  );

  return publicNoticeServiceOptions
    .filter((service) => !pairedPreventiveIds.has(service.service_id))
    .map((service) => {
      const preventiveId = preventivePairByPrimary[service.service_id];
      const preventive = preventiveId ? byId.get(preventiveId) : undefined;
      const services = preventive ? [service, preventive] : [service];

      return {
        id: service.service_id,
        label: service.label,
        companion_label: preventive?.label,
        member_ids: services.map((member) => member.service_id),
        services,
        service_class:
          service.service_id === "preventive-support"
            ? "PREVENTIVE_SUPPORT"
            : service.service_class || "OTHER",
        record_count: services.reduce(
          (total, member) => total + member.record_count,
          0,
        ),
      };
    });
}

const noticeDisplayGroups = buildNoticeDisplayGroups();

function findNoticeDisplayGroup(serviceId?: string) {
  if (!serviceId) return undefined;
  return noticeDisplayGroups.find((group) =>
    group.member_ids.includes(serviceId),
  );
}

function displaySections(groups: NoticeDisplayGroup[]) {
  return sectionOrder
    .map((serviceClass) => ({
      serviceClass,
      label: sectionLabels[serviceClass],
      groups: groups.filter(
        (group) => (group.service_class || "OTHER") === serviceClass,
      ),
    }))
    .filter((section) => section.groups.length > 0);
}

const pageLabel = (evidence: PublicNoticeEvidence) => {
  if (!evidence.page_start) return "";
  return evidence.page_end && evidence.page_end !== evidence.page_start
    ? " p." + evidence.page_start + "–" + evidence.page_end
    : " p." + evidence.page_start;
};

const sourceStateLabel = (record: PublicNoticeRecord) =>
  record.source_state === "RECONSTRUCTED_CANDIDATE"
    ? "再構成本文候補"
    : "公式旧HTML";

const currentnessLabel = (record: PublicNoticeRecord) =>
  record.currentness_state === "HOLD" ? "現行性HOLD" : "現行性GAP";

function groupedRecords(records: PublicNoticeRecord[]) {
  return records.reduce((groups, record) => {
    const key = record.service_id + "::" + record.section;
    const existing = groups.get(key) || [];
    existing.push(record);
    groups.set(key, existing);
    return groups;
  }, new Map<string, PublicNoticeRecord[]>());
}

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

function filterRecordsByQuery(records: PublicNoticeRecord[], query: string) {
  const terms = normalize(query).split(" ").filter(Boolean);
  if (!terms.length) return records;

  return records.filter((record) => {
    const haystack = normalize(
      [
        record.service_label,
        record.section,
        ...record.number_path,
        record.title,
        record.body_text,
      ].join(" "),
    );
    return terms.every((term) => haystack.includes(term));
  });
}

const noticeStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    RECONSTRUCTED_CANDIDATES_PUBLISHED_CURRENTNESS_HOLD:
      "再構成本文候補を公開・現行性HOLD",
    HISTORICAL_SOURCE_TEXT_PUBLISHED_CURRENTNESS_GAP:
      "公式旧資料の本文を公開・現行性GAP",
    ITEM_BODY_VERIFIED_CURRENTNESS_PENDING:
      "本文照合済み・現行性確認中",
    INDEXED_SHARED_MHLW_SOURCE_SCOPE_NOT_ITEM_VERIFIED:
      "一次資料scope収載済み・本文照合前",
    INDEXED_SHARED_MHLW_NOTICE_SCOPE_ONLY:
      "通知scope収載済み・本文照合前",
    SCOPE_DEFINED_NOT_RECONSTRUCTED:
      "通知scope定義済み・本文未再構成",
    WORK_CONTROL_ACCEPTED_NOT_REPOSITORY_INGESTED:
      "Work Control成果受理済み・Repository未統合",
    STAGING_COMPLETE_NOT_REPOSITORY_INGESTED:
      "通知staging完了・Repository未統合",
    NOT_REPOSITORY_INGESTED:
      "Repositoryへの通知本文取り込み前",
  };
  return labels[status] || status;
};

function VerificationPanels({
  services,
}: {
  services: PublicNoticeServiceOption[];
}) {
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

function ServiceGroupRow({ group }: { group: NoticeDisplayGroup }) {
  return (
    <Link
      className="notice-service-row"
      href={"/notices?service=" + group.id}
    >
      <span className="notice-service-name">
        <strong>{group.label}</strong>
        {group.companion_label ? (
          <small>{group.companion_label}を含む</small>
        ) : null}
      </span>
      <span className="notice-service-count">
        {group.record_count > 0
          ? group.record_count + "項目公開"
          : "本文整備中"}
      </span>
    </Link>
  );
}

function ServiceBrowser() {
  const published = noticeDisplayGroups.filter((group) => group.record_count > 0);
  const pending = noticeDisplayGroups.filter((group) => group.record_count === 0);

  return (
    <section className="notice-service-browser" aria-labelledby="notice-service-heading">
      <div className="notice-section-heading">
        <p className="eyebrow">BROWSE BY SERVICE</p>
        <h2 id="notice-service-heading">サービスから探す</h2>
        <p className="meta">
          介護予防サービスは対応するサービスと同じ入口にまとめています。
          介護予防支援だけは独立して扱います。
        </p>
      </div>

      {displaySections(published).map((section) => (
        <section className="notice-service-section" key={section.serviceClass}>
          <h3>{section.label}</h3>
          <div className="notice-service-list">
            {section.groups.map((group) => (
              <ServiceGroupRow group={group} key={group.id} />
            ))}
          </div>
        </section>
      ))}

      {pending.length ? (
        <details className="notice-pending-services">
          <summary>本文整備中のサービスを見る</summary>
          <div className="notice-pending-services-body">
            {displaySections(pending).map((section) => (
              <section className="notice-service-section" key={section.serviceClass}>
                <h3>{section.label}</h3>
                <div className="notice-service-list">
                  {section.groups.map((group) => (
                    <ServiceGroupRow group={group} key={group.id} />
                  ))}
                </div>
              </section>
            ))}
          </div>
        </details>
      ) : null}
    </section>
  );
}

export default async function NoticesPage({
  searchParams,
}: {
  searchParams: Promise<{ service?: string; q?: string }>;
}) {
  const { service = "", q = "" } = await searchParams;
  const selectedGroup = findNoticeDisplayGroup(service);
  const invalidService = Boolean(service && !selectedGroup);
  const baseRecords = selectedGroup
    ? publicNoticeRecords.filter((record) =>
        selectedGroup.member_ids.includes(record.service_id),
      )
    : q.trim()
      ? publicNoticeRecords
      : [];
  const records = filterRecordsByQuery(baseRecords, q);
  const grouped = groupedRecords(records);
  const currentnessHold =
    currentnessLedger.final_audit_classification?.counts?.HOLD || 0;
  const contextServiceId = selectedGroup?.member_ids.find(
    (serviceId) => serviceId === "dayservice" || serviceId === "dayrehab",
  );

  return (
    <article className="answer-page notice-reader-page">
      <p className="eyebrow">INTERPRETATION NOTICE DATABASE</p>
      <h1>基準解釈通知DB</h1>
      <p className="lead">
        老企第25号「指定居宅サービス等及び指定介護予防サービス等に関する基準について」を、
        サービスからたどるか、公開済み本文を横断検索して確認できます。
        原典の構造と順序は維持し、整備状況や根拠は必要なときに確認できる形で表示します。
      </p>

      <form className="notice-search-form" action="/notices" method="get">
        {selectedGroup ? (
          <input name="service" type="hidden" value={selectedGroup.id} />
        ) : null}
        <label>
          <span>
            {selectedGroup
              ? selectedGroup.label + "の通知を検索"
              : "公開済みの解釈通知を横断検索"}
          </span>
          <input
            defaultValue={q}
            name="q"
            placeholder="例：管理者、記録、非常災害"
            type="search"
          />
        </label>
        <button type="submit">検索</button>
      </form>

      {selectedGroup || q ? (
        <p className="notice-reset-link">
          <Link href="/notices">サービス一覧と横断検索に戻る</Link>
        </p>
      ) : null}

      {!selectedGroup && !q && !invalidService ? <ServiceBrowser /> : null}

      {invalidService ? (
        <div className="notice">
          指定されたサービスはservice catalogに登録されていません。
          <br />
          <Link href="/notices">サービス一覧に戻る</Link>
        </div>
      ) : null}

      {selectedGroup ? (
        <section className="notice-selection-summary">
          <p className="eyebrow">SELECTED SERVICE</p>
          <h2>{selectedGroup.label}</h2>
          {selectedGroup.companion_label ? (
            <p>
              <strong>{selectedGroup.companion_label}</strong>
              も同じ入口でまとめて扱います。
            </p>
          ) : null}
          <div className="notice-service-state-list">
            {selectedGroup.services.map((member) => (
              <span key={member.service_id}>
                <strong>{member.label}</strong>
                {" — "}
                {member.record_count > 0
                  ? member.record_count + "項目公開"
                  : "本文整備中"}
              </span>
            ))}
          </div>
        </section>
      ) : null}

      {contextServiceId ? <ServiceContextLinks serviceId={contextServiceId} /> : null}

      {q ? (
        <p className="notice-result-summary">
          <strong>{records.length}</strong>件
          {selectedGroup
            ? " / " + selectedGroup.label + "内の検索結果"
            : " / 全公開通知からの検索結果"}
          {" — "}
          「{q}」
        </p>
      ) : selectedGroup && records.length ? (
        <p className="notice-result-summary">
          <strong>{records.length}</strong>項目を原典順で表示しています。
        </p>
      ) : null}

      {selectedGroup && selectedGroup.record_count === 0 ? (
        <div className="notice">
          <strong>このサービス群の基準解釈通知本文は、まだRepositoryで公開していません。</strong>
          <br />
          整備状況は下部の「収載・確認状況」で確認できます。
        </div>
      ) : null}

      {q && records.length === 0 ? (
        <div className="notice">
          条件に一致する公開通知は見つかりませんでした。
        </div>
      ) : null}

      {records.length ? (
        <nav className="notice-reader-nav" aria-label="解釈通知の目次">
          <p className="eyebrow">CONTENTS</p>
          <h2>目次</h2>
          {[...grouped.entries()].map(([key, sectionItems]) => (
            <div className="notice-reader-nav-group" key={key}>
              <strong>
                {sectionItems[0].service_label} / {sectionItems[0].section}
              </strong>
              <div>
                {sectionItems.map((item) => (
                  <a href={"#" + item.id} key={item.id}>
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

            {sectionItems.map((item) => (
              <article className="notice-reader-item" id={item.id} key={item.id}>
                <header className="notice-reader-item-head">
                  <p className="meta">{item.number_path.join(" / ")}</p>
                  <h3>{item.title}</h3>
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
                      {item.service_label}
                      {" / "}
                      {sourceStateLabel(item)}
                      {" / "}本文照合：<strong>PASS</strong>
                      {" / "}現行性：<strong>{currentnessLabel(item)}</strong>
                      {" / "}人手確認：<strong>未実施</strong>
                    </p>

                    <div className="notice-evidence-list">
                      {item.source_evidence.map((evidence) => (
                        <p key={item.id + "-" + evidence.source_id + "-" + (evidence.role || "")}>
                          <a href={evidence.source_url} target="_blank" rel="noreferrer">
                            {evidence.source_title}
                          </a>
                          <span className="meta">
                            {pageLabel(evidence)}
                            {evidence.note ? " / " + evidence.note : ""}
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

      {(selectedGroup || q) && !invalidService ? (
        <details className="notice-audit-details">
          <summary>収載・確認状況を見る</summary>
          <div className="notice-audit-body">
            <section className="rules-stats" aria-label="基準解釈通知DBの収載状況">
              <div><strong>{publicNoticeRecords.length}</strong><span>公開通知項目</span></div>
              <div><strong>{publicNoticeRegisteredServiceCount}</strong><span>登録サービス</span></div>
              <div><strong>{publicNoticePublishedServiceCount}</strong><span>本文公開サービス</span></div>
              <div><strong>{records.length}</strong><span>現在の表示項目</span></div>
            </section>

            {selectedGroup ? (
              <>
                <div className="notice-service-status-detail">
                  {selectedGroup.services.map((member) => (
                    <p key={member.service_id}>
                      <strong>{member.label}</strong>
                      {"："}
                      {noticeStatusLabel(member.notice_status)}
                      {member.notice_note ? " / " + member.notice_note : ""}
                    </p>
                  ))}
                </div>
                <VerificationPanels services={selectedGroup.services} />
              </>
            ) : (
              <VerificationPanels
                services={publicNoticeServiceOptions.filter(
                  (option) => option.record_count > 0,
                )}
              />
            )}
          </div>
        </details>
      ) : null}

      {selectedGroup?.member_ids.includes("dayservice") ? (
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

      {selectedGroup
        ? historicalNoticeDatasets
            .filter((entry) => selectedGroup.member_ids.includes(entry.service_id))
            .map((entry) => (
              <details className="notice-audit-details" key={entry.service_id}>
                <summary>
                  {entry.label}{entry.data.item_count}項目の旧HTML・改正証拠
                </summary>
                <div className="notice-audit-body">
                  <section className="section">
                    <h2>現行統合本文ではありません</h2>
                    <p>
                      公式旧HTMLとの本文一致は独立照合済みですが、部分改正資料を旧HTMLへ
                      機械適用していません。現行性はGAP、人手確認は未実施です。
                    </p>
                    <p>
                      <a href={entry.data.source?.url} target="_blank" rel="noreferrer">
                        厚生労働省の公式旧HTMLを確認
                      </a>
                    </p>
                    {entry.data.amendment_evidence?.source_url ? (
                      <p>
                        <a
                          href={entry.data.amendment_evidence.source_url}
                          target="_blank"
                          rel="noreferrer"
                        >
                          改正資料を確認
                        </a>
                      </p>
                    ) : null}
                  </section>
                </div>
              </details>
            ))
        : null}
    </article>
  );
}
