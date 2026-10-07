import type { Metadata } from "next";
import CommunicationWorksheet from "./worksheet";

export const metadata: Metadata = {
  title: "問い合わせ・確認往復の棚卸しシート | 介護業務改善",
  description:
    "問い合わせ、確認の往復、連絡手段、必要情報、担当へのつなぎ方を整理し、小さな改善を試すための記入シート。",
};

export default function CommunicationReviewPage() {
  return (
    <main className="worksheetPage">
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="/issues/communication-collaboration">問い合わせ・連携へ戻る</a>
        </nav>
      </header>

      <section className="issueHero">
        <p className="eyebrow">改善を試す</p>
        <h1>問い合わせ・確認往復の<br />棚卸しシート</h1>
        <p className="lead">
          よく発生する問い合わせを3つまで選び、何が足りずに往復しているかを整理します。
          自動応答やAIを前提にせず、まずFAQ、様式、連絡先、担当へのつなぎ方で減らせる往復を探します。
        </p>
        <p>
          急変・事故・専門判断など、すぐ人へつなぐべき連絡を減らすためのツールではありません。
        </p>
      </section>

      <CommunicationWorksheet />

      <footer>
        <span>記入用様式 / 2026-10-07</span>
        <a href="/issues/communication-collaboration#evidence">改善手順の根拠へ戻る</a>
      </footer>
    </main>
  );
}
