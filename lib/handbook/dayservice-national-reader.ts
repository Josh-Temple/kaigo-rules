import standards from "../../data/ordinance37-nodes.json" with { type: "json" };
import careAct from "../../data/care-insurance-act-nodes.json" with { type: "json" };
import personnel from "../../data/notice-personnel-current-text-candidates.json" with { type: "json" };
import equipment from "../../data/notice-equipment-current-text-candidates.json" with { type: "json" };
import operations from "../../data/notice-operation-modern-current-text-candidates.json" with { type: "json" };
import legacyOperations from "../../data/notice-operation-legacy-current-text-candidates.json" with { type: "json" };
import feeGuidance from "../../data/fee-guidance-current-text-candidates.json" with { type: "json" };
import fees from "../../data/remuneration-current-text.json" with { type: "json" };
import feeIndex from "../../data/remuneration-current-skeleton.json" with { type: "json" };
import qaCorpus from "../../data/qa-corpus.json" with { type: "json" };
import qaMeta from "../../data/qa-corpus-meta.json" with { type: "json" };
import sources from "../../data/sources.json" with { type: "json" };
import delegated from "../../data/remuneration-delegated-nodes.json" with { type: "json" };
import { conciseFeeLocator } from "./dayservice-source-layout.ts";

/** A reading projection. Source bodies, review states and other services stay unchanged. */
export type ReaderReference = { family: "law" | "standard" | "notice" | "fee" | "fee-guidance" | "delegated"; id: string; label?: string; part?: string; readAcross?: boolean };
export type ReaderTopic = {
  id: string; title: string; basis: ReaderReference[]; interpretation?: ReaderReference[];
  qa?: string[]; local?: string; note?: string; criteria?: ReaderReference[];
  readerQuestions?: readonly string[]; qaSearchQuery?: string;
};
export type ReaderGroup = { title: string; topics: ReaderTopic[] };
export type ReaderExcerpt = {
  id: string; label: string; text: string; sourceTitle: string; locator: string;
  links: { label: string; url: string }[]; caution?: string; readAcross: boolean;
};

const standardById = new Map(standards.map(row => [row.id, row]));
const lawById = new Map(careAct.map(row => [row.id, row]));
const feeById = new Map(fees.map(row => [row.fee_id, row]));
const feeTitles = new Map(feeIndex.map(row => [row.id, row.title]));
const qaById = new Map(qaCorpus.map(row => [row.id, row]));
const sourceById = new Map(sources.map(row => [row.id, row]));
const noticeById = new Map([...personnel.items, ...equipment.items, ...operations.items, ...legacyOperations.items].map(row => [row.notice_id, row]));
const feeGuidanceById = new Map(feeGuidance.items.map(row => [row.guidance_id, row]));
const delegatedById = new Map(delegated.map(row => [row.id, row]));
const standardUrl = "https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0";

export function nationalSourceUrl(value: string): string | null {
  if (value !== value.trim() || /[\u0000-\u0020\u007f\\]/u.test(value)) return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port &&
      (url.hostname === "mhlw.go.jp" || url.hostname.endsWith(".mhlw.go.jp") || url.hostname === "laws.e-gov.go.jp") ? url.href : null;
  } catch { return null; }
}

function standardLocator(id: string): string {
  const match = /^ordinance37\.article\.([0-9-]+)(?:\.p\.(\d+))?(?:\.i\.(\d+))?/.exec(id);
  if (!match) throw new Error(`Unrecognised standard reference: ${id}`);
  const [article, branch] = match[1].split("-");
  return `第${article}条${branch ? `の${branch}` : ""}${match[2] ? `第${match[2]}項` : ""}${match[3] ? `第${match[3]}号` : ""}`;
}

