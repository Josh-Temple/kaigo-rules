/** Reading advice, not new staffing requirements or a finding of compliance. */
export const staffingReadingGuides: Record<string, { lead: string; checks: readonly [string, string][] }> = {
  dayservice: {
    lead: "職種を選び、必要な配置と、兼務・連携の条件を続けて確認してください。勤務時間の合計と、提供時間中の配置は別々に確認します。",
    checks: [
      ["勤務時間を確かめる", "利用者ごとの提供時間、提供単位、職種別の勤務表を用意します。平均提供時間数と勤務延時間数を混同しないよう、介護職員の説明と計算例を確認してください。"],
      ["兼務・外部連携を確かめる", "兼務する職務と時間帯、看護職員の契約先・連絡体制を確認します。条件と例外は、該当する職種の説明にあります。"],
      ["地域の基準を確かめる", "横浜市の説明は地域が明記された箇所で参照します。他の地域にそのまま当てはめず、指定権者の条例・資格の取扱いを確認してください。"],
    ],
  },
  dayrehab: {
    lead: "まず施設の種類を確かめてから、職種ごとの配置を読んでください。病院・診療所・介護老人保健施設・介護医療院では、適用する条件の確認が必要です。",
    checks: [
      ["施設の種類と指定を確かめる", "指定通知書などで施設の種類を確認し、医師の配置・みなし規定・診療所の特例をそれぞれ読みます。以下には根拠・適用条件を確認中の説明が含まれます。"],
      ["職種ごとの条件と全体の配置を確かめる", "理学療法士・作業療法士・言語聴覚士の条件と、看護職員・介護職員を含めた全体の条件を分けて確認します。単位ごとの利用者数と勤務表を用意してください。"],
      ["兼務・介護予防との一体運営を確かめる", "通常の通所リハと介護予防の指定、職務別の時間、管理者と代行者の任務を照合します。適用条件は各職種の説明と原典で確認してください。"],
    ],
  },
  homevisit: {
    lead: "管理者、サービス提供責任者、訪問介護員等を分けて確認します。「サ責」はサービス提供責任者の略称です。人数だけでなく、資格と担当する時間も確かめてください。",
    checks: [
      ["利用者数を確かめる", "月別の利用者数集計と名簿を用意し、サービス提供責任者の原則・常勤換算・特例を分けて読みます。対象となる利用者と集計期間も確認してください。"],
      ["勤務時間と資格を確かめる", "雇用契約、勤務表、出勤簿、資格証・研修修了証を照合します。常勤換算と職員の実人数は区別し、兼務する職務の時間を確認してください。"],
      ["例外と未確認の条件を確かめる", "兼務・第1号訪問事業との一体運営・旧資格の取扱いは、該当する説明の条件を確認します。資格や経験を確認できていない箇所は、不要と判断しないでください。"],
    ],
  },
};

const paragraphHeadings: Record<string, readonly string[]> = {
  "dayrehab/physician/one-or-more": ["配置人数と施設の種類"],
  "dayrehab/physician/fulltime-and-deeming": ["常勤・みなし規定の適用条件"],
  "dayrehab/rehabilitation-professionals/specialist-one-per-hundred": ["専門職と全体の配置の関係"],
  "dayrehab/rehabilitation-professionals/clinic-exception": ["診療所で確認する経験・勤務時間"],
  "dayrehab/nursing-and-care/unit-shift": ["看護職員・介護職員を含めた全体の配置"],
  "dayrehab/nursing-and-care/integrated-preventive": ["介護予防と一体運営する場合の条件"],
  "dayrehab/management/management-scope": ["管理者と代行者の役割"],
};

export function staffingParagraphHeading(service: string, role: string, requirement: string, index: number): string | null {
  return paragraphHeadings[`${service}/${role}/${requirement}`]?.[index] ?? null;
}
