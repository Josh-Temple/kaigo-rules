import type { Metadata } from 'next';
import ActionInventoryWorksheet, { type ActionField } from '../_components/ActionInventoryWorksheet';

export const metadata: Metadata = {
  title: '引き継ぎ情報・研修資源の正本整理シート | 介護業務改善',
  description: '新任者が必要な情報、正本、更新責任、口頭伝承への依存、短い教材にできる部分、人に残す判断を整理する記入用シート。',
};

const fields: ActionField[] = [
  { key: 'need', label: '新任者が最初に必要な情報', placeholder: '例: 日々の報告手順、緊急時の連絡経路', wide: true },
  { key: 'ask', label: '誰に聞かないと分からないか', placeholder: '役割・担当で記入。個人名は不要' },
  { key: 'knowledgeType', label: '知識の種類', kind: 'select', options: ['文書化できる知識', '更新責任が曖昧な知識', '経験知・専門判断'] },
  { key: 'sourceState', label: '正本の状態', kind: 'select', options: ['正本がある', '候補はあるが要確認', '正本がない'] },
  { key: 'owner', label: '更新責任', placeholder: '部署・役割・会議体など' },
  { key: 'gap', label: '研修資料と実運用の差', placeholder: '資料と現場運用で違う点', kind: 'textarea' },
  { key: 'faq', label: 'FAQ化できる質問', placeholder: '反復して聞かれる内容', kind: 'textarea' },
  { key: 'oral', label: '口頭伝承に依存している箇所', placeholder: '口頭でしか伝わっていない部分', kind: 'textarea' },
  { key: 'shortLearning', label: '短い教材にできる部分', placeholder: '確認一覧、短い手引き、短い動画等', kind: 'textarea' },
  { key: 'humanOnly', label: '人にしか教えられない部分', placeholder: '例外対応、専門判断、対人調整等', kind: 'textarea', wide: true },
];

export default function TrainingHandoverInventoryPage() {
  return (
    <main className="worksheetPage actionToolPage">
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="/issues/training-handover">教育・引き継ぎへ戻る</a>
          <a href="/issues/training-handover#evidence">根拠</a>
        </nav>
      </header>

      <section className="issueHero">
        <p className="eyebrow">改善を試す</p>
        <h1>引き継ぎ情報・研修資源の<br />正本整理シート</h1>
        <p className="lead">
          新任者が必要な情報を並べ、正本があるもの、更新責任が曖昧なもの、
          経験知・専門判断として人から学ぶべきものを分けます。
          FAQや短い教材に移せる部分だけを選ぶための様式です。
        </p>
        <p>
          AI教材生成を前提にしません。正式な手順として採用してよい内容かを確認し、
          個別ケア判断や例外対応などは人が教える経路を残します。
        </p>
      </section>

      <ActionInventoryWorksheet
        itemLabel="引き継ぎ項目"
        fields={fields}
        scopeLabel="今回棚卸しする職種・場面"
        scopePlaceholder="例: 新任介護職員の最初の2週間"
        trialLabel="小さく試す範囲・期間"
        trialPlaceholder="例: よく聞かれる上位5項目を2週間"
        noteLabel="最初に整えるもの"
        notePlaceholder="例: 上位5問をFAQ化し、正本リンクと更新担当を付ける"
      />

      <section className="section boundary">
        <p className="eyebrow">制度確認</p>
        <h2>研修資料に制度要件を含めるときは、原典を確認します。</h2>
        <p>
          Kaigo Ops内の説明だけで義務・要件を確定しません。サービス種別に応じた一次資料と検証状態を確認してください。
        </p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
          介護ルールで制度・原典を確認する →
        </a>
      </section>

      <footer>
        <span>記入用様式 / 2026-10-07</span>
        <a href="/issues/training-handover#evidence">教育・引き継ぎの根拠へ戻る</a>
      </footer>
    </main>
  );
}
