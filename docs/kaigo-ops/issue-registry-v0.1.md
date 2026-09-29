# Kaigo Ops Issue Registry v0.1

更新日: 2026-09-30  
状態: Active

## 目的

Kaigo Opsの公開Issueを、トップページ・横断navigation・将来の検索/計測で別々に定義しない。

実装上の正本は:

`ops-site/app/issues/registry.ts`

とする。

## 公開Issueの最小schema

各Issueは次を持つ。

| field | 用途 |
| --- | --- |
| `number` | 公開順序・navigation表示 |
| `title` | 利用者向けの困りごと表現 |
| `shortTitle` | 横断navigationの短縮表示 |
| `body` | 一覧での要約 |
| `status` | 現在の公開状態 |
| `href` | canonical public route |
| `group` | 粗い分類 |
| `keywords` | 軽量検索用の同義語・関連語 |

## group v0.1

現時点では分類を増やしすぎない。

- **日常業務**
  - 情報探索
  - 記録・文書
  - 問い合わせ・連携
- **人材・組織**
  - 職員教育・引き継ぎ
- **経営・生産性**
  - 稼働率・生産性

これは固定taxonomyではない。5 Issueで利用して、必要な分離が見えた場合だけ変更する。

## 検索 v0.1

トップページの検索は、全文検索エンジンではなく公開Issueの発見支援を目的とする。

検索対象:

- title
- shortTitle
- body
- group
- keywords

対象外:

- Evidence本文の全文
- 外部Source本文
- Kaigo Rulesの制度検索
- 個人情報
- AIによるsemantic retrieval

5 Issueの段階では、検索infraを増やさずclient-side filteringで十分かを確認する。

## 利用計測 v0.1

Vercel Web Analyticsのclient codeはproductionへ導入済み。ただし2026-09-30時点ではproject-level Web Analyticsの有効化は未確認で、tracking script endpointは404のため、page view収集開始前の状態と扱う。

v0.1で見るもの:

1. トップページpage view
2. Issue別page view
3. routeごとの閲覧偏り
4. referrer / device等、Vercel Web Analyticsが匿名化・集約して提供する標準指標

現段階ではcustom eventを追加しない。

そのため、以下はまだ直接計測しない。

- 検索語
- group filter click
- トップページ上のIssue click
- 原典リンクclick
- Kaigo Rules遷移
- 0件検索

まずpage viewだけでIssue需要の偏りを確認し、追加eventが意思決定に必要と分かった場合にだけ拡張する。

検索語を将来eventとして扱う場合も、raw queryをそのまま保存せず、
個人情報・利用者情報を送らない設計を優先する。

## 変更ルール

- Issueを追加する場合はregistryへ1件追加し、ページを作成する。
- トップページとIssueNavigationへ個別に重複追加しない。
- group / keywordsは利用者の発見支援用であり、Evidenceの結論を表す分類にはしない。
- taxonomyを増やす前に、既存分類で利用上の問題があるかを確認する。
