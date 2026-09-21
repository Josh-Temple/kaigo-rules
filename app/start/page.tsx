import sources from "../../data/sources.json";
import steps from "../../data/startup-steps.json";

export default function StartPage() {
  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">START A DAY SERVICE</p>
      <h1>通所介護を始めたい。<br />何から手を付ける？</h1>
      <p className="lead">開設相談で最初につまずきやすい順番を、全国共通の制度から整理します。申請先や事前相談の運用は自治体によって異なるため、最終的には予定地の指定権者を確認してください。</p>
      <div className="notice">物件契約や大きな改修、人材採用を確定する前に、サービス区分・設備基準・指定権者を確認する方が手戻りを減らせます。</div>
      <div className="step-list">
        {steps.map((step) => (
          <section className="step" key={step.id}>
            <span className="step-number">{String(step.order).padStart(2, "0")}</span>
            <div><h2>{step.title}</h2><p>{step.summary}</p>{step.source_ids.map((sourceId) => { const source = sources.find((s) => s.id === sourceId); return source ? <a key={sourceId} href={source.url} target="_blank" rel="noreferrer">公式資料を確認</a> : null; })}</div>
          </section>
        ))}
      </div>
      <section className="section"><h2>このページで今後追加するもの</h2><p>指定権者を選ぶと必要書類や自治体ページへ進める導線、開設前チェックリスト、「物件」「人員」「書類」「報酬」の詳細ガイドを順次追加します。</p></section>
    </article>
  );
}
