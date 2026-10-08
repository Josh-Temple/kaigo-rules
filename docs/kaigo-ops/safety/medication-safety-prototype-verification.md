# Kaigo Ops — 服薬業務の安全点検シート試作：Worker C実行検証記録

- 記録日：2026-10-08 JST
- 対象：PR [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451)（draft / 未マージ、非公開試作）
- 検証したコードのSHA：`54b84cd85981c785110b1a9459a5f8852fddd64f`
- 最新main照合時SHA：`d5e5b5f1c3a019c801c81c1af737964183bf7ce4`
- 実行環境：GitHub-hosted Ubuntu runner、Node 22、Next.js production build、Playwright Chromium headless。CIサーバーは`127.0.0.1`に限定。
- 検証run：[37761326870](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37761326870)（2026-10-08 10:08 UTC付近に完了、2 jobsともSUCCESS）
- C判定：**限定した機械テストPASS／全体PARTIAL_WITH_GAPS／PREVIEW_ONLY／NOT_PUBLIC**
- 情報取扱い：合成された選択値のみ。実在の利用者・薬剤・事故・職員情報、認証token、HAR、画面キャプチャ、印刷ファイルの公開保存なし。

## 1. 何を実行したか

GitHub Actions `.github/workflows/validate-medication-safety-preview.yml` を2つの独立jobに分離した。

| job | flag | コマンドと動作 | 結果 |
| --- | --- | --- | --- |
| `preview` | `MEDICATION_SAFETY_PREVIEW=enabled` | `npm ci --no-audit --no-fund`、`npm test`、`npm run build`、`npm run test:browser`、ローカルHTTPサーバー上の`npm run verify:routes` | **SUCCESS**。Chromium 13 PASS / 1条件付きskip。既存5 Issue/5 toolのroute PASS。 |
| `disabled` | 未設定 | 同じ5コマンドの別実行。試作routeのHTTP 404と既存tool操作を確認 | **SUCCESS**。Chromium 8 PASS / 6条件付きskip。既存5 Issue/5 toolのroute PASS。 |
| `disabled`のHTTP smoke | 誤設定`not-enabled` | localhost起動し`/tools/medication-safety-preview`のHTTP statusを検査 | **PASS（404）**。正規フラグ以外ではアクセスを認めない。 |

flag有効jobで404ケース1件がスキップされ、無効jobでpreview専用操作6件がスキップされるのはテスト設計どおり。skipをPASSへ換算しない。

`npm run verify:routes`では、公開home、既存5 Issue、既存5ツール、および関連リンク・feedback・Kaigo Rulesへの導線を検査した。今回のrunでは新しい試作routeを公開registryやsitemapへ追加していない。

## 2. 操作・プライバシー検証

| 項目 | 観察・テスト範囲 | 判定と限界 |
| --- | --- | --- |
| 初期／未回答 | 工程未選択、6項目未確認時に確認事項を表示 | 機械テストPASS |
| 全確認済み | 6項目すべて`confirmed`。自己申告と安全非保証の出力を検査 | 機械テストPASS |
| 全対象外 | 6項目すべて`not-applicable`。対象外の理由を責任者と確認する表示を検査 | 機械テストPASS |
| 不正値・想定外型 | `deriveReview`のunit testsでstage/構造/項目追加/値改ざんをfail-closed確認 | 限定した単体テストPASS。攻撃全類型の網羅ではない |
| 表示・リセット | 固定の架空例、印刷ボタン、cancel後の選択維持、連続reset、reload後の初期値、back後のURLを検査 | ChromiumテストPASS |
| Network | 選択値4種を変更した際にrequest URL、headers、postDataを収集。選択値の出現なし | **限定サンプルPASS**。通常のHTML・JS・Analytics pageview通信をゼロと主張しない |
| URL/Storage | location、history.state、query/hash、localStorage、sessionStorage、IndexedDBデータベース名を確認 | **限定サンプルPASS**。IndexedDB既存DB内部の全レコードやCookieを網羅していない |
| Analytics/feedback | 新しいanswer event、free-text、feedback prefillを実装していないことをソース点検 | ソース範囲PASS。実本番Analytics送信の全項目検証ではない |
| 390px | Chromium viewport 390×844でラベル・select・結果と横はみ出しを確認 | エミュレータ相当のChromium PASS。Android実機ではない |
| 200% | 1280×900のChromiumでroot CSS zoomを200%に設定し、focusと主要操作、横はみ出しを検証 | **CSS zoom模擬PASS**。ブラウザのネイティブ拡大やOSの文字サイズ設定の検証ではない |
| キーボード/通知 | selectのfocus/操作、`aria-live=polite`、labelに対するrole name照合 | 自動検査PASS。スクリーンリーダーの実聴取は未実施 |
| 印刷 | print mediaの非表示・概要表示、Chromium `page.pdf()`のPDFヘッダー検査 | 自動検査PASS。人による印刷プレビュー評価ではない |

