# 介護業務改善 Roadmap

更新日: 2026-10-08
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

状態: **5 Issue到達 / actionability拡張済み**

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

2026-10-07のWaveでは、5 Issueすべてに少なくとも1つの実行入口を揃えた。記録・文書の既存見直しシートに加え、情報の正本棚卸し、教育・引き継ぎ棚卸し、問い合わせ往復棚卸し、業務時間・待ち時間棚卸しを追加した。各Issueから根拠、実行、Kaigo Rulesでの制度確認、最小フィードバックへ移れる導線を優先する。

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
- 検索利用（pageviewで不足し、privacy boundaryを確認したうえで最小限のcustom eventを追加する場合のみ）
- 実際に試した改善策
- 判断に役立ったか
- 役立たなかった理由
- 人間評価を行った場合の原典到達時間・操作負担

PVやページ数だけを主要KPIにしない。

可能なら少人数の現場利用者から定性的なフィードバックを得るが、参加者確保を開発停止条件にはしない。

pageviewとfeedbackの継続観測は `docs/kaigo-ops/usage-observation.md` に記録する。初回観測日は2026-10-07とし、そこから2〜4週間後に5 Issue / 5 toolsを同じ期間でレビューする。route別比較は人気順位ではなく、観測あり / 観測なし / データ不足として保守的に読む。

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

## 2026-10-08 Public Discovery & Observation Operations 状態

- Kaigo Opsの技術的な検索入口は、`robots.txt`、`sitemap.xml`、home + 5 Issueのcanonical / metadataまでproductionで確認済み
- Google Search Consoleは認証済み接続がないため、property / sitemap submission / major URL index state / Google-selected canonicalを未確認のまま維持
- Kaigo RulesのDB横断検索後に、制度確認からKaigo Opsの業務見直しへ移る文脈付き入口をproduction反映
- direct entryの優先対象は情報探索と記録・文書の2 Issue。共有文案とnon-claimsをdistribution kitに固定
- Analyticsは受信継続。fresh snapshotはhomeのみ7 pageviews / 6 visitorsで、Issue / tool別の判断には母数不足
- feedbackはopen / closedとも0件
- custom eventは追加せず、2026-10-21前後から2026-11-04前後の初回review windowまで同じschemaで観測を続ける
- Issue 6や新しいaction toolは開始しない

## 直近の優先順位

1. Kaigo Opsの5 Issue・5 action toolと、Kaigo Rules → Kaigo Opsの文脈付き入口をproductionで維持する
2. 認証済みSearch Consoleへアクセス可能になった時点で、property、sitemap submission、major 6 URLのindex state、Google-selected canonicalを確認する。未確認をindex失敗へ読み替えない
3. 2026-10-07を初回観測日として、pageview・Search Console discovery state・feedbackを同じsnapshot schemaで継続し、2026-10-21前後〜11-04前後に初回レビューする
4. 第三者へ共有する場合は `docs/kaigo-ops/distribution-kit.md` の優先2 Issueとnon-claimsを使う。明示的な許可なしに外部投稿は行わない
5. Issue / tool別の観測やfeedbackが出た場合だけ、次の改善対象を `docs/kaigo-ops/usage-observation.md` に記録する
6. pageviewだけでは答えられない具体的な意思決定が確認され、privacy boundaryを満たす場合に限り、必要最小限のcustom eventを再検討する
7. Issue 6「収支・コスト構造」は、令和8年度介護事業経営実態調査の集計結果と既存5 Issueの利用・feedbackの双方が揃ってから再評価する

## 2026-10-08 Action Tool Reliability & Release Assurance Wave

