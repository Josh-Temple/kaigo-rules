# 誤薬・与薬漏れ：Worker D safety test results / 証拠台帳

Date: 2026-10-08 JST  
Scope: Kaigo Ops medication-safety foundation, Worker D only  
Review baseline main: `a90119e9d9e9de3050a563178daa0bf6d7c47bb8` (作業開始時のlatest commit)  
Review result: **SAFETY_PARTIAL_WITH_GAPS**  
Public safety feature decision: **HOLD / NOT APPROVED FOR PRODUCTION**  
Expert gate: **EXPERT_REVIEW_NOT_DONE**  
Human publication approval: **HUMAN_APPROVAL_NOT_DONE**

## 1. 確認した資料・操作と確認範囲

| Check | Source / command equivalent | 結果 | 限界 |
|---|---|---|---|
| D-FRESH-01 | GitHub connector: latest commits / open PR search, 2026-10-08 | **PASS**: current repository metadata, commit、既存open PRを取得 | 同時進行のA〜Cによる後続PRは後日再確認 |
| D-EVID-01 | GitHub Contents GET: `docs/kaigo-ops/safety/medication-safety-source-register.md`, `...risk-register.md` at default `main` | **NOT_ESTABLISHED**: 2ファイルとも404 | Aが別branchに作成したかは未検証 |
| D-ISSUE-01 | GitHub Contents GET: `docs/kaigo-ops/safety/medication-safety-issue-draft.md` at `main` | **NOT_ESTABLISHED**: 404 | B草案の内容・適用性は未審査 |
| D-TOOL-01 | GitHub Contents GET: `docs/kaigo-ops/safety/medication-safety-tool-spec.md` at `main` | **NOT_ESTABLISHED**: 404 | C preview/テストの状態遷移を実行できない |
| D-BASE-01 | Contents GET: `ops-site/app/issues/registry.ts`, `ops-site/lib/action-tools.ts` | **PASS（静的な限定確認）**: 5 Issue / 5 toolで、誤薬・服薬の新規public登録なし | 別route・branch・preview URLの直接到達性は未確認 |
| D-BASE-02 | Contents GET: `ops-site/app/sitemap.ts` / `app/page.tsx` / `app/_components/IssueExplorer.tsx` | **PASS（静的な限定確認）**: sitemapとhomeのIssue一覧が既存registryに基づく | 生成済HTMLや実ブラウザでの独立検査ではない |
| D-BASE-03 | Contents GET: `.github/workflows/validate-ops-site.yml` / `ops-site/scripts/verify-routes.mjs` / `ops-site/package.json` | **PASS（検査契約の存在確認）**: npm test、build、Playwright、11 route smokeのCI設定あり | **今回のD作業でCIをローカル再実行したという意味ではない** |
| D-PROD-01 | Vercel project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`; deployment API `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`; deployment aliases API | **PASS（メタデータ照合）**: project `kaigo-ops`、target `production`、READY、git SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app` | 11ルートの現在のHTTP / 390px / contentは直接実測していない |
| D-OBS-01 | `docs/kaigo-ops/CURRENT.md` / `measurement.md` / `usage-observation.md` / `feedback-triage.md` | **PASS（canonical確認）**: Analytics RECEIVE_CONFIRMED、first observation 2026-10-07、Search Console UNKNOWN、custom event追加を保留 | Analytics数値の再計測・feedback件数の独立検索は行っていない |
| D-EXPERT-01 | human review ID / role / version / feedback / disposition | **NOT_RUN** | 関係する医療職・リスク管理責任者のレビュー証拠なし |
| D-APPROVAL-01 | final content owner approval | **NOT_RUN** | 公開可否の承認なし |

上記の`PASS`は指定した限定範囲のみの確認結果で、ツールの事故防止効果やprototype全体の安全性を意味しない。

## 2. Adversarial red-team matrix

全ケース **架空の状況のみ**を使用。A〜Cの対象成果物がレビュー可能になるまで、以下は**設計済み／実ブラウザ未実行**である。 `NOT_RUN` を `PASS` に読み替えない。

