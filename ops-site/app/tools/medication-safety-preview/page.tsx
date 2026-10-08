import type { Metadata } from "next";
import { notFound } from "next/navigation";
import MedicationSafetyWorksheet from "./worksheet";
import "./preview.css";

export const dynamic = "force-dynamic";

// The route is inaccessible by default, even if a draft PR is accidentally merged.
// Enabling it on a *preview* deployment creates an externally reachable preview,
// not a private page: access control and expert review remain separate requirements.
export const metadata: Metadata = {
  title: "服薬業務の安全点検シート（試作） | 介護業務改善",
  description: "個別の服薬・医療判断を行わず、業務工程と相談事項だけを整理する試作です。",
  robots: { index: false, follow: false, nocache: true },
};

export default function MedicationSafetyPreviewPage() {
  if (process.env.MEDICATION_SAFETY_PREVIEW !== "enabled") notFound();

  return (
    <main className="medicationPreview worksheetPage">
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション"><a href="/">公開中の課題へ戻る</a></nav>
      </header>
      <section className="issueHero">
        <p className="eyebrow">未公開の試作 / 専門職レビュー前</p>
        <h1>服薬業務の安全点検シート</h1>
        <p className="lead">
          服薬業務のどの工程で、手順・中断・引き継ぎ・変更情報の確認が必要かを整理します。
          利用者ごとの薬や服薬内容を入力するものではありません。
        </p>
        <p className="medicationBoundary">
          このシートは業務の点検支援です。薬の投与判断、事故時の医療対応、事故報告の判断、
          事業所の正式な手順に代わるものではありません。内容とサービス別の適用範囲は未検証です。
        </p>
        <p>
          実際に事故や疑義が発生した場合は、このシートを使って判断せず、
          所属先の事故対応手順に従い、管理者・関係する医療専門職へ連絡し、必要な緊急対応を行ってください。
        </p>
      </section>
      <MedicationSafetyWorksheet />
      <section className="section boundary">
        <h2>利用できる範囲</h2>
        <p>
          施設での考え方を、訪問・通所・居住系の各サービスにそのまま当てはめないでください。
          各サービスの手順、関係職種の権限、自治体等への報告条件はここで判定しません。
        </p>
        <p>薬剤名、病名、利用者・職員の氏名、実際の事故内容、施設の非公開情報は入力しないでください。</p>
        <a className="textLink" href="https://kaigo-rules.vercel.app/databases/search" target="_blank" rel="noreferrer">
          介護ルールで一次資料を探す →
        </a>
      </section>
      <footer>
        <span>試作 / 専門職未確認 / 公開判定未実施</span>
        <span>回答はサーバーへ送信・保存しません。画面を閉じると失われます。</span>
      </footer>
    </main>
  );
}
