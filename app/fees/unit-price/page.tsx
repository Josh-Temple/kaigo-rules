import ratesData from "../../../data/unit-price-dayservice.json";
import metaData from "../../../data/unit-price-dayservice-meta.json";
import sourcesData from "../../../data/sources.json";

const rates=ratesData as Array<any>;
const meta=metaData as any;
const sources=sourcesData as Array<any>;

export default function UnitPricePage(){
  const source=sources.find(s=>s.id===meta.source_id || s.id==="mhlw-unit-price-current");
  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">UNIT PRICE DATABASE</p>
      <h1>通所介護の一単位単価</h1>
      <p className="lead">
        報酬単位数を金額へ換算する際の、通所介護に適用される地域区分別の一単位単価です。
        報酬告示19号とは別の告示として管理しています。
      </p>
      <div className="notice">
        <strong>機械取込済み・人手確認待ち</strong><br/>
        厚生労働省の現行告示HTMLから抽出しています。地域区分そのものの市区町村対応表は次工程で別データ化します。
      </div>
      <section className="section">
        <h2>地域区分別</h2>
        <div className="unit-price-table">
          <div className="unit-price-head"><span>地域区分</span><span>割合</span><span>1単位</span></div>
          {rates.map(row=>(
            <div className="unit-price-row" key={row.id}>
              <strong>{row.region_class}</strong>
              <span>{row.ratio_text}</span>
              <span>{row.unit_price_yen.toFixed(2)}円</span>
            </div>
          ))}
        </div>
      </section>
      <section className="section">
        <h2>計算の位置づけ</h2>
        <p>告示上、一単位の単価は10円に地域区分・サービス種類ごとの割合を乗じて算定します。通所介護は他サービスと同じ地域区分でも割合が異なる場合があります。</p>
        {source ? <p><a href={source.url} target="_blank" rel="noreferrer">厚生労働省の告示原文を確認</a></p> : null}
        <p className="meta">地域区分の市区町村対応：{meta.region_assignment_status || "未取込"}</p>
      </section>
    </article>
  );
}
