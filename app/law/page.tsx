import VerificationSummary from "../../components/verification-summary";
import Link from "next/link";
import nodesData from "../../data/care-insurance-act-nodes.json";
import metaData from "../../data/care-insurance-act-meta.json";
import scopeData from "../../data/care-insurance-act-scope.json";
import reviewData from "../../data/care-insurance-act-review.json";
import relationsData from "../../data/care-insurance-act-relations.json";
import { getDefaultService } from "../../lib/service-catalog";
import { filterRecordsForService, isRecordApplicableToService } from "../../lib/service-scope";

const nodes=nodesData as Array<any>;
const meta=metaData as any;
const scope=scopeData as any;
const review=reviewData as any;
const relations=relationsData as Array<any>;
const defaultService=getDefaultService();

const articleNumberLabel=(num:string)=>"第"+num.replace("-","条の")+"条";
const articleHref=(num:string)=>"/law/"+num;

export default function LawPage(){
  const scopedNodes=filterRecordsForService(
    defaultService.service_id,
    "care_insurance_act",
    nodes,
    n=>n.id,
  );
  const articles=scopedNodes.filter(n=>n.node_type==="article");
  const articleIds=new Set(articles.map(article=>article.id));
  const reviewed=new Set(
    (review.reviewed_articles||[])
      .map((r:any)=>r.article_id)
      .filter((id:string)=>articleIds.has(id)),
  );
  const scopedCrossLayerRelations=relations.filter(
    relation=>
      relation.target_layer!=="care_insurance_act" &&
      isRecordApplicableToService(
        defaultService.service_id,
        "care_insurance_act",
        String(relation.from),
      ),
  );
  return <article className="answer-page rules-page">
    <p className="eyebrow">CARE INSURANCE ACT</p>
    <h1>介護保険法DB</h1>
    <p className="lead">
      通所介護の実務から直接たどる上位法令だけを構造化しています。
      定義、居宅介護サービス費、指定、基準、変更届、指導監督、取消し・公示までを初期範囲としています。
    </p>
    <div className="notice">
      <strong>全条文を複製するDBではありません。</strong><br/>
      通所介護から到達する条文だけをe-Govの現行法令XMLから取り込み、基準省令・報酬告示・解釈通知への関係を付けます。
    </div>

      <VerificationSummary layerId="care-insurance-act" />
    <section className="rules-stats">
      <div><strong>{articles.length}</strong><span>対象条文</span></div>
      <div><strong>{scopedNodes.length}</strong><span>構造ノード</span></div>
      <div><strong>{scopedCrossLayerRelations.length}</strong><span>他レイヤー接続</span></div>
      <div><strong>{reviewed.size}</strong><span>人手確認済み</span></div>
    </section>
    <section className="section">
      <h2>現在の法令版</h2>
      <dl className="rule-meta">
        <div><dt>法令</dt><dd>{meta.law_title||scope.title}</dd></div>
        <div><dt>法令番号</dt><dd>{meta.law_num||scope.law_num}</dd></div>
        <div><dt>現行改正</dt><dd>{meta.current_revision?.amendment_law_num||"取込前"}</dd></div>
        <div><dt>施行日</dt><dd>{meta.current_revision?.amendment_enforcement_date||"—"}</dd></div>
      </dl>
    </section>
    <section className="section">
      <h2>通所介護からたどる条文</h2>
      <div className="law-list">
        {articles.map(article=>{
          const focus=scope.focus_paragraphs?.[article.article_num]||[];
          return <Link className="law-row" href={articleHref(article.article_num)} key={article.id}>
            <span className="law-number">{article.article_title||articleNumberLabel(article.article_num)}</span>
            <span>
              <span className="law-title">{article.caption||"条文"}</span>
              {focus.length?<span className="law-focus">重点：第{focus.join("・")}項</span>:null}
            </span>
            <span className="law-status">{reviewed.has(article.id)?"人手確認済み":"取込済み・確認待ち"}</span>
          </Link>
        })}
      </div>
    </section>
    <section className="section">
      <h2>初期範囲から分離した条文</h2>
      {scope.excluded_initial_scope.map((item:any)=><p key={item.article}><strong>第{item.article.replace("-","条の")}条</strong> — {item.reason}</p>)}
    </section>
  </article>
}
