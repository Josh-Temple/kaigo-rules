import { pageMetadata } from "../../lib/site-metadata";

export const metadata = pageMetadata("介護保険法DB", "介護保険法の収載条文を、適用範囲や確認状態を区別して閲覧できます。", "/law");

import VerificationSummary from "../../components/verification-summary";
import ServiceContextLinks from "../../components/service-context-links";
import Link from "next/link";
import nodesData from "../../data/care-insurance-act-nodes.json";
import metaData from "../../data/care-insurance-act-meta.json";
import scopeData from "../../data/care-insurance-act-scope.json";
import reviewData from "../../data/care-insurance-act-review.json";
import relationsData from "../../data/care-insurance-act-relations.json";
import { listServices } from "../../lib/service-catalog";
import { filterRecordsForService, isRecordApplicableToService } from "../../lib/service-scope";

const nodes=nodesData as Array<any>;
const meta=metaData as any;
const scope=scopeData as any;
const review=reviewData as any;
const relations=relationsData as Array<any>;

const articleNumberLabel=(num:string)=>"第"+num.replace("-","条の")+"条";

const filterServices=listServices().filter(service =>
  service.verification_layer_ids.some(
    layerId => layerId === "care-insurance-act" || layerId.startsWith("care-insurance-act-"),
  ),
);

export default async function LawPage({
  searchParams,
}: {
  searchParams: Promise<{ service?: string }>;
}){
  const { service = "" } = await searchParams;
  const selectedService=filterServices.find(item=>item.service_id===service);
  const selectedServiceId=selectedService?.service_id;
  const displayedNodes=selectedServiceId
    ? filterRecordsForService(selectedServiceId,"care_insurance_act",nodes,n=>n.id)
    : nodes;
  const articles=displayedNodes.filter(n=>n.node_type==="article");
  const articleIds=new Set(articles.map(article=>article.id));
  const reviewed=new Set(
    (review.reviewed_articles||[])
      .map((r:any)=>r.article_id)
      .filter((id:string)=>articleIds.has(id)),
  );
  const crossLayerRelations=relations.filter(relation=>{
    if(relation.target_layer==="care_insurance_act") return false;
    if(!selectedServiceId) return true;
    return isRecordApplicableToService(
      selectedServiceId,
      "care_insurance_act",
      String(relation.from),
    );
  });
  const suffix=selectedServiceId ? `?service=${encodeURIComponent(selectedServiceId)}` : "";

  return <article className="answer-page rules-page">
    <p className="eyebrow">CARE INSURANCE ACT DATABASE</p>
    <h1>介護保険法DB</h1>
    <p className="lead">
      e-Govの現行法令XMLから取り込んだ共有コーパスを全体表示します。
      サービスを選んだ場合だけ、そのサービスに適用scopeが登録された条文・項へ絞り込みます。
    </p>
    <div className="notice">
      <strong>全条文を複製するDBではなく、現在取り込み済みの制度コーパスです。</strong><br/>
      「すべて」ではサービス横断の共有コーパスを表示します。サービス別の確認状態や適用scopeは、
      公開・検証済みの範囲から順次追加します。
    </div>

    <nav className="rules-filter" aria-label="サービスで介護保険法を絞り込む">
      <Link className={!selectedServiceId ? "rules-filter-active" : ""} href="/law">すべて</Link>
      {filterServices.map(item=>(
        <Link
          className={selectedServiceId===item.service_id ? "rules-filter-active" : ""}
          href={`/law?service=${item.service_id}`}
          key={item.service_id}
        >
          {item.label}
        </Link>
      ))}
    </nav>

    {selectedServiceId==="dayservice" ? <ServiceContextLinks serviceId="dayservice" /> : null}

    <p className="scope-note">
      {selectedService
        ? `${selectedService.label}で絞り込み中。登録済みの適用scopeだけを表示しています。`
        : "共有コーパスを全体表示中。表示されること自体は、各サービスへの適用確認や人手確認を意味しません。"}
    </p>

    <VerificationSummary layerId="care-insurance-act" />

    <section className="rules-stats">
      <div><strong>{meta.counts?.articles_total || articles.length}</strong><span>共有コーパス条文</span></div>
      <div><strong>{meta.counts?.nodes_total || nodes.length}</strong><span>共有コーパスノード</span></div>
      <div><strong>{articles.length}</strong><span>表示中の条文</span></div>
      <div><strong>{crossLayerRelations.length}</strong><span>表示scopeの他レイヤー接続</span></div>
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
      <h2>{selectedService ? selectedService.label+"からたどる条文" : "取り込み済みの条文"}</h2>
      <div className="law-list">
        {articles.map(article=>{
          const focus=selectedServiceId==="dayservice"
            ? scope.focus_paragraphs?.[article.article_num]||[]
            : [];
          return <Link className="law-row" href={`/law/${article.article_num}${suffix}`} key={article.id}>
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

    {selectedServiceId==="dayservice" ? (
      <section className="section">
        <h2>通所介護の初期範囲から分離した条文</h2>
        {scope.excluded_initial_scope.map((item:any)=><p key={item.article}><strong>第{item.article.replace("-","条の")}条</strong> — {item.reason}</p>)}
      </section>
    ) : null}
  </article>
}
