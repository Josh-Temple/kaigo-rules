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
    status: "次の候補",
  },
  {
    title: "職員教育・引き継ぎが属人化する",
    body: "マニュアル、研修、質問対応を、現場で使える形に整理する方法を探る。",
    status: "候補",
  },
  {
    title: "問い合わせ・連携の負担が大きい",
    body: "定型的な確認、社内外の問い合わせ、申し送りの負担を減らす方法を考える。",
    status: "候補",
  },
];

const steps = [
  ["01", "困りごとを具体化", "誰が、どの作業で、どのような判断に困っているかを整理します。"],
  ["02", "事例と研究を確認", "公的資料、研究、事業者事例、ベンダー主張を分けて確認します。"],
  ["03", "条件を見極める", "何が機能しやすいか、何が失敗しやすいか、制度上の制約は何かを整理します。"],
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
        <p className="eyebrow">介護事業の経営・運営・業務改善</p>
        <h1>「困っていること」から、<br />改善の選択肢を探す。</h1>
        <p className="lead">
          介護事業者・介護現場の困りごとを起点に、国内外の公的資料、研究、導入事例を整理します。
          AIやDXありきではなく、どの方法がどの条件で役立つのか、何が失敗しやすいのかまで含めて判断材料を示します。
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
          <h2>まず、現場と事業運営の困りごとから。</h2>
          <p>
            製品名やAI機能ではなく、実際に時間、コスト、判断負担が発生している仕事から整理します。
            制度上の確認が必要な部分は介護ルールへつなぎます。
          </p>
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
          <h2>具体例を、判断材料に変える。</h2>
          <p>
            単なる成功事例集ではなく、複数の事例と研究から共通する条件を探し、
            AIを使わない選択肢も含めて、現場で試せる行動まで戻します。
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
        <p className="eyebrow">Rules & operations</p>
        <h2>制度の確認と、経営・運営・業務改善の検討は分けて扱います。</h2>
        <p>
          法令、基準省令、解釈通知、報酬、Q&Aなどの制度情報は「介護ルール」で確認します。
          このサイトでは、そのルールを前提に、事業をどう運営し、日々の仕事をどう改善できるかを扱います。
        </p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
          介護ルールを開く →
        </a>
      </section>

      <footer>
        <span>介護業務改善 — evidence-informed prototype</span>
        <span>公開情報・研究・事例をもとに、経営・運営・業務改善の判断材料を整理します。</span>
      </footer>
    </main>
  );
}
