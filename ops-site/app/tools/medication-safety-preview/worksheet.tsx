"use client";

import { useMemo, useState } from "react";
import {
  CHECK_FIELDS,
  CHECK_STATES,
  PROCESS_STAGES,
  WORKFLOW_BOUNDARY,
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
          これは事故が起きていない平時の業務点検を補助する未検証の試作です。
          事故や服薬上の疑義が現にある場合は使わず、本人の安全確保、正式手順、
          管理者・関係医療職への連絡、必要な緊急対応を優先してください。
          各サービスで実際に存在する工程と職種権限は責任者・関係職種が確認します。
          薬剤・処方・利用者情報・事故の詳細を入力する欄や、選択回答を送信・自動保存する機能はありません。
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
          これらの選択肢は厚生労働省が認定した点検基準ではなく、この試作独自の設計案です。
          「取扱いを把握している」は未検証の自己申告であり、安全確認ではありません。
          「自分の担当範囲では扱わない」も、責任者・関係職種による確認前の申告です。
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
        <p>点検工程：{stageLabel}（工程と担当権限は未検証）</p>
        {review.lines.length ? (
          <ul>
            {review.lines.map(line => <li key={line}>{line}</li>)}
          </ul>
        ) : null}
        <p className="medicationBoundary">{review.note}</p>
        <p className="medicationBoundary">{WORKFLOW_BOUNDARY}</p>
        <p>
          変更情報の受領・共有は連携経路を整理するための項目です。
          処方指示の正しさ・真正性や、指示変更の有効性を判定しません。
        </p>
        <p>
          実際の事故や服薬上の疑義がある場合、この結果で次の服薬・医療対応・報告要否を判断しないでください。
          本人の安全確保、正式な事故対応手順、管理者・関係する医療専門職への連絡を優先してください。
          業務手順の変更は責任者・関係専門職と検討し、本人の意思・尊厳、職員の業務負担、
          法令・自治体の現行手続も別途確認してください。
        </p>
      </section>
      <section className="medicationPrint printOnly" aria-label="印刷用の点検概要">
        <h2>服薬業務の安全点検シート（未公開の試作・匿名）</h2>
        <p>平時の業務点検に限ります。事故・服薬上の疑義が現にある場合は使用しないでください。</p>
        <p>選択肢は独自の設計案で、自己申告・未検証です。工程・担当権限も未確定です。</p>
        <p>点検工程：{stageLabel}（工程と担当権限は未検証）</p>
        {CHECK_FIELDS.map(field => (
          <p key={field.key}>{field.label}：{statusLabel(answers.checks[field.key])}</p>
        ))}
        <h3>確認・相談する事項</h3>
        <ul>{review.lines.map(line => <li key={line}>{line}</li>)}</ul>
        <p>{review.note}</p>
        <p>{WORKFLOW_BOUNDARY}</p>
        <p>この書式は未検証の試作です。事故防止、安全性、制度適合、実施権限、医療上の判断を保証しません。</p>
        <p>事故・疑義時には本人の安全確保、事業所の正式手順、管理者・関係医療職への連絡、必要な緊急対応、適用される法令・自治体の手続を優先してください。個別の再投与・事故報告要否は判定しません。</p>
        <p>本人の意思・尊厳を尊重してください。服薬拒否への医学的な対応や指示変更の正しさ・有効性を、この書式では判断しません。</p>
        <p>利用者情報・薬剤情報・事故の詳細を記録する欄は設けていません。</p>
      </section>
    </div>
  );
}
