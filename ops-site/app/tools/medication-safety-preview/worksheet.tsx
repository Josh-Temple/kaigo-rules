"use client";

import { useMemo, useState } from "react";
import {
  CHECK_FIELDS,
  CHECK_STATES,
  PROCESS_STAGES,
  deriveReview,
  emptyReview,
  fictionalReview,
  type CheckKey,
  type CheckState,
  type ProcessStage,
} from "../../../lib/medication-safety-review";

export default function MedicationSafetyWorksheet() {
  const [answers, setAnswers] = useState(emptyReview);
  const [demo, setDemo] = useState(false);
  const review = useMemo(() => deriveReview(answers), [answers]);
  const stageLabel = PROCESS_STAGES.find(stage => stage.value === answers.stage)?.label ?? "未確認";
  const statusLabel = (value: string) => CHECK_STATES.find(choice => choice.value === value)?.label ?? "未確認";

  function setCheck(key: CheckKey, value: CheckState) {
    setDemo(false);
    setAnswers(current => ({ ...current, checks: { ...current.checks, [key]: value } }));
  }

  function setStage(stage: ProcessStage) {
    setDemo(false);
    setAnswers(current => ({ ...current, stage }));
  }

  function loadDemo() {
    if (JSON.stringify(answers) !== JSON.stringify(emptyReview()) &&
        !window.confirm("現在の選択を架空例に置き換えますか？")) return;
    setAnswers(fictionalReview());
    setDemo(true);
  }

  function reset() {
    if (!window.confirm("選択内容を消去しますか？")) return;
    setAnswers(emptyReview());
    setDemo(false);
  }

  return (
    <div className="medicationWorksheet">
      <section className="section">
        <h2>1. 業務工程を選ぶ</h2>
        <p>
          個人情報や薬剤・処方内容は入力できません。選択結果はこの画面内だけで扱い、
          自動保存・サーバー送信はしません。印刷はボタン操作時のみ行います。
        </p>
        <label className="medicationField">
          <span>点検する工程</span>
          <select value={answers.stage} onChange={event => setStage(event.target.value as ProcessStage)}>
            {PROCESS_STAGES.map(stage => (
              <option value={stage.value} key={stage.value}>{stage.label}</option>
            ))}
          </select>
        </label>
        <div className="medicationActions noPrint">
          <button type="button" onClick={loadDemo}>架空例を読み込む</button>
          <button type="button" onClick={() => window.print()}>画面を印刷</button>
          <button type="button" onClick={reset}>選択内容を消去</button>
        </div>
        {demo ? <p className="worksheetNotice" role="status">架空の業務例を表示しています。実際の事故や改善効果を示すものではありません。</p> : null}
      </section>
      <section className="section">
        <h2>2. 現場の手順と連携を点検する</h2>
        <p>
          「確認できる」は自己申告であり、手順が正しいことや事故を防げることを意味しません。
          「対象外」を選んだ場合も、その判断は責任者と確認が必要です。
        </p>
        <div className="medicationQuestions">
          {CHECK_FIELDS.map((field, index) => (
            <label className="medicationQuestion" key={field.key}>
              <span><strong>{index + 1}. {field.label}</strong></span>
              <select
                value={answers.checks[field.key]}
                onChange={event => setCheck(field.key, event.target.value as CheckState)}
              >
                {CHECK_STATES.map(choice => (
                  <option key={choice.value} value={choice.value}>{choice.label}</option>
                ))}
              </select>
            </label>
          ))}
        </div>
      </section>
      <section className="section medicationResult" aria-live="polite">
        <h2>3. 確認・相談する事項</h2>
        <p>点検工程：{stageLabel}</p>
        {review.lines.length ? (
          <ul>
            {review.lines.map(line => <li key={line}>{line}</li>)}
          </ul>
        ) : null}
        <p className="medicationBoundary">{review.note}</p>
        <p>
          業務手順の変更は、責任者と関係する専門職の確認を経て検討してください。
          本人の意思、自立支援、職員の業務負担、正式な事故対応・報告手順も別途考慮が必要です。
        </p>
      </section>
      <section className="medicationPrint printOnly" aria-label="印刷用の点検概要">
        <h2>服薬業務の安全点検シート（試作・匿名）</h2>
        <p>点検工程：{stageLabel}</p>
        {CHECK_FIELDS.map(field => (
          <p key={field.key}>{field.label}：{statusLabel(answers.checks[field.key])}</p>
        ))}
        <h3>確認・相談する事項</h3>
        <ul>{review.lines.map(line => <li key={line}>{line}</li>)}</ul>
        <p>{review.note}</p>
        <p>この書式は未検証の試作です。事故防止や安全性、制度適合、医療上の判断を保証しません。</p>
        <p>利用者情報・薬剤情報・事故の詳細を記録する欄は設けていません。</p>
      </section>
    </div>
  );
}
