import Link from "next/link";
import questionsData from "../../data/questions.json";
import qaCorpusData from "../../data/qa-corpus.json";
import rulesData from "../../data/ordinance37-nodes.json";
import rulesReviewData from "../../data/ordinance37-review.json";
import feeNodesData from "../../data/remuneration-current-skeleton.json";
import feeTextsData from "../../data/remuneration-current-text.json";
import feeReviewData from "../../data/remuneration-review.json";
import { feeHref, getDefaultService } from "../../lib/service-catalog";
import { filterRecordsForService } from "../../lib/service-scope";
import { rankQuestionMatches } from "../../lib/question-search";

const questions = questionsData as Array<any>;
const qaCorpus = qaCorpusData as Array<any>;
const rules = rulesData as Array<any>;
const rulesReview = rulesReviewData as any;
const feeNodes = feeNodesData as Array<any>;
const feeTexts = feeTextsData as Array<any>;
const feeReview = feeReviewData as any;

const LIMIT = 8;

const normalize = (value: string) =>
  value.normalize("NFKC").toLowerCase().replace(/\s+/g, " ").trim();

const synonymGroups = [
  ["看護師", "看護職員", "准看護師"],
  ["生活相談員", "相談員"],
  ["ハンコ", "判子", "押印", "捺印", "印鑑"],
  ["サイン", "署名", "自署"],
  ["bcp", "業務継続計画"],
  ["デイサービス", "通所介護"],
  ["計画書", "通所介護計画", "計画"],
  ["機能訓練室", "機能訓練"],
  ["常勤換算", "常勤換算方法"],
] as const;

const expand = (term: string) => {
  const value = normalize(term);
  const group = synonymGroups.find((items) =>
    items.some((item) => normalize(item) === value)
  );
  return group ? group.map((item) => normalize(item)) : [value];
};

const hasAllTerms = (value: string, expandedTerms: string[][]) => {
  const haystack = normalize(value);
  return expandedTerms.every((alternatives) =>
    alternatives.some((term) => haystack.includes(term))
  );
};

const excerpt = (value: string, max = 180) => {
  const clean = value.replace(/\s+/g, " ").trim();
  return clean.length > max ? clean.slice(0, max) + "…" : clean;
};

const defaultService = getDefaultService();
const scopedRules = filterRecordsForService(
  defaultService.service_id,
  "ordinance37",
  rules,
  (node) => node.id,
);

