import type { Metadata } from "next";
import IssueNavigation from "../_components/IssueNavigation";

export const metadata: Metadata = {
  title: "職員教育・引き継ぎが属人化する | 介護業務改善",
  description:
    "介護現場の研修・引き継ぎ・質問対応を、正本化、検索、短い教材、職員同士の学び合い、必要に応じたAI検索の順にどう改善するかを整理します。",
};

const findings = [
  {
    label: "49.5%",
    title: "全員が研修に参加できないという課題",
    body:
      "厚生労働省の令和7年度調査では、施設・事業所内研修について、全員が参加できないことが課題として報告されています。一度きりの集合研修だけでは届かない職員がいます。",
  },
  {
    label: "19件のレビュー",
    title: "継続教育・職員が教え合う研修には改善の傾向",
    body:
      "2026年の長期ケア職員に関する複数のレビューをまとめた研究では、19件のレビューを統合し、継続教育や職員が教え合う研修が知識・実務能力を改善する傾向を報告しました。ただし根拠の質と評価した成果はばらつきがあります。",
  },
  {
    label: "3件の研究",
    title: "デジタル機器・ソフトの定着には教育と組織支援が必要",
    body:
      "高齢者の長期ケアに従事する看護職員のデジタル技術受容を扱った体系的な文献レビューでは、デジタル活用能力、研修、管理職の支援、職員の参加などが要因として挙げられました。対象研究は3件と少なく、一般化には限界があります。",
  },
];

const knowledgeTypes = [
  [
    "A",
    "文書化できる知識",
    "手順、承認済みの手順書、FAQ、システム操作、確認一覧。正本化・検索・短い教材・AI検索の対象にしやすい。",
  ],
  [
    "B",
    "更新責任が曖昧な知識",
    "古い様式、個人PCの手順、非公式メモ。AIへ入れる前に管理責任者、版、適用範囲を決める。",
  ],
  [
    "C",
    "経験知・専門判断",
    "利用者ごとの状況判断、例外対応、対人調整。指導担当者、職員同士の確認、事例検討で扱い、AIの確定回答にしない。",
  ],
];

const steps = [
  ["0", "質問を記録する", "誰が何を何度聞いているかを、個人情報を含めず種類で把握する。"],
  ["1", "正本を決める", "反復質問について管理責任者、版、更新日、対象職種・場面を決める。"],
  ["2", "短く学べる形にする", "FAQ、確認一覧、短い単位の学習、短い動画など、必要な場面で開ける形にする。"],
  ["3", "職員同士の学び合いを残す", "文書化しにくい経験知は指導担当者、事例検討、職員同士の確認で扱う。"],
  ["4", "必要ならAI検索を加える", "正本への入口として使い、原典・版・適用範囲・不確実性を確認できるようにする。"],
];

