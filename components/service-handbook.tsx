import Link from "next/link";
import { chapterRecords, handbookChapterHref, legalHref, type HandbookChapter, type HandbookEvidence, type HandbookRoleSection, type ServiceHandbookData } from "../lib/working-handbook";
import LegalRecordView from "./legal-record";
import HandbookChecklist from "./handbook-checklist";
import HandbookNavigation from "./handbook-navigation";
import StaffingReadingGuide from "./staffing-reading-guide";
import HandbookProse from "./handbook-prose";
import { handbookReaderText } from "../lib/handbook/public-copy";
import { staffingParagraphHeading } from "../lib/handbook/staffing-reading-guide";
import qaMeta from "../data/qa-corpus-meta.json";
import { isStaffingScopeOrException, readerEvidenceTitle, readerEvidenceLocator, safeHandbookEvidenceUrl, readerLabel, readerRequirementTitle, requirementCopy, separateHandbookParagraphs, splitDayserviceRegionalText, type HandbookAuthoritySegment } from "../lib/handbook/reader-content";
import { dayserviceChapterParagraphHeading, dayserviceChecklistText, dayserviceReadableText, dayserviceRoleParagraphHeading } from "../lib/handbook/dayservice-reader-editorial";

const evidenceNames: Record<HandbookEvidence["kind"], string> = {
  national_standard: "国の基準省令",
  national_interpretation: "国の基準解釈通知",
  national_qa: "国Q&A",
  national_law: "国の法律",
  national_form: "国の様式",
  national_fee_notice: "国の介護報酬告示",
  yokohama_ordinance: "横浜市条例",
  yokohama_regulation: "横浜市規則",
  yokohama_handbook: "参考資料：横浜市の運営の手引き",
};

const authorityDisplayLabels: Record<HandbookAuthoritySegment["authority"], string> = {
  national_law: "国の法律", national_standard: "国の基準省令",
  national_interpretation: "国の解釈通知（省令とは法的性格が異なります）",
  national_qa: "国のQ&A（省令とは法的性格が異なります）",
  national_fee_notice: "国の介護報酬告示（人員基準と算定要件は区別）",
  municipal_ordinance: "地域の条例（適用地域に法的効力がある場合があります）",
  municipal_regulation: "地域の規則（適用地域の規定を確認）",
  municipal_handbook: "自治体の運営手引（参考資料）",
};

