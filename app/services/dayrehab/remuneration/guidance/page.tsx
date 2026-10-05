import Link from "next/link";
import VerificationSummary from "../../../../../components/verification-summary";
import ServiceContextLinks from "../../../../../components/service-context-links";
import data from "../../../../../data/services/dayrehab/fee-guidance-index.json";

const layer = data as any;
const sourceById = new Map<string, any>(layer.canonical_sources.map((source: any) => [source.id, source]));
const sourcePageHref = (item: any) => {
  const source = sourceById.get(item.source_id);
  const firstPage = item.source_locator.match(/^p\.(\d+)/)?.[1];
  return source && firstPage ? `${source.url}#page=${firstPage}` : null;
};
const sourceStateLabel: Record<string, string> = {
  OMITTED_MARKER: "本文省略", BODY_VISIBLE: "本文の記載あり",
  BODY_OR_CROSS_REFERENCE: "本文または他項目への参照あり",
  HEADING_AND_CROSS_REFERENCE: "見出しと他項目への参照あり",
  CROSS_REFERENCE: "他項目への参照あり", CROSS_REFERENCE_AND_READ_AS: "他項目への参照・読み替えあり",
  PARTIAL_WITH_LITERAL_OMISSIONS: "一部の本文を省略", PARTIAL_VISIBLE: "本文の一部を確認",
};

export default function DayrehabFeeGuidancePage() {
  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY REHABILITATION / FEE GUIDANCE</p>
      <h1>通所リハビリテーションの算定上の留意事項</h1>
      <p className="lead">
        老企第36号第二／8の令和6年度確定新旧対照表から、33の主項目と88の見える子項目を出典ローカルの番号で参照できます。
      </p>

      <ServiceContextLinks serviceId="dayrehab" />

      <div className="notice">
        <strong>これは現行統合本文ではありません。</strong><br />
        令和6年新旧対照表の「略」や旧版HTMLを継ぎ足して本文を作っていません。
        令和8年通知改正対照は第6〜9節を新旧両欄で省略しており、第8節の変更有無を示しません。
        現行性は確認中で、人手確認と二段組みの視覚確認は未実施です。
      </div>

      <VerificationSummary layerId="fee-guidance-dayrehab" />

      <section className="section">
        <h2>論点から原資料を確認する</h2>
        <p>このページは出典案内です。掲載番号から令和6年の改正資料へ進めます。省略された本文や参照先の要件、後続改正は別途確認が必要です。</p>
        <ul className="source-list">
          {layer.items.filter((item: any) => ["R6-8-03", "R6-8-04", "R6-8-12", "R6-8-13"].includes(item.id)).map((item: any) => (
            <li key={item.id}><Link href={`#${item.id}`}>{item.title}</Link></li>
          ))}
        </ul>
      </section>

      <section className="rules-stats" aria-label="算定留意事項の公開状態">
        <div><strong>{layer.counts.parent_items}</strong><span>令和6年主項目</span></div>
        <div><strong>{layer.counts.visible_child_items}</strong><span>明示された子項目</span></div>
        <div><strong>{layer.counts.parents_with_literal_omission}</strong><span>主項目の「略」</span></div>
        <div><strong>確認中</strong><span>現行性</span></div>
      </section>

      <section className="section">
        <h2>令和6年確定新旧対照表・第8節</h2>
        <p className="meta">以下は同資料の主項目・番号・収載状況です。本文・省略条項・他サービスへの参照を復元していません。</p>
        {layer.items.map((item: any) => (
          <section className="rule-node" id={item.id} key={item.id}>
            <p className="rule-node-label">{item.slot}</p>
            <h3>{item.title}</h3>
            <p>資料上の状態：{sourceStateLabel[item.r6_source_state] || "記載範囲は原資料を確認"}</p>
            <p className="meta">{item.source_locator}</p>
            {sourcePageHref(item) ? <p><a href={sourcePageHref(item)!} target="_blank" rel="noreferrer">令和6年改正資料の該当ページを開く</a></p> : null}
            <p className="meta">現行性は未確定です。省略箇所・参照先の本文と後続改正を確認してください。</p>
            {item.children.length > 0 ? (
              <details>
                <summary>確認できた子項目 {item.children.length} 件</summary>
                <div className="rule-tree">
                  {item.children.map((child: any) => (
                    <section className="rule-node" key={child.id}>
                      <p className="rule-node-label">{child.marker}</p>
                      <p className="meta">{child.locator}</p>
                    </section>
                  ))}
                </div>
              </details>
            ) : null}
          </section>
        ))}
      </section>

      <section className="section">
        <h2>版別の出典台帳</h2>
        {layer.canonical_sources.map((source: any) => (
          <section className="rule-node" key={source.id}>
            <p className="rule-node-label">{source.title}</p>
            <p>{source.role} / {source.locator}</p>
            <p className="meta">{source.version_note}</p>
            <p><a href={source.url} target="_blank" rel="noreferrer">厚生労働省の原資料を開く</a></p>
          </section>
        ))}
      </section>

      <p><Link href="/services/dayrehab/remuneration">報酬基準を見る</Link></p>
      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
