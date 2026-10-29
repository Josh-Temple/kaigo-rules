/**
 * Dayservice-only editorial presentation. The canonical handbook JSON, evidence,
 * legal conditions, and review statuses are intentionally not modified.
 *
 * Changes are limited to exact previously observed management phrases. If the
 * underlying prose changes, an unmatched phrase stays visible for re-review.
 */
const roleHeadings: Record<string, readonly string[]> = {
  "life-counselor": ["配置と勤務時間", "横浜市の勤務時間に関する参考情報", "資格は指定権者の基準を確認"],
  nurse: ["単位ごとの配置と勤務", "医療機関等と連携する場合", "国Q&Aで確認すること"],
  "care-worker": ["平均提供時間数の考え方", "必要な勤務延時間数", "勤務時間の計算例", "提供時間中の配置と兼務"],
  "functional-training": ["配置人数と兼務", "横浜市の資格案内（参考）", "横浜市条例の併設特例"],
  manager: ["管理者の配置と兼務", "横浜市の兼務に関する参考情報", "45分は全国共通の法定基準ではありません"],
};

const chapterHeadings: Record<string, readonly string[]> = {
  applicability: ["通所介護の概要", "適用する基準と指定区分", "対象者とサービスの内容", "サービスの基本方針", "目標・計画とサービスの評価", "サービス提供時の配慮", "他の通所サービスとの区別"],
  designation: ["申請書・勤務表と事業所の実態", "指定・みなし・一体的運営の区別", "申請後に条件が変わったとき"],
  staffing: ["利用者数・提供時間と職種別の勤務", "人数・資格の確認先", "職種別の配置基準", "常時配置・兼務・常勤", "第一号通所事業と一体運営する場合", "管理者の常勤・専従と兼務"],
  equipment: ["設備の現況と使い方", "サービス区分による基準の違い"],
  operations: ["利用開始からサービス提供まで", "提供記録とサービス区分の確認"],
  records: ["利用者ごとの記録と勤務実績", "様式・閲覧権限・保存期間", "日々の記録と事故・苦情等の記録"],
  safeguarding: ["本人の意思・説明・プライバシー", "相談・連絡の記録と共有範囲"],
  incident_and_infection: ["送迎事故・転倒・感染への備え", "報告・家族連絡と再開の判断"],
  business_continuity: ["中断時の安全と支援の可否", "代替手順・連絡・再開後の確認"],
  remuneration: ["利用実績と算定条件", "基本報酬・加算・減算・その他の費用", "途中帰宅・利用時間短縮の日"],
  additions: ["加算要件を種類別に確認", "記録・体制・届出の突合", "早退した日の確認例"],
  deductions: ["減算の対象と適用時点", "実績の不一致を確認した場合", "欠席・変更の確認例", "定員超過と人員不足を区別"],
  notifications: ["変更内容と届出の要否", "提出・受領・内部周知の記録"],
  national_qa: ["質問の前提と確認する資料", "この章でのQ&Aの確認状況"],
  sources_and_history: ["資料の種類と確認できる範囲", "改正・準用・地域の基準の確認"],
};

export function dayserviceRoleParagraphHeading(roleId: string, index: number): string | null {
  return roleHeadings[roleId]?.[index] ?? null;
}

export function dayserviceChapterParagraphHeading(chapterId: string, index: number): string | null {
  return chapterHeadings[chapterId]?.[index] ?? null;
}

const feeFiles = "data/fee-guidance-current-text-candidates.json、data/remuneration-current-meta.json、data/services/dayservice/unit-price-scope.json";
const ordinanceFiles = "根拠候補は収載済みの 共有の省令第37号条文データ data/ordinance37-nodes.json（通所介護のサービス対応は別途照合） と関連する原典索引である。";
const standardsFiles = "data/care-insurance-act-scope.json、data/ordinance37-nodes.json";
const qaFiles = "data/qa-corpus.json、data/qa-corpus-meta.json、data/qa-service-mapping.json";

/**
 * Replace only known editorial metadata; do not use broad regexes that can
 * remove a statutory condition, an exception, or an unresolved warning.
 */
