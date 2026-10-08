# Kaigo Ops — 2026-10-09 服薬安全試作の版固定・独立再検証・実在レビューゲート：Worker E統合判定

**Checked at:** 2026-10-09 JST（GitHub、厚労省一次資料、Vercel API、公開HTTPを本Waveで再取得。実ブラウザ操作は未実施）  
**Instructions:** `/Kaigo Ops/Work Instructions/2026-10-09_medication_safety_version_lock_independent_revalidation_and_human_review_gate_wave_instructions.md`  
**Baseline main:** `1360bd78d971266c5e635c7a3416d5b4629e1c0e`（E変更前、production runtimeではない）  
**Scope:** 非公開「服薬業務の安全点検シート」に限定。実在利用者、薬剤、処方、事故記録、秘密情報は扱わない。

## 1. Decision — release HOLD

| 軸 | E判定 | 根拠・意味 |
| --- | --- | --- |
| Wave | **PARTIAL_WITH_GAPS** | A/B/C/Dの最新版対応を限定確認したが、残る実務・human・accessibility gate未解消 |
| 独立安全監査 | **SAFETY_PARTIAL_WITH_GAPS** | 新Cの同じ3コードblobに対するDの独立CIは成功。29ケース全てを安全PASSとはしない |
| 公開 | **PREVIEW_ONLY / NOT_PUBLIC** | 審査資料は準備済みだが、EX01/EX02/HU01は未実施、匿名previewのアクセス制御も未確立 |
| EX01 / EX02 | **EXPERT_REVIEW_NOT_DONE** / **EXPERT_REVIEW_NOT_DONE** | 実在専門職による対象版レビューID、日時、所見、承認なし。送付・依頼も行っていない |
| HU01 | **HUMAN_APPROVAL_NOT_DONE** | 公開責任者から版・サービス範囲・文言・運用担当への明示GOなし |

これは臨床的安全性、法令適合、事故防止効果、職種権限を認定する決定ではない。一般公開しない。C #451はdraft・未マージとし、productionのflag、public registry/nav、sitemap、Analyticsの回答収集を変更しない。**PREVIEW_ONLYは匿名公開の承認ではない**。重大な漏えいや医療的な危険誘導を実証したわけではないため、`BLOCKED`と断定せずHOLDを継続する。

**前Wave正本は保存する:** [2026-10-08 content alignment E decision](./2026-10-08-medication-safety-content-alignment-and-independent-validation-decision.md)。前回のB→A、C→D版不一致は、その**前回観測時点**には正しかったが、本Waveで後続の版追跡と再試験が進んだ。前回の記録を消したり、旧版のPASSを新版へ移したりしない。

## 2. Fresh GitHub identity / immutable version ledger

