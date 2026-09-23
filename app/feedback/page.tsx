"use client";

import type { FormEvent } from "react";
import { useEffect, useState } from "react";

const categories = [
  "情報が古い・誤っている",
  "根拠資料やリンクに問題がある",
  "説明が分かりにくい",
  "必要な情報が見つからない",
  "その他",
];

export default function FeedbackPage() {
  const [sourcePath, setSourcePath] = useState("/");
  const [category, setCategory] = useState(categories[0]);
  const [details, setDetails] = useState("");

  useEffect(() => {
    const from = new URLSearchParams(window.location.search).get("from");
    if (from?.startsWith("/")) setSourcePath(from);
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const pageUrl = window.location.origin + sourcePath;
    const body = [
      "## 種別",
      category,
      "",
      "## 対象ページ",
      pageUrl,
      "",
      "## 内容",
      details.trim(),
      "",
      "## 補足",
      "必要に応じて、根拠となる公式資料のURLや確認した日付を追記してください。",
    ].join("\n");

    const title = "[サイトフィードバック] " + category;
    const issueUrl =
      "https://github.com/Josh-Temple/kaigo-rules/issues/new?title=" +
      encodeURIComponent(title) +
      "&body=" +
      encodeURIComponent(body);

    window.location.assign(issueUrl);
  }

  return (
    <section className="answer-page feedback-page">
      <p className="eyebrow">フィードバック</p>
      <h1>内容の誤りや使いにくさを教えてください</h1>
      <p className="lead">
        いただいた内容は調査のきっかけとして扱い、制度情報へ自動反映はしません。
        必要に応じて厚生労働省・e-Gov・自治体等の一次資料で確認してから修正します。
      </p>

      <form className="feedback-form" onSubmit={handleSubmit}>
        <label>
          <span>対象ページ</span>
          <input value={sourcePath} readOnly aria-label="対象ページ" />
        </label>

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
            onChange={(event) => setDetails(event.target.value)}
            rows={8}
            required
            placeholder="例：この説明は令和6年度改正後の取扱いと違うように見えます。確認した公式資料は……"
          />
        </label>

        <button type="submit">GitHubで報告を続ける</button>
      </form>

      <p className="feedback-note">
        次の画面でGitHub Issueを作成します。GitHubへのサインインが必要です。
        投稿内容は公開されるため、氏名、利用者情報、事業所の非公開情報などは入力しないでください。
      </p>
    </section>
  );
}
