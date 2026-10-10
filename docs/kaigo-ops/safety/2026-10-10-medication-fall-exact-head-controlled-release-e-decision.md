# Kaigo Ops — 2026-10-10 E統合判定：服薬・転倒出典ガイドの同一版安全審査と公開ゲート

**Library指示書**: `/Kaigo Ops/Work Instructions/2026-10-10_medication_and_fall_source_guides_exact_head_safety_review_and_controlled_release_wave_instructions.md`。  
**対象**: `Josh-Temple/kaigo-rules`、`ops-site/`、Kaigo Ops専用Vercel project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`。  
**判定**: **PARTIAL_WITH_GAPS**。旧E記録は統合、新しい医療・法令の文章改訂と転倒・転落記事は公開保留。未実測はPASSに読み替えない。

## 1. 前Wave記録を閉鎖した事実

- 実行開始main `6c170418cbc178c7efebc32e76c46b8cbf4c3b32`。前Wave [PR #473](https://github.com/Josh-Temple/kaigo-rules/pull/473) head `30ba214ad9bee2418b32e1b095f90e46a3886115`、変更は`docs/kaigo-ops/CURRENT.md`、`ops-site/README.md`、前Wave E判定文書の**3ファイルのみ**。PR #473の同じheadでGitHub Actions `Validate ops site` [37993616408](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993616408)、`Validate build` [37993616402](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993616402)、`Verify publication readiness integration` [37993616341](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993616341)が各success。PRはmergeable、非draft。
- #473をsquash mergeし、main commit **`582792f64879477f8773dce450fff925d872fcb2`**。mainのbranch SHAおよび前Wave E判定ファイル、CURRENT、READMEをGitHubから再取得。**MERGED_READBACK**。これは文書統合であって新しい安全記事の承認・本番配信ではない。
- read-only外部HTTP probe [#472](https://github.com/Josh-Temple/kaigo-rules/pull/472)は既にmain統合済み（merge SHA `6c170418cbc178c7efebc32e76c46b8cbf4c3b32`）。旧productionに対する[run 37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787)の15/15期待HTTP結果は**過去の測定**として保持する。

## 2. 現時点のA→B→C→D実体と独立性

| 所有者 | GitHub実体と観測 | E判定への意味 |
| --- | --- | --- |
| A | main統合[#470](https://github.com/Josh-Temple/kaigo-rules/pull/470)、台帳blob `7f373c396f9358e0179021f09d95cb2698ce9b1f`。追加[#474](https://github.com/Josh-Temple/kaigo-rules/pull/474)はopen・未merge・head `650bb9bdf3522f263c03d410ccd051468eada922`。#474はB旧head `5df748a...` / 旧blob `16915a...`を参照。 | 主張・出典は限定評価。B最終更新への再照合と#474のmergeability解決が残る。 |
| B | [#466](https://github.com/Josh-Temple/kaigo-rules/pull/466) draft/open head `97389ce1538978abadcf4e2618493b7258995f27`、最終編集稿blob `1394df30751e408e997524e431a99bf696e52fe9`。文書のbuild/publication-readiness CIはsuccess。 | MED-A01〜08、FALL-01〜03とF-01〜04を結び、掲載予定文章を固定。編集上のPASS_LIMITED≠医療/法令安全承認。 |
| C | [#465](https://github.com/Josh-Temple/kaigo-rules/pull/465) open・未merge head **`ef12b659bc9fca43df4c7ebd15b9cf5471dbcecd`**、8 changed paths。服薬ページblob `f3415366187b47c8a6a93a378f3f223e0971d181`、新転倒ページblob `de66e2dfcb0985864be230049ecea44612fd3b05`、C対応表blob `3ce16c69c89af5f471ae116947cb147c033b3cf4`。 | B最終版を参照した表示・新記事の実装候補は**存在する**。未統合であり公開済みとは呼ばない。 |
| C exact CI | 上記C headで[ops 38007012548](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012548)、[build 38007012580](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012580)、[publication 38007012539](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012539)がsuccess。ops job `114078018376`のnpm ci/test/build・Chromium・route smokeの各stepもsuccessを照合。 | CODE_HEAD/CIは成立。ただし独立D監査・実Android・実本番の証拠ではない。 |
| D | [#475](https://github.com/Josh-Temple/kaigo-rules/pull/475) open・未merge head `300b4ad53b14f1483539f0b36e5047ba31eb6c9f`、監査台帳blob `e5b86536e7e78fba797f324adfc90662e70c5f5b`、文書2CIはsuccess。**検査対象C headは旧`77eb4b391ac722adc1a34024e6c7a33b35179949`、Bも旧`5df748a...`**。 | D結論の旧服薬改訂BLOCKED／転倒ページBLOCKEDは**旧対象版の記録**。新C headを未監査のままPASSとみなせない。 |
| 試作 | [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) draft/open/unmerged。 | **PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED**を維持。 |

**独立ゲート未達**：D #475はC新記事が「存在しない」旧headを審査している。その後Cが新ページと服薬P1文面を実装したため、#475のBLOCKEDを「最新版も未実装」という事実に流用せず、**最新版の安全判定は未実施**と記録する。A #474も最新版B blobより古い参照であり、同一版chainを構成しない。Aのsource support、Bの確定文章、Cのgreen CI、旧D判定を足してGOにしない。

## 3. 主張ごとの変更候補・出典境界・現行本番との差

- **MED-A01/A08**：C候補は既存服薬記事のlead直後に「実際に事故が起きている場合は閲覧より本人の安全確保・正式手順・必要な医療職等を優先」を新設。main既存ページblob `782a1f53c635997817faf46bfe2f4e63721482c2` にはこの位置の強い注意文は**ない**。G25ガイドラインは施設中心。
- **MED-A02/03/06**：2017年高齢者向け住まい研究の推奨とPMDAの一般相談案内、施設事例の適用範囲を制限。研究の受診推奨を全国共通法的義務、PMDAを個別診断、施設工程を全事業所の規範と説明しない。既存本文にも限定注記はあるが、CがBの最終文面へ更新した箇所の同一版D監査がない。
- **MED-A04/A05 / X-02**：C候補は2024年Vol.1332の「原則報告対象の事故」「別紙共通様式の主な対象サービス」「5日以内という初報目安」「自治体別運用」の区別を報告節で具体化し、PDF通し3頁と4頁を近接リンク。全国一律の法定期限、全サービス同一の様式対象・報告義務とは扱わない。
- **MED-A07**：本番の旧見出し「重大な結果と注意義務違反があれば…」をC候補で「服薬の間違いだけで、刑事責任が決まるわけではありません。」へ変更。個別犯罪・過失をサイトが判定しない。**刑法211条の該当施行版正式全文の原文直読はA/Dとも `NOT_ESTABLISHED`**。e-Govの動的画面や検索抜粋を全文照合済みとは呼ばない。
- **FALL-01/02/03＋MED-A04/05**：C候補の新route `/guides/fall-prevention-sources` はG25ガイドライン冊子30・32頁／PDF通し33・35頁に対応する、本人と環境／尊厳・過度な行動制限／ベッド周辺の視点、およびN24通知の対象・様式・5日目安を説明。施設中心の適用範囲を明記し、ベッド柵やセンサー設定、個別身体拘束合法性、診断・受診・搬送、過失一律、効果率を掲載しない構成。**Cの実装候補は検査したが、Dによるこの版の独立評価・公開GOはない。**
- A採否/B文面/C TSXの完全な逐語照合と12危険誤読（従来7＋転倒5）を**最新版のDが再実行するまで不成立**。PDF `#page`の実ブラウザ・PDFビューアの動作もNOT_RUN。自治体個別運用はNOT_ESTABLISHED。
- 出典はMHLW 2025 Vol.1436／2024 Vol.1332、MHLW掲載2017年研究、PMDA、e-Gov刑法。文書種別と対象を混同しない。D #475に記録された過去の独立原典閲覧を、新版Cの独立表示監査と取り違えない。

