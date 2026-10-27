"use client";

import styles from "./handbook-checklist.module.css";

type HandbookChecklistProps = {
  items: string[];
  chapterTitle: string;
  printable?: boolean;
};

/**
 * An optional, non-persistent reading aid. It never changes the legal data or
 * infers compliance from checked items. Printing is explicitly user initiated.
 */
export default function HandbookChecklist({ items, chapterTitle, printable = false }: HandbookChecklistProps) {
  return (
    <div className={styles.checklist}>
      <p className={styles.notice}>
        この確認欄は、事業所で確認する事項を整理するためのものです。
        項目ごとに該当する条件を確かめ、必要な書類・記録と原典を照合してください。
        書類の種類や確認する時点は、項目によって異なります。
      </p>
      <p className={styles.notice}>
        チェック済みでも法令への適合を証明するものではありません。
        チェック状態は保存されず、ページを再読み込みすると解除されます。
      </p>
      {items.length > 0 ? (
        <ul className={styles.items} aria-label={`${chapterTitle}の確認用チェック欄`}>
          {items.map((point, index) => (
            <li key={index} className={styles.item}>
              <label>
                <input type="checkbox" />
                <span className={styles.printMark} aria-hidden="true" />
                <span>{point}</span>
              </label>
            </li>
          ))}
        </ul>
      ) : <p>この章の確認項目は準備中です。項目がないことは、確認すべき義務がないことを意味しません。</p>}
      {printable ? (
        <div className={styles.actions}>
          <button type="button" onClick={() => window.print()}>この章のページを印刷・PDF保存</button>
          <p>印刷画面で用紙への印刷、またはPDFへの保存を選べます。関連資料の表示範囲は印刷前に確認してください。</p>
        </div>
      ) : null}
    </div>
  );
}
