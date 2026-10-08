# 2026-10-08 誤薬・与薬漏れ業務点検：公開判定（Worker E）

- 判定日時: **2026-10-08 JST**（A〜D提出後、GitHub／厚生労働省原典／Vercel APIの再確認）
- Review main: `39828b1039db9009595e60add180decc45a55225`（A #449・B #448・D #450の安全な資料／回帰ゲートを統合したcommit）
- C preview: PR [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451), head `dd7ccdc535aa34acd76d8d54943a72b856345832`（**draft・未マージ**）
- A [#449](https://github.com/Josh-Temple/kaigo-rules/pull/449) → squash `6d44d090ffd8c15b16a2b5804aaaaf8735045c43`
- B [#448](https://github.com/Josh-Temple/kaigo-rules/pull/448) → squash `574c259374484248fce067448d9cf704d0faddf3`
- D [#450](https://github.com/Josh-Temple/kaigo-rules/pull/450) → squash `39828b1039db9009595e60add180decc45a55225`
- Final integration PR: この記録を導入するWorker E PR（番号と最終merge SHAはPR成立後の記録を参照）
- **Evidence / integration: PARTIAL_WITH_GAPS**
- **Safety: SAFETY_PARTIAL_WITH_GAPS**
- **公開状態: PREVIEW_ONLY / NOT_PUBLIC**。本番公開を認めない。技術試作はPR C内に保持し、一般公開またはproduction flag有効化を認めない。

## 1. 判定の対象と証拠の強さ

| 対象 | 実際に確認したもの | 判定・留保 |
| --- | --- | --- |
| A source / risk | 20 claim（`MS-01〜20`）と12 riskのPRソース。厚労省Vol.1436の冊子p38〜39（PDF 0起算P40〜41）を独立に画像で閲覧 | **PARTIAL_WITH_GAPS**。限定した施設系の記述は裏付けあり。全20 claimを独立再照合したとはしない。 |
| B draft / applicability | Issue草案を直接読取。source-backedとdesign proposal、施設・通所・訪問・居住系等の適用境界を確認 | **PARTIAL_WITH_GAPS**。施設外の個別手順・職種権限は未確立。Issue採番は行わない。 |
| C prototype / privacy | PR #451のserver-side flag、選択式UI、純粋関数、不正値時の固定表示、source／browser testをレビュー。PR CのCI `preview` はsuccess | **PARTIAL_WITH_GAPS**。コード検査とCI実行結果を、独立したNetwork/Storage/200%実査や専門職検証と同一視しない。 |
| D adversarial / reviewer | チェックリスト、16ケースの結果台帳、preview非公開ガードのソース。PR DのCIはsuccess | **SAFETY_PARTIAL_WITH_GAPS**。16ケースは独立実行としてはすべて `NOT_RUN`。EX01 / EX02は `EXPERT_REVIEW_NOT_DONE`、HU01は `HUMAN_APPROVAL_NOT_DONE`。 |
| CI | PR #448: build/publication-readiness success、#449同、#450: 2 build + publication-readiness success、#451: 2 build + preview + publication-readiness success（GitHub check-runs） | PRごとの限定PASS。Cのプレビューをproduction上で実行した証拠ではない。結合後main CIは別途追跡。 |
| Production | Vercel `kaigo-ops` / project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`、deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` がREADY / production。SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/` が同deploymentを指す。Vercel fetchでhome + 5 Issue + 5 toolの**11ルートが各HTTP 200**、`/sitemap.xml` 200、`/tools/medication-safety-preview` **404** | 公開中は既存5 Issue/5 tool。Vercel本番runtimeは最新mainの**資料・テスト変更より前**のreleaseであり、新規安全機能を含まない。HTTP/HTML確認は実ブラウザの390px、keyboard、Analytics送信検査の代替ではない。 |
| Observation | canonicalの`measurement.md` / `usage-observation.md` / `CURRENT.md` | Analytics `RECEIVE_CONFIRMED`（2026-10-07初確認）。前Wave時点の集計：7 visitors / 8 pageviews、homeのみ。今回の独立した再計測値ではない。Search Console `UNKNOWN`。2〜4週間レビュー窓は2026-10-21前後〜11-04前後。 |

## 2. B草案からA source registerへの照合

**source claim IDが異なるため、以下を初期crosswalkとする。** 一致は「施設を中心とした文書内の限定された論点」の一致であって、全サービスへの適用許可・医学的適正・法的義務の確認を意味しない。

| B claim | A claim | E判断 |
| --- | --- | --- |
| `MHLW-01`：資料の対象範囲 | `MS-01` | **PASS（資料対象の説明のみ）**。施設が中心。居宅・居住系への適用は項目別に確認。 |
| `MHLW-02`：誤薬等、原因、工程差、作業環境 | `MS-02〜07` | **PARTIAL_WITH_GAPS**。`MS-07`の服薬後確認方法は専門職レビュー前。手順・人数を義務としない。 |
| `MHLW-03`：特養の実践事例 | `MS-09` | **PASS（単一事例の論点抽出のみ）**。因果効果や施設外への一般化を行わない。 |
| `MHLW-04`：原因分析と再評価 | `MS-10〜11` | **PASS（組織での検討という推奨）**。事故報告義務の自動判定を伴わない。 |
| `MHLW-05`：通所・訪問の特徴 | `MS-15` | **PARTIAL_WITH_GAPS**。服薬工程への転用は`NOT_ESTABLISHED`。 |
| `MHLW-06`：事故時の正式な手順 | `MS-12`、報告通知の補助資料 `MS-13〜14` | **PARTIAL_WITH_GAPS**。自治体別の個別報告要否・期限は確定しない。 |
| `MHLW-07`：本人の尊厳・意思 | `MS-16` | **PASS（原則のみ）**。服薬拒否等への個別判断はしない。 |
| 公開禁止の断定 | `MS-17〜20` | **NOT_ESTABLISHED / DO_NOT_PUBLISH**。再投与判断、安全効果、全サービス一律義務、旧通知優先を拒否。 |

厚労省一次資料：介護保険最新情報Vol.1436／「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」（2025-11-07周知） https://www.mhlw.go.jp/content/001591418.pdf。Aは別途Vol.1332（2024-11-29） https://www.mhlw.go.jp/content/001574219.pdf を記録。両者の版、実務推奨、通知、個別自治体の運用を混同しない。

## 3. 安全・プライバシー・公開遮断

- Cの画面は**選択式のみ**であり、氏名、処方、薬剤名、事故本文の入力欄を設けない。提示されたソースには回答の明示的なfetch、保存、URL送信処理はない。ただし実ブラウザの通信・Storage完全検証の`PASS`ではない。
- `deriveReview`は不正な入力構造を固定文言で拒否し、全て「確認できる」でも安全保証しない。これは単体／コード上の検査であり、事故を減らす実証ではない。
- Cの環境変数flagは**認証ではない**。PR previewがアクセス制限されているか未確認。第三者が到達可能な環境でflagを有効にしない。Cはdraft PRに残し、productionへ取り込まない。
- DのR01〜R16、privacy P01〜P07、UI U01〜U06は、A〜Cの**確定版**に対する独立の再検証が必要。特に200%拡大、keyboard、印刷、reset、Network payload、履歴・Storageを確認する。
- 医療職と事故防止・リスク管理実務責任者の**版に紐付く**レビューID／判定がない。内容責任者の公開承認もない。未実施をPASSとしない。
- 事故や疑義が発生した場合、サイトは医療判断や再投与を案内しない。現場の正式な事故時手順、管理者、関係専門職、必要な緊急対応、自治体・法令の正式ルールへ戻す。
- 誤薬関連ページは公開Issue registry / navigation / sitemapへ登録しない。既存ロードマップのIssue 6は「収支・コスト構造」のまま維持。

## 4. 厳格なrelease decisionと次回条件

**今回の結論：`PREVIEW_ONLY`。新たな事故防止Issue/toolのproduction deploymentは実施しない。** なお`RESEARCH_ONLY`より進められる根拠は、試作と機械テストがPR Cに存在することであり、一般公開可能という意味ではない。

| 必須の次の行為 | 担当 | 証拠と完了基準 |
| --- | --- | --- |
| A/B/Cのsource-to-content対応を、`MS-07`・`MS-15`・自治体報告・職種権限などの未確定点を中心に改訂 | source owner + Issue owner | 修正claim IDと該当原典、対象サービス、採否を記録。未確定箇所は非表示・`NOT_ESTABLISHED`。 |
| Cをアクセス制御下のレビュー環境で動作させ、Dの16例・privacy・mobile・200%・keyboard・印刷を独立再実施 | tool owner + safety reviewer | 対象C commit／local preview identity、各caseの実測PASS/FAIL/NOT_RUN、network・保存・公開URLの検査結果。 |
| 医療職（EX01）と事故防止責任者（EX02）のレビュー | 外部の適切な専門職・実務責任者 | 対象SHA、非識別review ID、レビュー日、指摘への修正、結果`DONE/PASS`。 |
| サービス適用範囲、公開文章と正式連絡先を審査し、公開を承認 | 内容責任者 / Worker E | `HU01`の承認ID、対象SHA、明示的なGO/HOLD。 |
| 上記全PASSの場合のみ公開統合、CI・route・390px・production exact-SHA/READY/aliasの検証 | Worker E | 新旧route＋5 Issue/5 tools、Kaigo Rules、feedback、sitemap、Analytics境界の実行証拠。未達時は公開せず保持。 |
| 既存日次deploy検証とSearch Consoleの未確認は独立に追跡 | production運用担当 | 日次GitHub Actionsでの`VERCEL_TOKEN`配置と実運用完走、Search Console認証とURL Inspection。推測で完了にしない。 |

## 5. 既存運用に対する判断

- docs・テストguardのintegrationのみ。**新しい公開Issue／toolは0件**、新規analytics eventは0件。
- 既存production 11ルートはVercel fetchによるHTTP 200を再確認。C preview routeは404。この確認はBrowser full regressionを実行したという意味ではない。
- Vercel deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` / runtime SHA `e49e770...` は引き続き既存公開コードのrelease。最新main（資料・テスト）のSHAを誤ってproduction runtime SHAと呼ばない。
- Analytics定義・first observed date・feedback導線・2〜4週間review windowは変更しない。閲覧数から事故減少や安全性は推定しない。
- 本Waveの終了判定は **`PARTIAL_WITH_GAPS` / `PREVIEW_ONLY`**。専門職レビューと独立したadversarial testの未完は次Waveに持ち越す。新Issue公開の条件とWave成果物の整備を混同しない。
