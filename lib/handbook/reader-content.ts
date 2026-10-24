/**
 * Reader-facing projection. The authoritative, unreviewed chapter text stays
 * in data/handbook-content.json and is never rewritten by this module.
 *
 * Never raise legal-currentness or verified-source claims through display copy.
 */
export const DAY_SERVICE_STAFFING = [
  {
    id: "life-counselor",
    heading: "生活相談員",
    brief: "提供時間に応じた勤務時間数を確保します。",
    points: [
      "サービスを提供する日ごとに、生活相談員の勤務時間数の合計を確認します。",
      "通所介護の提供に専ら従事する時間の合計を、事業所のサービス提供時間帯の長さで割った数が、1以上となるように配置します。",
    ],
    reference: "基準省令第93条第1項第1号",
  },
  {
    id: "nurse",
    heading: "看護職員",
    brief: "提供単位ごとに、看護師または准看護師を確保します。",
    points: [
      "看護職員は、看護師または准看護師です。",
      "サービスの提供単位ごとに、専ら通所介護の提供に当たる看護職員を1人以上確保するために必要な数を配置します。",
    ],
    reference: "基準省令第93条第1項第2号",
  },
  {
    id: "care-worker",
    heading: "介護職員",
    brief: "利用者数と提供時間に応じて配置し、常時1人以上従事させます。",
    points: [
      "提供単位ごとに、専ら通所介護に従事する介護職員の勤務時間数を合計します。",
      "この合計を単位のサービス提供時間数で割った数が、利用者15人までは1以上、15人を超える場合は「1＋（15人を超えた人数÷5）」以上となるように配置します。",
      "時間数による計算とは別に、提供単位ごとに介護職員を常時1人以上従事させます。",
      "利用者の処遇に支障がない場合は、他の提供単位の介護職員として従事することもできます。",
    ],
    reference: "基準省令第93条第1項第3号、第2・3項",
  },
  {
    id: "functional-training",
    heading: "機能訓練指導員",
    brief: "必要な訓練を行う能力がある人を1人以上配置します。",
    points: [
      "日常生活に必要な機能の低下を防ぐための訓練を行う能力がある人を、1人以上配置します。",
      "機能訓練指導員は、同じ事業所のほかの職務にも従事できます。",
    ],
    reference: "基準省令第93条第1項第4号、第5項",
  },
  {
    id: "manager",
    heading: "管理者",
    brief: "事業所ごとに常勤の管理者を置きます。",
    points: [
      "事業所ごとに、原則として管理者の職務に専ら従事する常勤の管理者を置きます。",
      "事業所の管理に支障がない場合は、その事業所のほかの職務や、別の事業所・施設等の職務と兼務できます。",
    ],
    reference: "基準省令第94条",
  },
];

export const DAY_SERVICE_STAFFING_SHARED = [
  {
    heading: "常勤職員の配置",
    text: "生活相談員または介護職員のうち、少なくとも1人は常勤でなければなりません。",
    reference: "基準省令第93条第6項",
  },
  {
    heading: "提供単位と一体運営",
    text: "「提供単位」は、同時に1人または複数の利用者に一体的に提供する通所介護を指します。所定の第一号通所事業と同じ事業所で一体的に運営する場合は、市町村が定めた人員基準を満たすことで、通所介護の基準を満たしたとみなされる場合があります。双方の指定や事業の範囲など、条文の条件を確認してください。",
    reference: "基準省令第93条第4・7項",
  },
];

/**
 * Only divert unmistakable drafting/source-index technical notes. Never
 * suppress text: the original note is returned verbatim for a details panel.
 * Mixed practical explanations are split at the specific internal-file marker.
 */
export function separateHandbookParagraphs(paragraphs) {
  const reader = [];
  const editorial = [];
  for (const paragraph of paragraphs) {
    if (!/data\/(?:services\/|qa-|notice-|care-|handbook-|remuneration-)/u.test(paragraph) &&
        !paragraph.includes("出典候補：")) {
      reader.push(paragraph);
      continue;
    }
    const marker = /(根拠候補は収載済みの\s*data\/|参照候補は\s*data\/|原典候補は\s*data\/|出典候補：)/u;
    const match = marker.exec(paragraph);
    if (!match) {
      reader.push(paragraph);
      continue;
    }
    const at = match.index;
    const first = paragraph.slice(0, at).trim();
    const note = paragraph.slice(at).trim();
    if (first) reader.push(first);
    if (note) editorial.push(note);
  }
  return { reader, editorial };
}
