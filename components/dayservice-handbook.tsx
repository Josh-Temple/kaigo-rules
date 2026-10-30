import Link from "next/link";
import { handbookChapterHref, type HandbookChapter, type ServiceHandbookData } from "../lib/working-handbook";
import { dayserviceChapterGroups, dayserviceChapterIntros, dayserviceQa, dayserviceQaIndex, nationalSourceUrl, readerExcerpt, type ReaderReference, type ReaderTopic } from "../lib/handbook/dayservice-national-reader";
import { sourceTextParagraphs } from "../lib/handbook/dayservice-reader-editorial";
import { basicFeeTable, dayserviceAppliedText, type FeeTableRow } from "../lib/handbook/dayservice-source-layout";
import HandbookChecklist from "./handbook-checklist";
import HandbookPrint from "./handbook-print";

function OriginalText({ text }: { text: string }) {
  return <div className="dayservice-original">{sourceTextParagraphs(text).map((paragraph, index) => paragraph.trim() ? <p key={index} className={/^[\s]*[・※①-⑳一二三四五六七八九十イロハニホヘトア-オ（(]/u.test(paragraph) ? "dayservice-source-item" : undefined}>{paragraph}</p> : null)}</div>;
}

function FeeTable({ title, rows }: { title: string; rows: FeeTableRow[] }) {
  return <><p className="dayservice-table-help">表は横にスクロールできます。</p>
    <div className="dayservice-table-scroll" role="region" aria-label={`${title}の単位数表`} tabIndex={0}>
      <table className="dayservice-fee-table"><caption><span>{title}（単位）</span></caption>
        <thead><tr><th scope="col">所要時間</th>{[1, 2, 3, 4, 5].map(care => <th scope="col" key={care}>要介護{care}</th>)}</tr></thead>
        <tbody>{rows.map(row => <tr key={row.duration}><th scope="row">{row.duration}</th>{row.units.map((unit, index) => <td key={index}>{unit}</td>)}</tr>)}</tbody>
      </table>
    </div></>;
}

function LifeCounselorExample() {
  return <aside className="handbook-calculation-example" aria-label="生活相談員の勤務時間の計算例">
    <p><strong>通知の計算例：午前・午後の2単位</strong></p>
    <figure className="dayservice-staffing-example">
      <figcaption>事業所のサービス提供時間</figcaption>
      <div className="dayservice-service-timeline" role="img" aria-label="午前の単位は9時から12時の3時間。12時から13時はサービス提供なし。午後の単位は13時から18時の5時間。">
        <span className="dayservice-service-period" aria-hidden="true">9〜12時<strong>3時間</strong></span>
        <span className="dayservice-service-gap" aria-hidden="true" />
        <span className="dayservice-service-period" aria-hidden="true">13〜18時<strong>5時間</strong></span>
      </div>
      <p className="dayservice-example-note">12時〜13時はサービス提供なし。計算から除きます。</p>
    </figure>
    <dl className="dayservice-example-result">
      <div><dt>事業所の提供時間数</dt><dd>3時間＋5時間＝<strong>8時間</strong></dd></div>
      <div><dt>必要な生活相談員の勤務延時間数</dt><dd><strong>合計8時間</strong></dd></div>
    </dl>
    <div className="dayservice-example-contrast">
      <p><strong>比較例：勤務時間数が不足する場合</strong></p>
      <figure className="dayservice-staffing-example">
        <figcaption>生活相談員の勤務帯と不足する時間帯（例）</figcaption>
        <div className="dayservice-counselor-comparison" role="img" aria-label="生活相談員Aは9時から12時の3時間、12時から13時はサービス提供なし。生活相談員Bは13時から17時の4時間。17時から18時は生活相談員の勤務がなく、合計1時間不足する例。">
          <span>9〜12時<strong>A：3時間</strong></span><span>12〜13時<strong>休止</strong></span>
          <span>13〜17時<strong>B：4時間</strong></span><span className="dayservice-missing-hour">17〜18時<strong>不足</strong></span>
        </div>
      </figure>
      <p>上記と同じ提供時間（9〜12時・13〜18時）で、生活相談員Aが9〜12時の3時間、Bが13〜17時の4時間だけ勤務した場合：</p>
      <p><strong>3時間＋4時間＝7時間</strong>。必要な8時間に1時間足りません。</p>
      <p className="dayservice-example-note">これは勤務延時間数だけの比較です。資格・専従、勤務の実態など、他の条件も別に確認してください。</p>
    </div>
    <p className="dayservice-example-note">掲載する解釈通知の例を図示しています。<a href="#staffing-role-life-counselor-interpretation">本文・確認上の注意を読む</a></p>
  </aside>;
}

function CareWorkerExample() {
  return <aside className="handbook-calculation-example" aria-label="介護職員の勤務時間の計算例">
    <p><strong>計算例（補足）：1単位・20人全員が5時間利用</strong></p>
    <p>平均提供時間数：（20人×5時間）÷20人＝5時間</p>
    <p>必要な勤務延時間数：｛1＋（20－15）÷5｝×5時間＝10時間</p>
    <figure className="dayservice-staffing-example"><figcaption>9時から14時まで提供する場合の配置例</figcaption>
      <table><thead><tr><th scope="col">職員</th><th scope="col">勤務時間帯</th><th scope="col">時間数</th></tr></thead>
        <tbody>{["介護職員A", "介護職員B"].map(name => <tr key={name}><th scope="row">{name}</th><td><span className="dayservice-time-bar">9時〜14時</span></td><td>5時間</td></tr>)}</tbody>
        <tfoot><tr><th scope="row" colSpan={2}>勤務延時間数の合計</th><td>10時間</td></tr></tfoot>
      </table>
    </figure>
    <p>時間数の合計に加え、提供単位ごとに介護職員を常時1人以上従事させます。他の単位との兼務は、利用者の処遇に支障がない場合の取扱いです。</p>
  </aside>;
}

function TrainingOverlapExample() {
  return <figure className="dayservice-timing-example">
    <figcaption>問57の時間帯例：2人の専従機能訓練指導員が重なる時間</figcaption>
    <div className="dayservice-time-example-scroll" role="region" tabIndex={0} aria-label="個別機能訓練加算の時間帯比較表">
      <table><thead><tr><th scope="col">時間</th><th scope="col">9〜10時</th><th scope="col">10〜12時</th><th scope="col">12〜13時</th></tr></thead>
      <tbody>
        <tr><th scope="row">指導員A</th><td>配置</td><td>配置</td><td>—</td></tr>
        <tr><th scope="row">指導員B</th><td>—</td><td>配置</td><td>配置</td></tr>
        <tr><th scope="row">問57の例</th><td>（Ⅰ）イ</td><td><strong>（Ⅰ）ロ</strong></td><td>（Ⅰ）イ</td></tr>
      </tbody></table>
    </div>
    <p className="dayservice-example-note">訓練を受けた利用者ごとに確認します。これは令和6年度Q&A問57の配置例であり、他の算定要件まで満たしたことを意味しません。</p>
  </figure>;
}

function ExtensionTimingExample() {
  return <figure className="dayservice-timing-example">
    <figcaption>延長加算の時間帯例（報酬告示注6による時間の考え方）</figcaption>
    <div className="dayservice-time-example-scroll" role="region" tabIndex={0} aria-label="通所介護と前後の世話の時間帯例">
      <table><thead><tr><th scope="col">時間</th><th scope="col">9〜17時30分</th><th scope="col">17時30分〜18時30分</th></tr></thead>
      <tbody><tr><th scope="row">提供内容</th><td>通所介護：8時間30分</td><td>引き続き日常生活上の世話：1時間</td></tr>
      <tr><th scope="row">合計</th><td colSpan={2}><strong>9時間30分</strong>（時間条件の例）</td></tr></tbody></table>
    </div>
    <p className="dayservice-example-note">届出、実際の提供内容、利用者ごとの条件、宿泊サービスとの関係などは別途確認が必要です。この図だけでは算定可否を決められません。</p>
  </figure>;
}

function OfficialLink({ url, children }: { url: string; children: React.ReactNode }) {
  const href = nationalSourceUrl(url);
  return href ? <a href={href} target="_blank" rel="noopener noreferrer">{children} ↗</a> : <span>出典リンクを確認中</span>;
}

function Excerpt({ reference, showCaution = true, showSourceTitle = true, showLabel = true }: { reference: ReaderReference; showCaution?: boolean; showSourceTitle?: boolean; showLabel?: boolean }) {
  const excerpt = readerExcerpt(reference);
  const table = reference.family === "fee" ? basicFeeTable(excerpt.text) : null;
  const applied = excerpt.readAcross ? dayserviceAppliedText(excerpt.id, excerpt.text) : null;
  return <div className="dayservice-excerpt" data-source-id={excerpt.id}>
    <p className="dayservice-excerpt-label">{showLabel && !table ? <strong>{excerpt.label}</strong> : null}<span>{excerpt.locator}</span></p>
    {showCaution && excerpt.caution ? <p className="handbook-role-warning dayservice-source-caution">{excerpt.caution}</p> : null}
    {applied ? <>
      <p className="dayservice-read-across">第105条の準用・読替えに沿い、サービス名等を通所介護に置き換えた表示です。<Link href="/rules/105?service=dayservice">準用の規定を確認</Link></p>
      <div className="dayservice-applied-text"><OriginalText text={applied} /></div>
      <details className="dayservice-original-details"><summary>読替え前の原文を確認する</summary><blockquote><OriginalText text={excerpt.text} /></blockquote></details>
    </> : table ? <>
      <FeeTable title={excerpt.label} rows={table} />
      <details className="dayservice-original-details"><summary>表の元となる告示の原文を確認する</summary><blockquote><OriginalText text={excerpt.text} /></blockquote></details>
    </> : <blockquote><OriginalText text={excerpt.text} /></blockquote>}
    <div className="dayservice-source-citation">{showSourceTitle ? <span>{excerpt.sourceTitle}</span> : null}
      <ul>{excerpt.links.map(link => <li key={link.url}><OfficialLink url={link.url}>{link.label}</OfficialLink></li>)}</ul>
    </div>
  </div>;
}

function NationalQa({ id, anchorId }: { id: string; anchorId: string }) {
  const qa = dayserviceQa(id);
  return <article id={anchorId} className="dayservice-qa" data-qa-id={id}>
    <p className="dayservice-qa-citation"><strong>問{qa.number}</strong><span className="dayservice-qa-topic">{qa.topic}</span><span>{qa.issuedLabel}</span></p>
    {qa.scopeNote ? <p className="dayservice-source-caution">{qa.scopeNote}</p> : null}
    <div className="dayservice-qa-question"><strong>質問</strong><OriginalText text={qa.question} /></div>
    <div className="dayservice-qa-answer"><strong>回答</strong><OriginalText text={qa.answer} /></div>
    <p className="dayservice-source-citation"><OfficialLink url={qa.originalUrl}>{qa.citationLabel}</OfficialLink><span>公式Q&A集の収載本文を表示。発出後の改正との適用関係は未確認です。</span></p>
  </article>;
}

function ReadingTopic({ topic, full, navigationId, requirementIds }: { topic: ReaderTopic; full: boolean; navigationId: string; requirementIds?: string[] }) {
  const TopicHeading = full ? "h2" : "h3";
  const BlockHeading = full ? "h3" : "h4";
  const isFee = topic.basis.some(reference => reference.family === "fee");
  const hasExample = ["staffing-role-life-counselor", "staffing-role-care-worker"].includes(topic.id);
  const sections = [
    ...(topic.basis.length ? [{ id: `${topic.id}-basis`, title: isFee ? "報酬告示" : "基準" }] : []),
    ...(topic.criteria?.length ? [{ id: `${topic.id}-criteria`, title: "大臣基準" }] : []),
    ...(topic.interpretation?.length ? [{ id: `${topic.id}-interpretation`, title: "解釈通知・留意事項" }] : []),
    ...(hasExample ? [{ id: `${topic.id}-example`, title: "勤務時間の計算例" }] : []),
    ...(topic.qa?.length ? [{ id: `${topic.id}-qa`, title: "国Q&A" }] : []),
  ];
  return <section id={topic.id} className={`dayservice-reading-topic${topic.id.startsWith("staffing-role-") ? " handbook-role" : ""}`}>
    {requirementIds?.map(id => <span key={id} id={`${topic.id}-requirement-${id}`} className="dayservice-legacy-anchor" />)}
    <TopicHeading>{topic.title}</TopicHeading>
    {topic.readerSummary ? <div className="dayservice-reader-overview">
      <p><strong>必要な基準の要点</strong></p><p>{topic.readerSummary}</p>
      {topic.readerConditions?.length ? <section aria-label="主な条件"><p><strong>主な条件</strong></p><ul>{topic.readerConditions.map(value => <li key={value}>{value}</li>)}</ul></section> : null}
      {topic.readerExceptions?.length ? <section aria-label="例外・注意"><p><strong>例外・注意</strong></p><ul>{topic.readerExceptions.map(value => <li key={value}>{value}</li>)}</ul></section> : null}
      <p className="dayservice-reader-question-note">要点は国の資料から整理した案内です。原文・発出時期・適用地域も確認してください。</p>
    </div> : null}
    {topic.readerQuestions?.length ? <aside className="dayservice-reader-questions" aria-label="この項目で確認すること">
      <p><strong>この項目で確認すること</strong></p>
      <ul>{topic.readerQuestions.map(question => <li key={question}>{question}</li>)}</ul>
      <p className="dayservice-reader-question-note">確認の入口です。該当する国の基準・通知・Q&Aに続けて目を通してください。</p>
    </aside> : null}
    {sections.length > 1 && (topic.criteria?.length || topic.qa?.length) ? <nav className="dayservice-source-navigation" aria-label={`${topic.title}の資料へ移動`}><ul>{sections.map(section => <li key={section.id}><a href={`#${section.id}`}>{section.title}</a></li>)}</ul></nav> : null}
    {topic.basis.length ? <section className="dayservice-source-block" id={`${topic.id}-basis`}><BlockHeading>{isFee ? "報酬告示" : "基準"}</BlockHeading>{topic.basis.map((reference, index) => <Excerpt key={reference.id} reference={reference} showLabel={reference.family !== "fee" || topic.basis.length > 1} showCaution={reference.family !== "fee"} showSourceTitle={index === 0 || reference.family !== topic.basis[index - 1].family} />)}</section> : null}
    {topic.criteria?.length ? <section className="dayservice-source-block" id={`${topic.id}-criteria`}><BlockHeading>厚生労働大臣が定める基準・算定方法</BlockHeading>{topic.criteria.map((reference, index) => <Excerpt key={reference.id} reference={reference} showLabel={false} showCaution={index === 0} />)}</section> : null}
    {topic.interpretation?.length ? <section className="dayservice-source-block" id={`${topic.id}-interpretation`}><BlockHeading>国の解釈通知・留意事項</BlockHeading>{topic.interpretation.map((reference, index) => <Excerpt key={`${reference.id}-${reference.part || ""}`} reference={reference} showCaution={index === 0} />)}</section> : null}
    {hasExample ? <section className="dayservice-source-block" id={`${topic.id}-example`}><BlockHeading>勤務時間の計算例</BlockHeading>{topic.id === "staffing-role-life-counselor" ? <LifeCounselorExample /> : <CareWorkerExample />}</section> : null}
    {topic.qa?.length ? <section className="dayservice-source-block" id={`${topic.id}-qa`}><BlockHeading>国Q&A</BlockHeading>{topic.qa.map(id => <NationalQa key={id} id={id} anchorId={`${topic.id}-qa-${id}`} />)}</section> : null}
    {topic.id === "fee-note-13" ? <TrainingOverlapExample /> : null}
    {topic.id === "fee-note-6" ? <ExtensionTimingExample /> : null}
    {topic.officialQaFurther?.length ? <section className="dayservice-source-block dayservice-official-qa-links" aria-label="あわせて確認する国Q&A">
      <BlockHeading>国Q&Aと回答の要点（発出資料）</BlockHeading>
      <ul>{topic.officialQaFurther.map(item => <li key={item.number}>
        <strong>{item.issuedLabel || (topic.id === "fee-note-6" ? "平成27年度Q&A Vol.1" : "令和6年度Q&A Vol.1")}・問{item.number}：{item.label}</strong>
        {item.explanation ? <p>{item.explanation}</p> : null}
        <OfficialLink url={item.url}>厚生労働省の問{item.number}を開く</OfficialLink>
      </li>)}</ul>
      <p>上記は発出時点の回答の要点です。後続改正との適用関係は未確認です。算定前に最新の国の資料も確認してください。</p>
    </section> : null}
    {topic.qaSearchQuery ? <p className="dayservice-qa-search-link">
      <Link href={`/qa?reader=1&service=16&q=${encodeURIComponent(topic.qaSearchQuery)}`}>「{topic.qaSearchQuery}」に関する国Q&Aをさらに探す</Link>
      <span>検索結果には過去の取扱いも含まれます。発出日と後続改正を確認してください。</span>
      <span className="dayservice-qa-print-url">印刷版から探す場合：kaigo-rules.vercel.app/qa?reader=1 で「{topic.qaSearchQuery}」を検索</span>
    </p> : null}
    {topic.local ? <aside className="dayservice-local"><p><strong>所在地の指定権者に確認すること</strong></p><p>{topic.local}</p></aside> : null}
    {topic.note ? <p>{topic.note}</p> : null}
    <p className="handbook-role-return"><a href={`#${navigationId}`}>{topic.id.startsWith("staffing-role-") ? "職種一覧に戻る ↑" : "項目一覧に戻る ↑"}</a></p>
  </section>;
}

function QaIndex() {
  return <ul className="dayservice-qa-index">{dayserviceQaIndex().map(item => <li key={item.qa.id}>
    <Link href={`${handbookChapterHref("dayservice", item.chapterId)}#${item.topicId}-qa-${item.qa.id}`}><strong>{item.topicTitle}：問{item.qa.number}</strong><span>{item.qa.question}</span></Link>
    <p className="meta">{item.qa.topic} ／ {item.qa.issuedLabel}</p>
  </li>)}</ul>;
}

function SourceGuide() {
  return <dl className="reader-source-types">
    <div><dt>基準省令</dt><dd><OfficialLink url="https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0">指定居宅サービス等の人員・設備・運営基準（第92条〜第107条）</OfficialLink><p>国の基準を掲載しています。所在地の条例・規則に独自の規定がある場合は、指定権者に確認してください。</p></dd></div>
    <div><dt>解釈通知・算定上の留意事項</dt><dd><Link href="/notices?service=dayservice">通所介護に関連する解釈通知</Link> ／ <Link href="/services/dayservice/remuneration/guidance">算定上の留意事項</Link><p>改正資料から整理した本文を含みます。各掲載箇所の資料・版と、確認が済んでいない事項を併記しています。</p></dd></div>
    <div><dt>報酬告示</dt><dd><Link href="/services/dayservice/remuneration">通所介護の報酬基準</Link><p>加算・減算は、告示だけでなく、参照先の大臣基準・留意事項・届出の条件も確認してください。</p></dd></div>
    <div><dt>国Q&A</dt><dd><OfficialLink url={dayserviceQaIndex()[0].qa.workbookUrl}>厚生労働省の介護サービス関係Q&A集</OfficialLink><p>各項目には関連する質問と回答、出典へのリンクを掲載しています。</p></dd></div>
  </dl>;
}

export default function DayserviceHandbookChapter({ chapter, full }: { service: ServiceHandbookData; chapter: HandbookChapter; full: boolean }) {
  const groups = dayserviceChapterGroups[chapter.section_id] || [];
  const isStaffing = chapter.section_id === "staffing";
  const expanded = full || isStaffing;
  const navigationId = isStaffing ? "staffing-role-navigation" : `${chapter.section_id}-topic-navigation`;
  const href = handbookChapterHref("dayservice", chapter.section_id);
  return <section className="section handbook-chapter handbook-dayservice dayservice-national-reader" id={chapter.section_id}>
    <p className="eyebrow">第{String(chapter.number).padStart(2, "0")}章</p>
    {!full ? <h2><Link href={href}>{chapter.title}</Link></h2> : null}
    <p className="dayservice-chapter-intro">{dayserviceChapterIntros[chapter.section_id]}</p>
    {full ? <p className="handbook-return-link"><Link href={`/services/dayservice#${chapter.section_id}`}>通所介護の手引に戻る</Link></p> : null}
    {isStaffing ? <div className="staffing-reading-guide"><p>国の基準、解釈通知の掲載資料、国Q&Aの順に読めます。解釈通知等には現行性を確認中の本文が含まれます。各資料の注意を併せて確認してください。</p></div> : null}
    {full && ["remuneration", "additions", "deductions"].includes(chapter.section_id) ? <p className="handbook-role-warning">掲載する報酬本文の適用版・改正附則と、参照される大臣基準・留意事項の照合は未完了です。この章だけでは算定可否を確定できません。</p> : null}
    {groups.length ? <nav className={isStaffing ? "handbook-role-navigation dayservice-topic-navigation" : "dayservice-topic-navigation"} id={navigationId} aria-label={isStaffing ? "職種・適用区分から探す" : "この章の項目"}>
      {groups.map(group => <div key={group.title}><p><strong>{group.title}</strong></p><ul>{group.topics.map(topic => <li key={topic.id}>{expanded ? <a href={`#${topic.id}`}>{topic.title}</a> : <Link href={`${href}#${topic.id}`}>{topic.title}</Link>}</li>)}</ul></div>)}
      {isStaffing ? <div><p><strong>勤務時間の計算例から読む</strong></p><ul><li><a href="#staffing-role-life-counselor-example">生活相談員の計算例</a></li><li><a href="#staffing-role-care-worker-example">介護職員の計算例</a></li></ul></div> : null}
    </nav> : null}
    {expanded ? groups.flatMap(group => group.topics).map(topic => <ReadingTopic key={topic.id} topic={topic} full={full} navigationId={navigationId} requirementIds={chapter.role_sections?.find(role => topic.id === `staffing-role-${role.id}`)?.requirements.map(item => item.id)} />) : null}
    {chapter.section_id === "national_qa" ? <><QaIndex /><p><Link href="/qa?service=16">通所介護の国Q&Aを検索する →</Link></p><p><Link href="/qa">共通事項を含む国Q&A全体を検索する →</Link></p></> : null}
    {chapter.section_id === "sources_and_history" ? <SourceGuide /> : null}
    {chapter.section_id === "notifications" ? <aside className="dayservice-local"><p><strong>問い合わせ時に伝えること</strong></p><p>変更する事項、変更予定日、事業所の指定区分を伝え、変更届・体制届の要否、提出期限、必要書類を確認してください。</p><p><Link href="/handbook/dayservice/additions">加算の規定を確認する</Link> ／ <Link href="/handbook/dayservice/deductions">減算の規定を確認する</Link></p></aside> : null}
    {isStaffing ? <details className="dayservice-checks" open={full}><summary>人員基準の確認用チェック欄</summary>
      <p>提供時間数を確認するときは、計画と実績を区別してください。<a href="#staffing-role-life-counselor-qa">提供時間数についての国Q&A（平成24年度・問11）</a></p>
      <HandbookChecklist items={chapter.checkpoints} chapterTitle={chapter.title} /></details> : null}
    {full ? <HandbookPrint /> : null}
    <div id={`handbook-sources-${chapter.section_id}`} className="handbook-inline-links">
      {!full ? <Link href={href}>この章を詳しく読む →</Link> : <Link href="/handbook/dayservice/sources-and-history">資料の種類・出典を確認する →</Link>}
    </div>
  </section>;
}
