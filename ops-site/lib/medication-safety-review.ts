/**
 * Preview-only workflow checklist. This module must not receive person, medicine,
 * prescription, dosage, incident narrative or institution identifiers.
 * All output strings are fixed; nothing is interpolated from user input.
 */
export const PROCESS_STAGES = [
  { value: "unselected", label: "工程を選択してください" },
  { value: "instruction-update", label: "指示変更の受領・共有" },
  { value: "preparation", label: "準備・確認" },
  { value: "administration-check", label: "配薬・服薬確認の運用" },
  { value: "record-handover", label: "記録・引き継ぎ" },
] as const;

export const CHECK_FIELDS = [
  { key: "procedure", label: "業務手順が文書化され、現場で確認できるか" },
  { key: "roles", label: "担当と引き継ぎ先が明確か" },
  { key: "interruptions", label: "作業中断や兼務が起きた際の取り扱いを確認できるか" },
  { key: "updates", label: "変更情報の受領・共有方法を確認できるか" },
  { key: "consultation", label: "責任者・関係専門職に相談する経路があるか" },
  { key: "review", label: "変更後の振り返りを行う方法があるか" },
] as const;

export const CHECK_STATES = [
  { value: "unknown", label: "未確認" },
  { value: "confirmed", label: "確認できる（自己申告）" },
  { value: "needs-review", label: "見直しが必要" },
  { value: "not-prepared", label: "未整備" },
  { value: "not-applicable", label: "対象外（要確認）" },
] as const;

export type ProcessStage = (typeof PROCESS_STAGES)[number]["value"];
export type CheckKey = (typeof CHECK_FIELDS)[number]["key"];
export type CheckState = (typeof CHECK_STATES)[number]["value"];
export type ReviewAnswers = {
  stage: ProcessStage;
  checks: Record<CheckKey, CheckState>;
};

const stageSet = new Set<string>(PROCESS_STAGES.map(item => item.value));
const stateSet = new Set<string>(CHECK_STATES.map(item => item.value));

export function emptyReview(): ReviewAnswers {
  return {
    stage: "unselected",
    checks: Object.fromEntries(CHECK_FIELDS.map(field => [field.key, "unknown"])) as Record<CheckKey, CheckState>,
  };
}

// These are fictional, non-personal selections, not a validated incident.
export function fictionalReview(): ReviewAnswers {
  return {
    stage: "record-handover",
    checks: {
      procedure: "confirmed",
      roles: "needs-review",
      interruptions: "unknown",
      updates: "needs-review",
      consultation: "confirmed",
      review: "not-prepared",
    },
  };
}

export type ReviewResult = {
  valid: boolean;
  lines: string[];
  note: string;
};

/** Strictly reject unknown structure and values, including forged selections. */
export function deriveReview(input: unknown): ReviewResult {
  if (typeof input !== "object" || input === null || Array.isArray(input)) return invalidReview();
  const candidate = input as Record<string, unknown>;
  if (
    Object.keys(candidate).length !== 2 ||
    !Object.hasOwn(candidate, "stage") ||
    !Object.hasOwn(candidate, "checks") ||
    typeof candidate.stage !== "string" ||
    !stageSet.has(candidate.stage) ||
    typeof candidate.checks !== "object" ||
    candidate.checks === null ||
    Array.isArray(candidate.checks)
  ) return invalidReview();

  const checks = candidate.checks as Record<string, unknown>;
  const keys = CHECK_FIELDS.map(field => field.key);
  if (
    Object.keys(checks).length !== keys.length ||
    keys.some(key => !Object.hasOwn(checks, key) || typeof checks[key] !== "string" || !stateSet.has(checks[key] as string))
  ) return invalidReview();

  const lines: string[] = [];
  if (candidate.stage === "unselected") {
    lines.push("点検する工程が未選択です。まず業務工程を選んでください。");
  }
  for (const field of CHECK_FIELDS) {
    const status = checks[field.key];
    if (status === "unknown") {
      lines.push(`「${field.label}」：運用状況を正式な手順と照合して確認してください。`);
    } else if (status === "needs-review") {
      lines.push(`「${field.label}」：責任者・関係職種と見直す論点として整理してください。`);
    } else if (status === "not-prepared") {
      lines.push(`「${field.label}」：整備の必要性と担当を責任者に相談してください。`);
    } else if (status === "not-applicable") {
      lines.push(`「${field.label}」：対象外にできる範囲と理由を正式な手順に照らして確認してください。`);
    }
  }
  return {
    valid: true,
    lines,
    note: lines.length
      ? "これは相談・確認事項の整理です。事故確率、医療判断、基準適合、安全性を評価するものではありません。"
      : "すべて「確認できる」と回答されました。自己申告であり、安全性・事故防止・制度適合を保証しません。正式手順や関係専門職による確認が別途必要です。",
  };
}

function invalidReview(): ReviewResult {
  return {
    valid: false,
    lines: ["入力の形式を確認できません。点検結果は生成しません。内容を消去して最初から確認してください。"],
    note: "不正な選択値を安全な判断として処理しません。",
  };
}
