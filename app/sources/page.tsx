import sources from "../../data/sources.json";

export default function SourcesPage() {
  return (
    <article className="answer-page">
      <p className="eyebrow">Source registry</p>
      <h1>根拠資料台帳</h1>
      <p className="lead">
        文書そのものと、当サイトで構造化・編集したデータを分離して管理します。
        「公開されている」ことと「現行全文を検証済み」であることは区別します。
      </p>
      <div className="question-list">
        {sources.map((source) => (
          <article className="question" key={source.id}>
            <span className="meta">{source.layer}</span>
            <a href={source.url} target="_blank" rel="noreferrer">{source.title}</a>
            <span className="status">{source.publisher}</span>
          </article>
        ))}
      </div>
      <section className="section">
        <h2>解釈通知の再構成方針</h2>
        <p>
          最新資料から確認できる部分を先にノード化し、不明部分を UNKNOWN として残します。
          過去の通知・新旧対照表を遡って穴を補完し、最後に基準版から改正を順方向へ再適用して一致を確認します。
        </p>
      </section>
    </article>
  );
}
