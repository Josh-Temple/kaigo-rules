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
    brief: "提供日ごとに、事業所の提供時間に応じた生活相談員の勤務時間を確保します。",
    points: [
      "サービス提供日ごとに計算します。提供単位が複数あっても、分母は事業所が実際に通所介護を提供する時間帯の長さです。重なる単位の時間を二重に数えません。",
      "生活相談員が通所介護の提供に専ら従事した時間数の合計を、上記の事業所の提供時間数で割り、1以上となるように配置します。たとえば9～14時と13～18時の2単位なら、分母は10時間ではなく9時間です。",
    ],
    reference: "基準省令第93条第1項第1号",
  },
  {
    id: "nurse",
    heading: "看護職員",
    brief: "提供単位ごとに看護職員を確保します。提供時間中の常時専従とは異なります。",
    points: [
      "看護職員は、看護師または准看護師です。",
      "通所介護の単位ごとに、専らその提供に当たる看護職員を1人以上確保するために必要な数を配置します。",
      "横浜市の令和8年6月版手引きでは、看護職員が提供時間を通じて専従する必要はない一方、事業所との密接かつ適切な連携が必要とされています。病院・診療所・訪問看護ステーションとの契約による連携で確保する場合は、提供日ごとの利用者の健康状態の確認と、提供時間帯に相談・指示を受けられる体制を確認します。",
      "連携先に看護職員がいるというだけで配置基準を満たすわけではありません。勤務・連携の記録、資格証と急変時の連絡体制を確認します。", 
    ],
    reference: "基準省令第93条第1項第2号",
  },
  {
    id: "care-worker",
    heading: "介護職員",
    brief: "利用者数と提供時間に応じて配置し、常時1人以上従事させます。",
    points: [
      "提供単位ごとに、専ら通所介護に従事する介護職員の勤務時間数を合計します。",
      "この合計を単位のサービス提供時間数で割った数が、利用者15人までは1以上、15人を超える場合は「1＋（15人を超えた人数÷5）」以上となるように配置します。提供時間が利用者によって異なる場合は、各利用者の提供時間数の合計を利用者数で割って平均提供時間数を求め、必要な介護職員の勤務延時間数を計算します。",
      "横浜市の手引きでは、時間帯によって利用者数が異なる例について、平均提供時間数と勤務延時間数を使った計算例を示しています。単位ごとの必要時間数と、時間帯を通じた常時1人の配置を別々に確認します。", 
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
      "機能訓練指導員は、同じ事業所のほかの職務にも従事できます。横浜市の令和8年6月版手引きでは、サービス提供日や単位ごとに必ず1人を配置する基準とは区別しています。",
      "横浜市条例第91条第8項には、特定のユニット型施設に併設する場合、利用者の処遇が適切に行われると認められるときに限り、生活相談員または機能訓練指導員を置かないことができる特例があります。一般の通所介護事業所に一律に適用されるものではありません。", 
    ],
    reference: "基準省令第93条第1項第4号、第5項",
  },
  {
    id: "manager",
    heading: "管理者",
    brief: "事業所ごとに常勤の管理者を置きます。",
    points: [
      "事業所ごとに、原則として管理者の職務に専ら従事する常勤の管理者を置きます。",
      "事業所の管理に支障がない場合は、その事業所のほかの職務や、別の事業所・施設等の職務と兼務できます。兼務先の業務中も利用者の状況を把握でき、指揮命令や緊急時の対応に支障がないかを確認します。",
      "横浜市の令和8年6月版手引きには、兼務する管理者の勤務日における45分（0.75時間）という目安があります。これは横浜市が示す実務上の目安であり、全国一律の法定勤務時間ではありません。管理に必要な時間を個別に確保します。", 
    ],
    reference: "基準省令第94条",
  },
];

export const DAY_SERVICE_STAFFING_SHARED = [
  {
    heading: "常勤職員の配置",
    text: "生活相談員または介護職員のうち、事業所として少なくとも1人は常勤でなければなりません。提供単位ごと・営業日ごとに常勤者を1人ずつ置くという意味ではありません。",
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
export function separateHandbookParagraphs(paragraphs: string[]): { reader: string[]; editorial: string[] } {
  const reader: string[] = [];
  const editorial: string[] = [];
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
