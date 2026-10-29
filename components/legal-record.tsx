import Link from "next/link";
import { legalDocument, legalHref, type LegalRecord } from "../lib/working-handbook";
import { safeHandbookEvidenceUrl } from "../lib/handbook/reader-content";
import { handbookReaderText } from "../lib/handbook/public-copy";

export default function LegalRecordView({ record, serviceId, expanded = false }: {
  record: LegalRecord;
  serviceId?: string;
  expanded?: boolean;
}) {
  const document = legalDocument(record.document_id);
  const references = serviceId ? record.service_references[serviceId] || [] : [];
  const bases = [...new Set(references.map(r => r.basis))];
  const paragraphReferences = [...new Set(references.filter(r => r.node_id !== record.id).map(r => r.label))];
  const officialUrl = safeHandbookEvidenceUrl(record.url) || safeHandbookEvidenceUrl(document?.url);
  return (
    <details className="handbook-source" open={expanded}>
      <summary>
        <span className="handbook-source-label">{record.label || "項目"}</span>
        <span>{record.title}</span>
      </summary>
      <div className="handbook-source-content">
        <p className="meta">{document?.title} {document?.number}</p>
        {document?.version ? <p className="meta">収載資料の版・施行日：{document.version}</p> : null}
        <p className="handbook-status">{record.state}</p>
        {bases.length ? <p className="meta">このサービスとの対応：{handbookReaderText(bases.join(" ／ "))}</p> : null}
        {paragraphReferences.length ? (
          <details><summary>登録された項・号等の参照箇所（{paragraphReferences.length}件）</summary>
            <ul className="handbook-reference-ids">{paragraphReferences.map(label => <li key={label}>{label}</li>)}</ul>
          </details>
        ) : null}
        {record.text ? <p className="handbook-original">{record.text}</p> : <p className="handbook-empty">見出しと所在を収載しています。本文は原典で確認でき、今後この欄へ追加できます。</p>}
        {record.locator ? <p className="meta">原典の掲載箇所：{handbookReaderText(record.locator)}</p> : null}
        <div className="handbook-inline-links">
          {officialUrl ? <a href={officialUrl} target="_blank" rel="noopener noreferrer">公式原典を開く ↗</a> : null}
          <Link href={legalHref({ record: record.id, service: serviceId })}>この項目へのリンク</Link>
        </div>
      </div>
    </details>
  );
}
