"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import questions from "../data/questions.json";

export default function QuestionSearch({ initialLimit }: { initialLimit?: number }) {
  const [query, setQuery] = useState("");
  const normalized = query.trim().toLowerCase();
  const results = useMemo(() => {
    const matched = normalized
      ? questions.filter((q) =>
          [q.title, q.category, ...q.aliases].join(" ").toLowerCase().includes(normalized)
        )
      : questions;
    return !normalized && initialLimit ? matched.slice(0, initialLimit) : matched;
  }, [initialLimit, normalized]);

  return (
    <>
      <form className="search" action="/search" method="get">
        <div className="home-search-row">
          <input
            name="q"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="例：計画書にハンコは必要？"
            aria-label="通所介護を検索"
          />
          <button type="submit">横断検索</button>
        </div>
        <small>
          入力中は厳選した実務ページを絞り込みます。横断検索では基準省令・報酬・国Q&Aも検索します。
        </small>
      </form>
      <div className="question-list">
        {results.length ? results.map((q) => (
          <article className="question" key={q.slug}>
            <span className="meta">{q.category}</span>
            <Link href={"/questions/" + q.slug}>{q.title}</Link>
            <span className={q.status === "verified" ? "status verified" : "status"}>
              {q.status === "verified" ? "確認済み" : "根拠確認中"}
            </span>
          </article>
        )) : (
          <p className="notice">
            確認済みの候補ページにはありません。横断検索で基準省令・報酬・国Q&Aを探せます。
          </p>
        )}
      </div>
    </>
  );
}