- A〜D: PR #442〜#445をmainへ統合、E: PR #446で結合後の`Validate ops site`（単体・build・5 toolの実ブラウザ操作・390px・route）をPASS。
- production: Kaigo Opsの統合SHA `e49e770a970e541d2ad95204ad277eca89a485d3` をVercelへrelease。deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` はREADY、public aliasは同deploymentを指す。
- `deploy-state/kaigo-ops`: 独立照合後に通常push相当でexpected SHAへ更新。日次workflow自身の本番成功は別途検証が必要。
- サービス固有の固定Rulesリンクを汎用DB検索に差替え。サービス適用と制度適合はOpsで判定しない。
- 情報探索・記録文書の2 Issueだけに早期action entryを追加。既存Evidence、限界、後半CTAは維持。
- 5 / 5 toolにChromium browser regressionを導入。synthetic fixtureで入力、更新、架空例、確認付き消去、印刷等を継続検証。
- release後public 11ページの本文取得とVercel SHA/alias照合を確認。production 390pxの独立再検証は今回未実施であり、CI側の390px PASSと区別する。
- analytics: 同じreview windowを継続。直近7 visitors / 8 pageviews（homeのみ）、feedback 0件。小標本から改善効果や人気順位を断定しない。
- immediate follow-up: trusted daily deployment workflowでVercel tokenとexpected SHA / READY / alias / routesの実動を確認し、運用上の不足があれば修復。Search Consoleは認証接続までUNKNOWNのまま非blocker。
- 2026-10-21前後の観測レビューまではIssue 6と新action toolを増やさない。


## 2026-10-08 誤薬・与薬漏れ／事故予防：次の公開判定

**現在：`PARTIAL_WITH_GAPS / PREVIEW_ONLY`。公開Issue・公開toolは追加しない。**

- A（#449）：出典20 claimと12 risk、B（#448）：利用者向けIssue草案・サービス別留保、D（#450）：独立安全レビューと公開遮断テストはmainへ統合。
- C（#451）：選択式の服薬業務安全点検シートはdraft PRで保持。CIで`preview`はPASSだが、本番公開しない。専門職レビュー・独立red-team・権限管理・適用範囲・200%の画面検証などは未完。
- Eのpublication decision: [safety/2026-10-08-medication-safety-publication-decision.md](./safety/2026-10-08-medication-safety-publication-decision.md)。`EXPERT_REVIEW_NOT_DONE`、`HUMAN_APPROVAL_NOT_DONE`のままGOにしない。
- 次の作業：claim / service scopeの未確定点を限定、アクセス制御下でR01〜R16 / privacy / UIテスト、適切な医療職と介護事故防止責任者のレビュー、内容責任者承認。その後にEが公開可否を再判定する。
- 既存5 Issue/5 toolの観測期間、Analytics計測定義、Search Consoleの`UNKNOWN`、Issue 6「収支・コスト構造」の扱いは維持する。日次deployment workflowの実行検証は別途継続。

## 2026-10-08 Medication-Safety Validation & Expert Review Readiness（公開保留）

- A #453、B #454、D #455の文書検証成果はmainへ統合。C #451はdraft／非公開試作のまま保持。詳しい固定版・未実施テスト・専門職審査のゲートは[最新判定記録](./safety/2026-10-08-medication-safety-validation-and-review-decision.md)を参照する。
- Waveは`PARTIAL_WITH_GAPS`、公開判断は`PREVIEW_ONLY / NOT_PUBLIC`。新しいIssue番号を採番せず、Issue 6「収支・コスト構造」を従来の候補として保持する。
- 次回公開再判定前の順序：(1) A/Bが最新版段落と原典traceを確定、(2) CがUI文言と結果・印刷を調整し制限環境で再検証、(3) Dが固定版の独立red-team/privacy/アクセシビリティ/公開遮断を実測、(4) EX01医療職とEX02介護事故防止責任者が実レビュー、(5) HU01内容責任者が対象版に明示GO/HOLDを付与、(6) Eが公開可否を再判定。
- 実在の利用者・薬剤・事故記録は収集しない。一般公開・Vercel production flag有効化・releaseはGOまで禁止。既存5 Issue/5 tool、Analytics計測定義、観測窓を維持する。

## 2026-10-09 服薬業務の安全点検シート：未公開のまま再審査へ

[Eの判定正本](./safety/2026-10-08-medication-safety-content-alignment-and-independent-validation-decision.md)：**`PARTIAL_WITH_GAPS / SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**。新規公開Issue・toolは増やさず、Issue 6「収支・コスト構造」の既存候補を維持。

公開前の順序は **Aが最終B本文・サービス資料のclaim traceを再固定 → B/Cが選択肢・結果・印刷文の対応を確定 → Dが最新版Cに対して独立した29ケースと不足した実機・プライバシー試験を再評価 → 実在のEX01/EX02審査 → HU01の明示承認 → EがGOを再判定**。レビュー・承認がない状態でC draft #451をmainに統合したり、公開flagを有効化したりしない。

既存5 Issue/5 toolは維持。本番の既存11ルートは2026-10-09 JSTにHTTP 200、試作routeは404。端末実操作や試作の一般公開適合を確認したという意味ではない。
