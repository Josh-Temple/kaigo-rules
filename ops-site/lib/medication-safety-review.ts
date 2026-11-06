/**
 * Preview-only workflow checklist. This module must not receive person, medicine,
 * prescription, dosage, incident narrative or institution identifiers.
 * All output strings are fixed; nothing is interpolated from user input.
 */
export const PROCESS_STAGES = [
  { value: "unselected", label: "工程を選択してください" },
  { value: "instruction-update", label: "変更情報の受領・共有" },
  { value: "preparation", label: "配薬準備の運用" },
  { value: "administration-check", label: "配薬・服薬確認に関する運用" },
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
  { value: "unknown", label: "まだ確認していない" },
  { value: "confirmed", label: "取扱いを把握している（自己申告・未検証）" },
  { value: "needs-review", label: "相談したい点がある" },
  { value: "not-prepared", label: "取り決めが見つからない" },
  { value: "not-applicable", label: "自分の担当範囲では扱わない（責任者確認前）" },
] as const;

/** B #459 section 8.2: shared, non-clinical result and print boundary. */
export const WORKFLOW_BOUNDARY = "この結果は平時の業務工程に関する自己申告を整理したものです。安全性・医療上の正しさ・職種権限・制度適合・事故報告の要否を判定しません。事故や服薬上の疑義が現にある場合は、このシートを使わず、所属先の正式手順に従い、管理者・関係する医療専門職に連絡してください。";

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
      lines.push(`「${field.label}」：まだ確認していません。正式な手順の所在と実際の取扱いを責任者・関係職種に確認してください。`);
    } else if (status === "needs-review") {
      lines.push(`「${field.label}」：相談したい点として、責任者・関係職種と確認してください。`);
    } else if (status === "not-prepared") {
      lines.push(`「${field.label}」：取り決めが見つからないため、正式手順の所在と整備の要否を責任者に確認してください。`);
    } else if (status === "not-applicable") {
      lines.push(`「${field.label}」：担当範囲では扱わないという自己申告です。工程の有無と担当権限を責任者・関係職種に確認してください。`);
    }
  }
  return {
    valid: true,
    lines,
    note: lines.length
      ? "これは平時の業務上の相談事項を自己申告で整理する独自の試作です。事故確率、安全性、医療判断、制度適合、実施権限を評価・認証するものではありません。"
      : "すべて「取扱いを把握している（自己申告・未検証）」を選択しました。手順の正しさ、安全性、事故防止、実施権限、制度適合を保証しません。責任者・関係専門職による確認が別途必要です。",
  };
}

function invalidReview(): ReviewResult {
  return {
    valid: false,
    lines: ["入力の形式を確認できません。点検結果は生成しません。内容を消去して最初から確認してください。"],
    note: "不正な選択値を安全な判断として処理しません。",
  };
}
