export const workTimeCategories = [
  { key: 'directCare', label: '直接ケア', help: '利用者への直接的なケア・看護・リハ等。単純な削減対象として扱いません。' },
  { key: 'requiredRecord', label: '必要な記録', help: '制度・運用上必要な記録や報告に使った時間。' },
  { key: 'movement', label: '移動', help: '事業所内外の移動に使った時間。' },
  { key: 'waiting', label: '待ち', help: '人・設備・承認・連絡などを待った時間。' },
  { key: 'search', label: '探索', help: '資料・情報・物品・担当者を探した時間。' },
  { key: 'coordination', label: '調整', help: '予定・役割・関係者との調整に使った時間。' },
  { key: 'reentry', label: '転記', help: '同じ情報を別の紙・システム・様式へ入れ直した時間。' },
  { key: 'meeting', label: '会議', help: '会議・打ち合わせに使った時間。必要な相談を一律に削減対象にしません。' },
  { key: 'review', label: '確認・修正', help: '確認、修正、手戻りに使った時間。' },
  { key: 'otherIndirect', label: 'その他間接業務', help: '上記に入らない間接業務。内容は条件欄へ補足します。' },
] as const;

export type WorkTimeKey = typeof workTimeCategories[number]['key'];

export type WorkTimePhase = {
  period: string;
  times: Record<WorkTimeKey, string>;
  conditions: string;
  quality: string;
  safety: string;
};

export function emptyWorkTimePhase(): WorkTimePhase {
  return {
    period: '',
    times: {
      directCare: '',
      requiredRecord: '',
      movement: '',
      waiting: '',
      search: '',
      coordination: '',
      reentry: '',
      meeting: '',
      review: '',
      otherIndirect: '',
    },
    conditions: '',
    quality: '',
    safety: '',
  };
}

export function workTimeSummary(phase: WorkTimePhase) {
  const raw = workTimeCategories.map(({ key }) => phase.times[key]);
  if (raw.some(value => !value.trim() || !Number.isFinite(Number(value)) || Number(value) < 0)) {
    return null;
  }
  const values = Object.fromEntries(
    workTimeCategories.map(({ key }) => [key, Number(phase.times[key])]),
  ) as Record<WorkTimeKey, number>;
  const total = workTimeCategories.reduce((sum, { key }) => sum + values[key], 0);
  if (!Number.isFinite(total)) return null;
  return {
    total,
    directCare: values.directCare,
    otherMeasured: total - values.directCare,
  };
}
