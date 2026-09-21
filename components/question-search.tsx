"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import questions from "../data/questions.json";

export default function QuestionSearch() {
  const [query, setQuery] = useState("");
  const normalized = query.trim().toLowerCase();
  const results = useMemo(() => {
    if (!normalized) return questions;
    return questions.filter((q) =>
      [q.title, q.category, ...q.aliases].join(" ").toLowerCase().includes(normalized)
    );
  }, [normalized]);

  return (
    <>
      <div className="search">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="例：計画書にハンコは必要？"
          aria-label="通所介護の質問を検索"
        />
        <small>通常検索のみ。AIによる回答生成は行いません。</small>
      </div>
      <div className="question-list">
        {results.length ? results.map((q) => (
          <article className="question" key={q.slug}>
            <span className="meta">{q.category}</span>
            <Link href={"/questions/" + q.slug}>{q.title}</Link>
            <span className="status">根拠確認中</span>
          </article>
        )) : (
          <p className="notice">確認済みの候補ページがありません。AIが推測して回答することはありません。</p>
        )}
      </div>
    </>
  );
}
