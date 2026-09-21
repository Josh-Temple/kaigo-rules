import QuestionSearch from "../components/question-search";

export default function HomePage() {
  return (
    <>
      <section className="hero">
        <p className="eyebrow">通所介護 MVP</p>
        <h1>「これ、どうする？」を<br />根拠までたどれるように。</h1>
        <p className="lead">
          通所介護の実務上の疑問を、法令・基準・通知・Q&Aなどの公式資料へ戻れる形で整理します。
          現在は基盤構築中で、未検証の結論は表示しません。
        </p>
        <QuestionSearch />
      </section>
    </>
  );
}
