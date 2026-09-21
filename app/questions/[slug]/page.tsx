import Link from "next/link";
import { notFound } from "next/navigation";
import questionsData from "../../../data/questions.json";
import sourcesData from "../../../data/sources.json";
import ruleNodesData from "../../../data/rule-nodes.json";
import noticeNodesData from "../../../data/notice-nodes.json";
import qaItemsData from "../../../data/qa-items.json";

const questions = questionsData as Array<any>;
const sources = sourcesData as Array<any>;
const ruleNodes = ruleNodesData as Array<any>;
const noticeNodes = noticeNodesData as Array<any>;
const qaItems = qaItemsData as Array<any>;

export function generateStaticParams() {
  return questions.map((q) => ({ slug: q.slug }));
}

export default async function QuestionPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const question = questions.find((q) => q.slug === slug);
  if (!question) notFound();

  const isVerified = question.status === "verified";
  const linkedRules = isVerified ? ruleNodes.filter((node) => question.rule_node_ids?.includes(node.id)) : [];
  const linkedNotices = isVerified ? noticeNodes.filter((node) => question.notice_node_ids?.includes(node.id)) : [];
  const linkedQa = isVerified ? qaItems.filter((item) => question.qa_item_ids?.includes(item.id)) : [];

  return (
    <article className="answer-page">
      <p className="eyebrow">通所介護 / {question.category}</p>
      <h1>{question.title}</h1>
      <p className="meta">全国共通事項を対象 / 状態：<span className={isVerified ? "verified" : ""}>{isVerified ? "一次資料確認済み" : "根拠確認中"}</span>{isVerified && question.last_verified ? ` / 最終確認 ${question.last_verified}` : ""}</p>
      {isVerified && question.verification_note ? <p className="scope-note">{question.verification_note}</p> : null}

      {!isVerified ? <div className="notice">この質問は現在、一次資料との対応関係を確認中です。確認が完了するまで制度上の結論は掲載しません。</div> : (
        <>
          <section className="section answer-summary"><h2>結論</h2><p>{question.short_answer}</p></section>
          <section className="section"><h2>実務では</h2><ol className="steps">{question.practical_steps?.map((step: string) => <li key={step}>{step}</li>)}</ol></section>
          <section className="section"><h2>注意</h2><ul className="source-list">{question.cautions?.map((caution: string) => <li key={caution}>{caution}</li>)}</ul></section>
          <section className="section">
            <h2>根拠</h2>
            {linkedRules.map((node) => {
              const source = sources.find((item) => item.id === node.source_id);
              return <div className="source-card" key={node.id}><p className="source-kind">基準省令</p><p className="meta">{node.path.join(" ＞ ")}</p><p>{node.official_text}</p>{node.text_form ? <p className="meta">上記は適用関係や列挙を読みやすくするため当サイトで構造化しています。逐語的な原文はリンク先で確認してください。</p> : null}{source ? <a href={source.url} target="_blank" rel="noreferrer">{source.publisher}の原文を確認</a> : null}</div>;
            })}
            {linkedNotices.map((node) => {
              const source = sources.find((item) => node.source_ids?.includes(item.id));
              return <div className="source-card" key={node.id}><p className="source-kind">解釈通知</p><p className="meta">{node.path.join(" ＞ ")}</p><p>{node.editorial_summary}</p><p className="meta">上記は当サイトの要約です。</p>{source ? <a href={source.url} target="_blank" rel="noreferrer">厚生労働省資料を確認</a> : null}</div>;
            })}
            {linkedQa.map((item) => {
              const source = sources.find((s) => s.id === item.source_id);
              return <div className="source-card" key={item.id}><p className="source-kind">国Q&A</p><p className="meta">{item.source_document} / {item.source_number}</p><p><strong>質問の要旨：</strong>{item.question_summary}</p><p><strong>回答の要旨：</strong>{item.answer_summary}</p><p className="meta">上記は検索しやすいよう当サイトで要約しています。</p>{source ? <a href={source.url} target="_blank" rel="noreferrer">厚生労働省Q&A集を確認</a> : null}</div>;
            })}
            {question.source_refs?.filter((ref: any) => !linkedRules.some((node) => node.source_id === ref.source_id) && !linkedNotices.some((node) => node.source_ids?.includes(ref.source_id)) && !linkedQa.some((item) => item.source_id === ref.source_id)).map((ref: any) => {
              const source = sources.find((item) => item.id === ref.source_id);
              if (!source) return null;
              return <div className="source-card" key={ref.source_id + ref.locator}><p className="source-kind">{source.layer}</p><p className="meta">{ref.locator}</p><p>{source.title}</p>{source.note ? <p className="meta">{source.note}</p> : null}<a href={source.url} target="_blank" rel="noreferrer">厚生労働省の資料を確認</a></div>;
            })}
          </section>
        </>
      )}
      <section className="section"><h2>検索用の言い換え</h2><p>{question.aliases.join(" / ")}</p><p><Link href={`/qa?q=${encodeURIComponent(question.aliases?.[0] || question.title)}&service=16`}>この論点で国Q&Aを検索する →</Link></p></section>
      <p><Link href="/">質問一覧へ戻る</Link></p>
    </article>
  );
}
