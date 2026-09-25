import Link from "next/link";
import VerificationSummary from "../../components/verification-summary";
import reviewPacketData from "../../data/notice-review-packet.json";
import currentnessLedgerData from "../../data/notice-rouki25-currentness-ledger.json";
import chainData from "../../data/notice-source-chain.json";
import sourcesData from "../../data/sources.json";

type SourceEvidence = {
  source_id: string;
  source_title: string;
  source_url: string;
  page_start?: number | null;
  page_end?: number | null;
  role?: string;
  note?: string;
};

type ReviewItem = {
  notice_id: string;
  family: string;
  section: string;
  title: string;
  number_path: string[];
  candidate_text: string;
  reconstruction_status: string;
  human_verification_status: string;
  source_evidence: SourceEvidence[];
  independent_verification?: { result?: string };
};

const reviewPacket = reviewPacketData as { items?: ReviewItem[] };
const currentnessLedger = currentnessLedgerData as any;
const chain = chainData as Array<any>;
const sources = sourcesData as Array<any>;
const items = reviewPacket.items || [];

const groupedItems = items.reduce((groups, item) => {
  const existing = groups.get(item.section) || [];
  existing.push(item);
  groups.set(item.section, existing);
  return groups;
}, new Map<string, ReviewItem[]>());

const pageLabel = (evidence: SourceEvidence) => {
  if (!evidence.page_start) return "";
  return evidence.page_end && evidence.page_end !== evidence.page_start
    ? ` p.${evidence.page_start}–${evidence.page_end}`
    : ` p.${evidence.page_start}`;
};

export default function NoticesPage() {
  const independentPass = items.filter(
    (item) => item.independent_verification?.result === "PASS"
  ).length;
  const currentnessHold =
    currentnessLedger.final_audit_classification?.counts?.HOLD || 0;

  return (
    <article className="answer-page notice-reader-page">
      <p className="eyebrow">INTERPRETATION NOTICE</p>
      <h1>解釈通知を読む</h1>
      <p className="lead">
        老企第25号「指定居宅サービス等及び指定介護予防サービス等に関する基準について」のうち、
        現在は通所介護の22項目を、項目ごとに読める形で掲載しています。
      </p>

      <div className="notice">
        <strong>掲載本文は、公式の改正資料から再構成した本文候補です。</strong><br />
        22項目は独立した機械照合を通過していますが、後続改正を網羅できていることの証明が未完了です。
        そのため「現行統合版」とは扱いません。重要な判断ではリンク先の一次資料も確認してください。
      </div>

      <nav className="notice-reader-nav" aria-label="解釈通知の目次">
        <p className="eyebrow">CONTENTS</p>
        {[...groupedItems.entries()].map(([section, sectionItems]) => (
          <div className="notice-reader-nav-group" key={section}>
            <strong>{section}</strong>
            <div>
              {sectionItems.map((item) => (
                <a href={`#${item.notice_id}`} key={item.notice_id}>
                  {item.number_path.at(-1)} {item.title}
                </a>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {[...groupedItems.entries()].map(([section, sectionItems]) => (
        <section className="notice-reader-section" key={section}>
          <p className="eyebrow">{sectionItems[0]?.number_path.slice(0, 3).join(" / ")}</p>
          <h2>{section}</h2>

          {sectionItems.map((item) => (
            <article className="notice-reader-item" id={item.notice_id} key={item.notice_id}>
              <header className="notice-reader-item-head">
                <p className="meta">{item.number_path.join(" / ")}</p>
                <h3>{item.title}</h3>
              </header>

              <div className="notice-reader-text">{item.candidate_text.trim()}</div>

              <details className="notice-item-details">
                <summary>根拠と確認状態</summary>
                <div className="notice-item-details-body">
                  <p className="meta">
                    本文の独立機械照合：
                    <strong>{item.independent_verification?.result === "PASS" ? "一致" : "未確認"}</strong>
                    {" / "}現行性：<strong>未確定</strong>
                    {" / "}人手確認：<strong>{item.human_verification_status === "NOT_REVIEWED" ? "未実施" : item.human_verification_status}</strong>
                  </p>

                  <div className="notice-evidence-list">
                    {item.source_evidence.map((evidence) => (
                      <p key={`${item.notice_id}-${evidence.source_id}-${evidence.role || ""}`}>
                        <a href={evidence.source_url} target="_blank" rel="noreferrer">
                          {evidence.source_title}
                        </a>
                        <span className="meta">{pageLabel(evidence)}</span>
                      </p>
                    ))}
                  </div>
                </div>
              </details>
            </article>
          ))}
        </section>
      ))}

      <details className="notice-audit-details">
        <summary>この解釈通知DBの検証・再構成情報</summary>
        <div className="notice-audit-body">
          <VerificationSummary layerId="rouki25-dayservice" />

          <section className="section">
            <h2>確認状況</h2>
            <p>
              本文候補は{items.length}項目、そのうち独立機械照合PASSは{independentPass}項目です。
              現行性は{currentnessHold}項目がHOLDです。本文候補の整合性と、
              現在有効な本文であることの証明を分けて扱っています。
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
    </article>
  );
}
