export type PracticalGuideLink = {
  label: string;
  href: string;
  detail: string;
};

export type PracticalGuideJourney = {
  id: string;
  title: string;
  summary: string;
  firstChecks: string[];
  databaseLinks: PracticalGuideLink[];
  officialSourceIds: string[];
  caution?: string;
};

export const practicalGuidePolicy = {
  workingLabel: "実務ガイド",
  purpose:
    "実務の目的から、公開済みの制度DBと公式資料へ進むための案内です。",
  safety:
    "複数資料を組み合わせた結論や個別案件への判断はここでは示さず、確認すべき原典とDB内の該当情報を案内します。",
} as const;

export const practicalGuideJourneys: PracticalGuideJourney[] = [
  {
    id: "standards",
    title: "人員・設備・運営基準を確認する",
    summary:
      "まず基準省令DBで該当する条文を探し、対象サービスの公開範囲をサービス別ページで確認します。",
    firstChecks: [
      "対象サービスを確認する",
      "人員・設備・運営のどの基準を確認したいか整理する",
      "DB上の条文と公式本文の両方を確認する",
    ],
    databaseLinks: [
      {
        label: "基準省令DBを見る",
        href: "/rules",
        detail: "公開済みの基準省令本文とサービスへの適用情報を確認します。",
      },
      {
        label: "「人員」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("人員")}`,
        detail: "法令・基準省令・通知・国Q&Aの公開データから関連項目を探します。",
      },
      {
        label: "サービス別の公開情報を見る",
        href: "/services",
        detail: "対象サービスで公開済みの制度情報へ進みます。",
      },
    ],
    officialSourceIds: ["egov-home-care-standards"],
    caution:
      "基準省令DBの公開範囲は順次拡大中です。対象サービスに必要な別の基準省令や自治体独自基準がある場合は、所管行政庁の情報も確認してください。",
  },
  {
    id: "designation",
    title: "指定・更新・届出の根拠を確認する",
    summary:
      "介護保険法の指定関係規定と、厚生労働省の指定申請等の案内を起点に確認します。",
    firstChecks: [
      "対象サービスと指定権者を確認する",
      "新規指定・更新・変更届など、確認したい手続の種類を整理する",
      "全国共通の根拠と、自治体ごとの提出方法・期限を分けて確認する",
    ],
    databaseLinks: [
      {
        label: "介護保険法DBを見る",
        href: "/law",
        detail: "指定・監督等に関する法令本文を確認します。",
      },
      {
        label: "「指定」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("指定")}`,
        detail: "公開済みDBから指定に関係する項目を横断検索します。",
      },
      {
        label: "サービス別の公開情報を見る",
        href: "/services",
        detail: "サービス固有の基準・通知・報酬への入口を確認します。",
      },
    ],
    officialSourceIds: ["egov-care-insurance-act", "mhlw-application-forms"],
    caution:
      "申請先、事前相談、提出期限、様式の運用は自治体によって異なる場合があります。最終的な手続は指定権者の案内を確認してください。",
  },
  {
    id: "remuneration",
    title: "報酬・加算の根拠を確認する",
    summary:
      "報酬基準と算定上の留意事項を分けて確認し、必要に応じて国Q&Aも検索します。",
    firstChecks: [
      "対象サービスを確認する",
      "基本報酬・加算・減算のどれを確認するか整理する",
      "報酬告示、算定上の留意事項、国Q&Aを別々の根拠として確認する",
    ],
    databaseLinks: [
      {
        label: "報酬基準DBの入口を見る",
        href: "/databases#remuneration",
        detail: "公開済みのサービス別報酬基準へ進みます。",
      },
      {
        label: "算定上の留意事項の入口を見る",
        href: "/databases#fee-guidance",
        detail: "サービス別に保持している算定上の留意事項へ進みます。",
      },
      {
        label: "国Q&Aで「加算」を検索",
        href: `/qa?q=${encodeURIComponent("加算")}`,
        detail: "厚生労働省Q&Aの収載データから関連項目を探します。",
      },
    ],
    officialSourceIds: ["mhlw-r8-reform-landing"],
    caution:
      "複数資料から算定可否を自動判定するガイドではありません。個別の算定判断は、該当する告示・通知・Q&Aの原文と最新改定を確認してください。",
  },
  {
    id: "qa",
    title: "国Q&Aを探す",
    summary:
      "厚生労働省の介護サービス関係Q&Aを、キーワードやサービス分類から探します。",
    firstChecks: [
      "確認したい論点を短いキーワードにする",
      "対象サービスを絞れる場合はサービス分類も指定する",
      "Q&Aの収載と現行性確認は別であることを確認する",
    ],
    databaseLinks: [
      {
        label: "国Q&A DBを検索する",
        href: "/qa",
        detail: "質問・回答・トピック・サービス分類から検索します。",
      },
      {
        label: "制度DB全体から探す",
        href: "/databases/search",
        detail: "法令・基準省令・公開済み通知・国Q&Aを同じキーワードで探します。",
      },
    ],
    officialSourceIds: ["mhlw-qa"],
    caution:
      "Q&Aは個々の項目について現行性が未確認のものを含みます。重要な判断では、現在の法令・通知との関係を原典で確認してください。",
  },
];
