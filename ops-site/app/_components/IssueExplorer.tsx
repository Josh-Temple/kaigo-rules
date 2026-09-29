"use client";

import { useMemo, useState } from "react";
import {
  issueGroups,
  issueRegistry,
  searchableIssueText,
  type IssueGroup,
} from "../issues/registry";

type GroupFilter = "すべて" | IssueGroup;

export default function IssueExplorer() {
  const [query, setQuery] = useState("");
  const [group, setGroup] = useState<GroupFilter>("すべて");

  const filteredIssues = useMemo(() => {
    const normalized = query.trim().toLocaleLowerCase("ja");

    return issueRegistry.filter((issue) => {
      const groupMatch = group === "すべて" || issue.group === group;
      const queryMatch =
        normalized.length === 0 || searchableIssueText(issue).includes(normalized);

      return groupMatch && queryMatch;
    });
  }, [group, query]);

  return (
    <div className="issueExplorer">
      <div className="issueTools">
        <label className="issueSearch">
          <span>困りごとを検索</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例: 転記、研修、FAX、稼働率"
          />
        </label>

        <div className="issueFilters" aria-label="Issue分類">
          {(["すべて", ...issueGroups] as GroupFilter[]).map((item) => (
            <button
              key={item}
              type="button"
              className={group === item ? "issueFilter isActive" : "issueFilter"}
              onClick={() => setGroup(item)}
              aria-pressed={group === item}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      <p className="issueResultCount" aria-live="polite">
        {filteredIssues.length} / {issueRegistry.length} Issue
      </p>

      <div className="issueList">
        {filteredIssues.map((issue) => (
          <article className="issueRow" key={issue.href}>
            <span className="issueNumber">{issue.number}</span>
            <div>
              <p className="issueGroup">{issue.group}</p>
              <h3>{issue.title}</h3>
              <p>{issue.body}</p>
            </div>
            <div className="issueAction">
              <span className="status">{issue.status}</span>
              <a className="issueOpen" href={issue.href}>
                読む →
              </a>
            </div>
          </article>
        ))}
      </div>

      {filteredIssues.length === 0 ? (
        <p className="issueEmpty">
          該当するIssueはありません。検索語を短くするか、「すべて」に戻してください。
        </p>
      ) : null}
    </div>
  );
}