export default async function SearchPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();
  const terms = normalize(query).split(" ").filter(Boolean);
  const expandedTerms = terms.map(expand);

  const reviewedRuleIds = new Set(
    (rulesReview.reviewed_articles || []).map((item: any) => item.article_id || item.id)
  );
  const reviewedFeeIds = new Set(
    (feeReview.reviewed_nodes || []).map((item: any) => item.fee_id)
  );
  const feeTextById = new Map(feeTexts.map((item) => [item.fee_id, item]));

  const questionMatches = query
    ? rankQuestionMatches(questions, query)
    : [];

  const articleNodes = scopedRules.filter((node) => node.node_type === "article");
  const ruleMatches = terms.length
    ? articleNodes.filter((article) => {
        const relatedText = scopedRules
          .filter((node) => node.article_num === article.article_num)
          .map((node) => node.official_text || "")
          .join(" ");
        return hasAllTerms(
          [article.article_title || "", article.caption || "", relatedText].join(" "),
          expandedTerms
        );
      })
    : [];

  const feeMatches = terms.length
    ? feeNodes
        .filter((node) => node.id !== "fee.dayservice.root")
        .filter((node) => {
          const text = feeTextById.get(node.id)?.official_text || "";
          return hasAllTerms(
            [node.title || "", (node.number_path || []).join(" "), text].join(" "),
            expandedTerms
          );
        })
    : [];

  const qaMatches = terms.length
    ? qaCorpus.filter((item) =>
        hasAllTerms(
          [
            item.scope,
            item.service_label,
            item.standard_label,
            item.topic,
            item.question,
            item.answer,
            item.issued_source,
            item.number,
          ]
            .filter(Boolean)
            .join(" "),
          expandedTerms
        )
      )
    : [];

  const total =
    questionMatches.length + ruleMatches.length + feeMatches.length + qaMatches.length;

  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">CROSS-SOURCE SEARCH</p>
      <h1>{defaultService.label}を横断検索</h1>
      <p className="lead">
        確認済みの実務ページ、基準省令、報酬告示、厚生労働省Q&Aを同じ語で探します。
        検索結果の表示と、内容の現行性確認は分けて扱います。
      </p>

      <form className="global-search-form" method="get" action="/search">
        <label>
          <span>キーワード</span>
          <input
            name="q"
            defaultValue={q}
            placeholder="例：看護職員、個別機能訓練、送迎"
            autoFocus
          />
        </label>
        <button type="submit">検索する</button>
      </form>

      {!terms.length ? (
        <div className="notice">
          キーワードを入力してください。確認済みの実務ページは自然文や代表的な言い換えも含めて順位付けし、基準省令などは複数語をすべて含む結果に絞り込みます。
        </div>
      ) : (
        <>
          <div className="qa-search-summary">
            <p><strong>{total.toLocaleString("ja-JP")}件</strong> 見つかりました</p>
            <Link href="/search">条件をクリア</Link>
          </div>

          <section className="section">
            <h2>確認済みの実務ページ <span className="meta">({questionMatches.length}件)</span></h2>
            {questionMatches.length ? (
              <div className="question-list">
                {questionMatches.slice(0, LIMIT).map((item) => (
                  <article className="question" key={item.slug}>
                    <span className="meta">{item.category}</span>
                    <Link href={"/questions/" + item.slug}>{item.title}</Link>
                    <span className={item.status === "verified" ? "status verified" : "status"}>
                      {item.status === "verified" ? "確認済み" : "根拠確認中"}
                    </span>
                  </article>
                ))}
              </div>
            ) : <p className="meta">該当なし</p>}
          </section>

          <section className="section">
            <h2>基準省令 <span className="meta">({ruleMatches.length}条)</span></h2>
            {ruleMatches.length ? (
              <div className="rules-list">
                {ruleMatches.slice(0, LIMIT).map((article) => (
                  <Link className="rule-row" href={"/rules/" + article.article_num} key={article.id}>
                    <span className="rule-number">{article.article_title}</span>
                    <span className="rule-title">{article.caption || "題名なし"}</span>
                    <span className="rule-status">
                      {reviewedRuleIds.has(article.id) ? "人手確認済み" : "機械取込・確認待ち"}
                    </span>
                  </Link>
                ))}
              </div>
            ) : <p className="meta">該当なし</p>}
            {ruleMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>報酬告示 <span className="meta">({feeMatches.length}項目)</span></h2>
            {feeMatches.length ? (
              <div className="fee-list">
                {feeMatches.slice(0, LIMIT).map((node) => {
                  const text = feeTextById.get(node.id)?.official_text || "";
                  return (
                    <Link className="fee-row fee-row-link" href={feeHref(defaultService.service_id, node.id)} key={node.id}>
                      <div>
                        <p className="meta">{(node.number_path || []).join(" / ")}</p>
                        <h3>{node.title}</h3>
                        {text ? <p className="meta">{excerpt(text, 120)}</p> : null}
                      </div>
                      <span className="fee-status">
                        {reviewedFeeIds.has(node.id) ? "人手確認済み" : "機械取込・確認待ち"}
                      </span>
                    </Link>
                  );
                })}
              </div>
            ) : <p className="meta">該当なし</p>}
            {feeMatches.length > LIMIT ? <p className="meta">上位{LIMIT}件を表示しています。</p> : null}
          </section>

          <section className="section">
            <h2>国Q&A <span className="meta">({qaMatches.length}件)</span></h2>
            {qaMatches.length ? (
              <>
                <div className="qa-list">
                  {qaMatches.slice(0, LIMIT).map((item) => (
                    <section className="qa-row" key={item.id}>
                      <div className="qa-row-head">
                        <p className="meta">{item.scope} ・ {item.standard_label || "基準種別なし"}</p>
                        <span className="corpus-status">収載済み・現行性未確認</span>
                      </div>
                      {item.topic ? <p className="qa-topic">{item.topic}</p> : null}
                      <h2>{item.question}</h2>
                      <p className="qa-answer">{excerpt(item.answer)}</p>
                    </section>
                  ))}
                </div>
                <p>
                  <Link href={"/qa?q=" + encodeURIComponent(query)}>
                    国Q&A検索で全{qaMatches.length.toLocaleString("ja-JP")}件を見る →
                  </Link>
                </p>
              </>
            ) : <p className="meta">該当なし</p>}
          </section>
        </>
      )}
    </article>
  );
}
