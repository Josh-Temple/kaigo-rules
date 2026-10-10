# Kaigo Ops — Current Projection

Updated: 2026-10-08
Status: current routing projection

このファイルは、Kaigo Opsで「現在そのまま再利用してよい知識」と「まだcurrent verified factとして扱わない知識」を短く確認するためのprojectionです。

正本を置き換えません。詳細な根拠・研究・検証状態は必ずリンク先で確認してください。

## Precedence

現在状態について矛盾がある場合は、次の順で扱います。

1. current `main` のcanonical data / review ledgers
2. `docs/kaigo-ops/research/README.md` のcurrent-state guard
3. current issue research
4. historical / recovered checkpoint

historical checkpointにある完了表現を、そのままcurrent verifiedへ昇格しません。

## Currently reusable

### 記録・文書作成

Current issue:
`docs/kaigo-ops/research/issues/documentation/README.md`

現在のEvidence synthesisから再利用できる実務上の順序:

1. 不要な記録・重複入力を特定する
2. 正本と入力元を決める
3. 一度入力した情報を再利用する
4. 紙・FAX・別システム間の転記を減らす
5. その後で音声入力、要約、AI draftを比較する
6. AI出力を正式記録へ入れる場合は、人間の確認責任を残す

AI導入自体を目的にせず、通常のICT・workflow改善で十分なら生成AIを追加しない。

### Information retrieval

Machine retrieval benchmarkの結果は、固定queryに対する検索導線・context integrityの機械的再現性として利用できる。

ただし、人間の探索時間短縮、使いやすさ、業務効率向上の実証とは扱わない。

Human field validationは `OPTIONAL_EXTERNAL_VALIDATION / NOT_RUN`。

## Measurement state

2026-10-08のPublic Discovery & Observation Operations Waveでは、integration PR #434をmainへ統合したruntime release SHA `81a307738d7a40562ad033c3d2491cd05a2f2337` を、Kaigo OpsとKaigo Rulesの両productionへexact SHAで反映した。

- Kaigo Ops: `dpl_6JuE6Cm2UnxFVvQdDZTV4cCRkhY1` / `https://ops-site-pi.vercel.app/` / `READY`
- Kaigo Rules: `dpl_5Ee8hKCoxAaQywaxxQGhJWypNDru` / `https://kaigo-rules.vercel.app/` / `READY`

Vercel Web Analyticsは **RECEIVE_CONFIRMED** を維持し、first confirmed observation dateは **2026-10-07**。release後のfresh aggregateでも、home `/` = **7 pageviews / 6 visitors** で、5 Issueと5 action toolにはrequestPath集計行がない。browserはChrome 6 pageviews / 5 visitors、Firefox 1 / 1、deviceTypeはdesktop 7 / 6だった。

この値は閲覧の観測値であり、外部実利用者数、需要、改善効果、tool実行完了を示さない。今回のproduction verificationはheadless / webdriverで実施しており、deployed Analytics scriptの既存自動化除外を前提にcontrolled verification trafficを実利用値へ読み替えない。

Kaigo Ops feedbackはtitle prefix `[Kaigo Opsフィードバック]` でopen / closedとも0件。0件を失敗、満足、需要なしの証拠にはしない。

Search Consoleは認証済み接続が利用できないため、property、sitemap submission、major 6 URL index state、Google-selected canonicalは `UNKNOWN`、indexing requestは `NOT_RUN`。詳細は `docs/kaigo-ops/search-discovery-observation.md` を正本とする。

custom eventは **CUSTOM_EVENT_NOT_JUSTIFIED**。現時点ではpageviewだけでは答えられない具体的な意思決定が特定されておらず、観測母数も極小のため追加しない。earliest review targetは **2026-10-21前後**、broader review windowは **2026-10-21〜2026-11-04前後**。

### Public discovery / contextual entry

Kaigo Ops productionでは、home + 5 Issue + 5 action tool、`robots.txt`、`sitemap.xml`、Issueページのcanonical / Open Graph、Analytics script deliveryを確認済み。390px production verificationでも11 routeと5つのIssue → tool / Kaigo Rules / feedback journeyがPASSした。

