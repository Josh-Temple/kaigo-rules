'use client';

import { useState } from 'react';

type InquiryRow = {
  topic: string;
  frequency: string;
  firstContact: string;
  requiredInfo: string;
  roundTrips: string;
  channel: string;
  selfServe: string;
  template: string;
  directRoute: string;
  escalation: string;
};

const emptyInquiry = (): InquiryRow => ({
  topic: '',
  frequency: '',
  firstContact: '',
  requiredInfo: '',
  roundTrips: '',
  channel: '',
  selfServe: '未確認',
  template: '未確認',
  directRoute: '未確認',
  escalation: '',
});

const choices = ['未確認', 'できる', '一部できる', '難しい'];

export default function CommunicationWorksheet() {
  const [scope, setScope] = useState('');
  const [rows, setRows] = useState<InquiryRow[]>([emptyInquiry(), emptyInquiry(), emptyInquiry()]);
  const [trial, setTrial] = useState('');
  const [keepHumanRoute, setKeepHumanRoute] = useState(false);
  const [example, setExample] = useState(false);

  function updateRow<K extends keyof InquiryRow>(index: number, key: K, value: InquiryRow[K]) {
    setRows(current =>
      current.map((row, position) => (position === index ? { ...row, [key]: value } : row)),
    );
  }

  function loadExample() {
    const hasInput =
      scope ||
      trial ||
      keepHumanRoute ||
      rows.some(row => Object.values(row).some(value => value && value !== '未確認'));
    if (hasInput && !window.confirm('入力内容を架空例に置き換えますか？')) return;

    setScope('事業所外から届く定型的な確認（架空例）');
    setRows([
      {
        topic: '提出物の到着確認',
        frequency: '週に数回（架空）',
        firstContact: '代表窓口',
        requiredInfo: '提出日、資料の種類',
        roundTrips: '不足情報の確認で1往復することがある（架空）',
        channel: '電話・FAX',
        selfServe: '一部できる',
        template: 'できる',
        directRoute: 'できる',
        escalation: '期限超過や内容不明の場合は担当者へつなぐ',
      },
      {
        topic: '担当部署の確認',
        frequency: '週に数回（架空）',
        firstContact: '代表窓口',
        requiredInfo: '用件の種類',
        roundTrips: '担当確認のため転送が発生（架空）',
        channel: '電話',
        selfServe: 'できる',
        template: '一部できる',
        directRoute: 'できる',
        escalation: '分類できない用件は代表窓口で受ける',
      },
      emptyInquiry(),
    ]);
    setTrial('2週間だけ、提出物の確認に必要な項目と担当先を一枚にまとめ、往復回数がどう変わるかを見る。');
    setKeepHumanRoute(false);
    setExample(true);
  }

  function reset() {
    if (!window.confirm('入力内容を消去しますか？')) return;
    setScope('');
    setRows([emptyInquiry(), emptyInquiry(), emptyInquiry()]);
    setTrial('');
    setKeepHumanRoute(false);
    setExample(false);
  }

  return (
    <div className="worksheet">
      <section className="section worksheetIntro">
        <h2>問い合わせの種類だけを記録する</h2>
        <p>
          個人名、利用者名、電話番号、介護記録本文などは入力しないでください。
          この様式の入力は送信・自動保存されません。必要なら印刷、または印刷画面からPDFへ保存してください。
        </p>
        <div className="worksheetActions noPrint">
          <button type="button" onClick={loadExample}>架空例を読み込む</button>
          <button type="button" onClick={() => window.print()}>印刷・PDF保存</button>
          <button type="button" onClick={reset}>入力を消去</button>
        </div>
        {example ? (
          <p role="status" className="worksheetNotice">
            架空の記入例です。実際の問い合わせ記録や改善効果ではありません。
          </p>
        ) : null}
        <label className="worksheetField">
          棚卸しする範囲
          <input
            value={scope}
            onChange={event => setScope(event.target.value)}
            placeholder="例: 事業所外から届く定型的な確認"
          />
        </label>
      </section>

      <section className="section">
        <h2>往復が起きる箇所を3つまで見る</h2>
        <p>
          内容は個別事例ではなく「提出物の到着確認」「担当部署の確認」のような種類で記入します。
          緊急連絡や個別判断を定型化の対象へ混ぜないでください。
        </p>
        <div className="worksheetPhases">
          {rows.map((row, index) => (
            <fieldset key={index}>
              <legend>問い合わせ {index + 1}</legend>
              <label className="worksheetField">
                問い合わせの種類
                <input value={row.topic} onChange={event => updateRow(index, 'topic', event.target.value)} placeholder="例: 提出物の到着確認" />
              </label>
              <label className="worksheetField">
                発生頻度
                <input value={row.frequency} onChange={event => updateRow(index, 'frequency', event.target.value)} placeholder="例: 週に数回" />
              </label>
              <label className="worksheetField">
                最初の問い合わせ先
                <input value={row.firstContact} onChange={event => updateRow(index, 'firstContact', event.target.value)} placeholder="役割・窓口名で記入" />
              </label>
              <label className="worksheetField">
                一度で回答するために必要な情報
                <textarea value={row.requiredInfo} onChange={event => updateRow(index, 'requiredInfo', event.target.value)} rows={3} placeholder="個人情報ではなく項目名だけを記入" />
              </label>
              <label className="worksheetField">
                情報不足などで起きる往復
                <textarea value={row.roundTrips} onChange={event => updateRow(index, 'roundTrips', event.target.value)} rows={3} placeholder="例: 提出日がなく確認の電話が1回増える" />
              </label>
              <label className="worksheetField">
                現在の連絡・転記経路
                <textarea value={row.channel} onChange={event => updateRow(index, 'channel', event.target.value)} rows={3} placeholder="例: 電話→紙メモ→システム" />
              </label>
              <label className="worksheetField">
                自分で確認できる入口にできるか
                <select value={row.selfServe} onChange={event => updateRow(index, 'selfServe', event.target.value)}>
                  {choices.map(choice => <option key={choice}>{choice}</option>)}
                </select>
              </label>
              <label className="worksheetField">
                定型様式にできるか
                <select value={row.template} onChange={event => updateRow(index, 'template', event.target.value)}>
                  {choices.map(choice => <option key={choice}>{choice}</option>)}
                </select>
              </label>
              <label className="worksheetField">
                適切な担当へ直接つなげられるか
                <select value={row.directRoute} onChange={event => updateRow(index, 'directRoute', event.target.value)}>
                  {choices.map(choice => <option key={choice}>{choice}</option>)}
                </select>
              </label>
              <label className="worksheetField">
                例外時のエスカレーション
                <textarea value={row.escalation} onChange={event => updateRow(index, 'escalation', event.target.value)} rows={3} placeholder="急変・事故・判断が必要な場合の人への経路" />
              </label>
            </fieldset>
          ))}
        </div>
      </section>

      <section className="section worksheetResult" aria-live="polite">
        <h2>上位1つだけ、小さく試す</h2>
        <label className="worksheetField">
          2週間程度で試す最小変更
          <textarea
            value={trial}
            onChange={event => setTrial(event.target.value)}
            rows={4}
            placeholder="例: 必要項目と担当先を一枚にまとめ、同じ種類の問い合わせで往復回数を再確認する"
          />
        </label>
        <label className="worksheetCheck">
          <input
            type="checkbox"
            checked={keepHumanRoute}
            onChange={event => setKeepHumanRoute(event.target.checked)}
          />
          急変・事故・専門判断・制度上の判断など、すぐ人へつなぐ経路を残した
        </label>
        <p className="worksheetNotice">
          {keepHumanRoute
            ? '試行条件として、人へつなぐ経路を残したことを記録できます。問い合わせ件数が減っただけでは改善成功とは判断しません。必要な相談が止まっていないかも確認してください。'
            : '問い合わせ削減が相談抑制にならないよう、例外時・緊急時に人へつなぐ経路を先に確認してください。'}
        </p>
        <p>
          制度上の判断が必要な問い合わせは、このシートで結論を出さず、該当する一次資料を確認します。
        </p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
          介護ルールで制度・原典を確認する →
        </a>
      </section>

      <section className="printOnly">
        <h2>記入内容</h2>
        <p>{example ? '架空例 / 実測ではありません' : '利用者による記入 / 個人情報は記入しない'}</p>
        <p className="printText">棚卸し範囲：{scope || '未記入'}</p>
        {rows.map((row, index) => (
          <div key={index}>
            <h3>問い合わせ {index + 1}</h3>
            <p>種類：{row.topic || '未記入'} / 頻度：{row.frequency || '未記入'}</p>
            <p>最初の問い合わせ先：{row.firstContact || '未記入'}</p>
            <p className="printText">必要情報：{row.requiredInfo || '未記入'}</p>
            <p className="printText">往復：{row.roundTrips || '未記入'}</p>
            <p className="printText">連絡・転記経路：{row.channel || '未記入'}</p>
            <p>自分で確認：{row.selfServe} / 定型様式：{row.template} / 直接担当へ：{row.directRoute}</p>
            <p className="printText">例外時：{row.escalation || '未記入'}</p>
          </div>
        ))}
        <p className="printText">小さな試行：{trial || '未記入'}</p>
        <p>人へつなぐ経路：{keepHumanRoute ? '確認済み' : '未確認'}</p>
      </section>
    </div>
  );
}
