import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "職員教育・引き継ぎが属人化する | 介護業務改善",
  description:
    "介護現場の研修・引き継ぎ・質問対応を、正本化、検索、短い教材、peer learning、必要に応じたAI検索の順にどう改善するかを整理します。",
};

const findings = [
  {
    label: "49.5%",
    title: "全員が研修に参加できないという課題",
    body:
      "厚生労働省の令和7年度調査では、施設・事業所内研修について、全員が参加できないことが課題として報告されています。一度きりの集合研修だけでは届かない職員がいます。",
  },
  {
    label: "19 reviews",
    title: "継続教育・peer-led trainingには改善signal",
    body:
      "2026年のLTC workforce umbrella reviewでは、19件のreviewを統合し、継続教育やpeer-led trainingが知識・competencyを改善する傾向を報告しました。ただしEvidenceの質とoutcomeはばらつきがあります。",
  },
  {
    label: "3 studies",
    title: "digital toolの定着には教育と組織支援が必要",
    body:
      "geriatric LTC nursing staffのdigital technology acceptanceを扱ったsystematic reviewでは、digital competence、training、leadership support、staff participationなどが要因として挙げられました。eligible studyは3件と少なく、一般化には限界があります。",
  },
];

const knowledgeTypes = [
  [
    "A",
    "文書化できる知識",
    "手順、approved manual、FAQ、system操作、checklist。正本化・検索・短い教材・AI検索の対象にしやすい。",
  ],
  [
    "B",
    "更新責任が曖昧な知識",
    "古い様式、個人PCの手順、非公式memo。AIへ入れる前にowner、version、scopeを決める。",
  ],
  [
    "C",
    "経験知・専門判断",
    "利用者ごとの状況判断、例外対応、対人調整。mentor、peer review、case discussionで扱い、AIの確定回答にしない。",
  ],
];

const steps = [
  ["0", "質問を記録する", "誰が何を何度聞いているかを、個人情報を含めずcategoryで把握する。"],
  ["1", "正本を決める", "反復質問についてowner、version、updated_at、対象職種・場面を決める。"],
  ["2", "短く学べる形にする", "FAQ、checklist、microlearning、短い動画など、必要な場面で開ける形にする。"],
  ["3", "peer learningを残す", "文書化しにくい経験知はmentor、case discussion、peer reviewで扱う。"],
  ["4", "必要ならAI検索を加える", "正本への入口として使い、source・version・scope・不確実性を確認できるようにする。"],
];

const sources = [
  {
    title: "介護現場における生産性の向上等を通じた働きやすい職場環境づくりに資する調査研究事業一式",
    note: "厚生労働省。研修参加、デジタル技能、導入後サポートの課題を確認。",
    href: "https://www.mhlw.go.jp/content/12300000/001712213.pdf",
  },
  {
    title: "Strategies to improve recruitment, retention, working conditions, and skills among the long-term care workforce",
    note: "2026年のumbrella review。19件のreviewを統合し、training・skills developmentのEvidenceを整理。",
    href: "https://www.sciencedirect.com/science/article/pii/S0168851025002507",
  },
  {
    title: "Online geriatric nursing education: A systematic review and typological analysis of interventions and outcomes",
    note: "2026年のsystematic review。online educationの柔軟性と、design・outcomeのheterogeneityを整理。",
    href: "https://pubmed.ncbi.nlm.nih.gov/42140053/",
  },
  {
    title: "Communities of Practice in Long-Term Care—Exploring Frameworks, Barriers and Enablers",
    note: "2026年のsystematic review。LTCでのpeer learningとevidence implementationの条件を整理。",
    href: "https://onlinelibrary.wiley.com/doi/10.1111/ajag.70207",
  },
  {
    title: "Peterborough City Council: Hey Geraldine, a personalised AI assistant",
    note: "Local Government Associationのcase report。expertへの反復質問をknowledge assistantへ移した例。独立評価ではない。",
    href: "https://www2.local.gov.uk/case-studies/peterborough-city-council-hey-geraldine-personalised-ai-assistant",
  },
];

