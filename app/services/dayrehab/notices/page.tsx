import Link from "next/link";
import VerificationSummary from "../../../../components/verification-summary";
import data from "../../../../data/services/dayrehab/rouki25-historical.generated.json";

const notice = data as any;

export default function DayrehabNoticesPage() {
  const groups = [...new Set(notice.items.map((item: any) => `${item.group_number} ${item.group_heading}`))];

  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY REHABILITATION / INTERPRETATION NOTICE</p>
      <h1>通所リハビリテーションの基準解釈通知</h1>
      <p className="lead">
        老企第25号の公式旧HTML「第九 通所リハビリテーション」を、9つのprincipal itemに分けて参照できます。
      </p>

      <div className="notice">
        <strong>これは現行統合本文ではありません。</strong><br />
        公式旧HTMLとの本文一致は独立照合済みですが、令和6年度新旧対照の「略」「新設」「削る」を旧HTMLへ機械適用していません。
        現行性はGAPとして管理し、人手確認も未実施です。
      </div>

      <VerificationSummary layerId="rouki25-dayrehab" />

      <section className="rules-stats" aria-label="解釈通知の公開状態">
        <div><strong>{notice.item_count}</strong><span>旧HTML principal item</span></div>
        <div><strong>{notice.item_count}</strong><span>公式source一致</span></div>
        <div><strong>GAP</strong><span>現行統合本文</span></div>
        <div><strong>0</strong><span>人手確認済み</span></div>
      </section>

      {groups.map((group: any) => {
        const items = notice.items.filter((item: any) => `${item.group_number} ${item.group_heading}` === group);
        return (
          <section className="section" key={group}>
            <h2>{group}</h2>
            {items.map((item: any) => (
              <section className="rule-node" id={item.id} key={item.id}>
                <p className="rule-node-label">{item.marker} {item.title}</p>
                {String(item.body_text).split("\n").map((line: string, index: number) => (
                  <p key={index}>{line}</p>
                ))}
                <p className="meta">{item.source_locator}</p>
                <p className="meta">本文SHA-256: <span className="hash">{item.body_sha256}</span></p>
              </section>
            ))}
          </section>
        );
      })}

      <section className="section">
        <h2>現行省令との関係</h2>
        <p>
          旧HTMLの準用説明は、現在の省令第119条の適用関係を決める正本としては使いません。
          現行の準用先はlive e-Govの第119条から別laneで抽出・検証しています。
        </p>
        <p><Link href="/services/dayrehab/rules/119">現行の第119条と準用関係を見る</Link></p>
      </section>

      <section className="section">
        <h2>出典・改正証拠</h2>
        <p><a href={notice.source.url} target="_blank" rel="noreferrer">厚生労働省の公式旧HTMLを確認</a></p>
        <p><a href={notice.amendment_evidence.source_url} target="_blank" rel="noreferrer">令和6年度新旧対照表を確認</a></p>
        <p className="meta">{notice.amendment_evidence.policy}</p>
      </section>

      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
