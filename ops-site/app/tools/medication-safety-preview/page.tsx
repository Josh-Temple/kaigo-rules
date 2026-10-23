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
          事故の起きていない平時に、手順・中断・引き継ぎ・変更情報の共有について
          事業所で相談する事項を整理する独自の試作です。本人・薬剤・処方・事故の記録は扱いません。
        </p>
        <p className="medicationBoundary">
          選択内容は自己申告であり、安全性、事故防止、制度適合、実施権限を認証しません。
          本シートは処方・再投与の判断、事故時の医療対応、事故報告の要否・期限、
          事業所の正式な手順に代わるものではありません。サービス別の適用範囲は未検証です。
        </p>
        <p>
          実際に事故や服薬上の疑義が発生している場合、このシートは使わないでください。
          本人の安全確保を優先し、所属先の正式な事故対応手順に従い、
          管理者・関係する医療専門職への連絡、必要な緊急対応と法令・自治体の手続を確認してください。
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
        <span>選択回答を送信・自動保存する機能はありません。通常のページ閲覧計測は別に行われます。</span>
      </footer>
    </main>
  );
}
