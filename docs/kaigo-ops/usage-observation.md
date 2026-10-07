# Kaigo Ops — 利用観測台帳・判断契約

更新日: 2026-10-08  
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

今後のsnapshotは、比較可能性を保つため同じ項目名・同じ意味で記録する。

| 項目 | 記録内容 |
|---|---|
| observation date/time | snapshotを取得した日時。JSTを明記する |
| observation window | 観測対象期間。APIが時刻を丸める場合は、その仕様も記録する |
| Analytics receive state | 受信確認済み / 受信未確認 / 一時的に不安定 |
| total visitors | Vercelで確認できた値。取得不能なら `unknown / unavailable` |
| total pageviews | Vercelで確認できた値。取得不能なら `unknown / unavailable` |
| home | `/` の観測状態またはpageview。集計行がない場合は「観測なし（集計行なし）」 |
| 5 Issue | 5 routeを個別に記録する。集計行がないことを需要なしへ読み替えない |
| 5 tools | 5 routeを個別に記録する。閲覧を実行完了へ読み替えない |
| feedback count | fresh検索で確認できた件数。取得不能と0件を区別する |
| feedback category summary | 既存7分類で要約。0件の場合は「該当なし」 |
| Search Console impressions / clicks | 取得できた場合のみ値を記録。取得不能なら `unknown / unavailable` |
| indexing state summary | Worker Aまたはcurrent canonicalから確認できる範囲だけ記録する |
| controlled traffic caveat | controlled verificationの除外可否と、由来を分離できないtrafficを明記する |
| interpretation | 観測値から直接言えること / 言えないことを短く記録する |
| next check | 次回確認日またはreview window |
| 重要な欠落 / blocker | 計測、導線、feedback取得等の問題。ない場合も「なし」と明記する |

値の状態は、少なくとも **観測あり / 観測なし / 母数不足 / unknown / unavailable** を区別する。0件と未取得を同じ値として扱わない。

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

### 2026-10-07 observation activation / release verification

- Analytics receive state: **受信確認済み**
- first confirmed observation date: **2026-10-07**
- release後fresh check: `visitors: 2 / pageviews: 2`
- requestPath breakdown: `/` = 2。5 Issue / 5 action toolは集計行なし
- browser breakdown: Chrome 1 / Firefox 1
- deviceType: desktop 2
- controlled verification: production route/journey確認と390px headless browser確認を実施。controlled trafficは実利用として扱わない
- Kaigo Ops feedback Issue: 0件（`[Kaigo Opsフィードバック]` title prefixでfresh検索）
- custom event: 追加なし

受信は確認できたため、初回観測の起点は2026-10-07とする。一方、現在の母数は極小で、2 pageviewの個々の由来も確定していない。home以外に集計行がないことは **観測なし / 母数不足** として記録し、需要なし、tool未利用、導線失敗とは読み替えない。

この時点で言えること:

- Vercel側でproduction pageview受信が成立している。
- current production runtimeで主要route、feedback導線、robots / sitemap、390px journeyの技術検証が通っている。
- feedbackとして確認できるGitHub Issueはまだない。

この時点で言えないこと:

- 2 pageviewが独立した実利用者2人によるものか。
- どのIssue / toolに需要があるか。
- action toolが役立ったか、実行されたか。
- 改善効果、業務時間削減、制度理解、支払い意思。

### 2026-10-08 public discovery / observation operations snapshot

- observation date/time: **2026-10-08 00:11 JST前後**
- observation window: 2026-10-07の観測開始後からsnapshot取得時点までを対象にfresh確認。Vercelのaggregate queryは時間bucket境界へ丸められるため、値はsnapshot取得時点で返されたproduction集計として扱う
- Analytics receive state: **受信確認済み**
- total visitors / pageviews: **6 visitors / 7 pageviews**
- home: `/` = **7 pageviews / 6 visitors**
- 5 Issue: **観測なし（requestPath集計行なし）**
  - `/issues/information-search`
  - `/issues/documentation`
  - `/issues/training-handover`
  - `/issues/communication-collaboration`
  - `/issues/productivity-utilization`
- 5 tools: **観測なし（requestPath集計行なし）**
  - `/tools/information-inventory`
  - `/tools/documentation-review`
  - `/tools/training-handover-inventory`
  - `/tools/communication-review`
  - `/tools/work-time-review`
- browser / device補助情報: Chrome = 6 pageviews / 5 visitors、Firefox = 1 pageview / 1 visitor、deviceTypeはdesktop = 7 pageviews / 6 visitors
- feedback count: **0件**（`[Kaigo Opsフィードバック]` title prefixでfresh検索）
- feedback category summary: 該当なし。0件を失敗・満足・需要なしとは解釈しない
- Search Console impressions / clicks: **unknown / unavailable**
- indexing state summary: **unknown / unavailable**。same-wave Worker Aのcanonical record `docs/kaigo-ops/search-discovery-observation.md` では、認証済みSearch Console接続が利用できないため、property / sitemap submission / major 6 URL index state / Google-selected canonical は `UNKNOWN`、indexing request は `NOT_RUN` と記録されている
- controlled traffic caveat: deployed Analytics scriptはheadless / webdriver trafficを除外することが既存検証で確認済み。ただし今回の6 visitors / 7 pageviewsの個々の由来は確定できず、外部実利用者数や独立した需要の証拠として扱わない
- 重要な欠落 / blocker: Search Consoleは認証済み接続が利用できず、property / sitemap submission / URL Inspectionを実確認できない。Analytics受信自体のblockerはなし
- interpretation: production Analytics受信は継続している。一方、観測はhomeに限られ、Issue / toolの利用差を判断できる母数はまだない。feedbackも0件であり、改善対象の優先順位を確定する根拠はまだ不足している
- next check: **earliest review target 2026-10-21前後 / broader review window 2026-10-21〜2026-11-04前後**

#### Custom event decision memo

**CUSTOM_EVENT_NOT_JUSTIFIED**

理由:

- first confirmed observation date 2026-10-07から2〜4週間の観測期間がまだ蓄積していない
- Issue / tool routeに観測がなく、pageviewだけでは答えられない「具体的な意思決定」がまだ特定できていない
- 現時点でeventを追加しても、母数不足の問題を解消せず、計測だけを先に複雑化する
- 当面はpageview、Search Console discovery state、feedbackを同じsnapshotで継続観測する

custom eventは追加しない。将来candidateを検討する場合も、個人情報、検索語、worksheet入力内容、介護記録本文はpayloadへ含めない。

## 2〜4週間レビュー契約

レビュー期間の起点は、`measurement.md` に記録された **first confirmed observation date** とする。受信未確認の間は、2〜4週間の観測期間が始まったものと扱わない。

current canonicalではfirst confirmed observation dateは **2026-10-07** のまま維持されている。したがって、初回の正式な判断時点は次とする。

- earliest review target: **2026-10-21前後**
- broader review window: **2026-10-21〜2026-11-04前後**

このwindowまでsnapshotを同じschemaで追記し、途中の少数値だけで需要や効果を確定しない。

初回レビューでは、次を同じ観測期間で確認する。

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
