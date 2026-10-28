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
  equipment: ["設備の現況と使い方", "サービス区分による基準の違い"],
  operations: ["利用開始からサービス提供まで", "提供記録とサービス区分の確認"],
  remuneration: ["利用実績と算定条件", "基本報酬・加算・減算・その他の費用", "途中帰宅・利用時間短縮の日"],
  additions: ["加算要件を種類別に確認", "記録・体制・届出の突合", "早退した日の確認例"],
  deductions: ["減算の対象と適用時点", "実績の不一致を確認した場合", "欠席・変更の確認例", "定員超過と人員不足を区別"],
};

export function dayserviceRoleParagraphHeading(roleId: string, index: number): string | null {
  return roleHeadings[roleId]?.[index] ?? null;
}

export function dayserviceChapterParagraphHeading(chapterId: string, index: number): string | null {
  return chapterHeadings[chapterId]?.[index] ?? null;
}

const feeFiles = "data/fee-guidance-current-text-candidates.json、data/remuneration-current-meta.json、data/services/dayservice/unit-price-scope.json";
const ordinanceFiles = "根拠候補は収載済みの 共有の省令第37号条文データ data/ordinance37-nodes.json（通所介護のサービス対応は別途照合） と関連する原典索引である。";

/**
 * Replace only known editorial metadata; do not use broad regexes that can
 * remove a statutory condition, an exception, or an unresolved warning.
 */
export function dayserviceReadableText(chapterId: string, value: string): string {
  if (chapterId === "staffing") {
    return value.replace(
      "収載省令37号の通所介護章の人員規定とサービス別scopeを候補に、",
      "国の基準省令第37号の通所介護に関する人員規定を参照し、",
    );
  }
  if (chapterId === "equipment" || chapterId === "operations") {
    return value.replace(
      ordinanceFiles,
      "根拠となる条文と通所介護への適用関係は、国の基準省令と指定権者の条例を使って確認する必要があります。",
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
