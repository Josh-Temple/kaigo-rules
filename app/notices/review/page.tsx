import Link from "next/link";
import packetData from "../../../data/notice-review-packet.json";

type Evidence = {
  snapshot_id: string;
  role: string | null;
  source_id: string;
  source_title: string | null;
  publisher: string | null;
  source_url: string | null;
  page_start: number | null;
  page_end: number | null;
  source_pdf_sha256: string | null;
  snapshot_body_sha256: string | null;
  operation: string | null;
  note: string | null;
};

type ReplayStep = {
  step: number;
  snapshot_id: string;
  operation: string;
  note?: string | null;
};

type ReviewItem = {
  notice_id: string;
  family: string;
  section: string;
  title: string;
  number_path: string[];
  effective_as_of: string | null;
  candidate_text: string;
  candidate_text_sha256: string;
  reconstruction_status: string;
  human_verification_status: string;
  baseline_snapshot_id: string;
  replay_order: ReplayStep[];
  source_evidence: Evidence[];
  independent_verification: {
    result: string;
    recorded_candidate_sha256: string | null;
    workflow_run_url: string | null;
    verified_at: string | null;
  };
  reviewer_checklist: string[];
  reviewer_decision: string | null;
  reviewer_note: string | null;
  reviewed_at: string | null;
  reviewed_candidate_sha256: string | null;
};

type ReviewPacket = {
  scope: string;
  policy: string;
  independent_verification_record: {
    result: string;
    workflow_run_url: string | null;
    verified_at: string | null;
    verified_main_sha: string | null;
  };
  items: ReviewItem[];
};

const packet = packetData as unknown as ReviewPacket;

const sectionOrder = ["人員に関する基準", "設備に関する基準", "運営に関する基準"];

const pageRange = (evidence: Evidence) => {
  if (evidence.page_start == null) return "ページ不明";
  if (evidence.page_end == null || evidence.page_start === evidence.page_end) {
    return `PDF p.${evidence.page_start}`;
  }
  return `PDF pp.${evidence.page_start}–${evidence.page_end}`;
};

const sourceHref = (evidence: Evidence) => {
  if (!evidence.source_url) return null;
  if (evidence.page_start == null) return evidence.source_url;
  return `${evidence.source_url}#page=${evidence.page_start}`;
};

