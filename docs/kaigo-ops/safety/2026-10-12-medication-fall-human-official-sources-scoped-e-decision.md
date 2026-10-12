# Kaigo Ops — 服薬・転倒・公的資料案内の人手受入と範囲別E統合判定（2026-10-12）

**判定日:** 2026-10-12 JST
**指示正本:** `/Kaigo Ops/Work Instructions/2026-10-12_medication_fall_human_acceptance_official_source_guides_and_scoped_release_wave_instructions.md` §9
**対象:** `Josh-Temple/kaigo-rules` の `ops-site/` と `docs/kaigo-ops/`
**全体:** **`PARTIAL_WITH_GAPS / NO_GO / ALL FOUR RELEASE SCOPES HOLD`**
**位置付け:** A/B/C/Dの現行候補・機械CI・人手受入の照合と、公開範囲ごとの決定。記事の公開・人手の署名・Vercel本番反映・post-deploy検証の実績ではない。

## 1. この判定の基準・版の固定

E着手時にGitHub APIで取得した `main` full SHAは **`7a06ddeaac82dc387a82006c442c856aff20647d`**。これは前E [#485](https://github.com/Josh-Temple/kaigo-rules/pull/485)の**文書のみ**統合後であり、Vercel runtime SHAではない。前E判定blobは `fd628a8a545ed7794314b8701f07380036e51032`（[前E正本](./2026-10-11-medication-fall-isolated-exact-head-e-decision.md)）。人手の安全内容・native 200%と実読み上げ・実PDF viewerと実印刷は引き続き**公開前必須**であり、D `PASS_LIMITED` やCI成功から補完しない。

| 所有 | 今回の実体と固定版 | この版の意味と限界 |
| --- | --- | --- |
| A | [Draft #490](https://github.com/Josh-Temple/kaigo-rules/pull/490) / head `378a6668f56b405f2abfffc3a409e69a2b3dca34` / 出典台帳§10 blob `c5abff32dc366129995cbd3d58c7a2dd3e478096` / 文書1パス | 新資料5 source ID、POLY-A01〜A09を採否。**mainには未統合**。元のG25/N24/R17/PMDAと法律節削除判断はNO_CHANGE。 |
| B | [Draft #466](https://github.com/Josh-Temple/kaigo-rules/pull/466) / head `5e186fc537e44c7f924ec491a3b09cdca545c2fc` / 原稿§10 blob `1b0ea3a08cd8f1ebb3423df3d1463da072e340e1` / 文書1パス | **既存4資料**の案内文とR/F/Gケース、人手受入票を作成。§10.9でも追加POLY原典の新カード文案はA確定後の追補待ち。§2/§3/§9の旧14引用ブロックは不変。**Bの新資料最終稿ではない**。 |
| C：新案内 | [Draft #491](https://github.com/Josh-Temple/kaigo-rules/pull/491) / base `7a06ddeaac82dc387a82006c442c856aff20647d` / head `606f12f86cd1d82a3521e7fb1a05cc1517eb3091` / 6パス | `/guides/accident-medication-sources` の静的・読取り専用の**ローカル審査候補**。G25/N24/R17/PMDAのみ掲載。新POLY資料は未掲載。通常環境・Vercelでは `notFound()`、ホーム・sitemap導線なし。公開版へ切替えるには新headの再審査が必要。 |
| D | [Draft #487](https://github.com/Josh-Temple/kaigo-rules/pull/487) / head `014f2b676d9bda0337b3744bbaac60a9871730ea` / 独立監査台帳§14 blob `c6539e490eacc24e2d0ebc535c312cbd27147255` / 文書1パス | 原典URLの負例を発見し、旧#480/#482 exact head/CIを再確認。**今回のA#490・B#466§10・C#491最終headが揃う前のpreflight**。新案内の同一版D最終監査ではない。main既存D§13 blob `0f00f2c344f34c36af52e20ea54b4ae733770c6c` と混同しない。 |
| C：服薬改訂 | [Draft #482](https://github.com/Josh-Temple/kaigo-rules/pull/482) / head `6c64af5924da24ea89a147ad9d42c7f1155c3f45` / 4パス / 服薬TSX blob `8f9876db7dfc81d232e04d3f250b5e115232b540` | 法律節・`#law`・e-Govリンクを除去。旧D§13 `PASS_LIMITED` は同じcode/test blobsに限る。未merge。 |
| C：転倒 | [Draft #480](https://github.com/Josh-Temple/kaigo-rules/pull/480) / head `b5b73e46e0217ff8ec689c9984d6b837cd7d92cc` / 6パス / 転倒TSX blob `de66e2dfcb0985864be230049ecea44612fd3b05` | 旧D§13 `PASS_LIMITED` は同じcode/test blobsに限る。単独では現行服薬の旧法律節が残り、転倒→服薬リンクで到達できる。未merge。 |

**重要な時系列の差:** D§14は確認時点でA追加節・B新稿・C新案内がまだ見つからないと記録した。その後にA#490・B#466§10・C#491がGitHubに存在することを**Eが直接再取得**した。したがって「新案内PRは存在しない」というDの当時の観察を現在の事実とはしない一方、Dの受入を後続headへ自動拡張もしない。

## 2. 出典誤対応と新案内の編集境界

- **採用禁止の誤リンク:** Wave指示書にあった `001094895.pdf` と `001094896.pdf` は、それぞれ指定された2018年総論編・2019年各論編そのものではない。D§14の独立負例とA§10の採否が一致。**誤リンクを新案内に掲載しない**。
- **Aの正本識別:** 総論編（2018年5月） `https://www.mhlw.go.jp/content/11120000/kourei-tekisei_web.pdf`、各論編（2019年6月） `https://www.mhlw.go.jp/content/11120000/000568037.pdf`。2026年7月31日の厚労省案内 `https://www.mhlw.go.jp/stf/newpage_74909.html` は**2026年の概要・普及啓発資料の案内**であって、2018/2019原指針そのものの改訂日ではない。正式な後継改訂版の網羅確認はA自身が `NOT_ESTABLISHED` としている。
- **新資料の掲載条件:** A§10の許容表現を受けBが新資料カードの最終文言・対象・年・できない判断を**同一版**で確定し、Cが当該新headとテストへ反映、Dが新headで原典・本文・N01〜N08を独立評価するまで追加しない。医師等の処方見直しを介護職の独断手順に変換しない。
- C#491現行は既存採用4資料のみ。冒頭の事故時の正式手順優先、G25施設中心、N24の5日以内**目安**と自治体差、PMDA一般相談は救急診断の代替でないことを**候補コード本文に確認**。**人間の誤読検査合格、またはDによる新候補の独立合格という意味ではない**。
- #451は別の選択式試作で `PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`。#465旧結合候補を一括mergeしない。新CページにHOLDの転倒・旧法令付き服薬・#451への公開導線を増やさない。

## 3. exact-head CIと実装差分

**#491 C最終headのGitHub Actions run → job → stepをEが取得**し、次のjobと主要実行stepが `completed/success` であることを確認した。いずれもGitHub上の機械的検査である。

| Workflow | run / job | 対象stepと判定 |
| --- | --- | --- |
| Validate ops site | [38195128511](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38195128511) / `114635980529` | npm ci/test、browser setup、build、Chromium、route smoke（4–9）：success |
| Validate build | [38195128484](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38195128484) / `114636033121` | source inventory・metadata/build・production gate verifier compile・smoke（6–12）：success |
| Verify publication readiness integration | [38195128514](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38195128514) / `114635979901` | canonical regeneration・bounded publication（4–5）：success |

**#491の6ファイルとGit blob:** `page.tsx` `ab4da442aabfb66ced804fc533329cda525b19d4`、`sources.module.css` `d73eed84d71e66deba6f4327dc51a84b72609a10`、`playwright.config.mjs` `5d3b5f6692875df11d7ffcdb59f08dcfdc94518c`、`scripts/verify-routes.mjs` `71188bf90f4aa1245ce0a17920820385acd6f02d`、`tests/browser/official-source-guide.spec.mjs` `bec1a2dcebdc8ed018f28e57acb9456a59ed830a`、`tests/official-source-guide.test.mjs` `a064d3763ee5fcf464c484d1d3bb4431cbb833e4`。

**A#490の文書CI** build [38194598905](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38194598905) / job `114634387273`、readiness [38194598912](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38194598912) / `114634387187` 成功。**B#466** build [38194573831](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38194573831) / `114634362279`、readiness [38194573829](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38194573829) / `114634311262` 成功。**D#487** build [38194514569](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38194514569) / `114634136199`、readiness [38194514554](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38194514554) / `114634136029` 成功。これらはそれぞれの文書headのCIであり、Dによる#491最終版安全審査を意味しない。

既存の#482（3 workflow run `38088336714/38088336703/38088336705`）と#480（`38087881729/38087881820/38087881829`）は旧D§13で同一版 `PASS_LIMITED`。**両候補を合成した新headの3 CI・D差分受入はまだ存在しない**。#491の合成後・公開用guard変更後のheadにも現行CIを流用しない。

## 4. Human acceptance：審査票の準備と受入の区別

B§10.4〜§10.7に、**服薬改訂・転倒・新案内を別版で特定**する記入票がある。安全理解のR01–R07 / F01–F05 / G01–G08、Android Chrome native 200%・390px・キーボード・実スクリーンリーダー、G25/N24/R17および新資料の実PDF viewer deep link、実紙印刷を分け、審査者・役割・時刻・対象SHA/blob・判定・欠陥理由を残す設計。**PACK_READY（旧4資料の限定案内分）**だが、Aで新規採用された資料用のB最終文案と固定表示版は未完成。

| Human gate | #482 服薬 | #480 転倒 | #491 新案内 |
| --- | --- | --- | --- |
| 介護現場／事故リスク管理責任者（必要な医療・法務は適格者）の内容理解 | `NOT_RUN / NO_SIGNOFF` | `NOT_RUN / NO_SIGNOFF` | `NOT_RUN / NO_SIGNOFF` |
| Android native 200%、390px、keyboard、実スクリーンリーダー | `NOT_RUN` | `NOT_RUN` | `NOT_RUN` |
| G25/N24/R17等の対象PDF viewer `#page=` と実紙印刷 | `NOT_RUN` | `NOT_RUN` | `NOT_RUN` |

この状態はBの記入票とEに提示されたGitHub証拠の範囲についての判定である。**外部で審査が一切行われていないと断定しているのではなく、対象版に紐づく利用可能な署名記録を確認できない**。審査者の指名・承諾・安全な資料提供先は未確定、専門職への連絡や匿名外部preview開放は**未許可・未実施**。他試作#451のEX01/EX02/HU01を代用しない。

## 5. Eの4範囲別GO/HOLD

| 公開範囲 | 独立確認状態 | **E判定** | HOLD解除に欠ける条件 |
| --- | --- | --- | --- |
| ① **既存服薬ガイド改訂 #482** | D§13 `PASS_LIMITED`（旧固定head）。CI成功。旧法令節は候補から削除されているが**mainの既存公開版には残る** | **`RELEASE_HOLD`** | 版付き人手安全/実機/PDF・印刷受入。release直前の差分・3CI/D受入の再照合 |
| ② **転倒ガイド #480** | D§13 `PASS_LIMITED`（旧固定head）。CI成功。単独mergeでは旧服薬への導線リスク | **`PUBLIC_SOURCE_GUIDE_HOLD`** | 人手3ゲート、#482先行後の最新版mainと共有CSS・route/browser testの合成、新head CI・D差分受入 |
| ③ **公的資料案内 #491** | C最終head 3CI success。ただしA新資料はC未収載、B新原稿未確定、D§14はpreflightのみ | **`PUBLIC_SOURCE_GUIDE_HOLD`**（独立D最終受入不足） | A採否を反映したB最終文案、C新head、D新head独立負例・原典監査、実在の人手3ゲート、公開guard解除版のCI・再受入 |
| ④ **非医学的UI単独** | 専用UI-only PR/headなし。CSS等は①②に付属 | **`RELEASE_HOLD`** | 単独で意味のある変更・新head・CI・Dと該当する人手受入が成立する場合のみ。不要なPRは作らない |

**E release decision = `NO_GO`。** A/B/C/Dの成果とCIの一部成功は「審査準備・候補作成」であり、人手承認のない公開は認めない。**#482/#480/#491/#451/#465のアプリmerge、公開操作、feature flag/Analytics/registry変更、deploy-state更新を実施しない**。

## 6. 本番・経路・deploy-stateの現物確認

EがVercel APIで照合した **Kaigo Ops専用project** `prj_7kKmZkto1j9r9Z3otwccx05LAjTp` / alias `https://ops-site-pi.vercel.app/` は、production `READY` deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` に対応。deploymentのGitHub metadataは repo `Josh-Temple/kaigo-rules`、**runtime full SHA `ffd70abb5723e950a0a1036795f28da31614a1f3`**。本WaveのA/B/C/Dのdocs・draft head、およびEのdocs-only変更をruntimeとはみなさない。

GitHub `refs/heads/deploy-state/kaigo-ops` は **`e49e770a970e541d2ad95204ad277eca89a485d3`**。**Eでは据置き**。新コードmergeなし、新production deployment作成なし、新runtime外部HTTP/HTML/DOM確認 **`NOT_RUN`**、正式post-deploy verifier **`NOT_RUN`**、marker更新 **`NOT_RUN / UNCHANGED`**。既存旧runtimeの read-only HTTP probe [37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787) による15/15は**過去証拠**であり新候補の検証ではない。

次にGOが成立した場合のみ、基礎 **15 URL相当**（home＋5 Issue＋5 tool＝11、服薬＝1、#451 404＝1、robots/sitemap＝2）、転倒公開時 **+1**、新案内公開時 **+1** で **15/16/17** と計数する。HOLDの転倒・新案内404は別負例。canonical/OG、直接原典URL、HTML/DOM冒頭注意、home・sitemap、print、privacy・Analytics不変、source guideの公開guardを**新しいruntime**で確認。さらに正式契約（`docs/kaigo-ops/deployment-assurance.md`、`.github/workflows/daily-vercel-production-deploy.yml`、`scripts/verify_kaigo_ops_production.py`）の**同一post-deploy verifier run**で expected exact SHA、project/repo、READY、alias、既存11ルートのHTTP 200/HTMLを実証したときだけ、forceせずmarker更新可能。secret不足なら `BLOCKED`。

## 7. 次のowner、順番、今回の作業境界

1. **B（最優先の文書残件）:** A#490§10の採用原典の正しいURL・2018/2019原指針・2026概要資料の位置付けに一致する新資料カード文言を#466へ限定追補し、固定blobと必要な新ケースを受入票へ反映する。追加指針を「介護職が処方を調整する手順」としない。既存14引用ブロックは維持。
2. **C:** B確定案に伴う新案内#491を最小修正して新head・差分・6ファイルblob・3CIを再固定する。非公開guardを維持し、HOLD旧記事や#451への導線を作らない。別途、将来#482先行後の#480安全合成を準備するが、公開は行わない。
3. **D（独立再受入）:** §14のpreflightを最終受入とせず、更新後のA/B/C同一版を独立再取得し、新資料の同一性・版・適用範囲、N01–N08、内容表示・アプリroute・新3CIを監査する。変更がなければ#482/#480の旧§13は不変blob範囲だけ再利用。
4. **実在の審査者／E:** 版を固定した受入票に対し、介護現場・事故リスク管理責任者の内容確認、必要な医療・法務の適格者確認、Android native 200%・実読み上げ、PDF viewer/実紙印刷を行い、実施者/役割/日時/SHA/blob/結果を記録。**現時点では審査依頼・外部送付を行わず、実施者の指名と提供方法について人間側の明示判断を待つ**。
5. **E:** 実在の3人手ゲート・同一版D受入・対象CIが揃った範囲だけ再判定。原則#482（法律節削除）→#480（共有ファイルの合成と独立D/CI再受入）→#491（独立公開guard解除版の再受入）の順。GOに至った場合にのみmerge・専用Vercel・外部HTML/DOM・正式verifierを順次実行する。

**本WaveのE成果:** 4範囲の公開HOLD条件を固定し、最新の候補・CI・旧productionを分離した。A#490/D#487は**Draft PRのまま**であり、Aの文書のみmergeを試した際はGitHubがDraft状態を理由に405を返したため、レビュー状態を変更せず統合もしていない。B#466、C#491/#482/#480もDraftを維持。本判断文書のGitHubへの保存・CI・main読戻しは、別途GitHub実績に基づき確認する。**判定文書のmergeはガイド記事のreleaseではない**。
