# 介護業務改善（Kaigo Ops）

介護事業者・介護現場が、経営・事業運営・業務改善について「調べる・比較する・判断する」負担を減らすための公開サイトです。

## Positioning

- **介護ルール**: 法令、基準省令、解釈通知、報酬、Q&Aなどから、「制度上どうなっているか」を確認する
- **介護業務改善（Kaigo Ops）**: 経営、事業運営、業務改善、DX、AI、ICT、人材・教育について、「どう運営し、どう改善するか」の判断材料を整理する
- 制度面と運営面が重なる場合は、制度上の根拠を介護ルールへ接続し、Kaigo Opsでは改善方法、導入条件、効果、費用、失敗・制約を扱う
- DX・AI・ICTは目的ではなく、業務廃止、標準化、役割分担、教育、外部委託などと並ぶ改善手段として扱う

## Product principle

基本の流れは次の通りです。

```text
困りごと
  ↓
根拠
  ↓
改善パターン
  ↓
向く条件 / 向かない条件
  ↓
最初の小さな実行
```

成功事例や製品の紹介だけで終わらせず、国内外の公的資料、研究、導入事例を分けて確認し、日本で使う際の条件と限界を明示します。

## Vercel

同じ GitHub リポジトリ `Josh-Temple/kaigo-rules` から別 Vercel Project として管理し、Root Directory は `ops-site` です。

Kaigo Rulesとは公開面を分離します。

## Current scope

2026-10-07時点では、5つの課題ページを公開対象として整備しています。

公開済み / 公開準備済み:

1. 必要な情報を探すのに時間がかかる
2. 記録・文書作成に時間がかかる
3. 職員教育・引き継ぎが属人化する
4. 問い合わせ・連携の負担が大きい
5. 稼働率・生産性を改善したい

次の候補:

6. 収支・コスト構造を把握したい

「収支・コスト構造」は令和8年度介護事業経営実態調査の集計結果公表後に、最新の公的データを使って深掘りする。

## 5 Issueの実行入口

5つの公開Issueすべてに、読んだ後に小さく試せる入口があります。

- 情報探索: `/tools/information-inventory`
- 記録・文書: `/tools/documentation-review`
- 教育・引き継ぎ: `/tools/training-handover-inventory`
- 問い合わせ・連携: `/tools/communication-review`
- 稼働率・生産性: `/tools/work-time-review`

新規ツールは個人情報や介護記録本文の入力を求めず、accountやserver保存を前提にしません。ツールの利用や数値差だけで改善成功・制度適合・人員削減可能性を自動判定しません。

各Issueには、内容に応じたKaigo Rulesの公開DB検索とKaigo Rulesトップへの導線があります。サービス適用範囲はKaigo Ops側で推定せず、必要な制度判断はKaigo Rules側の検証状態と一次資料で確認します。

フィードバックはGitHub Issuesを再利用します。5 Issueと5 action toolから同じ3質問（「何を試したか」「どこで止まったか」「何が足りなかったか」）へ進め、action toolから開始した場合はIssue routeとtool routeをprefillします。投稿内容はGitHub上で公開・保存されるため、氏名、利用者情報、介護記録、事業所の非公開情報は入力しないよう、リンク元とprefillの両方で案内します。内部の分類は利用者に選択させず、投稿後に少数カテゴリへ整理します。詳細は `../docs/kaigo-ops/feedback-triage.md` を参照してください。

## First deep Issueの検証状態

情報探索Issueでは、固定10問 × 3言い換え = 30 queryのMachine Retrieval Benchmarkをproductionで実施しています。

更新後productionでは:

- search hit: 30/30
- top-3 hit: 30/30
- context integrity: 10/10
- full pass: 30/30

これは固定queryに対する検索導線と構造化contextの機械的再現性を示す結果です。

人間によるField Validationは `OPTIONAL_EXTERNAL_VALIDATION / NOT_RUN` です。したがって、現時点では「人間の探索時間を短縮した」「使いやすさを実証した」「業務効率が上がった」とは表現しません。

## 記録業務の見直しシート

`/issues/documentation` から `/tools/documentation-review` へ進めます。

