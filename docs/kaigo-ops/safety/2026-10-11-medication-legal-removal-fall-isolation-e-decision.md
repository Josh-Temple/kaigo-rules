# Kaigo Ops — 2026-10-11 E統合判定：刑法節除外・転倒独立候補・公開ゲート

**Wave**: /Kaigo Ops/Work Instructions/2026-10-11_medication_legal_section_resolution_fall_guide_isolation_independent_reacceptance_and_conditional_release_wave_instructions.md  
**E判定**: **PARTIAL_WITH_GAPS / ALL THREE SCOPES HOLD**  
**checked_at**: 2026-10-11 JST（GitHub PR・commits・files・Actions・Vercel APIのread-only照合）  
**判定基準main**: ac5f6b356a389c395c23e2b88041d55bf4b3dace（A #481・D #479をdocs-only統合後。アプリのruntime SHAではない）  
**前判定**: docs/kaigo-ops/safety/2026-10-11-medication-fall-final-tuple-scoped-release-e-decision.md（#478、main統合済み）  
**独立監査正本**: docs/kaigo-ops/safety/2026-10-09-public-source-guides-worker-d-independent-audit.md §11・§12

## 1. 進展と正本統合（アプリ公開とは区別）

- 前E #478は既にmain統合済み。前D #475の§11は、旧結合C #465 head b33f8b166628f7c06fb96cc7ccac95a579e24434について12危険誤読中11 PASS_LIMITED、R04 BLOCKEDだった。この旧判定を新PRに流用しない。
- A #481 は原典台帳の§9だけを追加。head ca26522b19128988db2f854429d6808856fc516c、blob 576e52f0be9266884c62eccd215afac8d669f29f。Validate build run 38087897212 job 114318146229、publication readiness run 38087897196 job 114318145707、ともにcompleted/success（steps success）。1 docs path、mergeable確認後、merge SHA **c89bd2a68e60fdfffff3a70893915b407df58a27**。mainに同blobをreadback。
- D #479 は**候補PR作成前**に記録したpreflight §12のみ。head 6c0bcf7216caa03a48e3cba52f5ed126edf5920f、台帳blob 7357b57a8d2b5a1e963a426959398a5a29d6d43c。Validate build run 38087865643 job 114318098655、publication readiness run 38087865614 job 114318061643、ともにcompleted/success（steps success）。1 docs path、mergeability確認後、merge SHA **ac5f6b356a389c395c23e2b88041d55bf4b3dace**、mainで同blob readback。§12には新C #480/#482の受入は**一切ない**。この文書統合は独立再受入ではない。
- B #466 は open/draft、head 88721568ea0266862986a1587e149f1ff57ef19b、編集稿blob ab07897b9dce2795b602b50ab49b0132f60bc1fa、§9が最新指示。刑法節を新掲載候補から除外し、非法令の引用ブロック合計14（服薬7＋転倒7）とする。A §9が保存後B版を照合して MED-A07 REMOVE_FROM_NEW_PUBLICATION_CANDIDATE を採用。Aはe-Gov公式ページにおける候補施行版2026-05-21の第211条2文を確認したと記録する一方、公式API内部オブジェクト・hash独立抽出はNOT_RUN、個別責任・適用日の法的判断はNOT_ESTABLISHED。**法的節を削除する方針と、同一実装版のD独立受入は別ゲート**。

## 2. 3公開範囲の固定候補と判定

| 範囲 | 最新候補・実diff / GitHub Actions | Dの新候補exact-head受入 | E判定 |
| --- | --- | --- | --- |
| 服薬記事改訂 | C **draft #482** head **6c64af5924da24ea89a147ad9d42c7f1155c3f45**、main起点4 paths（服薬TSX / CSS / route verifier / browser spec）。服薬TSX blob **8f9876db7dfc81d232e04d3f250b5e115232b540**。旧法令節・目次anchor・e-Gov source・metadata法令記述の負例除去を確認。転倒page・home・sitemapは含まない。CI run 38088336714 (ops job 114319441078)、38088336703 (build job 114319453112)、38088336705 (readiness job 114319441087)：**全completed/success、steps success**。 | **NOT_ESTABLISHED**。D §12はこのPR以前のもの。新削除版のR04、他の変更範囲、出典リンク・可読性・旧11route/#451・privacyの独立審査がない。 | **RELEASE_HOLD** |
| 転倒・転落静的出典記事 | C **draft #480** head **b5b73e46e0217ff8ec689c9984d6b837cd7d92cc**、main起点6 paths（fall TSX / home / sitemap / CSS / route verifier / browser spec）。fall TSX blob **de66e2dfcb0985864be230049ecea44612fd3b05**。服薬TSXはmainと**同一blob 782a1f53c635997817faf46bfe2f4e63721482c2**。CI run 38087881729 (ops job 114318106632)、38087881820 (build job 114318107552)、38087881829 (readiness job 114318106839)：**全completed/success、steps success**。 | **NOT_ESTABLISHED**。旧#465のF01–F05 PASS_LIMITEDは新独立headへのD受入ではない。shared CSSと既存服薬link、新導線/SEO/16 URLs相当を含め独立審査が必要。 | **PUBLIC_SOURCE_GUIDE_HOLD** |
| 非医学的UI | #480のCSS/home/sitemap/route/testは転倒記事に結合、#482のCSS/testは服薬改訂と結合。独立したUI-only PR/headなし。 | **NOT_ESTABLISHED** | **RELEASE_HOLD** |

