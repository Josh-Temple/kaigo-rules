import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import dayservice from "../../docs/prototypes/evidence-bridges/dayservice.json";
import dayrehab from "../../docs/prototypes/evidence-bridges/dayrehab.json";

/**
 * Separate publication contract: this is a source-navigation *index*, never
 * the handbook, its unreviewed candidate paragraphs, or legal content.
 * Canonical source/currentness/human-review/publication HOLD remains unchanged.
 */
export const metadata: Metadata = {
  title: "通所系サービスの公式資料を探す（試験公開・未レビュー）",
  description: "通所介護と通所リハビリテーションの原典候補の所在を、15章の確認観点から探す試用ページ。法的な解釈や適用・算定の判断は提供しません。",
  robots: { index: false, follow: false, nocache: true },
};

type Bridge = typeof dayservice | typeof dayrehab;

const catalogs = [
  { title: "通所介護", id: "dayservice", data: dayservice },
  { title: "通所リハビリテーション", id: "dayrehab", data: dayrehab },
] as const;

function safeOfficialUrl(input: string): string | null {
  try {
    const url = new URL(input);
    if (
      url.protocol !== "https:" ||
      url.username || url.password ||
      url.port ||
      !["www.mhlw.go.jp", "laws.e-gov.go.jp"].includes(url.hostname) ||
      url.hash
    ) return null;
    return url.toString();
  } catch {
    return null;
  }
}

function validBridge(data: Bridge, serviceId: string, first: number, count: number): boolean {
  if (
    data.schema !== "KAIGO_EVIDENCE_CHAPTER_BRIDGE_DRAFT_V1" ||
    data.service_id !== serviceId ||
    data.release_gate !== "HOLD_NO_GO" ||
    data.publication !== "BLOCKED" ||
    data.currentness !== "NOT_ESTABLISHED" ||
    data.applicability !== "NOT_ESTABLISHED" ||
    data.human_review !== "NOT_REVIEWED" ||
    data.real_project_work_enabled !== false ||
    data.legal_explanations_accepted !== 0 ||
    data.chapter_count !== 15 ||
    data.chapters.length !== 15 ||
    data.candidate_paragraph_count !== count ||
    data.source_evidence.length !== 6
  ) return false;

  const evidence = new Map(data.source_evidence.map((r) => [r.task_id, r]));
  const ids = new Set<string>();
  const sections = new Set<string>();
  const tasks = new Set<string>();
  let found = 0;
  for (const r of data.source_evidence) {
    if (
      r.service_id !== serviceId ||
      !r.task_id.startsWith("KR-EVIDENCE-") ||
      !r.library_file_id.startsWith("libfile_") ||
      !/^[0-9a-f]{64}$/.test(r.byte_sha256) ||
      !Number.isInteger(r.size_bytes) || r.size_bytes <= 0
    ) return false;
    tasks.add(r.task_id);
  }
  if (tasks.size !== 6) return false;
  for (let i = 0; i < 6; i++) {
    if (!tasks.has(`KR-EVIDENCE-${String(first + i).padStart(3, "0")}`)) return false;
  }
  for (const chapter of data.chapters) {
    if (!chapter.section_id || !chapter.title || sections.has(chapter.section_id)) return false;
    sections.add(chapter.section_id);
    for (const p of chapter.candidate_paragraphs) {
      const r = evidence.get(p.evidence_task_id);
      if (
        p.draft_review_state !== "DRAFT_UNREVIEWED" ||
        !r ||
        p.evidence_library_file_id !== r.library_file_id ||
        p.source_url_from_evidence !== r.source_url ||
        !p.bridge_id.startsWith("KR-BRIDGE-") ||
        ids.has(p.bridge_id) ||
        !Array.isArray(p.source_identifiers) ||
        p.source_identifiers.some((x) => typeof x !== "string" || x.length > 250)
      ) return false;
      ids.add(p.bridge_id);
      found++;
    }
  }
  return found === count && ids.size === count && sections.size === 15;
}

export default function HandbookSourcesPage() {
  // Fail closed: only the two explicitly checked, UNREVIEWED source inventories
  // may be used in this independent source-directory page.
  if (!validBridge(dayservice, "dayservice", 1, 11) ||
      !validBridge(dayrehab, "dayrehab", 7, 18)) notFound();

  return (
    <article className="answer-page foundation-page" style={{ maxWidth: 1050 }}>
      <p className="eyebrow">資料の所在案内（試験公開）</p>
      <h1>通所系サービスの原典を探す</h1>
      <div className="notice" role="note">
        <strong>試験公開：資料の所在案内のみ・法令解説ではありません。</strong>
        <p>
          介護保険制度の公式資料を探すための仮の目次です。
          章の割当も未レビューです。各項目の掲載は、現行法令・適用条項・人員配置・報酬算定可否が確認されたことを意味しません。
          実務判断の際は公式原典、改正・施行情報、指定権者の条例と案内を改めて確認してください。
        </p>
        <p><strong>出典の現行性と適用条件は確認中です。</strong>
          出典候補ごとの照合は完了しておらず、未レビューの手引本文29文も掲載していません。</p>
      </div>

      <nav aria-label="サービス一覧" className="entry-links">
        {catalogs.map(({ id, title }) => (
          <a key={id} className="entry-row" href={`#${id}`}>{title}の公式資料候補へ ↓</a>
        ))}
      </nav>

      {catalogs.map(({ id, title, data }) => {
        const byId = new Map(data.source_evidence.map((e) => [e.task_id, e]));
        return (
          <section className="section" key={id} id={id}>
            <h2>{title}</h2>
            <p className="meta">
              出典候補を15章の暫定構成で分類しています。
              資料を探すための一覧であり、法令の有効性や適用条件を確認した結果ではありません。
            </p>
            {data.chapters.map((chapter, index) => (
              <details key={chapter.section_id} className="section" open={index === 0}>
                <summary><strong>第{index + 1}章　{chapter.title}</strong>（出典候補{chapter.candidate_paragraphs.length}件）</summary>
                {chapter.candidate_paragraphs.length === 0 ? (
                  <p>追加された出典候補はありません。根拠が存在しないという意味ではありません。</p>
                ) : (
                  <ul>
                    {chapter.candidate_paragraphs.map((item) => {
                      const source = byId.get(item.evidence_task_id);
                      const url = safeOfficialUrl(source?.source_url ?? "");
                      return (
                        <li key={item.bridge_id} style={{ margin: "1rem 0" }}>
                          <strong>原典の掲載先候補</strong>
                          <p className="meta">本文・条文の対応や施行版は未確認です。掲載先の原典を個別に照合してください。</p>
                          {url ? (
                            <p>
                              <a href={url} rel="noopener noreferrer" target="_blank">
                                厚生労働省などの公式掲載先を開く ↗
                              </a>
                              <small>（掲載先の案内。最新版・適用関係の保証ではありません）</small>
                            </p>
                          ) : (
                            <p className="meta">公式サイトへの個別リンクは未確認です。公開中の原典検索から確認してください。</p>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </details>
            ))}
            <p><Link href={`/databases/search?service=${id}`}>公開中の制度資料を横断検索する →</Link></p>
          </section>
        );
      })}
      <section className="section">
        <h2>このページでは判断できないこと</h2>
        <p>
          人員・設備・運営基準の充足、指定や届出の適否、加算・減算、
          法令の最新施行版、準用・読替え、自治体条例、Q&Aの現在性はこのページでは確認していません。
          詳細は原典と指定権者に確認してください。
        </p>
        <p><Link href="/services">サービス一覧に戻る →</Link></p>
      </section>
    </article>
  );
}
