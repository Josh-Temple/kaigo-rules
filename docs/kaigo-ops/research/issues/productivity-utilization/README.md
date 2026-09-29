# Issue 05 — 稼働率・生産性を改善したい

更新日: 2026-09-30  
状態: Evidence synthesis v0.1 / public page candidate

## 1. Issue

「稼働率」と「生産性」は同じ指標ではない。

- 稼働率: 定員・提供可能枠に対して、どれだけ利用されているか
- 生産性: 人・時間・設備を使って、必要なケアや業務をどの程度安定して提供できるか

介護事業では、稼働率だけを高めても、

- 職員負担
- ケアの質
- 残業
- 欠勤
- turnover
- 緊急対応余力

が悪化すれば持続しない。

このIssueでは、最初にEvidenceが比較的厚い「生産性・workforce運用」を扱い、稼働率についてはサービス種別ごとのcapacity / demand指標として後段で分ける。

## 2. 現時点の結論

現時点のEvidenceからは、次の順序が妥当。

1. 「生産性」を人員削減ではなく、間接業務・待ち・調整の削減として定義する
2. 直接ケア時間と間接業務時間を分けて測る
3. bottleneckを一つ選ぶ
4. workflow改善・標準化・data reuseを先に試す
5. staffing / skill mixはケアの質と職員outcomeを同時に見る
6. AI / optimizationは調整業務の補助として限定的に試す
7. 稼働率はサービス種別ごとに別指標として設計する

> 「同じ人数でより多くこなす」だけを生産性としない。

## 3. 日本の主要Evidence

### 3.1 介護記録ソフトとworkflow redesign

厚生労働省「令和7年度 介護テクノロジー等による生産性向上の取組に関する調査及び効果測定事業」では、
訪問・通所系6事業所で介護記録ソフト導入とオペレーション変更を組み合わせた前後実証を行った。

介護職員1人1日480分換算では、

- 記録・文書作成: 43.1分 → 30.4分
- 転記: 21.5分 → 8.2分
- 直接介護等: 196.4分 → 200.6分

だった。

ただし、

- randomized trialではない
- nが小さい
- software導入とworkflow変更が同時
- 事前・事後で回答者数が異なる

ため、software単体の因果効果とは扱わない。

重要なのは、

> 間接業務が減ると、その時間が必ず「人員削減」になるのではなく、直接ケア等へ再配分されることがある

点。

### 3.2 AI訪問スケジュール作成

同報告書の小規模実証では、

- スケジュール新規作成・修正: 43.8分 → 36.9分
- スケジュール転記・職員間調整: 41.3分 → 11.3分

と観測された。

「作成」より「転記・調整」の減少が大きい。

一方、直接介護・看護・リハ時間が増えたため、総業務時間は減少していない。

したがって、価値は

> 人を減らすことより、調整業務から直接業務へ時間を移せるか

で見る方がEvidenceに近い。

## 4. Workforce Evidence

### 4.1 Staffing structures

2026年のnarrative scoping reviewでは、OECD諸国のLTC homeにおけるstaffing structuresとcare-worker outcomeを扱った76研究を整理した。

reviewは、改善策を考える際に、

- sufficient staffing
- appropriate skills / competencies
- staffing structureのcontext

を重視している。

ここから、

> productivity改善を「最低限の人数へ削る」問題として扱わない

必要がある。

### 4.2 Structural workforce interventions

2026年のrapid living systematic reviewでは、LTC homeのstaffing interventionを扱うRCTのうち11試験が効果推定へ寄与した。

主な結果:

- skill-mix adjustmentはhospitalizationを減らす可能性があったが、certaintyはlow
- clinical health indicators / mortalityはeffectがsmall / uncertain
- QoLはlittle to no effectでmoderate certainty
- staffing shortagesとlow implementation fidelityがbarrier
- staff engagementとstructured trainingがfacilitator

したがって、

> staffing modelを変えれば全般的にqualityが改善する

とは言えない。

## 5. 生産性を四つに分ける

### A. Direct care capacity

- 利用者対応
- ケア
- 看護
- rehabilitation
- consultation

ここは単純削減対象ではない。

### B. Indirect work

- 記録
- 転記
- scheduling
- coordination
- searching
- reporting

