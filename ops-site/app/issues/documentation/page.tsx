import type { Metadata } from "next";
import IssueNavigation from "../_components/IssueNavigation";

export const metadata: Metadata = {
  title: "記録・文書作成に時間がかかる | 介護業務改善",
  description:
    "介護記録、報告、転記などの文書作業を、業務の見直し・データ再利用・ICT・AIによる下書きの順にどう減らすかを、公的資料と研究から整理します。",
};

const findings = [
  {
    label: "29.5%",
    title: "小規模実証では記録・文書時間が減少",
    body:
      "厚生労働省の令和7年度実証では、介護記録ソフト導入と業務フロー変更を組み合わせた6事業所で、記録・文書作成が43.1分から30.4分へ減少しました。ソフト単体の因果効果ではありません。",
  },
  {
    label: "44.7%",
    title: "電子化しても手入力転記が残る",
    body:
      "令和7年度全国調査では、介護記録ソフト利用回答者3,670件の44.7%で、記録から請求までに手入力転記が残っていました。電子化と一気通貫化は別です。",
  },
  {
    label: "運用",
    title: "技術だけでなく研修・支援体制が必要",
    body:
      "同じ全国調査では、端末での記録が難しい職員や、トラブル対応人材の不足も報告されています。導入後の運用設計をコストとして扱う必要があります。",
  },
];

const steps = [
  ["0", "不要な記録を減らす", "制度上必要な記録と、慣行で残っている重複記録を分ける。"],
  ["1", "正本と入力元を決める", "一度入力した情報をどこで保持し、どこへ再利用するかを整理する。"],
  ["2", "転記を減らす", "紙・FAX・別システム・請求への再入力を可視化して減らす。"],
  ["3", "入力場所と方法を変える", "携帯端末での入力、音声入力、入力項目をそろえた様式などを比較する。"],
  ["4", "必要ならAIによる下書きを試す", "AI出力は下書きとし、正式記録へ入れる前に人間が確認する。"],
];

const sources = [
  {
    title: "介護テクノロジー等による生産性向上の取組に関する調査及び効果測定事業",
    note: "厚生労働省。介護記録ソフトと業務フロー変更を組み合わせた小規模な前後実証。",
    href: "https://www.mhlw.go.jp/content/12300000/001690572.pdf",
  },
  {
    title: "介護現場における生産性の向上等を通じた働きやすい職場環境づくりに資する調査研究事業一式",
    note: "厚生労働省。記録ソフト利用時にも残る転記、研修・支援体制の課題を確認。",
    href: "https://www.mhlw.go.jp/content/12300000/001712213.pdf",
  },
  {
    title: "ICT導入支援事業 令和3年度 導入効果報告取りまとめ",
    note: "厚生労働省。5,058件の導入事業所自己申告。文書作成・再利用の改善と同時に業務見直しも実施。",
    href: "https://www.mhlw.go.jp/content/12300000/001124036.pdf",
  },
  {
    title: "Newcastle City Council: Magic Notes",
    note: "GOV.UK Algorithmic Transparency Record。AI出力を下書きとして扱い、担当職員の確認を残す運用例。",
    href: "https://www.gov.uk/algorithmic-transparency-records/newcastle-city-council-magic-notes",
  },
];

