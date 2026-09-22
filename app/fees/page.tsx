import nodesData from "../../data/remuneration-current-skeleton.json";
import metaData from "../../data/remuneration-current-meta.json";
import chainData from "../../data/remuneration-source-chain.json";
import sourcesData from "../../data/sources.json";

const nodes = nodesData as Array<any>;
const meta = metaData as any;
const chain = chainData as Array<any>;
const sources = sourcesData as Array<any>;

const labels: Record<string,string> = {
  CURRENT_STRUCTURE_NEEDS_HUMAN_CHECK:"現行構造・人手確認待ち",
  CURRENT_AFTER_TEXT_NEEDS_HUMAN_CHECK:"令和8年改正後文・人手確認待ち",
  OUT_OF_CORE_SCOPE:"コア範囲外",
  VERIFIED_CURRENT:"現行確認済み",
  UNKNOWN:"未確認"
};

export default function FeesPage() {
  const root=nodes.find(n=>n.id==="fee.dayservice.root");
  const children=nodes.filter(n=>n.parent_id===root?.id);
  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">REMUNERATION DATABASE</p>
      <h1>通所介護の報酬DB</h1>
      <p className="lead">
        介護報酬は、基準省令とは別に、報酬告示・算定方法告示・留意事項通知を分けて構造化します。
        現在は厚生労働省の現行統合HTMLを基礎に、通所介護費の骨格を構造化している段階です。
      </p>
      <div className="notice">
        <strong>単位数を「現行確定」として表示する段階ではありません。</strong><br/>
        厚生労働省の現行HTMLには令和8年告示第87号まで反映されていますが、各ノードの機械抽出と人手照合が終わるまでは確認済み表示にしません。
      </div>
      <section className="rules-stats">
        <div><strong>{meta.counts.nodes}</strong><span>骨格ノード</span></div>
        <div><strong>{meta.counts.base_rate_groups}</strong><span>基本報酬区分</span></div>
        <div><strong>{meta.counts.notes}</strong><span>注・加算減算</span></div>
        <div><strong>{meta.counts.out_of_core_scope}</strong><span>コア範囲外</span></div>
      </section>
      <section className="section">
        <h2>資料チェーン</h2>
        <div className="source-chain">
          {chain.map(entry=>{
            const source=sources.find(s=>s.id===entry.source_id);
            return <div className="source-chain-row" key={entry.source_id}>
              <span className="meta">{source?.layer || entry.source_class}</span>
              <div><strong>{source?.title || entry.source_id}</strong><p>{entry.use}</p>{entry.warning?<p className="meta">注意：{entry.warning}</p>:null}</div>
            </div>;
          })}
        </div>
      </section>
      <section className="section">
        <h2>通所介護費の骨格</h2>
        <div className="fee-list">
          {children.map(node=><section className="fee-row" key={node.id}>
            <div>
              <p className="meta">{node.number_path.join(" / ")}</p>
              <h3>{node.title}</h3>
            </div>
            <span className={node.verification_status==="OUT_OF_CORE_SCOPE"?"fee-status fee-out":"fee-status"}>
              {labels[node.verification_status] || node.verification_status}
            </span>
          </section>)}
        </div>
      </section>
      <section className="section">
        <h2>スコープ上の扱い</h2>
        <p>
          注7「共生型通所介護の減算」と、それを前提とする注8「生活相談員配置等加算」は、
          指定通所介護本体と混同しないよう「コア範囲外」として保持しています。
        </p>
      </section>
    </article>
  );
}