## 4. 変更範囲別E公開判定

| 範囲 | 判定 | 理由と解放条件 |
| --- | --- | --- |
| 前Wave #473文書だけ | **MERGED_READBACK** | 文書3ファイル、3CI成功、main `582792f64879477f8773dce450fff925d872fcb2`でreadback。 |
| 既存服薬記事P1本文差替え | **RELEASE_HOLD** | C最新版には候補あり。A #474とB最新版の整合を確認し、**C `ef12b...`または後続の最終exact headのD独立再監査**を完了する。刑法正文・自治体ルールのNOT_ESTABLISHEDを保持。 |
| 転倒・転落静的1ページ | **PUBLIC_SOURCE_GUIDE_HOLD** | C最新版にroute/page/SEO/testsあり。D #475は存在前のheadを監査。新記事のFALL/N24表示全段落・12危険誤読・16対象URLの機械回帰を最新版Dで再確認する。 |
| 目次・直リンク・印刷・アクセシビリティUI | **RELEASE_HOLD** | D #475のUI部分的PASSは旧3ファイルのC headに限る。今回8ファイルのC PRからUIだけを安全に分離していないため、**全PRを先行mergeしない**。 |
| 異食 | **PUBLIC_SOURCE_GUIDE_HOLD** | B/C今回の掲載対象外。 |
| 誤嚥・窒息 | **PUBLIC_SOURCE_GUIDE_HOLD** | 個別の食事・処置判断への誤読リスク、今回の掲載対象外。 |
| 選択式安全試作 #451 | **PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED** | flag有効化・公開・レビュー依頼なし。EX01/EX02 = NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE、HU01 = HUMAN_APPROVAL_NOT_DONE。 |