export default function TrainingHandoverIssuePage() {
  return (
    <main>
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="/#issues">困りごと</a>
          <a href="#evidence">根拠</a>
          <a href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
            介護ルール ↗
          </a>
        </nav>
      </header>

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">Issue 03 / Training & handover</p>
          <h1>職員教育・引き継ぎが<br />属人化する。</h1>
          <p className="lead">
            「詳しい人に聞く」が続くと、その人が休むだけで仕事が止まります。
            ただし、経験知まで全部manualやAIへ押し込むのも危険です。
            文書化できる知識と、専門判断を分けて整える方法を考えます。
          </p>
          <div className="issueMeta">
            <span>初版: 2026-09-30</span>
            <span>対象: 研修・onboarding・質問対応・引き継ぎ</span>
            <span>個別ケア判断は自動化対象外</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">Conclusion</p>
          <h2>属人化は、「人の知識をAIに移す」だけでは解けません。</h2>
          <p className="summaryLead">
            まず、繰り返し質問される内容を記録し、文書化できるものだけを正本化します。
            FAQ、checklist、短い教材、検索で届くようにしたうえで、
            それでも残る自然言語の探索負担にAIを検討します。
          </p>
          <p>
            一方、利用者ごとの判断や例外対応のような経験知は、mentor、peer review、case discussionなど、
            人同士で学ぶ経路を残します。全部を検索可能にすることより、どこから人間へ戻すかを決める方が重要です。
          </p>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">What the evidence suggests</p>
            <h2>研修量より、学べる仕組みと運用条件を見ます。</h2>
            <p>
              研修形式だけで優劣を決めず、参加可能性、実務への接続、組織支援、更新責任まで含めて評価します。
            </p>
          </div>
          <div className="findingList">
            {findings.map((finding) => (
              <div className="findingRow" key={finding.label}>
                <span className="findingLabel">{finding.label}</span>
                <div>
                  <h3>{finding.title}</h3>
                  <p>{finding.body}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="section muted">
          <div className="sectionHead">
            <p className="eyebrow">Knowledge types</p>
            <h2>まず、知識を三つに分けます。</h2>
            <p>
              属人化しているものをすべて同じ方法で扱わないことが、最初の安全策です。
            </p>
          </div>
          <ol className="levelList">
            {knowledgeTypes.map(([number, title, body]) => (
              <li key={number}>
                <span>{number}</span>
                <div>
                  <strong>{title}</strong>
                  <p>{body}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">Improvement order</p>
            <h2>質問logから、必要なところだけ仕組みにします。</h2>
          </div>
          <ol className="levelList">
            {steps.map(([number, title, body]) => (
              <li key={number}>
                <span>{number}</span>
                <div>
                  <strong>{title}</strong>
                  <p>{body}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">AI / non-AI</p>
            <h2>AIは、教育そのものより「正本へたどる入口」から。</h2>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">非AI</span>
              <div>
                <h3>FAQ・wiki・checklist・mentor</h3>
                <p>
                  searchable manual、microlearning、short video、onboarding checklist、office hours、
                  peer reviewなどで十分ならAIを追加しません。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">AI</span>
              <div>
                <h3>自然言語で正本へ到達する補助</h3>
                <p>
                  AIを使う場合も、source、version、updated_at、適用範囲、不確実性を確認できるようにします。
                  個別ケア判断や制度上の確定判断をtraining botだけで完結させません。
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="section experiment">
          <p className="eyebrow">Small experiment</p>
          <h2>2週間、質問の流れだけを測ります。</h2>
          <p>
            個人情報を含めず、誰にどんな質問が集中しているかをcategoryで記録します。
          </p>
          <div className="experimentGrid">
            <div>
              <span>01</span>
              <strong>質問log</strong>
              <p>質問theme、頻度、回答者、回答までの時間を記録する。</p>
            </div>
            <div>
              <span>02</span>
              <strong>三分類</strong>
              <p>文書化可能、専門判断が必要、個別case依存に分ける。</p>
            </div>
            <div>
              <span>03</span>
              <strong>上位5問だけ整備</strong>
              <p>FAQやshort guideを作り、正本とownerを付ける。</p>
            </div>
            <div>
              <span>04</span>
              <strong>再測定</strong>
              <p>同じ質問回数、回答時間、誤った自己解決、expert escalationを確認する。</p>
            </div>
          </div>
          <p>
            FAQで十分ならそこで止めます。自然言語検索の負担が残る場合だけ、同じ質問でAI検索と比較します。
          </p>
        </section>

        <section className="section boundary">
          <p className="eyebrow">Safety boundary</p>
          <h2>経験知を「正解集」に変えすぎない。</h2>
          <p>
            ベテランが普段していることの中には、正式な手順だけでなく、状況依存の判断や非公式なworkaroundも含まれます。
            AIやwikiへ移す前に、正式な知識として採用してよいかを確認します。
          </p>
          <p>
            制度上の義務・要件を扱う内容は、Kaigo Ops内の研修資料だけで確定せず、介護ルール側の原典と検証状態へ接続します。
          </p>
          <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
            介護ルールで制度・原典を確認する →
          </a>
        </section>

        <section className="section" id="evidence">
          <div className="sectionHead">
            <p className="eyebrow">Evidence</p>
            <h2>主な根拠</h2>
            <p>
              日本の公的調査、systematic / umbrella review、海外case reportを区別して扱います。
            </p>
          </div>
          <div className="sourceList">
            {sources.map((source, index) => (
              <a key={source.href} href={source.href} target="_blank" rel="noreferrer" className="sourceRow">
                <span>{String(index + 1).padStart(2, "0")}</span>
                <div>
                  <strong>{source.title}</strong>
                  <p>{source.note}</p>
                </div>
                <span aria-hidden="true">↗</span>
              </a>
            ))}
          </div>
        </section>

        <section className="section nextIssue">
          <p className="eyebrow">What we still do not know</p>
          <h2>まだ結論を出していないこと</h2>
          <ul>
            <li>日本の介護現場で、onboardingや質問対応に実際どれだけ時間が使われているか。</li>
            <li>microlearningやblended learningが介護現場でどの条件なら定着するか。</li>
            <li>AI assistantがFAQより優れる質問の種類は何か。</li>
            <li>誤答や古い知識を見逃さず更新できる運用コストはどれくらいか。</li>
            <li>引き継ぎ改善が離職・定着・care qualityへどの程度つながるか。</li>
          </ul>
          <p>
            ここは海外caseやtraining一般論から推測せず、日本の実利用データと追加研究を得ながら更新します。
          </p>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — evidence-informed prototype</span>
        <span>初版: 2026-09-30</span>
      </footer>
    </main>
  );
}
