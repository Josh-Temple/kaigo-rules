import Link from "next/link";
import nodesData from "../../../data/fee-guidance-current-skeleton.json";
import relationsData from "../../../data/fee-guidance-relations.json";
import eventsData from "../../../data/fee-guidance-amendment-events.json";
import chainData from "../../../data/fee-guidance-source-chain.json";
import metaData from "../../../data/fee-guidance-current-meta.json";
import reviewData from "../../../data/fee-guidance-review.json";
import candidatesData from "../../../data/fee-guidance-text-candidates.json";
import replayCoverageData from "../../../data/fee-guidance-replay-coverage.json";
import sourcesData from "../../../data/sources.json";
import feeData from "../../../data/remuneration-current-skeleton.json";

const nodes=nodesData as Array<any>;
const relations=relationsData as Array<any>;
const events=eventsData as Array<any>;
const chain=chainData as Array<any>;
const meta=metaData as any;
const review=reviewData as any;
const candidates=candidatesData as Array<any>;
const replayCoverage=replayCoverageData as Array<any>;
const sources=sourcesData as Array<any>;
const fees=feeData as Array<any>;

const label:Record<string,string>={
  KNOWN_AFTER_TEXT:"現行側の見出し・断片を確認",
  INHERITED_UNVERIFIED:"過去資料から見出し補完・本文未統合",
  UNKNOWN:"未確認・穴",
  VERIFIED_CURRENT:"現行確認済み"
};

const replayLabel:Record<string,string>={
  CHECKPOINT_CHAIN_COMPLETE_EXACT_TEXT_PENDING:"改正履歴確認済み・原文抽出待ち",
  BASE_BODY_SOURCE_PENDING:"基礎本文の取得待ち",
  BASE_BODY_SOURCE_PENDING_CURRENT_PATCH_CAPTURED:"基礎本文待ち・最新改正取得済み",
  CHECKPOINT_CHAIN_COMPLETE_CURRENT_PATCH_CAPTURED_EXACT_TEXT_PENDING:"改正履歴確認済み・最新改正取得済み・原文統合待ち"
};

const feeHref=(id:string)=>"/fees/"+id.replace("fee.dayservice.","");

export default function FeeGuidancePage(){
  return <article className="answer-page notice-db-page">
    <p className="eyebrow">REMUNERATION GUIDANCE DATABASE</p>
    <h1>通所介護の算定上の留意事項</h1>
    <p className="lead">
      老企第36号のうち「7 通所介護費」を、令和6年度の改正資料を起点に穴あき構造で再構成しています。
    </p>

    <div className="notice">
      <strong>現行統合版ではありません。</strong><br/>
      令和6年度資料で「略」とされた見出しは、過去の厚生労働省改正資料まで遡って補完しました。
      ただし本文の現行統合と人手確認は未完了であり、見出し補完だけで「確認済み」とは扱いません。
    </div>

    <section className="rules-stats">
      <div><strong>{meta.counts.total}</strong><span>骨格ノード</span></div>
      <div><strong>{meta.counts.KNOWN_AFTER_TEXT || 0}</strong><span>現行側確認</span></div>
      <div><strong>{meta.counts.INHERITED_UNVERIFIED || 0}</strong><span>見出し補完・本文未統合</span></div>
      <div><strong>{(review.reviewed_nodes || []).length}</strong><span>人手確認済み</span></div>
    </section>

    <section className="section">
      <h2>資料チェーン</h2>
      <div className="source-chain">
        {chain.map(entry=>{
          const source=sources.find(s=>s.id===entry.source_id);
          return <div className="source-chain-row" key={entry.source_id}>
            <span className="meta">{entry.issued_period}</span>
            <div>
              <strong>{source?.title || entry.source_id}</strong>
              <p>{entry.use}</p>
              {entry.warning?<p className="meta">注意：{entry.warning}</p>:null}
            </div>
          </div>;
        })}
      </div>
    </section>

    <section className="section">
      <h2>現在の骨格</h2>
      <div className="fee-guidance-list">
        {nodes.map(node=>{
          const linked=relations.filter(r=>r.from_guidance_id===node.id);
          const textCandidates=candidates.filter(c=>c.guidance_id===node.id);
          return <section className="fee-guidance-row" key={node.id}>
            <div className="fee-guidance-head">
              <div>
                <p className="meta">{node.number_path.join(" / ")}</p>
                <h3>{node.title}</h3>
              </div>
              <span className={node.verification_status==="UNKNOWN"?"fee-status fee-out":"fee-status"}>
                {label[node.verification_status] || node.verification_status}
              </span>
            </div>
            {node.verification_status==="UNKNOWN"
              ? <p className="notice-hole">令和6年度の新旧対照表では本文・見出しが省略されています。過去資料から再生します。</p>
              : <p className="meta">本文はまだ統合していません。現在側の見出し・参照関係のみ保持しています。</p>}
            {textCandidates.length?<p className="meta">本文再構成候補：{textCandidates.length}件収集済み（人手未確認）</p>:null}
            {linked.length?<p className="meta">対応する報酬項目：{
              linked.map((rel,index)=>{
                const fee=fees.find(f=>f.id===rel.to_fee_id);
                return <span key={rel.to_fee_id}>{index>0?" / ":""}<Link href={feeHref(rel.to_fee_id)}>{fee?.title || rel.to_fee_id}</Link></span>;
              })
            }</p>:null}
          </section>;
        })}
      </div>
    </section>

    <section className="section">
      <h2>本文再構成の進捗</h2>
      <p>
        令和6年度資料で省略された8項目について、過去の公式資料や後続改正から本文候補を収集しています。
        ここにある内容は現行統合本文ではなく、人手確認前の再構成材料です。
      </p>
      <div className="source-chain">
        {candidates.map(candidate=>{
          const node=nodes.find(n=>n.id===candidate.guidance_id);
          const source=sources.find(s=>s.id===candidate.source_id);
          const replay=replayCoverage.find(r=>r.guidance_id===candidate.guidance_id);
          return <div className="source-chain-row" key={candidate.id}>
            <span className="meta">{candidate.source_period}</span>
            <div>
              <strong>{node?.title || candidate.guidance_id}</strong>
              <p>{candidate.candidate_summary}</p>
              <p className="meta">出典：{source?.title || candidate.source_id} / 候補・人手未確認</p>
              {replay?<p className="meta">改正履歴：{replay.checkpoints.length}時点確認 / {replayLabel[replay.replay_status] || replay.replay_status}</p>:null}
            </div>
          </div>;
        })}
      </div>
    </section>

    <section className="section">
      <h2>改正イベント</h2>
      {events.map(event=><div className="source-card" key={event.id}>
        <p className="meta">{event.effective_from}{event.effective_to?" 〜 "+event.effective_to:""}</p>
        <p>{event.summary}</p>
      </div>)}
    </section>

    <section className="section">
      <h2>次の工程</h2>
      <p>
        8項目すべてで基礎資料と後続改正の経路を確保しました。次は根拠PDFの本文を項目単位で正確に統合し、
        7(25)には令和8年5月8日改正を重ねたうえで、人手確認用の現行本文候補を作ります。
      </p>
    </section>
  </article>;
}
