'use client';

import { useState } from 'react';
import {
  emptyWorkTimePhase,
  workTimeCategories,
  workTimeSummary,
  type WorkTimePhase,
} from '../../../lib/work-time-review';

const phaseNames = ['変更前', '変更後'];

export default function WorkTimeWorksheet() {
  const [scope, setScope] = useState('');
  const [unit, setUnit] = useState('');
  const [change, setChange] = useState('');
  const [phases, setPhases] = useState<WorkTimePhase[]>([emptyWorkTimePhase(), emptyWorkTimePhase()]);
  const [comparable, setComparable] = useState(false);
  const [qualityChecked, setQualityChecked] = useState(false);
  const [safetyChecked, setSafetyChecked] = useState(false);
  const [teamLevel, setTeamLevel] = useState(false);
  const [example, setExample] = useState(false);

  const before = workTimeSummary(phases[0]);
  const after = workTimeSummary(phases[1]);
  const format = (value: number) => value.toLocaleString('ja-JP', { maximumFractionDigits: 1 });

  function updatePhase(index: number, update: Partial<WorkTimePhase>) {
    setPhases(current =>
      current.map((phase, position) => (position === index ? { ...phase, ...update } : phase)),
    );
  }

  function loadExample() {
    const hasInput =
      scope ||
      unit ||
      change ||
      comparable ||
      qualityChecked ||
      safetyChecked ||
      teamLevel ||
      phases.some(phase =>
        phase.period ||
        phase.conditions ||
        phase.quality ||
        phase.safety ||
        Object.values(phase.times).some(Boolean),
      );
    if (hasInput && !window.confirm('入力内容を架空例に置き換えますか？')) return;

    setScope('午前の共通業務（架空例）');
    setUnit('同じ曜日の午前4時間を、チーム全体で観測');
    setChange('物品の置き場所と補充担当を固定し、探索と待ちの時間がどう変わるかを見る。');
    setPhases([
      {
        period: '変更前の1日（架空）',
        times: {
          directCare: '110',
          requiredRecord: '30',
          movement: '20',
          waiting: '15',
          search: '20',
          coordination: '15',
          reentry: '5',
          meeting: '10',
          review: '5',
          otherIndirect: '10',
        },
        conditions: '同じ曜日・同じ職員数・同程度の利用状況（架空）',
        quality: '事故・記録漏れなし。未記録の品質差は評価しない（架空）',
        safety: '急変対応の余力と休憩を削減対象にしない（架空）',
      },
      {
        period: '変更後の1日（架空）',
        times: {
          directCare: '115',
          requiredRecord: '30',
          movement: '20',
          waiting: '10',
          search: '10',
          coordination: '15',
          reentry: '5',
          meeting: '10',
          review: '5',
          otherIndirect: '10',
        },
        conditions: '同じ曜日・同じ職員数・同程度の利用状況。初期整理20分は別記（架空）',
        quality: '事故・記録漏れなし。職員から大きな負担増の申告なし（架空）',
        safety: '急変対応の余力と休憩を維持（架空）',
      },
    ]);
    setComparable(false);
    setQualityChecked(false);
    setSafetyChecked(false);
    setTeamLevel(false);
    setExample(true);
  }

  function reset() {
    if (!window.confirm('入力内容を消去しますか？')) return;
    setScope('');
    setUnit('');
    setChange('');
    setPhases([emptyWorkTimePhase(), emptyWorkTimePhase()]);
    setComparable(false);
    setQualityChecked(false);
    setSafetyChecked(false);
    setTeamLevel(false);
    setExample(false);
  }

  return (
    <div className="worksheet">
      <section className="section worksheetIntro">
        <h2>個人ではなく、業務の流れを観測する</h2>
        <p>
          個人名、利用者名、介護記録本文は入力しないでください。
          この様式の入力は送信・自動保存されません。必要なら印刷、または印刷画面からPDFへ保存してください。
        </p>
        <div className="worksheetActions noPrint">
          <button type="button" onClick={loadExample}>架空例を読み込む</button>
          <button type="button" onClick={() => window.print()}>印刷・PDF保存</button>
          <button type="button" onClick={reset}>入力を消去</button>
        </div>
        {example ? (
          <p role="status" className="worksheetNotice">
            架空の記入例です。実測結果や改善効果ではありません。
          </p>
        ) : null}
        <label className="worksheetField">
          観測する業務・場面
          <input value={scope} onChange={event => setScope(event.target.value)} placeholder="例: 午前の共通業務" />
        </label>
        <label className="worksheetField">
          比較する単位
          <input value={unit} onChange={event => setUnit(event.target.value)} placeholder="例: 同じ曜日の午前4時間をチーム全体で観測" />
        </label>
        <label className="worksheetField">
          試す変更は一つ
          <textarea value={change} onChange={event => setChange(event.target.value)} rows={3} placeholder="廃止、標準化、再利用、配置・動線の変更など。AIや自動化は必要な場合だけ" />
        </label>
      </section>

      <section className="section">
        <h2>時間の性質を分けて記録する</h2>
        <p>
          各欄は観測単位全体の合計分数です。重複して計上せず、発生しなかったものは0を入力してください。
          空欄は未測定として扱います。
        </p>
        <div className="worksheetPhases">
          {phases.map((phase, index) => (
            <fieldset key={phaseNames[index]}>
              <legend>{phaseNames[index]}</legend>
              <label className="worksheetField">
                {phaseNames[index]}の観測期間
                <input value={phase.period} onChange={event => updatePhase(index, { period: event.target.value })} placeholder="例: 10月7日 午前" />
              </label>
              {workTimeCategories.map(({ key, label, help }) => (
                <label className="worksheetField" key={key}>
                  {label}（分）
                  <small>{help}</small>
                  <input
                    type="number"
                    min="0"
                    step="any"
                    inputMode="decimal"
                    value={phase.times[key]}
                    onChange={event =>
                      updatePhase(index, { times: { ...phase.times, [key]: event.target.value } })
                    }
                  />
                </label>
              ))}
              <label className="worksheetField">
                人員配置・業務量・導入負担などの条件
                <textarea value={phase.conditions} onChange={event => updatePhase(index, { conditions: event.target.value })} rows={3} placeholder="同じ職員数か、利用状況、初期設定・研修時間など" />
              </label>
              <label className="worksheetField">
                品質・職員負担の確認
                <textarea value={phase.quality} onChange={event => updatePhase(index, { quality: event.target.value })} rows={3} placeholder="記録漏れ、手戻り、職員負担など。未確認ならその旨を記入" />
              </label>
              <label className="worksheetField">
                安全・必要な余力の確認
                <textarea value={phase.safety} onChange={event => updatePhase(index, { safety: event.target.value })} rows={3} placeholder="急変対応、相談、休憩、新人支援などを削っていないか" />
              </label>
            </fieldset>
          ))}
        </div>
      </section>

      <section className="section worksheetResult" aria-live="polite">
        <h2>時間差と、品質・安全を分けて確認する</h2>
        {before && after ? (
          <>
            <dl className="worksheetTotals">
              <div><dt>変更前の観測合計</dt><dd>{format(before.total)}分</dd></div>
              <div><dt>変更後の観測合計</dt><dd>{format(after.total)}分</dd></div>
              <div><dt>変更前の直接ケア</dt><dd>{format(before.directCare)}分</dd></div>
              <div><dt>変更後の直接ケア</dt><dd>{format(after.directCare)}分</dd></div>
              <div><dt>変更前のその他の観測時間</dt><dd>{format(before.otherMeasured)}分</dd></div>
              <div><dt>変更後のその他の観測時間</dt><dd>{format(after.otherMeasured)}分</dd></div>
            </dl>
            <p>
              観測合計の差（変更後 − 変更前）：<strong>{format(after.total - before.total)}分</strong>。
              この差だけでは改善成功・生産性向上・人員削減余地を意味しません。
            </p>
          </>
        ) : (
          <p>すべての時間欄に0以上の数値を入力すると、観測時間の内訳を表示します。空欄や負数は比較しません。</p>
        )}

        <label className="worksheetCheck">
          <input type="checkbox" checked={teamLevel} onChange={event => setTeamLevel(event.target.checked)} />
          個人評価・個人ランキングではなく、チームまたは業務単位の改善として扱う
        </label>
        <label className="worksheetCheck">
          <input type="checkbox" checked={comparable} onChange={event => setComparable(event.target.checked)} />
          観測時間、業務量、人員構成など、前後を比較できる条件であることを確認した
        </label>
        <label className="worksheetCheck">
          <input type="checkbox" checked={qualityChecked} onChange={event => setQualityChecked(event.target.checked)} />
          ケア・記録・手戻り・職員負担の悪化がないか確認した
        </label>
        <label className="worksheetCheck">
          <input type="checkbox" checked={safetyChecked} onChange={event => setSafetyChecked(event.target.checked)} />
          急変対応、相談、休憩、新人支援など、必要な余力を削っていないことを確認した
        </label>

        <p className="worksheetNotice">
          {before && after && teamLevel && comparable && qualityChecked && safetyChecked
            ? '比較条件と品質・安全の確認を記録できます。ただし、一つの前後比較から因果効果、一般的な生産性向上率、適正人員を確定することはできません。'
            : '時間差だけでは改善成功と判断しません。個人評価に使わず、比較条件、品質、職員負担、安全、必要な余力を別に確認してください。'}
        </p>
        <p>
          人員配置や記録など制度上の要件は、このシートで判定せず、サービス種別に応じた一次資料を確認します。
        </p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
          介護ルールで制度・原典を確認する →
        </a>
      </section>

      <section className="printOnly">
        <h2>記入内容</h2>
        <p>{example ? '架空例 / 実測ではありません' : '利用者による記入 / 個人評価には使用しない'}</p>
        <p>対象：{scope || '未記入'} / 比較単位：{unit || '未記入'}</p>
        <p className="printText">変更：{change || '未記入'}</p>
        {phases.map((phase, index) => (
          <div key={index}>
            <h3>{phaseNames[index]}</h3>
            <p>観測期間：{phase.period || '未記入'}</p>
            <p>
              {workTimeCategories.map(({ key, label }) => `${label}: ${phase.times[key] || '未記入'}分`).join(' / ')}
            </p>
            <p className="printText">条件：{phase.conditions || '未記入'}</p>
            <p className="printText">品質・負担：{phase.quality || '未記入'}</p>
            <p className="printText">安全・余力：{phase.safety || '未記入'}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