/** Select a complete numbered paragraph; never cut at a fixed character count. */
export function numberedNoticePart(text: string, marker?: string): string {
  if (!marker) return text;
  const markers = "①②③④⑤⑥⑦⑧⑨⑩";
  const index = markers.indexOf(marker);
  if (marker.length !== 1 || index < 0) throw new Error(`Invalid notice marker: ${marker}`);
  const start = text.indexOf(marker);
  if (start < 0) throw new Error(`Missing notice marker: ${marker}`);
  // A paragraph may refer to itself (e.g. 「以下⑤について同じ」).
  const end = index < markers.length - 1 ? text.indexOf(markers[index + 1], start + 1) : -1;
  return end < 0 ? text.slice(start) : text.slice(start, end);
}

export function readerExcerpt(ref: ReaderReference): ReaderExcerpt {
  if (ref.family === "delegated") {
    const row = delegatedById.get(ref.id);
    if (!row?.official_text) throw new Error(`Missing delegated text: ${ref.id}`);
    const source = sourceById.get(row.source_id);
    return { id: row.id, label: ref.label || row.heading, text: row.official_text,
      sourceTitle: source?.title || "厚生労働大臣が定める基準（別告示）", locator: row.heading.split(" ")[0],
      links: [{ label: "厚生労働省の別告示を確認", url: row.source_url }],
      caution: "別告示の掲載本文です。適用版・後続改正と、報酬告示・留意事項との照合は未完了です。", readAcross: false };
  }
  if (ref.family === "law") {
    const row = lawById.get(ref.id);
    if (!row?.official_text) throw new Error(`Missing law text: ${ref.id}`);
    return { id: ref.id, label: ref.label || "介護保険法", text: row.official_text, sourceTitle: "介護保険法",
      locator: row.source_locator, links: [{ label: "e-Govの条文を確認", url: row.source_url }], readAcross: false };
  }
  if (ref.family === "standard") {
    const row = standardById.get(ref.id);
    if (!row?.official_text) throw new Error(`Missing standard text: ${ref.id}`);
    return { id: ref.id, label: ref.label || row.caption || standardLocator(ref.id), text: row.official_text,
      sourceTitle: "指定居宅サービス等の事業の人員、設備及び運営に関する基準（厚生省令第37号）",
      locator: `${standardLocator(ref.id)}${ref.readAcross ? "（第105条により準用）" : ""}`,
      links: [{ label: "厚生労働省の条文を確認", url: standardUrl }], readAcross: !!ref.readAcross };
  }
  if (ref.family === "fee") {
    const row = feeById.get(ref.id);
    if (!row?.official_text) throw new Error(`Missing remuneration text: ${ref.id}`);
    return { id: ref.id, label: ref.label || feeTitles.get(ref.id) || "報酬告示", text: row.official_text,
      sourceTitle: "指定居宅サービスに要する費用の額の算定に関する基準", locator: conciseFeeLocator(row.source_locator),
      links: [{ label: "厚生労働省の報酬告示を確認", url: row.source_url }],
      caution: "掲載本文の適用版・改正附則と、参照される大臣基準・留意事項の照合は未完了です。", readAcross: false };
  }
  const row = ref.family === "notice" ? noticeById.get(ref.id) : feeGuidanceById.get(ref.id);
  if (!row?.candidate_text) throw new Error(`Missing notice text: ${ref.id}`);
  const evidence = ref.id === "notice.dayservice.personnel.staffing" && ref.part
    ? row.evidence.filter(item => ref.part === "⑥" ? item.source_id === "mhlw-2021-interpretation-redline" : "role" in item && item.role === "baseline")
    : row.evidence;
  const links = evidence.map(evidence => {
    const source = sourceById.get(evidence.source_id);
    if (!source?.url) throw new Error(`Missing source: ${evidence.source_id}`);
    // Physical pages checked in the H27 source: the broad staffing range starts
    // on p45, but the counselor passage starts on p46 and the care passage on p47.
    const page = ref.id === "notice.dayservice.personnel.staffing" && evidence.source_id === "mhlw-h27-interpretation-redline"
      ? ref.part === "④" ? 46 : ref.part === "⑤" ? 47 : evidence.page_start
      : evidence.page_start;
    return { label: source.title, url: `${source.url}#page=${page}` };
  }).filter((link, index, all) => all.findIndex(other => other.url === link.url) === index);
  return { id: ref.id, label: ref.label || row.title, text: numberedNoticePart(row.candidate_text, ref.part),
    sourceTitle: ref.family === "notice" ? "基準の解釈通知・改正資料（老企第25号）" : "報酬の算定上の留意事項・改正資料",
    locator: `${row.number_path.join("・")}${ref.part ? `・${ref.part}` : ""}`,
    links, caution: ref.id === "notice.dayservice.personnel.staffing" && ref.part === "⑤"
      ? "過去の改正資料の本文です。冒頭の「第2項の適用を受ける場合」は旧規定への参照を含みます。現行の配置要件は上の第93条も併せて確認してください。後続改正との照合は未完了です。"
      : "過去の改正資料から整理した掲載本文です。参照条番号・現行性・後続改正との照合は未完了です。", readAcross: false };
}

