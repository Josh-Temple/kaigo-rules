import qaItems from "../../data/qa-items.json";
import sources from "../../data/sources.json";

export default function QaPage() {
  return (
    <article className="answer-page wide-page">
      <p className="eyebrow">MHLW Q&A CORPUS</p>
      <h1>国Q&A</h1>
      <p className="lead">厚生労働省が過去に発出した介護サービス関係Q&Aを、サービス種別・基準種別・論点・発出時期・文書番号で構造化していきます。</p>
      <div className="notice">現在はデータ構造の検証段階です。Q&Aだけで結論を出さず、法令・基準・通知と一緒に確認します。</div>
      <div className="qa-list">
        {qaItems.map((item) => {
          const source = sources.find((s) => s.id === item.source_id);
          return <section className="qa-row" key={item.id}><p className="meta">{item.service.join(" / ")} ・ {item.standard_category} ・ {item.issued_at}</p><h2>{item.topic.join(" / ")}</h2><p><strong>質問の要旨：</strong>{item.question_summary}</p><p><strong>回答の要旨：</strong>{item.answer_summary}</p><p className="meta">{item.source_document} / {item.source_number}</p>{source ? <a href={source.url} target="_blank" rel="noreferrer">厚生労働省のQ&A集を確認</a> : null}</section>;
        })}
      </div>
      <section className="section"><h2>取り込み方針</h2><p>Q&A本文を単純に並べるのではなく、元の発出文書と番号を保持し、現在の法令・通知ノードへ接続します。将来は「古いQ&Aが現在も使えるか」を改正履歴から判定できる形を目指します。</p></section>
    </article>
  );
}
