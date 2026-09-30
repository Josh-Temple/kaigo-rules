import Link from "next/link";
import { notFound } from "next/navigation";
import VerificationSummary from "../../../../../components/verification-summary";
import standardsData from "../../../../../data/services/dayrehab/standards-index.json";

const standards = standardsData as any;

export function generateStaticParams() {
  return standards.articles.map((item: any) => ({ article: item.article_number }));
}

export default async function DayrehabRuleArticlePage({
  params,
}: {
  params: Promise<{ article: string }>;
}) {
  const { article } = await params;
  const item = standards.articles.find((row: any) => row.article_number === article);
  if (!item) notFound();

  return (
    <article className="answer-page rules-page">
      <p className="eyebrow">通所リハビリテーション / {item.section}</p>
      <h1>{item.article_label} {item.heading}</h1>

      <div className="notice">
        <strong>インデックス公開・本文確認中</strong><br />
        このページは条文の存在・位置・見出しを確認するための公開プレビューです。本文全文は、共有e-Govコーパスへの統合と独立再照合が完了するまで掲載しません。
      </div>

      <VerificationSummary layerId="ordinance37-dayrehab-preview" />

      <section className="section">
        <h2>記録している情報</h2>
        <dl className="rule-meta">
          <div><dt>章</dt><dd>{standards.chapter}</dd></div>
          <div><dt>節</dt><dd>{item.section}</dd></div>
          <div><dt>出典位置</dt><dd>{item.source_locator}</dd></div>
          <div><dt>改正表示</dt><dd>{item.amendment_marker || "—"}</dd></div>
          <div><dt>抽出状態</dt><dd>Committer受理済み</dd></div>
          <div><dt>現行性</dt><dd>未確定（GAP）</dd></div>
          <div><dt>人手確認</dt><dd>未実施</dd></div>
        </dl>
      </section>

      <section className="section">
        <h2>原文を確認する</h2>
        <p>
          <a href="https://laws.e-gov.go.jp/law/411M50000100037" target="_blank" rel="noreferrer">e-Gov法令検索</a>
        </p>
        <p>
          <a href="https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0" target="_blank" rel="noreferrer">厚生労働省 法令等データベース</a>
        </p>
        <p className="meta">
          本サイトでは、一次資料の版・現行性を独立に確認できるまで本文を確定表示しません。
        </p>
      </section>

      <p><Link href="/services/dayrehab/rules">基準省令一覧へ戻る</Link></p>
    </article>
  );
}
