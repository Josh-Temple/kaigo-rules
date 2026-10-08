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

