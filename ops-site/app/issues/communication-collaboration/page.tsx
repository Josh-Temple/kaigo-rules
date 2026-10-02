import type { Metadata } from "next";
import IssueNavigation from "../_components/IssueNavigation";

export const metadata: Metadata = {
  title: "問い合わせ・連携の負担が大きい | 介護業務改善",
  description:
    "電話、FAX、メール、ケアプラン共有、確認の往復など、介護現場の問い合わせ・連携負担を、業務の流れ整理、自分で確認できる仕組み、data exchange、必要に応じたAI補助の順に改善する方法を整理します。",
};

const findings = [
  {
    label: "54.5%",
    title: "郵送・FAX等の共有に時間がかかるという回答",
    body:
      "厚生労働省のケアプランデータ連携に関する調査の一部対象では、ケアプラン・提供票の共有について54.5%が郵送・FAX等の共有に時間がかかると回答しました。小規模sampleの箇所であり、全国値としては扱いません。",
  },
  {
    label: "Network",
    title: "片側だけの導入では価値が出にくい",
    body:
      "同じ調査では、利用意向が低い回答者で「普及率が低くメリットが小さい」が挙げられました。複数事業所をまたぐdata exchangeは、自施設だけの改善とは違い、相手側の採用状況が実装条件になります。",
  },
  {
    label: "16 studies",
    title: "連携方法は複数あり、万能な一つは見えていない",
    body:
      "2026年のsystematic reviewでは、LTC physicianとmedical specialistの連携16研究を整理し、teleconsultation、on-site consultation、multidisciplinary collaborationを確認しました。研究設計・outcomeの異質性が大きく、どの要素が最も有効かは確定していません。",
  },
];

const types = [
  ["A", "定型問い合わせ", "様式、締切、提出先、status確認。FAQ、検索、status表示で減らしやすい。"],
  ["B", "定型的な情報共有", "ケアプラン、提供票、報告など。入力項目をそろえた様式やdata exchangeを検討する。"],
  ["C", "判断を伴う相談", "例外対応、状態変化、専門職間調整。人間への担当者への引き継ぎを前提にする。"],
  ["D", "緊急連絡", "急変・事故など。通常queueと分け、即時連絡経路を維持する。"],
];

const steps = [
  ["0", "問い合わせを分類する", "誰から何について何回来るかをcategoryで把握する。"],
  ["1", "反復問い合わせを減らす", "FAQ、guide、status表示など自分で確認できる仕組みへ移せるものを移す。"],
  ["2", "minimum information setを決める", "連携先ごとに、必須・任意・緊急時の情報を分ける。"],
  ["3", "連絡手段を用途別にする", "緊急、定型提出、非同期確認、status確認の経路を分ける。"],
  ["4", "必要ならシステム・AIを加える", "連携相手の導入状況を確認し、AIは分類・要約・返信の下書き等の補助から試す。"],
];

const sources = [
  {
    title: "介護事業所におけるデータ連携による生産性向上に関する調査研究等一式 報告書",
    note: "厚生労働省。ケアプラン・提供票共有の紙・FAX負担と、連携相手の導入状況の条件を確認。",
    href: "https://www.mhlw.go.jp/content/12300000/R5_ICT_houkokusyo.pdf",
  },
  {
    title: "ICT導入支援事業 令和3年度 導入効果報告取りまとめ",
    note: "厚生労働省。情報共有に関する導入事業所の自己申告。因果効果とは扱わない。",
    href: "https://www.mhlw.go.jp/content/12300000/001124036.pdf",
  },
  {
    title: "Swaying Information About Care: Information-Sharing Challenges in Transitional Care of Older Adults in Japan",
    note: "2026年の日本研究。送り手・受け手で必要情報が異なることや、timeliness・個別性の課題を整理。",
    href: "https://link.springer.com/article/10.1007/s10823-026-09563-2",
  },
  {
    title: "The Use of Health Information Exchange to Augment Patient Handoff in Long-Term Care",
    note: "22研究のsystematic review。業務の流れ integration、組織条件、missing dataなどを整理。",
    href: "https://pmc.ncbi.nlm.nih.gov/articles/PMC6170191/",
  },
  {
    title: "Impact of interprofessional collaboration between long-term care physicians and medical specialists",
    note: "2026年のsystematic review。16研究、3類型の連携介入。heterogeneityが大きく追加研究が必要。",
    href: "https://pubmed.ncbi.nlm.nih.gov/41329454/",
  },
];