export function dayserviceReadableText(chapterId: string, value: string): string {
  // Exact, redundant production phrases only. All substantive clauses and
  // uncertainty stay in the canonical data and in the displayed explanation.
  value = value
    .replaceAll("事業所で使用する書類と現況を対応付けて確認する。", "")
    .replaceAll("通所施設に通う利用者の日中の生活支援と活動を組み立てるサービス", "通所介護")
    .replaceAll("施設内の活動と実施記録の記録", "施設内の活動の実施記録")
    .replaceAll("施設内サービスの記録の実績", "施設内サービスの実績")
    .replaceAll("施設内の活動と実施記録の実施記録", "施設内の活動の実施記録")
    .replaceAll("提供形態と現況の点検：", "")
    .replaceAll("書類・記録の突合：", "")
    .replaceAll("原典・区分と未確認事項：", "適用条件（未確認）：")
    .replaceAll("実務証拠の突合：", "")
    .replaceAll("参照候補の収載だけでは", "この章の参照資料だけでは")
    .replaceAll("国Q&Aの探索課題：", "確認する例：")
    .replaceAll("（DRAFT_UNREVIEWED）", "（内容は未審査）")
    .replaceAll("自治体の案内を追記できる章です。", "自治体の現行案内で確認します。")
    .replaceAll("該当する条文と自治体の規定を確認して追記します。", "該当する条文と自治体の規定で確認します。")
    .replaceAll("連絡先、報告手順、研修、会議、記録を項目ごとに追記できます。", "連絡先・報告手順・研修・会議・記録を分けて確認します。")
    .replaceAll("項目ごとの根拠に沿って追記します。", "項目ごとの原典で確認します。")
    .replaceAll("自治体の案内と照合して追記します。", "自治体の現行案内で確認します。")
    .replaceAll("対象者、実施内容、職員体制、併算定の条件を項目ごとに確認できます。", "個別の対象者・実施内容・職員体制・併算定の条件は、原典との照合が必要です。")
    .replaceAll("この草稿で法的な該当性を断定しません", "この説明だけでは法的な該当性を断定できません")
    .replaceAll("固定の復旧期限や連絡期限をこの草稿から設定せず", "この説明だけで復旧期限や連絡期限を決めず")
    .replaceAll(`参照候補は${standardsFiles}です。scopeに当該事項が含まれるか、準用・除外や自治体条例がどう関係するかは原典で未照合です。`, "この事項への基準省令の適用、準用・除外、自治体条例との関係は、原典で未照合です。")
    .replaceAll(`${standardsFiles}は提供基準等の参照候補ですが、記載scopeだけで現行のBCP要件や自治体の判断を確定できません。`, "現行の業務継続計画（BCP）の要件や自治体の取扱いは、この章の参照資料だけでは確定できません。")
    .replaceAll(`参照候補はdata/notice-source-chain.json、data/notice-current-meta.json、data/notice-current-review.jsonと${standardsFiles}ですが、収載scopeだけから提出先・様式・期限・適用を確定できません。`, "提出先・様式・期限・適用は、この章の参照資料だけでは確定できません。")
    .replaceAll(`${qaFiles} は参照候補であり、質問本文と回答の対象条件・発出日・後続訂正を原文で照合するまでは適用を断定しない。`, "国Q&Aは、質問と回答の対象条件・発出日・後続訂正を原文で照合するまで、適用を断定しないでください。")
    .replaceAll(`通所介護の原典候補は${standardsFiles}です。報酬関係は${feeFiles}、国のQ&A照合には${qaFiles}を併用します。`, "確認する資料は、介護保険法、基準省令、介護報酬の告示・関連通知、国Q&Aです。")
    .replaceAll("これらのscope・索引・対応表は探索範囲を示す資料であり、本文の完全性、法令の現行性、当該事業所への適用を証明するものではありません。", "参照先を示す一覧だけでは、本文の完全性、法令の現行性、当該事業所への適用は確認できません。");
  if (chapterId === "staffing") {
    return value.replace("訪問系の訪問実績だけでは把握できないため、時間帯ごとの職種別勤務と利用者数を対応付けます。", "時間帯ごとの職種別勤務と利用者数を照らし合わせます。").replace(
      "収載省令37号の通所介護章の人員規定とサービス別scopeを候補に、",
      "国の基準省令第37号の通所介護に関する人員規定を参照し、",
    );
  }
  if (["designation", "equipment", "operations", "records", "incident_and_infection"].includes(chapterId)) {
    return value.replace(
      ordinanceFiles,
      "根拠となる条文と通所介護への適用関係は、国の基準省令第37号と指定権者の条例を使って確認する必要があります。",
    );
  }
  if (chapterId === "remuneration") {
    return value
      .replace(
        `参照候補は${feeFiles}ですが、索引やscopeは算定可否・単位数・現行性の証明ではありません。`,
        "関連資料の参照先は整理されていますが、掲載されているだけでは算定の可否・単位数・現行性を確認できたことにはなりません。",
      )
      .replace(
        `${feeFiles}の該当箇所と請求データを照合し`,
        "国の介護報酬告示・関連通知の該当箇所と請求データを照合し",
      );
  }
  if (chapterId === "additions") {
    return value
      .replace(
        `参照候補は${feeFiles}ですが、索引・scope・候補文書だけでは個別事業所の算定要件を確定しません。`,
        "関連資料は候補段階です。掲載資料だけで個別事業所の算定要件を確定することはできません。",
      )
      .replace(
        `${feeFiles}から正式な要件本文と参照版を確かめ`,
        "国の介護報酬告示・関連通知から要件本文と適用版を確かめ",
      );
  }
  if (chapterId === "deductions") {
    return value
      .replace(
        `参照候補は${feeFiles}であり、候補scopeに項目があること自体は当該事業所への該当を示しません。`,
        "関連資料は候補段階です。掲載されていることだけでは、この事業所への減算の適用を示しません。",
      )
      .replace(
        `${feeFiles}の原文・参照版を確認し`,
        "国の介護報酬告示・関連通知の原文と適用版を確認し",
      );
  }
  return value;
}

/**
 * Break only at sentence boundaries outside quotes/brackets. The concatenation
 * is byte-for-byte identical: provisos, numbers and citations cannot disappear.
 * A long single sentence is not mechanically rewritten or split at commas.
 */
export function readerTextParagraphs(value: string, targetLength = 110): string[] {
  const closing = new Map([["（", "）"], ["(", ")"], ["「", "」"], ["『", "』"], ["【", "】"]]);
  const stack: string[] = [];
  const sentences: string[] = [];
  let current = "";
  for (const character of value) {
    current += character;
    const close = closing.get(character);
    if (close) stack.push(close);
    else if (stack.at(-1) === character) stack.pop();
    if (character === "。" && stack.length === 0) {
      sentences.push(current);
      current = "";
    }
  }
  if (current) sentences.push(current);
  const paragraphs: string[] = [];
  current = "";
  for (const sentence of sentences) {
    if (current && current.length + sentence.length > targetLength) {
      paragraphs.push(current);
      current = "";
    }
    current += sentence;
  }
  if (current) paragraphs.push(current);
  return paragraphs;
}

export function dayserviceChecklistText(value: string): string {
  return readerTextParagraphs(value, 65).join("\n");
}