通常のAnalytics script配信やページ閲覧通信と、**回答の選択値が通信に含まれること**を区別した。今回の合成値4種について回答を含むrequestは検出されなかったが、すべての通信先・実環境に関する全面的保証ではない。

## 3. 失敗と再試験

- 初回run [37760983338](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37760983338) のpreview jobはChromium 12 PASS / 1 FAIL / 1 skip。失敗箇所はprivacy testの`page.goBack()`後の遷移先を必ず試作routeだと決め打ちしたexpectで、実測値は`/`。**漏えい・医療助言が検出された失敗ではない**。
- 修正：`54b84cd85981c785110b1a9459a5f8852fddd64f`。戻り先がrootでもpreviewでもURLへの回答漏えいがないことを調べ、試作へ直接再訪問して入力が初期化されることを確認する方式へ変更。
- 再試験run [37761326870](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37761326870)：preview 13 PASS / 1 skip、disabled 8 PASS / 6 skip、flag誤設定時404、既存route smokeいずれもSUCCESS。

## 4. Source / branch / 公開状態

- main上のAのsource register、BのIssue draft、Dのreview資料、Eの既存公開判定を閲覧してCの境界を照合した。**段落別source-to-claimの全面レビューはCの実施結果ではない**。現在のBのサービス適用範囲、権限境界は未確定のまま保持する。
- PR #451はdraftであり公開registry、ナビ、sitemapに新規Issue/toolを追加しない。一般公開可能なflag-enabled Vercel previewは使わず、GitHub Actionsのlocalhostで検証。
- Vercel `kaigo-ops` のproduction metadataを再照合：deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`、`READY`、runtime SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app`。このruntime SHAは新しい試作のコードを含まない。現runにおける公開HTTP直接応答再測定は**NOT_RUN**（以前のE記録では試作route 404）。
- Vercel対象projectのbranch-filtered deployment一覧ではC branchに対応するdeployment 0件を観測。ただし他の外部配信先全般の不存在までは証明しない。
- 既存Analyticsは`RECEIVE_CONFIRMED`、Search Consoleは`UNKNOWN`という最新canonicalの区別を継承。今回新custom eventは作らず、事故防止効果や需要を推定しない。

## 5. 未完了と次担当

1. **D**：A/B/Cの確定版に対するR01〜R16、P01〜P07、U01〜U06の独立red-teamと人手操作。今回Cの機械テスト成功をDの独立安全レビュー完了としない。
2. **実在の専門職**：EX01（医療・服薬安全）、EX02（事故防止・リスク管理）＝`EXPERT_REVIEW_NOT_DONE`。対象SHAに紐づく署名・指摘・再評価の証拠なし。
3. **内容責任者/E**：HU01＝`HUMAN_APPROVAL_NOT_DONE`。公開対象サービス、文言・主張の根拠と人のレビューを確認して公開可否を再判定する。
4. **C/D**：実Android Chrome、スクリーンリーダー実聴取、ネイティブ200%拡大、利用者テスト、アクセス認証付きレビューURLの検証は`NOT_RUN`。
5. **公開ゲート**：`PREVIEW_ONLY / NOT_PUBLIC`を維持。production merge/deploy、feature flag有効化、新Issue/新action toolの公開は行わない。

**Worker C結論**：指定CI内の非公開・合成データに限定した実行証拠は再現可能な形で得られた。公開適合性・医学的安全性・現場適用性は別ゲート未完なので、総合判定は`PARTIAL_WITH_GAPS`。

## 6. 2026-10-08 Content alignment — C同一版での再実行（前回の記録を保持）

