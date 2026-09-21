import Link from "next/link";
import QuestionSearch from "../components/question-search";

export default function HomePage() {
  return (
    <section className="hero">
      <p className="eyebrow">通所介護 MVP</p>
      <h1>「これ、どうする？」を<br />根拠までたどれるように。</h1>
      <p className="lead">通所介護の実務上の疑問を、法令・基準・通知・Q&Aなどの公式資料へ戻れる形で整理します。未検証の結論は表示しません。</p>
      <QuestionSearch />
      <div className="entry-links">
        <Link className="entry-row" href="/start"><span>これから通所介護を始めたい</span><small>開設準備の順番を確認する →</small></Link>
        <Link className="entry-row" href="/qa"><span>厚生労働省の過去Q&Aから探したい</span><small>国Q&Aを見る →</small></Link>
      </div>
    </section>
  );
}
