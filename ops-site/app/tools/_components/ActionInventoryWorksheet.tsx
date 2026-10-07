'use client';

import { useMemo, useState } from 'react';

export type ActionField = {
  key: string;
  label: string;
  placeholder?: string;
  help?: string;
  kind?: 'text' | 'textarea' | 'select';
  options?: string[];
  wide?: boolean;
};

type Row = {
  id: number;
  values: Record<string, string>;
};

type Props = {
  itemLabel: string;
  fields: ActionField[];
  scopeLabel: string;
  scopePlaceholder: string;
  trialLabel: string;
  trialPlaceholder: string;
  noteLabel: string;
  notePlaceholder: string;
};

function blankValues(fields: ActionField[]) {
  return Object.fromEntries(fields.map((field) => [field.key, '']));
}

export default function ActionInventoryWorksheet({
  itemLabel,
  fields,
  scopeLabel,
  scopePlaceholder,
  trialLabel,
  trialPlaceholder,
  noteLabel,
  notePlaceholder,
}: Props) {
  const [scope, setScope] = useState('');
  const [trial, setTrial] = useState('');
  const [notes, setNotes] = useState('');
  const [nextId, setNextId] = useState(4);
  const [rows, setRows] = useState<Row[]>(() =>
    [1, 2, 3].map((id) => ({ id, values: blankValues(fields) })),
  );

  const enteredRows = useMemo(
    () => rows.filter((row) => Object.values(row.values).some((value) => value.trim())),
    [rows],
  );

  function updateRow(id: number, key: string, value: string) {
    setRows((current) =>
      current.map((row) =>
        row.id === id ? { ...row, values: { ...row.values, [key]: value } } : row,
      ),
    );
  }

  function addRow() {
    setRows((current) => [...current, { id: nextId, values: blankValues(fields) }]);
    setNextId((current) => current + 1);
  }

  function removeRow(id: number) {
    setRows((current) => {
      if (current.length === 1) return current;
      return current.filter((row) => row.id !== id);
    });
  }

  function reset() {
    if (!window.confirm('入力内容を消去しますか？')) return;
    setScope('');
    setTrial('');
    setNotes('');
    setRows([1, 2, 3].map((id) => ({ id, values: blankValues(fields) })));
    setNextId(4);
  }

  return (
    <div className="actionWorksheet">
      <section className="section actionToolForm">
        <h2>棚卸しの範囲を決める</h2>
        <p>
          個人名、利用者名、介護記録の本文などの個人情報は入力しないでください。
          入力内容は送信・自動保存されません。必要な場合は印刷、または印刷画面からPDFへ保存してください。
        </p>
        <div className="worksheetActions noPrint">
          <button type="button" onClick={addRow}>行を追加</button>
          <button type="button" onClick={() => window.print()}>印刷・PDF保存</button>
          <button type="button" onClick={reset}>入力を消去</button>
        </div>
        <div className="actionFields">
          <label className="worksheetField">
            {scopeLabel}
            <input value={scope} onChange={(event) => setScope(event.target.value)} placeholder={scopePlaceholder} />
          </label>
          <label className="worksheetField">
            {trialLabel}
            <input value={trial} onChange={(event) => setTrial(event.target.value)} placeholder={trialPlaceholder} />
          </label>
        </div>
      </section>

      <section className="section actionToolForm">
        <h2>{itemLabel}を記入する</h2>
        <p>
          空欄は未確認のまま残します。このシートは正本や改善策を自動判定せず、現状を整理するために使います。
        </p>
        <div className="actionRows">
          {rows.map((row, index) => (
            <fieldset className="actionRow" key={row.id}>
              <legend>{itemLabel} {index + 1}</legend>
              <div className="actionRowHead noPrint">
                <span>分かる範囲だけ記入</span>
                {rows.length > 1 ? (
                  <button type="button" onClick={() => removeRow(row.id)}>この行を削除</button>
                ) : null}
              </div>
              <div className="actionFields">
                {fields.map((field) => (
                  <label className={`worksheetField${field.wide ? ' actionFieldWide' : ''}`} key={field.key}>
                    {field.label}
                    {field.help ? <small>{field.help}</small> : null}
                    {field.kind === 'textarea' ? (
                      <textarea
                        rows={3}
                        value={row.values[field.key]}
                        onChange={(event) => updateRow(row.id, field.key, event.target.value)}
                        placeholder={field.placeholder}
                      />
                    ) : field.kind === 'select' ? (
                      <select
                        value={row.values[field.key]}
                        onChange={(event) => updateRow(row.id, field.key, event.target.value)}
                      >
                        <option value="">未確認</option>
                        {(field.options ?? []).map((option) => <option key={option}>{option}</option>)}
                      </select>
                    ) : (
                      <input
                        value={row.values[field.key]}
                        onChange={(event) => updateRow(row.id, field.key, event.target.value)}
                        placeholder={field.placeholder}
                      />
                    )}
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
        </div>
      </section>

      <section className="section actionToolForm">
        <h2>次に試すことを一つだけ決める</h2>
        <label className="worksheetField">
          {noteLabel}
          <textarea value={notes} onChange={(event) => setNotes(event.target.value)} rows={4} placeholder={notePlaceholder} />
        </label>
        <p className="worksheetNotice">
          このシートへの記入だけで改善効果や制度適合を確認したことにはなりません。
          実行後は、必要な根拠・品質・安全・現場負担を別に確認してください。
        </p>
      </section>

      <section className="actionToolPrint">
        <h2>記入内容</h2>
        <p>棚卸し範囲：{scope || '未記入'}</p>
        <p>試行範囲・期間：{trial || '未記入'}</p>
        {(enteredRows.length ? enteredRows : rows.slice(0, 1)).map((row, index) => (
          <div className="actionPrintRow" key={row.id}>
            <h3>{itemLabel} {index + 1}</h3>
            {fields.map((field) => (
              <p className="printText" key={field.key}>
                <strong>{field.label}：</strong>{row.values[field.key] || '未記入'}
              </p>
            ))}
          </div>
        ))}
        <p className="printText"><strong>{noteLabel}：</strong>{notes || '未記入'}</p>
        <p>個人情報は記入しない前提の様式です。改善効果・制度適合は自動判定していません。</p>
      </section>
    </div>
  );
}