**共通の限界**: GitHub Actionsのnpm ci/test/build、Chromium、五つの既存tool操作、route smoke successは確定したが、これは機械的CIでありDの別主体監査・外部production・実機・人間の理解確認の代用ではない。#482は先行headのroute smoke失敗後、正しい削除仕様へverifierを更新した最新headに対するCI successを確認。過去headのsuccessを転用しない。

**新旧法令節の重要な境界**: #480は既存の公開服薬TSXを完全に維持している。その**既存main版にも旧#law/刑法211条への記載が残る**。#480のみ公開しても、サイト全体の法令記載を削除したことにはならない。#482の修正済み服薬TSXには該当法律文面・anchorがないことをコード文字列で確認したが、これは本番表示確認ではない。

**HOLD混入防止**: 元C #465（8 changed paths、未merged）を一括統合しない。#480は服薬改訂を含まず、#482は転倒記事・home/sitemap掲載を含まないことをそれぞれPR差分で確認。両者とも独立D受入とE GOが必要。#451（open/draft、head 2dd0e260d0922e18d003905f4a7edf42560f640c）は PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED のままであり、EX01/EX02/HU01を静的記事の自動GOと取り違えない。

## 3. 出典・人手・安全の残余とGO条件

- G25は主に介護保険施設向け、R17は高齢者向け住まい研究、PMDAは一般相談、N24は事故報告対象・報告初報5日目安・標準様式対象を**別の範囲**として扱う。自治体ごとの報告要否・期限はNOT_ESTABLISHED。具体的な薬剤・患者・受診・搬送・再投与・医療・身体拘束・刑事責任の個別判断を新記事に導入しない。
- Android Chrome native 200%、実スクリーンリーダー聴取、紙印刷、PDF viewer #page遷移、人間による危険な誤読／説明文の受入、実在専門職レビューは**NOT_RUN**。CSS zoom/headless printだけでPASSとしない。
- **今回は独立Dゲート未成立のため公開不可**。次のEでGOを検討する際、出典直リンクと緊急時注意・読者の誤認リスクについて人手の文面・アクセシビリティ確認を原則要求する。未実施のまま限定公開を例外的に認める場合は、対象・残存リスク・責任者の明示的な受容理由をE文書に記す。現状ではそのような例外承認もない。
- Dは新候補それぞれの**exact head**に対して、服薬R04の実削除、転倒F01–F05、shared CSS、11旧routeと既存服薬、15/16 URL相当、sitemap/robots/canonical/OG、#451 404、privacy/新Analytics無しと出典原文／B最終稿／rendered evidenceを独立確認する必要がある。CIによる自己証明をD受入としない。
- #480/#482の現行headとD受入が成立するまで、コードPRを**mergeしない**。後続コミットやmain更新があれば再度head・base・変更パス・CI・D受入を照合する。共通CSSの両候補併合時には別の差分検証を要する。

## 4. production / formal deploy-state：今回の実測と未実施を区別

**コードのmain統合なし、production新deployなし、alias切替なし、post-deploy verifierなし。** Vercel APIをread-only取得し、専用project **prj_7kKmZkto1j9r9Z3otwccx05LAjTp**、alias **ops-site-pi.vercel.app** が deployment **dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu** に対応し、同deploymentは **target=production / READY**、repo **Josh-Temple/kaigo-rules**、**runtime exact SHA ffd70abb5723e950a0a1036795f28da31614a1f3** であることを独立確認。docs-only main ac5f6b3...はruntimeではない。これは**既存公開状態の再確認**であって今回の新アプリ公開ではない。

正式marker **refs/heads/deploy-state/kaigo-ops = e49e770a970e541d2ad95204ad277eca89a485d3**をGitHub ref APIでreadback、**UNCHANGED**。過去の旧runtimeに対する15/15 HTTP試験を新分離版の試験に流用しない。**新production HTTP/HTML/DOM = NOT_RUN**、実Android・読み上げ・印刷・PDF viewer = NOT_RUN。新deploymentが存在しないため15/16 URLの新規production受入やmarker fast-forwardの条件は未成立。secret・deploy-stateに手を触れない。

## 5. 次のownerと再開条件

1. **D**：#480 head b5b73e...、#482 head 6c64af...を**別々に**原典/B最新版/コード/CIと突合し、既存D台帳に変更点だけ追加。各範囲のPASS_LIMITED/PARTIAL/BLOCKEDとGOに必要な人手条件を明記。前§12 preflightを新審査と誤称しない。
2. **A/B**：B #466 draftの最新blobに実質更新があった時だけA再照合。法律節の削除判断は固定済みであり、同じ出典探索を繰り返さない。
3. **C**：Dが具体的に指摘した不具合だけ独立PRに修正し、headが変われば3CI・D再受入を更新。UI-onlyの有意義な分離差分がなければ新PRを増やさない。
4. **E**：D再受入が各候補の現在headと一致した場合に限り、独立GO/HOLDと人手例外の有無を判定。GOのみmain merge→新Vercel deploymentのexact SHA/READY/alias→外部15/16 URL HTTP/HTML・DOM→正式post-deploy verifier契約確認。いずれか不足ならHOLD、marker据置き。

**本Waveの統合判定作業は終了。公開作業は未完了。** 主な新規阻害条件は「新しく独立したコード2候補へのD exact-head再受入が存在しない」。旧R04の出典未確立だけを理由に現在の削除版を評価せず、実装差分に対する検証で再判定する。