Kaigo Rules productionの `/databases/search` には、制度上の要件を確認した後に業務見直しへ進む文脈付き入口を反映済み。direct linkは情報探索と記録・文書の2 Issueに限定し、Kaigo Opsが制度適合を確定しない境界を同じ入口で明示する。

第三者へ直接共有する場合の対象・紹介文・non-claimsは `docs/kaigo-ops/distribution-kit.md` をcanonical public-entry recordとする。外部投稿は明示的な許可なしに実行しない。

## Actionability / public journey

2026-10-07のUtilization & Actionability Waveでは、5つの公開Issueすべてに「読んだ後に試す」入口を揃えた。

- 情報探索: `/tools/information-inventory`
- 記録・文書: `/tools/documentation-review`
- 教育・引き継ぎ: `/tools/training-handover-inventory`
- 問い合わせ・連携: `/tools/communication-review`
- 稼働率・生産性: `/tools/work-time-review`

新規4ツールはclient-side中心で、accountやserver保存を前提にしない。氏名、利用者情報、介護記録本文などの入力を求めず、ツール利用だけで改善成功や制度適合を判定しない。

5 Issueすべてで、具体的なKaigo Rulesの公開DB検索への導線と、Kaigo Rulesトップへの汎用導線を併存させる。サービス適用範囲はKaigo Ops側で推定せず、Kaigo Rules側の検証状態と一次資料へ戻って確認する。

フィードバックはGitHub Issuesを再利用し、「何を試したか」「どこで止まったか」「何が足りなかったか」を最小入力として案内する。投稿はGitHub上で公開・保存されるため、個人情報、介護記録、事業所の非公開情報を記載しないよう明示する。

Issue 6「収支・コスト構造」は開始していない。Analyticsの実受信は確認できたが母数はまだ極小のため、現時点で需要や改善効果は断定しない。

## Production release state

2026-10-08 Public Discovery & Observation Operations Waveのproduction state:

- integration PR: #434
- integrated runtime SHA: `81a307738d7a40562ad033c3d2491cd05a2f2337`
- Kaigo Ops deployment: `dpl_6JuE6Cm2UnxFVvQdDZTV4cCRkhY1`
- Kaigo Ops alias: `https://ops-site-pi.vercel.app/`
- Kaigo Rules deployment: `dpl_5Ee8hKCoxAaQywaxxQGhJWypNDru`
- Kaigo Rules alias: `https://kaigo-rules.vercel.app/`
- both deployments: `READY`
- integration CI: `Validate build` PASS
- Kaigo Ops CI: `Validate ops site` PASS
- publication-readiness integration: PASS
- production verifier run: `37653052826` PASS
- Kaigo Ops home + 5 Issue + 5 action tool: PASS
- Issue → tool / Kaigo Rules / feedback: 5 / 5 PASS
- Kaigo Rules → Kaigo Ops contextual entry: PASS
- canonical / Open Graph / robots / sitemap: PASS
- Analytics script delivery: PASS
- 390px verification: PASS
- custom event: not added
- Issue 6 / new feature: not added

The production state in the preceding subsection is the historical Public Discovery & Observation release, superseded for Kaigo Ops by the newer runtime section below.

## Current non-claims

現時点では、次をcurrent verified factとして一般化しない。

- 「生成AIで介護記録の作業時間が○％減る」
- 「AIなら介護記録時間を大幅に減らせる」
- 「音声要約で記録品質が上がる」
- 「生成AIの方が通常入力より費用対効果が高い」
- machine retrieval benchmarkのPASSを、人間の時間削減や使いやすさの証拠とすること

特に、現在のKaigo Ops researchには、日本の介護現場におけるGenAI documentationのvalidated human time-reduction percentageを、そのまま再利用できる形では保持していない。

外部ICT導入調査、workflow変更を伴う効果測定、self-report、machine benchmarkの数値を、生成AI単体の因果効果へ変換しない。

## Regulation boundary

制度上の義務・要件・許容範囲はKaigo Opsで確定しない。

- 法令
- 基準省令
- 報酬
- 解釈通知
- 国Q&A
- current verification state

は、同じRepositoryの介護ルール側canonical dataへ戻って確認する。

## Update rule

このprojectionを更新するのは、次のいずれかが変わったときだけ。

