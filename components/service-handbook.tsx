import Link from "next/link";
import { chapterRecords, handbookChapterHref, legalHref, type HandbookChapter, type ServiceHandbookData } from "../lib/working-handbook";
import LegalRecordView from "./legal-record";
import { readerLabel, requirementCopy, separateHandbookParagraphs } from "../lib/handbook/reader-content";

const evidenceNames = {
  national_standard: "国の基準省令",
  national_interpretation: "国の基準解釈通知",
  national_qa: "国Q&A",
  yokohama_ordinance: "横浜市条例",
  yokohama_handbook: "横浜市の運営の手引き",
} as const;

function StaffingRoles({ service, chapter, full }: {
  service: ServiceHandbookData; chapter: HandbookChapter; full: boolean;
}) {
  const staffing = chapter.section_id === "staffing";
  const roles = staffing ? chapter.role_sections : chapter.rule_sections;
  const groupHeading = staffing ? "職種ごとの人員基準" : "項目ごとの要件と条件";
  const anchor = staffing ? "staffing-role" : `chapter-${chapter.section_id}-rule`;
  const staffingServices = ["homevisit", "dayrehab", "dayservice", "small-scale-multifunctional", "specific-welfare-equipment-sale", "welfare-equipment-rental", "preventive-welfare-equipment-rental", "preventive-support", "homerehab", "preventive-homerehab", "preventive-dayrehab", "preventive-homenursing", "homebath", "homenursing", "regular-round", "shortstay-life", "shortstay-medical", "preventive-homebath", "preventive-shortstay-life", "preventive-shortstay-medical", "specific-facility", "preventive-specific-facility", "community-specific-facility", "community-elderly-facility", "specific-preventive-welfare-equipment-sale"];
  const ruleChapters = ["equipment", "operations", "records", "safeguarding", "incident_and_infection", "business_continuity", "notifications"];
  const allowed = staffing ? staffingServices.includes(service.service_id)
    : service.service_id === "community-elderly-facility" && ruleChapters.includes(chapter.section_id);
  if (!allowed || !roles?.length) return null;
  const detailHref = handbookChapterHref(service.service_id, chapter.section_id);
  if (!full) return <nav className="handbook-role-navigation" aria-label={groupHeading}>
    <h3>{groupHeading}</h3>
    <ul>{roles.map(role => <li key={role.id}><Link href={`${detailHref}#${anchor}-${role.id}`}>{readerLabel(role.title)}の要件を見る →</Link></li>)}</ul>
  </nav>;
  return <section className="handbook-roles" aria-label={groupHeading}>
    <h3>{groupHeading}</h3>
    <p className="meta">次の解説は、記載された対象範囲と出典確認状況に限ります。原典の現行性・人手受入は別途確認してください。</p>
    <nav className="handbook-role-navigation" aria-label={staffing ? "職種・役割に移動" : "要件の項目に移動"}>
      <ul>{roles.map(role => <li key={role.id}><a href={`#${anchor}-${role.id}`}>{readerLabel(role.title)}</a></li>)}</ul>
    </nav>
    {roles.map(role => <section key={role.id} id={`${anchor}-${role.id}`} className="handbook-role">
      <h4>{readerLabel(role.title)}</h4>
      {role.requirements.map(requirement => <section key={requirement.id} className="handbook-role-requirement" id={`${anchor}-${role.id}-requirement-${requirement.id}`}>
        <h5>{requirement.title}</h5>
        {requirement.verification_state === "EVIDENCE_GAP" ? <p className="handbook-role-warning">根拠未確認：要件の適用条件と原典の照合が必要です。</p> : null}
        {requirementCopy(requirement.description).split("\n").map((paragraph, index) => <p key={index}>{paragraph}</p>)}
        <p><strong>適用範囲：</strong>{requirement.applicability}</p>
        {requirement.description.startsWith("【Research Mesh隔離候補・法令適合未審査】") && requirement.verification_state !== "EVIDENCE_GAP" ? <p className="handbook-role-warning">この要件の法令適合性は未審査です。</p> : null}
        {requirement.practical_checks.length ? <>
          <h6>実務上の確認ポイント（法令上の義務とは別）</h6>
          <ul className="handbook-checkpoints">{requirement.practical_checks.map((point, index) => <li key={index}>{point}</li>)}</ul>
        </> : null}
        <h6>関連する原典と適用上の注意</h6>
        {requirement.evidence.length ? <ul className="handbook-role-evidence">{requirement.evidence.map((evidence, index) => <li key={index}>
          <strong>{evidenceNames[evidence.kind]}</strong>
          <span className="handbook-role-evidence-state">{evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" ? "原文確認済み（限定範囲）" : "未確認・根拠候補"}</span>
          <div>{evidence.title}（{evidence.issuer}）</div>
          <div>該当箇所：{evidence.locator} ／ 版：{evidence.version}</div>
          <div>対象：{evidence.scope}{evidence.effective_date ? ` ／ 適用日：${evidence.effective_date}` : ""}</div>
          {evidence.note ? <p>{evidence.note}</p> : null}
          {evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" && evidence.url ? <div><a href={evidence.url} target="_blank" rel="noopener noreferrer">公式原典を開く ↗</a></div> : null}
          {evidence.checked_at_jst ? <details className="handbook-editorial-details"><summary>原文の確認記録</summary><p>{evidence.checked_at_jst}</p></details> : null}
        </li>)}</ul> : <p className="handbook-role-warning">この要件の個別原典は未特定です。</p>}
        {!requirement.evidence.some(e => e.kind === "national_qa" && e.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED") ? <p className="handbook-role-warning">関連する確認済み国Q&Aは未特定です。</p> : null}
      </section>)}
    </section>)}
  </section>;
}

export function HandbookChapterContent({ service, chapter, full = false }: {
  service: ServiceHandbookData;
  chapter: HandbookChapter;
  full?: boolean;
}) {
  const paragraphs = chapter.section_id === "staffing" && ["homevisit", "dayrehab", "dayservice"].includes(service.service_id)
    ? separateHandbookParagraphs(chapter.paragraphs) : { reader: chapter.paragraphs, editorial: [] };
  const records = chapterRecords(chapter);
  const shown = full ? records : records.slice(0, 3);
  const detailHref = handbookChapterHref(service.service_id, chapter.section_id);
  return (
    <section className="section handbook-chapter" id={chapter.section_id}>
      <p className="eyebrow">第{String(chapter.number).padStart(2, "0")}章</p>
      <h2>{full ? chapter.title : <Link href={detailHref}>{chapter.title}</Link>}</h2>
      <p>{chapter.summary}</p>
      {chapter.section_id !== "national_qa" && records.length > 0
        ? <p className="handbook-quick-link"><a href={`#handbook-sources-${chapter.section_id}`}>この章の関連資料へ移動 ↓</a></p>
        : null}
      {chapter.section_id === "staffing" && ["homevisit", "dayrehab", "dayservice"].includes(service.service_id)
        ? <StaffingRoles service={service} chapter={chapter} full={full} /> : null}
      {chapter.section_id === "staffing" && ["homevisit", "dayrehab", "dayservice"].includes(service.service_id) ? <h3>章の原稿と補足</h3> : null}
      {paragraphs.reader.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      {paragraphs.editorial.length ? <details className="handbook-editorial-details"><summary>資料の作成時の補足</summary>{paragraphs.editorial.map((paragraph, index) => <p key={index}>{paragraph}</p>)}</details> : null}
      <h3>確認すること</h3>
      <ul className="handbook-checkpoints">{chapter.checkpoints.map((point, index) => <li key={index}>{point}</li>)}</ul>
      {chapter.section_id !== "staffing" || !["homevisit", "dayrehab", "dayservice"].includes(service.service_id)
        ? <StaffingRoles service={service} chapter={chapter} full={full} /> : null}
      {chapter.section_id === "national_qa" ? <>
        <h3>関連する国Q&A</h3>
        <p>サービス個別・共通分類の候補を合わせて{service.qa_count.toLocaleString("ja-JP")}件収載しています。共通分類は各問の条件を確認してください。</p>
        <div className="handbook-inline-links">
          {service.qa_codes.map(code => <Link key={code} href={`/qa?service=${code}`}>{service.qa_direct_codes.includes(code) ? "サービス個別" : "共通分類"}（{code}）→</Link>)}
          <Link href="/qa">国Q&A全体を見る →</Link>
        </div>
      </> : <>
        <h3 id={`handbook-sources-${chapter.section_id}`}>関連する条文・資料 <small>（{records.length}件）</small></h3>
        {full ? <p className="meta">登録済みのサービス対応と見出しを使って配置した確認候補です。準用先の本文は、読替え前の原文を表示します。</p> : null}
        {shown.length ? shown.map(record => <LegalRecordView key={record.id} record={record} serviceId={service.service_id} />)
          : <p className="handbook-empty">この章への個別資料の対応付けは追記できます。収載済みの資料全体からも探せます。</p>}
      </>}
      <div className="handbook-inline-links">
        {!full ? <Link href={detailHref}>この章を詳しく読む{records.length > shown.length ? `（関連資料${records.length}件）` : ""} →</Link> : null}
        {full ? <Link href={`/services/${service.service_id}#${chapter.section_id}`}>手引のこの章へ戻る ↑</Link> : null}
        <Link href={legalHref({ service: service.service_id })}>{records.length ? "このサービスの法令等を見る →" : "個別資料が未登録のため、法令等の全候補から探す →"}</Link>
      </div>
    </section>
  );
}

export default function ServiceHandbook({ service }: { service: ServiceHandbookData }) {
  return (
    <article className="answer-page wide-page handbook-page">
      <p className="eyebrow"><Link href="/services">サービス別手引</Link> ／ 全15章</p>
      <h1>{service.label}の手引</h1>
      <p className="lead">開設、人員・設備、日常運営、報酬までを章ごとにまとめています。概要と確認項目から、関連する条文・通知・Q&Aへ進めます。</p>
      <p className="handbook-working-note">作成中の手引です。確認前の解説・条文対応も掲載し、内容を随時追加・調整しています。資料ごとの版と確認状況は、本文を開くと確認できます。</p>
      <div className="handbook-summary" aria-label="収載状況">
        <span><strong>15</strong>章</span>
        <span><strong>{service.source_record_count.toLocaleString("ja-JP")}</strong>条文・資料</span>
        <span><strong>{service.qa_count.toLocaleString("ja-JP")}</strong>関連Q&A候補</span>
      </div>
      <div className="handbook-inline-links handbook-top-links">
        <Link href={legalHref({ service: service.service_id })}>法令等を条文順で読む →</Link>
        <Link href="/services">別のサービスを選ぶ →</Link>
      </div>
      {service.service_id === "dayrehab" ? <section className="handbook-working-note" aria-label="通所リハビリテーションの報酬関連資料">
        <p>報酬関連資料は現行性確認中です。現行統合本文とは区別してご確認ください。</p>
        <div className="handbook-inline-links">
          <Link href="/databases/search?service=dayrehab">このサービスのデータベースを検索 →</Link>
          <Link href="/rules?service=dayrehab">このサービスの基準省令を確認 →</Link>
          <Link href="/notices?service=dayrehab">このサービスの解釈通知を確認 →</Link>
          <Link href="/services/dayrehab/remuneration">報酬基準を見る →</Link>
          <Link href="/services/dayrehab/remuneration/guidance">算定上の留意事項を見る →</Link>
        </div>
      </section> : null}
      <nav className="handbook-toc" aria-label="手引の目次">
        {service.chapters.map(chapter => <a key={chapter.section_id} href={`#${chapter.section_id}`}>
          <span>{String(chapter.number).padStart(2, "0")}</span>{chapter.title}
        </a>)}
      </nav>
      {service.chapters.map(chapter => <HandbookChapterContent key={chapter.section_id} service={service} chapter={chapter} />)}
      <p><Link href="/services">サービス一覧へ戻る →</Link></p>
    </article>
  );
}
