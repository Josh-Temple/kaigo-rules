import type { Metadata } from "next";
import { buildPublicPageMetadata } from "../../../lib/site-metadata";
import IssueNavigation from "../_components/IssueNavigation";
import IssueFollowThrough from "../_components/IssueFollowThrough";

export const metadata: Metadata = buildPublicPageMetadata({
  path: "/issues/productivity-utilization",
  title: "稼働率・生産性を改善したい | 介護業務改善",
  description: "介護事業の稼働率と生産性を分け、間接業務、待ち・調整、人員配置、AI活用を、ケアの質と職員負担を損なわない順序で整理します。",
  type: "article",
});

const findings = [
  {
    label: "時間再配分",
    title: "間接業務が減っても、総業務時間が必ず減るわけではない",
    body:
      "厚生労働省の令和7年度実証では、記録・転記や予定調整の時間が減る一方、直接介護・看護・リハ時間が増えた例があります。生産性は「人を減らす」より、時間の使い方がどう変わったかで見る必要があります。",
  },
  {
    label: "11件の試験",
    title: "人員配置への介入の効果は一様ではない",
    body:
      "2026年の迅速に更新される系統的レビューでは11試験が効果推定に寄与し、職種・技能の構成調整は入院を減らす可能性がありましたが根拠の確実性は低い水準でした。生活の質など他結果指標は効果がほぼないか不確かでした。",
  },
  {
    label: "76件の研究",
    title: "人員配置は人数だけでなく技能・現場条件を見る",
    body:
      "2026年の研究範囲を整理するレビューでは76研究を整理し、十分な人員配置と適切な技能・能力を改善の優先事項として示しています。単純な人員削減を生産性改善と同一視しません。",
  },
];

const workTypes = [
  ["A", "直接ケア", "利用者対応、ケア、看護、リハ。単純な削減対象ではない。"],
  ["B", "間接業務", "記録、転記、予定、調整、検索、報告。改善効果を比較的測りやすい。"],
  ["C", "待ち・調整・手戻り", "移動、待ち、承認、再確認、手戻り。業務の流れ設計で減らせる余地がある。"],
  ["D", "緊急時への備え", "急変、欠勤、新人支援、緊急対応、品質確認。余剰時間とみなして削らない。"],
];

const steps = [
  ["0", "時間の使い方を測る", "直接ケア / 間接業務 / 待ち / 手戻りへ分ける。"],
  ["1", "最大の負担要因を一つ選ぶ", "全部を同時にDXせず、最も大きい負担から着手する。"],
  ["2", "廃止・標準化・再利用を先に試す", "自動化の前に、不要作業や重複を減らす。"],
  ["3", "削減時間の行き先を決める", "直接ケア、休憩、研修、品質確認、受け入れ能力のどこへ戻すか決める。"],
  ["4", "必要ならAI / 最適化を加える", "勤務・予定の作成支援、経路案の作成、可視化など限定用途で比較する。"],
];

const sources = [
  {
    title: "令和7年度 介護テクノロジー等による生産性向上の取組に関する調査及び効果測定事業",
    note: "厚生労働省。記録・転記、訪問予定調整等の小規模実証。業務の流れ変更との複合介入として読む。",
    href: "https://www.mhlw.go.jp/content/12300000/001690572.pdf",
  },
  {
    title: "The impact of staffing structures in long-term care homes on the quality of work-life and work outcomes of care-workers",
    note: "2026年の研究範囲を整理する記述的レビュー。76研究を整理し、人員配置の構造と職員への影響を検討。",
    href: "https://pubmed.ncbi.nlm.nih.gov/41319443/",
  },
  {
    title: "Effects of Structural Workforce Interventions on Resident and Staff Outcomes in Long-Term Care Facilities",
    note: "2026年の迅速に更新される系統的レビュー。11試験の効果推定、実装を妨げる条件・支える条件も整理。",
    href: "https://pubmed.ncbi.nlm.nih.gov/41956438/",
  },
  {
    title: "令和8年度介護事業経営実態調査",
    note: "2026年実施。集計結果は介護給付費分科会で公表予定。収支・コスト構造の課題は結果公表後の更新を優先。",
    href: "https://r8-keiei.kaigo-survey.mhlw.go.jp/",
  },
];