// Question numbers and physical PDF pages were checked against the original PDFs.
// Questions/answers themselves remain references to the unchanged official workbook corpus.
export const dayserviceQaLocators: Record<string, { number: string; page?: number; url: string; collection?: boolean; issuedLabel?: string }> = {
  "qa.mhlw.09387a7f7b6c9726887a": { number: "44", page: 27, url: "https://www.mhlw.go.jp/content/12404000/000760502.pdf" },
  "qa.mhlw.d9a7f5b49c1ba8a9326e": { number: "59", page: 36, url: "https://www.mhlw.go.jp/content/12300000/001230308.pdf" },
  "qa.mhlw.a3ceb95affec100c3cc3": { number: "184", page: 111, url: "https://www.mhlw.go.jp/content/12300000/001230308.pdf" },
  "qa.mhlw.012fdfa8b64a3b333d4e": { number: "58", page: 35, url: "https://www.mhlw.go.jp/content/12300000/001230308.pdf" },
  "qa.mhlw.5dcdd91060267fa2466d": { number: "63", page: 39, url: "https://www.mhlw.go.jp/content/12300000/001230308.pdf" },
  "qa.mhlw.52fc9e66a5367b1901bf": { number: "64", page: 39, url: "https://www.mhlw.go.jp/content/12300000/001230308.pdf" },
  "qa.mhlw.98d49d29f427379ec4b3": { number: "62", page: 38, url: "https://www.mhlw.go.jp/content/12300000/001230308.pdf" },
  "qa.mhlw.19ff5348270062de7154": { number: "45", page: 28, url: "https://www.mhlw.go.jp/content/12404000/000760502.pdf" },
  // Original vol.273 question numbers were checked in the nationally issued PDF.
  // The public link is explicitly labelled as the Ministry's current Q&A collection.
  "qa.mhlw.98bc1e237f7981f16869": { number: "11", url: qaMeta.source_workbook, collection: true, issuedLabel: "平成24年度介護報酬改定Q&A（Vol.2）／平成24年3月30日" },
  "qa.mhlw.bed5148c4af01939c01d": { number: "12", url: qaMeta.source_workbook, collection: true, issuedLabel: "平成24年度介護報酬改定Q&A（Vol.2）／平成24年3月30日" },
};

export function dayserviceQa(id: string) {
  const row = qaById.get(id);
  const locator = dayserviceQaLocators[id];
  if (!row || !locator || !["01", "02", "06", "16"].includes(row.service_code)) throw new Error(`Q&A has no scoped original locator: ${id}`);
  return { ...row, number: locator.number, originalUrl: locator.page ? `${locator.url}#page=${locator.page}` : locator.url, workbookUrl: qaMeta.source_workbook,
    citationLabel: locator.collection ? "厚生労働省Q&A集で確認する" : "この問の発出資料",
    scopeNote: id === "qa.mhlw.19ff5348270062de7154" ? "指定通所介護の取扱いは回答①です。回答②は地域密着型通所介護についての記載です。" : undefined,
    issuedLabel: locator.issuedLabel || (locator.url.includes("000760502") ? "令和3年度介護報酬改定Q&A（Vol.3）／令和3年3月26日" : "令和6年度介護報酬改定Q&A（Vol.1）／令和6年3月15日") };
}