- 実装と仕様を再検証した対象PR head: `6e5d150f71d6df87cac2b9bac3ba10e0ddbe7f0f`（draft #451、未マージ）。本節以外の後続ドキュメントコミットと区別する。
- 照合した `main`: `233f11f60bd53cee4684fd66eb5c0490b2fee926`（2026-10-08 JST）。
- A source-to-content trace blob: `2cb32c3b4de093d51d410d23c04511e020a43571`。**旧B草案blob `4418af5405044be3a74268c7fa9ff85e6759126f` のcrosswalkであるため最新版へのA独立再追跡は未完。**
- 現行B Issue draft: `083ffd0a17419e1533e65205e9230d725f3232ab`（B-00〜B-13）、service applicability: `8138d89832ddd4b706ff1da4751ffd2626e251bb`。今回はB-04〜06の語彙とB-00/B-09/B-12〜13の安全・適用留保をCの表示・結果・印刷に反映した。実施権限やサービス横断の妥当性は依然 `NOT_ESTABLISHED`。
- 厚労省2025年11月ガイドラインVol.1436の冊子p38〜39（PDF 0起算p40〜41）とp46（PDF p48）、2024年11月通知Vol.1332のPDF 0起算p2を2026-10-08 JSTに再閲覧。ガイドラインは施設中心の推奨と特養一事例、p46は通所・訪問の一般的な情報共有・連携上の留意点であり、全サービスの服薬工程・職種権限を確定しない。事故報告通知を個別報告判断の自動化根拠にしない。
- Cコードblob（再取得可能）：`medication-safety-review.ts`=`8853e5c5dae84293e5c283bc779fd08a3c2c79db`、`worksheet.tsx`=`bc54ab9d8c13a1713f9e68d41b433f2c3130dc95`、`page.tsx`=`cfa6f30633c5c8536b570c4c82b2794cd4353320`。unit test blob=`b1329ac595c35ef0395521ae1e4bf1f5ef56cc54`、Chromium test blob=`420bdb726349a400cf33cd4c1673b832e3e08c79`。
- GitHub Actions: [run 37783117273](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37783117273)、`Validate medication safety preview`、`SUCCESS`。GitHub-hosted Ubuntu、Node22、Chromium headless、localhost 127.0.0.1、CI限定の合成選択値、secret不使用。匿名アクセス可能なVercel Previewは用いなかった。

| 検証条件 | 実行した内容 | 実測と解釈 |
| --- | --- | --- |
| flag `enabled`（localhost限定） | `npm ci --no-audit --no-fund`, `npm test`, `npm run build`, `npm run test:browser`, `npm run verify:routes` | 全step成功。unit 28 PASS / 0 FAIL、Chromium **13 PASS / 1条件付きSKIP**。既存5 Issue・5 action toolのrouteとリンクを検証。 |
| flag未設定 | 同じ5コマンド、flagを無効としたChromium試験と既存routeのsmoke | 全step成功。unit 28 PASS / 0 FAIL、Chromium **8 PASS / 6条件付きSKIP**。試作routeの404を検証。 |
| flag不正値 `not-enabled` | disabled jobのローカルHTTP smoke | preview route **404**。設定値を誤っても表示しない。 |
| 語彙と結果 | 未選択、全確認申告、全担当範囲外申告、混在、架空例、不正構造・不正値をunit/Chromiumで検証 | **限定した自動テストPASS**。『確認済み』『対象外』を無条件の安全・義務免除として表示しない。 |
| 情報境界 | 合成状態4種のrequest URL/headers/body、ブラウザURL/history、local/session storage、IndexedDB名、Cookie、印刷media/PDF生成をChromiumで検証 | **限定した合成データ・Chromiumの検証PASS**。回答値の漏出を検出せず。Analytics通常pageview通信そのものがないとは主張しない。全ブラウザ・全レコード・全外部通信の不存在を保証しない。 |
| 画面・操作 | 390px、CSS zoom 200%模擬、select label/focus/aria-live、reset cancel/confirm、reload、戻る・再訪問、print | **Chromium自動テストPASS（実機試験ではない）**。 |
| 公開registry / production | ソース構造とローカル既存route smoke | 既存5 Issue/5 toolは変更せず。productionの本Wave再デプロイなし。production HTTP独立再測定は**CではNOT_RUN**。 |

### Cで実行していないこと、次に必要なこと