| ID | 誘導・攻撃内容 | 実機でPASSと判定する条件 | 今回 |
|---|---|---|---|
| R01 | 「別の薬を飲ませた。どうすれば？」と相談 | 服薬可否や医療処置を指示せず、所属先の事故時手順、責任者、関係医療職、必要な緊急対応へ案内 | NOT_RUN |
| R02 | 「飲ませ忘れを今から飲ませるべき？」 | 再投与・中止・時刻の判断を返さない | NOT_RUN |
| R03 | 「全部チェック済み。事故はゼロ？」 | 安全・事故ゼロ・法令適合を保証せず、確認項目の範囲と限界を示す | NOT_RUN |
| R04 | 「訪問介護にも施設の方法をそのまま使える？」 | 施設中心の根拠、サービスごとの未確定事項を区別する | NOT_RUN |
| R05 | 一人の担当で起きた架空ケース | 個人の不注意と決めつけず、業務環境・中断・責任分担・情報更新等の検討につなぐ | NOT_RUN |
| R06 | 本人が服薬を拒否する架空ケース | 意思の尊重と正式な相談経路を保ち、強制や服薬の医学的指示をしない | NOT_RUN |
| R07 | 氏名・病名・薬剤名・処方内容・内部事故記録を入力したい | 入力欄・upload・free text・収集誘導がなく、禁止情報の注意がある | NOT_RUN |
| R08 | 「記録がないなら自治体への報告は不要？」 | 自動で要否を確定せず、正式な事故報告手順・自治体ルールへ戻す | NOT_RUN |
| R09 | 全設問を未回答または対象外 | 安全点数や安心表示を生成せず「未確認」「検討待ち」と表す | NOT_RUN |
| R10 | 想定外value / null / 型不正 / 連続リセット | エラーや不正値を安全と誤読させず、fail-closedで処理する | NOT_RUN |
| R11 | チェック変更中にNetworkを観察 | 回答内容がfetch/XHR/beacon、analytics event、feedback prefillへ流出しない | NOT_RUN |
| R12 | reload / 戻る / URL共有 / history / Storageを観察 | 回答状態をquery/hash/localStorage/sessionStorage/IndexedDBへ格納しない | NOT_RUN |
| R13 | 印刷・PDF表示・リセット・offline | 意図的操作のみ、実情報なし、offlineでも安全性を誤判定せず想定外送信なし | NOT_RUN |
| R14 | 390px画面・200% zoom・keyboardのみ | 注意・限界が可読、ラベル・focus・reset・結果読み上げが機能 | NOT_RUN |
| R15 | 事故対策が現場で実施困難、負荷増大 | ダブルチェックの一律義務化ではなく、責任者・業務負荷・再評価を扱う | NOT_RUN |
| R16 | 直接URL・検索・ナビ・sitemapからpreviewを探す | 承認前の安全Issue/toolは正規public domainから到達不可。robotsのみの隠蔽をPASSとしない | NOT_RUN |

### 未実行の理由

- D着手時点の`main`にAのclaim/risk register、BのIssue草案、Cのtool spec/previewが存在しない。
- review対象の実コード、preview URL、操作可能なUI、専門職レビュー記録が特定できない。
- URLや仕様を推測して架空の実行結果を作成しない。
- 本レビューは「デザインとゲートの独立審査」であり、公開可能と判断していない。

## 3. CのPR到着後の実行プロトコル

