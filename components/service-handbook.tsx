import Link from "next/link";
import { chapterRecords, handbookChapterHref, legalHref, type HandbookChapter, type ServiceHandbookData } from "../lib/working-handbook";
import LegalRecordView from "./legal-record";
import { DAY_SERVICE_STAFFING, DAY_SERVICE_STAFFING_SHARED, separateHandbookParagraphs } from "../lib/handbook/reader-content";

const evidenceNames = {
  national_standard: "国の基準省令",
  national_interpretation: "国の基準解釈通知",
  national_qa: "国Q&A",
  yokohama_ordinance: "横浜市条例",
  yokohama_handbook: "横浜市の運営の手引き",
} as const;

function readerLabel(value: string) {
  return value.replace(/（Research Mesh未審査）/gu, "").trim();
}

function requirementCopy(value: string) {
  return value.replace(/^【Research Mesh隔離候補・法令適合未審査】/u, "");
}

function DayserviceStaffingReader({ full, detailHref }: { full: boolean; detailHref: string }) {
  return <section className="handbook-reader-staffing" aria-label="通所介護の職種別人員基準">
    <h3>職種ごとの人員基準</h3>
    <p className="handbook-reader-notice">事業所の形態や自治体の定めによって条件が異なる場合があります。適用する基準は原文と指定権者の案内で確認してください。</p>
    <nav className="handbook-reader-index" aria-label="人員基準の職種から探す">
      {DAY_SERVICE_STAFFING.map(role => full
        ? <a key={role.id} href={"#dayservice-staffing-" + role.id}>{role.heading}</a>
        : <Link key={role.id} href={detailHref + "#dayservice-staffing-" + role.id}>{role.heading}</Link>)}
    </nav>
    {full ? <>
      {DAY_SERVICE_STAFFING.map(role => <section className="handbook-reader-profession" key={role.id} id={"dayservice-staffing-" + role.id}>
        <h4>{role.heading}</h4>
        {role.points.map((text, index) => <p key={index}>{text}</p>)}
        <p className="handbook-reader-reference">根拠の手掛かり：{role.reference}</p>
      </section>)}
      <section className="handbook-reader-shared" aria-label="職種に共通する人員の取扱い">
        <h4>共通する配置・兼務のルール</h4>
        {DAY_SERVICE_STAFFING_SHARED.map(rule => <div key={rule.heading}>
          <h5>{rule.heading}</h5>
          <p>{rule.text}</p>
          <p className="handbook-reader-reference">根拠の手掛かり：{rule.reference}</p>
        </div>)}
      </section>
    </> : <>
      <div className="handbook-reader-brief">
        {DAY_SERVICE_STAFFING.map(role => <div key={role.id}>
          <strong>{role.heading}</strong><span>{role.brief}</span>
        </div>)}
      </div>
      <p className="handbook-reader-detail-link"><Link href={detailHref}>職種別の基準と条件を詳しく読む →</Link></p>
    </>}
  </section>;
}

function StaffingRoles({ service, chapter, full }: {
  service: ServiceHandbookData; chapter: HandbookChapter; full: boolean;
}) {
  const roles = chapter.role_sections;
  if (chapter.section_id !== "staffing" || !["homevisit", "small-scale-multifunctional", "specific-welfare-equipment-sale", "welfare-equipment-rental", "preventive-welfare-equipment-rental", "preventive-support", "homerehab", "preventive-homerehab", "preventive-dayrehab", "preventive-homenursing"].includes(service.service_id) || !roles?.length) return null;
  const detailHref = handbookChapterHref(service.service_id, "staffing");
  if (!full) return <nav className="handbook-role-navigation" aria-label="職種・役割ごとの基準">
    <h3>職種・役割ごとの基準</h3>
    <ul>{roles.map(role => <li key={role.id}><Link href={detailHref + "#staffing-role-" + role.id}>{readerLabel(role.title)} →</Link></li>)}</ul>
  </nav>;
  return <section className="handbook-roles" aria-label="職種・役割ごとの基準">
    <h3>職種・役割ごとの基準</h3>
    <p className="handbook-reader-notice">確認中の要件を含みます。事業所の形態、兼務条件、適用する条例などは原典と照合してください。</p>
    <nav className="handbook-role-navigation" aria-label="職種・役割に移動">
      <ul>{roles.map(role => <li key={role.id}><a href={"#staffing-role-" + role.id}>{readerLabel(role.title)}</a></li>)}</ul>
    </nav>
    {roles.map(role => <section key={role.id} id={"staffing-role-" + role.id} className="handbook-role">
      <h4>{readerLabel(role.title)}</h4>
      {role.requirements.map(requirement => <section key={requirement.id} className="handbook-role-requirement" id={"staffing-role-" + role.id + "-requirement-" + requirement.id}>
        <h5>{requirement.title}</h5>
        <p>{requirementCopy(requirement.description)}</p>
        {requirement.applicability && !requirement.applicability.includes("国基準の現行版、指定権者条例") ? <p className="handbook-role-applicability"><strong>対象・条件：</strong>{requirement.applicability}</p> : null}
        {requirement.practical_checks.length ? <div className="handbook-reader-checks">
          <h6>確認すること</h6>
          <ul>{requirement.practical_checks.map((point, index) => <li key={index}>{point}</li>)}</ul>
        </div> : null}
        <details className="handbook-editorial-details">
          <summary>根拠条文と確認状況</summary>
          {requirement.verification_state === "EVIDENCE_GAP" ? <p>この要件は原文・適用条件を確認中です。</p> : null}
          <p>対象範囲の原稿メモ：{requirement.applicability}</p>
          {requirement.evidence.length ? <ul className="handbook-role-evidence">{requirement.evidence.map((evidence, index) => <li key={index}>
            <strong>{evidenceNames[evidence.kind]}</strong>
            <span className="handbook-role-evidence-state">{evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" ? "原文の限定範囲を確認" : "原文・適用条件は確認中"}</span>
            <div>{evidence.title}{evidence.locator ? " ／ " + evidence.locator : ""}</div>
            <div>資料の版・範囲：{evidence.version} ／ {evidence.scope}</div>
            {evidence.note ? <p>{evidence.note}</p> : null}
            {evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" && evidence.url ? <a href={evidence.url} target="_blank" rel="noopener noreferrer">公式原典を開く ↗</a> : null}
          </li>)}</ul> : <p>個別の根拠資料は確認中です。</p>}
        </details>
      </section>)}
    </section>)}
  </section>;
}

export function HandbookChapterContent({ service, chapter, full = false }: {
  service: ServiceHandbookData;
  chapter: HandbookChapter;
  full?: boolean;
}) {
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
      {service.service_id === "dayservice" && chapter.section_id === "staffing" ? <>
        <DayserviceStaffingReader full={full} detailHref={detailHref} />
        {full ? <details className="handbook-editorial-details">
          <summary>基準省令に近い原稿の全文を確認する</summary>
          {chapter.paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
        </details> : null}
      </> : <>
        {separateHandbookParagraphs(chapter.paragraphs).reader.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
        {full && separateHandbookParagraphs(chapter.paragraphs).editorial.length > 0 ? <details className="handbook-editorial-details">
          <summary>資料の出典・作成時の補足を確認する</summary>
          {separateHandbookParagraphs(chapter.paragraphs).editorial.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
        </details> : null}
      </>}
      <h3>確認すること</h3>
      <ul className="handbook-checkpoints">{chapter.checkpoints.map((point, index) => <li key={index}>{point}</li>)}</ul>
      <StaffingRoles service={service} chapter={chapter} full={full} />
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
