import Link from "next/link";
import LegalRecordView from "../../components/legal-record";
import { filterLegalRecords, legalDocuments, legalHref, LEGAL_CATEGORIES, serviceHandbooks, type LegalFilters } from "../../lib/working-handbook";
import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("法令等を条文順で読む", "介護保険法・9種類の基準省令・通知・報酬基準を、条文・原典の掲載順で閲覧し、39サービス別に絞り込めます。", "/legislation");
const PAGE_SIZE = 30;
type Params = LegalFilters & { page?: string };

export default async function LegislationPage({ searchParams }: { searchParams: Promise<Params> }) {
  const raw = await searchParams;
  const input = Object.fromEntries(Object.entries(raw).filter(([, value]) => typeof value === "string")) as Params;
  const service = serviceHandbooks.find(s => s.service_id === input.service);
  const category = LEGAL_CATEGORIES.find(c => c.id === input.category);
  const document = legalDocuments.find(d => d.id === input.document && (!category || d.category === category.id));
  const filters: LegalFilters = { service: input.service || "", category: category?.id || "", document: document?.id || "", q: input.q || "", record: input.record || "" };
  const records = filterLegalRecords(filters);
  const pageCount = Math.max(1, Math.ceil(records.length / PAGE_SIZE));
  const requested = Number.parseInt(input.page || "1", 10);
  const page = Math.min(pageCount, Math.max(1, Number.isFinite(requested) ? requested : 1));
  const shown = records.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const documents = legalDocuments.filter(d => !category || d.category === category.id);
  return (
    <article className="answer-page wide-page handbook-page">
      <p className="eyebrow">法令・通知・報酬基準</p>
      <h1>法令等を条文順で読む</h1>
      <p className="lead">収載済みの介護保険法・各サービスの基準省令を条文順で、通知・報酬を原典の掲載順で表示します。サービスを選ぶと、登録された関連箇所に絞り込めます。</p>
      <form className="legal-browser-filters" action="/legislation" method="get">
        <label><span>サービス</span><select name="service" defaultValue={input.service || ""}>
          <option value="">すべてのサービス</option>
          {serviceHandbooks.map(s => <option key={s.service_id} value={s.service_id}>{s.label}</option>)}
        </select></label>
        <label><span>資料の種類</span><select name="category" defaultValue={category?.id || ""}>
          <option value="">すべての種類</option>
          {LEGAL_CATEGORIES.map(c => <option key={c.id} value={c.id}>{c.label}</option>)}
        </select></label>
        <label className="legal-document-select"><span>法令・通知</span><select name="document" defaultValue={document?.id || ""}>
          <option value="">すべての法令・通知</option>
          {documents.map(d => <option key={d.id} value={d.id}>{d.title}</option>)}
        </select></label>
        <label className="legal-keyword"><span>キーワード・条文番号</span><input type="search" name="q" defaultValue={input.q || ""} placeholder="例：人員、業務継続、第一条" /></label>
        <button type="submit">絞り込む</button>
        <Link href="/legislation">解除</Link>
      </form>
      <p className="handbook-working-note">確認前の資料対応も表示します。サービスの絞り込みは登録された関連箇所を示します。準用・読替え・例外や適用条件は原典で確認してください。新旧対照表・旧版資料は、それぞれの版を保って表示しています。</p>
      <div className="legal-results-header">
        <p><strong>{records.length.toLocaleString("ja-JP")}件</strong> {service ? `／ ${service.label}` : "／ 全サービス"} <span className="meta">条文・原典掲載順</span></p>
        {service ? <Link href={`/services/${service.service_id}`}>このサービスの手引へ →</Link> : null}
      </div>
      {input.record ? <p><Link href={legalHref({ ...filters, record: "" })}>項目指定を解除して一覧へ →</Link></p> : null}
      {shown.length ? <div>
        {shown.map((record, index) => {
          const previousDoc = index ? shown[index - 1].document_id : "";
          const doc = legalDocuments.find(d => d.id === record.document_id);
          return <div key={record.id}>
            {previousDoc !== record.document_id ? <div className="legal-document-heading"><h2>{doc?.title}</h2><p className="meta">{doc?.number} {doc?.version ? `／ ${doc.version}` : ""}</p></div> : null}
            <LegalRecordView record={record} serviceId={service?.service_id} expanded={Boolean(input.record)} />
          </div>;
        })}
      </div> : <div className="handbook-empty"><p>この条件に対応する収載資料はありません。条件を減らすか、サービスの手引から原典を確認してください。</p><Link href={legalHref({ service: service?.service_id })}>このサービスの資料をすべて表示する →</Link></div>}
      {pageCount > 1 ? <nav className="legal-pagination" aria-label="条文一覧のページ送り">
        {page > 1 ? <Link href={legalHref({ ...filters, page: page - 1 })}>← 前の{PAGE_SIZE}件</Link> : <span />}
        <span>{page} / {pageCount}ページ</span>
        {page < pageCount ? <Link href={legalHref({ ...filters, page: page + 1 })}>次の{PAGE_SIZE}件 →</Link> : <span />}
      </nav> : null}
      <p><Link href="/services">サービス別の手引から読む →</Link></p>
    </article>
  );
}
