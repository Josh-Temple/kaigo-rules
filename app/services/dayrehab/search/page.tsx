import Link from "next/link";
import verificationRegistryData from "../../../../data/verification-registry.json";
import {
  searchDayrehabPublicLayers,
  type DayrehabSearchLayer,
  type DayrehabSearchResult,
} from "../../../../lib/dayrehab-search";

const registry = verificationRegistryData as any;
const LIMIT_PER_LAYER = 12;

const layerOrder: DayrehabSearchLayer[] = [
  "ordinance37",
  "rouki25",
  "remuneration",
  "fee-guidance",
];

const layerTitles: Record<DayrehabSearchLayer, string> = {
  ordinance37: "基準省令",
  rouki25: "基準解釈通知",
  remuneration: "報酬基準",
  "fee-guidance": "算定上の留意事項",
};

function verificationText(layerId: string) {
  const layer = (registry.layers || []).find((item: any) => item.id === layerId);
  if (!layer) return "確認状態を取得できません";
  const content = String(layer.content_verification?.status || "未確認");
  const currentness = String(layer.currentness?.status || "未確認");
  const human = String(layer.human_review?.status || "未確認");

  const contentLabel = content.startsWith("PASS")
    ? "原資料との機械照合済み"
    : "内容確認中";
  const currentnessLabel =
    currentness === "GAP" || currentness.includes("HISTORICAL")
      ? "現行性GAP"
      : currentness.includes("LIVE_SOURCE")
        ? "現行性を継続監視"
        : currentness.includes("HOLD")
          ? "現行性HOLD"
          : `現行性: ${currentness}`;
  const humanLabel =
    human.includes("NOT") || human.includes("UNREVIEWED") || human.includes("NEEDS_HUMAN")
      ? "人手確認未実施"
      : `人手確認: ${human}`;

  return `${contentLabel} / ${currentnessLabel} / ${humanLabel}`;
}

function ResultRows({ results }: { results: DayrehabSearchResult[] }) {
  return (
    <div className="source-chain">
      {results.slice(0, LIMIT_PER_LAYER).map((result) => (
        <article className="source-card" key={`${result.layer}:${result.id}`}>
          <p className="meta">{result.meta}</p>
          <h3><Link href={result.href}>{result.title}</Link></h3>
          {result.excerpt ? <p>{result.excerpt}</p> : null}
          <p className="meta">{verificationText(result.verificationLayerId)}</p>
        </article>
      ))}
    </div>
  );
}

export default async function DayrehabSearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();
  const results = searchDayrehabPublicLayers(query);
  const grouped = new Map<DayrehabSearchLayer, DayrehabSearchResult[]>(
    layerOrder.map((layer) => [
      layer,
      results.filter((result) => result.layer === layer),
    ]),
  );

  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">DAY REHABILITATION / CROSS-LAYER SEARCH</p>
      <h1>通所リハビリテーションを横断検索</h1>
      <p className="lead">
        公開済みの基準省令、基準解釈通知、報酬基準、算定上の留意事項を、通所リハのservice contextを保ったまま同じ語で探します。
      </p>

      <div className="notice">
        <strong>検索対象は通所リハの公開4レイヤーです。</strong><br />
        検索結果に出ることと、現行性・人手確認済みであることは別です。
        旧HTMLや改正対照表だけを根拠にしている項目は、結果にもGAPを表示します。
        通所介護のFAQ・Q&Aはこの検索には混ぜません。
      </div>

      <form className="global-search-form" method="get" action="/services/dayrehab/search">
        <label>
          <span>キーワード</span>
          <input
            name="q"
            defaultValue={q}
            placeholder="例：入浴介助、送迎、管理者、感染症"
            autoFocus
          />
        </label>
        <button type="submit">検索する</button>
      </form>

      {!query ? (
        <section className="section">
          <h2>検索対象</h2>
          <div className="entry-links">
            <Link className="entry-row" href="/rules?service=dayrehab">
              <span>基準省令</span><small>直接11条 + 第119条準用先 →</small>
            </Link>
            <Link className="entry-row" href="/notices?service=dayrehab">
              <span>基準解釈通知</span><small>公式旧HTML / 現行性GAP →</small>
            </Link>
            <Link className="entry-row" href="/services/dayrehab/remuneration">
              <span>報酬基準</span><small>42項目 / 現行性GAP →</small>
            </Link>
            <Link className="entry-row" href="/services/dayrehab/remuneration/guidance">
              <span>算定上の留意事項</span><small>33主項目 / 現行性GAP →</small>
            </Link>
          </div>
        </section>
      ) : (
        <>
          <div className="qa-search-summary">
            <p><strong>{results.length.toLocaleString("ja-JP")}件</strong> 見つかりました</p>
            <Link href="/services/dayrehab/search">条件をクリア</Link>
          </div>

          {layerOrder.map((layer) => {
            const rows = grouped.get(layer) || [];
            return (
              <section className="section" key={layer}>
                <h2>
                  {layerTitles[layer]} <span className="meta">({rows.length}件)</span>
                </h2>
                {rows.length ? (
                  <>
                    <ResultRows results={rows} />
                    {rows.length > LIMIT_PER_LAYER ? (
                      <p className="meta">
                        上位{LIMIT_PER_LAYER}件を表示しています。このレイヤーでは{rows.length}件一致しました。
                      </p>
                    ) : null}
                  </>
                ) : (
                  <p className="meta">該当なし</p>
                )}
              </section>
            );
          })}
        </>
      )}

      <p><Link href="/services/dayrehab">通所リハビリテーションへ戻る</Link></p>
    </article>
  );
}