export default function DocumentationIssuePage() {
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

      <IssueNavigation current="/issues/documentation" />

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">困りごと 02</p>
          <h1>記録・文書作成に<br />時間がかかる。</h1>
          <p className="lead">
            記録時間を減らす方法は、文章生成AIだけではありません。
            重複入力、紙と電子の併用、転記、後追い記録を先に見直し、
            それでも残る作業にICTやAIを使う順序で整理します。
          </p>
          <div className="issueMeta">
            <span>初版: 2026-09-29</span>
            <span>対象: 記録・転記・文書作成</span>
            <span>個人情報を含むAI利用は別途運用設計が必要</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">結論</p>
          <h2>先に減らすのは、文章を書く時間より「二度書く時間」です。</h2>
          <p className="summaryLead">
            日本の公的な根拠資料では、記録ソフト導入と業務フロー変更を組み合わせた実証で、
            記録・文書作成や転記の時間が減った例があります。一方、全国調査では記録ソフトを使っていても
            手入力転記が残る事業所が多く、電子化だけでは分断が解消しないことも確認されています。
          </p>
          <p>
            そのため、まず不要な記録と重複入力を減らし、一度入力した情報を再利用できる流れを作ります。
            音声入力やAI要約は、その後に残る作業へ限定して試す方が、効果とリスクを評価しやすくなります。
          </p>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">根拠から分かること</p>
            <h2>日本のデータから見えること</h2>
            <p>
              数値は特定の調査設計・対象条件に依存します。一般的な効果率としては扱いません。
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
            <p className="eyebrow">改善の順序</p>
            <h2>改善は、重複を減らしてから自動化します。</h2>
            <p>
              AIを追加しても、同じ内容を別システムへ転記する構造が残れば、全体の負担は残ります。
            </p>
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
            <h2>AIを使う前に、普通の改善策も比較します。</h2>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">非AI</span>
              <div>
                <h3>様式統合・入力項目をそろえた様式・情報の再利用</h3>
                <p>
                  チェック欄、定型様式、共通情報再利用、システム連携、紙の廃止、入力タイミング変更などで十分なら、
                  生成AIを追加する必要はありません。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">AI</span>
              <div>
                <h3>音声・要約・文章化は下書き用途から</h3>
                <p>
                  AIを使う場合は、まず低リスクの下書き用途から試し、正式記録へ入れる前に人間が確認します。
                  モデルの性能だけでなく、誤りの修正にかかる時間も測ります。
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="section experiment">
          <p className="eyebrow">小さく試す</p>
          <h2>1週間、記録作業を四つに分けて測ります。</h2>
          <p>
            いきなり製品を選ばず、どこに時間が消えているかを先に確認します。
          </p>
          <div className="experimentGrid">
            <div>
              <span>01</span>
              <strong>必要な記録</strong>
              <p>制度・運用上、本当に残す必要がある記録に使った時間。</p>
            </div>
            <div>
              <span>02</span>
              <strong>転記・再入力</strong>
              <p>同じ内容を紙、別システム、請求、報告へもう一度入れた時間。</p>
            </div>
            <div>
              <span>03</span>
              <strong>探す・確認する</strong>
              <p>過去記録、様式、正しい入力方法を探した時間。</p>
            </div>
            <div>
              <span>04</span>
              <strong>後追い記録</strong>
              <p>業務後に思い出しながらまとめ直した時間。</p>
            </div>
          </div>
          <p>
            最も大きい一つだけを対象に、様式統合、情報の再利用、携帯端末での入力、音声入力、AIによる下書きを比較します。
          </p>
        </section>

        <section className="section">
          <p className="eyebrow">改善を試す</p>
          <h2>記録業務の見直しシートで、前後を比較する。</h2>
          <p>処理件数と作業時間を分け、確認・修正時間や品質も含めて記録します。入力内容は送信せず、印刷して手元に残せます。</p>
          <a className="primaryLink" href="/tools/documentation-review">見直しシートを開く →</a>
        </section>

        <section className="section boundary">
          <p className="eyebrow">運用上の注意</p>
          <h2>正式な介護記録では、生成速度より運用責任を先に決めます。</h2>
          <p>
            個人情報・要配慮個人情報を含む記録でAIを使う場合は、アクセス権限、保存期間、
            提供事業者・再委託先、人間による確認、訂正方法、代替手順などを確認する必要があります。
            海外の実装例でも、AI出力を下書きとして扱い、最終確認を職員へ残す設計が採られています。
          </p>
          <p>
            何を記録として残す必要があるか、制度上の要件を確認する場合は介護ルール側の原典・検証状態を確認してください。
          </p>
          <a className="textLink" href="https://kaigo-rules.vercel.app/questions/care-plan-content" target="_blank" rel="noreferrer">
            通所介護計画の記載内容を確認 →
          </a>
        </section>

        <section className="section" id="evidence">
          <div className="sectionHead">
            <p className="eyebrow">根拠</p>
            <h2>主な根拠</h2>
            <p>
              公的実証、全国調査、導入事業所の自己申告、海外の透明性記録を区別して扱います。
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
            <li>日本の介護現場で、生成AIによる記録の下書きが独立評価でどれだけ時間を減らすか。</li>
            <li>音声入力とAIによる要約のどちらが負担軽減に寄与しているか。</li>
            <li>誤りを修正する時間まで含めても効果が残るか。</li>
            <li>記録品質が改善するか、低下するか。</li>
            <li>小規模事業所で費用対効果が成立するか。</li>
          </ul>
          <p>
            ここは製品事例から推測せず、独立評価・公的実証・実利用データが得られた段階で更新します。
          </p>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — 根拠に基づく試作版</span>
        <span>初版: 2026-09-29</span>
      </footer>
    </main>
  );
}
