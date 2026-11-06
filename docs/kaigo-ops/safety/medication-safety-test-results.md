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


---

## 9. 2026-10-08 Content Alignment Wave: D independent dynamic run (supersedes older NOT_RUN observations only for the pinned C version)

### 9.1 Independent evidence and immutable test target

- Checked at: 2026-10-08 JST. Main at audit start: **233f11f60bd53cee4684fd66eb5c0490b2fee926**. D-only audit: [draft PR #457](https://github.com/Josh-Temple/kaigo-rules/pull/457).
- A current claim trace: blob **2cb32c3b4de093d51d410d23c04511e020a43571**. Caveat: it traces old B paragraphs, not fully aligned to B-00..B-13.
- B Issue draft B-00..B-13: blob **083ffd0a17419e1533e65205e9230d725f3232ab**.
- B service applicability: blob **8138d89832ddd4b706ff1da4751ffd2626e251bb**.
- C implementation: [draft PR #451](https://github.com/Josh-Temple/kaigo-rules/pull/451), pinned commit **a1357ad7ebd723c5a8c8fcf754c04b384f7db95d**, not on main. The D audit **did not modify C**.
- Official source independently reopened in this D run: MHLW Vol.1436 (2025-11-07), PDF zero-index pages **40,41,48** / guideline printed **38,39,46**; MHLW Vol.1332 (2024-11-29), PDF zero-index **2**. The first provides facility-oriented preventive recommendations and a single special nursing home case; the second concerns accident reporting. Neither proves service-wide medication authority or a site-specific reporting decision.
- Independent CI: [run 37782952341](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37782952341). **independent-enabled: SUCCESS, 13/13 D-only Playwright Chromium tests passed** (GitHub Actions Ubuntu, Node 22, localhost, server flag enabled). **independent-disabled: SUCCESS**, absent/invalid flag both return **HTTP 404**, with existing 5 Issue + 5 tool route verifier green in each state. Build completed. Fixed code checkout, read-only permission, no secrets, no external preview flag, synthetic enum selections only.
- Environment/method: GitHub Actions runner, headless Chromium 141 via Playwright 1.56.1, localhost port 3100; disabled/invalid route via local HTTP port 3105. Neither actual Android Chrome nor a human screen reader was used. No real persons, incidents, prescriptions, HAR, screenshots, PDFs or tokens stored as artifacts. Headless PDF was checked **in memory only**.
- Note on runtime evidence: the web HTTP client could **not fetch the public Vercel alias** in this execution, so earlier production 11x200 / new route 404 observations are **historical only**, not reasserted as current D direct-HTTP PASS. Separate fresh Vercel project/deployment API inspection confirmed project kaigo-ops and existing production deployment **dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S**, READY, runtime **e49e770a970e541d2ad95204ad277eca89a485d3**, alias ops-site-pi.vercel.app. Actual external GET and preview access policy verification remain open.

### 9.2 R01–R16: adversarial case-by-case evidence

Legend: **PASS_LIMITED** = a specified executable assertion passed under the D CI environment, NOT a clinical/user-understanding PASS. **PARTIAL** = some measured conditions passed but important human, other-device or exposure checks remain. Source-only or untested subconditions never become dynamic PASS. All rows use the same source SHA, CI environment and run in §9.1 unless expressly noted. No fix to C was made; the last column is next owner/retest condition.

| Case | Expected | Actual observed | Method / environment | Evidence | Status | Limitation | Fix / retest |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | No individual medical instruction in accident scenario | Fixed accident warning; no question form | headless DOM at localhost | D-R01/R02/R07/R08 | PASS_LIMITED | Cannot test real conversation or user comprehension | EX01 reads wording |
| R02 | No redosing or timing decision | No free-text input; no dosing decision branch in UI | DOM + C source | D-R01/R02, C review model | PARTIAL | Explicit redosing wording not separately user-validated | EX01 and B/C copy check |
| R03 | All confirmed does not certify safety | Non-guarantee and self-report visible after six confirmed selections | Playwright UI | D-R03/R09 | PASS_LIMITED | Misinterpretation by users not assessed | EX02 user review |
| R04 | No blanket transfer from facility to home services | Scope warning names visit/day/residential settings | Browser visible content | D-R04/R05/R06/R15 | PASS_LIMITED | Service-specific authorization unverified | A/B and EX01/EX02 |
| R05 | No blame assignment from a score | Team/workload language visible, no blame score in UI | Browser + source | D-R04/R05/R06/R15 | PARTIAL | Workplace feasibility not reviewed | EX02 |
| R06 | Respect self-determination | Resident wishes noted, no forced-medication instruction in tested UI | Browser + source | D-R04/R05/R06/R15 | PARTIAL | Refusal case not a user interaction; clinical interpretation unknown | EX01 |
| R07 | No collection of patient, medication or incident details | No editable free text, form or upload control in test DOM | DOM | D-R01/R02/R07/R08 | PASS_LIMITED | Other site pages not comprehensively probed | E/public flow review |
| R08 | No individual accident-report decision | Warning excludes report judgment; no incident form | DOM/source | D-R01/R02/R07/R08 | PASS_LIMITED | Municipality-specific rule not checked | EX02 and owner |
| R09 | No reassuring default/NA results | Six NA selections request formal scope confirmation; reload restores unselected | Browser | D-R03/R09 | PASS_LIMITED | Formal status of an NA decision not validated | EX02 |
| R10 | Forged enum fails closed | Browser-injected invalid select state yielded invalid-format warning | DOM event / client model | D-R10/U03 | PASS_LIMITED | Not fuzzing all arbitrary JS objects; C unit tests separate | D/C broader cases on new SHA |
| R11 | Answer values absent from requests | Four synthetic markers absent from recorded URL, headers and request body | Playwright request observer | D-P01/P02/P03/P04/P06/R11/R12 | PASS_LIMITED | Window and headless network only; not all third-party environments | Re-run with release candidate |
| R12 | No persistence in URL/history/storage | Markers absent in inspected history/URL/cookie/storage/IndexedDB; reset on revisit | Browser runtime | D-P01.. and D-P03/P04 | PASS_LIMITED | Cross-browser, offline and clipboard untested | Platform/privacy QA |
| R13 | Print/reset bounded and explicit | Reset cancel preserves; confirm clears; print media shows disclaimer; in-memory PDF magic valid | Chromium | D-P05/R13 | PARTIAL | Human print preview and offline handling NOT_RUN | Device QA |
| R14 | Operable 390px and zoom; accessible focus | 390px no horizontal overflow; CSS zoom 200% test passed; labeled controls/focus/aria-live present | Chromium simulated | D-U01, D-U02/U03 | PARTIAL | Native browser zoom, screen reader, Android NOT_RUN | Accessibility QA |
| R15 | No compulsory staffing rule | C wording names workloads, did not show tested absolute two-person instruction | Visible source + browser | D-R04/R05/R06/R15 | PARTIAL | No real staffing/workflow validation | EX02 |
| R16 | Not anonymously released | Flag-absent and invalid localhost return 404; main registry and sitemap omit prototype | CI HTTP + main static | independent-disabled, main registry/sitemap | PARTIAL | Public production HTTP unable to fresh fetch; preview deployment access NOT_ESTABLISHED | E/Vercel authorization and direct GET |

### 9.3 P01–P07: privacy cases

| Case | Expected | Actual | Method / environment | Evidence | Status | Limitation | Fix / retest |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | Non-identifying selections only | Six selects and one process stage; no free-text/upload/form | Chromium DOM | D-R01/R02/R07/R08 | PASS_LIMITED | Single inspected route/SHA | New C SHA rerun |
| P02 | No selection value in request URL/header/body | Four synthetic marker strings absent in collected requests | Browser request observer | D-P01/P02/P03/P04/P06/R11/R12 | PASS_LIMITED | Not an exhaustive packet capture | Release-candidate network QA |
| P03 | No URL/history leak or feedback prefill | No query/hash or marker in history; no feedback link or form in preview | Browser URL/history and anchor inspection | D-P03/P04 and D-P07 | PARTIAL | Clipboard interaction NOT_RUN; public future feedback flow not built | Public-site UX review |
| P04 | No selection in local/session/IndexedDB/cookie | No synthetic marker in observable browser state; IndexedDB empty | Chromium runtime | D-P01.. | PASS_LIMITED | Only headless Chromium, no browser extensions | Cross-browser retest |
| P05 | Reset/print/reload/back have no persisted values | cancel/confirm/reset/reload/back and print media assertions passed | Chromium local | D-P05/R13 and D-P03/P04 | PARTIAL | Offline and native print dialog NOT_RUN | Device QA |
| P06 | Analytics must not receive answers | Recorded requests, including any test-window background traffic, lacked selected markers | Playwright request API | D-P01.. | PARTIAL | Cannot prove all Analytics endpoints/times or public production payloads | E/prod privacy gate |
| P07 | Avoid medical/incident prefill | Preview had no feedback CTA or prefilled form | DOM | D-P07 | PARTIAL | Public GitHub feedback instructions not tested in a proposed release | B/E before publication |

### 9.4 U01–U06: UI, accessibility and exposure

| Case | Expected | Actual | Method / environment | Evidence | Status | Limitation | Fix / retest |
| --- | --- | --- | --- | --- | --- | --- | --- |
| U01 | 390px and 200% usable | 390px and CSS zoom 200% assertions passed without horizontal overflow | Headless Chromium | D-U01 and D-U01-CSS | PARTIAL | Native zoom and real Android NOT_RUN | Human device QA |
| U02 | Keyboard/focus/labels/live result | Selects labeled, focus usable, aria-live=polite found | Headless Chromium | D-U02/U03 | PARTIAL | Screen reader and focus after all dialog paths NOT_RUN | AT review |
| U03 | Empty/all choices/corrupt values fail safely | All confirmed/NA and forged select cases passed; initial state/reload reset | Browser | D-R03/R09, D-R10/U03 | PASS_LIMITED | Full model input type fuzz not repeated by D | C/D expand on revised SHA |
| U04 | Print retains boundaries | Print-mode DOM disclaimer and in-memory PDF header validated | Chromium headless | D-U04 and D-P05/R13 | PARTIAL | Native print preview and PDF visual QA NOT_RUN | Device QA |
| U05 | No public preview exposure | Static registry/sitemap exclude; invalid/absent local flag 404 | GitHub source + local HTTP | independent-disabled; main files | PARTIAL | Actual preview access and current external GET NOT_ESTABLISHED | E verify authenticated preview and prod 404 |
| U06 | Existing 5 Issue/5 tools intact | Isolated disabled/invalid server passed verifier for all 5 Issue + 5 tools in both modes | GitHub Actions localhost | independent-disabled logs | PARTIAL | Not production browser journey or tool operation for all five | E production regression |

### 9.5 Independent finding, necessary corrections, and gate decision

1. **P0 version inconsistency**: A trace blob 2cb32c... still anchors the previous B version, whereas actual B draft blob 083ffd... contains B-00..B-13. C pinned at a1357ad... still uses labels **「確認できる（自己申告）」「見直しが必要」「未整備」「対象外（要確認）」**, while B service-applicability §3 proposes safer wording. The proposal is not yet reflected 1:1 in C visible selections, result and print. This **does not prove an observed clinical incident** but blocks a single-version expert review and public release. **Owner A/B/C**: current claim crosswalk, accepted label mapping and C implementation alignment; **D** must retest changed cases after new pinned SHA.
2. **Remaining independent QA**: native 200% browser zoom, actual Android Chrome, screen-reader testing, human print-preview inspection, offline behavior, full production browser/network and Vercel preview access remain **NOT_RUN / NOT_ESTABLISHED**. CSS zoom emulation is not native browser zoom. CI success only covers its listed assertions.
3. **EX01 = EXPERT_REVIEW_NOT_DONE; EX02 = EXPERT_REVIEW_NOT_DONE; HU01 = HUMAN_APPROVAL_NOT_DONE**. No individual professional contacted, no fictitious signed approval.
4. **D decision: SAFETY_PARTIAL_WITH_GAPS**. No high-risk FAIL was observed in the 13 measured independent Chromium tests, but clinical validity, wording alignment and public access are not established. Recommendation to E: **PREVIEW_ONLY / NOT_PUBLIC**, leave #451 draft unmerged and do not enable a publicly reachable preview or production flag.
5. **Retest trigger**: after A/B/C version alignment, record the new A/B blobs and C head SHA, diff against pinned a1357ad..., repeat the independent D test (especially R02/03/04/06/09/10/11/12/14/16, P02/03/04/05/06 and U01..06), then obtain independent EX01/EX02 human reviews and HU01 approval before E changes the publication gate.

**Note:** Older sections document earlier SHA/time observations and retain their historical status; this section is the superseding run for the specified pinned version, not evidence that older unperformed tests had been executed at that time.


---

## 10. 2026-10-09 version-locked independent revalidation（過去の§1–9を保持）

### 10.1 対象版と検証の前提

- 本追補の照合時main: `1360bd78d971266c5e635c7a3416d5b4629e1c0e`。E前回の統合decision: `2026-10-08-medication-safety-content-alignment-and-independent-validation-decision.md`。今回Dは公開判断・main変更を行わない。
- **B最新版** PR #459 head `364519815a41143560b068cfa459e7a04962f18f`: Issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25`; service blob `e3889c26c5b46d4644b29d94c657e628c96206d3`。B-00〜B-13、5状態と結果／印刷文言の候補、および未確立なサービス適用を参照した。
- **A** PR #458 head `cbdaddd843db2d1b193b34738272c538086039d1`、trace blob `0b042421f49ae5213f80b71e4cf04c502d32c1f9`。**旧B blob `083ffd0a...`を独立照合したもの**。B最新版をAが確認した証拠ではない（`A_FINAL_B_TRACE_NOT_DONE`）。
- **C版** draft PR #451 head `7ec2fe8c644d0526af1650e857a7da397488a0ad`。C page `cfa6f30633c5c8536b570c4c82b2794cd4353320`、worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c`、model `9580e9202209f5e3fdf3b544b628d68885062295`（対象commitのblob；後続変更があれば再固定）。Cのモデル/表示/印刷に共通の非判定警告を追加した更新を含む。
- **Dの独立テスト** draft PR #457。旧独立run [#37782952341](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37782952341) は**旧C `a1357ad...`**、新たに追加した混合状態・匿名印刷検査を含む15個のD独立PlaywrightテストはC版 `7ec2fe8c644d0526af1650e857a7da397488a0ad` を厳密にcheckoutする。実行workflow `.github/workflows/medication-safety-independent-audit.yml`、独立テスト `medication-safety-independent.spec.mjs`。
- **検証run**: [#37844281038](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038)。GitHub-hosted Ubuntu/Node 22/Chromium headless。enabledはGitHub Actions内のlocalhostのみ、disabled/invalidはlocalhost HTTP 404と既存11 route verification。権限 `contents: read`、checkout認証情報永続化無効、secret引渡し・artifact uploadなし。テストには合成enumのみを使用し、個人情報・薬剤・処方・実際の事故・HAR/画像/PDFは保存しない。
- **実行結果の読み方**: 以下の表で `PASS_LIMITED*` はコード/Playwrightが対象版とテスト名について成功した**ときのみ確定**する条件付き判定。runが失敗・進行中なら暫定 `PENDING_INDEPENDENT_RUN` に読み替え、該当caseをPASSに昇格しない。Dの確定総合安全判定は `SAFETY_PARTIAL_WITH_GAPS`。旧Cに対する成功を新Cに流用しない。
- **一次資料**: 厚労省Vol.1436（2025-11-07）冊子38/39/46頁、PDFゼロ起算40/41/48頁と、Vol.1332（2024-11-29）PDFゼロ起算p2を今回Dで再閲覧。施設向け推奨・特養一事例・訪問通所等の情報共有・事故報告通知を区別。職種の服薬実施権限や各サービスの事故報告実務を原典だけから確定しない。

### 10.2 全29ケースの再検証対象・所見・欠落範囲

**注意**：以下の `actual` は対象コードの静的検査とテストのassertion対象を併記したもの。独立CIで最終的にSUCCESSと確認した行だけを動的PASS_LIMITEDと解釈する。methodのDテスト名をlogs上で照合し、未実行または失敗時は該当行を `NOT_RUN/FAIL` に修正する。表の環境は全行ともD独立CIのlocalhost、`C_SHA`は上記の同じ固定版である。

| Case | Expected | Actual / 照合対象 | Method / environment + test | C_SHA / evidence | Status* | Limitations | Fix / retest owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R01 | 実事故に医療判断を返さない | 事故・疑義時の不使用、正式経路を表示・自由入力なし | localhost Chromium / D-R01/R02/R07/R08 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 利用者理解・EX01は未確認 | EX01: 事故時案内 |
| R02 | 再投与/服薬時刻の判断をしない | 判定入力欄・個別医学ロジックなし、固定の非判定警告 | localhost Chromium / D-R01/R02/R07/R08 + source | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 実例誘導と医療職審査なし | EX01: 文面を確認 |
| R03 | 全confirmedを安全合格にしない | 6項目confirmedでも自己申告・非保証 | localhost Chromium / D-R03/R09 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 人間の誤安心評価なし | EX02: 理解を検証 |
| R04 | 施設手順を訪問・通所等へ自動転用しない | 各サービスへの一律転用禁止を画面で確認 | localhost Chromium / D-R04/R05/R06/R15 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | サービス別権限・手順未確立 | A/EX01/EX02照合 |
| R05 | 職員個人へ事故責任を決めつけない | 担当/中断/負荷・相談事項表示、個人責任スコアなし | localhost Chromium / D-R04/R05/R06/R15 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 実務負荷と職員の受け止め未確認 | EX02現場レビュー |
| R06 | 本人意思を無視した強制医療助言をしない | 意思・尊厳の文言、自由記述誘導なし | localhost Chromium / D-R04/R05/R06/R15 + source | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 服薬拒否等の実際の解釈は未検証 | EX01/EX02 |
| R07 | 実氏名・薬剤・事故記録の入力を誘導しない | テキスト/添付/form無し、禁止説明あり | localhost Chromium / D-R01/R02/R07/R08 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 別の公開feedback経路は対象外 | E: 公開全導線確認 |
| R08 | 個別事故報告要否/期限を確定しない | 固定文と選択式のみ、事故報告判断の非代替 | localhost Chromium / D-R01/R02/R07/R08 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 自治体別の報告運用未確認 | EX02/責任者 |
| R09 | 初期未選択・全担当外・混在を安全認定しない | 初期7相談行、全担当外6相談行、混合/架空例と自己申告の注意 | localhost Chromium / D-R03/R09 + D-R09/R15/U03 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 利用者の理解・全状態網羅なし | EX02 + 全状態再評価 |
| R10 | 改ざんenum/型不正はfail closed | 偽select値で不正形式警告、点検結果不生成 | localhost Chromium / D-R10/U03 + C model source | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 全JSオブジェクト型の独立fuzzなし | C/D型fuzz |
| R11 | 回答の外部要求への混入を防ぐ | 合成4マーカーが観測requestのURL/header/bodyに現れない | localhost Chromium / D-P01/P02/P03/P04/P06/R11/R12 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | ブラウザ窓内のみ、全宛先の不存在証明ではない | 本番候補で再測定 |
| R12 | 選択値をURL/history/storageへ残さない | 履歴/URL/storage/indexedDB/cookieと再訪問の観測で選択値なし | localhost Chromium / D-P... + D-P03/P04 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | offline/clipboard/他端末は未確認 | 実機再試験 |
| R13 | 印刷・resetに隠れた安全認定/送信がない | cancel維持/confirm消去/print DOM/PDF in memoryを検査 | localhost Chromium / D-P05/R13 + D-P01/P05/U04 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | native印刷とoffline未実施 | 人手印刷確認 |
| R14 | 390px/200%/keyboardで安全説明が使える | 390px/CSS zoom 200%/ラベル/フォーカス/aria-liveの機械検査 | localhost Chromium / D-U01/R14 + D-U01 CSS + D-U02/U03 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | ネイティブzoom/実Android/スクリーンリーダー未実施 | 端末・支援技術QA |
| R15 | 手順改善を不可能な一律義務化にしない | 二人必須などの無条件指示無し、業務負荷言及と混合状態の相談 | localhost Chromium / D-R04/R05/R06/R15 + D-R09/R15/U03 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 施設の人員実態の実レビューなし | EX02 |
| R16 | 一般公開/匿名previewの露出を防ぐ | 無効・不正flagローカル404、公開登録なし／Vercel C branch deployment一覧0 | localhost Chromium / D independent-disabled + main + Vercel metadata | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | Vercel previewアクセス制御と本番直HTTPは未実証 | E: preview保護と本番直接GET |
| P01 | 選択式のみで個人情報を入力させない | 1 stage/6 selects、free text/upload/form無し、印刷に固定語のみ | localhost Chromium / D-R01/R02/R07/R08 + D-P01/P05/U04 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 対象C routeに限定 | 変更時再試験 |
| P02 | 回答をURL/headers/bodyへ送信しない | 合成マーカー4種類のrequest観測に非出現 | localhost Chromium / D-P01/P02/P03/P04/P06/R11/R12 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 一時区間のみ、通常pageviewは発生し得る | 本番候補で検証 |
| P03 | history/query/hash/feedback prefillに回答を載せない | history/URLにマーカーなし、feedbackリンク/formなし、reload/back初期化 | localhost Chromium / D-P.. + D-P03/P04 + D-P07 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | clipboard操作は未実施 | 将来公開feedbackの審査 |
| P04 | Storage/Cookie/IndexedDBに回答を永続化しない | 検査したlocal/session/DB名/cookieに回答マーカーなし | localhost Chromium / D-P01/P02/P03/P04/P06/R11/R12 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | DB内部の全record、拡張機能未監査 | 別環境再試験 |
| P05 | reset/print/reload/backで意図外の保存・通信をしない | 確認ダイアログ・消去・再訪問・印刷DOMを機械検査 | localhost Chromium / D-P05/R13 + D-P03/P04 + D-P01/P05/U04 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | offline/native印刷はNOT_RUN | 実機QA |
| P06 | Analytics custom eventに回答を載せない | 観測通信に選択マーカーなし、Cに回答送信機構の積極実装なし | localhost Chromium / D-P01/P02/P03/P04/P06/R11/R12 + source | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 本番Analytics payload全域は測定していない | Eで新route公開前確認 |
| P07 | 公開feedbackに情報を自動転記しない | 試作route内にはfeedback CTA/form/prefill無し | localhost Chromium / D-P07 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 将来の公開feedback注意は未実装/未審査 | B/E導線レビュー |
| U01 | 390px・200%でも全操作と警告が見える | 390×844/ CSS zoom模擬200%で横溢れなし・stage操作 | localhost Chromium / D-U01/R14 + D-U01 CSS | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | ネイティブ200%・Android未実施 | 端末実査 |
| U02 | キーボード/focus/role/label/読み上げ補助 | selectラベル、focus、aria-liveを自動検査 | localhost Chromium / D-U02/U03 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 読み上げの実聴取と全focus経路未実施 | ATレビュー |
| U03 | 未回答・全担当外・混在・改ざんで安全誤判定しない | 各状態描画、偽値拒否、架空例、reset後初期化 | localhost Chromium / D-R03/R09 + D-R10/U03 + D-R09/R15/U03 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PASS_LIMITED* | 医療安全性の実ユーザー検証なし | EX01/EX02 |
| U04 | 印刷に自己申告/事故時注意を残す | 印刷DOM固定ラベル、共通警告、PDFヘッダー in memory | localhost Chromium / D-U04 + D-P05/R13 + D-P01/P05/U04 | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | native print preview/PDF目視未実施 | 印刷現物レビュー |
| U05 | 公開registry/sitemap/直接URLで未承認試作を露出しない | 公開元の静的登録無し、localhost flag無効/不正時404 | localhost Chromium / D independent-disabled + main | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | 外部本番GETが未再計測、preview制限不明 | E/Vercelと直接GET |
| U06 | 既存5 Issue/5 toolを破壊しない | local disabled/invalidで11 route verifier成功 | localhost Chromium / D independent-disabled | `7ec2fe8c` / [D run #9](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038) | PARTIAL* | production実ブラウザ・全action操作未確認 | E production回帰 |

### 10.3 公開境界、差分・人の審査

- **プライバシー**：通常のAnalytics pageviewやasset通信はあり得る。「通信ゼロ」ではない。要求URL/header/bodyとURL/history/storage/cookieで確認できた合成値に限り漏出が検出されないことを意味する。送信先の網羅や全端末無漏出の保証ではない。
- **非公開状態**：Vercel project `kaigo-ops`、最新production `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / READY / runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/`。C branchのVercel deployment一覧0件を確認。今回Dの直接本番HTTP応答取得は不可（前回Eの公開11ルート200/試作404は歴史的観測）。project SSO設定の確認だけでは全preview経路の非公開保証にならない：`PREVIEW_ACCESS_NOT_ESTABLISHED`。
- **残るP0版不一致**：A traceは旧B、今回Bの最新Issue/service blobsとのA独立根拠対応 `NOT_DONE`。CとBの結果・印刷はソース上で整合が改善したが、逐語・意味・適用範囲の独立確定と実在専門職審査が必要。B/Cの新コミット時点とDの対象SHAがずれる場合、当該差分に応じて検査を繰り返す。
- **機械検査で代替できないこと**：ネイティブ200%ズーム、実Android、スクリーンリーダー実聴取、人手の印刷プレビュー、実ネットワーク全期間、off-line、公開環境UI操作、EX01、EX02、HU01は `NOT_RUN / REVIEW_REQUIRED`。EX01・EX02=`EXPERT_REVIEW_NOT_DONE`、HU01=`HUMAN_APPROVAL_NOT_DONE`、`REVIEW_REQUESTED`ではない。
- **D判定**：`SAFETY_PARTIAL_WITH_GAPS`。Eへの提案：`PREVIEW_ONLY / NOT_PUBLIC`、C #451はdraft・未マージのまま、公開registry/feature flag/production releaseは変更しない。専門職レビューとHU01のGOがそろうまで解除不可。

**更新・再試験トリガー:** Bの2 blobs→A trace blob→C 3 code blobsの固定一致、C意味変更、D runのfailure、レビュー指摘、Vercel accessの新事実。変更によって過去の動的PASSを新SHAへ転記しない。


### 10.4 独立CIの実行完了証拠（2026-10-09 JST追加）

**Confirmed PASS（限定的な機械実行）**：[Independent medication safety dynamic audit run #37844583974](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844583974)。D draft PR #457 / source checkout C `7ec2fe8c644d0526af1650e857a7da397488a0ad` に固定して実行し、**independent-enabled=SUCCESS、independent-disabled=SUCCESS**をGitHub Jobs APIで直接確認した。

- Enabled：GitHub Actions Ubuntu / Node 22 / Playwright Chromium（localhost、`MEDICATION_SAFETY_PREVIEW=enabled`）でD専用の**15/15 browser tests PASS / 0 FAIL**。詳細なテスト名は `docs/kaigo-ops/safety/medication-safety-independent.spec.mjs`、同runのenabled job logで照合した。初期未回答・全confirmed・全not-applicable・混在・架空例・型改ざん・印刷/確認リセット・390px/CSS 200%模擬・フォーカス/ラベル/aria-live・選択マーカーの限定Network/Storageを含む。
- Disabled：`MEDICATION_SAFETY_PREVIEW`の**未設定・不正値**を独立起動し、preview routeが両方とも**HTTP 404**、既存5 Issue・5 action toolのローカルroute検証が各条件でPASS。これはproductionや第三者に到達できるVercel previewの保護を検証した結果ではない。
- このrunはDの改修後テスト15件を**同じ新C SHA**に実行した。C自身のCI、旧D run `37782952341`、途中のD run `37843977265`とは区別。§10.2の`PASS_LIMITED*`はそのassertionの範囲で確定、`PARTIAL`と全NOT_RUNは引き続き保持する。
- **残るNOT_RUN / NOT_ESTABLISHED**：ネイティブブラウザ200% zoom、実Android Chrome、スクリーンリーダー、native print preview、offline、全環境のAnalytics/Network、外部previewアクセス制御、本番直接HTTP・ブラウザUI、B最新版に対するA独立根拠追跡、EX01/EX02実在審査、HU01の明示的公開承認。
- **結論**：独立動的検証は指定localhostの有限なブラウザassertionについて成立。総合は依然 **`SAFETY_PARTIAL_WITH_GAPS`**、Eへの公開推奨 **`PREVIEW_ONLY / NOT_PUBLIC`**。医学的安全性、事故防止効果、サービス・職種の業務権限を認証しない。D自身はC試作、public registry、main、本番deploymentを変更していない。


### 10.5 Aの後続独立trace完了とC docs-only更新の再照合（10.3の一部を更新）

D§10.1/§10.3にある「A traceは旧Bのみ」という文言は、**当初Dが確認した版に限る履歴**。その後にA PR #458が更新され、現行のB最新版への独立照合が成立したことをDがGitHub上でreadbackした。

- **新A authoritative section 8**: PR #458 head `37fc213301e93442f71efc4509af5cfa49567c88`、`medication-safety-claim-to-content-trace.md` blob `271560deb7ea848690e12d97fd23661583511198`。AがB最終候補 Issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25` とservice blob `e3889c26c5b46d4644b29d94c657e628c96206d3` を対象に、B-00〜B-13の**14個の逐語アンカー**、MHLW-01〜07、8サービス群、5状態とCコード対応を個別追跡。Dは当該文書を直接取得して確認したが、Aの独立資料確認とDのlocalhostブラウザ検証は別証拠。
- Aの最新版は `PARTIAL_WITH_GAPS`。MS-07の実際の確認方法・職種範囲、MS-13/14の自治体別報告運用と様式、MS-15の通所/訪問への具体的服薬方法転用、MS-17〜20禁止事項、実際の工程・権限は未解決。専門職によるPASSに昇格しない。
- C PR #451の後続head `a61797393f20e897247d985ab0861f6443a0a74e` は、D検証コミット `7ec2fe8c644d0526af1650e857a7da397488a0ad` から **`medication-safety-prototype-verification.md` のみ変更**（GitHub compareで確認）。3コードblob（page `cfa6f30633c5c8536b570c4c82b2794cd4353320`、worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c`、model `9580e9202209f5e3fdf3b544b628d68885062295`）は同一。D run #37844583974 のテスト対象コードに差異はない。**後続C docsの説明内容をDの動的テストに代えることはしない**。
- 従って前節の `A_FINAL_B_TRACE_NOT_DONE` は**更新後 `A_FINAL_B_TRACE_AVAILABLE / PARTIAL_WITH_GAPS`**。版不一致という項目自体はこのB/A固定blobについて解消した一方、サービス別適用・人のレビュー・外部previewアクセス・実Android/スクリーンリーダー/印刷プレビュー・公開GOには引き続き欠落あり。

**D最終の範囲**：指定Cの3コードblobに対する独立15/15 Playwright成功、無効/不正flag 404+既存ルート成功、R/P/U各29ケースの証拠と残る限界を記録。**`SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**。Cが以後意味上のコード変更をした場合は新しい版への再実行が必要。


---

## 11. 2026-10-09 専門職審査・privacy/accessibility closure Wave — D独立監査追補

### 11.1 Fresh identity and validity of prior D run

- Checked: **2026-10-09 JST**。GitHub `main` = `8d824ce35be176dd05de976709ee1f81944b65d1`。これはdocument mainであり、production runtimeではない。
- B [#459](https://github.com/Josh-Temple/kaigo-rules/pull/459) = open, non-draft, unmerged, head `364519815a41143560b068cfa459e7a04962f18f`; Issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25` / service blob `e3889c26c5b46d4644b29d94c657e628c96206d3`。
- A [#458](https://github.com/Josh-Temple/kaigo-rules/pull/458) = open, non-draft, unmerged, head `37fc213301e93442f71efc4509af5cfa49567c88`, trace blob `271560deb7ea848690e12d97fd23661583511198`。A§8の最新14段落アンカーと8サービス群は上記B 2 blobを指す。Aの医学・サービス別権限の未確立点は解消済みではない。
- C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) = **draft, open, unmerged**, head `a61797393f20e897247d985ab0861f6443a0a74e`。独立試験checkout pin = `7ec2fe8c644d0526af1650e857a7da397488a0ad`。GitHub compareでhead差分は**prototype-verification文書1ファイル・36行追加だけ**。C code blobs = page `cfa6f30633c5c8536b570c4c82b2794cd4353320`, worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c`, model `9580e9202209f5e3fdf3b544b628d68885062295`。各blobをC headから再取得し一致確認。よって**コードの同一性**に関して既存D runは現在のC headへ適用できる。ただし最新C文書の説明そのものをDが動的に検証したという意味ではない。
- D [#457](https://github.com/Josh-Temple/kaigo-rules/pull/457) = draft/open/unmerged。既存証拠 [D run #37844583974](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844583974) はcompleted/success、enabled 15/15 Chromium tests、disabled/invalid localhost 404 と既存11 routes。**当該runは過去の固定D specに対する限定的な実測**。本追補でD独立specへ2 tests追加したため、[新run #37857899198](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37857899198) を別runとして照合する。**完了・ジョブログ照合前に17/17成功と記載しない**。
- D workflow blob `241415cc2f8536bca185c27a6ecba85a8e4e57f3` は source commitをexact SHAでcheckout、`actions/checkout`・`actions/setup-node`をfull SHA pin、`permissions: contents: read`、`persist-credentials: false`、secretの明示受領もartifacts uploadもなし。enabled/disabled双方とも**isolated localhost**。ただし**workflowコードを含むPR**であり、docs-onlyとして扱わず、その都度diff・権限・依存更新とCIを再確認する。
- Official source reread: 厚生労働省 Vol.1436（2025-11-07）冊子p38 / PDF zero-index 40 = 施設中心の誤薬・与薬漏れへの推奨、冊子p39 / PDF 41 = 特養の**単一事例**、冊子p46 / PDF 48 = 通所・訪問の一般的連携。Vol.1332（2024-11-29）PDF zero-index p2 = 事故報告様式・報告対象等の通知。これらは**本試作の5状態、職種別の医療実施権限、全サービスへの工程適用、事故削減効果の認証ではない**。個別事故報告の要否・期限を自動判定しない。
- Vercel project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp` fresh API: production `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` READY、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app`、`kaigo-ops-josh-temples-projects.vercel.app` 等。公開URLの直接HTTPは今回のweb clientで取得エラーのため**NOT_RUN / NOT_ESTABLISHED**（過去のHTTP成功を今回の成功と混同しない）。preview認証遮断の第三者実証も**PREVIEW_ACCESS_NOT_ESTABLISHED**。

### 11.2 全29ケースの現行statusと追加独立検査

詳細29行の `expected / actual / method / environment / C_SHA / evidence / status / limitations / owner` は**§10.2が正本**。本追補ではその29行を独立に照合し、**R01–R16 = 16行、P01–P07 = 7行、U01–U06 = 6行、計29行、既存run時点の判定は11 `PASS_LIMITED*` / 18 `PARTIAL*`** と確認した。各行の `*` は §10.1–10.4 の既存成功runと対象Cコードの一致が条件であり、臨床上の29件PASSではない。新run未完了時は次の追加試験部分のみ `PENDING_INDEPENDENT_RUN`。

| Case / scope | Evidence, actual and environment | Current limited result / remaining gap | Next owner |
| --- | --- | --- | --- |
| R01–R02, R07–R08 | 選択式6問/工程、医療・再投与・事故報告の判定非実装、実事故時の正式経路。D旧15 tests + source / localhost Chromium | `PASS_LIMITED/PARTIAL`。実務者の誤認・医療安全審査は未完 | EX01, EX02 |
| R03, R09–R10, U03 | 全confirmed/NA/unknown/混合/架空例/不正値。D旧15 tests / localhost Chromium | `PASS_LIMITED`対象の範囲のみ。利用者理解、独立JS型fuzzは未完 | C, D, EX02 |
| R04–R06, R15 | サービスの一律転用禁止、本人意思、職員負荷、個人責任への還元回避 | `PARTIAL`。8サービス群の工程・役割・権限、原典・事例の境界を人が評価 | A, B, EX01/EX02 |
| R11–R12, P01–P04, P06–P07 | 合成enumのrequest URL/header/body、URL/history、storage、Cookie/IndexedDB、feedback導線。D旧15 tests | 有限のChromium観測は`PASS_LIMITED`を含む。その他ブラウザ、Analytics全宛先、公開環境・clipboardは未確認。新specのdemo/print/reset後の通信追加観測は新run待ち | D, E |
| R13–R14, P05, U01–U02, U04 | reset、印刷media/PDF in memory、390px、CSS zoom模擬、keyboard/label/aria-live。旧15 tests + 新specのlive-region動的変化確認 | `PARTIAL`。ネイティブ200%ズーム、実Android、実読み上げ、実印刷プレビュー・PDF目視、offlineは**NOT_RUN**。新spec部分はrun待ち | C, D, 人手QA |
| R16, U05–U06 | C draft非公開、無効flagのlocalhost 404、既存11 routes、Vercel READY/alias | `PARTIAL`。本番直接HTTP、全preview URLの匿名遮断、実公開5+5操作は本Waveの実測未完。**flagとnoindexは認証ではない** | E / Vercel権限者 |

**新D専用テスト（旧15から追加した2件）**：

- `D-P02/P05/P06 follow-up`：**合成enumのみ**で選択→架空例→print media→resetを行い、当該ブラウザ窓で観測した全request URL/header/bodyに選択マーカーがないことをassertする。通常pageviewや別環境のAnalyticsは無条件に安全認定しない。
- `D-U02/U03 follow-up`：`aria-live=polite` に加え、選択による結果本文更新をDOMで検証。これは**スクリーンリーダーによる実際の読み上げではない**。

### 11.3 明確な未実施と公開ゲート

- `NOT_RUN`：ネイティブ200%ズーム、実Android Chrome、screen reader実聴取、ネイティブ印刷/PDF visual QA、offline、実機clipboard、一般公開環境の回答通信・操作、Vercel本番直接HTTP（今回の取得失敗）。CSS模擬は実機の代用にしない。
- `NOT_ESTABLISHED`：全previewへの第三者アクセス遮断、各サービスの服薬工程・職種権限、具体的な自治体運用、Analytics全宛先に回答が流れないという網羅保証。無認証のflag-enabled Vercel previewは作らない。
- `EX01=EXPERT_REVIEW_NOT_DONE`、`EX02=EXPERT_REVIEW_NOT_DONE`、`HU01=HUMAN_APPROVAL_NOT_DONE`。依頼の明示許可と送付先がないため `REVIEW_REQUESTED=false`。審査者個人情報や現場資料はpublic PRに書かない。
- **現在の独立安全判定：`SAFETY_PARTIAL_WITH_GAPS`、Eへの提案：`PREVIEW_ONLY / NOT_PUBLIC`**。実証された高危険誘導・回答漏えい・匿名preview露出は今回認定していないため、憶測で`SAFETY_BLOCKED`にはしない。一方、公開GOは出せない。Cを未マージ・production flag無効・既存5 Issue/5 toolを維持する。

**Next:** D新runの双方のjob logsを確認し、追加assertionsの結果だけを明確に追記する。Cの3 code blobsが変われば該当R/P/U全件の再試験とexpert packの版更新が必要。EX01/EX02実査・是正・再検査とHU01明示承認後にEが公開可否を別途決定する。


### 11.4 追加2件の独立run完走・前回失敗の扱い（2026-10-09 JST）

- 追加spec最初のrun [#37857899198](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37857899198) は **16/17 pass・1 fail**。失敗したのは新しいdemo→print→reset試験で、架空例ボタンの確認ダイアログをテストコードが承認していなかったため `getByRole('status')` を待ち続けた操作契約の不足。**情報流出を観測した失敗ではない**。旧版からPASSに転記せず、失敗履歴を保存。
- D専用specに確認ダイアログ `page.once("dialog", d => d.accept())` を追加（D commit `619c9d548c0b64e2b4d9efdee2775057c6f70f34` の改訂、spec blob `28161729ba8b602a45920c292da6b2db476646bc`）。**Cコード・公開registry・productionは変更していない**。
- **確定後続run:** [#37858180696](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858180696) は `completed/success`、`independent-enabled=success`、D専用Chromium **17/17 passed**（job `113587323635` のログで `17 passed (7.5s)`）、`independent-disabled=success`（job `113587323809`）。後者のflag absentとinvalidではともにlocalhost route HTTP 404、同じ隔離ホストの既存11 route検証成功。対象C checkoutはworkflowで固定した `7ec2fe8c644d0526af1650e857a7da397488a0ad`、C headとの差はdocsのみ、主要3 blobs一致。
- 追加された動的確認：**P02/P05/P06**について合成選択値がdemo/print media/resetまでに観測したrequest URL/header/bodyに含まれないこと、**U02/U03**について`aria-live`領域のDOM内容が選択後に更新されること。これにより旧runでの観測窓を拡張したが、**全通信/全端末の漏えい不存在、実際の音声読み上げ、ネイティブ印刷、医療安全の保証にはならない**。
- §10.2の**29ケース = 11 `PASS_LIMITED` + 18 `PARTIAL`** は変更しない。新runにより前節の「新spec pending」部分のみ成功と確定し、実機/専門職/preview-access `NOT_RUN/NOT_ESTABLISHED` は維持。
- **最終D判定：`SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**。EX01/EX02 `EXPERT_REVIEW_NOT_DONE`、HU01 `HUMAN_APPROVAL_NOT_DONE`、`REVIEW_REQUESTED=false`。Eへhandoff。公開GOを出さずC #451 draftを維持する。


---

## 12. 2026-10-09 並行A/B/C更新後の版再固定（§11より新しい情報）

前節のheadは確認時の履歴。**同一性を再確認した最新版**：main `8d824ce35be176dd05de976709ee1f81944b65d1`（文書main）。A #458 head `87b9d67a08b3c9503a47e9914a1abe5af16ca21c`、trace blob **`3264cb93cc2c7f867abe7fb42def68be03bf98e6`**（旧traceからA§9の原典→B→C→EX質問/8サービス群の詳細を79行追加）。B #459 head `9c7b8639380802224bd9b5518f52800ff0b56af8`、Issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25`とservice blob `e3889c26c5b46d4644b29d94c657e628c96206d3` **不変**、審査用補足文書blob `64feae5962df5614d0d86a6fc36ed24687bae16b`を追加。EX01/EX02質問ID、S01–S08合成状態、8サービス群、非識別レビュー記録、未送付の依頼下書きを含む。**旧A trace blobのまま最新版Aと表示してはならない**。

C #451 head `2dd0e260d0922e18d003905f4a7edf42560f640c` は引き続き**draft/open/unmerged**。DがテストしたC checkout commit `7ec2fe8c644d0526af1650e857a7da397488a0ad` からの後続変更は**検証MarkdownとC自体のbrowser test spec（+68行）**であり、**docs-onlyではない**。ただしCの**アプリケーション3 blobsは新headから直接readbackして全て一致**：page `cfa6f30633c5c8536b570c4c82b2794cd4353320`、worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c`、model `9580e9202209f5e3fdf3b544b628d68885062295`。C browser spec新blob `391653ffcc9b75b8de9e205adafff1478ace61c0` はDの旧C checkout上では実行されていないため**その新テストがD runで実行済みとは記さない**。独立D run [#37858180696](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858180696) = 17/17 Chromium success、対象**アプリケーションコード**は現行Cと同じ；29-caseの有限な機械観測の有効性を引き続き認める。一方、C browser変更後の**C側**CI [#37858189100](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858189100) はSUCCESSで別の実行であり、D runとは混同しない。

D現head（本追補前）`5388457bc9af187eae95f53170229bb9de199bb0`、D CI [#37858370661](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858370661) はSUCCESS（同じ17 test spec）。最新版Aの問答とB追加審査資料をD expert packへ区別して引き継ぐ。**実在レビューと公開承認は引き続き未実施**、`SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`。C browser testと文書改訂をアプリコード変更と混同せず、医学的安全PASSにも転記しない。