改善対象として比較的測りやすい。

### C. Waiting / friction

- system待ち
- 移動
- approval待ち
- 折り返し
- information不足による再確認

process改善の余地がある。

### D. Slack / resilience

- 急変
- 欠勤
- 新人支援
- 緊急対応
- quality review

「余っている時間」と誤認して削ると、resilienceが落ちる。

## 6. 稼働率は別に扱う

稼働率はサービスごとに意味が違う。

例:

- 通所: 定員 × 営業日 × 利用枠
- 訪問: 職員時間、移動、地域、資格、希望時間帯
- 入所: bed occupancyと入退所flow
- short stay: bed mixと予約変動

したがってKaigo Opsでは、

> 全サービス共通の「理想稼働率」を出さない。

将来、service-specific Issueとして、

- capacity
- demand
- cancellation
- no-show
- referral
- waitlist
- staffing constraint

を分けて扱う。

## 7. 改善パターン

### Pattern A — Time mapを作る

1週間、

- direct care
- documentation
- transcription
- coordination
- search
- travel
- waiting
- rework

へ時間を分類する。

### Pattern B — 最大bottleneckを一つ選ぶ

全業務を同時にDXしない。

上位1つを、

- eliminate
- standardize
- reuse
- automate
- reallocate

の順で検討する。

### Pattern C — “saved time”の行き先を決める

削減時間を、

- direct care
- break
- training
- quality review
- capacity expansion

のどこへ戻すかを先に決める。

### Pattern D — Staffingはskill mixも見る

人数だけでなく、

- qualification
- experience
- role
- shift
- workload
- supervision burden

を合わせて見る。

### Pattern E — AI / optimizationは狭い調整業務から

例:

- schedule proposal
- route draft
- workload visualization
- transcription
- document draft

人員配置の最終決定を自動化しない。

## 8. AIを使わない選択肢

- 標準作業
- schedule rule整理
- role redesign
- shift handoff改善
- data reuse
- structured form
- 5S
- layout変更
- meeting削減
- batch処理
- cancellation rule
- referral flow改善

process整理で十分ならAIを追加しない。

## 9. 小さな実験

### 1週間のtime allocation audit

1. 2〜3職種だけ対象
2. 15〜30分単位で業務categoryを記録
3. direct care / indirect / waiting / reworkへ分類
4. 最大のindirect / frictionを1つ選ぶ
5. 改善を1つ入れる
6. もう1週間測る

見る指標:

- 対象業務時間
- direct care時間
- overtime
- rework
- staff burden
- missed / delayed work

「対象業務が短くなった」だけで成功判定しない。

## 10. Safety boundary

生産性向上が、

- staffing削減
- break削減
- documentation省略
- consultation抑制
- emergency buffer削減

だけになると、ケアの質や職員outcomeを悪化させる可能性がある。

したがって、

> efficiency metricとquality / workforce metricを必ず対で見る。

## 11. 現時点で言わないこと

- AI schedulingで人員を減らせる
- staffingを薄くすれば生産性が上がる
- productivity改善で総労働時間が必ず減る
- 特定のstaff ratioが全サービスで最適
- 稼働率は高いほどよい
- technology導入だけで直接ケア時間が増える

## 12. 収支・コスト構造Issueとの順序

令和8年度介護事業経営実態調査は2026年に実施中で、集計結果は社会保障審議会介護給付費分科会で公表予定。

そのため、

- productivity / workforce: 現在のEvidenceで先に公開
- cost structure / margin: 令和8年度経営実態調査の集計結果公開後に更新

の順にする。

## 13. 次に確認すること

- service種別ごとのcapacity / utilization指標
- cancellation / no-showと稼働率
- direct care timeとquality outcome
- overtime / sick leave / turnoverとの関係
- scheduling optimizationの独立評価
- productivity改善のcost / implementation burden
- 令和8年度介護事業経営実態調査の集計結果

## 14. 公開ページへの要約

公開ページでは、

1. 稼働率と生産性の違い
2. 日本のtime-study
3. workforce Evidence
4. direct / indirect / friction / resilience
5. 改善順序
6. AI / non-AI
7. small experiment
8. safety boundary
9. 分かっていないこと
10. 出典

に圧縮する。
