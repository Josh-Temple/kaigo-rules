import type { Metadata } from "next";
import WorkTimeWorksheet from "./worksheet";
import ToolFollowThrough from "../_components/ToolFollowThrough";

export const metadata: Metadata = {
  title: "業務時間・待ち・間接業務の棚卸しシート | 介護業務改善",
  description:
    "直接ケア、必要な記録、移動、待ち、探索、調整、転記などを分け、小さな業務改善を前後で確認する記入シート。",
};

export default function WorkTimeReviewPage() {
  return (
    <main className="worksheetPage">
      <header className="siteHeader">
        <a className="brand" href="/">介護業務改善</a>
        <nav aria-label="主要ナビゲーション">
          <a href="/issues/productivity-utilization">稼働率・生産性へ戻る</a>
        </nav>
      </header>

      <section className="issueHero">
        <p className="eyebrow">改善を試す</p>
        <h1>業務時間・待ち・間接業務の<br />棚卸しシート</h1>
        <p className="lead">
          直接ケア、必要な記録、移動、待ち、探索、調整、転記などを分け、
          どこに改善余地があるかを業務単位で確認します。
        </p>
        <p>
          職員個人の監視・ランキングや、人員削減の判断に使うためのツールではありません。
          時間差だけで改善成功とは判定しません。
        </p>
      </section>

      <WorkTimeWorksheet />

      <ToolFollowThrough issuePath="/issues/productivity-utilization" toolPath="/tools/work-time-review" />

      <footer>
        <span>記入用様式 / 2026-10-07</span>
        <a href="/issues/productivity-utilization#evidence">改善手順の根拠へ戻る</a>
      </footer>
    </main>
  );
}
