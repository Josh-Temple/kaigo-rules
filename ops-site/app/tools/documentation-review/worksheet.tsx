'use client';

import { useState } from 'react';
import { emptyPhase, phaseSummary, timeCategories, type ReviewPhase } from '../../../lib/documentation-review';

const methods = ['不要な記録・重複記録の見直し', '様式の統合', '一度入力した情報の再利用', '入力場所・入力方法の変更', 'AIによる下書き'];
const phaseNames = ['変更前', '変更後'];

export default function DocumentationWorksheet() {
  const [service, setService] = useState('');
  const [task, setTask] = useState('');
  const [method, setMethod] = useState(methods[0]);
  const [change, setChange] = useState('');
  const [phases, setPhases] = useState([emptyPhase(), emptyPhase()]);
  const [comparable, setComparable] = useState(false);
  const [qualityChecked, setQualityChecked] = useState(false);
  const [example, setExample] = useState(false);
  const before = phaseSummary(phases[0]);
  const after = phaseSummary(phases[1]);
  const format = (value: number) => value.toLocaleString('ja-JP', { maximumFractionDigits: 2 });

  function updatePhase(index: number, update: Partial<ReviewPhase>) {
    setPhases(current => current.map((phase, position) => position === index ? { ...phase, ...update } : phase));
  }
  function loadExample() {
    const hasInput = service || task || change || method !== methods[0] || comparable || qualityChecked || phases.some(phase => phase.count || phase.period || phase.conditions || phase.quality || Object.values(phase.times).some(Boolean));
    if (hasInput && !window.confirm('入力内容を架空例に置き換えますか？')) return;
    setService('通所介護（架空例）');
    setTask('職員の業務報告を1件まとめる');
    setMethod(methods[2]);
    setChange('共通項目を一度入力し、別の報告様式へ再利用する。');
    setPhases([
      { period: '変更前の1週間', count: '20', times: { record: '60', copy: '40', search: '20', later: '20', review: '10' }, conditions: '同じ様式、同程度の内容、20件', quality: '記録漏れ0件、修正が必要な報告2件（架空）' },
      { period: '変更後の1週間', count: '20', times: { record: '60', copy: '10', search: '20', later: '20', review: '15' }, conditions: '同じ様式、同程度の内容、20件。設定に別途30分（架空）', quality: '記録漏れ0件、修正が必要な報告2件（架空）' },
    ]);
    setComparable(false); setQualityChecked(false); setExample(true);
  }
  function reset() {
    if (!window.confirm('入力内容を消去しますか？')) return;
    setService(''); setTask(''); setChange(''); setMethod(methods[0]); setPhases([emptyPhase(), emptyPhase()]); setComparable(false); setQualityChecked(false); setExample(false);
  }

  return <div className="worksheet">
    <section className="section worksheetIntro">
      <h2>測る対象と、変えることを決める</h2>
      <p>個人名・利用者の情報・介護記録そのものは入力しないでください。この様式の入力は送信・自動保存されません。ページを閉じる前に印刷、または印刷画面からPDFへ保存してください。</p>
      <div className="worksheetActions noPrint">
        <button type="button" onClick={loadExample}>架空例を読み込む</button>
        <button type="button" onClick={() => window.print()}>印刷・PDF保存</button>
        <button type="button" onClick={reset}>入力を消去</button>
      </div>
      {example ? <p role="status" className="worksheetNotice">架空の記入例です。実測結果や効果の実証ではありません。実測を始めるときは入力を消去してください。</p> : null}
      <label className="worksheetField">サービス種別<input value={service} onChange={event => setService(event.target.value)} placeholder="例: 通所介護" /></label>
      <label className="worksheetField">比較する業務と1件の単位<input value={task} onChange={event => setTask(event.target.value)} placeholder="例: 同じ種類の報告を1件まとめる" /></label>
      <label className="worksheetField">試す改善策<select value={method} onChange={event => setMethod(event.target.value)}>{methods.map(item => <option key={item}>{item}</option>)}</select></label>
      <label className="worksheetField">変えることは一つ<textarea value={change} onChange={event => setChange(event.target.value)} rows={3} placeholder="入力元と正本、変更する手順、対象範囲を記入" /></label>
    </section>
    <section className="section">
      <h2>時間と品質を、前後で記録する</h2>
      <p>各欄は期間全体の合計分数です。作業時間は重複して計上せず、発生しなかった作業は0を入力してください。空欄は未測定として扱います。</p>
      <p>初期設定・研修・導入費用は下の条件欄へ別に記録します。日常作業の時間差だけで費用対効果を判断しません。</p>
      <div className="worksheetPhases">{phases.map((phase, index) => <fieldset key={phaseNames[index]}>
        <legend>{phaseNames[index]}</legend>
        <label className="worksheetField">{phaseNames[index]}の計測期間<input value={phase.period} onChange={event => updatePhase(index, { period: event.target.value })} placeholder="例: 10月5日〜11日" /></label>
        <label className="worksheetField">{phaseNames[index]}の処理件数<input type="number" min="1" step="1" inputMode="numeric" value={phase.count} onChange={event => updatePhase(index, { count: event.target.value })} /></label>
        {timeCategories.map(({ key, label, help }) => <label className="worksheetField" key={key}>{phaseNames[index]}：{label}（分）<small>{help}</small><input type="number" min="0" step="any" inputMode="decimal" value={phase.times[key]} onChange={event => updatePhase(index, { times: { ...phase.times, [key]: event.target.value } })} /></label>)}
        <label className="worksheetField">{phaseNames[index]}の条件・導入負担<textarea value={phase.conditions} onChange={event => updatePhase(index, { conditions: event.target.value })} rows={3} placeholder="職種、担当人数、内容の難しさ、設定・研修時間、費用など" /></label>
        <label className="worksheetField">{phaseNames[index]}の記録漏れ・品質・修正件数<textarea value={phase.quality} onChange={event => updatePhase(index, { quality: event.target.value })} rows={3} placeholder="例: 記録漏れ0件、修正が必要な報告2件。未確認ならその旨を記入" /></label>
      </fieldset>)}</div>
    </section>
    <section className="section worksheetResult" aria-live="polite">
      <h2>確認・修正を含めた比較</h2>
      {before && after ? <>
        <dl className="worksheetTotals">
          <div><dt>変更前の合計</dt><dd>{format(before.total)}分 / {before.count}件</dd></div>
          <div><dt>変更後の合計</dt><dd>{format(after.total)}分 / {after.count}件</dd></div>
          <div><dt>変更前の1件当たり</dt><dd>{format(before.perRecord)}分</dd></div>
          <div><dt>変更後の1件当たり</dt><dd>{format(after.perRecord)}分</dd></div>
        </dl>
        <p>1件当たりの時間差（変更後 − 変更前）：<strong>{format(after.perRecord - before.perRecord)}分</strong>。負の値は短縮、正の値は増加です。</p>
      </> : <p>前後の処理件数と、すべての時間欄を入力すると合計と1件当たりの時間を表示します。空欄・負数・0件は比較しません。</p>}
      <label className="worksheetCheck"><input type="checkbox" checked={comparable} onChange={event => setComparable(event.target.checked)} />サービス・業務・1件の単位・難しさ・担当条件を比較できることを確認した</label>
      <label className="worksheetCheck"><input type="checkbox" checked={qualityChecked} onChange={event => setQualityChecked(event.target.checked)} />記録漏れや品質、職員の負担の悪化がないことを確認した</label>
      <p className="worksheetNotice">{before && after && comparable && qualityChecked ? '条件と品質を確認した記録として扱えます。ただし、一つの前後比較から改善策の因果効果や一般的な効果率は確定できません。' : '時間差だけでは改善成功と判断しません。比較条件と品質の確認が必要です。'}</p>
      <p>制度上必要な記録の要件は、Kaigo Rulesでサービス種別に合う資料を探し、適用範囲・検証状態・原典を確認してください。このシートでは制度適合を判定しません。</p>
      <a className="textLink" href="https://kaigo-rules.vercel.app/databases/search" target="_blank" rel="noreferrer">介護ルールの制度DBを検索する →</a>
    </section>
    <section className="printOnly">
      <h2>記入内容</h2>
      <p>{example ? '架空例 / 実測ではありません' : '利用者による記入 / 効果を自動判定していません'}</p>
      <p>サービス：{service || '未記入'} / 業務・単位：{task || '未記入'} / 方法：{method}</p>
      <p className="printText">変更：{change || '未記入'}</p>
      {phases.map((phase, index) => <div key={index}><h3>{phaseNames[index]}</h3><p>期間：{phase.period || '未記入'}</p><p>件数：{phase.count || '未記入'}</p><p>{timeCategories.map(({ key, label }) => `${label}: ${phase.times[key] || '未記入'}分`).join(' / ')}</p><p className="printText">条件・導入負担：{phase.conditions || '未記入'}</p><p className="printText">品質：{phase.quality || '未記入'}</p></div>)}
    </section>
  </div>;
}
