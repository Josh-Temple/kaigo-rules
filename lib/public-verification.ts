export type VerificationKind = "content" | "currentness" | "human";

export function publicVerificationLabel(
  value: string | undefined,
  kind: VerificationKind,
): string {
  if (!value) return "確認情報なし";

  if (kind === "content") {
    const labels: Record<string, string> = {
      PASS: "確認済み",
      PASS_BOUNDED_SCOPE_ONLY: "対象範囲を限定して確認済み",
      PARTIAL: "一部確認済み",
      ACCEPTED_WORK_CONTROL_RECEIPT: "確認中",
      IMPORTED_NEEDS_HUMAN_CHECK: "確認中",
      INGESTED_UNREVIEWED: "確認中",
      NOT_STARTED: "未確認",
      NOT_ESTABLISHED: "未確認",
    };
    return labels[value] || "確認情報あり";
  }

  if (kind === "currentness") {
    const labels: Record<string, string> = {
      PASS: "確認済み",
      VERIFIED_CURRENT: "確認済み",
      LIVE_SOURCE_REPARSE_SCHEDULED: "確認中",
      HOLD: "確認中",
      PARTIAL: "確認中",
      BLOCKED: "確認中",
      GAP: "確認中",
      GAP_HISTORICAL_SOURCE_ONLY: "旧資料のみ・現行性未確認",
      NOT_STARTED: "未確認",
      NOT_ESTABLISHED: "未確認",
    };
    return labels[value] || "確認情報あり";
  }

  const labels: Record<string, string> = {
    PASS: "確認済み",
    REVIEWED: "確認済み",
    HUMAN_VERIFIED: "確認済み",
    NOT_REVIEWED: "未実施",
    NOT_STARTED: "未実施",
    IMPORTED_NEEDS_HUMAN_CHECK: "未実施",
    INGESTED_UNREVIEWED: "未実施",
    MONITORED_NOT_HUMAN_VERIFIED: "未実施",
  };
  return labels[value] || "確認情報あり";
}
