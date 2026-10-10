# Kaigo Ops — 2026-10-10 E統合判定：公的出典ガイド HTTP 到達と claim-aligned release

**指示書**: Library `/Kaigo Ops/Work Instructions/2026-10-10_public_source_guide_http_closure_and_claim_aligned_release_wave_instructions.md`。本書は今回の実測を前WaveのE判定から更新する。**本番HTTPの確認と、新しい記事の公開許可・実ブラウザ検証は別**。

## 1. 正本の取得と統合した成果

- 判定開始時main `1c7771add72d91b58673d758dcb13ec65a14998a`、A #470／D #471文書統合後main `4d644763eb1c1da6bb822117017630fec1f9c692`。ここでいうmainは**文書Git SHA**でありVercel runtimeではない。判定文書を最終mergeする際はhead／merge SHAをreadbackする。
- **A [#470](https://github.com/Josh-Temple/kaigo-rules/pull/470)**: head `b98ff0e527d6bd6b18ea48e461fafc9660a079b9`、出典監査既存台帳1ファイルを追補、GitHub Actions2件success、**squash merge `2c92223f97173091e94b2dbd8dafd3038be8f0ef`**。MED-A01〜08の維持／文面修正、FALL/ASP/INGとB段落のcrosswalk、第2テーマを今回採用しない方針。判定 `PASS_LIMITED`（原典・主張のみ）。
- **B [#466](https://github.com/Josh-Temple/kaigo-rules/pull/466)**: latest head `5df748a60b0d3699c751643b47fe77e90aa9a8d2`、draft/open/unmerged。既存服薬記事の限定修正案と転倒・転落のB文章をA採否へ結び直した**編集確定稿**。CI文書系2件successだが、**Cの公開コードへ未実装**である。
- **C [#465](https://github.com/Josh-Temple/kaigo-rules/pull/465)**: latest head `77eb4b391ac722adc1a34024e6c7a33b35179949`、open/unmerged。変更3ファイル（`ops-site/app/globals.css`、既存服薬ガイドpage、Playwright spec）。目次、印刷、段落から公的原文への直接リンクを追加。最新headに対するGitHub Actions `37957413246`（ops）、`37957413269`（publication readiness）、`37957413305`（build）がsuccess。**A/Bによる服薬本文のP1修正・転倒記事本体はCのheadに含まれない**。
- **D [#471](https://github.com/Josh-Temple/kaigo-rules/pull/471)**: head `c65e366acb5e61bd960d8efe7750470140072b21`、独立監査既存台帳1ファイルを追補、文書系Actions2件success、**squash merge `4d644763eb1c1da6bb822117017630fec1f9c692`**。判定 `PARTIAL_WITH_GAPS`。Dが独立確認したCは**head `8e18f9bd54662d246081f4620728ba8c8ff38665`**。Cはその後、本文からの直接原文リンクとテストを3コミットで変更し、最新headは`77eb4b...`。**Dの同一版承認は最新版Cに及ばない**。Dが参照したBも旧head `e58adc...` であり、新しいB/C最終表示組合せの安全審査は未完了。
- **旧試作 [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451)**: draft/open/unmerged。公開UI・設定・flagをEでは変更しない。

## 2. 既存productionの独立5層検証

- Vercel専用project `kaigo-ops` / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`。本番deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` は `production / READY`、repository `Josh-Temple/kaigo-rules`、**runtime SHA `ffd70abb5723e950a0a1036795f28da31614a1f3`**。
- Vercel deploymentのalias配列と`ops-site-pi.vercel.app`の直接deployment照会で、aliasが同じdeployment IDを指すことを再取得。**mainの最新文書SHAとは区別**。
- 当実行環境のPython HTTPS試行はDNS失敗、Web直接取得も不可。**これはHTTP 404／5xxではない**。そこで、deploymentを触らず **[#472](https://github.com/Josh-Temple/kaigo-rules/pull/472)** の**read-only GitHub Actions外部runner**を使用。
- [run **37993334787**](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787)（job **114032888418**、検査コードhead `d566641319e89e2285f5fc6e309014493ad3de4c`）は `success`。ログに **15/15 PASS**を記録：home 1 + 5 Issue + 5 tool の全11がHTTP 200、既存ガイド `/guides/medication-incident-sources` がHTML HTTP 200、非公開試作route `/tools/medication-safety-preview` が期待404、`/robots.txt` と `/sitemap.xml` がHTTP 200。site shell識別を行い、ガイドcanonical/OG／出典アンカー／公式hostリンクの機械チェックも成功。
- 同run artifact: `kaigo-ops-public-http-probe-37993334787`（artifact ID **11646440673**）。GitHub Actionsの外部Ubuntu runnerのGET/HTML抽出という証拠であり、**Androidブラウザ、実際のリンク先文書のHTTP閲覧、実ユーザーによる操作の証明ではない**。deployment個別URLとのHTTP一致やキャッシュ差の確認も未実施。
- **既存productionの本番HTTP判定：`PRODUCTION_HTTP_CONFIRMED`（検査した15 URLのみ）**。DOMとしてはサーバー応答のHTML構造・メタデータを限定抽出、ブラウザJS実行・アクセシビリティツリー・native zoom・スクリーンリーダーは `NOT_RUN`。
- **`deploy-state/kaigo-ops` tip `e49e770a970e541d2ad95204ad277eca89a485d3`を据置き。** 理由：現行の正式contractはdeploy hook要求時刻以後の**新規**READY deploymentとそのexpected Git SHA・alias・11 routeの同一verification runを要求。今回の外部read-only GET成功は旧deploymentについての補完検査であり、正式post-deploy run／marker前進の代わりにはしない。

## 3. 現行服薬記事：変更／保留

- **本番の現行記事は今回未修正**。C #465とB #466を本番へ統合・デプロイしていない。既存の初動注意、研究報告の適用対象、医療職相談と行政報告の区別、非監修表示は原典と限定的に整合するというA/D評価にとどまる。
- 重要なP1修正未反映：刑法211条の見出し「重大な結果」を条文の「人を死傷させた」と誤読なく区別し、「誤薬だけで刑罰が自動成立しない」と説明する。2024事故報告通知Vol.1332の本文の報告対象と**様式が想定するサービスの範囲**を分け、第1報の「5日」を全国一律の法定期限と誤表現しない。2017年住まい研究の推奨を全国共通義務に一般化しない。公的原文リンクを段落から直接到達可能にする。
- Aが確認した法令原典の限界：e-Gov動的法令全文の直接取得 `NOT_ESTABLISHED`。最新の自治体別報告ルールや個別の医学的判断も `NOT_ESTABLISHED`。出典が公的であることは国や実在専門職の監修認定ではない。

## 4. 範囲別GO/HOLD

| 範囲 | 最終判定 | 根拠・次のゲート |
| --- | --- | --- |
| **既存静的服薬ガイドの現行HTTP到達** | **PRODUCTION_HTTP_CONFIRMED** | 外部runner 15/15 + Vercel READY/alias。機械HTTPの範囲だけ |
| **既存服薬ガイドの安全な文言・UI更新** | **RELEASE_HOLD** | B #466最新最終文章 → Cが本文へ反映 → C exact-head CI → Dが**そのhead**を独立監査する必要あり |
| **転倒・転落** | **PUBLIC_SOURCE_GUIDE_HOLD** | A FALL-01〜03・B F-01〜04はあるがCの新規articleなし、DのHTML実装審査なし |
| **異食** | **PUBLIC_SOURCE_GUIDE_HOLD** | A ING-01/02のみ。B記事本体・C実装・D最終審査なし。異食と誤飲は別 |
| **誤嚥・窒息** | **PUBLIC_SOURCE_GUIDE_HOLD** | A ASP-01/02、Bの参考案があっても個別食事形態・救命・治療判断を掲載不可。今回は第二候補不採用 |
| **回答選択式の服薬試作 #451** | **PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED** | EX01/EX02=`NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE`、HU01=`HUMAN_APPROVAL_NOT_DONE`。依頼・試作flag有効化・mergeを実施しない |

**Wave全体：`PARTIAL_WITH_GAPS`**。前WaveのHTTP gapを機械実測で閉じたが、P1同一版安全ゲート、実ブラウザ・Android／native 200%・読み上げ・印刷検証が残る。公開件数を優先していない。

## 5. 技術・アクセシビリティ、次の担当

- #465のheadless Playwright／CSS zoom代替テスト（CI success）は**native Android 200%、実読み上げ、紙の印刷確認の代替でない**。各項目 `NOT_RUN`。390pxもCのheadless CIとproduction実Androidを区別。キーボード、font拡大、source direct links、metadataは公開反映後の最終再検証が必要。
- read-only probeはHTTP statusと静的HTMLを確認した。原典リンク先の現在のHTTP availability、利用者が視認できる外部タブ遷移、実端末での印刷は追加検証事項。
- **次のA/B/C/D**：Aの台帳追補はmainに保存済み。Bは#466 final draftを維持し、A主張IDと原文頁を表示稿へ引継ぎ。Cは#465を既存服薬文言修正と転倒・転落の限定静的記事へ反映しCIを更新。DはCの**最新headとB最終文章・表示された文面**を再監査し、7つの危険な誤読ケースと追加記事の禁止表現を再確認。
- **Eの次の仕事**：D同一版再検証後に変更ごとのrelease GO/HOLDを判定。merge／新production deploymentが生じれば、新runtime SHA・READY・alias・新deploymentに対する外部GETと実ブラウザを再照合。正式deploy verification contractが完結した場合にのみmarker更新。
- 公開11 routeと5+5、Issue 6候補、既存Analytics運用は変更しない。個人情報・事故入力・カスタムAnalytics収集、専門職への新規レビュー依頼、予定済タスク登録なし。

## 6. 本Eの操作境界

今回A #470とD #471の監査文書だけmainへ統合。#466（文章草案）、#465（未承認code）、#451（安全試作）のマージと公開はしない。既存productionのdeployment／alias／flag／deploy-stateはEが変更していない。外部read-only probe PR #472の統合はそのrequired checks完了を確認した場合だけ別途扱う。本判定のPR・main merge commitとreadbackは統合作業完了後に記録する。

**独立結論**：Vercel READY・公開HTTP・独立安全審査・実端末使用・非公開試作のヒューマンレビューはそれぞれ別の証拠であり、相互に代替しない。
