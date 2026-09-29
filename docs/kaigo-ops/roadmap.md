# 介護業務改善 Roadmap

更新日: 2026-09-30
状態: Working roadmap

## 現在地

Kaigo Opsは、調査基盤を作る段階から、実際のIssueを公開し、利用価値を検証する段階へ移っている。

役割分担:

- **介護ルール**: 法令、基準省令、解釈通知、報酬、Q&Aなどを基に、「制度上どうなっているか」「何が義務・要件・許容範囲か」を確認する。
- **介護業務改善（Ops）**: 経営、事業運営、業務改善、DX、AI、ICT、人材・教育について、「どう運営し、どう改善するか」の判断材料を整理する。
- 制度面と運営面が重なるIssueでは、制度上の根拠を介護ルールへ接続し、Opsは改善方法、実装条件、効果、費用、失敗・制約を扱う。

DX・AI・ICTは目的ではなく、業務廃止、標準化、役割分担、教育、外部委託などと並ぶ改善手段として扱う。

## Phase 0 — 公開基盤

状態: **概ね完了**

- 介護ルール: 稼働中
- 介護業務改善: 別Vercel Projectとしてデプロイ済み
- 同一GitHubリポジトリ内の `ops-site/` で管理
- Kaigo Opsから介護ルールへの制度確認導線あり
- production deployはKaigo Rules / Kaigo Opsを分けて管理

残課題は公開基盤そのものより、コンテンツと利用価値の検証を優先する。

## Phase 1 — 事前調査基盤

状態: **主要部分完了**

整備済みの主な要素:

- 世界の介護DX・AI活用のfirst-pass landscape
- 国内外のEvidence register
- case register
- Japan transferability review
- Research Protocol
- Evidenceの区別と公開前レビュー基準
- Claim-level verification / retrieval evaluation
- 再調査と差分更新の考え方

今後は調査基盤を拡張すること自体を目的化せず、公開Issueを作るために必要な範囲で追加する。

## Phase 2 — First deep Issue

状態: **公開済み / 継続評価**

First deep Issue:

> 必要な情報を探すのに時間がかかる

すでに以下を準備・実施済み。

- 国内外のSource / Evidence整理
- 問題構造、失敗条件、改善パターンの整理
- 固定10問のField Validation protocol
- Machine Retrieval Benchmark
- production上の固定10問 × 3言い換え = 30 queryの再評価
- 利用者向けIssue pageの初版

2026-09-26時点のMachine Retrieval Benchmarkでは、更新後productionで以下を確認した。

- search hit: 30/30
- top-3 hit: 30/30
- context integrity: 10/10
- full pass: 30/30

この結果は固定queryでの検索導線とcontext保持を示すものであり、人間の探索時間短縮、使いやすさ、業務効率の改善を示すものではない。

人間によるField Validationは **OPTIONAL_EXTERNAL_VALIDATION / NOT_RUN** とし、サイト改善やサービス範囲拡張の必須ゲートにはしない。実施する場合は既存protocolを維持し、実測データを推定・代替生成しない。

Phase 2の残り:

1. 実利用queryまたは独立に作成した将来queryによる追加評価を、取得できる範囲で行う
2. 必要に応じて人間Field Validationを実施する
3. production反映後に公開routeを確認する

## Phase 3 — 3〜5 Issueで型を検証

状態: **5 Issue到達**

公開対象として以下の5 Issueを整備済み。

1. 必要な情報を探すのに時間がかかる
2. 記録・文書作成に時間がかかる
3. 職員教育・引き継ぎが属人化する
4. 問い合わせ・連携の負担が大きい
5. 稼働率・生産性を改善したい

次の候補:

6. 収支・コスト構造を把握したい

「収支・コスト構造」は、令和8年度介護事業経営実態調査の集計結果公表後に最新の公的データで深掘りする。

各Issueでは、原則として次を揃える。

- どんな困りごとか
- 対象業務・職種・場面
- 制度上の制約
- 主なボトルネック
- 改善パターン
- 国内外の事例
- 論文・公的資料
- 効果が期待できる条件
- 失敗・制約
- AIを使う場合 / 使わない場合
- 日本への適用条件
- 最初の小さな実験
- 介護ルールへの制度確認リンク
- 原典・最終調査日

5 Issueに到達し、公開Issueの定義を共通registryへ統合した。トップページにはkeyword検索と3分類の軽量filterを追加し、横断navigationも同じregistryから生成する。Issue数を増やすだけの段階は一旦区切り、今後は利用計測と再調査に重心を移す。

## Phase 4 — 再調査ループ

Issueごとに再調査日を持つ。

```text
publish
  ↓
watch
  ↓
scheduled re-search
  ↓
difference review
  ↓
conclusion changed?
  ├─ NO → 更新履歴のみ
  └─ YES → Evidence / Research Site / Issue page 更新
```

重要なのは「新しい情報が出たか」ではなく「既存の判断が変わるか」。

目安:

- 制度・法令: 改正・通知等のイベント駆動
- DX / AI 事例: 3〜6か月ごと
- 論文・公的調査: 6か月程度
- 重要Issue: 大きな新規証拠が出た場合は随時

## Phase 5 — 利用検証

見る指標:

- Issue閲覧
- 原典クリック
- 介護ルール遷移
- 再訪
- 検索語
- 実際に試した改善策
- 判断に役立ったか
- 役立たなかった理由
- 人間評価を行った場合の原典到達時間・操作負担

PVやページ数だけを主要KPIにしない。

可能なら少人数の現場利用者から定性的なフィードバックを得るが、参加者確保を開発停止条件にはしない。

## Phase 6 — 小規模事業としての検証

無料部分で利用価値が確認できた後に試す。

候補:

- 更新通知
- Issue monitoring
- 実務テンプレート
- 比較表
- チーム用保存・共有
- 自社条件に合わせたチェック
- 個別Evidence Brief
- 業界向け定期レポート

価格や機能は先に決めない。

「何に対して支払い意思があるか」を確認してから実装する。

## Phase 7 — 他業界への横展開判断

介護で以下が確認できた場合のみ検討する。

- 3〜5 Issueが継続運用できる
- 更新を半自動化できる
- 実際の利用がある
- 共通化できる調査・表示基盤が見えた

候補業界:

- 建設
- 保育
- 福祉
- 士業
- 製造
- 小売

サイト数を増やすこと自体は目的にしない。

## 直近の優先順位

1. 共通registry・分類・keyword検索をproductionへ反映し、mobileを含む公開動作を確認
2. productionへ反映済みのVercel Web Analytics clientについて、project-level Web Analyticsを有効化する
3. page view収集開始後、Issue別閲覧偏りを確認する
4. page viewで不足する場合だけcustom eventを検討し、検索語・外部遷移等を最小限追加する
5. 令和8年度介護事業経営実態調査の集計結果が公表されたら「収支・コスト構造」を再評価
6. 利用データとフィードバックを基に、再調査・事業化候補を判断