const s = (article: string, label?: string, readAcross = false): ReaderReference => ({ family: "standard", id: `ordinance37.article.${article}`, label, readAcross });
const n = (id: string, part?: string): ReaderReference => ({ family: "notice", id: `notice.dayservice.${id}`, part });
const f = (number: string): ReaderReference => ({ family: "fee", id: `fee.dayservice.${number}` });
const fg = (number: string): ReaderReference => ({ family: "fee-guidance", id: `fee-guidance.dayservice.${number}` });
const fullTimeQa = "qa.mhlw.09387a7f7b6c9726887a";

export const dayserviceStaffingTopics: ReaderTopic[] = [
  { id: "staffing-role-life-counselor", title: "生活相談員", basis: [s("93.p.1.i.1", "提供日ごとの配置"), s("93.p.6", "常勤者の確保")],
    interpretation: [n("personnel.staffing", "④"), n("personnel.life-counselor")], qa: [fullTimeQa, "qa.mhlw.98bc1e237f7981f16869", "qa.mhlw.bed5148c4af01939c01d"],
    local: "資格の認定範囲や実務経験の取扱い、必要書類は、事業所所在地を所管する指定権者の介護保険担当窓口に確認してください。" },
  { id: "staffing-role-nurse", title: "看護職員", basis: [s("93.p.1.i.2", "単位ごとの確保")],
    interpretation: [n("personnel.staffing", "⑥")], qa: ["qa.mhlw.d9a7f5b49c1ba8a9326e", "qa.mhlw.19ff5348270062de7154"],
    readerQuestions: [
      "単位ごとの看護職員をどのように確保するか？",
      "外部の病院・診療所・訪問看護ステーションと連携する場合、健康状態の確認・連絡体制はどうするか？",
      "機能訓練指導員との兼務について、国Q&Aと配置条件を確認したか？",
    ],
    qaSearchQuery: "看護職員",
    local: "外部連携を行う場合の契約・連絡体制や提出書類は、所在地の指定権者に確認してください。" },
  { id: "staffing-role-care-worker", title: "介護職員", basis: [s("93.p.1.i.3", "必要な勤務時間と利用者数"), s("93.p.2", "単位ごとの常時配置"), s("93.p.3", "他の単位との兼務"), s("93.p.6", "常勤者の確保")],
    interpretation: [n("personnel.staffing", "⑤")], qa: [fullTimeQa, "qa.mhlw.98bc1e237f7981f16869"],
    readerQuestions: [
      "利用者数と平均提供時間数から必要な勤務延時間数を確認したか？",
      "各単位のサービス提供中、介護職員の常時配置を確認したか？",
      "他の単位と兼務する場合、利用者の処遇に支障がないか確認したか？",
    ],
    qaSearchQuery: "介護職員" },
  { id: "staffing-role-functional-training", title: "機能訓練指導員", basis: [s("93.p.1.i.4", "配置人数"), s("93.p.5", "能力と兼務")],
    interpretation: [n("personnel.function-training")], qa: ["qa.mhlw.012fdfa8b64a3b333d4e", "qa.mhlw.19ff5348270062de7154"],
    local: "資格・経験の確認書類や、併設施設との取扱いは、所在地の指定権者に確認してください。" },
  { id: "staffing-role-manager", title: "管理者", basis: [s("94.p.1", "常勤・専従と兼務"), s("52", "管理者の責務", true)],
    interpretation: [n("personnel.manager")], qa: ["qa.mhlw.a3ceb95affec100c3cc3"],
    local: "兼務する職務・事業所、勤務体制と緊急時の対応を示し、管理に支障がないか、所在地の指定権者に確認してください。" },
];