export default function CommunicationCollaborationIssuePage() {
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

      <IssueNavigation current="/issues/communication-collaboration" />

      <article className="issueDetail">
        <section className="issueHero">
          <p className="eyebrow">困りごと 04</p>
          <h1>問い合わせ・連携の<br />負担が大きい。</h1>
          <p className="lead">
            電話、FAX、メール、システム、確認の折り返し。
            連絡手段が増えても、必要な情報が一度で届かなければ往復は減りません。
            問い合わせそのものを減らし、必要な相談は残す順序で整理します。
          </p>
          <div className="issueMeta">
            <span>初版: 2026-09-30</span>
            <span>対象: 問い合わせ・情報共有・多職種 / 多事業所連携</span>
            <span>緊急連絡・個別判断は自動化対象外</span>
          </div>
        </section>

        <section className="section issueSummary">
          <p className="eyebrow">結論</p>
          <h2>減らすのは「必要な相談」ではなく、不要な往復です。</h2>
          <p className="summaryLead">
            まず、問い合わせと連携を種類ごとに分けます。定型確認はFAQやstatus表示へ、
            定型共有は入力項目をそろえた様式やdata exchangeへ、判断を伴う相談は人間へ、
            緊急連絡は独立した経路へ残します。
          </p>
          <p>
            連携systemは自施設だけ導入しても価値が出ない場合があります。
            相手側の採用、二重入力、代替手順まで含めて判断し、AIは分類・要約・下書きなどの補助から始めます。
          </p>
        </section>

        <section className="section">
          <div className="sectionHead">
            <p className="eyebrow">根拠から分かること</p>
            <h2>連携負担は、連絡手段より業務の流れで決まります。</h2>
            <p>
              数値は調査対象・sample条件に依存します。全国の一般値や単独systemの効果としては扱いません。
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
            <p className="eyebrow">Four types</p>
            <h2>問い合わせ・連携を四つに分けます。</h2>
            <p>全部を同じ受信窓口、同じAI、同じシステムへ流さないことが最初の設計です。</p>
          </div>
          <ol className="levelList">
            {types.map(([number, title, body]) => (
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
            <h2>窓口を増やす前に、問い合わせを減らします。</h2>
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
            <h2>AIより先に、連絡手段と責任分担を整理します。</h2>
          </div>
          <div className="findingList">
            <div className="findingRow">
              <span className="findingLabel">非AI</span>
              <div>
                <h3>FAQ・shared 受信窓口・入力項目をそろえた様式・data exchange</h3>
                <p>
                  status page、contact matrix、担当者への引き継ぎ rule、定型様式などで
                  反復確認や二重連絡を減らせるなら、生成AIを追加しません。
                </p>
              </div>
            </div>
            <div className="findingRow">
              <span className="findingLabel">AI</span>
              <div>
                <h3>分類・要約・返信の下書きから</h3>
                <p>
                  AIを使う場合は、問い合わせ分類、FAQ候補、長文要約、返信下書き、担当者への引き継ぎ候補などから試します。
                  個別ケア判断、医療判断、制度上の確定判断はAI単独で返しません。
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="section experiment">
          <p className="eyebrow">小さく試す</p>
          <h2>2週間、問い合わせの「往復」を測ります。</h2>
          <p>
            通話内容や個人情報を保存する必要はありません。categoryと処理負担だけで十分です。
          </p>
          <div className="experimentGrid">
            <div>
              <span>01</span>
              <strong>記録</strong>
              <p>theme、連絡手段、回答時間、往復回数を記録する。</p>
            </div>
            <div>
              <span>02</span>
              <strong>分類</strong>
              <p>eliminate、自分で確認できる仕組み、様式をそろえた情報交換、human judgment、emergencyに分ける。</p>
            </div>
            <div>
              <span>03</span>
              <strong>上位3つだけ改善</strong>
              <p>FAQ、form、status表示、連絡手段整理など最小変更を入れる。</p>
            </div>
            <div>
              <span>04</span>
              <strong>再測定</strong>
              <p>件数、往復回数、response time、二重入力、担当者への引き継ぎを比較する。</p>
            </div>
          </div>
        </section>

        <section className="section boundary">
          <p className="eyebrow">運用上の注意</p>
          <h2>問い合わせ削減が、相談抑制にならないようにします。</h2>
          <p>
            自分で確認できる仕組みや自動応答を強くしすぎると、必要な相談まで止まる可能性があります。
            急変・事故・専門判断などは通常queueと分け、すぐ人間へ到達できる経路を維持します。
          </p>
          <p>
            制度上の判断が必要な問い合わせは、Kaigo Ops内の回答だけで確定せず、
            介護ルール側の原典と検証状態へ接続します。
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
              日本の公的調査、国内研究、systematic reviewを区別して扱います。
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
            <li>日本の介護事業所で、問い合わせ対応に実際どれだけ時間が使われているか。</li>
            <li>ケアマネジャー・サービス事業所間で、同じ情報が何回往復しているか。</li>
            <li>data exchangeのcurrent adoptionが、どの程度network valueを生んでいるか。</li>
            <li>family communicationでは、どの連絡手段設計が負担と満足度を両立するか。</li>
            <li>AIによる問い合わせの振り分け・返信の下書きの修正時間まで含めて効果が残るか。</li>
          </ul>
          <p>
            ここは推測で埋めず、実際の利用記録、公的調査、独立研究が得られた段階で更新します。
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
