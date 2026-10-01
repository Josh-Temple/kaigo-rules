import Link from "next/link";
import VerificationSummary from "../../../../components/verification-summary";
import data from "../../../../data/services/dayrehab/remuneration-index.json";

const layer = data as any;

export default function DayrehabRemunerationPage() {
  const tariffRows = layer.items.filter((item: any) => item.kind === "BASE_TARIFF_ROW");
  const notes = layer.items.filter((item: any) => item.kind === "NUMBERED_NOTE");
  const addOns = layer.items.filter((item: any) => item.kind === "LETTERED_ADD_ON");

  return (
    <article className="answer-page foundation-page">
      <p className="eyebrow">DAY REHABILITATION / REMUNERATION STANDARD</p>
      <h1>通所リハビリテーションの報酬基準</h1>
      <p className="lead">
        告示第19号の掲載表示を42項目に分け、要介護度別の基本単位数70値を出典別に参照できます。
      </p>

      <div className="notice">
        <strong>これは現行統合本文ではありません。</strong><br />
        基本単位数は厚生労働省掲載表示の取得範囲、令和8年告示第87号は明示されたヘの差分として分離しています。
        令和8年対照表でイ〜ホが「略」とされているため、変更なしとは扱っていません。
        現行性はGAP、人手確認は未実施です。
      </div>

      <VerificationSummary layerId="remuneration-dayrehab" />

      <section className="rules-stats" aria-label="通所リハ報酬基準の公開状態">
        <div><strong>{layer.counts.parent_items}</strong><span>出典側の親項目</span></div>
        <div><strong>{layer.counts.base_tariff_rows}</strong><span>基本報酬区分</span></div>
        <div><strong>{layer.counts.base_tariff_rate_values}</strong><span>要介護度別の掲載単位値</span></div>
        <div><strong>GAP</strong><span>現行性</span></div>
      </section>

      <section className="section">
        <h2>厚生労働省掲載表示の基本報酬</h2>
        <p className="meta">取得時表示の版をそのまま区分した値です。現行性は未確認で、令和8年告示第87号とは合成していません。</p>
        {tariffRows.map((item: any) => (
          <section className="rule-node" key={item.id}>
            <p className="rule-node-label">{item.marker} {item.group_title}・{item.duration}</p>
            <p>単位/回：{item.rates.map((rate: any) => "要介護" + rate.care_level + " " + Number(rate.units).toLocaleString("ja-JP")).join(" / ")}</p>
            <p className="meta">{item.source_locator}</p>
          </section>
        ))}
      </section>

      <section className="section">
        <h2>注1〜24・追加項目ハ〜ヘ</h2>
        <p className="meta">以下はCycle 3抽出要約で、告示の全文引用ではありません。基準本文と届出・関連要件は厚生労働省の出典を確認してください。</p>
        {[...notes, ...addOns].map((item: any) => (
          <section className="rule-node" key={item.id}>
            <p className="rule-node-label">{item.marker} {item.title}</p>
            {item.summary ? <p>{item.summary}</p> : null}
            {item.base_rate_slots ? <p>{item.base_rate_slots.map((rate: any) => rate.label + " " + rate.units + " " + rate.unit).join(" / ")}</p> : null}
            <p className="meta">{item.source_locator}</p>
          </section>
        ))}
      </section>

      <section className="section">
        <h2>令和8年告示第87号の独立差分</h2>
        <p>{layer.amendment_patches[0].policy}</p>
        <p className="meta">施行日：令和8年6月1日。単位数の算定基礎はイ〜ホ。ここにある率を掲載表示の基本報酬へ自動適用した表は作っていません。</p>
        <div className="rules-list">
          {layer.amendment_patches[0].rates.map((rate: any) => (
            <div className="rule-row" key={rate.label}>
              <span className="rule-number">{rate.label}</span>
              <span className="rule-title">{rate.per_thousand}/1000</span>
              <span className="rule-status">告示87号のヘ差分</span>
            </div>
          ))}
        </div>
        <p>旧注2（Ⅴ）は削除表示です。イ〜ホの「略」から当該区分の変更有無は判断できません。</p>
      </section>

      <section className="section">
        <h2>出典と版</h2>
        {layer.canonical_sources.map((source: any) => (
          <section className="rule-node" key={source.id}>
            <p className="rule-node-label">{source.title}</p>
            <p>{source.role} / {source.locator}</p>
            <p className="meta">{source.version_note}</p>
            <p><a href={source.url} target="_blank" rel="noreferrer">厚生労働省の原資料を開く</a></p>
          </section>
        ))}
      </section>

      <p><Link href="/services/dayrehab/remuneration/guidance">算定上の留意事項を見る</Link></p>
      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