function topic(id: string, title: string, basis: ReaderReference[], interpretation?: ReaderReference[], qa?: string[], local?: string): ReaderTopic {
  return { id, title, basis, interpretation, qa, local };
}
const operationTopics: ReaderGroup[] = [
  { title: "サービス開始前", topics: [
    topic("explanation-consent", "内容・手続の説明と同意", [s("8", undefined, true)]),
    topic("acceptance", "提供拒否の禁止", [s("9", undefined, true)]),
    topic("service-difficulty", "サービス提供困難時の対応", [s("10", undefined, true)]),
    topic("eligibility", "受給資格等の確認", [s("11", undefined, true)]),
    topic("certification-support", "要介護認定の申請・更新の援助", [s("12", undefined, true)]),
  ] },
  { title: "利用開始と計画の作成", topics: [
    topic("assessment-coordination", "心身の状況把握と関係事業者との連携", [s("13", undefined, true), s("14", undefined, true), s("15", undefined, true)]),
    topic("care-plan", "居宅サービス計画との関係・通所介護計画", [s("16", undefined, true), s("17", undefined, true), s("99")], [n("operation.plan")]),
    topic("service-policy", "サービス提供の基本方針・具体的な取扱い", [s("97"), s("98")], [n("operation.policy")]),
  ] },
  { title: "サービス提供時", topics: [
    topic("service-record", "サービス提供の記録", [s("19", undefined, true)]),
    topic("charges", "利用料・費用の受領と証明書", [s("96"), s("21", undefined, true)], [n("operation.fees")]),
    topic("emergency", "市町村への通知・緊急時の対応", [s("26", undefined, true), s("27", undefined, true)]),
  ] },
  { title: "事業所の運営", topics: [
    topic("manager-duties", "管理者の責務", [s("52", undefined, true)], undefined, ["qa.mhlw.a3ceb95affec100c3cc3"]),
    topic("management-rules", "運営規程", [s("100")], [n("operation.rules")]),
    topic("working-system", "勤務体制と定員の遵守", [s("101"), s("102")], [n("operation.staffing")]),
    topic("community", "地域との連携等", [s("104-2")], [n("operation.community")]),
    topic("disclosure-privacy", "重要事項の掲示・ウェブサイトへの掲載", [s("32", undefined, true)]),
    topic("privacy", "秘密保持・個人情報の利用", [s("33", undefined, true)]),
    topic("advertising", "広告", [s("34", undefined, true)]),
    topic("profit-provision", "居宅介護支援事業者への利益供与の禁止", [s("35", undefined, true)]),
    topic("complaints-accounts", "苦情処理", [s("36", undefined, true)]),
    topic("accounts", "会計の区分", [s("38", undefined, true)]),
  ] },
];

const additionIds = ["note.5", "note.6", "note.8", "note.9", "note.10", "note.11", "note.12", "note.13", "note.14", "note.15", "note.16", "note.17", "note.18", "note.19", "note.20", "note.21", "service-provision", "treatment-improvement"];
const feeTopic = (id: string): ReaderTopic => ({ ...topic(`fee-${id.replaceAll(".", "-")}`, feeTitles.get(`fee.dayservice.${id}`) || id, [f(id)],
  id === "note.6" ? [fg("5")] : id === "note.5" ? [fg("7-2")] : undefined,
  id === "note.10" ? ["qa.mhlw.98d49d29f427379ec4b3", "qa.mhlw.5dcdd91060267fa2466d"] : id === "note.13" ? ["qa.mhlw.012fdfa8b64a3b333d4e"] : undefined),
  criteria: delegated.filter(row => (row.related_fee_ids.includes(`fee.dayservice.${id}`) ||
    ({ "note.8": "criteria95.dayservice.14-5", "note.19": "criteria95.dayservice.19-2", "note.20": "criteria95.dayservice.20" } as Record<string, string>)[id] === row.id) && row.id.startsWith("criteria95.dayservice.")).map(row => ({ family: "delegated" as const, id: row.id })),
  ...(id === "note.13" ? {
    readerQuestions: [
      "算定を検討するのは個別機能訓練加算（Ⅰ）イ・（Ⅰ）ロ・（Ⅱ）のどれか？",
      "配置・計画・届出など、該当する区分の条件を別告示と留意事項で確認したか？",
      "人員基準としての配置と、加算の算定要件を区別して確認したか？",
    ],
    qaSearchQuery: "個別機能訓練加算",
  } : id === "note.6" ? {
    readerQuestions: [
      "指定通所介護の所要時間は8時間以上9時間未満か？",
      "通所介護の前後に引き続き日常生活上の世話を行ったか？",
      "通所介護と前後の世話の時間の合計・届出・該当区分を確認したか？",
    ],
    qaSearchQuery: "延長加算",
  } : {}),
});

