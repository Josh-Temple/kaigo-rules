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
    issueHref: "/issues/training-handover",
    href: "/tools/training-handover-inventory",
    title: "引き継ぎ情報・研修資源の正本整理シート",
    evidenceHref: "/issues/training-handover#evidence",
  },
];

export function actionToolForIssue(issueHref: string) {
  return actionToolRoutes.find((tool) => tool.issueHref === issueHref);
}
