import type { Metadata } from 'next';
import DocumentationWorksheet from './worksheet';
import ToolFollowThrough from '../_components/ToolFollowThrough';

export const metadata: Metadata = {
  title: '記録業務の見直しシート | 介護業務改善',
  description: '記録・転記・探索・後追い記録と確認修正の時間を分け、一つの改善を前後で比較するシート。',
};

export default function DocumentationReviewPage() {
  return <main className="worksheetPage">
    <header className="siteHeader">
      <a className="brand" href="/">介護業務改善</a>
      <nav aria-label="主要ナビゲーション"><a href="/issues/documentation">記録・文書作成へ戻る</a></nav>
    </header>
    <section className="issueHero">
      <p className="eyebrow">改善を試す</p>
      <h1>記録業務の<br />見直しシート</h1>
      <p className="lead">同じ種類の業務を、変更前と変更後で測ります。まず1週間、作業ごとに時間を記録し、下の欄に合計を入力してください。改善策は一つに絞ります。</p>
      <p>これは業務改善の記入用様式です。制度上必要な記録を省略できるかを判定するものではありません。</p>
    </section>
    <DocumentationWorksheet />
    <ToolFollowThrough issuePath="/issues/documentation" toolPath="/tools/documentation-review" />
    <footer><span>記入用様式 / 2026-10-02</span><a href="/issues/documentation#evidence">改善手順の根拠へ戻る</a></footer>
  </main>;
}
