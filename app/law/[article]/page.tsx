import Link from "next/link";
import {notFound} from "next/navigation";
import nodesData from "../../../data/care-insurance-act-nodes.json";
import relationsData from "../../../data/care-insurance-act-relations.json";
import reviewData from "../../../data/care-insurance-act-review.json";
import metaData from "../../../data/care-insurance-act-meta.json";

const nodes=nodesData as Array<any>;
const relations=relationsData as Array<any>;
const review=reviewData as any;
const meta=metaData as any;

export function generateStaticParams(){
  return nodes.filter(n=>n.node_type==="article").map(n=>({article:n.article_num}));
}

const targetHref=(relation:any)=>{
  if(relation.target_layer==="care_insurance_act"){
    const m=String(relation.to).match(/^careact\.article\.([0-9-]+)/);
    return m?"/law/"+m[1]:null;
  }
  if(relation.target_layer==="ordinance37"){
    const m=String(relation.to).match(/^ordinance37\.article\.([0-9-]+)/);
    return m?"/rules/"+m[1]:null;
  }
  if(relation.target_layer==="remuneration") return "/fees";
  if(relation.target_layer==="interpretation_notice") return "/notices";
  return null;
};

export default async function LawArticlePage({params}:{params:Promise<{article:string}>}){
  const {article}=await params;
  const aid=`careact.article.${article}`;
  const root=nodes.find(n=>n.id===aid&&n.node_type==="article");
  if(!root) notFound();
  const children=nodes.filter(n=>n.parent_id===aid);
  const reviewed=(review.reviewed_articles||[]).find((r:any)=>r.article_id===aid);
  const outgoing=relations.filter(r=>r.from===aid || String(r.from).startsWith(aid+".p."));
  return <article className="answer-page rules-page">
    <p className="eyebrow">介護保険法 / 通所介護関連</p>
    <h1>{root.article_title} {root.caption||""}</h1>
    <p className="meta">{root.id}</p>
    <div className={reviewed?"notice fee-reviewed-notice":"notice"}>
      <strong>{reviewed?"人手確認済み":"e-Gov現行XMLから取込済み・人手確認待ち"}</strong><br/>
      法令本文の取込と、基準省令・報酬告示等への関係確認は別に管理します。
    </div>
    <section className="section">
      <h2>条文</h2>
      <div className="rule-tree">
        {children.map(p=><section className="rule-node" key={p.id}>
          <span className="rule-node-label">{p.label||("第"+p.paragraph_num+"項")}</span>
          <p>{p.official_text}</p>
          {nodes.filter(n=>n.parent_id===p.id).map(i=><div className="rule-node rule-node-item" key={i.id}>
            <span className="rule-node-label">{i.label}</span><p>{i.official_text}</p>
          </div>)}
        </section>)}
      </div>
    </section>
    {outgoing.length?<section className="section">
      <h2>制度グラフ</h2>
      <div className="law-graph">
        {outgoing.filter(r=>r.relation!=="contains").map((r,index)=>{
          const href=targetHref(r);
          return <div className="law-graph-row" key={r.from+r.relation+r.to+index}>
            <span className="meta">{r.relation}</span>
            <div>{href?<Link href={href}>{r.to}</Link>:<span>{r.to}</span>}<p className="meta">{r.target_layer}{r.verification_status?" / "+r.verification_status:""}</p></div>
          </div>
        })}
      </div>
    </section>:null}
    <section className="section">
      <h2>取得証跡</h2>
      <dl className="rule-meta">
        <div><dt>法令版</dt><dd>{meta.current_revision?.law_revision_id||"—"}</dd></div>
        <div><dt>本文SHA-256</dt><dd className="hash">{root.text_sha256}</dd></div>
        <div><dt>人手確認</dt><dd>{reviewed?"確認済み":"未確認"}</dd></div>
      </dl>
      <p><a href={root.source_url} target="_blank" rel="noreferrer">e-Govの原文を確認</a></p>
    </section>
    <p><Link href="/law">介護保険法DBへ戻る</Link></p>
  </article>
}