export default function ProductivityUtilizationIssuePage() {
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

      <IssueNavigation current="/issues/productivity-utilization" />

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">困りごと 05</p>
          <h1>稼働率・生産性を<br />改善したい。</h1>
          <p className="lead">
            稼働率を上げることと、生産性を上げることは同じではありません。
            まず、間接業務や待ち・調整を減らし、浮いた時間をどこへ戻すかを決めます。
            人員配置削減だけを目的にしない形で整理します。
          </p>
          <div className="issueMeta">
            <span>初版: 2026-09-30</span>
            <span>対象: 作業時間の配分・人員配置・予定・受け入れ能力</span>
            <span>全サービス共通の理想稼働率は設定しない</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">結論</p>
          <h2>生産性は、「少ない人数で回すこと」ではありません。</h2>
          <p className="summaryLead">
            最初に見るのは、直接ケア、記録・転記、調整、待ち、やり直しへ時間がどう配分されているかです。
            間接業務が減った時間を、直接ケア、休憩、研修、品質確認、受け入れ能力のどこへ戻すかまで決めます。
          </p>
          <p>
            稼働率はサービスごとに受け入れ能力の意味が違うため、共通の目標値は置きません。
            通所、訪問、入所などで指標を分ける前提にします。
          </p>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">根拠から分かること</p>
            <h2>「削減時間」だけを成功指標にしません。</h2>
            <p>
              生産性、品質、職員への影響を同時に見ます。小規模実証やレビューの結果を、全事業所へそのまま一般化しません。
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
            <p className="eyebrow">Time allocation</p>
            <h2>時間を四つに分けます。</h2>
            <p>「空いている時間」に見えても、緊急対応や支援のために必要な余力があります。</p>
          </div>
          <ol className="levelList">
            {workTypes.map(([number, title, body]) => (
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
            <h2>測ってから、一つだけ変えます。</h2>
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
            <p className="eyebrow">Utilization</p>
            <h2>稼働率は、サービス種別ごとに別の問題です。</h2>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">通所</span>
              <div>
                <h3>定員・営業日・利用枠</h3>
                <p>キャンセル、曜日差、送迎、職員配置を含めて受け入れ能力を考えます。</p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">訪問</span>
              <div>
                <h3>職員時間・移動・資格・希望時間帯</h3>
                <p>単純な予約枠ではなく、地理と制約条件が受け入れ能力を決めます。</p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">入所</span>
              <div>
                <h3>ベッド稼働率・入退所の流れ</h3>
                <p>空床だけでなく、入退所調整、医療対応、人員配置との組み合わせで見ます。</p>
              </div>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">AIを使う方法・使わない方法</p>
            <h2>最適化の前に、業務の流れを単純にします。</h2>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">非AI</span>
              <div>
                <h3>標準化・役割分担・情報の再利用</h3>
                <p>
                  予定のルール整理、会議削減、様式統合、配置変更、まとめて処理などで十分なら、
                  AIや高度な最適化を追加しません。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">AI</span>
              <div>
                <h3>勤務・予定の作成支援・経路案の作成・可視化</h3>
                <p>
                  AIや最適化を使う場合も、提案・補助から始め、人員配置の最終決定と例外判断は人間に残します。
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="section experiment">
          <p className="eyebrow">小さく試す</p>
          <h2>1週間の作業時間の内訳確認から始めます。</h2>
          <p>2〜3職種だけを対象にし、大規模なシステム導入前に負担要因を特定します。</p>
          <div className="experimentGrid">
            <div>
              <span>01</span>
              <strong>分類</strong>
              <p>直接ケア、間接業務、待ち、手戻りへ時間を分ける。</p>
            </div>
            <div>
              <span>02</span>
              <strong>最大負担を一つ選ぶ</strong>
              <p>最も大きい間接業務・待ち・調整だけを対象にする。</p>
            </div>
            <div>
              <span>03</span>
              <strong>最小変更</strong>
              <p>廃止、標準化、再利用、自動化の順に試す。</p>
            </div>
            <div>
              <span>04</span>
              <strong>再測定</strong>
              <p>対象時間、直接ケア、残業、手戻り、職員の負担を比較する。</p>
            </div>
          </div>
          <p className="noPrint">
            <a className="primaryLink" href="/tools/work-time-review">業務時間・待ち・間接業務を棚卸しする →</a>
          </p>
        </section>

        <section className="section boundary">
          <p className="eyebrow">運用上の注意</p>
          <h2>「効率化」が、必要な余力の削減にならないようにします。</h2>
          <p>
            急変、欠勤、新人支援、相談、品質確認のための時間は、単なる空き時間とは限りません。
            人員配置削減、休憩削減、記録省略、相談抑制だけで数字を改善しないことを前提にします。
          </p>
          <p>
            人員配置に制度上の要件がある場合は、Kaigo Rules側の原典・検証状態で確認します。
          </p>
          <IssueFollowThrough issuePath="/issues/productivity-utilization" />
        </section>

        <section className="section" id="evidence">
          <div className="sectionHead">
            <p className="eyebrow">根拠</p>
            <h2>主な根拠</h2>
            <p>日本の公的実証と、長期ケアの職員に関するレビューを分けて扱います。</p>
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
            <li>サービス種別ごとの適切な受け入れ能力 / 稼働状況指標。</li>
            <li>稼働率と職員の負担・品質の関係。</li>
            <li>予定の最適化の独立評価と実装費用。</li>
            <li>生産性改善が残業・欠勤・離職へどう影響するか。</li>
            <li>令和8年度介護事業経営実態調査の集計結果を踏まえた収支との接続。</li>
          </ul>
          <p>ここは単一施設の成功事例から一般化せず、サービス種別ごとのデータと最新公的調査で更新します。</p>
        </section>
      </article>

      <footer>
        <span>介護業務改善 — 根拠に基づく試作版</span>
        <span>初版: 2026-09-30</span>
      </footer>
    </main>
  );
}
