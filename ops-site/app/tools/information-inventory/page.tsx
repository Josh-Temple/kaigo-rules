import type { Metadata } from 'next';
import ActionInventoryWorksheet, { type ActionField } from '../_components/ActionInventoryWorksheet';
import ToolFollowThrough from '../_components/ToolFollowThrough';

export const metadata: Metadata = {
  title: '情報探索の棚卸しシート | 介護業務改善',
  description: 'よく探す情報について、正本、保管場所、更新責任、探索経路、重複や古い版のリスクを整理する記入用シート。',
};

const fields: ActionField[] = [
  { key: 'information', label: 'よく探す情報', placeholder: '例: 加算の要件、事業所内の申請手順', wide: true },
  { key: 'source', label: '現在の正本', placeholder: '不明なら空欄のまま' },
  { key: 'location', label: '保管場所・入口', placeholder: '例: 共有フォルダ、紙ファイル、Web' },
  { key: 'owner', label: '更新責任者・担当', placeholder: '役割名で記入。個人名は不要' },
  { key: 'route', label: '見つけるまでの経路', placeholder: '例: 共有→規程→最新版', kind: 'textarea' },
  { key: 'duplicates', label: '重複保管・別版', placeholder: '同じ情報が別の場所にもあるか', kind: 'textarea' },
  { key: 'staleRisk', label: '古い版を参照する懸念', placeholder: '版・更新日が分からない等', kind: 'textarea' },
  { key: 'workaround', label: '人への問い合わせで補っている箇所', placeholder: 'どこで詳しい人に聞くか', kind: 'textarea' },
  { key: 'nextEntry', label: '改善後の入口候補', placeholder: '例: 正本リンク一覧、FAQ、検索入口', kind: 'textarea', wide: true },
];

export default function InformationInventoryPage() {
  return (
    <main className="worksheetPage actionToolPage">
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="/issues/information-search">情報探索へ戻る</a>
          <a href="/issues/information-search#evidence">根拠</a>
        </nav>
      </header>

      <section className="issueHero">
        <p className="eyebrow">改善を試す</p>
        <h1>情報探索の<br />棚卸しシート</h1>
        <p className="lead">
          検索ツールを増やす前に、よく探す情報の正本・保管場所・更新責任・探索経路を並べます。
          重複や古い版、人への問い合わせに頼っている箇所を見つけ、改善する入口を一つ選ぶための様式です。
        </p>
        <p>
          制度情報を扱う場合はKaigo Rulesや一次資料を確認先候補にできますが、
          事業所内文書の正本をこのシートが決めることはありません。
        </p>
      </section>

      <ActionInventoryWorksheet
        itemLabel="情報"
        fields={fields}
        scopeLabel="今回棚卸しする範囲"
        scopePlaceholder="例: 管理者が月1回以上探す制度・運営情報"
        trialLabel="小さく試す範囲・期間"
        trialPlaceholder="例: 上位5項目だけ、2週間"
        noteLabel="最初に変える入口"
        notePlaceholder="例: 上位5項目の正本リンクと更新責任だけを1ページにまとめる"
      />

      <section className="section boundary">
        <p className="eyebrow">制度確認</p>
        <h2>制度上必要な内容は、原典へ戻って確認します。</h2>
        <p>
          Kaigo Opsは制度要件を確定しません。制度情報の整理では、サービス種別や適用範囲に応じて一次資料を確認してください。
        </p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/" target="_blank" rel="noreferrer">
          介護ルールで制度・原典を確認する →
        </a>
      </section>

      <ToolFollowThrough issuePath="/issues/information-search" toolPath="/tools/information-inventory" />

      <footer>
        <span>記入用様式 / 2026-10-07</span>
        <a href="/issues/information-search#evidence">情報探索の根拠へ戻る</a>
      </footer>
    </main>
  );
}