| 項目 | 今回確認したhead・blob／状態 | 評価 |
| --- | --- | --- |
| main（E着手） | `1360bd78d971266c5e635c7a3416d5b4629e1c0e`（#460 merged） | 文書用branch。runtimeと区別 |
| B [#459](https://github.com/Josh-Temple/kaigo-rules/pull/459) | open, non-draft, unmerged; head `364519815a41143560b068cfa459e7a04962f18f`; Issue blob **`e0cc354e2b78a28912c80c0611ccf3c165d00b25`**; service blob **`e3889c26c5b46d4644b29d94c657e628c96206d3`** | B第9節、five-state、共通警告、8サービス群。医学・実務レビュー未了 |
| A [#458](https://github.com/Josh-Temple/kaigo-rules/pull/458) | open, non-draft, unmerged; head `37fc213301e93442f71efc4509af5cfa49567c88`; trace blob **`271560deb7ea848690e12d97fd23661583511198`** | 第8節は上の**正確なB 2 blob**を対象。B-00〜13の14逐語anchor、MS 20 claim、8サービス群を追跡。結論PARTIAL_WITH_GAPS |
| C [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) | open, **draft / unmerged**; latest head `a61797393f20e897247d985ab0861f6443a0a74e`; tested code commit `9814dc541880c16cf311f0c700dc458c33ee2a83`; code含有のD pin `7ec2fe8c644d0526af1650e857a7da397488a0ad` | latest headへの差は検証Markdownのみ。code固定は次の3 blobs |
| C 3 code blobs | page **`cfa6f30633c5c8536b570c4c82b2794cd4353320`**; worksheet **`2ecd0475681f5a822da0f3dbe32c4610a041d47c`**; model **`9580e9202209f5e3fdf3b544b628d68885062295`** | Bの共通警告と選択肢を反映。結果・印刷の限定自動検査のみ |
| D [#457](https://github.com/Josh-Temple/kaigo-rules/pull/457) | open, **draft / unmerged**; head `3f3527bacbe8f34029064a0092cae35c78023e00`; case results blob `56e3ad3bb75f2673eb0e6d5e4c6bba6de235eabb` | D §10.2/§10.4/§10.5とexpert pack §8.6を最新版として優先。旧target a1357ad…は履歴 |

**同一版検査:** B本文/service最新2 blobs → A第8節のexact anchor/source crosswalk → C最新版の同一3 code blobs → Cのflag別CI → D workflowがcheckoutするC commit `7ec2fe8c...` → D独立run → D review packの最新版§8.6。**今回の固定blob間の旧不一致は解消**。ただし「同じ版を調べた」ことと「公開上の医学・サービス・UI妥当性がPASS」は異なる。D workflowとcase台帳は現在もD draft PR内にあり、mainにまだ統合していない。

### CI / checks（CI runと対象版の混同禁止）

- **B current head:** `build`, `publication-readiness` 共にGitHub check `success`。**A current head:** 同2 checks `success`。
- **C自身:** [Validate medication safety preview run 37844184628](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844184628), target `7ec2fe8c...`, `completed/success`。enabled localhostはunit **29 pass**、Chromium **13 pass / 1 conditional skip**。disabled localhostはunit **29 pass**、Chromium **8 pass / 6 conditional skip**。未設定／不正flagはlocalhost 404。関連 [Validate ops site run 37844184648](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844184648)も`success`。skipはPASSに含めない。前のC runの成功を新版へ流用しない。
- **D独立:** [Independent medication safety dynamic audit run 37844583974](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844583974) `completed/success`。PR #457最新headのchecksは`independent-enabled/disabled`、`build`、`publication-readiness`が`success`。専用Chromium **15/15 tests pass**（localhost enabled）、未設定・不正flagは各404＋既存公開11 route local verifier pass。workflow `contents: read`、両checkoutはcommit pin／actions pin、`persist-credentials: false`、外部環境への匿名試作の生成やartifact uploadなし。対象C commit `7ec2fe8c...`と最新Cの**コードblob同一**を確認。D run自体のhead SHAはD branchのworkflow commitでありC headとは別。

### D全29ケースの読み方

正本は[D case ledger §10.2, §10.4–10.5](./medication-safety-test-results.md)（現時点ではD #457上）。`R01–R16`16件＋`P01–P07`7件＋`U01–U06`6件、**計29 case記録**。内訳は **`PASS_LIMITED` 11件、`PARTIAL` 18件**。15件のD独立Chromiumテスト成功は、29件の医学的安全審査PASSを意味しない。各caseの`expected/actual/method/C_SHA/run/limitation/retest`とコード的根拠はD §10に残す。

- **限定実行:** 合成enumの初期・全confirmed・全not-applicable・mixed・架空例・不正型、reset、結果／print DOMとPDF in memory、URL/header/bodyの合成マーカー、history/storage/cookie、390px、CSS zoom模擬、label/focus/aria-live、flag遮断。
- **残る部分・NOT_RUN:** 実Android Chrome、nativeブラウザ200%拡大、スクリーンリーダー実聴取、ネイティブ印刷プレビュー/現物、offline/clipboardの一部、外部アクセス制限が実証されたpreview、全環境のNetwork/Analytics、productionのユーザー操作と390px実機回帰。ページ閲覧・通常Analytics pageviewはゼロ通信の証拠ではない。
- **privacy:** 検査対象の合成値は有限なブラウザ／時間窓内で送信・保存への混入を検出せず。未測定の通信先、全状態、外部サービスへの包括的な不存在は断定しない。

## 3. Source and service applicability — checked limits

Eは2026-10-09 JSTに厚労省の原典PDFの該当ページを再閲覧した。**G25**＝[介護保険最新情報Vol.1436／2025-11-07](https://www.mhlw.go.jp/content/001591418.pdf)、「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」、冊子p38/39（PDF 0起算40/41）・冊子p46（PDF 0起算48）。施設向けの誤薬・与薬漏れに関する推奨、**特定の特養一事例**、通所/訪問等における情報共有と連携の一般的記述を区別する。冊子p38は服薬後の確認にも**実際に言及**するが、全職種・全サービスの共通手順を法的に義務付ける根拠ではない。

**N24**＝[介護保険最新情報Vol.1332／2024-11-29](https://www.mhlw.go.jp/content/001574219.pdf)、PDF 0起算p2（事故報告の対象、自治体ごとの取扱い、報告内容／方法／目安）。標準様式の提示は、本試作の服薬実施権限、個別事故報告要否・期限の自動判定を認めない。

A traceはBの14アンカーとMS-01〜20、資料版・証拠種別・サービスscopeを区別。残る**MS-07（服薬確認方法・専門職境界）、MS-08（一事例）、MS-13/14（事故報告）、MS-15（通所・訪問への転用限界）、MS-17〜20（DO_NOT_PUBLISH）**は資格・権限・自治体運用に関する専門・実務判断へ送る。Bの五値は厚労省が承認した尺度ではなく本サイト独自の`DESIGN_PROPOSAL`。8サービス群の実際の工程、職種権限、正式手順、自治体別報告運用は `REVIEW_REQUIRED / NOT_ESTABLISHED` を維持。現時点で全サービス一律の完成教材・公開手引としない。

## 4. Human gates and handoff (no surrogate approval)

審査用の質問・版付きpackは[D expert review pack §8.2–8.6](./medication-safety-expert-review-pack.md) に準備され、**REVIEW_PACK_READY**。`REVIEW_REQUESTED=false`。`EX01/EX02=EXPERT_REVIEW_NOT_DONE`、`HU01=HUMAN_APPROVAL_NOT_DONE`。匿名review ID、実査日、指摘、是正、新C blob、再審査結果、本人の承認GOは空欄のまま。実名/所属/署名/連絡先や実事故記録を公開GitHubに記録しない。

- **EX01 owner:** 実在の薬剤師・看護職等。MS-07、再投与/服薬拒否、事故発生時、本人意思、印刷警告、医療判断に見える文言を対象版でレビュー。未依頼。
- **EX02 owner:** 介護事故防止・リスク管理実務責任者。施設・短期入所・居住/通所/訪問・居宅支援等の工程と役割、現場負荷、全確認/全担当外の誤安心、事故時経路を確認。未依頼。
- **HU01 owner:** 内容・公開の実在責任者。EX01/EX02の実結果、残る技術gap、対象サービス、公開文面、訂正/問い合わせ/更新責任者を確認し、対象commit/blobsに**明示GO/HOLD**。未実施。

権限者の明示許可なく外部レビュー依頼・招待・資料送付をしない。意味の変更があればB→A→C→Dの該当版を再固定し、審査packを再提示する。

## 5. Production and pre-release exposure (fresh E observation)

| 対象 | E再取得結果 | 射程 |
| --- | --- | --- |
| Vercel project | `kaigo-ops` / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp` | Kaigo Ops専用 |
| 最新production | `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`、target `production`、`READY` | **新deploymentなし** |
| Vercel Git SHA | **`e49e770a970e541d2ad95204ad277eca89a485d3`** | docs用main SHAとは別 |
| deploy-state branch | `deploy-state/kaigo-ops` = `e49e770a970e541d2ad95204ad277eca89a485d3` | runtimeと一致 |
| Production alias | [https://ops-site-pi.vercel.app/](https://ops-site-pi.vercel.app/) | Vercel deployment alias直接照合 |
| Public HTTP（本Wave） | home 1、Issue 5、tool 5 **合計11ルート全てHTTP 200** | Vercel経由の実HTTP取得。ブラウザUI操作PASSではない |
| Preview route（本Wave） | `/tools/medication-safety-preview` **HTTP 404** | public productionの特定routeのみ |
| Search files | `/robots.txt` **200**、`/sitemap.xml` **200** | sitemapはホームと既存5 Issue（新試作なし） |
| Public source | `app/issues/registry.ts` 5 Issue、`lib/action-tools.ts` 5 tool、`app/sitemap.ts`に試作登録なし | mainを直接read |
| C Vercel branch deployment | `worker-c/medication-safety-preview-20261008`での最新取得結果は対象0件、Eは新previewを作成せず | 他の環境・非公開ホストまでの網羅保証ではない |
| Vercel protection metadata | projectのSSO `all_except_custom_domains`、passwordProtection off | flag-enabled外部previewのaccess controlを実証しておらず`PREVIEW_ACCESS_NOT_ESTABLISHED` |

**今回未実施:** 本番Chromeでの実際の入力/消去/印刷/390px journey、完全なlive Network/Analytics payloadの監査、全canonicalのブラウザDOM確認、Kaigo Rules/feedbackの実操作・Search Console認証済み確認。HTTP応答をUI/E2E PASSと記載しない。既存ツールのlocal browser regressionはC/DのCI証拠として別記録。既存の制度確認リンクやfeedback契約はコード変更していないが、実操作の新規PASSとはしない。

**Analytics:** `RECEIVE_CONFIRMED` は**前Waveからの継承値**であり、このEでは新たな認証済み利用統計やイベントペイロードを計測していない。合成選択値をAnalytics custom eventへ送らない。**Search Console:** `UNKNOWN` は継承値、今回fresh authenticated確認なし。PVは服薬事故の減少を示さない。既存の観測窓（2026-10-21頃〜2026-11-04頃）を変更しない。

## 6. Integration disposition, next owner, reevaluation

- Eは本書と `docs/kaigo-ops/CURRENT.md`、`docs/kaigo-ops/roadmap.md`、`ops-site/README.md` の4 Markdownのみを専用branch/PRへ保存する。前回decisionは残す。CIとmerge/main readbackはE PRの実際の結果で別途確定する（記録前に成功を主張しない）。
- A #458とB #459はdocs-only、checks成功だが、専門職未レビューの公開候補本文を無条件にmainへ進めない。別途内容確認と統合順を要する。D #457は**GitHub Actions workflowと独立テストを含む**ためdocs-onlyではない。workflowのpin/最小権限を確認したが、draft未マージを維持。C #451はdraft未マージが絶対条件。A/B/Dをmergeした事実は本Eではない。
- **Next A/B:** 根拠の限界・文言差・サービス範囲が人間レビューにより変化した場合、2 B blobsとA exact-anchor traceを再固定。**Next C:** 変更時には3 code blobs、flag別local testと privacy/print/ARIAを再測定。**Next D:** 改訂後Cで29case実行台帳を更新し、native zoom/Android/支援技術/印刷/外部accessの不足をcaseごとに記録。**Next EX01/EX02/HU01:** 実査・HOLD/GOの匿名証拠を残す。**Next E:** 全ゲート完了後に限り公開GOの可否を再判定。
- **Reevaluation triggers:** B/A/Cの意味・blob変化、D失敗/漏えい・匿名露出検出、EX01/EX02レビュー実査と是正・再審査、HU01明示結果、外部preview accessと端末/アクセシビリティ/印刷のgap解消。本番で重大な危険誘導や漏えいを実証したら直ちに公開HOLD/隔離を判断。
- 既存5 Issue/5 action toolを維持。Issue 6「収支・コスト構造」候補を服薬安全で置き換えない。認証なしpreview、public flag、production新release、回答収集、secret表示、実在症例、専門職代理承認は実施しない。

**現時点の最終結論: `PARTIAL_WITH_GAPS / SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`。**
