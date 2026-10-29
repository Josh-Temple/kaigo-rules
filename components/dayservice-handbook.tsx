import Link from "next/link";
import { handbookChapterHref, type HandbookChapter, type ServiceHandbookData } from "../lib/working-handbook";
import { dayserviceChapterGroups, dayserviceChapterIntros, dayserviceQa, dayserviceQaIndex, nationalSourceUrl, readerExcerpt, type ReaderReference, type ReaderTopic } from "../lib/handbook/dayservice-national-reader";
import { readerTextParagraphs } from "../lib/handbook/dayservice-reader-editorial";
import HandbookChecklist from "./handbook-checklist";
import HandbookPrint from "./handbook-print";

function OriginalText({ text }: { text: string }) {
  return <div className="dayservice-original">{text.split("\n").flatMap(line => readerTextParagraphs(line, 110)).map((paragraph, index) => <p key={index}>{paragraph}</p>)}</div>;
}

function OfficialLink({ url, children }: { url: string; children: React.ReactNode }) {
  const href = nationalSourceUrl(url);
  return href ? <a href={href} target="_blank" rel="noopener noreferrer">{children} ↗</a> : <span>出典リンクを確認中</span>;
}

function Excerpt({ reference, showCaution = true }: { reference: ReaderReference; showCaution?: boolean }) {
  const excerpt = readerExcerpt(reference);
  return <div className="dayservice-excerpt" data-source-id={excerpt.id}>
    <p className="dayservice-excerpt-label"><strong>{excerpt.label}</strong><span>{excerpt.locator}</span></p>
    {showCaution && excerpt.caution ? <p className="handbook-role-warning dayservice-source-caution">{excerpt.caution}</p> : null}
    {excerpt.readAcross ? <p className="dayservice-read-across">第105条による準用条文です。以下は読替え前の原文のため、「訪問介護」等の表記を含みます。<Link href="/rules/105?service=dayservice">第105条の読替えを確認</Link></p> : null}
    <blockquote><OriginalText text={excerpt.text} /></blockquote>
    <div className="dayservice-source-citation"><span>{excerpt.sourceTitle}</span>
      <ul>{excerpt.links.map(link => <li key={link.url}><OfficialLink url={link.url}>{link.label}</OfficialLink></li>)}</ul>
    </div>
  </div>;
}

function NationalQa({ id }: { id: string }) {
  const qa = dayserviceQa(id);
  return <article className="dayservice-qa" data-qa-id={id}>
    <p className="dayservice-qa-citation"><strong>問{qa.number}</strong><span>{qa.issuedLabel}</span></p>
    <div className="dayservice-qa-question"><strong>質問</strong><OriginalText text={qa.question} /></div>
    <div className="dayservice-qa-answer"><strong>回答</strong><OriginalText text={qa.answer} /></div>
    <p className="dayservice-source-citation"><OfficialLink url={qa.originalUrl}>この問の発出資料</OfficialLink><span>公式Q&A集の収載本文を表示。発出後の改正との適用関係は未確認です。</span></p>
  </article>;
}