export default function NoticeReviewPage() {
  const independentPass = packet.items.filter(
    (item) => item.independent_verification.result === "PASS"
  ).length;
  const reviewed = packet.items.filter(
    (item) =>
      item.reviewer_decision &&
      item.reviewed_candidate_sha256 === item.candidate_text_sha256
  ).length;

  const groups = sectionOrder.map((section) => ({
    section,
    items: packet.items.filter((item) => item.section === section),
  }));

  return (
    <article className="answer-page notice-review-page">
      <p className="eyebrow">HUMAN REVIEW WORKSPACE</p>
      <h1>老企第25号 22項目レビュー</h1>
      <p className="lead">
        機械再構成した本文候補を、一次資料・改正適用順・独立機械照合の記録と並べて確認するための画面です。
      </p>

      <div className="notice review-warning">
        <strong>この画面を開いただけでは人手確認済みになりません。</strong><br />
        実際に一次資料と照合した後、確認した candidate hash とともに
        <code> notice-current-review.json </code>へ記録します。
      </div>

      <section className="rules-stats notice-review-stats" aria-label="レビュー進捗">
        <div><strong>{packet.items.length}</strong><span>レビュー対象</span></div>
        <div><strong>{independentPass}</strong><span>独立機械照合PASS</span></div>
        <div><strong>{reviewed}</strong><span>人手確認済み</span></div>
        <div><strong>{packet.items.length - reviewed}</strong><span>残り</span></div>
      </section>

      <section className="section review-procedure">
        <div className="review-section-head">
          <div>
            <h2>確認手順</h2>
            <p className="meta">スマホでは各項目を1件ずつ開いて確認します。</p>
          </div>
          <Link href="/notices">通知DBへ戻る</Link>
        </div>
        <ol>
          <li>本文候補を読む。</li>
          <li>baseline と patch の一次資料を、記載ページから確認する。</li>
          <li>改正の適用順と、後続改正で当該項目が変わっていないことを確認する。</li>
          <li>独立機械照合の hash と現在の candidate hash が一致していることを確認する。</li>
          <li>確認後に、確認した candidate hash をレビュー台帳へ記録する。</li>
        </ol>
      </section>

      <nav className="review-jump" aria-label="レビュー項目への移動">
        {groups.map((group) => (
          <a href={`#${group.section}`} key={group.section}>
            {group.section} <span>{group.items.length}</span>
          </a>
        ))}
      </nav>

      {groups.map((group) => (
        <section className="section review-section" id={group.section} key={group.section}>
          <div className="review-section-head">
            <div>
              <p className="eyebrow">SECTION</p>
              <h2>{group.section}</h2>
            </div>
            <span className="meta">{group.items.length}項目</span>
          </div>

          <div className="review-item-list">
            {group.items.map((item, index) => {
              const reviewCurrent =
                Boolean(item.reviewer_decision) &&
                item.reviewed_candidate_sha256 === item.candidate_text_sha256;
              const independentCurrent =
                item.independent_verification.result === "PASS" &&
                item.independent_verification.recorded_candidate_sha256 ===
                  item.candidate_text_sha256;

              return (
                <details
                  className="review-item"
                  id={item.notice_id}
                  key={item.notice_id}
                  open={index === 0 && group.section === "人員に関する基準"}
                >
                  <summary>
                    <span className="review-item-number">{item.number_path.at(-1)}</span>
                    <span className="review-item-title">{item.title}</span>
                    <span className={reviewCurrent ? "review-state review-state-done" : "review-state"}>
                      {reviewCurrent ? "人手確認済み" : "未確認"}
                    </span>
                  </summary>

                  <div className="review-item-body">
                    <div className="review-status-line">
                      <span className={independentCurrent ? "review-chip review-chip-pass" : "review-chip"}>
                        独立照合 {independentCurrent ? "PASS" : "要再確認"}
                      </span>
                      <span className="review-chip">基準日 {item.effective_as_of || "不明"}</span>
                    </div>

                    <section className="review-candidate" aria-labelledby={`${item.notice_id}-candidate`}>
                      <div className="review-subhead">
                        <h3 id={`${item.notice_id}-candidate`}>本文候補</h3>
                        <span className="meta">machine reconstructed</span>
                      </div>
                      <p>{item.candidate_text}</p>
                      <p className="hash">
                        candidate SHA-256<br />{item.candidate_text_sha256}
                      </p>
                    </section>

                    <section className="review-block">
                      <h3>改正適用順</h3>
                      <div className="review-replay">
                        {item.replay_order.map((step) => (
                          <div className="review-replay-row" key={`${item.notice_id}-${step.step}`}>
                            <span>{step.step === 0 ? "基準" : `+${step.step}`}</span>
                            <div>
                              <strong>{step.snapshot_id}</strong>
                              <p className="meta">{step.operation}{step.note ? ` / ${step.note}` : ""}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </section>

                    <section className="review-block">
                      <h3>一次資料</h3>
                      <div className="review-evidence-list">
                        {item.source_evidence.map((evidence) => {
                          const href = sourceHref(evidence);
                          return (
                            <div className="review-evidence" key={evidence.snapshot_id}>
                              <div className="review-evidence-head">
                                <span className="review-evidence-role">{evidence.role || "evidence"}</span>
                                <span className="meta">{pageRange(evidence)}</span>
                              </div>
                              <p>
                                {href ? (
                                  <a href={href} target="_blank" rel="noreferrer">
                                    {evidence.source_title || evidence.source_id}
                                  </a>
                                ) : (
                                  evidence.source_title || evidence.source_id
                                )}
                              </p>
                              {evidence.note ? <p className="meta">{evidence.note}</p> : null}
                              <details className="review-hash-details">
                                <summary>hash を確認</summary>
                                <p className="hash">PDF: {evidence.source_pdf_sha256 || "—"}</p>
                                <p className="hash">snapshot: {evidence.snapshot_body_sha256 || "—"}</p>
                              </details>
                            </div>
                          );
                        })}
                      </div>
                    </section>

                    <section className="review-block">
                      <h3>レビューチェック</h3>
                      <ul className="review-checklist">
                        {item.reviewer_checklist.map((check) => (
                          <li key={check}>{check}</li>
                        ))}
                      </ul>
                      <p className="meta">
                        判定記録：{item.reviewer_decision || "未記録"}
                        {item.reviewed_at ? ` / ${item.reviewed_at}` : ""}
                      </p>
                    </section>
                  </div>
                </details>
              );
            })}
          </div>
        </section>
      ))}

      <section className="section">
        <h2>独立機械照合</h2>
        <p>
          このpacketに記録された22項目は、通常のimporter / assemblerとは別実装の検証器で照合されています。
          ただし、機械照合のPASSは人手確認の代替ではありません。
        </p>
        {packet.independent_verification_record.workflow_run_url ? (
          <p>
            <a
              href={packet.independent_verification_record.workflow_run_url}
              target="_blank"
              rel="noreferrer"
            >
              独立検証のGitHub Actions実行結果を見る
            </a>
          </p>
        ) : null}
        <p className="hash">verified main SHA: {packet.independent_verification_record.verified_main_sha || "—"}</p>
      </section>
    </article>
  );
}
