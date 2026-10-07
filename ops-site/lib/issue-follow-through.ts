export const RULES_HOME_HREF = "https://kaigo-rules.vercel.app/";

export const issueFollowThrough = {
  "/issues/information-search": {
    issueLabel: "情報探索",
    rulesHref: "https://kaigo-rules.vercel.app/databases/search",
    rulesLabel: "公開済み制度DBを横断検索する",
  },
  "/issues/documentation": {
    issueLabel: "記録・文書",
    rulesHref: "https://kaigo-rules.vercel.app/databases/search?q=%E8%A8%98%E9%8C%B2",
    rulesLabel: "「記録」で制度DBを確認する",
  },
  "/issues/training-handover": {
    issueLabel: "教育・引き継ぎ",
    rulesHref: "https://kaigo-rules.vercel.app/databases/search?q=%E7%A0%94%E4%BF%AE",
    rulesLabel: "「研修」で制度DBを確認する",
  },
  "/issues/communication-collaboration": {
    issueLabel: "問い合わせ・連携",
    rulesHref: "https://kaigo-rules.vercel.app/databases/search?q=%E9%80%A3%E6%90%BA",
    rulesLabel: "「連携」で制度DBを確認する",
  },
  "/issues/productivity-utilization": {
    issueLabel: "稼働率・生産性",
    rulesHref: "https://kaigo-rules.vercel.app/databases/search?q=%E4%BA%BA%E5%93%A1",
    rulesLabel: "「人員」で制度DBを確認する",
  },
} as const;

export type IssuePath = keyof typeof issueFollowThrough;

export function buildOpsFeedbackHref(issuePath: IssuePath) {
  const config = issueFollowThrough[issuePath];
  const title = `[Kaigo Opsフィードバック] ${config.issueLabel}`;
  const body = [
    "## 対象",
    `Kaigo Ops ${issuePath}`,
    "",
    "## 何を試したか",
    "",
    "## どこで止まったか",
    "",
    "## 何が足りなかったか",
    "",
    "## 入力しないでください",
    "氏名、利用者情報、介護記録、事業所の非公開情報などは記載しないでください。",
  ].join("\n");

  return (
    "https://github.com/Josh-Temple/kaigo-rules/issues/new?title=" +
    encodeURIComponent(title) +
    "&body=" +
    encodeURIComponent(body)
  );
}