function ReadingTopic({ topic, full, navigationId, requirementIds }: { topic: ReaderTopic; full: boolean; navigationId: string; requirementIds?: string[] }) {
  const TopicHeading = full ? "h2" : "h3";
  const BlockHeading = full ? "h3" : "h4";
  return <section id={topic.id} className={`dayservice-reading-topic${topic.id.startsWith("staffing-role-") ? " handbook-role" : ""}`}>
    {requirementIds?.map(id => <span key={id} id={`${topic.id}-requirement-${id}`} className="dayservice-legacy-anchor" />)}
    <TopicHeading>{topic.title}</TopicHeading>
    {topic.basis.length ? <section className="dayservice-source-block"><BlockHeading>基準</BlockHeading>{topic.basis.map(reference => <Excerpt key={reference.id} reference={reference} showCaution={reference.family !== "fee"} />)}</section> : null}
    {topic.interpretation?.length ? <section className="dayservice-source-block"><BlockHeading>国の解釈通知・留意事項</BlockHeading>{topic.interpretation.map((reference, index) => <Excerpt key={`${reference.id}-${reference.part || ""}`} reference={reference} showCaution={index === 0} />)}</section> : null}
    {topic.qa?.length ? <section className="dayservice-source-block" id={`${topic.id}-qa`}><BlockHeading>国Q&A</BlockHeading>{topic.qa.map(id => <NationalQa key={id} id={id} />)}</section> : null}
    {topic.id === "staffing-role-care-worker" ? <aside className="handbook-calculation-example" aria-label="介護職員の勤務時間の計算例">
      <p><strong>計算例（補足）</strong></p><p>1単位20人全員が5時間利用する場合、平均提供時間数は（20人×5時間）÷20人＝5時間。必要な勤務延時間数は｛1＋（20－15）÷5｝×5時間＝10時間です。</p>
      <p>時間数の合計に加え、提供単位ごとに介護職員を常時1人以上従事させます。他の単位との兼務は、利用者の処遇に支障がない場合の取扱いです。</p>
    </aside> : null}
    {topic.local ? <aside className="dayservice-local"><p><strong>所在地の指定権者に確認すること</strong></p><p>{topic.local}</p></aside> : null}
    {topic.note ? <p>{topic.note}</p> : null}
    <p className="handbook-role-return"><a href={`#${navigationId}`}>{topic.id.startsWith("staffing-role-") ? "職種一覧に戻る ↑" : "項目一覧に戻る ↑"}</a></p>
  </section>;
}

function QaIndex() {
  return <ul className="dayservice-qa-index">{dayserviceQaIndex().map(item => <li key={item.qa.id}>
    <Link href={`${handbookChapterHref("dayservice", item.chapterId)}#${item.topicId}-qa`}><strong>{item.topicTitle}：問{item.qa.number}</strong><span>{item.qa.question}</span></Link>
    <p className="meta">{item.qa.issuedLabel}</p>
  </li>)}</ul>;
}

function SourceGuide() {
  return <dl className="reader-source-types">
    <div><dt>基準省令</dt><dd><OfficialLink url="https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0">指定居宅サービス等の人員・設備・運営基準（第92条〜第107条）</OfficialLink><p>国の基準を掲載しています。所在地の条例・規則に独自の規定がある場合は、指定権者に確認してください。</p></dd></div>
    <div><dt>解釈通知・算定上の留意事項</dt><dd><Link href="/notices?service=dayservice">通所介護に関連する解釈通知</Link> ／ <Link href="/services/dayservice/remuneration/guidance">算定上の留意事項</Link><p>改正資料から整理した本文を含みます。各掲載箇所の資料・版と、確認が済んでいない事項を併記しています。</p></dd></div>
    <div><dt>報酬告示</dt><dd><Link href="/services/dayservice/remuneration">通所介護の報酬基準</Link><p>加算・減算は、告示だけでなく、参照先の大臣基準・留意事項・届出の条件も確認してください。</p></dd></div>
    <div><dt>国Q&A</dt><dd><OfficialLink url={dayserviceQaIndex()[0].qa.workbookUrl}>厚生労働省の介護サービス関係Q&A集</OfficialLink><p>各項目には関連する質問と回答、発出資料へのリンクを掲載しています。</p></dd></div>
  </dl>;
}

