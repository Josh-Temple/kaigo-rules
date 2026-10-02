import { issueRegistry } from "../registry";

export default function IssueNavigation({ current }: { current: string }) {
  return (
    <nav className="issueNav" aria-label="公開中の困りごと">
      {issueRegistry.map((issue) => (
        <a
          key={issue.href}
          href={issue.href}
          className={issue.href === current ? "issueNavItem isCurrent" : "issueNavItem"}
          aria-current={issue.href === current ? "page" : undefined}
        >
          <span>{issue.number}</span>
          <strong>{issue.shortTitle}</strong>
        </a>
      ))}
    </nav>
  );
}
