# Research Protocol for 介護業務改善

更新日: 2026-09-22
状態: Draft protocol

## 1. 調査の目的

公開情報を大量に集めることではなく、介護現場のIssueについて、

- 何が分かっているか
- 何がまだ分からないか
- どの条件で改善策が機能しやすいか
- どの条件では機能しにくいか
- 日本で試す場合の最小行動は何か

を再現可能な形で整理する。

## 2. 調査対象

優先順位:

1. 一次資料・公的資料
2. 査読論文、学術レビュー
3. 独立した調査・評価
4. 事業者・企業の導入事例
5. ベンダー事例
6. 報道・専門メディア
7. 補助的なコミュニティ情報

企業・ベンダー資料は有用だが、効果主張を独立検証済みの事実として扱わない。

## 3. 地理的範囲

初期段階から日本に限定しない。

対象例:

- Japan
- United States
- United Kingdom
- Australia
- Canada
- Nordic countries
- Singapore
- South Korea
- other relevant regions

検索語は介護だけでなく、以下を含める。

- long-term care
- aged care
- elder care
- senior living
- home care
- home health
- nursing home
- care workforce
- care technology
- digital health
- AI in long-term care
- robotics in elder care

## 4. Evidence register

### 論文・研究

記録項目:

- title
- authors
- year
- DOI / URL
- country
- setting
- study design
- sample size
- population
- intervention
- comparator
- outcome
- main result
- limitations
- funding / conflicts
- applicability to Japanese care
- checked_at

### 企業・事業所事例

記録項目:

- organization
- country
- service type
- scale
- pain point
- prior workflow
- intervention
- technology
- vendor
- implementation period
- reported outcome
- measurement method
- adoption / usage condition
- cost if public
- constraints
- failures / rollback if public
- source type
- independent verification
- source URL
- checked_at

### 公的資料

記録項目:

- organization
- jurisdiction
- document title
- publication date
- scope
- relevant findings
- definitions
- update cycle
- source URL
- checked_at

## 5. Evidenceの区別

最低限、以下を混ぜない。

- 企業が主張していること
- 公開資料から確認できること
- 独立研究が示していること
- Studio Labの分析
- 推測
- 不明

ページ上でも必要に応じて区別を残す。

## 6. 調査終了条件

検索件数ではなく「追加調査による結論更新が小さくなったか」で判断する。

初回Issueでは、少なくとも:

- 複数国
- 複数の独立情報源
- 成功例だけでなく制約・否定的結果
- 学術研究と実装事例の両方
- 日本への適用条件

を確認する。

件数目安は固定しないが、最初のIssueでは広めに探索し、分類が安定するまで調査する。

## 7. 再調査

再調査は全件を最初から読み直す方式ではなく、差分を中心に行う。

確認項目:

- 新しい研究
- 新しい導入事例
- 既存事例の続報
- 失敗・中止情報
- 製品終了・統合
- 規制変更
- 結論を覆す証拠
- 新しい改善パターン

再調査時には、

- 前回の結論
- 新規Evidence
- 結論変更の有無
- 更新した箇所
- 更新不要と判断した理由

を残す。

## 8. 著作権・保存

原則として、外部の論文PDF、書籍、企業資料などを無断でGitHubへ複製しない。

保存するもの:

- URL
- DOI / 書誌情報
- 自分たちの要約
- 必要最小限の引用
- 構造化した事実
- 分析結果

原資料そのものはライセンスを確認した場合のみ保存する。

## 9. 公開前レビュー

公開コンテンツは最低限、以下を確認する。

- 原典へのリンクがある
- 更新日がある
- 企業主張と独立Evidenceを混同していない
- 制度上の正式判断と改善提案を混同していない
- 日本への適用可能性を断定しすぎていない
- 数字の母数・期間・単位が分かる
- 失敗条件や限界を省いていない
- 「AIを使わない」選択肢も検討している

## 10. Studio Labでの利用

Studio Labは、次の単位で調査できるようにする。

```text
Pain
 ↓
Issue
 ↓
Search plan
 ↓
Source collection
 ↓
Evidence register
 ↓
Cross-case synthesis
 ↓
Contradiction / uncertainty check
 ↓
Human review
 ↓
Publish / hold / re-research
```

目的は記事生成の自動化ではなく、更新可能なEvidence baseを作ること。
