"use client";

export default function HandbookPrint() {
  return <div className="handbook-print-action"><button type="button" onClick={() => window.print()}>この章を印刷・PDF保存</button></div>;
}
