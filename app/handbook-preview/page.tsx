import type { Metadata } from "next";
import { notFound } from "next/navigation";
import dayservice from "../../docs/prototypes/evidence-bridges/dayservice.json";
import dayrehab from "../../docs/prototypes/evidence-bridges/dayrehab.json";

// Restricted release preview: NEVER render on the production deployment.
// Source text is DRAFT_UNREVIEWED, not legally accepted or current.
export const dynamic = "force-dynamic";
export const metadata: Metadata = {
  title: "サービス別手引・未レビュー原典候補（限定プレビュー）",
  description: "原典所在の確認を目的とする未レビューの試用ページです。法令の現行性・適用・算定可否は未確認です。",
  robots: { index: false, follow: false, nocache: true },
};

const services = [
  { data: dayservice, name: "通所介護" },
  { data: dayrehab, name: "通所リハビリテーション" },
] as const;

function isValidForPreview(data: typeof dayservice | typeof dayrehab): boolean {
  if (
    data.schema !== "KAIGO_EVIDENCE_CHAPTER_BRIDGE_DRAFT_V1" ||
    data.release_gate !== "HOLD_NO_GO" ||
    data.publication !== "BLOCKED" ||
    data.currentness !== "NOT_ESTABLISHED" ||
    data.human_review !== "NOT_REVIEWED" ||
    data.legal_explanations_accepted !== 0 ||
    data.real_project_work_enabled !== false ||
    data.chapter_count !== 15 ||
    data.chapters.length !== 15
  ) return false;
  const seen = new Set<string>();
  let count = 0;
  for (const chapter of data.chapters) {
    for (const item of chapter.candidate_paragraphs) {
      if (
        item.draft_review_state !== "DRAFT_UNREVIEWED" ||
        !item.bridge_id ||
        seen.has(item.bridge_id) ||
        typeof item.text !== "string" ||
        item.text.length === 0
      ) return false;
      seen.add(item.bridge_id);
      count++;
    }
  }
  return count === data.candidate_paragraph_count;
}

export default function HandbookEvidencePreviewPage() {
  // The preview environment is protected by Vercel SSO. Production must 404
  // even after these files are eventually merged into main.
  if (
    process.env.VERCEL_ENV !== "preview" &&
    process.env.NODE_ENV !== "development"
  ) notFound();

  if (
    !isValidForPreview(dayservice) ||
    !isValidForPreview(dayrehab) ||
    dayservice.candidate_paragraph_count !== 11 ||
    dayrehab.candidate_paragraph_count !== 18
  ) notFound();

  return (
    <article style={{ maxWidth: 1024, padding: "2rem 1rem", margin: "0 auto" }}>
      <p style={{ fontWeight: 700, color: "#925900" }}>
        LIMITED PREVIEW / DRAFT_UNREVIEWED / NOT_ESTABLISHED
      </p>
      <h1>サービス別手引 — 原典照合の追加候補</h1>
      <p>
        これは原典の所在・確認観点を整理した未レビューの試用版です。
        現行の法令・指定権者の条例・個別サービスへの適用・報酬算定の適否を認定しません。
        実務判断は厚生労働省・e-Govの現行原典および所管行政庁を必ず確認してください。
      </p>
      <p><strong>人手レビュー済み：0件。一般公開・本番反映：未承認。</strong></p>
      <nav aria-label="プレビュー対象サービス">
        {services.map(({ data, name }) => (
          <p key={data.service_id}>
            <a href={`#${data.service_id}`}>{name}（追加{data.candidate_paragraph_count}件）</a>
          </p>
        ))}
      </nav>
      {services.map(({ data, name }) => (
        <section id={data.service_id} key={data.service_id}>
          <h2>{name}</h2>
          <p>
            15章の章割当は作業用の暫定候補です。
            原典案内を掲載することは法令解釈や最新施行版の確認完了を意味しません。
          </p>
          {data.chapters.map((chapter, index) => (
            <section key={chapter.section_id} style={{ margin: "1.4rem 0" }}>
              <h3>第{index + 1}章：{chapter.title}</h3>
              {chapter.candidate_paragraphs.length === 0 ? (
                <p>この章の第2段階追加候補はありません。規制や根拠の不存在を意味しません。</p>
              ) : chapter.candidate_paragraphs.map((item) => (
                <div key={item.bridge_id} style={{ border: "1px solid #b8c4c8", borderRadius: 8, margin: "1rem 0", padding: 14 }}>
                  <h4>確認候補 {item.bridge_id}</h4>
                  <p>{item.text}</p>
                  <p style={{ fontSize: ".875rem" }}>
                    照合記録：{item.evidence_task_id} ／ 根拠候補：{item.source_identifiers.join("、") || "未特定"}
                  </p>
                  <p style={{ fontSize: ".875rem" }}>
                    DRAFT_UNREVIEWED / HUMAN_REVIEW_NOT_DONE /
                    法令の現行性・個別適用 NOT_ESTABLISHED
                  </p>
                </div>
              ))}
            </section>
          ))}
        </section>
      ))}
      <p><strong>公開判定：HOLD_NO_GO。法令の現行性と人手レビューを経ない確定本文への昇格はしません。</strong></p>
    </article>
  );
}
