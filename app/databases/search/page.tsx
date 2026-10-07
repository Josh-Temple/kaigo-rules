import { pageMetadata } from "../../../lib/site-metadata";

export const metadata = pageMetadata("制度DB横断検索", "介護保険法、基準省令、通知、Q&Aなどの公開資料を横断検索します。", "/databases/search", false);

import Link from "next/link";
import careNodesData from "../../../data/care-insurance-act-nodes.json";
import ordinanceNodesData from "../../../data/ordinance37-nodes.json";
import qaCorpusData from "../../../data/qa-corpus.json";
import unitPriceRatesData from "../../../data/unit-price-dayservice.json";
import unitPriceMetaData from "../../../data/unit-price-dayservice-meta.json";
import { publicNoticeRecords } from "../../../lib/notice-database";
import { databaseSearchExcerpt, rankDatabaseSearch } from "../../../lib/database-search";
import {
  filterProgressivePublishedRules,
  getProgressivePublicationTrust,
  getProgressiveSourceRecords,
} from "../../../lib/publication-policy";
import {
  DELEGATED_REMUNERATION_SOURCE_FAMILY,
  GOVERNING_STANDARDS_SOURCE_FAMILY,
  UNIT_PRICE_SOURCE_FAMILY,
  publicSourceFamiliesForService,
} from "../../../lib/public-source-navigation";
import { verifiedRelatedPrimarySources } from "../../../lib/verified-related-sources";
import { publicVerificationLabel } from "../../../lib/public-verification";
import { listServices } from "../../../lib/service-catalog";
import { publicServiceNavigationGroups } from "../../../lib/service-navigation-groups";

const careNodes = careNodesData as Array<any>;
const ordinanceNodes = ordinanceNodesData as Array<any>;
const qaCorpus = qaCorpusData as Array<any>;
const unitPriceRates = unitPriceRatesData as Array<any>;
const unitPriceMeta = unitPriceMetaData as any;
const LIMIT = 10;

const practicalTopicSearches = [
  { id: "staffing", label: "人員基準", query: "人員" },
  { id: "equipment", label: "設備基準", query: "設備" },
  { id: "operations", label: "運営基準", query: "運営" },
  { id: "remuneration", label: "報酬・算定", query: "算定" },
  { id: "unit-price", label: "地域区分・単価", query: "地域区分" },
  { id: "designation", label: "指定", query: "指定" },
  { id: "filing", label: "更新・届出", query: "届出" },
] as const;

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

const feedbackHref = (query: string, serviceLabel?: string) => {
  const params = new URLSearchParams();
  params.set("from", "/databases/search");
  if (query) params.set("q", query);
  if (serviceLabel) params.set("service", serviceLabel);
  return "/feedback?" + params.toString();
};

