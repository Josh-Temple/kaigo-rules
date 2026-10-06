"use client";

import type { FormEvent } from "react";
import { useEffect, useState } from "react";

const categories = [
  "誤り",
  "古い",
  "見つからない",
  "分かりにくい",
  "リンク・出典",
  "その他",
];

const safeParam = (params: URLSearchParams, name: string, max: number) =>
  (params.get(name) || "").trim().slice(0, max);

export default function FeedbackPage() {
  const [sourcePath, setSourcePath] = useState("/");
  const [service, setService] = useState("");
  const [database, setDatabase] = useState("");
  const [sourceFamily, setSourceFamily] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [category, setCategory] = useState(categories[0]);
  const [details, setDetails] = useState("");
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const from = safeParam(params, "from", 500);
    if (from.startsWith("/")) setSourcePath(from);
    setService(safeParam(params, "service", 120));
    setDatabase(safeParam(params, "db", 120));
    setSourceFamily(safeParam(params, "source_family", 120));
    setSearchQuery(safeParam(params, "q", 200));
  }, []);

  function buildPayload() {
    const pageUrl = window.location.origin + sourcePath;
    const context = [
      service ? "- サービス: " + service : "",
      database ? "- DB: " + database : "",
      sourceFamily ? "- 資料群: " + sourceFamily : "",
      searchQuery.trim() ? "- 検索語: " + searchQuery.trim() : "",
    ].filter(Boolean);

    return [
      "## 種別",
      category,
      "",
      "## 対象ページ",
      pageUrl,
      ...(context.length ? ["", "## 画面の文脈", ...context] : []),
      "",
      "## 内容",
      details.trim(),
      "",
      "## 補足",
      "必要に応じて、根拠となる公式資料のURLや確認した日付を追記してください。",
    ].join("\n");
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const title = "[サイトフィードバック] " + category;
    const issueUrl =
      "https://github.com/Josh-Temple/kaigo-rules/issues/new?title=" +
      encodeURIComponent(title) +
      "&body=" +
      encodeURIComponent(buildPayload());

    window.location.assign(issueUrl);
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(buildPayload());
    setCopied(true);
  }

  const hasContext = Boolean(service || database || sourceFamily || searchQuery);

  return (
    <section className="answer-page feedback-page">
      <p className="eyebrow">フィードバック</p>
      <h1>誤り・更新漏れ・見つけにくさを教えてください</h1>
      <p className="lead">
        対象ページと、検索時に選んでいたサービス・DBなどの文脈を引き継ぎます。
        いただいた内容をそのまま制度情報へ反映せず、必要に応じて厚生労働省・e-Gov・自治体等の一次資料を確認してから修正します。
      </p>

      <form className="feedback-form" onSubmit={handleSubmit}>
        <label>
          <span>対象ページ</span>
          <input value={sourcePath} readOnly aria-label="対象ページ" />
        </label>

        {hasContext ? (
          <fieldset>
            <legend>引き継いだ文脈</legend>
            {service ? (
              <label>
                <span>サービス</span>
                <input value={service} readOnly aria-label="サービス" />
              </label>
            ) : null}
            {database ? (
              <label>
                <span>DB</span>
                <input value={database} readOnly aria-label="DB" />
              </label>
            ) : null}
            {sourceFamily ? (
              <label>
                <span>資料群</span>
                <input value={sourceFamily} readOnly aria-label="資料群" />
              </label>
            ) : null}
            {searchQuery ? (
              <label>
                <span>検索語</span>
                <input
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value.slice(0, 200))}
                  aria-label="検索語"
                />
                <small>
                  GitHubで報告すると公開されます。個人情報や非公開情報が含まれる場合は削除してください。
                </small>
              </label>
            ) : null}
          </fieldset>
        ) : null}

        <label>
          <span>種類</span>
          <select value={category} onChange={(event) => setCategory(event.target.value)}>
            {categories.map((item) => (
              <option key={item} value={item}>{item}</option>
            ))}
          </select>
        </label>

        <label>
          <span>内容</span>
          <textarea
            value={details}
            onChange={(event) => {
              setDetails(event.target.value);
              setCopied(false);
            }}
            rows={8}
            required
            placeholder="例：この説明は改正後の取扱いと違うように見えます。確認した公式資料は……"
          />
        </label>

        <button type="submit">GitHubで報告する</button>
        <button type="button" onClick={handleCopy}>内容をコピー</button>
        {copied ? <p className="meta">コピーしました。</p> : null}
      </form>

      <p className="feedback-note">
        GitHubで報告する場合はサインインが必要で、投稿内容は公開されます。
        GitHubを使わない場合は「内容をコピー」で手元に残せます。
        氏名、利用者情報、事業所の非公開情報、検索語に含まれる個人情報などは入力しないでください。
      </p>
    </section>
  );
}