- 変更前後の処理件数と、必要な記録・転記・探索・後追い記録・確認修正の合計時間を入力
- 件数で補正した1件当たり時間を比較。空欄・負数・0件は比較対象外
- 比較条件、記録漏れ・品質、初期設定・研修の負担を別に記録
- 架空例を明示し、改善効果の実測や因果効果と区別
- 入力は送信・自動保存せず、印刷またはPDF保存。個人情報や介護記録そのものは入力しない

## 検証

`ops-site` 内で `npm test`、`npm run build` を実行します。サーバー起動後、`npm run verify:routes -- <base-url>` で共通registryの全5課題、5つのaction tool、Issue→tool、tool→evidence、Issue→Kaigo Rules、フィードバック導線を検証します。

2026-10-02のローカル検証では、計算テスト3件・ビルド・全ルート確認を通過。390px幅の検索・分類・検索0件からの復帰、様式の計算・0件除外・ブラウザ保存なし、印刷PDFと日本語表示を確認しました。これは開発時の動作確認であり、現場での業務改善効果の検証ではありません。

## 公開発見・共有

2026-10-08のPublic Discovery & Observation Operations Waveで、Kaigo OpsとKaigo Rulesを同じintegration SHA `81a307738d7a40562ad033c3d2491cd05a2f2337` からproductionへ反映しました。

- Kaigo Opsの `robots.txt` / `sitemap.xml` / Issue canonical / Open Graphはproduction確認済み
- Kaigo Rules `/databases/search` から、情報探索・記録文書の2 Issueへ文脈付きで移る入口をproduction反映
- Kaigo Opsは制度適合を確定せず、必要な判断はKaigo Rulesの検証状態と一次資料へ戻す
- Search Consoleは認証済み接続がないため、property / sitemap submission / index state / Google-selected canonicalを `UNKNOWN` のまま維持
- direct-entryの紹介文とnon-claimsは `../docs/kaigo-ops/distribution-kit.md` を参照
- 外部投稿は明示的な許可なしに実行しない

## Action Tool Reliability & Release Assurance（2026-10-08）

既存5 Issue / 5 action toolを増やさず、次の運用境界を実装しています。

- 記録業務見直しシートの制度確認リンクは、通所介護専用routeではなくKaigo Rulesの汎用DB検索へ進む。サービス適用範囲は利用者がKaigo Rulesの検証状態と原典で確認し、Ops側で自動推定・制度適合判定をしない。
- 情報探索と記録・文書作成の2 Issueは、hero付近から既存toolへ進める。後半のEvidence・limitations・従来CTAも維持する。
- `npm test` は単体・source regression、`npm run build` と `npm run verify:routes` はビルド・route、`npm run test:browser` はPlaywright Chromiumで5 toolの入力・表示・架空例・消去・印刷と390px journeyを確認する。
- `Validate ops site` CIはPR/mainの両方でPlaywrightをlocal production-modeに対して実行する。fixtureは架空データのみで、production Analyticsへテストtrafficを送らない。
- 日次Kaigo Ops production workflowは、hook受理のみでは完了扱いにしない。Vercel API read tokenのGitHub Actions secret `VERCEL_TOKEN` が必須で、expected SHA、`READY`、production aliasと11公開routeの確認後に限り `deploy-state/kaigo-ops` をfast-forward更新する。設定と失敗条件は `../docs/kaigo-ops/deployment-assurance.md` を参照。

**注意:** CIが成功しても、それだけでproduction反映済みとは扱わない。deployment ID / READY / SHA / aliasをrelease後に再取得して確認する。

## 利用観測

2026-10-08のrelease後にVercel project、production、Web Analyticsをfresh確認しました。

- Kaigo Ops production: `dpl_6JuE6Cm2UnxFVvQdDZTV4cCRkhY1` / `READY`
- Kaigo Rules production: `dpl_5Ee8hKCoxAaQywaxxQGhJWypNDru` / `READY`
- `@vercel/analytics` とAnalytics script deliveryはproductionで確認済み
- first confirmed observation date: **2026-10-07**
- fresh aggregate: **6 visitors / 7 pageviews**、requestPathは `/` のみ
- 5 Issue / 5 action toolはrequestPath集計行なし
- feedbackはopen / closedとも0件
- controlled Playwright trafficはdeployed Analytics scriptの自動化判定を前提に実利用値として扱わない
- custom event、検索語、worksheet入力内容、個人情報、介護記録本文は追加収集しない

