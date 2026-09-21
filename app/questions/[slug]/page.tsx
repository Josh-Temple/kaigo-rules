import Link from "next/link";
import { notFound } from "next/navigation";
import questions from "../../../data/questions.json";

export function generateStaticParams() {
  return questions.map((q) => ({ slug: q.slug }));
}

export default async function QuestionPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const question = questions.find((q) => q.slug === slug);
  if (!question) notFound();

  return (
    <article className="answer-page">
      <p className="eyebrow">通所介護 / {question.category}</p>
      <h1>{question.title}</h1>
      <p className="meta">全国共通事項を対象 / 状態：根拠確認中</p>

      <div className="notice">
        この質問は現在、一次資料との対応関係を確認中です。確認が完了するまで制度上の結論は掲載しません。
      </div>

      <section className="section">
        <h2>結論</h2>
        <p>未掲載（根拠確認完了後に公開）</p>
      </section>

      <section className="section">
        <h2>実務では</h2>
        <p>未掲載（根拠確認完了後に公開）</p>
      </section>

      <section className="section">
        <h2>根拠</h2>
        <p>法令・基準省令・解釈通知・Q&A等との対応付けを進めています。</p>
        <Link href="/sources">根拠資料台帳を見る</Link>
      </section>

      <section className="section">
        <h2>検索用の言い換え</h2>
        <p>{question.aliases.join(" / ")}</p>
      </section>
    </article>
  );
}
