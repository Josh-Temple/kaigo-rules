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

export type PracticalGuideServiceGroup = {
  id: string;
  title: string;
  serviceIds: string[];
  note?: string;
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
  {
    id: "staffing",
    title: "人員配置の基準を調べる",
    summary:
      "人員配置に関する基準省令の条文を起点に、必要に応じて解釈通知や国Q&Aへ進みます。",
    firstChecks: [
      "対象サービスを確認する",
      "職種・配置人数・勤務体制など、確認したい論点を整理する",
      "基準省令の本文と、必要に応じて解釈通知を別々に確認する",
    ],
    databaseLinks: [
      {
        label: "「人員」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("人員")}`,
        detail: "公開済みの法令・基準省令・通知・国Q&Aから関連項目を探します。",
      },
      {
        label: "基準省令DBを見る",
        href: "/rules",
        detail: "人員基準を含む基準省令の公開本文を確認します。",
      },
      {
        label: "基準解釈通知DBを見る",
        href: "/notices",
        detail: "公開済みの解釈通知から人員配置に関する説明を探します。",
      },
    ],
    officialSourceIds: ["egov-home-care-standards", "mhlw-interpretation-html"],
    caution:
      "ガイド上では必要人数や配置可否を個別判定しません。対象サービスの条文、解釈通知、自治体の指定基準を確認してください。",
  },
  {
    id: "equipment",
    title: "設備基準を調べる",
    summary:
      "設備・専用区画・備品などの基準を、基準省令DBと公式原文から確認します。",
    firstChecks: [
      "対象サービスを確認する",
      "設備、区画、備品など確認したい対象を整理する",
      "条文の適用範囲と、自治体独自基準の有無を分けて確認する",
    ],
    databaseLinks: [
      {
        label: "「設備」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("設備")}`,
        detail: "公開済みDBから設備基準に関係する項目を横断検索します。",
      },
      {
        label: "基準省令DBを見る",
        href: "/rules",
        detail: "設備基準を含む基準省令本文を確認します。",
      },
      {
        label: "サービス別の公開情報を見る",
        href: "/services",
        detail: "対象サービスに絞って公開中の制度情報へ進みます。",
      },
    ],
    officialSourceIds: ["egov-home-care-standards"],
    caution:
      "面積・設備要件の個別適合性はここでは判定しません。該当条文と指定権者の条例・手引を確認してください。",
  },
  {
    id: "operations",
    title: "運営基準を調べる",
    summary:
      "記録、掲示、苦情対応、事故対応などの運営基準を、基準省令と解釈通知から探します。",
    firstChecks: [
      "対象サービスを確認する",
      "確認したい運営業務を短いキーワードにする",
      "基準省令と解釈通知の役割を分けて確認する",
    ],
    databaseLinks: [
      {
        label: "「運営」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("運営")}`,
        detail: "公開済みDBから運営基準に関係する項目を横断検索します。",
      },
      {
        label: "基準省令DBを見る",
        href: "/rules",
        detail: "運営に関する基準省令本文を確認します。",
      },
      {
        label: "基準解釈通知DBを見る",
        href: "/notices",
        detail: "公開済みの解釈通知から具体的な説明を探します。",
      },
    ],
    officialSourceIds: ["egov-home-care-standards", "mhlw-interpretation-html"],
    caution:
      "複数条文や通知を組み合わせた個別事案の結論は示しません。必要な一次資料を確認するための入口として利用してください。",
  },
  {
    id: "fee-guidance",
    title: "算定上の留意事項を探す",
    summary:
      "報酬告示とは分けて、算定上の留意事項や改定資料を確認します。",
    firstChecks: [
      "対象サービスと報酬項目を確認する",
      "告示上の算定要件と、留意事項通知の説明を分けて確認する",
      "改定時期が関係する場合は最新の改定資料も確認する",
    ],
    databaseLinks: [
      {
        label: "算定上の留意事項の入口を見る",
        href: "/databases#fee-guidance",
        detail: "公開済みの算定上の留意事項DBへ進みます。",
      },
      {
        label: "「算定」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("算定")}`,
        detail: "公開済みDBから算定に関係する項目を横断検索します。",
      },
      {
        label: "国Q&Aで「算定」を検索",
        href: `/qa?q=${encodeURIComponent("算定")}`,
        detail: "厚生労働省Q&Aから具体例を探します。",
      },
    ],
    officialSourceIds: ["mhlw-r8-reform-landing", "mhlw-r8-fee-interpretation-amendment"],
    caution:
      "留意事項やQ&Aを組み合わせた算定可否の個別判定は行いません。該当する告示・通知・Q&Aの原文を確認してください。",
  },
  {
    id: "unit-price",
    title: "単価・地域区分を確認する",
    summary:
      "一単位単価の告示と、公開中の地域区分DBを分けて確認します。",
    firstChecks: [
      "対象サービスを確認する",
      "事業所所在地の地域区分を確認する",
      "サービスに対応する一単位単価の区分を公式告示で確認する",
    ],
    databaseLinks: [
      {
        label: "一単位単価・地域区分DBを見る",
        href: "/fees/unit-price",
        detail: "現在公開中の通所介護向け地域区分・一単位単価DBを確認します。",
      },
      {
        label: "「地域区分」で制度DBを検索",
        href: `/databases/search?q=${encodeURIComponent("地域区分")}`,
        detail: "公開済みDBから地域区分に関係する情報を探します。",
      },
    ],
    officialSourceIds: ["mhlw-unit-price-current"],
    caution:
      "公開中の一単位単価DBは通所介護向けです。他サービスは、厚生労働省告示のサービス区分と地域区分を原文で確認してください。",
  }
];


export const practicalGuideServiceGroups: PracticalGuideServiceGroup[] = [
  { id: "dayservice", title: "通所介護", serviceIds: ["dayservice"] },
  { id: "homevisit", title: "訪問介護", serviceIds: ["homevisit"] },
  { id: "homebath", title: "訪問入浴介護", serviceIds: ["homebath", "preventive-homebath"] },
  { id: "homenursing", title: "訪問看護", serviceIds: ["homenursing", "preventive-homenursing"] },
  { id: "homerehab", title: "訪問リハビリテーション", serviceIds: ["homerehab", "preventive-homerehab"] },
  { id: "homecaremanagement", title: "居宅療養管理指導", serviceIds: ["homecaremanagement", "preventive-homecaremanagement"] },
  { id: "dayrehab", title: "通所リハビリテーション", serviceIds: ["dayrehab", "preventive-dayrehab"] },
  { id: "shortstay-life", title: "短期入所生活介護", serviceIds: ["shortstay-life", "preventive-shortstay-life"] },
  { id: "shortstay-medical", title: "短期入所療養介護", serviceIds: ["shortstay-medical", "preventive-shortstay-medical"] },
  { id: "specific-facility", title: "特定施設入居者生活介護", serviceIds: ["specific-facility", "preventive-specific-facility"] },
  { id: "welfare-equipment-rental", title: "福祉用具貸与", serviceIds: ["welfare-equipment-rental", "preventive-welfare-equipment-rental"] },
  { id: "specific-welfare-equipment-sale", title: "特定福祉用具販売", serviceIds: ["specific-welfare-equipment-sale", "specific-preventive-welfare-equipment-sale"] },
  { id: "care-management", title: "居宅介護支援", serviceIds: ["care-management"] },
  { id: "preventive-support", title: "介護予防支援", serviceIds: ["preventive-support"], note: "介護予防支援は、対応する通常サービスへ統合せず独立して案内します。" },
];