観測履歴と解釈ルールは `../docs/kaigo-ops/usage-observation.md`、計測契約は `../docs/kaigo-ops/measurement.md` を参照してください。

## 残りの実行と次の判断

- production route、主要journey、metadata、390px表示はproduction verifier run `37653052826` でPASS
- pageview、Search Console discovery state、feedbackを同じschemaで継続観測する
- earliest review targetは2026-10-21前後、broader review windowは2026-10-21〜2026-11-04前後
- Search Consoleへ認証済みでアクセスできるようになった時点で、property、sitemap submission、major 6 URL index state、Google-selected canonicalを確認する
- custom eventはまだ追加しない。pageviewだけでは答えられない具体的な意思決定が出た場合だけ再検討する
- Issue 6「収支・コスト構造」と新しいaction toolは、既存5 Issueの利用・feedbackと必要な公的データが揃うまで開始しない

## Latest Kaigo Ops production（2026-10-08 reliability wave）

- release: PR #442〜#446を統合したcommit `e49e770a970e541d2ad95204ad277eca89a485d3`
- production: `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / READY / `https://ops-site-pi.vercel.app/`（Vercel APIでalias対応を確認）
- browser CI: `Validate ops site` run `37728218607` PASS（unit / build / 5 tool Chromium interaction / 390px / route）
- public home + 5 Issue + 5 tools: release後の本文取得を確認。production 390pxの別ブラウザ再実行は未実施。
- `deploy-state/kaigo-ops`: release SHAへforceなしで更新済み。ただしこの更新はVercel直接releaseと独立照合によるもので、日次GitHub Actionsの本番実行成功を証明しない。日次実行にはGitHub Actions secret `VERCEL_TOKEN` が必要で、現時点の配置有無は未確認。
- Analytics: 2026-10-07〜08指定期間で7 visitors / 8 pageviews（homeのみ）。Search Consoleは`UNKNOWN`、Issue 6 / 新tool追加は保留。

上の状態がcurrentであり、本文に残るPR #434 / 旧deploymentの記述は以前のWaveの履歴である。

## 服薬業務の安全点検シート（2026-10-08：非公開検証中）

