const issues = [
  {
    title: "必要な情報を探すのに時間がかかる",
    body: "制度、通知、事業所内資料など、散らばった情報への到達時間を短くする。",
    status: "調査公開",
    href: "/issues/information-search",
  },
  {
    title: "記録・文書作成に時間がかかる",
    body: "記録、報告、会議資料など、繰り返し発生する文書作業をどう減らせるか。",
    status: "準備中",
  },
  {
    title: "職員教育・引き継ぎが属人化する",
    body: "マニュアル、研修、質問対応を、現場で使える形に整理する方法を探る。",
    status: "準備中",
  },
  {
    title: "問い合わせ・連携の負担が大きい",
    body: "定型的な確認、社内外の問い合わせ、申し送りの負担を減らす方法を考える。",
    status: "準備中",
  },
];

const steps = [
  ["01", "困りごとを具体化", "誰が、どの作業で、どれくらい困っているかを整理します。"],
  ["02", "事例と研究を確認", "企業・事業所の公開事例、論文、公的資料を分けて確認します。"],
  ["03", "条件を見極める", "AIを使う条件、使わない方がよい条件、必要な前提を整理します。"],
  ["04", "小さく試す", "大規模導入の前に、限定した業務で確認できる最初の一歩を示します。"],
];

export default function Home() {
  return (
    <main>
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="#issues">困りごと</a>
          <a href="#approach">調べ方</a>
          <a href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
            介護ルール ↗
          </a>
        </nav>
      </header>

      <section className="hero">
        <p className="eyebrow">介護現場の業務改善</p>
        <h1>「困っていること」から、<br />改善の選択肢を探す。</h1>
        <p className="lead">
          介護現場の困りごとを起点に、公開事例、論文、公的資料を整理します。
          AIありきではなく、どの方法がどの条件で役立つのかを分かりやすく示すことを目指します。
        </p>
        <div className="heroLinks">
          <a className="primaryLink" href="#issues">困りごとを見る</a>
          <a href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
            制度・基準を確認する →
          </a>
        </div>
      </section>

      <section className="section" id="issues">
        <div className="sectionHead">
          <p className="eyebrow">Issues</p>
          <h2>まず、現場の困りごとから。</h2>
          <p>製品名やAI機能ではなく、実際に時間や負担が発生している仕事から整理します。</p>
        </div>

        <div className="issueList">
          {issues.map((issue, index) => (
            <article className="issueRow" key={issue.title}>
              <span className="issueNumber">{String(index + 1).padStart(2, "0")}</span>
              <div>
                <h3>{issue.title}</h3>
                <p>{issue.body}</p>
              </div>
              <div className="issueAction">
                <span className="status">{issue.status}</span>
                {issue.href ? <a className="issueOpen" href={issue.href}>読む →</a> : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="section muted" id="approach">
        <div className="sectionHead">
          <p className="eyebrow">Approach</p>
          <h2>具体例を、本質的な判断材料に変える。</h2>
          <p>
            単なる成功事例集ではなく、複数の事例と研究から共通する条件を探し、
            現場で試せる行動まで戻します。
          </p>
        </div>

        <ol className="stepList">
          {steps.map(([number, title, body]) => (
            <li key={number}>
              <span>{number}</span>
              <div><strong>{title}</strong><p>{body}</p></div>
            </li>
          ))}
        </ol>
      </section>

      <section className="section boundary">
        <p className="eyebrow">Rules & improvement</p>
        <h2>制度の確認と、業務改善の検討は分けて扱います。</h2>
        <p>
          人員・設備・運営基準、通知、Q&Aなどの制度情報は「介護ルール」で確認します。
          このサイトでは、そのルールを前提に、日々の業務をどう改善できるかを扱います。
        </p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
          介護ルールを開く →
        </a>
      </section>

      <footer>
        <span>介護業務改善 — prototype</span>
        <span>公開情報・研究・事例をもとに検討するための試作サイトです。</span>
      </footer>
    </main>
  );
}