const sources = [
  {
    title: "介護現場における生産性の向上等を通じた働きやすい職場環境づくりに資する調査研究事業一式",
    note: "厚生労働省。研修参加、デジタル技能、導入後サポートの課題を確認。",
    href: "https://www.mhlw.go.jp/content/12300000/001712213.pdf",
  },
  {
    title: "Strategies to improve recruitment, retention, working conditions, and skills among the long-term care workforce",
    note: "2026年の複数レビューを統合した研究。19件のレビューから、研修・技能開発の根拠を整理。",
    href: "https://www.sciencedirect.com/science/article/pii/S0168851025002507",
  },
  {
    title: "Online geriatric nursing education: A systematic review and typological analysis of interventions and outcomes",
    note: "2026年の系統的レビュー。オンライン教育の柔軟性と、研究設計・結果指標の違いを整理。",
    href: "https://pubmed.ncbi.nlm.nih.gov/42140053/",
  },
  {
    title: "Communities of Practice in Long-Term Care—Exploring Frameworks, Barriers and Enablers",
    note: "2026年の系統的レビュー。長期ケアでの職員同士の学び合いと根拠を実務へ取り入れる条件を整理。",
    href: "https://onlinelibrary.wiley.com/doi/10.1111/ajag.70207",
  },
  {
    title: "Peterborough City Council: Hey Geraldine, a personalised AI assistant",
    note: "英国地方自治体協会の事例報告。専門担当者への反復質問を知識検索支援ツールへ移した例。独立評価ではない。",
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

      <IssueNavigation current="/issues/training-handover" />

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">困りごと 03</p>
          <h1>職員教育・引き継ぎが<br />属人化する。</h1>
          <p className="lead">
            「詳しい人に聞く」が続くと、その人が休むだけで仕事が止まります。
            ただし、経験知まで全部手順書やAIへ押し込むのも危険です。
            文書化できる知識と、専門判断を分けて整える方法を考えます。
          </p>
          <div className="issueMeta">
            <span>初版: 2026-09-30</span>
            <span>対象: 研修・新人受け入れ・質問対応・引き継ぎ</span>
            <span>個別ケア判断は自動化対象外</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">結論</p>
          <h2>属人化は、「人の知識をAIに移す」だけでは解けません。</h2>
          <p className="summaryLead">
            まず、繰り返し質問される内容を記録し、文書化できるものだけを正本化します。
            FAQ、確認一覧、短い教材、検索で届くようにしたうえで、
            それでも残る自然言語の探索負担にAIを検討します。
          </p>
          <p>
            一方、利用者ごとの判断や例外対応のような経験知は、指導担当者、職員同士の確認、事例検討など、
            人同士で学ぶ経路を残します。全部を検索可能にすることより、どこから人間へ戻すかを決める方が重要です。
          </p>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">根拠から分かること</p>
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
            <p className="eyebrow">知識の種類</p>
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
            <p className="eyebrow">改善の順序</p>
            <h2>質問記録から、必要なところだけ仕組みにします。</h2>
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
            <p className="eyebrow">AIを使う方法・使わない方法</p>
            <h2>AIは、教育そのものより「正本へたどる入口」から。</h2>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">非AI</span>
              <div>
                <h3>FAQ・共有の手引き・確認一覧・指導担当者</h3>
                <p>
                  検索できる手順書、短い単位の学習、短い動画、新人受け入れ 確認一覧、質問を受け付ける時間、
                  職員同士の確認などで十分ならAIを追加しません。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">AI</span>
              <div>
                <h3>自然言語で正本へ到達する補助</h3>
                <p>
                  AIを使う場合も、原典、版、更新日、適用範囲、不確実性を確認できるようにします。
                  個別ケア判断や制度上の確定判断を研修支援AIだけで完結させません。
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="section experiment">
          <p className="eyebrow">小さく試す</p>
          <h2>2週間、質問の流れだけを測ります。</h2>
          <p>
            個人情報を含めず、誰にどんな質問が集中しているかを種類で記録します。
          </p>
          <div className="experimentGrid">
            <div>
              <span>01</span>
              <strong>質問記録</strong>
              <p>質問内容、頻度、回答者、回答までの時間を記録する。</p>
            </div>
            <div>
              <span>02</span>
              <strong>三分類</strong>
              <p>文書化可能、専門判断が必要、個別事例依存に分ける。</p>
            </div>
            <div>
              <span>03</span>
              <strong>上位5問だけ整備</strong>
              <p>FAQや短い手引きを作り、正本と管理責任者を付ける。</p>
            </div>
            <div>
              <span>04</span>
              <strong>再測定</strong>
              <p>同じ質問回数、回答時間、誤った自己解決、専門担当者への引き継ぎを確認する。</p>
            </div>
          </div>
          <p>
            FAQで十分ならそこで止めます。自然言語検索の負担が残る場合だけ、同じ質問でAI検索と比較します。
          </p>
        </section>

        <section className="section boundary">
          <p className="eyebrow">運用上の注意</p>
          <h2>経験知を「正解集」に変えすぎない。</h2>
          <p>
            ベテランが普段していることの中には、正式な手順だけでなく、状況依存の判断や非公式な独自の回避手順も含まれます。
            AIや共有の手引きへ移す前に、正式な知識として採用してよいかを確認します。
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
            <p className="eyebrow">根拠</p>
            <h2>主な根拠</h2>
            <p>
              日本の公的調査、系統的レビュー・複数レビューの統合、海外事例報告を区別して扱います。
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
          <p className="eyebrow">まだ分からないこと</p>
          <h2>まだ結論を出していないこと</h2>
          <ul>
            <li>日本の介護現場で、新人受け入れや質問対応に実際どれだけ時間が使われているか。</li>
            <li>短い単位の学習や対面とオンラインを組み合わせた学習が介護現場でどの条件なら定着するか。</li>
            <li>AIアシスタントがFAQより優れる質問の種類は何か。</li>
            <li>誤答や古い知識を見逃さず更新できる運用コストはどれくらいか。</li>
            <li>引き継ぎ改善が離職・定着・ケアの質へどの程度つながるか。</li>
          </ul>
          <p>
            ここは海外事例や研修一般論から推測せず、日本の実利用データと追加研究を得ながら更新します。
          </p>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — 根拠に基づく試作版</span>
        <span>初版: 2026-09-30</span>
      </footer>
    </main>
  );
}