誤薬・与薬漏れに関する業務工程の試作は、[draft PR #451](https://github.com/Josh-Temple/kaigo-rules/pull/451)で隔離しています。**公開中の5 Issue / 5 action toolには含めません**。投薬判断、再投与、個別事故への対応、職種権限、事故報告要否・期限をこの試作で判定しません。

A #453（出典と主張）、B #454（Issue草案とサービス適用性）、D #455（独立検証台帳と専門職review pack）は文書のみmain統合済みです。試作Cはflag未設定・誤設定の場合404であり、flagはアクセス認証ではありません。公開可能なpreview URLでflagを有効にしないでください。

Cのlocalhost GitHub Actionsテストには成果があるものの、Dの独立動的検証、サービス別適用範囲の最終確認、医療職EX01・事故防止責任者EX02の実レビュー、内容責任者HU01の明示的公開承認は未完了です。**Wave `PARTIAL_WITH_GAPS`／公開 `PREVIEW_ONLY / NOT_PUBLIC`**。次の条件と版は[統合判定記録](../docs/kaigo-ops/safety/2026-10-08-medication-safety-validation-and-review-decision.md)を参照してください。

本番に新機能は配信していません。2026-10-08の照合では、従来11ルートがHTTP 200、試作routeが404、Kaigo Ops専用Vercel productionは`dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / READY / runtime `e49e770a970e541d2ad95204ad277eca89a485d3`です。mainの文書commitとproduction runtime SHAを混同しないでください。

## Medication-safety preview publication gate (2026-10-09 JST)

非公開「服薬業務の安全点検シート」の最新の統合判定は [E decision](../docs/kaigo-ops/safety/2026-10-08-medication-safety-content-alignment-and-independent-validation-decision.md)。**`PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**。試作 [draft PR #451](https://github.com/Josh-Temple/kaigo-rules/pull/451) を未マージで維持する。Aのclaim追跡とB最終本文の版差、Dの独立試験とC最新版のSHA差、実在のEX01/EX02/HU01未実施が公開阻害条件。表示flagは認証機能ではない。公開registry・ナビ・sitemapへ試作を追加しない。

Eでのproduction HTTP確認：既存のhome+5 Issue+5 toolは各200、`/tools/medication-safety-preview`は404。production runtime SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` はREADY。本Waveで服薬安全機能のproduction releaseを実施しない。

## 2026-10-09 medication-safety version-lock decision（最新）

非公開の「服薬業務の安全点検シート」は[最新版E統合判定](../docs/kaigo-ops/safety/2026-10-09-medication-safety-version-lock-and-review-gates-decision.md)のとおり、**`PARTIAL_WITH_GAPS / SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**。B最終2 blobとA trace、C同一3 code blobs、D最新版コードに対する独立CIは追跡可能だが、29-caseは11`PASS_LIMITED`/18`PARTIAL`。実在の医療職EX01・事故防止EX02レビューは未実施、HU01公開GOも未実施。外部preview認証、実Android、native zoom、読み上げ、印刷実物は未確認。C #451はdraft・未マージで、公開flag/nav/registry/sitemap/Analyticsに試作は追加しない。

最新Vercel production `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` READY、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/`。E再取得の公開HTTPは既存11ページ200、服薬試作route404、robots/sitemap200。**今回の新規本番release・本番browser操作テストなし**。前WaveのAnalytics受信情報とSearch Console `UNKNOWN`は継承であり、新たな実測ではない。次の担当と版固定はE decision参照。


## 2026-10-09 Expert Review Activation & Accessibility/Privacy Closure — E decision

服薬業務の安全点検シートは引き続き**非公開のdraft [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451)**。最新の[専門職審査・アクセシビリティ／privacy E判定](../docs/kaigo-ops/safety/2026-10-09-medication-safety-expert-review-and-accessibility-privacy-gates-decision.md)は`PARTIAL_WITH_GAPS / SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`。A/B出典・サービス・文面とCコード3 blobは一致、D独立17 Chromium testsは成功したが、29-caseは11 `PASS_LIMITED`・18 `PARTIAL`。

EX01/EX02は未依頼・未実施、HU01未承認。native zoom 200%、Android、実読み上げ・印刷、外部preview access control、実production browser journeyは未実施または未確立。flagは認証機構ではないため公開環境で有効化しない。本番は従来5 Issue＋5 tool／Vercel deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` READY、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/`。今回の本番HTTP直接取得は環境エラー、11 route HTTP 200と試作404は**前回の確認値**であって新規実測ではない。新しいproduction releaseなし。


## 2026-10-09 服薬事故の出典付き注意情報（静的ページ）

[公的資料に基づく注意事項](https://ops-site-pi.vercel.app/guides/medication-incident-sources)を、回答選択式の服薬安全試作とは**別の静的な公開資料**として追加。元資料、発行年・ページ、推奨と通知・法律の区別を示す。特に高齢者向け住まい2017年報告の受診推奨は、全サービス一律の法的義務や全事故の「必ずかかりつけ医連絡」へ拡張しない。事故時の個別医療判断、服薬可否、報告要否、刑事責任の断定をしない。

[根拠と範囲の台帳](../docs/kaigo-ops/safety/2026-10-09-medication-incident-public-source-guide-evidence.md)を参照。PR #463のunit・ops/browser regression・build・publication readinessが成功し、Vercel deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` READY、runtime SHA `ffd70abb5723e950a0a1036795f28da31614a1f3`、alias `ops-site-pi.vercel.app` をVercel APIで確認。**外部DNS・直接HTTP・実ブラウザの本番確認はこの実行環境では不可**のため、実URLごとのPASSは未確立。既存5 Issue／5 tool registryは不変。C #451の非公開試作は引き続き専門職／責任者の審査待ち（EX01/EX02/HU01 NOT_DONE）。


## 2026-10-09 公的出典ガイドのE統合・本番確認（最新）

最新の[判定記録](../docs/kaigo-ops/safety/2026-10-09-public-source-guides-release-verification-and-expansion-e-decision.md)は `PARTIAL_WITH_GAPS`。出典監査A #467と独立監査D #468は文書だけmainに統合。記事草案B #466（draft）と静的ガイドのナビ・印刷改善C #465（CI success）は未統合。新しい転倒・転落／誤嚥・窒息／異食の公開は全て `PUBLIC_SOURCE_GUIDE_HOLD`（C実装＋同一版D監査不足）。

服薬出典ガイドの既存productionは `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` READY、runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`。alias は `ops-site-pi.vercel.app` に割当。ただしEの実環境からDNS解決できず、HTTP/DOMの新規成功・実機ブラウザ表示は **未確立**。390px/200%/読み上げ/印刷は今回 `NOT_RUN`。`deploy-state/kaigo-ops` は旧検証SHA `e49e770a970e541d2ad95204ad277eca89a485d3` に据え置き。**本Eから新production releaseなし**。基礎11ルート、事故入力なし、旧試作 #451 非公開、EX01/EX02/HU01保留を維持。古い章のHTTP PASSは過去Waveの検証結果で、今回の直接HTTP結果ではない。


## 2026-10-10 公的出典ガイドの外部HTTP再検証と公開保留

[Kaigo Ops E判定](../docs/kaigo-ops/safety/2026-10-10-public-source-guide-http-closure-and-claim-aligned-e-decision.md)は`PARTIAL_WITH_GAPS`。専用Vercel production deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`／runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`／aliasの一致を再取得。今回GitHub Actions [read-only public HTTP probe #37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787)で、既存11 routeと服薬ガイド、試作404、robots/sitemapの**15/15件が期待応答**を返すことを検証。服薬ガイドのHTML canonical/OG・出典アンカーも確認。これは**外部HTTPの証拠**であり、Android Chrome実機・native 200%・読み上げ・印刷／人間の閲覧評価を実施したものではない。

A #470とD #471の出典・監査文書はmain統合済み。B #466／C #465は最終同一版の文章・実装・独立監査条件が未完で、既存記事の法的・報告対象表現の修正と新しい転倒・転落記事は**RELEASE_HOLD／PUBLIC_SOURCE_GUIDE_HOLD**。異食と誤嚥・窒息も今回掲載なし。回答選択式試作#451はdraft・非公開を維持し、EX01/EX02/HU01未依頼・未実施・未承認。新しいdeployment、flag変更、`deploy-state/kaigo-ops`更新は行わない。

## 2026-10-10 服薬・転倒ガイド — Eの同一版安全・公開ゲート

[判定正本](../docs/kaigo-ops/safety/2026-10-10-medication-fall-exact-head-controlled-release-e-decision.md)：**PARTIAL_WITH_GAPS**。前WaveのE記録 #473 は文書のみmainに統合しreadback済（`582792f64879477f8773dce450fff925d872fcb2`）。服薬の文言修正と転倒記事を含むC #465はhead `ef12b659...`、exact-head GitHub Actions 3件success、ただしD #475の独立監査対象は**旧head `77eb4b...`**で新しい文章・新記事を対象にしていない。A #474が参照したBも旧版であり、最終A/B/C/D chainが未成立。

服薬改訂・UI修正は`RELEASE_HOLD`、転倒記事・異食・誤嚥窒息は`PUBLIC_SOURCE_GUIDE_HOLD`。**新記事の公開なし**。現行productionは`dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` READY、runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`、alias `ops-site-pi.vercel.app`。過去15/15 HTTPは旧deploymentの観測で新releaseの確認ではない。正式deploy-state markerは`e49e770a970e541d2ad95204ad277eca89a485d3`を維持。実Android・native 200%・読み上げ・紙印刷`NOT_RUN`。#451非公開、EX01/EX02未依頼、HU01未承認。最新版Dによる同一版独立監査後にEが改めてreleaseを判定する。
