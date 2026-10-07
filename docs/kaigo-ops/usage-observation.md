# Kaigo Ops — 利用観測台帳・判断契約

更新日: 2026-10-07  
状態: canonical operational ledger  
対象: Kaigo Ops

## 役割

このファイルは、Kaigo Opsのpageviewとfeedbackを継続観測し、少数データを需要・改善効果へ誤変換しないための台帳と判断ルールをまとめる。

技術的な計測対象、非収集データ、初回観測日の定義は `docs/kaigo-ops/measurement.md` を正本とする。このファイルでは、観測期間ごとの実測値、controlled verificationの影響、feedback、そこから言えること・言えないことを記録する。

## 記録原則

- 実測できた値だけを記録し、欠損値を0で補わない。
- Analytics受信が未確認の間は、route別に「0 pageview」と断定しない。
- Worker、CI、開発者、controlled browser verificationによるアクセスは、実利用と分けて扱う。
- pageviewは閲覧の観測値であり、需要、改善効果、実行完了、制度理解を直接示さない。
- feedback 0件は失敗や満足の証拠ではない。
- 恣意的な数値thresholdで人気・成功・失敗を決めない。
- first confirmed observation dateは、browser pageview sendとVercel receiveの双方を確認した場合だけ `measurement.md` に記録する。

## 観測単位

各観測期間では、最低限次を記録する。

| 項目 | 記録内容 |
|---|---|
| 観測期間 | 開始日時と終了日時 |
| Analytics receive state | 受信確認済み / 受信未確認 / 一時的に不安定 |
| total visitors | Vercelで確認できた値。未確認なら「未確認」 |
| total pageviews | Vercelで確認できた値。未確認なら「未確認」 |
| route別pageviews | home、5 Issue、5 action tool。受信未確認なら欠損を0にしない |
| controlled verification | 有無、日時、対象route、想定アクセス数。分からない場合はその旨を記録 |
| feedback件数 | 対象期間に確認できた件数 |
| feedback分類 | 下記の少数分類でtriage。利用者に追加入力を要求しない |
| 重要な欠落 / blocker | 計測、導線、feedback取得等の問題 |
| 言えること | 観測値から直接支持される範囲 |
| 言えないこと | 需要、効果、完了等の未確認事項 |

## 観測対象route

### Home

- `/`

### 5 Issue

| Issue | route |
|---|---|
| 必要な情報を探すのに時間がかかる | `/issues/information-search` |
| 記録・文書作成に時間がかかる | `/issues/documentation` |
| 職員教育・引き継ぎが属人化する | `/issues/training-handover` |
| 問い合わせ・連携の負担が大きい | `/issues/communication-collaboration` |
| 稼働率・生産性を改善したい | `/issues/productivity-utilization` |

### 5 action tool

| 対象 | route |
|---|---|
| 情報探索の棚卸し | `/tools/information-inventory` |
| 記録業務の見直し | `/tools/documentation-review` |
| 教育・引き継ぎの棚卸し | `/tools/training-handover-inventory` |
| 問い合わせ・連携の棚卸し | `/tools/communication-review` |
| 業務時間・待ち・間接業務の棚卸し | `/tools/work-time-review` |

route比較は順位表にせず、まず「観測あり / 観測なし / データ不足」とfeedback有無を分けて記録する。

## Feedbackの内部分類

GitHub Issuesで受け取ったfeedbackは、必要に応じて後から次の少数分類へ整理する。

- 情報不足
- 手順が分かりにくい
- toolが使いにくい
- 制度確認先が分からない
- 自分の業務に当てはめにくい
- 既存の方法で足りる
- その他

分類は改善作業のtriage用であり、利用者に大量の選択を要求するためのものではない。氏名、利用者情報、介護記録、事業所の非公開情報は収集対象にしない。

## 初期観測記録

### 2026-10-07 baseline

- 観測時点: 2026-10-07 21:44 JST前後
- Analytics receive state: **受信未確認**
- Vercel fresh check: `visitors: 0 / pageviews: 0`
- requestPath breakdown: 空
- controlled verification: 前Waveでproduction route / mobile journeyの検証あり。Analytics受信との対応は未確認
- Kaigo Ops feedback Issue: 0件
- first confirmed observation date: 未確定

route別については、Analytics受信自体が未確認のため「0 pageview」とは扱わず、全対象を **データ不足（受信未確認）** とする。

この時点で言えること:

- tracking script配信確認後も、Vercel側pageview受信は確認できていない。
- Kaigo Ops feedbackとして確認できるGitHub Issueはまだない。

この時点で言えないこと:

- 実利用者が0人であること。
- 5 Issueの需要順位。
- action toolが使われていないこと。
- 役に立った / 役に立たなかったこと。
- 改善効果、業務時間削減、制度理解、実行完了。

## 2〜4週間レビュー契約

レビュー期間の起点は、`measurement.md` に記録された **first confirmed observation date** とする。受信未確認の間は、2〜4週間の観測期間が始まったものと扱わない。

初回レビューは、受信確認後おおむね2〜4週間の範囲で実施し、次を同じ観測期間で確認する。

1. homeのpageview
2. 5 Issueのroute別pageview
3. 5 action toolのroute別pageview
4. homeとIssue / toolの母数関係
5. feedbackの有無と内容分類
6. controlled verification trafficの影響
7. 異常な0件が計測不具合か、単に観測がないのか

レビュー時に見ないもの:

- pageviewだけから推定した改善効果
- tool閲覧から推定した実行完了
- revenue見込み
- 人員削減効果
- 介護ルール遷移から推定した制度理解完了

## 判断ルール

- pageview受信自体が不安定 → まず計測を修復する。
- 特定Issueに閲覧が偏るがfeedbackなし → 内容需要とは断定せず、入口、検索流入、表示位置も確認する。
- Issue閲覧はあるがtool閲覧がほぼない → Issueからtoolへの導線と説明を確認する。
- tool閲覧はあるがfeedbackがない → feedbackまでの摩擦、GitHubサインイン要件、案内文を確認する。
- feedbackで同じ不足が複数回出る → 再調査またはUI改善候補として優先度を上げるが、件数だけで効果を断定しない。
- pageview自体が極端に少ない → custom eventを増やす前に、discoverability、公開入口、計測状態を確認する。
- controlled verificationの比率を切り分けられない → 初期値を実利用の証拠として使わない。

## Custom eventを提案できる条件

今回custom eventは実装しない。将来提案する場合は、少なくとも次をすべて満たす。

1. pageview受信が安定している。
2. おおむね2〜4週間の観測がある。
3. pageviewだけでは具体的な意思決定ができない項目が特定されている。
4. eventに個人情報、検索語、worksheet入力内容、介護記録本文を含めない。
5. 追加する各eventの利用目的を1つに限定できる。

条件を満たさない場合は、既存pageviewとfeedbackの観測を続ける。

## 更新方法

観測値を追加するときは、対象期間と確認時刻を明記し、既存記録を上書きして履歴を消さない。

新しい判断を追加する場合は、先に「どの観測値から何が判断できず困ったか」を記録する。測定項目を増やすこと自体を目的にしない。
