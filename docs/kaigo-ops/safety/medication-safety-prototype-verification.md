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
