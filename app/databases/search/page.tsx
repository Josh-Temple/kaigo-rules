import Link from "next/link";
import careNodesData from "../../../data/care-insurance-act-nodes.json";
import ordinanceNodesData from "../../../data/ordinance37-nodes.json";
import qaCorpusData from "../../../data/qa-corpus.json";
import { publicNoticeRecords } from "../../../lib/notice-database";
import { rankDatabaseSearch } from "../../../lib/database-search";

const careNodes = careNodesData as Array<any>;
const ordinanceNodes = ordinanceNodesData as Array<any>;
const qaCorpus = qaCorpusData as Array<any>;
const LIMIT = 10;

const excerpt = (value: string, max = 180) => {
  const clean = String(value || "").replace(/\s+/g, " ").trim();
  return clean.length > max ? clean.slice(0, max) + "…" : clean;
};

const articleSearchFields = (article: any, nodes: Array<any>) => {
  const articleNodes = nodes.filter(
    (node) => node.article_num === article.article_num,
  );
  return [
    {
      value: [article.article_title, article.caption].filter(Boolean).join(" "),
      weight: 8,
    },
    {
      value: [
        ...(article.path || []),
        article.service_scope,
        article.source_locator,
      ]
        .filter(Boolean)
        .join(" "),
      weight: 4,
    },
    {
      value: articleNodes
        .map((node) => node.official_text)
        .filter(Boolean)
        .join(" "),
      weight: 1,
    },
  ];
};

export default async function DatabaseSearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();

  const lawArticles = careNodes.filter((node) => node.node_type === "article");
  const ordinanceArticles = ordinanceNodes.filter(
    (node) => node.node_type === "article",
  );

  const lawMatches = rankDatabaseSearch(
    lawArticles,
    query,
    (article) => articleSearchFields(article, careNodes),
  );
  const ordinanceMatches = rankDatabaseSearch(
    ordinanceArticles,
    query,
    (article) => articleSearchFields(article, ordinanceNodes),
  );
  const noticeMatches = rankDatabaseSearch(
    publicNoticeRecords,
    query,
    (notice) => [
      { value: notice.title, weight: 8 },
      {
        value: [notice.service_label, notice.section]
          .filter(Boolean)
          .join(" "),
        weight: 4,
      },
      { value: (notice.number_path || []).join(" "), weight: 2 },
      { value: notice.body_text, weight: 1 },
    ],
  );
  const qaMatches = rankDatabaseSearch(
    qaCorpus,
    query,
    (item) => [
      { value: item.question || "", weight: 8 },
      { value: item.topic || "", weight: 6 },
      {
        value: [
          item.scope,
          item.service_label,
          item.current_service_scope,
        ]
          .filter(Boolean)
          .join(" "),
        weight: 4,
      },
      { value: item.standard_label || "", weight: 3 },
      { value: item.answer || "", weight: 1 },
      {
        value: [item.issued_source, item.number]
          .filter(Boolean)
          .join(" "),
        weight: 0.5,
      },
    ],
  );

  const total =
    lawMatches.length +
    ordinanceMatches.length +
    noticeMatches.length +
    qaMatches.length;

  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">DATABASE-WIDE SEARCH</p>
      <h1>介護制度DBを横断検索</h1>
      <p className="lead">
        サービスを先に選ばず、介護保険法・基準省令・公開済みの基準解釈通知・厚生労働省Q&Aを同じキーワードで探します。
        表示されること自体は、各サービスへの適用確認や現行性・人手確認を意味しません。
      </p>

      <div className="notice">
        <strong>報酬基準と算定上の留意事項は、この全体検索には混ぜません。</strong><br />
        サービスごとに構造と確認状態が異なるため、DB一覧からサービス別の公開データへ進んでください。
      </div>

      <form className="global-search-form" method="get" action="/databases/search">
        <label>
          <span>キーワード</span>
          <input
            name="q"
            defaultValue={q}
            placeholder="例：業務継続計画、認知症、通所リハ"
            autoFocus
          />
        </label>
        <button type="submit">全体から検索する</button>
      </form>

      {!query ? (
        <div className="notice">
          キーワードを入力してください。複数語を入力した場合は、すべての語に一致する記録へ絞り込みます。
        </div>
      ) : (
        <>
          <div className="qa-search-summary">
            <p><strong>{total.toLocaleString("ja-JP")}件</strong> 見つかりました</p>
            <Link href="/databases/search">条件をクリア</Link>
          </div>
          <p className="meta">
            各DB内では、見出し・質問文・トピックなどの直接一致を本文中の一致より優先した関連度順で表示します。
          </p>

          <section className="section">
            <h2>介護保険法 <span className="meta">({lawMatches.length}条)</span></h2>
            {lawMatches.length ? (
              <div className="law-list">
                {lawMatches.slice(0, LIMIT).map((article) => (
                  <Link className="law-row" href={"/law/" + article.article_num} key={article.id}>
                    <span className="law-number">{article.article_title}</span>
                    <span className="law-title">{article.caption || "条文"}</span>
                    <span className="law-status">共有コーパス</span>
                  </Link>
                ))}
              </div>
            ) : <p className="meta">一致なし</p>}
            {lawMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>基準省令 <span className="meta">({ordinanceMatches.length}条)</span></h2>
            {ordinanceMatches.length ? (
              <div className="rules-list">
                {ordinanceMatches.slice(0, LIMIT).map((article) => (
                  <Link className="rule-row" href={"/rules/" + article.article_num} key={article.id}>
                    <span className="rule-number">{article.article_title}</span>
                    <span className="rule-title">{article.caption || "題名なし"}</span>
                    <span className="rule-status">共有コーパス</span>
                  </Link>
                ))}
              </div>
            ) : <p className="meta">一致なし</p>}
            {ordinanceMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>基準解釈通知 <span className="meta">({noticeMatches.length}件)</span></h2>
            {noticeMatches.length ? (
              <div className="source-chain">
                {noticeMatches.slice(0, LIMIT).map((notice) => (
                  <article className="source-card" key={notice.id}>
                    <p className="meta">{notice.service_label} / {notice.number_path.join(" / ")}</p>
                    <h3><Link href={"/notices#" + notice.id}>{notice.title}</Link></h3>
                    <p>{excerpt(notice.body_text)}</p>
                    <p className="meta">
                      本文照合：{notice.content_verification} / 現行性：{notice.currentness_state} / 人手確認：{notice.human_review_state}
                    </p>
                  </article>
                ))}
              </div>
            ) : <p className="meta">一致なし</p>}
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
                        <span className="corpus-status">収載済み・現行性未確認</span>
                      </div>
                      {item.topic ? <p className="qa-topic">{item.topic}</p> : null}
                      <h2><Link href={"/qa/" + encodeURIComponent(item.id)}>{item.question}</Link></h2>
                      <p className="qa-answer">{excerpt(item.answer)}</p>
                    </section>
                  ))}
                </div>
                <p>
                  <Link href={"/qa?q=" + encodeURIComponent(query)}>
                    国Q&A DBで全結果を見る →
                  </Link>
                </p>
              </>
            ) : <p className="meta">一致なし</p>}
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
