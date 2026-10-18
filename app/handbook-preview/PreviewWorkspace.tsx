"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "./preview-workspace.module.css";

export type PreviewCandidate = {
  bridgeId: string;
  text: string;
  evidenceTaskId: string;
  sourceIdentifiers: string[];
  officialUrl: string | null;
};
export type PreviewChapter = {
  sectionId: string;
  title: string;
  candidates: PreviewCandidate[];
};
export type PreviewService = {
  serviceId: "dayservice" | "dayrehab";
  title: string;
  chapters: PreviewChapter[];
};

type ProgressStatus = "not_started" | "referenced" | "recheck";
type SectionRecord = { status: ProgressStatus; note: string };
type Records = Record<string, SectionRecord>;

const STORAGE_KEY = "kaigo-handbook-preview-personal-notes-v1";
const STATUSES: ProgressStatus[] = ["not_started", "referenced", "recheck"];
const STATUS_TEXT: Record<ProgressStatus, string> = {
  not_started: "未着手",
  referenced: "参照した",
  recheck: "要再確認",
};

function isRecord(value: unknown): value is SectionRecord {
  if (!value || typeof value !== "object") return false;
  const x = value as Partial<SectionRecord>;
  return STATUSES.includes(x.status as ProgressStatus) && typeof x.note === "string";
}

function loadRecords(): Records {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (raw === null) return {};
  const parsed: unknown = JSON.parse(raw);
  if (!parsed || typeof parsed !== "object") throw new Error("保存データの形式が不明です");
  const data = parsed as { version?: unknown; sections?: unknown; review_completed?: unknown };
  if (data.version !== 1 || data.review_completed !== false || !data.sections ||
      typeof data.sections !== "object" || Array.isArray(data.sections)) {
    throw new Error("保存データの版または形式が一致しません");
  }
  const restored: Records = {};
  for (const [key, value] of Object.entries(data.sections)) {
    if (!isRecord(value)) throw new Error("保存データに不正な記録があります");
    restored[key] = value;
  }
  return restored;
}