- current issue researchの結論またはnon-claim
- human validation state
- canonical review ledger / answerability gate
- 公開siteで再利用するcurrent knowledge boundary

記事追加やhistorical checkpoint追加だけでは更新しない。

## 2026-10-08 Action Tool Reliability & Release Assurance（今回のcurrent release）

- integration: PR #442 (A), #443 (D), #444 (C), #445 (B), #446 (E)
- Kaigo Ops production: `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / `READY`
- exact runtime SHA: `e49e770a970e541d2ad95204ad277eca89a485d3`
- public alias: `https://ops-site-pi.vercel.app/` → 上記deployment ID（Vercel APIで照合済み）
- `deploy-state/kaigo-ops`: 上記SHAへ通常のfast-forward更新済み。更新前markerは`5ed01a64a1d5ca07d1853d973cac00a74c932934`
- Kaigo Rules production: このWaveでは再デプロイせず。Rulesの前Wave production stateと混同しない。
- documentation-reviewは通所介護固定の制度確認リンクを削除し、Kaigo Rules汎用DB検索と原典・適用範囲の確認へ変更。Opsは制度適合を判定しない。
- information-search / documentationの2 Issueはhero付近に小さな実行入口を追加。従来のEvidence、limitations、後半CTAを維持。
- `Validate ops site` PR #446: unit/source tests、Next build、Playwright Chromiumでの5 tool・390px操作、route verifierがPASS（run `37728218607`）。publication readinessもPASS（run `37728218610`）。
- release後: public home + 5 Issue + 5 toolの表示内容を外部取得して確認。Vercel APIではREADY・expected SHA・aliasを確認。production上で390pxの独立ブラウザ再実行およびHTTP statusの全件直接測定はこの実行では未実施。
- 新しい日次deploy verifierとfail-closed合成テストは統合済み。ただし今回のreleaseはVercel APIから実行し、markerは別途照合した結果を受けて更新した。**日次GitHub Actions自身の本番実行成功は未確認**。GitHub Actions secret `VERCEL_TOKEN` の有無も未確認。手順は `docs/kaigo-ops/deployment-assurance.md`。
- Analytics snapshot (2026-10-07〜10-08の指定期間、取得時点): 7 visitors / 8 pageviews、requestPath `/`のみ。feedback 0件（専用title prefixでfresh検索）。需要・改善効果は判定しない。
- Search Console: `authenticated Search Console access unavailable` / index `UNKNOWN` を維持。
- next review: 2026-10-21前後、broader window 2026-10-21〜2026-11-04前後。Issue 6 / 新toolは開始しない。

**Release assessment:** アプリの統合テストと本番SHA/aliasは確認済み。日次workflowの実動・production 390px再検証などは未確認なので、Waveの全項目を完全達成とは扱わない。


## 2026-10-08 Accident Prevention & Medication-Safety Foundation（Worker E判定）

**安全領域候補：`PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`。** 誤薬・与薬漏れに関する根拠・リスク台帳（PR #449）、Issue草案（#448）、独立安全レビュー・公開遮断テスト（#450）をmainに統合した。Cの選択式業務点検シート（PR #451）はdraft branchに留保し、一般公開・production登録・feature flag有効化は認めない。

- E判定の正本: [safety/2026-10-08-medication-safety-publication-decision.md](./safety/2026-10-08-medication-safety-publication-decision.md)
- 厚労省Vol.1436の誤薬・与薬漏れ（冊子38〜39頁）に限定した出典の照合はあるが、全サービスへの転用は未確立。BのMHLW-01〜07とAのMS-01〜20はE判定記録にcrosswalkを置いた。
- C PRのpreview CIはPASS。ただしDの16ケースの独立実行、200%・network/storage等の実査、適切な医療職と事故防止責任者のレビューは**未完**。EX01/EX02=`EXPERT_REVIEW_NOT_DONE`、HU01=`HUMAN_APPROVAL_NOT_DONE`。
- productionは既存5 Issue / 5 toolを維持。Vercel deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` はREADY、runtime SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/`。Vercel HTML取得では公開11ルートは各200、`/tools/medication-safety-preview` は404。390px・200%の今回の独立本番ブラウザ実査ではない。
- docs/testのmain最新SHAをproduction runtime SHAに読み替えない。今Waveで新Issue/toolをreleaseしたとは報告しない。新しいVercel production deploymentは不要。
- Search Consoleは`UNKNOWN`、Analyticsは従来の`RECEIVE_CONFIRMED`、first observation 2026-10-07。観測schema・custom eventsを変えず、2026-10-21前後〜11-04前後に既存5 Issue/5 toolの観測レビューを行う。
- 日次GitHub Actionsでのproduction deploy verifier実運用成功と`VERCEL_TOKEN`配置確認は未完。安全領域の新機能公開の保留とは独立に追跡する。