export default function DayserviceHandbookChapter({ service, chapter, full }: { service: ServiceHandbookData; chapter: HandbookChapter; full: boolean }) {
  const groups = dayserviceChapterGroups[chapter.section_id] || [];
  const isStaffing = chapter.section_id === "staffing";
  const expanded = full || isStaffing;
  const navigationId = isStaffing ? "staffing-role-navigation" : `${chapter.section_id}-topic-navigation`;
  const href = handbookChapterHref("dayservice", chapter.section_id);
  const index = service.chapters.findIndex(item => item.section_id === chapter.section_id);
  return <section className="section handbook-chapter handbook-dayservice dayservice-national-reader" id={chapter.section_id}>
    <p className="eyebrow">第{String(chapter.number).padStart(2, "0")}章</p>
    {!full ? <h2><Link href={href}>{chapter.title}</Link></h2> : null}
    <p className="dayservice-chapter-intro">{dayserviceChapterIntros[chapter.section_id]}</p>
    {full ? <p className="handbook-return-link"><Link href={`/services/dayservice#${chapter.section_id}`}>通所介護の手引に戻る</Link></p> : null}
    {isStaffing ? <div className="staffing-reading-guide"><p>国の基準、解釈通知の掲載資料、国Q&Aの順に読めます。解釈通知等には現行性を確認中の本文が含まれます。各資料の注意を併せて確認してください。</p></div> : null}
    {full && ["remuneration", "additions", "deductions"].includes(chapter.section_id) ? <p className="handbook-role-warning">掲載する報酬本文の適用版・改正附則と、参照される大臣基準・留意事項の照合は未完了です。この章だけでは算定可否を確定できません。</p> : null}
    {groups.length ? <nav className={isStaffing ? "handbook-role-navigation dayservice-topic-navigation" : "dayservice-topic-navigation"} id={navigationId} aria-label={isStaffing ? "職種・適用区分から探す" : "この章の項目"}>
      {groups.map(group => <div key={group.title}><p><strong>{group.title}</strong></p><ul>{group.topics.map(topic => <li key={topic.id}>{expanded ? <a href={`#${topic.id}`}>{topic.title}</a> : <Link href={`${href}#${topic.id}`}>{topic.title}</Link>}</li>)}</ul></div>)}
    </nav> : null}
    {expanded ? groups.flatMap(group => group.topics).map(topic => <ReadingTopic key={topic.id} topic={topic} full={full} navigationId={navigationId} requirementIds={chapter.role_sections?.find(role => topic.id === `staffing-role-${role.id}`)?.requirements.map(item => item.id)} />) : null}
    {chapter.section_id === "national_qa" ? <><QaIndex /><p><Link href="/qa?service=16">通所介護の国Q&Aを検索する →</Link></p><p><Link href="/qa">共通事項を含む国Q&A全体を検索する →</Link></p></> : null}
    {chapter.section_id === "sources_and_history" ? <SourceGuide /> : null}
    {chapter.section_id === "notifications" ? <aside className="dayservice-local"><p><strong>問い合わせ時に伝えること</strong></p><p>変更する事項、変更予定日、事業所の指定区分を伝え、変更届・体制届の要否、提出期限、必要書類を確認してください。</p><p><Link href="/handbook/dayservice/additions">加算の規定を確認する</Link> ／ <Link href="/handbook/dayservice/deductions">減算の規定を確認する</Link></p></aside> : null}
    {isStaffing ? <details className="dayservice-checks" open={full}><summary>人員基準の確認用チェック欄</summary><HandbookChecklist items={chapter.checkpoints} chapterTitle={chapter.title} /></details> : null}
    {full ? <HandbookPrint /> : null}
    <div id={`handbook-sources-${chapter.section_id}`} className="handbook-inline-links">
      {!full ? <Link href={href}>この章を詳しく読む →</Link> : <Link href="/handbook/dayservice/sources-and-history">資料の種類・出典を確認する →</Link>}
    </div>
    {full ? <nav className="handbook-chapter-sequence" aria-label="前後の章">
      {index > 0 ? <Link href={handbookChapterHref("dayservice", service.chapters[index - 1].section_id)}>前の章：{service.chapters[index - 1].title}</Link> : null}
      {index < service.chapters.length - 1 ? <Link href={handbookChapterHref("dayservice", service.chapters[index + 1].section_id)}>次の章：{service.chapters[index + 1].title}</Link> : null}
    </nav> : null}
  </section>;
}
