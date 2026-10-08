# Kaigo Ops — 2026-10-09 服薬安全専門職審査・アクセシビリティ／プライバシー統合HOLD判定

**checked_at:** 2026-10-09 08:25 JST（版・PR・Vercel API・公的資料を照合。公開HTTPの実測不可）  
**scope:** `ops-site/` 非公開「服薬業務の安全点検シート」。既存5 Issue／5 action toolは対象外の公開既存機能。  
**instruction:** `/Kaigo Ops/Work Instructions/2026-10-09_medication_safety_expert_review_activation_and_accessibility_privacy_closure_wave_instructions.md`  
**prior decision:** [2026-10-09 version-lock decision](./2026-10-09-medication-safety-version-lock-and-review-gates-decision.md)（PR [#461](https://github.com/Josh-Temple/kaigo-rules/pull/461) merged）。前回決定は履歴として保存。

## 1. Eの最終判断と公開境界

| 独立判定軸 | 結果 | 根拠・限界 |
| --- | --- | --- |
| Wave検証 | **PARTIAL_WITH_GAPS** | 固定版の資料・テストは前進したが、実機、人間審査、production実操作などが未実施 |
| 独立安全監査 | **SAFETY_PARTIAL_WITH_GAPS** | DのChromium独立テスト17/17成功。ただしR/P/U 29 cases＝11 `PASS_LIMITED`／18 `PARTIAL`。実務上・医学的安全のPASSではない |
| 公開 | **PREVIEW_ONLY / NOT_PUBLIC** | EX01／EX02実レビューとHU01明示GOがない。アクセス制御も未実証 |
| 本番リリース | **HOLD / NEW_DEPLOYMENT_NOT_RUN** | 未承認C #451をdraft／未マージで保持。公開flag・public registry・nav・sitemap・Analyticsは変更しない |

`PREVIEW_ONLY`は認証なしの公開previewを意味しない。flag `MEDICATION_SAFETY_PREVIEW=enabled`は認証ではなく、第三者遮断を実証できないVercel Preview等を新設・送付しない。localhost限定の検証結果を一般公開GOへ読み替えない。重大な危険誘導・漏えい・匿名露出の**実証**は今回ないが、不足試験を陰性証拠としない。

## 2. 同一版ledger（この時点のfresh read）

| Layer | HEAD / blob・test identity | 状態 |
| --- | --- | --- |
| main | `8d824ce35be176dd05de976709ee1f81944b65d1`（前E #461 merge） | docs main。production runtimeと**別** |
| B [#459](https://github.com/Josh-Temple/kaigo-rules/pull/459) | open, non-draft; head `9c7b8639380802224bd9b5518f52800ff0b56af8`; issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25`, service blob `e3889c26c5b46d4644b29d94c657e628c96206d3`; 新規review補足 `64feae5962df5614d0d86a6fc36ed24687bae16b` | 本文・サービスの意味は不変。補足で5状態、S01–S08、EX01/02質問、空欄様式、未送付依頼文を作成 |
| A [#458](https://github.com/Josh-Temple/kaigo-rules/pull/458) | open, non-draft; head `87b9d67a08b3c9503a47e9914a1abe5af16ca21c`; trace blob `3264cb93cc2c7f867abe7fb42def68be03bf98e6` | §8のB 2 blobs照合を保持し、§9で原典→B→C→EX質問と8群の暫定除外を追補。B-00〜13 exact 14/14、8群アンカー8/8は**文書整合のみ** |
| C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) | **open/draft/unmerged**; head `2dd0e260d0922e18d003905f4a7edf42560f640c`; D固定元code commit `7ec2fe8c644d0526af1650e857a7da397488a0ad` | 3 app code blobsは一致。D固定点からの変更は`medication-safety-prototype-verification.md`とCブラウザtestの2ファイル（「docs-only」ではない） |
| C 3 code blobs | page `cfa6f30633c5c8536b570c4c82b2794cd4353320`; worksheet `2ecd0475681f5a822da0f3dbe32c4610a041d47c`; model `9580e9202209f5e3fdf3b544b628d68885062295` | branchファイルを直接readback。結果・印刷・モデル変更なし |
| D [#457](https://github.com/Josh-Temple/kaigo-rules/pull/457) | **open/draft/unmerged**; head `61a0189c21cb2b782b9522bd17172d6e20eedb66`; independent spec blob `28161729ba8b602a45920c292da6b2db476646bc`; workflow blob `241415cc2f8536bca185c27a6ecba85a8e4e57f3` | 前回独立run後のhead差分はDドキュメント3本のみ。workflowとtestはC code `7ec2fe8c...`へSHA固定 |
| D review pack | D `medication-safety-expert-review-pack.md` blob `75b5d78c630f4c3940d83d0e630401a7ff2e069e`、§9.6 | 最新A・B補足・C差分・17テストを取り込んだ。**READYは送付・審査済みを意味しない** |

**出典（EがPDF現物の該当ページを再閲覧）:** 厚生労働省 Vol.1436（2025-11-07）[ガイドライン](https://www.mhlw.go.jp/content/001591418.pdf)冊子p38＝PDF zero-index40（施設中心の誤薬・与薬漏れ対策の推奨、服薬後確認の手順記載あり）、p39＝PDF41（特養の単一事例）、p46＝PDF48（通所の家族連携、訪問の事業者連携という一般的論点）。Vol.1332（2024-11-29）[事故報告様式等の通知](https://www.mhlw.go.jp/content/001574219.pdf)PDF zero-index2–3（報告の範囲・様式と自治体の取り扱い、服薬実施権限を定めるものではない）。一事例を全事業所の義務・標準業務・事故減少の証拠にしない。**独自5状態は厚労省が認定した尺度ではない**。

## 3. 技術検証・29-caseの到達点

- **C最新-head own CI:** [preview run 37858189100](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858189100) `success`、[Ops regression 37858188762](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858188762) `success`、[publication readiness 37858188830](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858188830) `success`、generic build 37858188777 `success`。Chromium localhostのみ、flag enabled側29 unit PASS/15 browser PASS＋1 conditional SKIP、disabled側29 unit PASS/8 browser PASS＋8 conditional SKIP（詳細C検証§9）。5状態のscreen+print warnings、390px keyboard/focusも合成値で追加確認。CI成功はhuman QAでも公開承認でもない。
- **D独立実行:** 追加2 assertを含む17件は初回 [run 37857899198](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37857899198) `failure`（架空例の確認dialogをtest harnessが扱わなかった）。修正後 [37858180696](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858180696) `success`、17/17。最新D headでも [37858614736](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858614736) `success`（変更ファイルはdocsのみ）。失敗履歴を消さない。
- **R01–R16、P01–P07、U01–U06＝29 cases:** 最終 `11 PASS_LIMITED / 18 PARTIAL`。個別`expected/actual/method/target SHA/run/limitations/retest owner`はD [`medication-safety-test-results.md` §10.2／§11.2／§11.4](https://github.com/Josh-Temple/kaigo-rules/blob/61a0189c21cb2b782b9522bd17172d6e20eedb66/docs/kaigo-ops/safety/medication-safety-test-results.md)が正本。17 Playwright assertions≠29 casesの独立PASS、29件≠医学的検証済み。
- **観測したprivacyの範囲:** 独立C/D localhost・合成選択値のURL、リクエストbody/header、browser storage、履歴、Analytics custom event対象の限定テスト。調べたパスで回答漏えいを検出しなかったが、既存Analytics pageview通信は存在し得る。**全環境・全ネットワークで回答送信ゼロと断言しない**。
- **NOT_RUN:** 実Android Chrome＋OS文字サイズ、native browser zoom 200%、スクリーンリーダー人間実聴取、native印刷プレビュー・紙/PDFの人間目視、production実ブラウザprivacy＋390px操作。Playwright CSS模擬・print DOM・PDF in-memoryは人間検査の代用ではない。
- **PREVIEW_ACCESS_NOT_ESTABLISHED:** 外部のflag-enabled previewで第三者アクセス遮断を確認した実証なし。flag/noindex/URL秘匿は認証でない。
- **workflow security（静的）:** D workflowは`contents: read`、Action checkout/setup-nodeはSHA pin、`persist-credentials: false`、D checkoutから試作code commitを明示SHA pin。localhostだけで実行。workflowを含むD PRをdocs-onlyとして自動mergeしてはならない。その他の実行基盤・配信範囲の網羅的保証ではない。

## 4. 表現・サービス／職種の判断待ち

Bの5状態 `unknown/confirmed/needs-review/not-prepared/not-applicable` はCと静的に対応。**全confirmedでも安全合格・投薬権限の保証はない**。**全not-applicableでも工程不要・免責ではない**。印刷物の独り歩き、警告の見落とし、架空例、未回答、resetを検証対象とする。

A §9・Bサービス§7の8サービス群の現場業務・役割・担当職種の権限・正式手順・自治体の事故報告運用は個別に`REVIEW_REQUIRED / NOT_ESTABLISHED`。通所、訪問、短期入所、居宅介護支援・介護予防支援などで直接服薬業務を当然視する工程は暫定除外候補。現実の疑義・事故に本シートを使わず本人の安全、所属先の正式手順、管理者、関係する医療職／緊急対応へ戻る。再投与・服薬可否・事故報告要否／期限の判断は対象外。原典の推奨、単一事例、独自設計を厳密に分ける。

## 5. 実在の人間ゲート（実施と準備の混同を禁止）

| Gate | 審査役割と対象 | 許可／依頼／実査／結論 |
| --- | --- | --- |
| EX01 | 薬剤師・看護職等。医療判断誤読、本人意思、実施職種の権限、表示・印刷を審査 | `PERMISSION_NOT_ESTABLISHED / NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE` |
| EX02 | 事故防止・実務リスク責任者。8サービス、工程、中断・引継ぎ、誤安心、事故報告境界を審査 | `PERMISSION_NOT_ESTABLISHED / NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE` |
| HU01 | 責任者本人がEX01/EX02の実査・是正・再審査後、対象版・運用・公開範囲にGO/HOLD | `PERMISSION_NOT_ESTABLISHED / NOT_REQUESTED / HUMAN_APPROVAL_NOT_DONE` |

**REVIEW_PACK_READYのみ。** 資料はB補足＋D packに整備したが、レビュアーの個人情報、匿名review ID、実査日時、指摘、署名、承認を架空補填しない。正当な依頼者／権限・送付内容・審査者資格・守秘方法・明示的送付許可が確定するまでメール、招待、共有は行わない。指摘による意味変更後はB 2 blobs→A trace→C code/flag別CI→D cases→EX再審査の順で再固定。

## 6. 本番project identityとリリース未実施の範囲

- Vercel APIにて`kaigo-ops` project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`、latest production `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`、`target=production`、`READY`、runtime Git SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app`を**今回fresh確認**。docs main `8d824...` とruntimeを混同しない。
- `deploy-state/kaigo-ops` branchのGit ref SHAは `e49e770a970e541d2ad95204ad277eca89a485d3`（今回GitHub APIでreadback）。日次workflow自身の完走成功を意味しない。
- main登録は既存5 Issue＋5 toolのまま。公開11 routes（home＋5＋5）の**過去EのHTTP 200**、試作route `/tools/medication-safety-preview` **過去Eの404**、robots/sitemap 200は**前回から継承**。本Eでは公開URLへのHTTP直接取得が環境エラーとなり、**FRESH_HTTP_NOT_RUN**。従って今回の11 route 200／試作404を新規PASSとは記さない。Vercel API READY＝各URLのHTTP結果でも実利用者のブラウザ操作でもない。
- **production browser `NOT_RUN`**、390px、各ツールの操作、Kaigo Rules制度確認・feedback導線、Analytics通信の新規実測は未実施。Analytics `RECEIVE_CONFIRMED`、Search Console `UNKNOWN`は従前の観測から継承。アクセス権を持つ集計の再取得はしていない。観測期間2026-10-21前後〜11-04前後は保持。PVを事故予防効果・需要の確証としない。
- **本Waveのproduction deployment／alias切替／認証なしpreview公開なし**。Issue 6「収支・コスト構造」の候補番号を占有しない。

## 7. 未充足ゲート、次担当、再判定条件

1. **EX01/EX02・送付権限者:** 正当な依頼者・審査者の役割と資格、送付可否と守秘方法を非公開で確定。明示許可後に同一版packを共有し、実在の指摘・是正・再審査結果を匿名IDで記録。**現時点NOT_REQUESTED**。
2. **C（#451）:** 非公開条件を維持し、実Android、native 200%、支援技術読み上げ、ネイティブ印刷と紙/PDFの人手確認、全状態の警告理解を実測。変更すればblobとflag別runを再固定。draft維持。
3. **D（#457）:** C変更時は該当R/P/U再試験、現29 caseの`PARTIAL`解消、合成値network/Analytics全域と外部previewアクセス遮断の証拠整備。workflow pinと最小権限を再確認。draft維持。
4. **A/B（#458/#459）:** EXからの意味修正はB本文／serviceとA claim traceの再照合を実施。適用が立証できないサービス・工程は公開候補から外す。docs-only PRは別途CIと競合を精査しなければmergeしない。
5. **E／HU01:** 完了版の独立技術証拠とEX01/EX02実査・全指摘の是正／再審査を確認し、権限あるHU01本人が対象版と公開サービス範囲、訂正・問い合わせの責任者を明示GOする場合に限り`GO_FOR_PUBLICATION`再評価。既存11本番ルートHTTP＋実ブラウザ、release CI・access、privacyを必要な範囲でfresh再確認。
6. **既存Ops運用者:** production HTTP取得が可能な環境で11ルート、試作404、robots/sitemap/canonical、実操作390pxを再測定。日次production verifierのsecret配置と実行実績、Search Console認証済み実測は別途追跡。

**Reassessment trigger:** 出典や文言の意味変更、C/D code/test/workflowの変更、独立の危険誘導／漏えい／匿名露出の実証、端末・privacy・accessibilityの欠落解消、EX01/02実査と再審査、HU01本人の明示GO/HOLD。全公開ゲートが揃うまでは**PREVIEW_ONLY / NOT_PUBLIC**を維持し、`#451`をマージしない。