- **D独立R01〜R16 / P01〜P07 / U01〜U06**：本Cの既存CI runをDの独立red-team検証とは扱わない。`NOT_RUN_BY_C`。
- **Android Chrome実機、ネイティブ200%拡大、スクリーンリーダー実聴取、利用者による印刷プレビュー**：`NOT_RUN`。CIのviewport/CSS模擬と区別。
- **EX01（薬剤師・看護職等）、EX02（事故防止・リスク管理実務責任者）**：`EXPERT_REVIEW_NOT_DONE`。**HU01（公開責任者）**：`HUMAN_APPROVAL_NOT_DONE`。実在レビュー・署名・GOは作成していない。
- **Aの最新B本文への独立trace**：旧BへのA資料しかないため `REVIEW_REQUIRED`。CはBの現行版を直接読んで文言対応を行ったが、source claim全件のPASSを代用しない。
- **Vercel preview access**：flag enabledのアクセス制御された外部URLは試していない。`PREVIEW_ACCESS_NOT_ESTABLISHED`。flag=enabledの匿名Vercel preview作成は禁止を維持。
- **公開判断**：`PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`。PR #451をdraft・未マージで維持し、公開registry、production環境変数、deploymentは変更しない。

**Dへの固定版handoff**：B blob `083ffd0a17419e1533e65205e9230d725f3232ab`、service blob `8138d89832ddd4b706ff1da4751ffd2626e251bb`、A trace blob `2cb32c3b4de093d51d410d23c04511e020a43571`（旧B対応であることを明示）、C tested head `6e5d150f71d6df87cac2b9bac3ba10e0ddbe7f0f`。再審査時はこの版とのdiffを照合し、変わったケースだけでなく安全・プライバシー・印刷の影響範囲を再試験する。

## 7. 2026-10-09 Worker C — 版固定とB第9節への追従（検証待ちの事実を区別）

**判定（この記録時点）: PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC。** この節は前節までの2026-10-08実測を上書きしない。最終公開candidateとしてのB→A→C→D同一版は未成立である。

### 7.1 対象と正本の固定

