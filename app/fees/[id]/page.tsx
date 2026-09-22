import Link from "next/link";
import { notFound } from "next/navigation";
import nodesData from "../../../data/remuneration-current-skeleton.json";
import textData from "../../../data/remuneration-current-text.json";
import relationsData from "../../../data/remuneration-relations.json";
import reviewData from "../../../data/remuneration-review.json";
import sourcesData from "../../../data/sources.json";
import metaData from "../../../data/remuneration-current-meta.json";

type FeeNode = {
  id:string;
  parent_id:string|null;
  number_path:string[];
  title:string;
  authority_layer:string;
  service_scope:string;
  verification_status:string;
  source_id:string;
  source_locator:string;
  latest_amendment_evidence?:Array<{source_id:string;locator:string;evidence_type:string}>;
  note?:string;
};

type FeeText = {
  fee_id:string;
  official_text:string;
  text_sha256:string;
  source_id:string;
  source_url:string;
  source_locator:string;
  import_status:string;
};

const nodes=nodesData as FeeNode[];
const texts=textData as FeeText[];
const relations=relationsData as Array<any>;
const review=reviewData as any;
const sources=sourcesData as Array<any>;
const meta=metaData as any;

const routeKey=(id:string)=>id.replace("fee.dayservice.","");
const nodeByRoute=(route:string)=>nodes.find(node=>routeKey(node.id)===route);
const ordinanceHref=(id:string)=>{
  const match=id.match(/^ordinance37\.article\.([0-9-]+)/);
  return match ? `/rules/${match[1]}` : "/rules";
};

export function generateStaticParams(){
  return nodes.filter(node=>node.id!=="fee.dayservice.root").map(node=>({id:routeKey(node.id)}));
}

export default async function FeeDetailPage({params}:{params:Promise<{id:string}>}){
  const {id}=await params;
  const node=nodeByRoute(id);
  if(!node) notFound();

  const current=texts.find(item=>item.fee_id===node.id);
  const nodeReview=(review.reviewed_nodes||[]).find((item:any)=>item.fee_id===node.id);
  const related=relations.filter(rel=>rel.from_fee_id===node.id);
  const source=sources.find(item=>item.id===node.source_id);
  const isReviewed=Boolean(nodeReview && current && nodeReview.text_sha256===current.text_sha256);

  return (
    <article className="answer-page rules-page fee-detail-page">
      <p className="eyebrow">{node.authority_layer}</p>
      <h1>{node.title}</h1>
      <p className="meta">{node.number_path.join(" / ")} ・ {node.service_scope}</p>

      <div className={isReviewed ? "notice fee-reviewed-notice" : "notice"}>
        <strong>{isReviewed ? "人手確認済み" : "現行公式本文を機械取込済み・人手確認待ち"}</strong><br/>
        {isReviewed
          ? "確認時の本文SHA-256と現在の取込本文が一致しています。"
          : "厚生労働省の現行HTMLから取得していますが、見出し・単位数・条件・参照先の人手照合はまだ完了していません。"}
      </div>

      <section className="section">
        <h2>現行本文</h2>
        {current ? <div className="fee-official-text">{current.official_text}</div> : <p>本文はまだ取り込まれていません。</p>}
      </section>

      {related.length ? (
        <section className="section">
          <h2>関連する制度・別告示</h2>
          <div className="relation-list">
            {related.map((rel,index)=>{
              const linkedSource=rel.to_source_id ? sources.find(item=>item.id===rel.to_source_id) : null;
              return <div className="relation-row" key={`${rel.relation}-${index}`}>
                <strong>{rel.relation}</strong>
                <div>
                  {rel.to_id ? <p><Link href={ordinanceHref(rel.to_id)}>{rel.to_id.replace("ordinance37.article.","基準省令 第")}条</Link></p> : null}
                  {linkedSource ? <p><a href={linkedSource.url} target="_blank" rel="noreferrer">{linkedSource.title}</a></p> : null}
                  <p className="meta">{rel.status}</p>
                </div>
              </div>;
            })}
          </div>
        </section>
      ) : null}

      {node.latest_amendment_evidence?.length ? (
        <section className="section">
          <h2>最新改定の証跡</h2>
          {node.latest_amendment_evidence.map((evidence,index)=>{
            const evidenceSource=sources.find(item=>item.id===evidence.source_id);
            return <p key={index}>
              {evidenceSource ? <a href={evidenceSource.url} target="_blank" rel="noreferrer">{evidenceSource.title}</a> : evidence.source_id}
              <br/><span className="meta">{evidence.locator} / {evidence.evidence_type}</span>
            </p>;
          })}
        </section>
      ) : null}

      <section className="section">
        <h2>取得証跡</h2>
        <dl className="rule-meta">
          <div><dt>取得元</dt><dd>{source ? <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a> : node.source_id}</dd></div>
          <div><dt>最新反映</dt><dd>{meta.current_amendment?.amendment_law_num || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{meta.current_amendment?.effective_from || "—"}</dd></div>
          <div><dt>本文SHA-256</dt><dd className="hash">{current?.text_sha256 || "—"}</dd></div>
        </dl>
      </section>

      {node.note ? <p className="scope-note">{node.note}</p> : null}
      <p><Link href="/fees">報酬DB一覧へ戻る</Link></p>
    </article>
  );
}
