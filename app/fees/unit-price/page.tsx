import Link from "next/link";
import VerificationSummary from "../../../components/verification-summary";
import assignmentsData from "../../../data/unit-price-region-assignments.json";
import assignmentMetaData from "../../../data/unit-price-region-assignments-meta.json";
import reviewData from "../../../data/unit-price-review.json";
import {
  UNIT_PRICE_SOURCE_FAMILY,
  getProgressivePublicationTrust,
} from "../../../lib/publication-policy";
import {
  listPublicUnitPriceServices,
  publicUnitPriceRows,
  searchPublicUnitPrices,
  unitPriceHref,
} from "../../../lib/unit-price-discovery";

const assignments = assignmentsData as Array<{
  id: string;
  prefecture: string;
  locality: string;
  region_class: string;
  effective_reference_date: string;
}>;
const assignmentMeta = assignmentMetaData as {
  effective_reference_date?: string;
  review_status?: string;
};
const review = reviewData as {
  reviewed_assignment_ids?: string[];
  reviewed_default_rule?: boolean;
};

const normalize = (value: string) =>
  value.normalize("NFKC").replace(/\s+/g, "").trim();

export default async function UnitPricePage({
  searchParams,
}: {
  searchParams: Promise<{ service?: string; q?: string }>;
}) {
  const params = await searchParams;
  const q = String(params.q || "").slice(0, 120).trim();
  // Preserve the existing /fees/unit-price URL for dayservice users.
  const selectedId = String(params.service || "dayservice").trim();
  const query = normalize(q);
  const services = listPublicUnitPriceServices();
  const selectedService = services.find((item) => item.service_id === selectedId);
  const trust = selectedService
    ? getProgressivePublicationTrust(selectedId, UNIT_PRICE_SOURCE_FAMILY)
    : null;
  const allRates = selectedService ? publicUnitPriceRows(selectedId) : [];
  const rateMatches = selectedService
    ? searchPublicUnitPrices(q, selectedId)
    : [];
  const regionMatches = selectedService && query
    ? assignments.filter((row) =>
        normalize(row.prefecture + row.locality).includes(query)
      )
    : [];
  const priceByRegion = new Map(
    allRates.map((row) => [row.region_class, row]),
  );

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">UNIT PRICE DATABASE</p>
      <h1>介護サービスの一単位単価</h1>
      <p className="lead">
        厚生労働省の単価告示について、公開条件を満たしたサービスのみを選択できます。
        地域区分ごとの一単位単価を、サービス別の算定割合とともに表示します。
        報酬単位数そのものや加算要件とは区別します。
      </p>

      <div className="notice">
        <strong>公開範囲と確認状態</strong>
        <p>
          単価の表示にはサービス別の本文・適用範囲・現行性の公開判定を適用しています。
          市区町村の地域区分は別の取込データで、人手確認の状態も異なります。
          未公開のサービスや未確認の算定条件を類推して表示しません。
        </p>
      </div>

      <section className="section">
        <h2>サービスを選ぶ</h2>
        <form className="region-search-form" method="get">
          <label htmlFor="unit-price-service">サービス</label>
          <select id="unit-price-service" name="service" defaultValue={selectedId}>
            {!selectedService ? <option value={selectedId}>公開対象外のサービス</option> : null}
            {services.map((service) => (
              <option value={service.service_id} key={service.service_id}>
                {service.label}
              </option>
            ))}
          </select>
          {q ? <input type="hidden" name="q" value={q} /> : null}
          <button type="submit">表示する</button>
        </form>
        <p className="meta">現在の公開対象：{services.length}サービス。公開対象であっても、人手確認済みを意味しません。</p>
      </section>

      {!selectedService || !trust || !allRates.length ? (
        <div className="notice">
          <strong>このサービスの単価は現在公開していません。</strong>
          <p>
            データが存在しないことを意味しません。公開条件を満たしたサービスから選ぶか、
            公式の告示を確認してください。
          </p>
          <p><Link href="/databases">制度DB一覧へ戻る →</Link></p>
        </div>
      ) : (
        <>
          <section className="section">
            <h2>{selectedService.label}の単価</h2>
            <p className="meta">
              出典：{trust.source_title}
              {trust.effective_date ? " / 適用基準日：" + trust.effective_date : ""}
              {trust.checked_at ? " / 公式表示確認日：" + trust.checked_at : ""}
            </p>
            <p>
              <a href={trust.source_url} target="_blank" rel="noreferrer">
                厚生労働省の告示原文 →
              </a>
            </p>
            {selectedId === "dayservice" ? <VerificationSummary layerId="unit-price" /> : null}
          </section>

          <section className="section">
            <h2>地域区分・単価を検索</h2>
            <form className="region-search-form" method="get">
              <input type="hidden" name="service" value={selectedId} />
              <label htmlFor="unit-price-query">地域区分、単価、市区町村名</label>
              <input
                id="unit-price-query"
                name="q"
                defaultValue={q}
                maxLength={120}
                placeholder="例：一級地、地域区分、横浜市"
              />
              <button type="submit">検索</button>
            </form>
            {query ? (
              <p className="meta">
                <Link href={unitPriceHref(selectedId)}>検索条件をクリア</Link>
              </p>
            ) : null}

            {rateMatches.length ? (
              <div className="unit-price-table">
                <div className="unit-price-head">
                  <span>地域区分</span><span>1単位</span><span>適用割合</span>
                </div>
                {rateMatches.map((row) => (
                  <div className="unit-price-row" key={row.id}>
                    <strong>{row.region_class}</strong>
                    <span>{row.unit_price_yen.toFixed(2)}円</span>
                    <span>{row.ratio_text}</span>
                  </div>
                ))}
              </div>
            ) : !regionMatches.length ? (
              <div className="notice">
                <strong>現在公開している範囲では一致しませんでした。</strong>
                <p>資料が存在しないことを意味しません。検索語を変更するか、公式資料で確認してください。</p>
              </div>
            ) : null}
          </section>

          <section className="section">
            <h2>市区町村名から地域区分を探す</h2>
            <p>
              告示に明示された市区町村のみを検索します。地域割当は機械取込済みですが、
              人手確認が完了していないため、正式な算定前に告示原文で照合してください。
            </p>
            {regionMatches.length ? (
              <div className="region-result-list">
                {regionMatches.map((row) => {
                  const rate = priceByRegion.get(row.region_class);
                  return (
                    <div className="region-result-row" key={row.id}>
                      <div>
                        <strong>{row.prefecture} {row.locality}</strong>
                        <p className="meta">地域名の基準日：{row.effective_reference_date}</p>
                      </div>
                      <div>
                        <strong>{row.region_class}</strong>
                        <span>
                          {rate ? rate.unit_price_yen.toFixed(2) + "円 / 単位" : "この区分の単価は未公開"}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <p className="meta">
                地域名を入力すると、明示地域の一致結果を表示します。
                入力した地域が見つからなくても、自動的に「その他」と判定しません。
                東京都の23区は告示上「特別区」としてまとめて記載されています。
              </p>
            )}
          </section>

          <section className="section">
            <h2>出典・確認上の注意</h2>
            <dl className="rule-meta">
              <div><dt>サービス</dt><dd>{selectedService.label}</dd></div>
              <div><dt>公開単価</dt><dd>{allRates.length}区分</dd></div>
              <div><dt>公式表示確認日</dt><dd>{trust.checked_at || "未記録"}</dd></div>
              <div><dt>地域割当の基準日</dt><dd>{assignmentMeta.effective_reference_date || "未記録"}</dd></div>
              <div><dt>地域割当の人手確認</dt><dd>
                {(review.reviewed_assignment_ids || []).length} / {assignments.length}件
              </dd></div>
              <div><dt>「その他」の地域判定</dt><dd>
                {review.reviewed_default_rule ? "人手確認済み" : "人手未確認・自動適用なし"}
              </dd></div>
            </dl>
            <p className="meta">
              「現行性確認」と「人手確認」は別の状態です。
              地域割当の取込状態：{assignmentMeta.review_status || "未記録"}。
            </p>
          </section>
        </>
      )}
    </article>
  );
}
