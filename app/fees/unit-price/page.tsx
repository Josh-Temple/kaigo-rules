import VerificationSummary from "../../../components/verification-summary";
import ratesData from "../../../data/unit-price-dayservice.json";
import metaData from "../../../data/unit-price-dayservice-meta.json";
import assignmentsData from "../../../data/unit-price-region-assignments.json";
import assignmentMetaData from "../../../data/unit-price-region-assignments-meta.json";
import reviewData from "../../../data/unit-price-review.json";
import sourcesData from "../../../data/sources.json";

const rates = ratesData as Array<any>;
const meta = metaData as any;
const assignments = assignmentsData as Array<any>;
const assignmentMeta = assignmentMetaData as any;
const review = reviewData as any;
const sources = sourcesData as Array<any>;

const normalize = (value: string) =>
  value.normalize("NFKC").replace(/\s+/g, "").trim();

export default async function UnitPricePage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = normalize(q);
  const source = sources.find(
    (item) => item.id === meta.source_id || item.id === "mhlw-unit-price-current"
  );
  const priceById = new Map(rates.map((row) => [row.id, row]));
  const matches = query
    ? assignments.filter((row) =>
        normalize(row.prefecture + row.locality).includes(query)
      )
    : [];

  const counts = new Map<string, number>();
  for (const row of assignments) {
    counts.set(row.region_class, (counts.get(row.region_class) || 0) + 1);
  }

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">UNIT PRICE DATABASE</p>
      <h1>通所介護の一単位単価</h1>
      <p className="lead">
        報酬単位数を金額へ換算する際の、通所介護に適用される地域区分別の一単位単価です。
        報酬告示19号とは別の告示として管理しています。
      </p>

      <div className="notice">
        <strong>機械取込済み・人手確認待ち</strong><br />
        厚生労働省の現行告示HTMLから、単価と地域区分の明示地域を抽出しています。
        原文照合が終わるまでは「確認済み」と表示しません。
      </div>

      <VerificationSummary layerId="unit-price" />

      <section className="section">
        <h2>地域区分別</h2>
        <div className="unit-price-table">
          <div className="unit-price-head">
            <span>地域区分</span><span>1単位</span><span>明示地域</span>
          </div>
          {rates.map((row) => (
            <div className="unit-price-row" key={row.id}>
              <strong>{row.region_class}</strong>
              <span>{row.unit_price_yen.toFixed(2)}円</span>
              <span>
                {row.region_class === "その他"
                  ? "上記以外"
                  : String(counts.get(row.region_class) || 0) + "地域"}
              </span>
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>市区町村から調べる</h2>
        <form className="region-search-form" method="get">
          <input
            aria-label="市区町村名"
            name="q"
            defaultValue={q}
            placeholder="例：横浜市、川崎市、厚木市"
          />
          <button type="submit">検索</button>
        </form>

        {query ? (
          matches.length ? (
            <div className="region-result-list">
              {matches.map((row) => {
                const price = priceById.get(row.unit_price_id);
                return (
                  <div className="region-result-row" key={row.id}>
                    <div>
                      <strong>{row.prefecture} {row.locality}</strong>
                      <p className="meta">
                        名称・区域の基準日：{row.effective_reference_date}
                      </p>
                    </div>
                    <div>
                      <strong>{row.region_class}</strong>
                      <span>{price ? price.unit_price_yen.toFixed(2) + "円 / 単位" : "単価未接続"}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="notice">
              <strong>明示地域には一致しませんでした。</strong><br />
              告示では一級地〜七級地として明示されない地域は「その他」ですが、
              入力誤りを避けるため、この検索だけで自動的に「その他」と断定しません。
              なお、東京都の23区は告示上「特別区」と一括して記載されています。
            </div>
          )
        ) : (
          <p className="meta">
            告示で一級地〜七級地として明示された地域を検索します。
          </p>
        )}
      </section>

      <section className="section">
        <h2>地域区分の扱い</h2>
        <p>
          告示は、一級地〜七級地の対象地域を明示し、それ以外を「その他の地域」としています。
          地域名・区域は令和6年4月1日時点を基準として扱われます。
        </p>
        <dl className="rule-meta">
          <div><dt>明示地域</dt><dd>{assignmentMeta.explicit_assignment_count ?? assignments.length}件</dd></div>
          <div><dt>基準日</dt><dd>{assignmentMeta.effective_reference_date || "—"}</dd></div>
          <div><dt>その他</dt><dd>{assignmentMeta.default_rule_present ? "フォールバック規則あり" : "未取込"}</dd></div>
          <div><dt>確認状態</dt><dd>{assignmentMeta.review_status || meta.review_status || "—"}</dd></div>
        </dl>
      </section>

      <section className="section">
        <h2>人手チェック状況</h2>
        <dl className="rule-meta">
          <div><dt>単価</dt><dd>{(review.reviewed_rate_ids || []).length} / {rates.length}件</dd></div>
          <div><dt>地域割当</dt><dd>{(review.reviewed_assignment_ids || []).length} / {assignments.length}件</dd></div>
          <div><dt>「その他」規則</dt><dd>{review.reviewed_default_rule ? "確認済み" : "未確認"}</dd></div>
        </dl>
        <p className="meta">確認結果は生成データとは別台帳で管理し、公式ソースが更新された場合は再確認を要求します。</p>
      </section>

      <section className="section">
        <h2>計算の位置づけ</h2>
        <p>
          一単位の単価は10円に地域区分・サービス種類ごとの割合を乗じて算定します。
          通所介護は、同じ地域区分でも別のサービス種類と単価が異なる場合があります。
        </p>
        {source ? (
          <p>
            <a href={source.url} target="_blank" rel="noreferrer">
              厚生労働省の告示原文を確認
            </a>
          </p>
        ) : null}
      </section>
    </article>
  );
}