export const dayserviceChapterGroups: Record<string, ReaderGroup[]> = {
  staffing: [{ title: "はじめに確認する用語", topics: [
    topic("staffing-unit", "単位の定義", [s("93.p.4")], [n("personnel.staffing", "①")]),
  ] }, { title: "職種ごとの人員基準", topics: dayserviceStaffingTopics }, { title: "一体的に運営する場合", topics: [
    topic("staffing-integrated", "第一号通所事業との一体的運営", [s("93.p.7"), s("93.p.1.i.3")], undefined, undefined,
      "第一号通所事業の基準と一体的運営の取扱いは、事業所所在地の市町村・指定権者に確認してください。"),
  ] }],
  equipment: [{ title: "設備・備品", topics: [
    topic("rooms", "必要な設備・食堂及び機能訓練室・相談室", [s("95.p.1"), s("95.p.2")], [n("equipment.office"), n("equipment.dining-training-room")], undefined,
      "面積の算定方法、建築関係の確認先と必要書類は、所在地の指定権者・関係窓口に確認してください。"),
    topic("fire-safety", "消火設備・非常災害への備え", [s("95.p.1")], [n("equipment.fire-safety")], undefined,
      "建物・利用形態に応じた消防関係の手続・設備は、所在地の消防署等に確認してください。"),
    topic("shared-equipment", "設備の共用", [s("95.p.3")], [n("equipment.shared-equipment")]),
    topic("overnight", "通所介護以外の宿泊サービスを提供する場合", [s("95.p.4")], [n("equipment.overnight-service")], undefined,
      "届出先・様式と地域の指針は、所在地の指定権者に確認してください。"),
    topic("integrated-equipment", "第一号通所事業との一体的運営", [s("95.p.5")], undefined, undefined,
      "第一号通所事業の設備基準と一体的運営の取扱いは、所在地の市町村・指定権者に確認してください。"),
  ] }],
  operations: operationTopics,
  records: [{ title: "記録の作成と保存", topics: [topic("record-retention", "記録の整備・保存期間", [s("104-4"), s("19", undefined, true)], [n("operation.records")], undefined,
    "保存期間や電磁的記録の取扱いは、所在地の指定権者の条例・規則等も確認してください。")]}],
  safeguarding: [{ title: "説明・権利擁護・個人情報", topics: [
    topic("consent-rights", "説明と同意・身体的拘束等の禁止", [s("8", undefined, true), s("98")]),
    topic("confidentiality", "秘密保持・苦情処理", [s("33", undefined, true), s("36", undefined, true)]),
  ] }],
  incident_and_infection: [{ title: "事故・感染症・虐待の防止", topics: [
    topic("accident", "事故発生時の対応", [s("104-3")], [n("operation.accident")], undefined, "事故報告の提出先・対象・様式は、所在地の指定権者等の案内を確認してください。"),
    topic("infection", "衛生管理・感染症対策", [s("104")], [n("operation.hygiene")]),
    topic("abuse", "虐待の防止", [s("37-2", undefined, true)], [n("operation.abuse")]),
  ] }],
  business_continuity: [{ title: "業務継続・非常災害", topics: [
    topic("bcp", "業務継続計画の策定等", [s("30-2", undefined, true)], [n("operation.bcp")]),
    topic("disaster", "非常災害対策", [s("103")], [n("operation.disaster")]),
  ] }],
  remuneration: [{ title: "基本報酬と所要時間", topics: [
    topic("basic-fee", "事業所規模別の基本報酬", [f("standard"), f("large1"), f("large2"), f("note.1")], [fg("6")]),
    topic("short-duration", "2時間以上3時間未満の算定", [f("note.4")], [fg("4")]),
    topic("duration-weather", "急な気象状況の悪化と所要時間", [], undefined, ["qa.mhlw.52fc9e66a5367b1901bf"]),
    feeTopic("note.22"),
  ] }],
  additions: [{ title: "加算の名称から探す", topics: additionIds.map(feeTopic) }],
  deductions: [{ title: "減算の名称から探す", topics: ["note.1", "note.2", "note.3", "note.7", "note.23", "note.24"].map(feeTopic) }],
};

