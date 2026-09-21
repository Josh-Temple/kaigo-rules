import Link from "next/link";
import { notFound } from "next/navigation";
import questions from "../../../data/questions.json";
import sources from "../../../data/sources.json";
import ruleNodes from "../../../data/rule-nodes.json";

export function generateStaticParams() {
  return questions.map((q) => ({ slug: q.slug }));
}

export default async function QuestionPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const question = questions.find((q) => q.slug === slug);
  if (!question) notFound();

  const isVerified = question.status === "verified";
  const linkedRules = isVerified && "rule_node_ids" in question
    ? ruleNodes.filter((node) => question.rule_node_ids?.includes(node.id))
    : [];

  return (
    <article className="answer-page">
      <p className="eyebrow">通所介護 / {question.category}</p>
      <h1>{question.title}</h1>
      <p className="meta">
        全国共通事項を対象 / 状態：
        <span className={isVerified ? "verified" : ""}>
          {isVerified ? "一次資料確認済み" : "根拠確認中"}
        </span>
        {isVerified && "last_verified" in question ? ` / 最終確認 ${question.last_verified}` : ""}
      </p>

      {!isVerified ? (
        <div className="notice">
          この質問は現在、一次資料との対応関係を確認中です。確認が完了するまで制度上の結論は掲載しません。
        </div>
      ) : (
        <>
          <section className="section answer-summary">
            <h2>結論</h2>
            <p>{question.short_answer}</p>
          </section>

          <section className="section">
            <h2>実務では</h2>
            <ol className="steps">
              {question.practical_steps?.map((step) => <li key={step}>{step}</li>)}
            </ol>
          </section>

          <section className="section">
            <h2>注意</h2>
            <ul className="source-list">
              {question.cautions?.map((caution) => <li key={caution}>{caution}</li>)}
            </ul>
          </section>

          <section className="section">
            <h2>根拠</h2>
            {linkedRules.map((node) => {
              const source = sources.find((item) => item.id === node.source_id);
              return (
                <div className="source-card" key={node.id}>
                  <p className="meta">{node.path.join(" ＞ ")}</p>
                  <p>{node.official_text}</p>
                  {source ? (
                    <a href={source.url} target="_blank" rel="noreferrer">
                      {source.publisher}の原文を確認
                    </a>
                  ) : null}
                </div>
              );
            })}
            {"source_refs" in question ? question.source_refs
              ?.filter((ref) => !linkedRules.some((node) => node.source_id === ref.source_id))
              .map((ref) => {
                const source = sources.find((item) => item.id === ref.source_id);
                if (!source) return null;
                return (
                  <div className="source-card" key={ref.source_id + ref.locator}>
                    <p className="meta">{source.layer} / {ref.locator}</p>
                    <p>{source.title}</p>
                    {source.note ? <p className="meta">{source.note}</p> : null}
                    <a href={source.url} target="_blank" rel="noreferrer">厚生労働省の資料を確認</a>
                  </div>
                );
              }) : null}
          </section>
        </>
      )}

      <section className="section">
        <h2>検索用の言い換え</h2>
        <p>{question.aliases.join(" / ")}</p>
      </section>

      <p><Link href="/">質問一覧へ戻る</Link></p>
    </article>
  );
}