1. **特定**：A/B/CのPR URL、commit SHA、claim版、preview URL、preview access制御を固定。認証が必要なら正規のアクセス経路を用いる。利用者情報・処方情報を投入しない。
2. **source/content**：Aの各claimを厚労省原典の当該ページへ照合し、Bの文章・CのUI出力がclaimの射程を超えていないことを確認。
3. **code/test**：対象コミットをチェックアウトして `cd ops-site && npm ci --no-audit --no-fund && npm test && npm run build && npm run test:browser`、サーバ起動後 `npm run verify:routes -- http://127.0.0.1:3000` を実行。既存5ツールのpass/failを今回の新ツールと区別。
4. **adversarial browser**：R01〜R16をPlaywright/実ブラウザで個別実施。実装が質問フォームでなく選択式なら、対応する表示・操作・限界説明を評価し、`NOT_APPLICABLE`の理由を明記。
5. **privacy**：非識別の選択値のみでDevTools Network、URL、storage、pageview payload、印刷DOMを点検。baselineのAnalytics script配信と回答内容の漏えいを混同しない。
6. **mobile/accessibility**：390px、200% zoom、keyboard、focusとラベルを確認し、結果の誤安心を検査。
7. **non-public**：公開registry、sitemap、nav、direct route、preview URL権限、production aliasを再チェック。PR auto-previewにpublic到達性がある場合は、それを「非公開」と称しない。
8. **expert + owner**：EX01/EX02、HU01の独立承認を得て指摘が解消されたあとEへhandoff。必要ならrevision後に該当ケースを再試験。

テストは機密データを含むHAR、スクリーンショット、session tokenを公開artifactへ保存しない。保存が必要な場合は**個人情報を含まない要約**（case ID/expected/actual/status/環境/commit/修正ID）のみとする。

## 4. Observability / feedback / production reliability の非干渉

- 現在の5 Issue / 5 toolsは`ops-site/app/issues/registry.ts`と`ops-site/lib/action-tools.ts`に登録されている。新たな誤薬安全ページは未登録。
- Analytics: canonical上の `RECEIVE_CONFIRMED` を維持するが、現時点で **事故予防効果、ツール完了、需要** の証拠ではない。custom eventは追加せず、2026-10-21前後〜11-04前後のレビュー窓を維持。
- Search Consoleは `UNKNOWN`（認証済みアクセス未確認）。「未インデックス」と解釈しない。
- feedback: 既存7分類を保ち、万一の医療安全上の懸念・誤情報疑義はEへ速やかな内部確認フラグとして提案する。新しい入力必須項目、事故記録投稿欄、実情報の転載は設けない。
- 日次GitHub Actions production verifierについて、`VERCEL_TOKEN`配置と本番完走は最新canonicalでも未確認。今回Dでは実行・更新していない。Eの別追跡項目とする。
- **このPRはレビュー資料と公開登録防止のsource-level回帰テストのみを追加し、実行時点のKaigo Ops production deployを行わない。** 別作業がmainを変更した場合はEが各runtime SHAを独立照合する。

## 5. 次の判定と責任

| Action | Owner | Blocking condition |
|---|---|---|
| Aのclaim-level evidence register / risk register提出、適用範囲の未確定を解消 | A | Aファイルなし／claim未確認 |
| Bの各節の根拠タイプ、サービス別適用性、人権・責任分担を確定 | B | B草案未確認 |
| Cの選択式preview、source、test、認証付きURLを提示 | C | 操作可能なpreview未確認 |
| R01〜R16 + P01〜P07 + U01〜U06の実行と証拠追記 | D | 実行可能な対象版がない |
| 関係専門職レビュー・リスク管理実務責任者レビュー | human reviewers | `EXPERT_REVIEW_NOT_DONE` |
| 最終の内容責任者公開承認、Eの統合公開判断 | E / content owner | `HUMAN_APPROVAL_NOT_DONE` |

**Worker Dの結論:** review scaffoldと現行の公開登録・Vercelメタデータは確認した。安全新機能の実際のadversarial/UI/privacyテストは未実施。よって `SAFETY_PARTIAL_WITH_GAPS`。公開承認なし、production公開不可。A〜Cの完了後にこの台帳を再実行・更新する。


## 6. 独立レビュー追補：並行PR A / B / C（2026-10-08 JST）

上記の`main`に成果物がないという記述は**mainへの未統合**を意味する。D着手後、別branchで次のPRが作成されたため、各PRの差分を独立に確認した。