export const dayserviceChapterIntros: Record<string, string> = {
  applicability: "指定通所介護の対象と、国の基準省令で定めるサービスの基本方針を確認します。",
  designation: "指定申請の窓口・必要書類・申請日程は、事業所所在地を所管する指定権者に確認してください。通常の指定、共生型、基準該当は適用する規定が異なります。",
  staffing: "職種ごとに、国の基準・解釈通知の掲載資料・関連する国Q&Aを続けて確認できます。",
  equipment: "必要な設備と利用上の条件を、国の基準省令・解釈通知の掲載資料から確認します。",
  operations: "サービス開始前、計画の作成、サービス提供時、事業所運営の順に確認します。",
  records: "サービス提供・事故・苦情等の記録と保存の規定を確認します。",
  safeguarding: "説明と同意、身体的拘束等の禁止、秘密保持、苦情処理の規定を確認します。",
  incident_and_infection: "事故発生時の対応、衛生管理・感染症対策、虐待防止の規定を項目ごとに確認します。",
  business_continuity: "業務継続計画と非常災害への備えを確認します。報酬の減算要件は減算の章で別に確認してください。",
  remuneration: "基本報酬、所要時間、他サービスとの関係を国の掲載資料から確認します。",
  additions: "加算名から、報酬告示・掲載済みの大臣基準・留意事項・国Q&Aを続けて確認できます。",
  deductions: "減算名から、報酬告示の該当規定を確認できます。定員・人員基準に関する規定と、その他の減算を区別してください。",
  notifications: "変更内容に応じた届出の要否・提出先・様式・期限は、所在地の指定権者の案内で確認してください。報酬の体制届は、該当する加算・減算の規定も確認します。",
  national_qa: "各項目で読める国Q&Aの索引です。質問と回答は、それぞれの基準・解釈通知と併せて確認してください。",
  sources_and_history: "国の基準省令、解釈通知、報酬告示・留意事項、国Q&Aを出典の種類ごとに確認できます。",
};

dayserviceChapterGroups.applicability = [{ title: "対象と基本方針", topics: [
  topic("dayservice-definition", "通所介護の定義", [{ family: "law", id: "careact.article.8.p.7", label: "介護保険法第8条第7項" }]),
  topic("basic-policy", "指定通所介護の基本方針", [s("92")]),
] }];
dayserviceChapterGroups.designation = [{ title: "指定区分", topics: [topic("designation-types", "共生型・基準該当の規定", [s("105-2"), s("105-3"), s("106"), s("107")], undefined, undefined,
  "申請する指定区分、指定の要件、手続・提出書類は、所在地の指定権者へ確認してください。")]}];

export function dayserviceQaIndex() {
  const seen = new Set<string>();
  return Object.entries(dayserviceChapterGroups).flatMap(([chapterId, groups]) => groups.flatMap(group => group.topics.flatMap(item =>
    (item.qa || []).filter(id => { if (seen.has(id)) return false; seen.add(id); return true; })
      .map(id => ({ chapterId, topicId: item.id, topicTitle: item.title, qa: dayserviceQa(id) })),
  )));
}
