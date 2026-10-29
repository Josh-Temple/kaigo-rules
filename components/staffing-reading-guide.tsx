import { staffingReadingGuides } from "../lib/handbook/staffing-reading-guide";

export default function StaffingReadingGuide({ serviceId }: { serviceId: string }) {
  const guide = staffingReadingGuides[serviceId];
  if (!guide) return null;
  return <aside className="staffing-reading-guide" aria-label="人員基準の読み方">
    <p className="staffing-guide-lead">{guide.lead}</p>
    <details>
      <summary>確認する順序と、手元に用意する書類</summary>
      <ol>{guide.checks.map(([title, text]) => <li key={title}><strong>{title}</strong><p>{text}</p></li>)}</ol>
      <p className="meta">書類は確認のための例です。新たな法令上の義務や、法令への適合判定を示すものではありません。</p>
    </details>
  </aside>;
}
