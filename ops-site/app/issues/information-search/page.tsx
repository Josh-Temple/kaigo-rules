import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "必要な情報を探すのに時間がかかる | 介護業務改善",
  description:
    "制度・通知・Q&A・事業所内資料など、散らばった情報をどう整理し、必要な根拠へ早く到達できるようにするかを、調査結果と実務上の改善手順から整理します。",
};

const findings = [
  {
    label: "分散",
    title: "検索機能だけでは解けない",
    body:
      "介護現場では、制度資料、記録システム、紙、事業所内資料、人への問い合わせが併存しやすく、情報の所在そのものが分かれています。最初に確認すべきなのは、検索性能より正本・重複・更新経路です。",
  },
  {
    label: "転記",
    title: "デジタル化しても分断は残る",
    body:
      "厚生労働省の2025年度調査では、介護記録ソフト利用回答者3,670件の44.7%が、記録から請求までに手入力転記が発生すると回答しています。システム導入だけで一気通貫になるとは限りません。",
  },
  {
    label: "改善",
    title: "業務の組み替えと一体で考える",
    body:
      "厚生労働省の実証では、介護記録ソフトと業務フロー変更を組み合わせた事例で、記録・文書と転記に要する時間の減少が観測されています。単なるツール追加ではなく、重複作業の廃止まで含めて設計する必要があります。",
  },
];

const levels = [
  ["0", "不要な情報・作業を減らす", "古い版、重複文書、不要な転記や確認を先に減らす。"],
  ["1", "正本を決める", "情報源、管理者、版、更新日、適用範囲を明確にする。"],
  ["2", "普通の検索を改善する", "分類、タグ、全文検索、FAQ、業務別の導線を整える。"],
  ["3", "必要ならAI検索を加える", "根拠、該当箇所、日付、適用範囲、不確実性を一緒に返す。"],
  ["4", "検索結果を業務につなぐ", "チェックリスト、手続、研修、更新通知など次の行動へ接続する。"],
];

const sources = [
  {
    title: "介護現場における生産性の向上等を通じた働きやすい職場環境づくりに資する調査研究事業一式",
    note: "厚生労働省。介護記録ソフト利用時にも残る手入力転記の状況を確認。",
    href: "https://www.mhlw.go.jp/content/12300000/001712213.pdf",
  },
  {
    title: "介護テクノロジー等による生産性向上の取組に関する調査及び効果測定事業",
    note: "厚生労働省。業務フロー変更を含む実証で、記録・文書、転記時間の変化を確認。",
    href: "https://www.mhlw.go.jp/content/12300000/001690572.pdf",
  },
  {
    title: "ICT導入支援事業 令和3年度 導入効果報告取りまとめ",
    note: "厚生労働省。導入事業所による検索性・情報共有の自己評価。選択・自己申告バイアスに注意。",
    href: "https://www.mhlw.go.jp/content/12300000/001124036.pdf",
  },
  {
    title: "Nursing Information Flow in Long-Term Care Facilities",
    note: "複数の情報源・媒体が併存する長期ケア施設の情報フローを扱った研究。",
    href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC5931917/",
  },
];

export default function InformationSearchIssuePage() {
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
          <p className="eyebrow">Issue 01 / Information search</p>
          <h1>必要な情報を探すのに<br />時間がかかる。</h1>
          <p className="lead">
            制度、通知、Q&A、マニュアル、事業所内資料。情報が増えるほど、
            「どこを見ればよいか」を判断する負担も増えます。
            このページでは、検索ツールを増やす前に確認したい構造と、小さく改善する順序を整理します。
          </p>
          <div className="issueMeta">
            <span>調査公開: 2026-09-25</span>
            <span>対象: 公開された制度・業務知識</span>
            <span>個人のケア情報は対象外</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">Conclusion</p>
          <h2>先に整えるのは、AIではなく情報の土台です。</h2>
          <p className="summaryLead">
            現時点の調査では、情報探索の負担は「検索が弱い」だけでは説明できません。
            正本が不明確、同じ情報を複数システムへ転記する、古い版が残る、詳しい人に質問が集中する、といった構造が重なっています。
          </p>
          <p>
            そのため、改善は「AI検索を入れる」から始めず、不要な情報を減らし、正本を決め、
            通常の検索を改善したうえで、それでも残る複数資料横断や自然言語での探索にAIを検討する順序が妥当です。
          </p>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">What the evidence suggests</p>
            <h2>見えてきた三つの論点</h2>
            <p>数値は効果を一般化するためではなく、問題の所在を把握する材料として扱います。</p>
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
            <p className="eyebrow">Improvement ladder</p>
            <h2>改善は、下から順に。</h2>
            <p>
              上の段階ほど高度ですが、下の段階が未整理のままでは効果を評価しにくくなります。
              普通の検索で十分なら、AIを足す必要はありません。
            </p>
          </div>
          <ol className="levelList">
            {levels.map(([number, title, body]) => (
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

        <section className="section experiment">
          <p className="eyebrow">Small experiment</p>
          <h2>最初の一歩は、よく聞かれる10問で十分です。</h2>
          <p>
            まず、職員や事業所から繰り返し出る質問を10問程度選びます。
            それぞれについて「正しい原典」「該当箇所」「条件」「現在の版」を固定し、
            今の探し方でどれくらい時間がかかるかを測ります。
          </p>
          <div className="experimentGrid">
            <div>
              <span>01</span>
              <strong>質問を固定</strong>
              <p>頻度が高く、答えの根拠を一次資料で確認できる質問を選ぶ。</p>
            </div>
            <div>
              <span>02</span>
              <strong>現状を測る</strong>
              <p>正しい根拠へ到達する時間、クリック数、聞き直し回数を記録する。</p>
            </div>
            <div>
              <span>03</span>
              <strong>導線を整える</strong>
              <p>FAQ、分類、全文検索など、AIを使わない方法から試す。</p>
            </div>
            <div>
              <span>04</span>
              <strong>必要ならAIと比較</strong>
              <p>同じ質問セットで、速さだけでなく誤答・古い情報・回答保留も比較する。</p>
            </div>
          </div>
        </section>

        <section className="section boundary">
          <p className="eyebrow">Safety boundary</p>
          <h2>制度情報は、検証状態を確認して使います。</h2>
          <p>
            介護ルールでは、機械取込・独立監査・人手確認を分けて管理しています。
            現在、人手確認が完了していない情報層もあるため、このページから制度上の個別判断を自動的に確定することはしません。
            個別の制度確認では、介護ルール側に表示される検証状態と原典を確認してください。
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
              調査では国内外の資料を比較しています。ここでは、このページの主要な判断に使った資料を示します。
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
            <li>AI検索が、よく設計された通常検索より実務上優れるか。</li>
            <li>介護事業所で実際に何分の探索時間を減らせるか。</li>
            <li>古い資料や根拠不足の質問に、十分な精度で回答を控えられるか。</li>
            <li>小規模事業所でも費用対効果が成立するか。</li>
          </ul>
          <p>
            ここは推測で埋めず、同じ質問セットを使った比較実験で確認していきます。
          </p>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — evidence-informed prototype</span>
        <span>最終調査日: 2026-09-25</span>
      </footer>
    </main>
  );
}