| 項目 | 2026-10-09 JSTに取得した識別子と意味 |
| --- | --- |
| baseline main | `1360bd78d971266c5e635c7a3416d5b4629e1c0e`（試作のproduction SHAではない） |
| B #459 本文 | `e0cc354e2b78a28912c80c0611ccf3c165d00b25` — B-00〜13及び第9節の固定文言。Bが並行更新中のため後続変更を必ず再確認 |
| B #459 サービス適用表 | `e3889c26c5b46d4644b29d94c657e628c96206d3` — 施設・居住・通所・訪問・短期入所・居宅支援等。実際の担当権限は未確立 |
| A #458 trace | `0b042421f49ae5213f80b71e4cf04c502d32c1f9`。**旧B `083ffd0a17419e1533e65205e9230d725f3232ab`対象**であり上記B最新版への独立traceは未完。最新A確定待ち |
| C実装／テストcommit | `9814dc541880c16cf311f0c700dc458c33ee2a83`（既存draft #451内、未マージ） |
| C code blob | page `cfa6f30633c5c8536b570c4c82b2794cd4353320` / worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c` / model `9580e9202209f5e3fdf3b544b628d68885062295` |
| C tests blob | unit `4615d25a3f2a0d809f0997840acec5a8ce2ebe83` / Chromium `f4187363f03abda0fc02ed30e950957afb9f575f` |
| 公式原典 | 厚労省 Vol.1436（2025-11-07周知）冊子p38〜39=PDF 0起算p40〜41、冊子p46=PDF p48を2026-10-09 JST確認。Vol.1332（2024-11-29）PDF p2を同日確認。原典は施設向けの推奨・特養一事例と通所/訪問の情報共有・連携上の注意であり、Cの5値を定義した公的尺度ではない |

B第9.4節のソース差分を確認し、結果と印刷に**同一の共通警告文**を `WORKFLOW_BOUNDARY` として適用。印刷物へ事故時の必要な緊急対応・法令自治体手続・本人の意思と尊厳への留保を追記。変更情報の共有項目について、処方指示の正しさ・真正性・有効性を本シートで判定しないことを結果近くに追記した。事故率、服薬判断、再投与、報告期限、職種権限の自動判定は追加していない。全5状態の内部valueと既存公開registryは維持した。

B確定5ラベルとmodel `CHECK_STATES` はソース照合上は一致する。全確認／全担当外／未選択／混合／架空例／異常値については、unit・Chromiumの既存テストと追加の結果・印刷警告回帰テストを使用する。文言の逐語一致は**B第9節の共通警告部分に限定**。他の警告文は意味の同等性と差異をBに明示しており、専門職による安全性承認ではない。

### 7.2 CI（同一コードcommitのflag別検証）

| 環境 | 新たな実行証拠 | 状態 |
| --- | --- | --- |
| flag enabled（GitHub-hosted Ubuntu / Node22 / Chromium / localhostのみ） | [GitHub Actions 37844003519](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844003519) | **PENDING**（作成後の時点。成功・失敗未確定） |
| flag未設定 / 不正値 `not-enabled` | 同上runのdisabled job（4種の基本コマンドとローカル404・既存route確認） | **PENDING** |
| 関連の公開route等のCI | [Validate ops site 37844003647](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844003647)、[Validate build 37844003649](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844003649) | **PENDING** |
| 回答を変えた時のURL/header/body、history/storage/Cookie/IndexedDB、390px、CSS zoom 200%、PDF、reset、ARIA | C Playwright内の合成選択値を対象に自動検証を設定 | **今回SHAのrun結果待ち**。既存の2026-10-08成功結果は最新版のPASSではない |
| 実Android／ネイティブ200%／スクリーンリーダー／人手の印刷画面 | 実行できる端末・人手審査を確保していない | **NOT_RUN** |
| D独立29ケース、EX01/EX02/HU01 | Cの担当外。実査や承認をこの節で行っていない | **NOT_RUN_BY_C / EXPERT_REVIEW_NOT_DONE / HUMAN_APPROVAL_NOT_DONE** |

### 7.3 非公開と残る依存関係

- `#451`はopen / draft / unmerged。公開Issue/ツールの既存5件ずつを変更せず、旗を公開・本番で有効化しない。flag・noindex・URL非掲載は認証ではない。
- Vercel `kaigo-ops` projectの2026-10-09時点latest productionは `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` READY、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app`。C branchを指定したVercel deployment一覧は0件。公開HTTP実測は今回**NOT_RUN / ACCESSIBLE_RESPONSE_NOT_ESTABLISHED**（Web取得失敗）で、previous Waveのpreview 404を今回の直接HTTP PASSに読み替えない。
- Preview access restrictionを実際のflag-enabled URLで実証していないので `PREVIEW_ACCESS_NOT_ESTABLISHED`。匿名で到達可能なVercel Previewは作らない。
- B最終2 blobが再更新された場合は本表を再固定する。**Aが同じB2 blobでsource-to-claimを検証するまで、このC版は最終candidateではない。** Dは同じC code SHAでR01〜R16/P01〜P07/U01〜U06を独立再実行しなければならない。Eのみが公開判定する。

## 8. 2026-10-09 Worker C 同一版CI完了証拠とA最終追跡の受領

この節は第7節の作業途中PENDINGを**最新の確定実行結果**で更新する。第6節以前の旧コードへの成功を流用しない。**C検証結果: 機械試験 PASS_LIMITED / Worker C総合 PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC。**

### 8.1 A/B/Cの新しい読み戻し識別子

- **B #459（head `364519815a41143560b068cfa459e7a04962f18f`）:** 2026-10-09版本文 `e0cc354e2b78a28912c80c0611ccf3c165d00b25`、service `e3889c26c5b46d4644b29d94c657e628c96206d3`。上記第7節で扱ったBの2 blobと同一。
- **A #458（head `37fc213301e93442f71efc4509af5cfa49567c88`）:** 追跡表 `271560deb7ea848690e12d97fd23661583511198`。A第8節は**上記Bの正確な2 blob**を参照しB-00〜13、MS-01〜20、一次資料edition/頁、各サービス群の未確立とCの固定コードblobを照合した。Aの限定判定は `PARTIAL_WITH_GAPS`、MS-07/08/13/15・17〜20等はレビュー・未確立。**旧A blob `0b0424...`は履歴扱い**に訂正する。
- **C試験対象:** code commit `9814dc541880c16cf311f0c700dc458c33ee2a83`。CI checkoutはこのコードを全て含むdocs-only最新head `7ec2fe8c644d0526af1650e857a7da397488a0ad`。page blob `cfa6f30633c5c8536b570c4c82b2794cd4353320`、model `9580e9202209f5e3fdf3b544b628d68885062295`、worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c`。unit blob `4615d25a3f2a0d809f0997840acec5a8ce2ebe83`、browser blob `f4187363f03abda0fc02ed30e950957afb9f575f`。
- 原典の限定: G25＝厚労省Vol.1436（2025-11-07）、冊子38〜39（PDF0:40〜41）、46（PDF0:48）、10/27/26等。N24＝Vol.1332（2024-11-29）PDF0:1〜3。**施設中心の推奨・一事例・通所訪問一般連携・事故報告通知は実施権限や全サービス必須工程の根拠ではない。** 出典・主張単位の審査結果はA trace第8節を正本とする。

