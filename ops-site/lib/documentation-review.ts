export const timeCategories = [
  { key: 'record', label: '必要な記録', help: '最初の入力・文書作成に使った時間。' },
  { key: 'copy', label: '転記・再入力', help: '同じ内容を紙・別システム・報告へ入れ直した時間。' },
  { key: 'search', label: '探す・確認する', help: '資料・過去記録・入力方法を探して確認した時間。' },
  { key: 'later', label: '後追い記録', help: '後から思い出してまとめ直した時間。' },
  { key: 'review', label: '確認・修正', help: '完成した記録やAIの下書きを点検・修正した時間。他の欄と重複させない。' },
] as const;
export type TimeKey = typeof timeCategories[number]['key'];
export type ReviewPhase = { period: string; count: string; times: Record<TimeKey, string>; conditions: string; quality: string };
export function emptyPhase(): ReviewPhase {
  return { period: '', count: '', times: { record: '', copy: '', search: '', later: '', review: '' }, conditions: '', quality: '' };
}
export function phaseSummary(phase: ReviewPhase) {
  const count = Number(phase.count);
  if (!phase.count.trim() || !Number.isInteger(count) || count <= 0) return null;
  const values = timeCategories.map(({ key }) => phase.times[key]);
  if (values.some(value => !value.trim() || !Number.isFinite(Number(value)) || Number(value) < 0)) return null;
  const total = values.reduce((sum, value) => sum + Number(value), 0);
  if (!Number.isFinite(total)) return null;
  return { count, total, perRecord: total / count };
}
