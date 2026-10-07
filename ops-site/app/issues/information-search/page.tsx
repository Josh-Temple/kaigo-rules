import type { Metadata } from "next";
import IssueNavigation from "../_components/IssueNavigation";
import IssueFollowThrough from "../_components/IssueFollowThrough";

export const metadata: Metadata = {
  title: "必要な情報を探すのに時間がかかる | 介護業務改善",
  description:
    "制度・通知・Q&A・事業所内資料など、散らばった情報をどう整理し、必要な根拠へ早く到達できるようにするかを、調査結果・機械評価・実務上の改善手順から整理します。",
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
    label: "実装",
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

      <IssueNavigation current="/issues/information-search" />

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">困りごと 01</p>
          <h1>必要な情報を探すのに<br />時間がかかる。</h1>
          <p className="lead">
            制度、通知、Q&A、マニュアル、事業所内資料。情報が増えるほど、
            「どこを見ればよいか」を判断する負担も増えます。
            このページでは、検索ツールを増やす前に確認したい構造と、小さく改善する順序を整理します。
          </p>
          <div className="issueMeta">
            <span>最終更新: 2026-10-07</span>
            <span>主要な機械評価: 2026-09-26</span>
            <span>個人のケア情報は対象外</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">結論</p>
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
            <p className="eyebrow">根拠から分かること</p>
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

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">Machine evaluation</p>
            <h2>固定30クエリでは、本番環境の検索導線を再現できました。</h2>
            <p>
              固定10問について、それぞれ3種類の言い換えを用いた機械検索の再現性評価を本番環境で実行しました。
              更新後本番環境では、検索成功・上位3件への到達・全項目の成功が30/30、参照情報の完全性が10/10でした。
            </p>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">30/30</span>
              <div>
                <h3>検索成功・上位3件への到達・全項目の成功</h3>
                <p>
                  固定評価セットでは、対象ページへの検索導線と必要な構造化参照情報の取得が全検索語で成立しました。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">10/10</span>
              <div>
                <h3>参照情報の完全性</h3>
                <p>
                  10問すべてで正式な原典を含む必要な参照情報が保持されました。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">未検証</span>
              <div>
                <h3>人間の探索時間・使いやすさ</h3>
                <p>
                  人間による人間による現場検証はまだ実施していません。この結果から「探索時間を短縮した」「業務効率が上がった」とは判断しません。
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="section experiment">
          <p className="eyebrow">小さく試す</p>
          <h2>自分の現場では、よく聞かれる10問から測れます。</h2>
          <p>
            まず、職員や事業所から繰り返し出る質問を10問程度選びます。
            それぞれについて「正しい原典」「該当箇所」「条件」「現在の版」を固定し、
            今の探し方でどれくらい負担があるかを測ります。
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

        <section className="section actionToolCta">
          <p className="eyebrow">記入用様式</p>
          <h2>まず、今ある情報の置き場所と正本を並べます。</h2>
          <p>
            よく探す情報について、現在の正本、保管場所、更新責任、見つけるまでの経路、
            重複や古い版の懸念を記入できます。改善策を決める前の棚卸しに使ってください。
          </p>
          <a className="primaryLink" href="/tools/information-inventory">
            情報探索の棚卸しシートを開く →
          </a>
        </section>

        <section className="section boundary">
          <p className="eyebrow">運用上の注意</p>
          <h2>制度情報は、検証状態を確認して使います。</h2>
          <p>
            介護ルールでは、機械取込・独立監査・人手確認を分けて管理しています。
            現在、人手確認が完了していない情報層もあるため、このページから制度上の個別判断を自動的に確定することはしません。
            個別の制度確認では、介護ルール側に表示される検証状態と原典を確認してください。
          </p>
          <IssueFollowThrough issuePath="/issues/information-search" />
        </section>

        <section className="section" id="evidence">
          <div className="sectionHead">
            <p className="eyebrow">根拠</p>
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
          <p className="eyebrow">まだ分からないこと</p>
          <h2>まだ結論を出していないこと</h2>
          <ul>
            <li>固定評価セット以外の実利用検索語でも同じ検索性能が再現するか。</li>
            <li>Kaigo Rulesを使うことで、人間が正しい原典へ到達する時間が短くなるか。</li>
            <li>操作負担や使いやすさが改善するか。</li>
            <li>AI検索が、よく設計された通常検索より実務上優れる領域はどこか。</li>
            <li>小規模事業所でも費用対効果が成立するか。</li>
          </ul>
          <p>
            ここは推測で埋めず、独立した将来検索語や、参加者を確保できた場合の人間による現場検証で確認します。
          </p>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — 根拠に基づく試作版</span>
        <span>最終更新: 2026-09-29</span>
      </footer>
    </main>
  );
}
