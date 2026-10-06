import Link from "next/link";
import careNodesData from "../../../data/care-insurance-act-nodes.json";
import ordinanceNodesData from "../../../data/ordinance37-nodes.json";
import qaCorpusData from "../../../data/qa-corpus.json";
import { publicNoticeRecords } from "../../../lib/notice-database";
import { databaseSearchExcerpt, rankDatabaseSearch } from "../../../lib/database-search";
import {
  PROGRESSIVE_SOURCE_FAMILY,
  UNIT_PRICE_SOURCE_FAMILY,
  filterProgressivePublishedRules,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
  listProgressivePublicationServicesAcrossFamilies,
} from "../../../lib/publication-policy";
import { publicVerificationLabel } from "../../../lib/public-verification";
import { listServices } from "../../../lib/service-catalog";
import { publicServiceNavigationGroups } from "../../../lib/service-navigation-groups";

const careNodes = careNodesData as Array<any>;
const ordinanceNodes = ordinanceNodesData as Array<any>;
const qaCorpus = qaCorpusData as Array<any>;
const LIMIT = 10;

const articleSearchFields = (article: any, nodes: Array<any>) => {
  const articleNodes = nodes.filter(
    (node) => node.article_num === article.article_num,
  );
  return [
    {
      value: articleNodes
        .map((node) => node.official_text)
        .filter(Boolean)
        .join(" "),
      weight: 10,
    },
    {
      value: [article.article_title, article.caption].filter(Boolean).join(" "),
      weight: 9,
    },
    {
      value: [...(article.path || []), article.service_scope]
        .filter(Boolean)
        .join(" "),
      weight: 5,
    },
    {
      value: article.source_locator || "",
      weight: 2,
    },
  ];
};

const filterHref = (query: string, serviceId?: string) => {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (serviceId) params.set("service", serviceId);
  const suffix = params.toString();
  return "/databases/search" + (suffix ? "?" + suffix : "");
};

