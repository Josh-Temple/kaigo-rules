# 世界の介護DX・AI活用 全体地図 — 調査計画

更新日: 2026-09-22
状態: Active — initial landscape completed

## 現在地

2026-09-22にfirst-pass landscapeを実施した。

成果物:

- [Initial landscape](./research/world-care-dx-map/initial-landscape.md)
- [Source register](./research/world-care-dx-map/source-register.csv)
- [Search log](./research/world-care-dx-map/search-log-2026-09-22.md)

初回調査では、日本、England、Australia、Denmark、Singapore、United States、Europeの公的資料と、LTC / aged care関連のsystematic reviewを横断した。

暫定的に、First deep Issueは「必要な情報を探すのに時間がかかる」を第一候補とした。これは確定ではなく、追加調査で更新する。

## 目的

個別事例を先に深掘りする前に、世界で介護・高齢者ケアのDXやAIが「どの課題に、どの方法で使われているか」を俯瞰する。

この全体地図を、今後のIssue選定、調査優先順位、サイト分類の基礎にする。

## 調査する主な領域

### 1. 記録・文書
- 音声入力
- 自動要約
- 記録支援
- ケア記録の構造化
- 文書生成

### 2. 情報検索・知識管理
- 社内ナレッジ検索
- 制度・手順検索
- RAG
- FAQ
- ナレッジ更新

### 3. 職員教育・引き継ぎ
- e-learning
- AI tutor
- 手順支援
- onboarding
- competency support

### 4. 見守り・安全
- センサー
- 転倒予測
- 異常検知
- 夜間見守り
- wandering detection

### 5. ロボティクス
- 移乗
- 搬送
- コミュニケーション
- リハビリ
- cleaning / logistics

### 6. シフト・人員配置
- workforce optimization
- scheduling
- demand forecasting
- acuity-based staffing

### 7. ケア計画・意思決定支援
- risk stratification
- care planning support
- deterioration detection
- clinical decision support

### 8. 家族・利用者との連携
- family communication
- portal
- automated updates
- remote monitoring

### 9. 事務・請求・管理
- billing
- claims
- compliance documentation
- procurement
- back-office automation

### 10. 採用・定着
- recruitment
- retention analytics
- workforce support
- burnout reduction

## 各事例で確認する項目

- 国
- サービス種別
- 対象課題
- 技術カテゴリ
- 製品・ベンダー
- 導入主体
- 導入規模
- 実装期間
- 既存業務から何を変えたか
- 人間の役割
- 報告された成果
- 成果測定方法
- 失敗・制約
- 費用
- データ要件
- セキュリティ・規制
- 日本への適用可能性
- 情報源の種類
- 独立検証の有無

## 全体地図から作るアウトプット

1. **Landscape**
   - 何がどこで使われているか。

2. **Maturity map**
   - 実証中心 / 一部実装 / 広く運用、などの成熟度。

3. **Evidence gap**
   - 導入事例は多いが独立研究が少ない領域。
   - 研究では有望だが現場導入が少ない領域。

4. **Japan transferability**
   - 日本でも比較的導入しやすいもの。
   - 制度・インフラ差が大きいもの。

5. **Issue priority**
   - 介護業務改善サイトで次に深掘りすべきテーマ。

## 初回調査から追加された視点

初回調査により、次の区別を明示する必要が分かった。

- technology adoption と care outcome
- fall detection と fall prevention
- provider-reported result と independent evidence
- narrow AI と general-purpose / generative AI
- pilot と scaled operation
- technology capability と implementation capability

今後のsource registerでは、この区別を可能な限り構造化する。

## 次の調査

1. 日本の令和7年度・8年度効果測定資料から定量outcomeを抽出する。
2. 「必要な情報を探すのに時間がかかる」をFirst deep Issueとして検索範囲を広げる。
3. Australia / England / Denmarkの代表例についてJapan transferabilityを具体的に比較する。
4. Generative AIのcase-note / knowledge searchについて独立評価研究を探す。
5. Fall / monitoringは研究量が多いため独立Evidence Review候補とする。

## 期待する使い方

全体地図は記事そのものではなく「研究の索引」として使う。

例:

```text
世界の介護DX全体地図
  ├─ 情報検索
  │    └─ Issue: 必要な情報を探すのに時間がかかる
  ├─ 記録
  │    └─ Issue: 記録・文書作成に時間がかかる
  ├─ 教育
  │    └─ Issue: 職員教育・引き継ぎが属人化する
  └─ 見守り
       └─ Issue: 夜間見守りの負担が大きい
```

ここから、利用価値とEvidenceが高い領域を優先して公開コンテンツへ進める。