## 2026-10-08 Medication-Safety Validation & Expert Review Readiness（最新の公開判断）

- Worker A [#453](https://github.com/Josh-Temple/kaigo-rules/pull/453)／B [#454](https://github.com/Josh-Temple/kaigo-rules/pull/454)／D [#455](https://github.com/Josh-Temple/kaigo-rules/pull/455)の安全資料をdocs-onlyでmainに統合（main baseline `bab39f09d85a00dbca6d6e78d7b956889c22575d`）。C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451)はdraft・未マージ。
- 新しい統合判定の正本: [2026-10-08-medication-safety-validation-and-review-decision.md](./safety/2026-10-08-medication-safety-validation-and-review-decision.md)。
- **Wave `PARTIAL_WITH_GAPS`、公開 `PREVIEW_ONLY / NOT_PUBLIC`**。Aの段落追跡は改訂前B本文に紐付き、最新版Bとの文単位の再照合が必要。施設資料を訪問・通所・居住系の服薬手順に一律転用しない。
- CはGitHub Actions localhostのflag別Chromium等の限定機械テストを実行・記録（最新head `a1357ad7ebd723c5a8c8fcf754c04b384f7db95d`、checks success）。Dの独立flag有効ブラウザ、ネットワーク全体・印刷/200%等の実査は未達。CとDのPASSを混同しない。
- EX01/EX02は`EXPERT_REVIEW_NOT_DONE`、HU01は`HUMAN_APPROVAL_NOT_DONE`。Dの専門職レビューpackは準備済みであり、人の審査を行ったことにはならない。
- 今回fresh照合の本番は`dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / READY / runtime `e49e770a970e541d2ad95204ad277eca89a485d3` / `https://ops-site-pi.vercel.app/`。公開home + 5 Issue + 5 toolsはHTTP 200、試作routeは404、sitemap 200。new deployなし。今回はproduction 390pxなどの独立実操作はしていない。
- Analytics受信とSearch Console `UNKNOWN`、初回レビュー窓2026-10-21前後〜11-04前後、Issue 6「収支・コスト構造」の扱いを維持。PVは事故予防効果ではない。

## 2026-10-09 Medication-Safety Content Alignment & Independent Validation — E判断

2026-10-09 JST、[E統合判定](./safety/2026-10-08-medication-safety-content-alignment-and-independent-validation-decision.md) を実施。**Wave `PARTIAL_WITH_GAPS`、安全 `SAFETY_PARTIAL_WITH_GAPS`、公開 `PREVIEW_ONLY / NOT_PUBLIC`** を維持する。試作は一般公開していない。

- A [#458](https://github.com/Josh-Temple/kaigo-rules/pull/458) のclaim traceは、B [#459](https://github.com/Josh-Temple/kaigo-rules/pull/459) の最終本文blobへの再照合が必要。C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) は語彙を更新しflag別CI成功（run 37783554826）、ただしD [#457](https://github.com/Josh-Temple/kaigo-rules/pull/457) の独立ブラウザ検査成功（run 37783550622）は**Cの旧SHA**に対するもの。最新版への再試験が必要。
- 実在専門職の審査 **EX01/EX02 = `EXPERT_REVIEW_NOT_DONE`**、公開承認 **HU01 = `HUMAN_APPROVAL_NOT_DONE`**。C #451はdraft・未マージ。新たな公開Issue、action tool、公開preview、production releaseは行わない。
- 本番Vercel `kaigo-ops` は `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / `READY`、runtime SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/`。今回Eの直接HTTP再検査では既存11ルートが各200、試作route 404、robots/sitemap各200。**HTTP確認とブラウザ実操作は別**。
- Analytics `RECEIVE_CONFIRMED`、Search Console `UNKNOWN`は既存canonicalからの継承であり、Eによる新規集計結果ではない。観測定義・レビュー期間は変更しない。

## 2026-10-09 服薬安全試作：版固定と人間審査ゲート（最新E判定）

[最新版 E decision](./safety/2026-10-09-medication-safety-version-lock-and-review-gates-decision.md)を正本とする。**Wave `PARTIAL_WITH_GAPS` / safety `SAFETY_PARTIAL_WITH_GAPS` / 公開 `PREVIEW_ONLY / NOT_PUBLIC`**。旧WaveにあったB→AとC→Dの版不一致は、B最終2 blobへのA第8節追跡と、同一Cコード3 blobへのD独立CI成功により限定的に解消。DはR/P/U計29ケースのうち`PASS_LIMITED`11、`PARTIAL`18。技術的限定成功を専門職レビューや公開承認とは扱わない。

実在EX01・EX02は`EXPERT_REVIEW_NOT_DONE`、HU01は`HUMAN_APPROVAL_NOT_DONE`。native zoom/Android/読み上げ/人手印刷・外部preview accessは未確立。C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451)はdraft・未マージで、匿名previewも本番にも公開しない。Eの本番HTTP再取得では従来11ルート200、試作404、robots/sitemap 200。Kaigo Ops production READY `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`（docs main SHAではない）。**新production releaseなし**。このHTTP確認をブラウザ操作PASSとしない。Analytics受信は前Waveからの継承、Search Consoleは`UNKNOWN`のまま。


## 2026-10-09 Expert Review Activation & Accessibility/Privacy Closure — E decision

2026-10-09 JST、非公開「服薬業務の安全点検シート」の新しい[E統合判定](./safety/2026-10-09-medication-safety-expert-review-and-accessibility-privacy-gates-decision.md)を記録。**Wave `PARTIAL_WITH_GAPS`／独立安全 `SAFETY_PARTIAL_WITH_GAPS`／公開 `PREVIEW_ONLY / NOT_PUBLIC`** を維持する。既存公開の5 Issue／5 action toolは変更せず、C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451)はdraft・未マージ。