export default async function DatabaseSearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; service?: string }>;
}) {
  const { q = "", service = "" } = await searchParams;
  const query = q.trim();
  const requestedService = service.trim();
  const progressiveServices =
    listProgressivePublicationServicesAcrossFamilies();
  const progressiveServiceIds = new Set(
    progressiveServices.map((item) => item.service_id),
  );
  const progressiveServiceById = new Map(
    progressiveServices.map((item) => [item.service_id, item]),
  );
  const selectedService = progressiveServiceById.get(requestedService);
  const requestedCatalogService = listServices().find(
    (item) => item.service_id === requestedService,
  );
  const groupedProgressiveServices = publicServiceNavigationGroups(
    progressiveServiceIds,
  );
  const selectedPrimaryFamily = selectedService?.source_families.includes(
    PROGRESSIVE_SOURCE_FAMILY,
  )
    ? PROGRESSIVE_SOURCE_FAMILY
    : selectedService?.source_families[0];
  const publicationTrust =
    selectedService && selectedPrimaryFamily
      ? getProgressivePublicationTrust(
          selectedService.service_id,
          selectedPrimaryFamily,
        )
      : null;
  const selectedSourceNodes =
    selectedService &&
    selectedService.source_families.includes(
      PROGRESSIVE_SOURCE_FAMILY,
    )
      ? (getProgressiveSourceRecords(
          selectedService.service_id,
          PROGRESSIVE_SOURCE_FAMILY,
        ) as Array<any>)
      : ordinanceNodes;
  const selectedUnitPriceRecords =
    selectedService &&
    selectedService.source_families.includes(UNIT_PRICE_SOURCE_FAMILY)
      ? (getProgressiveSourceRecords(
          selectedService.service_id,
          UNIT_PRICE_SOURCE_FAMILY,
        ) as Array<any>)
      : [];

  const lawArticles = careNodes.filter((node) => node.node_type === "article");
  const ordinanceArticles = ordinanceNodes.filter(
    (node) => node.node_type === "article",
  );
  const selectedSourceArticles = selectedSourceNodes.filter(
    (node) => node.node_type === "article",
  );

  const scopedOrdinanceArticles = requestedService
    ? selectedService?.source_families.includes(
        PROGRESSIVE_SOURCE_FAMILY,
      )
      ? filterProgressivePublishedRules(
          selectedService.service_id,
          selectedSourceArticles,
          (article) => article.id,
        )
      : []
    : ordinanceArticles;

  const lawMatches = requestedService
    ? []
    : rankDatabaseSearch(
        lawArticles,
        query,
        (article) => articleSearchFields(article, careNodes),
      );
  const ordinanceMatches = rankDatabaseSearch(
    scopedOrdinanceArticles,
    query,
    (article) => articleSearchFields(article, selectedSourceNodes),
  );
  const noticeMatches = requestedService
    ? []
    : rankDatabaseSearch(
        publicNoticeRecords,
        query,
        (notice) => [
          { value: notice.body_text, weight: 10 },
          { value: notice.title, weight: 9 },
          {
            value: [notice.service_label, notice.section]
              .filter(Boolean)
              .join(" "),
            weight: 5,
          },
          { value: (notice.number_path || []).join(" "), weight: 2 },
        ],
      );
  const qaMatches = requestedService
    ? []
    : rankDatabaseSearch(
        qaCorpus,
        query,
        (item) => [
          { value: item.question || "", weight: 10 },
          { value: item.answer || "", weight: 8 },
          { value: item.topic || "", weight: 6 },
          {
            value: [
              item.scope,
              item.service_label,
              item.current_service_scope,
            ]
              .filter(Boolean)
              .join(" "),
            weight: 5,
          },
          { value: item.standard_label || "", weight: 3 },
          {
            value: [item.issued_source, item.number]
              .filter(Boolean)
              .join(" "),
            weight: 1,
          },
        ],
      );

  const unitPriceMatches =
    selectedUnitPriceRecords.length
      ? rankDatabaseSearch(
          selectedUnitPriceRecords,
          query,
          (item) => [
            {
              value: [
                item.region_class,
                item.service,
                item.ratio_text,
              ]
                .filter(Boolean)
                .join(" "),
              weight: 10,
            },
            {
              value: [
                item.ratio_per_thousand,
                item.unit_price_yen,
              ]
                .filter((value) => value !== undefined)
                .join(" "),
              weight: 7,
            },
            {
              value: item.source_locator || "",
              weight: 2,
            },
          ],
        )
      : [];

  const total =
    lawMatches.length +
    ordinanceMatches.length +
    noticeMatches.length +
    qaMatches.length +
    unitPriceMatches.length;

  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">DATABASE-WIDE SEARCH</p>
      <h1>介護制度DBを横断検索</h1>
      <p className="lead">
        {selectedService
          ? `${selectedService.label}について、公開条件を満たした一次資料をsource family横断で検索します。`
          : "サービスを先に選ばず、介護保険法・基準省令・公開済みの基準解釈通知・厚生労働省Q&Aを同じキーワードで探します。各結果から本文と出典へ進めます。対象範囲や現行性は、必要なときに各ページの確認情報で確認できます."}
      </p>

      <div className="notice">
        {selectedService && publicationTrust ? (
          <>
            <strong>{selectedService.label}の公開条件を満たした一次資料を検索しています。</strong><br />
            source identity・現行性・適用範囲を確認できたpublication unitだけを対象とし、未確認の制度間関係や解釈は含めません。
            <a href={publicationTrust.source_url} target="_blank" rel="noreferrer"> 公式原文</a>
          </>
        ) : requestedService ? (
          <>
            <strong>
              {requestedCatalogService?.label || "指定したサービス"}のサービス別絞り込みは現在公開準備中です。
            </strong><br />
            DB全体では名称やキーワードから確認できます。
            {requestedCatalogService ? (
              <>
                {" "}
                <Link href={filterHref(requestedCatalogService.label)}>
                  このサービス名でDB全体を検索
                </Link>
              </>
            ) : null}
          </>
        ) : (
          <>
            <strong>報酬基準と算定上の留意事項は、この全体検索には混ぜません。</strong><br />
            サービスごとに構造と確認状態が異なるため、DB一覧からサービス別の公開データへ進んでください。
          </>
        )}
      </div>

      <nav className="rules-filter" aria-label="公開済みサービスで検索を絞り込む">
        <Link
          className={!requestedService ? "rules-filter-active" : ""}
          href={filterHref(query)}
        >
          全体
        </Link>
        {groupedProgressiveServices.map((group) => (
          <span key={group.id}>
            <span className="meta">{group.label}</span>
            {group.units.map((unit) => (
              <span key={unit.service_ids.join("|")}>
                {unit.services.map((item) => (
                  <Link
                    className={
                      requestedService === item.service_id
                        ? "rules-filter-active"
                        : ""
                    }
                    href={filterHref(query, item.service_id)}
                    key={item.service_id}
                  >
                    {item.label}
                  </Link>
                ))}
              </span>
            ))}
          </span>
        ))}
      </nav>

      <form className="global-search-form" method="get" action="/databases/search">
        {selectedService ? (
          <input type="hidden" name="service" value={selectedService.service_id} />
        ) : null}
        <label>
          <span>キーワード</span>
          <input
            name="q"
            defaultValue={q}
            placeholder="例：業務継続計画、認知症、通所リハ"
            autoFocus
          />
        </label>
        <button type="submit">検索する</button>
      </form>

      {!query ? (
        <div className="notice">
          キーワードを入力してください。複数語を入力した場合は、すべての語に一致する記録へ絞り込みます。
        </div>
      ) : (
        <>
          <div className="qa-search-summary">
            <p><strong>{total.toLocaleString("ja-JP")}件</strong> 見つかりました</p>
            <Link href={selectedService ? filterHref("", selectedService.service_id) : "/databases/search"}>
              キーワードをクリア
            </Link>
          </div>
          <p className="meta">
            各DB内では、一次資料の本文・質問文への直接一致を優先し、次に見出し、サービス・トピック、出典情報の順で関連度を判定します。
            未確認の制度間関係や内部の確認スコアは順位付けに使いません。
          </p>

          {total === 0 ? (
            <div className="notice">
              <strong>現在公開している範囲では一致する資料が見つかりませんでした。</strong><br />
              資料そのものが存在しないことを意味しません。語を変えて検索するか、DB一覧・公式資料から確認してください。
              <p>
                <Link href="/databases">DB一覧を見る →</Link>
                {" / "}
                <Link href="/sources">公式の根拠資料を見る →</Link>
              </p>
            </div>
          ) : null}

          <section className="section">
            <h2>介護保険法 <span className="meta">({lawMatches.length}条)</span></h2>
            {lawMatches.length ? (
              <div className="law-list">
                {lawMatches.slice(0, LIMIT).map((article) => (
                  <Link className="law-row" href={"/law/" + article.article_num} key={article.id}>
                    <span className="law-number">{article.article_title}</span>
                    <span className="law-title">{article.caption || "条文"}</span>
                    <span className="law-status">公式本文</span>
                  </Link>
                ))}
              </div>
            ) : <p className="meta">現在公開している範囲では一致なし</p>}
            {lawMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>基準省令 <span className="meta">({ordinanceMatches.length}条)</span></h2>
            {ordinanceMatches.length ? (
              <div className="rules-list">
                {ordinanceMatches.slice(0, LIMIT).map((article) => (
                  <Link
                    className="rule-row"
                    href={
                      "/rules/" +
                      article.article_num +
                      (selectedService
                        ? "?service=" + encodeURIComponent(selectedService.service_id)
                        : "")
                    }
                    key={article.id}
                  >
                    <span className="rule-number">{article.article_title}</span>
                    <span className="rule-title">{article.caption || "題名なし"}</span>
                    <span className="rule-status">
                      {selectedService ? "本文・適用範囲を確認済み" : "公式本文"}
                    </span>
                  </Link>
                ))}
              </div>
            ) : <p className="meta">現在公開している範囲では一致なし</p>}
            {ordinanceMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>基準解釈通知 <span className="meta">({noticeMatches.length}件)</span></h2>
            {noticeMatches.length ? (
              <div className="source-chain">
                {noticeMatches.slice(0, LIMIT).map((notice) => (
                  <article className="source-card" key={notice.id}>
                    <p className="meta">{notice.service_label} / {notice.number_path.join(" / ")}</p>
                    <h3>
                      <Link href={"/notices?service=" + notice.service_id + "#" + notice.id}>
                        {notice.title}
                      </Link>
                    </h3>
                    <p>{databaseSearchExcerpt(notice.body_text, query)}</p>
                    <p className="meta">
                      本文：{publicVerificationLabel(notice.content_verification, "content")} / 現行性：{publicVerificationLabel(notice.currentness_state, "currentness")} / 人手確認：{publicVerificationLabel(notice.human_review_state, "human")}
                    </p>
                  </article>
                ))}
              </div>
            ) : <p className="meta">現在公開している範囲では一致なし</p>}
            {noticeMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>国Q&A <span className="meta">({qaMatches.length}件)</span></h2>
            {qaMatches.length ? (
              <>
                <div className="qa-list">
                  {qaMatches.slice(0, LIMIT).map((item) => (
                    <section className="qa-row" key={item.id}>
                      <div className="qa-row-head">
                        <p className="meta">{item.service_label || item.scope} ・ {item.standard_label || "基準種別なし"}</p>
                        <span className="corpus-status">厚生労働省Q&A</span>
                      </div>
                      {item.topic ? <p className="qa-topic">{item.topic}</p> : null}
                      <h2><Link href={"/qa/" + encodeURIComponent(item.id)}>{item.question}</Link></h2>
                      <p className="qa-answer">{databaseSearchExcerpt(item.answer, query)}</p>
                    </section>
                  ))}
                </div>
                <p>
                  <Link href={"/qa?q=" + encodeURIComponent(query)}>
                    国Q&A DBで全結果を見る →
                  </Link>
                </p>
              </>
            ) : <p className="meta">現在公開している範囲では一致なし</p>}
          </section>

          {selectedService?.source_families.includes(
            UNIT_PRICE_SOURCE_FAMILY,
          ) ? (
            <section className="section">
              <h2>一単位単価 <span className="meta">({unitPriceMatches.length}件)</span></h2>
              {unitPriceMatches.length ? (
                <div className="unit-price-table">
                  {unitPriceMatches.slice(0, LIMIT).map((item) => (
                    <Link
                      className="unit-price-row"
                      href="/fees/unit-price"
                      key={item.id}
                    >
                      <strong>{item.region_class}</strong>
                      <span>{Number(item.unit_price_yen).toFixed(2)}円 / 単位</span>
                      <span>{item.ratio_text}</span>
                    </Link>
                  ))}
                </div>
              ) : (
                <p className="meta">現在公開している範囲では一致なし</p>
              )}
              {unitPriceMatches.length > LIMIT ? (
                <p className="meta">上位{LIMIT}件を表示しています。</p>
              ) : null}
            </section>
          ) : null}

          <section className="section">
            <h2>次の探し方</h2>
            <p>
              一次資料を検索しても判断点が整理しにくい場合は、実務上の目的から関連DBへ進めるガイドも利用できます。
            </p>
            <p><Link href="/guide">実務ガイドから探す →</Link></p>
          </section>
        </>
      )}

      <section className="section">
        <h2>サービス固有DB</h2>
        <p>報酬基準・算定上の留意事項はサービス別に確認状態を保持しています。</p>
        <p><Link href="/databases#remuneration">報酬基準DBへ →</Link></p>
        <p><Link href="/databases#fee-guidance">算定上の留意事項へ →</Link></p>
      </section>
    </article>
  );
}
