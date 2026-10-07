export type ActionToolRecord = {
  issueHref: string;
  href: string;
  title: string;
  evidenceHref: string;
};

export const actionToolRoutes: ActionToolRecord[] = [
  {
    issueHref: "/issues/information-search",
    href: "/tools/information-inventory",
    title: "情報探索の棚卸しシート",
    evidenceHref: "/issues/information-search#evidence",
  },
  {
    issueHref: "/issues/documentation",
    href: "/tools/documentation-review",
    title: "記録業務の見直しシート",
    evidenceHref: "/issues/documentation#evidence",
  },
  {
    issueHref: "/issues/training-handover",
    href: "/tools/training-handover-inventory",
    title: "引き継ぎ情報・研修資源の正本整理シート",
    evidenceHref: "/issues/training-handover#evidence",
  },
  {
    issueHref: "/issues/communication-collaboration",
    href: "/tools/communication-review",
    title: "問い合わせ・確認往復の棚卸しシート",
    evidenceHref: "/issues/communication-collaboration#evidence",
  },
  {
    issueHref: "/issues/productivity-utilization",
    href: "/tools/work-time-review",
    title: "業務時間・待ち・間接業務の棚卸しシート",
    evidenceHref: "/issues/productivity-utilization#evidence",
  },
];

export function actionToolForIssue(issueHref: string) {
  return actionToolRoutes.find((tool) => tool.issueHref === issueHref);
}