export default async function DatabaseSearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string; service?: string }>;
}) {
  const { q = "", service = "" } = await searchParams;
  const query = q.trim();
  const requestedService = service.trim();
  const catalogServices = listServices();
  const publicFamiliesByService = new Map(
    catalogServices.map((item) => [
      item.service_id,
      publicSourceFamiliesForService(item.service_id),
    ]),
  );
  const progressiveServiceIds = new Set(
    catalogServices
      .filter((item) => (publicFamiliesByService.get(item.service_id) || []).length > 0)
      .map((item) => item.service_id),
  );
  const requestedCatalogService = catalogServices.find(
    (item) => item.service_id === requestedService,
  );
  const selectedPublicFamilies = requestedCatalogService
    ? publicFamiliesByService.get(requestedCatalogService.service_id) || []
    : [];
  const selectedService =
    requestedCatalogService && selectedPublicFamilies.length > 0
      ? {
          service_id: requestedCatalogService.service_id,
          label: requestedCatalogService.label,
        }
      : undefined;
  const groupedProgressiveServices = publicServiceNavigationGroups(
    progressiveServiceIds,
  );
  const standardsPublished = selectedPublicFamilies.some(
    (item) => item.source_family === GOVERNING_STANDARDS_SOURCE_FAMILY,
  );
  const publicationTrust =
    selectedService && standardsPublished
      ? getProgressivePublicationTrust(selectedService.service_id)
      : null;
  const selectedSourceNodes =
    selectedService && standardsPublished
      ? (getProgressiveSourceRecords(selectedService.service_id) as Array<any>)
      : ordinanceNodes;

  const lawArticles = careNodes.filter((node) => node.node_type === "article");
  const ordinanceArticles = ordinanceNodes.filter(
    (node) => node.node_type === "article",
  );
  const selectedSourceArticles = selectedSourceNodes.filter(
    (node) => node.node_type === "article",
  );

  const scopedOrdinanceArticles = requestedService
    ? selectedService && standardsPublished
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

  const dayserviceUnitPricePublished = publicSourceFamiliesForService(
    "dayservice",
  ).some((item) => item.source_family === UNIT_PRICE_SOURCE_FAMILY);
  const unitPriceVisible = requestedService
    ? requestedService === "dayservice" &&
      selectedPublicFamilies.some(
        (item) => item.source_family === UNIT_PRICE_SOURCE_FAMILY,
      )
    : dayserviceUnitPricePublished;
  const unitPriceMatches = unitPriceVisible
    ? rankDatabaseSearch(unitPriceRates, query, (row) => [
        {
          value: [
            row.ratio_text,
            row.unit_price_yen ? String(row.unit_price_yen) + "円" : "",
          ]
            .filter(Boolean)
            .join(" "),
          weight: 10,
        },
        { value: row.region_class || "", weight: 9 },
        { value: row.service || "", weight: 5 },
        { value: "一単位単価 地域区分 単価", weight: 3 },
      ])
    : [];

  const delegatedCriteriaPublished = Boolean(
    selectedService &&
      selectedPublicFamilies.some(
        (item) =>
          item.source_family ===
          DELEGATED_REMUNERATION_SOURCE_FAMILY,
      ),
  );
  const delegatedCriteriaRecords =
    delegatedCriteriaPublished && selectedService
      ? (getProgressiveSourceRecords(
          selectedService.service_id,
          DELEGATED_REMUNERATION_SOURCE_FAMILY,
        ) as Array<any>)
      : [];
  const delegatedCriteriaMatches =
    delegatedCriteriaPublished
      ? rankDatabaseSearch(
          delegatedCriteriaRecords,
          query,
          (record) => [
            {
              value: record.official_text || "",
              weight: 10,
            },
            {
              value: record.heading || "",
              weight: 9,
            },
            {
              value: [
                record.item_label,
                record.source_document_title,
              ]
                .filter(Boolean)
                .join(" "),
              weight: 5,
            },
            {
              value: record.source_locator || "",
              weight: 2,
            },
          ],
        )
      : [];

  const total =
    lawMatches.length +
    ordinanceMatches.length +
    unitPriceMatches.length +
    delegatedCriteriaMatches.length +
    noticeMatches.length +
    qaMatches.length;

  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">DATABASE-WIDE SEARCH</p>
      <h1>介護制度DBを横断検索</h1>
      <p className="lead">
        {selectedService
          ? `${selectedService.label}について、現在公開している一次資料を資料種別ごとに検索します。`
          : "サービスを先に選ばず、介護保険法・基準省令・公開済みの基準解釈通知・厚生労働省Q&Aに加え、公開条件を満たした追加資料を同じキーワードで探します。各結果から本文と出典へ進めます。"}
      </p>

      <div className="notice">
        {selectedService ? (
          <>
            <strong>{selectedService.label}で現在公開している資料</strong><br />
            {selectedPublicFamilies.map((item, index) => (
              <span key={item.source_family}>
                {index > 0 ? " / " : ""}
                <Link href={item.href}>{item.label}</Link>
              </span>
            ))}
            <br />
            公開条件を満たした資料だけを表示します。未確認の制度間関係や解釈は検索対象に含めません。
            {publicationTrust?.source_url ? (
              <a href={publicationTrust.source_url} target="_blank" rel="noreferrer"> 基準省令の公式原文</a>
            ) : null}
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

      <section className="section">
        <h2>実務テーマから探す</h2>
        <p className="meta">
          内部の資料分類を知らなくても、確認したい実務テーマから公開済みDBを検索できます。
          サービスを選択している場合は、その公開範囲を維持します。
        </p>
        <nav className="rules-filter" aria-label="実務テーマから検索">
          {practicalTopicSearches.map((item) => (
            <Link
              className={query === item.query ? "rules-filter-active" : ""}
              href={filterHref(item.query, selectedService?.service_id)}
              key={item.id}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </section>

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
                {" / "}
                <Link href="/guide">実務ガイドから探す →</Link>
                {" / "}
                <Link href={feedbackHref(query, selectedService?.label)}>見つからない資料を知らせる →</Link>
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
            <h2>一単位単価・地域区分 <span className="meta">({unitPriceMatches.length}件)</span></h2>
            {unitPriceMatches.length ? (
              <div className="source-chain">
                {unitPriceMatches.slice(0, LIMIT).map((row) => (
                  <article className="source-card" key={row.id}>
                    <p className="meta">通所介護 / 一単位単価・地域区分</p>
                    <h3>
                      <Link href="/fees/unit-price">{row.region_class}</Link>
                    </h3>
                    <p>
                      {row.ratio_text} / 1単位 {Number(row.unit_price_yen).toFixed(2)}円
                    </p>
                    <p className="meta">
                      現行性：公開条件を満たした現行資料
                      {unitPriceMeta.source_urls?.[0] ? (
                        <>
                          {" / "}
                          <a href={unitPriceMeta.source_urls[0]} target="_blank" rel="noreferrer">
                            厚生労働省の告示原文
                          </a>
                        </>
                      ) : null}
                    </p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="meta">
                {unitPriceVisible
                  ? "現在公開している範囲では一致なし"
                  : "この資料種別は、公開条件を満たしたサービスだけ検索対象になります。"}
              </p>
            )}
            {unitPriceMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>
              報酬算定基準（別告示）
              <span className="meta">
                ({delegatedCriteriaMatches.length}件)
              </span>
            </h2>
            {delegatedCriteriaMatches.length && selectedService ? (
              <div className="source-chain">
                {delegatedCriteriaMatches
                  .slice(0, LIMIT)
                  .map((record) => {
                    const related =
                      verifiedRelatedPrimarySources(
                        selectedService.service_id,
                        DELEGATED_REMUNERATION_SOURCE_FAMILY,
                        record,
                      );
                    return (
                      <article
                        className="source-card"
                        key={record.id}
                      >
                        <p className="meta">
                          {selectedService.label} /{" "}
                          {record.source_document_title ||
                            "報酬算定基準"}
                        </p>
                        <h3>
                          <Link
                            href={
                              "/fees/criteria?service=" +
                              encodeURIComponent(
                                selectedService.service_id,
                              ) +
                              "#" +
                              record.id
                            }
                          >
                            {record.heading ||
                              record.item_label ||
                              record.id}
                          </Link>
                        </h3>
                        <p>
                          {databaseSearchExcerpt(
                            record.official_text || "",
                            query,
                          )}
                        </p>
                        <p className="meta">
                          <a
                            href={record.source_url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            厚生労働省の原文
                          </a>
                          {record.source_locator
                            ? " / " + record.source_locator
                            : ""}
                        </p>
                        {related.length ? (
                          <p className="meta">
                            関連する一次資料：{" "}
                            {related.map((relation, index) => (
                              <span
                                key={
                                  relation.related_record_id
                                }
                              >
                                {index > 0 ? " / " : ""}
                                <Link href={relation.href}>
                                  {relation.title}
                                </Link>
                              </span>
                            ))}
                          </p>
                        ) : null}
                      </article>
                    );
                  })}
              </div>
            ) : (
              <p className="meta">
                {delegatedCriteriaPublished
                  ? "現在公開している範囲では一致なし"
                  : "この資料種別は、公開条件を満たしたサービスだけ検索対象になります。"}
              </p>
            )}
            {delegatedCriteriaMatches.length > LIMIT ? (
              <p className="meta">
                上位{LIMIT}件を表示しています。
              </p>
            ) : null}
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

          <section className="section">
            <h2>次の探し方</h2>
            <p>
              一次資料を検索しても判断点が整理しにくい場合は、実務上の目的から関連DBへ進めるガイドも利用できます。
            </p>
            <p><Link href="/guide">実務ガイドから探す →</Link></p>
          </section>

          <section className="section">
            <p className="eyebrow">制度確認の次に</p>
            <h2>制度上の要件を確認した後、業務の見直しへ</h2>
            <p>
              介護ルールは、法令・基準・通知・報酬・Q&amp;Aから「制度上どうなっているか」を確認するためのサイトです。
              制度を確認したうえで、情報の探し方や記録・文書作業そのものを見直す場合は、介護業務改善で改善の選択肢と小さな試し方を確認できます。
            </p>
            <div className="entry-links">
              <a
                className="entry-row"
                href="https://ops-site-pi.vercel.app/issues/information-search"
                target="_blank"
                rel="noreferrer"
              >
                <span>必要な情報を探すのに時間がかかる</span>
                <small>介護業務改善で見る ↗</small>
              </a>
              <a
                className="entry-row"
                href="https://ops-site-pi.vercel.app/issues/documentation"
                target="_blank"
                rel="noreferrer"
              >
                <span>記録・文書作成に時間がかかる</span>
                <small>介護業務改善で見る ↗</small>
              </a>
            </div>
            <p className="meta">
              介護業務改善では制度適合を確定しません。制度上の判断が必要な場合は、介護ルールの検証状態と原典へ戻って確認してください。
            </p>
          </section>
        </>
      )}

      <section className="section">
        <h2>サービス固有DB</h2>
        <p>報酬基準・算定上の留意事項・一単位単価などは、資料種別ごとの公開条件を満たした範囲から順に案内します。</p>
        <p><Link href="/databases#remuneration">報酬基準DBへ →</Link></p>
        <p><Link href="/databases#fee-guidance">算定上の留意事項へ →</Link></p>
      </section>
    </article>
  );
}
