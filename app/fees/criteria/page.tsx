import VerificationSummary from "../../../components/verification-summary";
import nodesData from "../../../data/remuneration-delegated-nodes.json";
import relationsData from "../../../data/remuneration-delegated-relations.json";
import metaData from "../../../data/remuneration-delegated-meta.json";
import sourcesData from "../../../data/sources.json";

const nodes=nodesData as Array<any>;
const relations=relationsData as Array<any>;
const meta=metaData as any;
const sources=sourcesData as Array<any>;

export default function FeeCriteriaPage(){
  const grouped = [
    {
      title:"告示27号：利用者数・人員欠如等の算定方法",
      items:nodes.filter(n=>n.id.startsWith("calc27.")),
    },
    {
      title:"告示95号：厚生労働大臣が定める基準",
      items:nodes.filter(n=>n.id.startsWith("criteria95.")),
    }
  ];

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">DELEGATED REMUNERATION CRITERIA</p>
      <h1>通所介護の別告示DB</h1>
      <p className="lead">
        報酬告示19号から参照される算定方法告示・厚生労働大臣基準を、現行の厚生労働省HTMLから構造化します。
      </p>
      <div className="notice">
        <strong>機械取込済み・人手確認待ち</strong><br/>
        現行公式HTMLから直接抽出していますが、個々の区切り・参照関係は人手確認前です。
      </div>

      <VerificationSummary layerId="remuneration-notices" />
      <section className="rules-stats">
        <div><strong>{meta.counts?.nodes || nodes.length}</strong><span>ノード</span></div>
        <div><strong>{meta.counts?.notice27_nodes || 0}</strong><span>告示27号</span></div>
        <div><strong>{meta.counts?.notice95_nodes || 0}</strong><span>告示95号</span></div>
        <div><strong>{meta.counts?.relations || relations.length}</strong><span>対応関係</span></div>
      </section>

      {grouped.map(group=>(
        <section className="section" key={group.title}>
          <h2>{group.title}</h2>
          <div className="delegated-list">
            {group.items.map(item=>{
              const source=sources.find(s=>s.id===item.source_id);
              return <details className="delegated-node" id={item.id} key={item.id}>
                <summary>
                  <span>{item.heading}</span>
                  <small>取込済み・確認待ち</small>
                </summary>
                <div className="delegated-body">
                  <p className="fee-official-text">{item.official_text}</p>
                  {item.related_fee_ids?.length ? <p className="meta">対応候補：{item.related_fee_ids.join(" / ")}</p> : null}
                  <p className="meta">ID: {item.id}</p>
                  <p className="meta">SHA-256: {item.text_sha256}</p>
                  {source ? <p><a href={source.url} target="_blank" rel="noreferrer">厚生労働省の原文を確認</a></p> : null}
                </div>
              </details>;
            })}
          </div>
        </section>
      ))}
    </article>
  );
}
