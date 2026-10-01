import registryData from "../data/verification-registry.json";

type VerificationLayer = {
  id: string;
  content_verification?: { status?: string; evidence?: string };
  currentness?: { status?: string; coverage_end?: string };
  human_review?: { status?: string };
};

const registry = registryData as { layers?: VerificationLayer[] };

const statusLabel = (value?: string) => {
  const labels: Record<string, string> = {
    PASS: "原文と独立機械照合済み",
    PASS_BOUNDED_SCOPE_ONLY: "限定範囲で原文と機械照合済み",
    HOLD: "現行性は未確定（HOLD）",
    LIVE_SOURCE_REPARSE_SCHEDULED: "継続監視中",
    MONITORED_NOT_HUMAN_VERIFIED: "継続監視中",
    NOT_REVIEWED: "人手確認未実施",
    NOT_STARTED: "未実施",
    IMPORTED_NEEDS_HUMAN_CHECK: "確認待ち",
    INGESTED_UNREVIEWED: "確認待ち",
    PARTIAL: "一部実施",
    ACCEPTED_WORK_CONTROL_RECEIPT: "受理済み・独立再照合前",
    GAP: "根拠の不足あり（GAP）",
    GAP_HISTORICAL_SOURCE_ONLY: "旧資料のみ・現行性は未確定（GAP）",
  };
  return value ? labels[value] || value : "—";
};

export default function VerificationSummary({ layerId }: { layerId: string }) {
  const layer = (registry.layers || []).find((item) => item.id === layerId);
  if (!layer) {
    throw new Error(`Unknown verification layer: ${layerId}`);
  }

  return (
    <details className="verification-summary">
      <summary>このデータの確認状態</summary>
      <div className="verification-summary-body">
        <dl className="rule-meta">
          <div>
            <dt>本文の独立確認</dt>
            <dd>{statusLabel(layer.content_verification?.status)}</dd>
          </div>
          <div>
            <dt>現行性</dt>
            <dd>{statusLabel(layer.currentness?.status)}</dd>
          </div>
          <div>
            <dt>人手確認</dt>
            <dd>{statusLabel(layer.human_review?.status)}</dd>
          </div>
        </dl>
        <p className="meta">現行性調査の対象末日：{layer.currentness?.coverage_end || "レイヤーの検証記録を参照"} / 照合記録：{layer.content_verification?.evidence || "記録なし"}</p>
        <p className="meta">
          独立確認は、一次資料からの再取得・再構成による照合結果です。現行性の確認や人手確認とは別に管理しています。
        </p>
      </div>
    </details>
  );
}