**Wave総合：PARTIAL_WITH_GAPS**。コンテンツ本番マージなし。前Wave文書だけ確定。

## 5. Vercel・外部HTTP・ブラウザ・deploy-state

- Kaigo Ops専用project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`のproduction一覧とaliasのVercel再取得で、本番alias `ops-site-pi.vercel.app` は既存deployment **`dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`** を指す。target=production、state=READY、接続repo `Josh-Temple/kaigo-rules`、**runtime SHA `ffd70abb5723e950a0a1036795f28da31614a1f3`**。#473 docs main SHAとruntimeは別。
- [run 37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787)の旧runtime外部HTTP **15/15**＝home+5 Issue+5 tool 11件200、既存服薬ガイド200、試作404、robots/sitemap各200を過去証拠として継承。HTTPと静的HTML shell・canonical/OG/source anchorのproxy検査であって、**新しい16対象URLの検証ではない**。
- Cをmainにマージしていないため**新しいC runtime/deploymentは作成も照合もしていない**。今回の新productionに対する判定 **PRODUCTION_NOT_VERIFIED**。新routeはproduction公開済みとしない。外部原典PDFの最新HTTP/ディープリンクを各環境で開けることも今回未実測。React hydrated DOMと実人間閲覧はNOT_RUN。
- CのGitHub Actions上のheadless/Chromium、390px proxy、CSS 200% proxy、印刷CSSは**機械検査**。実Android Chrome、native 200%、スクリーンリーダー実聴、実印刷プレビュー・紙、productionの実ブラウザ操作：すべて**NOT_RUN**。未検査の性能や事故予防効果を断定しない。
- `deploy-state/kaigo-ops` ref **`e49e770a970e541d2ad95204ad277eca89a485d3`** をAPI確認し、更新しない。`docs/kaigo-ops/deployment-assurance.md` contractの、hook request開始以後の新deployment・exact expected Git SHA・READY・正しいalias・既存11 routeのHTTP/HTML shellを同一post-deploy runで確認する条件を欠く。旧read-only probeやC PR CIによる前進は**不可**。
- 公開5 Issue/5 tool、Issue 6候補、Analytics event schema、個人・事故入力、サイトの認証/flag、Kaigo Rules別projectを変更しない。

## 6. 次の実行順序とreadback

1. **A**：[#474](https://github.com/Josh-Temple/kaigo-rules/pull/474)のmergeabilityを検証し、**B最終head `97389ce...`／blob `1394df...`**と§7 crosswalkを再照合。MED/FALL採否、L211/自治体NOT_ESTABLISHEDを明記。Aが改訂したらB/Cへ差分通知。
2. **B/C**：Aが許容するB文章・C実装を最終固定。変更が出れば最新headで再CI。C PR #465を安全本文・転倒・非医学UIで別々に公開できる単位へ切り分けるか、全体を監査対象に固定する。
3. **D**：**C head `ef12b...`以降の最新head＋med blob `f3415...`＋fall blob `de66e...`＋B `1394df...`＋A最終blob**に対して出典・表示・12危険誤読・SEO・privacy・flag/旧11/新route/試作404・exact head CIを独立再評価。旧D `77eb...`の結論を転用しない。範囲別PASS_LIMITED/PARTIAL/BLOCKEDを記録。
4. **E**：全gateを見直し、証拠が揃う範囲だけマージ。新release実施時のみVercel専用projectの新deployment ID、runtime SHA、READY、alias切替、外部16 URL HTTP/DOM、可能な実ブラウザを測定。正式deployment contractを満たした時のみmarkerを進める。
5. このE decisionとCURRENT/READMEは**別docs-only PR**としてmain統合後にreadbackする。PR登録・CI・merge・最終main SHAはGitHubの確定値で検査し、予定値を成功値と呼ばない。

**判定の核**：新C実装とCIは前進したが、Dの同一版安全監査と新production実測が欠ける。ユーザー保護を優先し、今回新しい事故防止記事を公開しない。
