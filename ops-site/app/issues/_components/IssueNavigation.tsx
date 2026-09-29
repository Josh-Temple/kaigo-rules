const issues = [
  { number: "01", title: "情報探索", href: "/issues/information-search" },
  { number: "02", title: "記録・文書", href: "/issues/documentation" },
  { number: "03", title: "教育・引き継ぎ", href: "/issues/training-handover" },
  { number: "04", title: "問い合わせ・連携", href: "/issues/communication-collaboration" },
];

export default function IssueNavigation({ current }: { current: string }) {
  return (
    <nav className="issueNav" aria-label="公開Issue">
      {issues.map((issue) => (
        <a
          key={issue.href}
          href={issue.href}
          className={issue.href === current ? "issueNavItem isCurrent" : "issueNavItem"}
          aria-current={issue.href === current ? "page" : undefined}
        >
          <span>{issue.number}</span>
          <strong>{issue.title}</strong>
        </a>
      ))}
    </nav>
  );
}