/** Preserve original anchor targets while placing staff roles before scope and exception items. */
function RoleNavigation({ roles, staffing, anchor, detailHref, full, headingTag = "h4" }: {
  roles: HandbookRoleSection[]; staffing: boolean; anchor: string; detailHref: string; full: boolean; headingTag?: "h3" | "h4";
}) {
  const NavHeading = headingTag;
  const categories = staffing ? [
    { title: "職種・役割から探す", items: roles.filter(role => !isStaffingScopeOrException(role.title)) },
    { title: "人数の算定・適用区分・特例", items: roles.filter(role => isStaffingScopeOrException(role.title)) },
  ] : [{ title: "項目から探す", items: roles }];
  return <nav id={`${anchor}-navigation`} className="handbook-role-navigation" aria-label={staffing ? "職種・適用区分から探す" : "要件の項目に移動"}>
    {categories.filter(category => category.items.length > 0).map(category => <div key={category.title} className="handbook-role-nav-group">
      <NavHeading>{category.title}</NavHeading>
      <ul>{category.items.map(role => <li key={role.id}>{full
        ? <a href={`#${anchor}-${role.id}`}>{readerLabel(role.title)}</a>
        : <Link href={`${detailHref}#${anchor}-${role.id}`}>{readerLabel(role.title)}の要件を見る</Link>
      }</li>)}</ul>
    </div>)}
  </nav>;
}

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
  const chapterPage = full && service.service_id === "dayservice";
  const GroupHeading = chapterPage ? "h2" : "h3";
  const RoleHeading = chapterPage ? "h3" : "h4";
  const RequirementHeading = chapterPage ? "h4" : "h5";
  const DetailHeading = chapterPage ? "h5" : "h6";
  // The three pilot services show actual role requirements in their service guide.
  // Other services retain a direct link to the full staffing chapter.
  const inlineStaffing = staffing && !full && ["dayservice", "dayrehab", "homevisit"].includes(service.service_id);
  if (!full && !inlineStaffing) return <section className="handbook-role-preview" aria-label={groupHeading}>
    <GroupHeading>{groupHeading}</GroupHeading>
    <p className="handbook-primary-action"><Link href={detailHref}>職種別の配置・勤務・資格を確認する</Link></p>
    <RoleNavigation roles={roles} staffing={staffing} anchor={anchor} detailHref={detailHref} full={false} />
  </section>;
  return <section className="handbook-roles" aria-label={groupHeading}>
    <GroupHeading>{groupHeading}</GroupHeading>
    <p className="meta">未確認の内容を含みます。適用前に最新の原典と指定権者の基準を確認してください。{service.service_id === "dayservice" ? "出典本文の一部を確認した資料でも、要件全体の施行版・適用条件の確認が完了したことを意味しません。" : null}</p>
    <RoleNavigation roles={roles} staffing={staffing} anchor={anchor} detailHref={detailHref} full={true} headingTag={chapterPage ? "h3" : "h4"} />
    {roles.map(role => <section key={role.id} id={`${anchor}-${role.id}`} className="handbook-role">
      <RoleHeading>{readerLabel(role.title)}</RoleHeading>
      {service.service_id === "dayservice" && staffing && role.title.includes("看護職員") ? <>
        <p><Link href="/questions/nurse-staffing">看護職員の配置と連携について実務Q&Aを読む</Link></p>
        <p className="meta">このQ&Aは手引の補足です。連携・兼務の適用条件は、国の解釈通知・Q&Aの現行内容を別途確認してください。</p>
      </> : null}
      {role.requirements.map(requirement => {
        const copy = requirementCopy(requirement.description);
        const parts = service.service_id === "dayservice" && staffing
          ? splitDayserviceRegionalText(copy, requirement.authority_segments, requirement.evidence) : null;
        return <section key={requirement.id} className="handbook-role-requirement" id={`${anchor}-${role.id}-requirement-${requirement.id}`}>
        <RequirementHeading>{readerRequirementTitle(
          requirement.title, requirement.aspect,
          role.requirements.slice(0, role.requirements.indexOf(requirement)).filter(item => item.aspect === requirement.aspect && /^(確認事項|要件|確認すること)$/u.test(readerLabel(item.title))).length,
          role.requirements.filter(item => item.aspect === requirement.aspect && /^(確認事項|要件|確認すること)$/u.test(readerLabel(item.title))).length,
        )}</RequirementHeading>
        {requirement.verification_state === "EVIDENCE_GAP" ? <p className="handbook-role-warning">{parts?.classified === false
          ? "未確認：原典との照合が必要です。国・自治体の根拠区分も確認中のため、全国共通の基準として扱わないでください。"
          : "未確認：この要件の根拠と適用条件は、原典との照合が必要です。"}</p> : null}
        {parts ? parts.segments.map((segment, index) => <section key={index} className={segment.authority === "unclassified" ? "handbook-unclassified-content" : segment.authority.startsWith("municipal_") ? "handbook-regional-note" : "handbook-authority-note"}>
          {segment.authority === "unclassified" && requirement.verification_state === "EVIDENCE_GAP" ? null : <DetailHeading>{segment.authority === "unclassified"
            ? "国・自治体の根拠区分を確認中（全国共通の基準として扱わないでください）"
            : `${segment.authority.startsWith("municipal_") ? `${segment.jurisdiction}：` : ""}${authorityDisplayLabels[segment.authority]}`}</DetailHeading>}
          {segment.text.split("\n").filter(Boolean).map((paragraph, paragraphIndex) => <div key={paragraphIndex} className="handbook-reader-paragraph">
            {service.service_id === "dayservice" && staffing && segment.authority === "unclassified" && parts.segments.length === 1 && dayserviceRoleParagraphHeading(role.id, paragraphIndex)
              ? <DetailHeading>{dayserviceRoleParagraphHeading(role.id, paragraphIndex)}</DetailHeading> : null}
            <HandbookProse text={handbookReaderText(paragraph)} readable={service.service_id === "dayservice"} />
          </div>)}
        </section>) : copy.split("\n").filter(Boolean).map((paragraph, index) => <div key={index} className="handbook-reader-paragraph">
          {staffingParagraphHeading(service.service_id, role.id, requirement.id, index)
            ? <DetailHeading>{staffingParagraphHeading(service.service_id, role.id, requirement.id, index)}</DetailHeading> : null}
          <HandbookProse text={handbookReaderText(paragraph)} readable={service.service_id === "dayservice"} />
        </div>)}
        {service.service_id === "dayservice" ? <div className="handbook-applicability"><DetailHeading>適用範囲と注意点</DetailHeading><HandbookProse text={handbookReaderText(requirement.applicability)} readable /></div>
          : <p><strong>適用範囲：</strong>{handbookReaderText(requirement.applicability)}</p>}
        {requirement.description.startsWith("【Research Mesh隔離候補・法令適合未審査】") && requirement.verification_state !== "EVIDENCE_GAP" ? <p className="handbook-role-warning">この要件の法令適合性は未審査です。</p> : null}
        {requirement.practical_checks.length ? <>
          <DetailHeading>実務上の確認ポイント（法令上の義務とは別）</DetailHeading>
          <ul className="handbook-checkpoints">{requirement.practical_checks.map((point, index) => <li key={index}>{handbookReaderText(point)}</li>)}</ul>
        </> : null}
        <DetailHeading>関連する原典と適用上の注意</DetailHeading>
        {requirement.evidence.length ? <ul className="handbook-role-evidence">{requirement.evidence.map((evidence, index) => <li key={index}>
          <strong>{evidenceNames[evidence.kind]}</strong>
          <span className="handbook-role-evidence-state">{evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" ? "原文確認済み（限定範囲）" : "出典候補・原文未照合"}</span>
          <div>{handbookReaderText(readerEvidenceTitle(evidence.title).label)}（{evidence.issuer}）</div>
          <details className="handbook-evidence-details"><summary>条文・適用版の情報</summary>
            <p>該当箇所：{handbookReaderText(readerEvidenceLocator(evidence.locator))}</p>
            <p>版：{handbookReaderText(evidence.version)}</p>
          </details>
          <div>対象：{handbookReaderText(evidence.scope)}{evidence.effective_date ? ` ／ 適用日：${evidence.effective_date}` : ""}</div>
          {evidence.note ? <p>{handbookReaderText(evidence.note)}</p> : null}
          {evidence.verification_state === "PRIMARY_TEXT_CHECKED_SCOPED" && safeHandbookEvidenceUrl(evidence.url) ? <div><a href={safeHandbookEvidenceUrl(evidence.url)!} target="_blank" rel="noopener noreferrer">{evidence.kind === "yokohama_handbook" ? "横浜市の手引を開く ↗" : "公式資料を開く ↗"}</a></div> : null}
        </li>)}</ul> : <p className="handbook-role-warning">個別の出典候補はまだ登録されていません。原典の特定・照合が必要です。</p>}
        {requirement.evidence.some(e => e.kind === "national_qa" && e.verification_state !== "PRIMARY_TEXT_CHECKED_SCOPED") ? <p className="meta">関連する国Q&Aは候補の段階です。原問との照合が必要です。</p> : null}
      </section>})}
      <p className="handbook-role-return"><a href={`#${anchor}-navigation`}>職種一覧に戻る ↑</a></p>
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
  const hasReadAcross = records.some(record => record.service_references[service.service_id]?.some(reference => reference.basis.includes("準用")));
  const shown = full ? records : records.slice(0, 3);
  const detailHref = handbookChapterHref(service.service_id, chapter.section_id);
  const chapterIndex = service.chapters.findIndex(item => item.section_id === chapter.section_id);
  const precedingChapter = chapterIndex > 0 ? service.chapters[chapterIndex - 1] : null;
  const followingChapter = chapterIndex >= 0 ? service.chapters[chapterIndex + 1] : null;
  const dayservice = service.service_id === "dayservice";
  const TopicHeading = full && dayservice ? "h2" : "h3";
  const staffingSupplement = dayservice && chapter.section_id === "staffing"
    && ["life-counselor", "nurse", "care-worker", "functional-training", "manager"].every(id => chapter.role_sections?.some(role => role.id === id));
  const paragraphContent = paragraphs.reader.map((paragraph, index) => <div key={index} className="handbook-reader-paragraph">
    {service.service_id === "dayservice" && dayserviceChapterParagraphHeading(chapter.section_id, index)
      ? <TopicHeading>{dayserviceChapterParagraphHeading(chapter.section_id, index)}</TopicHeading> : null}
    <HandbookProse text={handbookReaderText(service.service_id === "dayservice" ? dayserviceReadableText(chapter.section_id, paragraph) : paragraph)} readable={dayservice} />
  </div>);
  const sourceItems = shown.length ? shown.map(record => <LegalRecordView key={record.id} record={record} serviceId={service.service_id} />)
    : <p className="handbook-empty">この章への個別資料の対応付けは確認中です。関連する資料全体からも探せます。</p>;
  return (
    <section className={`section handbook-chapter${dayservice ? " handbook-dayservice" : ""}`} id={chapter.section_id}>
      <p className="eyebrow">第{String(chapter.number).padStart(2, "0")}章</p>
      {full && dayservice ? null : <h2>{full ? `${chapter.title}の確認ポイント` : <Link href={detailHref}>{chapter.title}</Link>}</h2>}
      <p>{handbookReaderText(dayservice ? dayserviceReadableText(chapter.section_id, chapter.summary) : chapter.summary)}</p>
      {service.service_id === "homevisit" && chapter.section_id === "staffing" ? <p className="meta">「サ責」は「サービス提供責任者」の略称です。資格や配置の条件は、以下の職種別の説明と原典で確認してください。</p> : null}
      {full ? <p className="handbook-return-link"><Link href={`/services/${service.service_id}#${chapter.section_id}`}>{service.label}の手引に戻る</Link></p> : null}
      {!full && chapter.section_id === "staffing" && !["dayservice", "dayrehab", "homevisit"].includes(service.service_id)
        ? <p className="handbook-primary-action"><Link href={detailHref}>人員基準を確認する（配置・資格・勤務の条件）</Link></p> : null}
      {chapter.section_id !== "national_qa" && records.length > 0
        ? <p className="handbook-quick-link"><a href={`#handbook-sources-${chapter.section_id}`}>この章の関連資料へ移動 ↓</a></p>
        : null}
      {chapter.section_id === "staffing" && ["homevisit", "dayrehab", "dayservice"].includes(service.service_id)
        ? <><StaffingReadingGuide serviceId={service.service_id} /><StaffingRoles service={service} chapter={chapter} full={full} /></> : null}
      {dayservice && chapter.section_id === "staffing" ? <p className="meta">国の基準と地域の条例・規則は別の根拠です。自治体の運営手引は参考資料です。適用地域の規定、原典の施行版、未確認の条件を別途確認してください。</p> : null}
      {staffingSupplement ? <details className="handbook-supplement">
        <summary>人員基準の全体像・条文に沿った補足を読む</summary>
        {paragraphContent}
      </details> : <>
        {chapter.section_id === "staffing" && ["homevisit", "dayrehab"].includes(service.service_id) ? <h3>人員基準の全体像</h3> : null}
        {paragraphContent}
      </>}
      <TopicHeading>確認すること</TopicHeading>
      <HandbookChecklist items={chapter.checkpoints.map(item => {
        const text = handbookReaderText(service.service_id === "dayservice" ? dayserviceReadableText(chapter.section_id, item) : item);
        return dayservice ? dayserviceChecklistText(text) : text;
      })} chapterTitle={chapter.title} printable={full} showInstructions={!dayservice || full} />
      {chapter.section_id !== "staffing" || !["homevisit", "dayrehab", "dayservice"].includes(service.service_id)
        ? <StaffingRoles service={service} chapter={chapter} full={full} /> : null}
      {chapter.section_id === "national_qa" ? <>
        <TopicHeading>関連する国Q&A</TopicHeading>
        <p>{dayservice ? "通所介護の質問と、サービス共通の質問を探せます。各問の対象サービス・適用条件・発出日を確認してください。" : `サービス個別・共通分類の候補を合わせて${service.qa_count.toLocaleString("ja-JP")}件収載しています。共通分類は各問の条件を確認してください。`}</p>
        <div className="handbook-inline-links">
          {service.qa_codes.map(code => <Link key={code} href={`/qa?service=${code}`}>{(qaMeta.scope_by_code as Record<string, string>)[code] || "関連する国Q&A"} →</Link>)}
          <Link href="/qa">国Q&A全体を見る →</Link>
        </div>
      </> : <>
        <TopicHeading id={`handbook-sources-${chapter.section_id}`}>{dayservice ? "根拠を確認する" : <>関連する条文・資料 <small>（{records.length}件）</small></>}</TopicHeading>
        {dayservice ? <p className="meta">この章に関連する資料の候補です。適用関係は原典で確認してください。{hasReadAcross ? "準用する条文は読替え前の原文を表示します。準用元が訪問介護などの場合は、そのサービス名のまま表示されます。" : null}</p>
          : full ? <p className="meta">この章に関連する資料の候補です。適用関係は原典で確認してください。準用する条文は、読替え前の原文を表示します。</p> : null}
        {dayservice && shown.length ? <details className="handbook-source-list">
          <summary>{full ? `関連資料${records.length}件を開く` : `関連資料の見出しを開く（${shown.length}件）`}</summary>
          {sourceItems}
        </details> : sourceItems}
      </>}
      {full ? <nav className="handbook-chapter-sequence" aria-label="前後の章">
        {precedingChapter ? <Link href={handbookChapterHref(service.service_id, precedingChapter.section_id)}>前の章：{precedingChapter.title}</Link> : null}
        {followingChapter ? <Link href={handbookChapterHref(service.service_id, followingChapter.section_id)}>次の章：{followingChapter.title}</Link> : null}
      </nav> : null}
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
      <p className="handbook-primary-action handbook-staffing-entry"><a href="#staffing">人員基準を確認する（職種別の配置・資格・勤務時間）</a></p>
      <p className="handbook-working-note">確認中の説明を含む手引です。適用条件や未確認の注意を読み、判断前に最新の国の原典と指定権者の基準を確認してください。</p>
      <HandbookNavigation service={service} inline />
      {service.service_id === "dayservice" ? <details className="handbook-collection-details">
        <summary>掲載資料の件数を確認する</summary>
        <p>全15章。条文・資料は{service.source_record_count.toLocaleString("ja-JP")}件、関連Q&A候補は{service.qa_count.toLocaleString("ja-JP")}件です。件数は適用の確認済み件数を示すものではありません。</p>
      </details> : <div className="handbook-summary" aria-label="収載状況">
        <span><strong>15</strong>章</span>
        <span><strong>{service.source_record_count.toLocaleString("ja-JP")}</strong>条文・資料</span>
        <span><strong>{service.qa_count.toLocaleString("ja-JP")}</strong>関連Q&A候補</span>
      </div>}
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
      <h2 id="handbook-toc">全15章の目次</h2>
      <nav className="handbook-toc" aria-label="手引の目次">
        {service.chapters.map(chapter => <a key={chapter.section_id} href={`#${chapter.section_id}`}>
          <span>{String(chapter.number).padStart(2, "0")}</span>{chapter.title}
        </a>)}
      </nav>
      {service.service_id === "dayservice" ? <p className="handbook-checklist-instructions">各章の確認欄は、条件・書類・記録と原典を照らし合わせるための点検用です。書類の種類と確認時点は項目ごとに異なります。チェック済みでも法令への適合を証明するものではありません。チェック状態は保存されず、再読み込みすると解除されます。</p> : null}
      {service.chapters.map(chapter => <HandbookChapterContent key={chapter.section_id} service={service} chapter={chapter} />)}
      <p><Link href="/services">サービス一覧へ戻る →</Link></p>
    </article>
  );
}
