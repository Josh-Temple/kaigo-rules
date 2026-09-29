export type IssueGroup = "日常業務" | "人材・組織" | "経営・生産性";

export type IssueRecord = {
  number: string;
  title: string;
  shortTitle: string;
  body: string;
  status: "調査公開";
  href: string;
  group: IssueGroup;
  keywords: string[];
};

export const issueGroups: IssueGroup[] = ["日常業務", "人材・組織", "経営・生産性"];

export const issueRegistry: IssueRecord[] = [
  {
    number: "01",
    title: "必要な情報を探すのに時間がかかる",
    shortTitle: "情報探索",
    body: "制度、通知、事業所内資料など、散らばった情報への到達時間を短くする。",
    status: "調査公開",
    href: "/issues/information-search",
    group: "日常業務",
    keywords: ["検索", "制度", "通知", "Q&A", "マニュアル", "情報", "FAQ", "AI検索"],
  },
  {
    number: "02",
    title: "記録・文書作成に時間がかかる",
    shortTitle: "記録・文書",
    body: "記録、報告、転記など、繰り返し発生する文書作業をどこから減らすか。",
    status: "調査公開",
    href: "/issues/documentation",
    group: "日常業務",
    keywords: ["記録", "文書", "転記", "報告", "音声入力", "AI draft", "データ再利用"],
  },
  {
    number: "03",
    title: "職員教育・引き継ぎが属人化する",
    shortTitle: "教育・引き継ぎ",
    body: "研修、質問対応、引き継ぎを、正本・短い教材・peer learningで支える方法を整理する。",
    status: "調査公開",
    href: "/issues/training-handover",
    group: "人材・組織",
    keywords: ["研修", "教育", "引き継ぎ", "新人", "onboarding", "FAQ", "mentor", "人材"],
  },
  {
    number: "04",
    title: "問い合わせ・連携の負担が大きい",
    shortTitle: "問い合わせ・連携",
    body: "電話、FAX、確認の往復を、self-service・structured exchange・適切なescalationで減らす。",
    status: "調査公開",
    href: "/issues/communication-collaboration",
    group: "日常業務",
    keywords: ["問い合わせ", "連携", "電話", "FAX", "ケアプラン", "情報共有", "多職種", "家族"],
  },
  {
    number: "05",
    title: "稼働率・生産性を改善したい",
    shortTitle: "稼働率・生産性",
    body: "直接ケア、間接業務、待ち・調整、staffingを分け、質と負担を損なわず改善する。",
    status: "調査公開",
    href: "/issues/productivity-utilization",
    group: "経営・生産性",
    keywords: ["稼働率", "生産性", "staffing", "配置", "スケジュール", "残業", "直接ケア", "経営"],
  },
];

export function searchableIssueText(issue: IssueRecord) {
  return [
    issue.title,
    issue.shortTitle,
    issue.body,
    issue.group,
    ...issue.keywords,
  ]
    .join(" ")
    .toLocaleLowerCase("ja");
}