### 8.2 flag別CI実測 — C本人の自動テストに限定

**GitHub Actions [run 37844184628](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844184628)、head `7ec2fe8c644d0526af1650e857a7da397488a0ad`、overall `SUCCESS`。** 権限 `contents: read`、GitHub-hosted Ubuntu / Node22、Chromium、localhost `127.0.0.1`。シークレット・患者情報・実症例を渡さず、列挙型の合成選択値のみ。

| 条件／job | コマンドと実行範囲 | 実測結果 |
| --- | --- | --- |
| flag `enabled`／preview job | `npm ci --no-audit --no-fund`, `npm test`, `npm run build`, `npm run test:browser`, `npm run verify:routes`（localhost） | **job SUCCESS**。単体 `29 pass / 0 fail / 0 skip`、Chromium `13 pass / 1 conditional skip`。既存5 Issue/5 action toolルートsmoke成功 |
| flag未設定／disabled job | 同じnpm install/test/build/Chromiumと既存公開ルート確認 | **job SUCCESS**。単体 `29 pass / 0 fail / 0 skip`、Chromium `8 pass / 6 conditional skip`。試作route 404 |
| 不正flag `not-enabled`／disabled job | local HTTP smoke + `verify:routes` | **PASS**。試作route HTTP 404、既存ルート確認成功 |
| 公開site regression | [run 37844184648](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844184648) | **SUCCESS**。既存5 action toolのChromium実行を含む |
| Publication readiness integration | [run 37844184757](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844184757) | **SUCCESS**。これは公開承認を意味しない |
| Generic validate build | [run 37844184705](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844184705) | 本追補作成時 **IN_PROGRESS / RESULT_NOT_ESTABLISHED**。後で結論を独立確認する |

preview/disabled各jobの実行ログで単体件数とChromiumのPASS/SKIP数を確認した。前run `37844003519` は同期commit更新でキャンセルされたため成功証拠には含めない。今回のC最新テストはflag enabledでの画面・結果・印刷・PDF生成・reset・390px・CSS zoom模擬、合成値のURL/header/body/history/storage/cookie/IndexedDBの漏えい検査を含む。**実測対象の合成値に漏えいを検出しなかった**という限定結果であり、全通信・全環境の不存在を立証しない。通常Analytics pageviewの通信は無送信保証とは別。

### 8.3 D/Eおよび人間ゲートへの確定handoff

- **D**：上記Cのコード commitと3 code blob、A最新trace `271560deb7ea848690e12d97fd23661583511198`、Bの2 blobを対象に**独立した**R01〜16/P01〜07/U01〜06全29ケースを再実施して固定。C CI成功をD独立安全PASSへ転記しない。D変更やB/A/C意味変更があれば該当case・privacy・印刷を再実施。
- **EX01/EX02**：実在の医療職・事故防止実務責任者のレビューは **EXPERT_REVIEW_NOT_DONE**。**HU01**：対象サービス、同一版、訂正責任者、公開範囲への明示GOは **HUMAN_APPROVAL_NOT_DONE**。外部のレビュー依頼は実施しない。
- **NOT_RUN**：実Android Chrome、ブラウザネイティブ200%ズーム、スクリーンリーダー実聴取、現場利用者の印刷画面の人手評価。CSS zoom 200%模擬と区別する。
- **公開隔離**：PR #451 open/draft/unmerged、registry・navigation・sitemap・production flagに変更なし。Vercel project `kaigo-ops` latest production `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` READY、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app`（このC試作を含まない）。C branch filterでVercel deployment 0件。今回のproduction直接HTTPとflag有効external preview accessの実測は **NOT_RUN / PREVIEW_ACCESS_NOT_ESTABLISHED**。flag/noindexが認証の代用ではない。
- **次担当：** Dの独立監査とexpert pack更新 → Eが4版と実在EX/HU証拠を突合し公開HOLD/GOを決定。安全性・医療的妥当性・実務適用性は本CのCIからは保証できない。

**Worker Cの閉鎖判断：PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC。** C仕様の非公開テストは成功したが、D独立29ケース・現場端末・実在の専門職・人間公開責任者の確認が未完了。未承認のPR merge、本番deployment、匿名preview有効化は行わない。
