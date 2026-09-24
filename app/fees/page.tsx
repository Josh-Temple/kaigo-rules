import Link from "next/link";
import nodesData from "../../data/remuneration-current-skeleton.json";
import textData from "../../data/remuneration-current-text.json";
import metaData from "../../data/remuneration-current-meta.json";
import textMetaData from "../../data/remuneration-current-text-meta.json";
import reviewData from "../../data/remuneration-review.json";
import chainData from "../../data/remuneration-source-chain.json";
import sourcesData from "../../data/sources.json";

const nodes = nodesData as Array<any>;
const texts = textData as Array<any>;
const meta = metaData as any;
const textMeta = textMetaData as any;
const review = reviewData as any;
const chain = chainData as Array<any>;
const sources = sourcesData as Array<any>;

const labels: Record<string,string> = {
  CURRENT_STRUCTURE_NEEDS_HUMAN_CHECK:"現行構造・人手確認待ち",
  CURRENT_AFTER_TEXT_NEEDS_HUMAN_CHECK:"令和8年改正後文・人手確認待ち",
  OUT_OF_CORE_SCOPE:"コア範囲外",
  VERIFIED_CURRENT:"現行確認済み",
  UNKNOWN:"未確認"
};

const routeKey = (id: string) => id.replace("fee.dayservice.", "");

export default function FeesPage() {
  const root=nodes.find(n=>n.id==="fee.dayservice.root");
  const children=nodes.filter(n=>n.parent_id===root?.id);
  const reviewedIds=new Set((review.reviewed_nodes || []).map((item:any)=>item.fee_id));
  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">REMUNERATION DATABASE</p>
      <h1>通所介護の報酬DB</h1>
      <p className="lead">
        介護報酬は、基準省令とは別に、報酬告示・算定方法告示・留意事項通知を分けて構造化します。
        厚生労働省の現行統合HTMLから通所介護費を区画ごとに取り込み、人手確認できる形にしています。
      </p>
      <div className="notice">
        <strong>公式現行本文は取り込み済みですが、人手確認は別工程です。</strong><br/>
        厚生労働省の現行HTMLには令和8年告示第87号まで反映されています。
        個々の単位数・加算率は、原文照合が終わるまで「確認済み」とは表示しません。
      </div>

      <section className="rules-stats fee-stats">
        <div><strong>{meta.counts.nodes}</strong><span>骨格ノード</span></div>
        <div><strong>{textMeta.record_count || texts.length}</strong><span>本文取込</span></div>
        <div><strong>{(review.reviewed_nodes || []).length}</strong><span>人手確認済み</span></div>
        <div><strong>{meta.counts.out_of_core_scope}</strong><span>コア範囲外</span></div>
      </section>

      <section className="section">
        <h2>現在の取得元</h2>
        <dl className="rule-meta">
          <div><dt>現行告示</dt><dd>指定居宅サービスに要する費用の額の算定に関する基準</dd></div>
          <div><dt>最新反映</dt><dd>{textMeta.current_amendment || meta.current_amendment?.amendment_law_num || "—"}</dd></div>
          <div><dt>施行日</dt><dd>{textMeta.current_amendment_effective_from || meta.current_amendment?.effective_from || "—"}</dd></div>
          <div><dt>本文取込</dt><dd>{texts.length}区画 / 確認済み {reviewedIds.size}区画</dd></div>
        </dl>
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
        <h2>通所介護費の項目</h2>
        <p>各項目を開くと、厚生労働省の現行HTMLから取り込んだ本文と取得証跡を確認できます。</p>
        <div className="fee-list">
          {children.map(node=>{
            const imported=texts.some(item=>item.fee_id===node.id);
            const isReviewed=reviewedIds.has(node.id);
            return <Link id={node.id} className="fee-row fee-row-link" href={`/fees/${routeKey(node.id)}`} key={node.id}>
              <div>
                <p className="meta">{node.number_path.join(" / ")}</p>
                <h3>{node.title}</h3>
                <p className="meta">{imported ? "現行公式本文を取込済み" : "本文未取込"}</p>
              </div>
              <span className={node.verification_status==="OUT_OF_CORE_SCOPE"?"fee-status fee-out":isReviewed?"fee-status fee-reviewed":"fee-status"}>
                {isReviewed ? "人手確認済み" : labels[node.verification_status] || node.verification_status}
              </span>
            </Link>;
          })}
        </div>
      </section>

      <section className="section">
        <h2>別告示の算定基準</h2>
        <p>
          定員超過・人員欠如時の算定方法や、「別に厚生労働大臣が定める基準」とされた加算要件は
          報酬告示19号とは別の告示にあります。
        </p>
        <p><Link href="/fees/criteria">告示27号・95号の構造化データを見る →</Link></p>
        <p><Link href="/fees/unit-price">通所介護の一単位単価を見る →</Link></p>
        <p><Link href="/fees/guidance">算定上の留意事項（老企第36号）の再構成状況を見る →</Link></p>
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