- B [#459](https://github.com/Josh-Temple/kaigo-rules/pull/459)の本文・service 2 blobsを変えず専門職用補足を追加、A [#458](https://github.com/Josh-Temple/kaigo-rules/pull/458)は出典→文章→画面→EX01/EX02の論点を追補。D [#457](https://github.com/Josh-Temple/kaigo-rules/pull/457)の独立Chromium 17件は修正再試験後成功。ただし29 casesは11 `PASS_LIMITED`／18 `PARTIAL`。
- 実Android、native 200% zoom、screen readerの人間聴取、印刷プレビュー／紙の人手評価、外部preview access制御は未確立。EX01/EX02実在審査未依頼・未実施、HU01本人の公開承認なし。
- Vercel APIで再取得したproductionは既存`dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`／READY／runtime `e49e770a970e541d2ad95204ad277eca89a485d3`／alias `https://ops-site-pi.vercel.app/`。本Eの直接HTTP取得は環境エラーで**NOT_RUN**（旧11 route 200／preview route 404は履歴）。productionの新release・実ブラウザ確認なし。Analytics `RECEIVE_CONFIRMED`とSearch Console `UNKNOWN`は継承。
- `REVIEW_PACK_READY`と`REVIEW_REQUESTED`は別。送付先と権限・明示許可が整うまで外部連絡なし。Issue 6の「収支・コスト構造」候補は変更しない。既存の観測レビュー時期2026-10-21前後〜11-04前後を維持。


## 2026-10-09 公的資料に基づく服薬事故の注意情報（試作ツールと別）

[公的資料に基づく出典・公開境界記録](./safety/2026-10-09-medication-incident-public-source-guide-evidence.md)。厚生労働省2025年ガイドライン、2017年の高齢者向け住まい研究報告、2024年事故報告通知、PMDA、刑法211条に基づく**静的な注意情報ページ** `/guides/medication-incident-sources` を[PR #463](https://github.com/Josh-Temple/kaigo-rules/pull/463)でmainへ統合。2017資料の「別の薬を飲ませた場合は自己判断で軽視せず受診」の推奨を全サービス共通の法的義務へ一般化しない。事故報告の対象と自治体運用、刑事責任の成立要件は分離。全文転載ではなく要約と元資料リンクを掲載し、個別医療判断・入力・診断機能なし。

**Vercelによるproduction反映：** deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`、READY、exact runtime SHA `ffd70abb5723e950a0a1036795f28da31614a1f3`、alias `https://ops-site-pi.vercel.app/` をAPI readback。今回の環境では外部DNSが解決できず、新ルート・既存11ルート・試作404等の直接HTTP/実ブラウザ確認は**NOT_ESTABLISHED**。日次deploy verifierによる本番成功を確認したとは扱わず、`deploy-state/kaigo-ops`を更新しない。外部取得可能な環境でURL/表示/404/sitemap/canonicalと390px操作を確認し再記録する。

**独立の公開HOLD：** 回答選択型の服薬安全点検ツール [C #451](https://github.com/Josh-Temple/kaigo-rules/pull/451) は依然draft/未マージ/非公開。EX01/EX02専門職レビューとHU01公開承認は未実施のまま保留。5 Issue・5 action toolのregistryは変更なし。


## 2026-10-09 公的事故防止出典ガイド拡充 — E統合判定（最新）

[Worker Eの統合判定](./safety/2026-10-09-public-source-guides-release-verification-and-expansion-e-decision.md)は **`PARTIAL_WITH_GAPS`**。出典台帳 A [#467](https://github.com/Josh-Temple/kaigo-rules/pull/467) と独立監査 D [#468](https://github.com/Josh-Temple/kaigo-rules/pull/468) はdocs-onlyでmainに統合。編集B [#466](https://github.com/Josh-Temple/kaigo-rules/pull/466) はdraft／未merge、情報ページUI C [#465](https://github.com/Josh-Temple/kaigo-rules/pull/465) はCI成功だがDによる最新C headの独立検証を欠き未merge。

**新記事：転倒・転落／誤嚥・窒息／異食の全て `PUBLIC_SOURCE_GUIDE_HOLD`。** Aの `SOURCE_SUPPORTED` はB/C/D同一版審査・公開承認ではない。既存服薬事故情報ページはVercel `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`／READY／runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`、alias `https://ops-site-pi.vercel.app/` はAPI照合済み。しかし本Eの直接HTTPはDNS解決失敗、公開11ルート／服薬ガイド／旧試作404／robots／sitemapの実測は `FRESH_HTTP_NOT_ESTABLISHED`、実Android/200%/読み上げ/印刷は `NOT_RUN`。**`PRODUCTION_NOT_VERIFIED`、新production releaseなし、deploy-state marker据え置き `e49e770a970e541d2ad95204ad277eca89a485d3`。**

既存服薬本文は刑法211条の見出しと2024年事故報告通知の対象サービスにP1修正候補。医療・自治体報告の個別判断は載せない。非公開選択式試作C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) はdraft・未mergeで `PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`。EX01/EX02は依頼せず審査未実施、HU01未承認。既存5 Issue/5 action tool、Issue 6候補、Analytics schema、観測レビュー期間は不変。


## 2026-10-10 — 公的出典ガイドHTTP到達のE統合判定

[今回のE統合判定](safety/2026-10-10-public-source-guide-http-closure-and-claim-aligned-e-decision.md)：**PARTIAL_WITH_GAPS**。Kaigo Ops専用Vercel `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` はproduction READY（runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`）、alias `ops-site-pi.vercel.app` の割当確認済み。従来のDNS障害を回避し、GitHub Actions外部runner [run #37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787) が**公開15 URL中15件の期待HTTP応答**を確認。旧11 routeは各200、静的服薬ガイド200、非公開試作route404、robots/sitemap各200。ガイドcanonical/OG/出典アンカーも機械HTMLで確認。**PRODUCTION_HTTP_CONFIRMEDはこの外部HTTP測定の範囲だけ**であり、Android実機・native 200%・読み上げ・印刷は未実施。

出典A [#470](https://github.com/Josh-Temple/kaigo-rules/pull/470)と独立監査D [#471](https://github.com/Josh-Temple/kaigo-rules/pull/471)の文書追補はmain統合済み。B [#466](https://github.com/Josh-Temple/kaigo-rules/pull/466)はdraft、C [#465](https://github.com/Josh-Temple/kaigo-rules/pull/465)は未マージ。C最新版headはDが審査したheadより進んでおり、既存服薬記事の法的見出し・事故報告サービス範囲の修正、転倒・転落の新記事実装とD同一版再審査が残る。既存記事改訂は`RELEASE_HOLD`、転倒・転落／異食／誤嚥・窒息は各`PUBLIC_SOURCE_GUIDE_HOLD`。旧試作#451はdraft/NOT_PUBLIC、EX01/EX02/HU01は未依頼・未実施・未承認。**新しいproduction deployと`deploy-state/kaigo-ops`更新は行わず、markerは`e49e770a970e541d2ad95204ad277eca89a485d3`に据置き。**

## 2026-10-10 — 服薬・転倒出典ガイドの同一版Eゲート

[最新版のE統合判定](safety/2026-10-10-medication-fall-exact-head-controlled-release-e-decision.md)：**PARTIAL_WITH_GAPS**。前Wave判定PR #473を文書3ファイルの3CI成功後にmainへ統合（`582792f64879477f8773dce450fff925d872fcb2`、readback済）。A #474は未統合でBの旧稿を参照、B #466最終稿head `97389ce...`／blob `1394df...`、C #465新記事込みhead `ef12b659...`（8ファイル、exact-head CI 3件success）、D #475は**旧C head `77eb4b...`を独立監査**。したがって最新版のA/B/C/D同一版安全ゲートは未成立。既存服薬改訂`RELEASE_HOLD`、新転倒・転落`PUBLIC_SOURCE_GUIDE_HOLD`、UI改善`RELEASE_HOLD`。異食・誤嚥窒息も公開しない。

今回、新しいアプリ・記事をmainにマージせず、productionにも配信しない。専用Vercel alias `ops-site-pi.vercel.app`は旧deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`／READY／runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`のまま。過去probe 15/15は旧deploymentの証拠。**新productionは`PRODUCTION_NOT_VERIFIED`**、実Android/native 200%/読み上げ/印刷は`NOT_RUN`、deploy-state `e49e770a970e541d2ad95204ad277eca89a485d3`据置き。#451はdraft/NOT_PUBLIC、EX01/EX02未依頼・HU01未承認。次はA/B最新版の整合→C固定CI→Dの最新head独立再監査→Eの範囲別release判定。


## 2026-10-10 服薬・転倒最終照合Wave — Eの範囲別公開HOLD

最新の[最終統合判定](safety/2026-10-10-medication-fall-final-alignment-staged-release-e-decision.md)は **`PARTIAL_WITH_GAPS`**。A #474の最新版§8はB #466最終blob `4549faac...`との主張・段落照合を完了したが、D #475の§10独立監査はA/Bのそれ以前のblobを対象にしており、**A/B/C/Dの最終同一版は未成立**。C #465最新head `b33f8b16...`で機械CI 3件がsuccessしても、Dの最終版独立承認や公開GOではない。

既存服薬改訂 **`RELEASE_HOLD`**、転倒記事 **`PUBLIC_SOURCE_GUIDE_HOLD`**、非医学的UI **`RELEASE_HOLD`**。異食と誤嚥・窒息は今回対象外としてHOLD。#451は `PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`。刑法211条の該当施行版公式全文直読と自治体個別事故報告ルールは `NOT_ESTABLISHED`。実Android・native 200%、スクリーンリーダー人間聴取、紙印刷、PDF deep link実ビューアは `NOT_RUN`。EX01/EX02の審査とHU01の承認は未実施。

**今回アプリのmain統合・新production releaseなし。** 現行Kaigo Ops専用Vercel aliasは既存deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`／runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`／`READY`。以前の15/15外部HTTPは旧runtimeの結果であり、新releaseのHTTP/DOM実測ではない。正式`deploy-state/kaigo-ops`は `e49e770a970e541d2ad95204ad277eca89a485d3` のまま。次は最終A/B/C固定版に対するD独立差分再審査と、範囲別E再判定。公開数を優先して未承認の2記事やリンクを混入させない。