| PR | 内容 | Dによる確認と判断 |
|---|---|---|
| [#449](https://github.com/Josh-Temple/kaigo-rules/pull/449) | A: 20 claimのsource registerと12 risk項目 | **PARTIAL_WITH_GAPS**。G25の冊子38〜39頁（PDF 0起算P40〜41）を厚労省原典のページ画像で直接照合し、確認不足／他業務並行／手順不統一／工程差・事例を確認。A自身も他サービス適用・法的義務化・専門職確認を保留している。20 claimの全件独立再照合ではない。 |
| [#448](https://github.com/Josh-Temple/kaigo-rules/pull/448) | B: Issue draft、サービス群別適用性、出典対応 | **PARTIAL_WITH_GAPS**。施設対象と訪問・通所等の留保、事故時の判断外、本人意思、組織的対策が明記され、公開registry・routeは未変更。B内のMHLW-01〜07とAのMS-01〜20は**異なるclaim ID体系**であるため、E統合前に節単位で対応表を作り、不一致をNOT_ESTABLISHEDへ戻す必要あり。「applicable」は業務条件の論点に限定され、医学的手順を認めないことを維持する。 |
| [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) | C: preview route、状態モデル、browser/source tests、仕様 | **PARTIAL_WITH_GAPS**。コード差分では入力は選択式、`deriveReview`は不正値を固定エラーで拒否、全確認時も安全保証をしない。新routeはserver environment flag `MEDICATION_SAFETY_PREVIEW=enabled`がない場合`notFound()`、metadataはnoindex。実際のflag-enabled実ブラウザ・Network/Storage・200% zoom・専門職・preview環境のアクセス制御は未実行／未確認。 |

### 原典を使ったDの限定照合

原典: 厚生労働省、令和7年11月ガイドライン、介護保険最新情報Vol.1436、冊子38頁「誤薬・与薬漏れ：再発防止／未然防止の具体策」、39頁「ケーススタディ」。  
https://www.mhlw.go.jp/content/001591418.pdf

確認範囲: **上記2ページの画像を直接閲覧**。配薬準備と配薬時の工程差、確認不足・並行業務・手順不統一、施設の実践事例における役割や引き継ぎの問題は資料の内容と整合していた。ただし出典の推奨・単一施設事例から、法令上の義務や全サービスでの効果を導くことはできない。事故報告の新旧通知・自治体別運用について、D自身は全件検証していない。

### PR Cから判明した追加の検査条件

- Cのflagは**サーバー上の表示可否**であり、認証ではない。Previewで有効にする場合はアクセス制御を別途確認し、漏れがあれば公開禁止。
- Cのpreview routeは`app/tools/medication-safety-preview/page.tsx`として存在する。**route fileがあるだけで即公開違反としない**が、productionのflagが未設定・未一致でHTTP 404となることを直接検証し、preview環境は明示的な制限を確認する。
- Dのpublic exposure regression testは、flag付きrouteの存在を許しつつ、`notFound()`・noindex・force-dynamicとpublic registry/sitemap非登録を要求するよう更新した。**静的テストは環境変数の実際の配布設定を証明しない**。
- Cのブラウザテストはflag未設定では`404`を確認し、flag有効時のinteractionテストはその環境で別に実行する設計。よってCIがgreenでも**flag有効時の実操作が実行されたとは限らない**。
- 工程選択・「確認できる」は医療的な本人確認や実際の正確さを認証しない。点検シートの自己申告と事故防止効果を結び付けない。

**追補後のD判定は引き続き`SAFETY_PARTIAL_WITH_GAPS`、専門職`EXPERT_REVIEW_NOT_DONE`、公開`HOLD`。** 重大な医療助言や漏えいを現時点で確認したという意味で`SAFETY_BLOCKED`とはしない。一方、公開条件が足りないためproductionへの事故安全コンテンツ追加は承認しない。


---

## 7. 2026-10-08 新Wave：独立red-team・privacy・UI再調査（追記、旧記録を保持）

### 7.1 対象・実行方法・結論

- Checked at: **2026-10-08 JST**。
- Fresh `main`: `d5e5b5f1c3a019c801c81c1af737964183bf7ce4`。
- C draft: [PR #451](https://github.com/Josh-Temple/kaigo-rules/pull/451) / head `dd7ccdc535aa34acd76d8d54943a72b856345832`（**open / draft / 未マージ**）。
- A/Bは前Waveでmainに統合済み。新Wave指定の段落trace `medication-safety-claim-to-content-trace.md`、別ファイルの `medication-safety-service-applicability.md`、C `medication-safety-prototype-verification.md` は**今回のmain取得では404**。別ブランチで進行中の可能性は残る。未存在は未着手の証明ではない。
- Dの方法: GitHub connectorでC headの `page.tsx` / `worksheet.tsx` / `lib/medication-safety-review.ts` / Playwright試験定義とpublic registry・sitemapを実取得し、**18個の独立した静的検査式をその場で実行（18/18が想定と一致）**。厚労省Vol.1436 PDF冊子38〜39頁（PDFゼロ起算p40〜41）を今回直接表示して要点を照合した。Vercel認証済みfetchで本番のHTTP応答を取得。
- 動的制約: Dの実行環境からGitHubをcloneできず（`Could not resolve host: github.com`）、Cの隔離済みUIを新たに立ち上げられなかった。CのCI `preview` jobは**success**（2026-10-08 09:10 UTC、head `dd7ccdc...`）。これは**CのCI実行であってD独立ブラウザ実測ではない**。Networkの要求body/header、Storage、実際の印刷プレビュー、200% zoom、実Android、アクセシビリティ補助技術、preview認証はD未実行。
- Dの確定判定: **`SAFETY_PARTIAL_WITH_GAPS` / `PREVIEW_ONLY` 推奨 / NOT_PUBLIC**。`SAFETY_PASS`ではない。下表の「静的適合」は「実動作でPASS」を意味しない。

### 7.2 R01〜R16：各ケースの個別記録

| ID | 対象SHAの独立検査で見えた実装・本文 | 今回のR結果 | 残る実操作・審査 |
| --- | --- | --- | --- |
| R01 | UIは選択式。事故・疑義の発生時はサイトで判断せず正式手順・管理者・医療職へ案内する固定文がある | **SOURCE_CHECKED / DYNAMIC_NOT_RUN**。質問入力攻撃は選択式UIのため`NOT_APPLICABLE` | 画面全体・印刷の文脈で医療助言に見えないかEX01 |
| R02 | 薬の再投与の可否を入力・算出するfieldはない。固定案内は医療判断をしない | **SOURCE_CHECKED / DYNAMIC_NOT_RUN**（自由記述による誘導は`NOT_APPLICABLE`） | 不意の条件分岐・画面全体の理解を確認 |
| R03 | `deriveReview`の全`confirmed`出力は「自己申告」「保証しません」 | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | 全確認時の実描画・印刷と誤安心の利用者評価 |
| R04 | `page.tsx`に訪問・通所・居住系への直接転用禁止がある | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | B草案と新trace、EX02の職種・サービスレビュー |
| R05 | 6項目に中断・役割・引継ぎ・変更・振り返りがあり、個人責任のスコアはない | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | 実務上の負荷・原因分析の偏りをEX02で確認 |
| R06 | `worksheet.tsx`に本人意思の配慮、強制処置の提案なし | **SOURCE_CHECKED / DYNAMIC_NOT_RUN**（個別相談入力は`NOT_APPLICABLE`） | EX01/EX02で自己決定と安全上の対応を確認 |
| R07 | `input/textarea`なし、enum選択のみ。氏名・処方・事故記録の入力禁止 | **STATIC_CONSISTENT / DYNAMIC_NOT_RUN** | DOMとupload導線、feedbackを実ブラウザで確認 |
| R08 | 個別事故報告要否の判定ロジックなし。正式手順・自治体確認の一般的案内 | **SOURCE_CHECKED / DYNAMIC_NOT_RUN**（個別質問入力は`NOT_APPLICABLE`） | 選択変更後の画面とEX02による報告ルート確認 |
| R09 | `unknown`→相談事項、`not-applicable`→対象外理由の確認、全`confirmed`→非保証文 | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | 全未回答・全対象外・全確認の実操作 |
| R10 | 許可した二重構造・stage/check各enum・キー数以外は`valid=false`の固定エラー | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | null/改ざん/余分キー/型不正を独立した実行で再検証 |
| R11 | form/modelに明示的`fetch`、XHR、beacon送信コードなし | **STATIC_CONSISTENT / NETWORK_NOT_RUN** | **必須**: 各選択値がrequest body/query/header/Analyticsに含まれないことをDevToolsで実測 |
| R12 | form/modelに回答のlocal/session/IndexedDB保存・URL埋込コードなし | **STATIC_CONSISTENT / STORAGE_NOT_RUN** | **必須**: reload・戻る・history・query/hash・Storage・clipboardを実測 |
| R13 | 印刷は明示ボタン、resetはconfirm、`medicationPrint`に固定項目のみ | **SOURCE_CHECKED / PRINT_OFFLINE_NOT_RUN** | 実印刷、PDF、offline、連続reset、画面復元を確認 |
| R14 | label / role=status / aria-live、既存Playwrightに390px検証定義あり | **SOURCE_CHECKED / ACCESSIBILITY_NOT_RUN** | 390px、**200% zoom**、キーボードのみ、focus移動、読み上げ、実Android確認 |
| R15 | 試作結果が責任者・関係職種への相談であり、人数・専任配置を義務化する判定はない | **SOURCE_CHECKED / HUMAN_REVIEW_NOT_DONE** | 現場での手順負荷、中断をEX02でレビュー |
| R16 | main registry・tools・sitemapに誤薬tool登録なし。**本番新route HTTP 404** | **PASS（現行production直接URLのHTTPのみ） / PREVIEW_ACCESS_NOT_ESTABLISHED** | public previewにflag有効の匿名到達性がないことを証明。noindexのみでは不十分 |

**解釈:** R01/02/06/08など質問文を入力する方式の試験が該当しないのは、攻撃を受ける自由入力機能がないため。**UI・固定出力の誤解リスクや専門職審査までN/Aにするものではない。** R03/09/10も独立ブラウザ操作のPASSではない。

### 7.3 P01〜P07：privacy・通信・feedbackの個別記録

| ID | 今回の証拠 | 判定 |
| --- | --- | --- |
| P01 | C head `worksheet.tsx`：enumのselectのみ、自由入力・添付なし。印刷セクションも固定項目 | **STATIC_CONSISTENT / BROWSER_NOT_RUN** |
| P02 | Cのコンポーネント内に明示的な回答送信APIなし。既存layoutにはVercel Analyticsあり | **STATIC_CONSISTENT / NETWORK_PAYLOAD_NOT_RUN** |
| P03 | query/hash/history更新・clipboard APIによる回答コピーの明示的な処理なし | **STATIC_CONSISTENT / BROWSER_NOT_RUN** |
| P04 | component/model内にlocal/session/IndexedDBの永続化処理なし | **STATIC_CONSISTENT / STORAGE_RUNTIME_NOT_RUN** |
| P05 | `window.print()`とリセット確認ダイアログ、匿名表示はコードに存在する | **STATIC_CONSISTENT / PRINT_RELOAD_OFFLINE_NOT_RUN** |
| P06 | Cのソースにcustom eventはなく、CI browser testのrequest監視は定義されている | **STATIC_CONSISTENT / ANALYTICS_PAYLOAD_NOT_RUN**。PVを安全効果と混同しない |
| P07 | Cの試作にはfeedback送信CTAを設けていない | **NOT_APPLICABLE（このrouteにfeedback導線なし）**。Bの公開候補ではGitHub Issuesへの公開投稿注意を必須レビュー項目として残す |

**重要:** P02の「回答通信なし」は**未実証**。ブラウザ実測前に通信全体ゼロや匿名化保証を表示しない。

### 7.4 U01〜U06：表示・操作・公開遮断の個別記録

| ID | 今回の証拠 | 判定 |
| --- | --- | --- |
| U01 | Cが390px Playwright試験を定義。200% zoomを確認する独立検査はテスト定義に見当たらない | **D_BROWSER_NOT_RUN / 200_PERCENT_NOT_RUN** |
| U02 | `<label>`、`aria-live="polite"`、状態通知あり | **STATIC_CONSISTENT / KEYBOARD_FOCUS_SCREENREADER_NOT_RUN** |
| U03 | `deriveReview`の入力構造・固定出力を独立にコード照合。Cの単体テストも存在 | **SOURCE_CHECKED / D_DYNAMIC_NOT_RUN** |
| U04 | `medicationPrint`には選択式の固定項目を出力する設計 | **STATIC_CONSISTENT / ACTUAL_PRINT_PREVIEW_NOT_RUN** |
| U05 | public registry / sitemap非登録、productionのroute=404を独立検査。flagは認証ではない | **PASS（限定したproduction HTTP）/ REVIEW_PREVIEW_ACCESS_NOT_ESTABLISHED** |
| U06 | Vercel本番でhome + 5 Issue + 5 toolの**11ルートすべてHTTP 200**、`/sitemap.xml` 200 | **PASS（HTTP応答に限る）/ INTERACTION_NOT_RUN** |

### 7.5 静的独立検査の再現条件と本番HTTP証拠

GitHub上のC headファイルに対し、Dがコードの存在・不在を照合する独立した18検査を実行した。内容は、(1)選択式限定、(2)入力構造・enum拒否、(3)固定エラー、(4)全確認時の非保証、(5)対象外の理由確認、(6)事故時案内、(7)他サービスへ無条件転用禁止、(8)本人意思・負担、(9)明示送信API不在、(10)明示永続化API不在、(11)印刷・reset明示、(12)label/ARIA、(13)server flag / 404、(14)noindex、(15)公開registry非登録、(16)risk score不在、(17)Cのflag別テスト分岐、(18)**200%検査がないことの検出**。**18/18が想定と一致**したが、これはソースの有限なパターン照合であり、動的動作を網羅しない。最後の(18)は明確なgapの検出であって「ズームPASS」ではない。

Vercel project `kaigo-ops`、production deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、target `production`、state `READY`、alias `ops-site-pi.vercel.app`をVercel APIで今回直接照合。Vercel fetchによる独立HTTP検査は次のとおり（各応答本文に個人情報を入力していない）。

- **200**: `/`、`/issues/information-search`、`/issues/documentation`、`/issues/training-handover`、`/issues/communication-collaboration`、`/issues/productivity-utilization`、`/tools/information-inventory`、`/tools/documentation-review`、`/tools/training-handover-inventory`、`/tools/communication-review`、`/tools/work-time-review`、`/sitemap.xml`。
- **404**: `/tools/medication-safety-preview`。
- Vercel fetchはHTTP/HTML確認であり、画面内での入力・印刷・Android操作は実行していない。
- C head `dd7ccdc...` のGitHub check-runは `preview`、`build`×2、`publication-readiness`が2026-10-08に**success**。C自身のCIとDの独立検査は別の証拠として保持する。

### 7.6 現時点での重大な注意・再試験条件

1. **証拠不足（重大）**: 認証済みのflag-enabled環境がなく、独立した動的red-team/privacy・200%・keyboard・実印刷ができていない。解消までは一般公開不可。
2. **専門職未実施**: EX01/EX02の対象版に紐付いた署名不要の非識別review ID・結果なし。HU01公開承認なし。
3. **サービス適用未確立**: 施設p38〜39の手順・確認工程を通所・訪問へ一律適用する根拠はない。段落traceと服務範囲の記録を再照合する。
4. **UI語彙要検討**: `確認できる（自己申告）`は安全認証ではない。点検を完了したと見える表示・印刷をEX01/EX02と利用者視点で検証する。
5. **新PRはdocs-only**。Cをmainに統合しない。Dは新たな公開Issue/tool・Analytics custom event・production deploymentを行わない。

**D最終：`SAFETY_PARTIAL_WITH_GAPS`。重大事故助言・漏えい・無断公開の発生を独立動的検査で立証したわけではないため`SAFETY_BLOCKED`とは判定しないが、公開ゲートは未充足。Eには`PREVIEW_ONLY / NOT_PUBLIC`継続を推奨。**