export default function PreviewWorkspace({ services }: { services: PreviewService[] }) {
  const [serviceId, setServiceId] = useState<PreviewService["serviceId"]>("dayservice");
  const [sectionId, setSectionId] = useState("all");
  const [query, setQuery] = useState("");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [records, setRecords] = useState<Records>({});
  const [loaded, setLoaded] = useState(false);
  const [canPersist, setCanPersist] = useState(true);
  const [storageError, setStorageError] = useState("");
  const [downloadError, setDownloadError] = useState("");
  const [exportFallback, setExportFallback] = useState("");

  useEffect(() => {
    try {
      setRecords(loadRecords());
    } catch {
      // Never overwrite unreadable storage with an empty snapshot.
      setCanPersist(false);
      setStorageError("保存済みの閲覧記録を読めません。上書きを防ぐため自動保存を停止しました。");
    } finally {
      setLoaded(true);
    }
  }, []);

  useEffect(() => {
    if (!loaded || !canPersist) return;
    try {
      window.localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ version: 1, review_completed: false, sections: records })
      );
      setStorageError("");
    } catch {
      // Keep full, untruncated edits in React state; allow manual JSON export.
      setStorageError("ブラウザ内保存に失敗しました。入力内容はこの画面に保持しています。JSONを書き出してください。");
    }
  }, [records, loaded, canPersist]);

  const service = services.find((item) => item.serviceId === serviceId) ?? services[0];
  const normalized = query.trim().toLocaleLowerCase("ja-JP");
  const chapters = useMemo(() => (service?.chapters ?? []).filter((chapter) => {
    if (sectionId !== "all" && chapter.sectionId !== sectionId) return false;
    if (!normalized) return true;
    return (
      chapter.title.toLocaleLowerCase("ja-JP").includes(normalized) ||
      chapter.sectionId.toLocaleLowerCase("ja-JP").includes(normalized) ||
      chapter.candidates.some((candidate) =>
        [candidate.bridgeId, candidate.evidenceTaskId, candidate.text, ...candidate.sourceIdentifiers]
          .some((value) => value.toLocaleLowerCase("ja-JP").includes(normalized))
      )
    );
  }), [service, sectionId, normalized]);

  const update = (key: string, change: Partial<SectionRecord>) => {
    setRecords((prev) => ({
      ...prev,
      [key]: { status: prev[key]?.status ?? "not_started", note: prev[key]?.note ?? "", ...change },
    }));
  };

  const exportData = () => {
    // No HTTP POST, analytics, background upload, or server storage.
    const data = {
      schema: "KAIGO_PREVIEW_PERSONAL_RECORDS_V1",
      exported_at: new Date().toISOString(),
      review_completed: false,
      disclaimer: "閲覧記録であり、法令現行性・人手レビュー・公開可否を承認するものではありません。",
      sections: records,
    };
    const json = JSON.stringify(data, null, 2);
    try {
      const blob = new Blob([json], { type: "application/json;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      try {
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = "kaigo-handbook-preview-notes.json";
        document.body.appendChild(anchor);
        try { anchor.click(); } finally { anchor.remove(); }
      } finally {
        // Defer cleanup until after the browser processes the click.
        window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      }
      setExportFallback("");
      setDownloadError("");
    } catch {
      setExportFallback(json); // Entire payload, without truncation.
      setDownloadError("ファイルの書出しに失敗しました。下のJSON全文をコピーして保存してください。");
    }
  };

  if (!service) return <p role="alert">利用可能な試用データがありません。</p>;

  return (
    <main className={styles.page}>
      <p className={styles.warning}>LIMITED PREVIEW / DRAFT_UNREVIEWED / NOT_ESTABLISHED</p>
      <h1>通所系サービス手引 — 読む・絞る・記録する</h1>
      <p className={styles.lead}>
        15章構成の暫定草稿を調べるための保護付き試用画面です。
        掲載内容は未レビューであり、現行法令・指定権者の条例・適用・算定可否を確定しません。
        実務判断前に必ず公式原典と改正・施行情報を再確認してください。
      </p>
      <p><strong>人手レビュー済み0件／公開判定 HOLD_NO_GO／現行性 NOT_ESTABLISHED</strong></p>

      <div className={styles.controls}>
        <fieldset className={styles.switcher}>
          <legend>対象サービス</legend>
          {services.map((option) => (
            <button
              type="button"
              key={option.serviceId}
              className={option.serviceId === serviceId ? styles.active : styles.button}
              aria-pressed={option.serviceId === serviceId}
              onClick={() => { setServiceId(option.serviceId); setSectionId("all"); setQuery(""); }}
            >
              {option.title}
            </button>
          ))}
        </fieldset>
        <div className={styles.fields}>
          <label>章へ移動
            <select value={sectionId} onChange={(event) => setSectionId(event.target.value)}>
              <option value="all">すべての章（15章）</option>
              {service.chapters.map((chapter, index) => (
                <option value={chapter.sectionId} key={chapter.sectionId}>
                  第{index + 1}章 {chapter.title}
                </option>
              ))}
            </select>
          </label>
          <label>章名・候補ID・本文・照合記録を検索
            <input
              type="search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="例：人員、KR-BRIDGE、記録"
            />
          </label>
        </div>
      </div>
      <p role="status" aria-live="polite">
        {service.title}：{chapters.length}章を表示／全15章、未レビュー候補{
          chapters.reduce((sum, chapter) => sum + chapter.candidates.length, 0)
        }件
      </p>
      {chapters.length === 0 && (
        <p className={styles.empty}>条件に一致する章はありません。検索語または章の選択を変更してください。</p>
      )}
      <div className={styles.actions}>
        <button type="button" onClick={() => setExpanded((prev) => ({
          ...prev, ...Object.fromEntries(chapters.map((c) => [serviceId + ":" + c.sectionId, true])),
        }))}>表示中の章をすべて開く</button>
        <button type="button" onClick={() => setExpanded((prev) => ({
          ...prev, ...Object.fromEntries(chapters.map((c) => [serviceId + ":" + c.sectionId, false])),
        }))}>表示中の章をすべて閉じる</button>
      </div>

      {chapters.map((chapter) => {
        const index = service.chapters.findIndex((item) => item.sectionId === chapter.sectionId);
        const key = serviceId + ":" + chapter.sectionId;
        const record = records[key] ?? { status: "not_started" as const, note: "" };
        const isExpanded = expanded[key] ?? Boolean(normalized || sectionId !== "all" || index === 0);
        return (
          <section className={styles.chapter} key={key} id={key}>
            <h2>
              <button
                type="button"
                className={styles.chapterToggle}
                aria-expanded={isExpanded}
                aria-controls={"body-" + key}
                onClick={() => setExpanded((prev) => ({ ...prev, [key]: !isExpanded }))}
              >
                <span>第{index + 1}章 {chapter.title}</span>
                <span>{chapter.candidates.length}候補 {isExpanded ? "▲" : "▼"}</span>
              </button>
            </h2>
            {isExpanded && (
              <div id={"body-" + key} className={styles.chapterBody}>
                <p>確認ポイント：この章に整理された出典候補の所在・改正履歴・当該サービスへの適用を原典で照合する。</p>
                <p><strong>未確立：</strong>法令の現行性、具体的な適用判断、人手レビュー。章割当も暫定です。</p>
                {chapter.candidates.length === 0 ? (
                  <p className={styles.empty}>この章に追加の未レビュー候補はありません。法的根拠が存在しないという意味ではありません。</p>
                ) : chapter.candidates.map((candidate) => (
                  <section className={styles.candidate} key={candidate.bridgeId}>
                    <h3>確認候補 {candidate.bridgeId} <span className={styles.draft}>未レビュー</span></h3>
                    <p>{candidate.text}</p>
                    <p className={styles.meta}>照合記録：{candidate.evidenceTaskId}</p>
                    <p className={styles.meta}>出典候補ID：{candidate.sourceIdentifiers.join("、") || "未特定"}</p>
                    {candidate.officialUrl ? (
                      <a href={candidate.officialUrl} target="_blank" rel="noopener noreferrer">
                        厚生労働省・e-Govの掲載先を開く ↗
                      </a>
                    ) : (
                      <p className={styles.meta}>公式原典への直接リンク未確認。下の公開資料検索から照合してください。</p>
                    )}
                    <p className={styles.meta}>DRAFT_UNREVIEWED / NOT_ESTABLISHED（公開・法令承認なし）</p>
                  </section>
                ))}
                <p><a href={`/databases/search?service=${serviceId}`}>公開中の資料検索へ →</a></p>
                <div className={styles.notes}>
                  <label>個人用閲覧記録
                    <select
                      value={record.status}
                      onChange={(event) => update(key, { status: event.target.value as ProgressStatus })}
                    >
                      {STATUSES.map((status) => <option key={status} value={status}>{STATUS_TEXT[status]}</option>)}
                    </select>
                  </label>
                  <label>章別メモ（ブラウザ内のみ・個人情報や事業所情報を入力しない）
                    <textarea
                      rows={3}
                      value={record.note}
                      onChange={(event) => update(key, { note: event.target.value })}
                      placeholder="確認したい原典や後で見直す点など（機微情報は記入しない）"
                    />
                  </label>
                  <p className={styles.meta}>この記録は法令の人手レビュー承認ではありません。</p>
                </div>
              </div>
            )}
          </section>
        );
      })}

      <section className={styles.exportPanel} aria-label="閲覧記録を書き出す">
        <h2>閲覧記録の保存と書出し</h2>
        <p>記録とメモはこのブラウザのlocalStorageだけに保存します。サーバー送信はしません。共有端末では利用を避けてください。</p>
        <p>書出しJSONには必ず <code>review_completed: false</code> を入れます。手引本文の確定・公開承認には使用できません。</p>
        {!loaded && <p role="status">ブラウザ保存領域の確認中です。</p>}
        {storageError && <p role="alert" className={styles.error}>{storageError}</p>}
        <button type="button" onClick={exportData}>閲覧記録・メモをJSONで書き出す</button>
        {downloadError && <p role="alert" className={styles.error}>{downloadError}</p>}
        {exportFallback && (
          <label>書出し用JSON全文（コピーして保存）
            <textarea readOnly rows={10} value={exportFallback} />
          </label>
        )}
      </section>
    </main>
  );
}
