# Kaigo Ops — 服薬・転倒独立候補の同一版D受入後 E統合判定（2026-10-11）

**判定日:** 2026-10-11 JST  
**Wave:** `/Kaigo Ops/Work Instructions/2026-10-11_medication_fall_isolated_exact_head_independent_acceptance_scoped_release_and_production_verification_wave_instructions.md` §7  
**判定:** `PARTIAL_WITH_GAPS / NO_GO / ALL THREE SCOPES HOLD`  
**対象:** 既存服薬事故の静的出典ガイド改訂、施設中心の転倒・転落静的出典ガイド追加、非医学的UI単独のrelease。選択式試作 #451 は対象外・非公開。  
**このファイル:** Eの公開判断・人手ゲートの記録であり、未実施の審査またはdeploymentの実行証明ではない。

## 1. Eが直接確認した固定版とD文書統合

| 項目 | 実取得・確認した版 | 意味 |
| --- | --- | --- |
| E開始時main | `254b0aecdc8708f1de6c5359615295b82bf3f4be` | 前E #483のdocs-only統合済み。app runtimeとは別 |
| 前E判定 | `docs/kaigo-ops/safety/2026-10-11-medication-legal-removal-fall-isolation-e-decision.md` | 服薬・転倒・UIすべてHOLD、当時は新C候補のD受入なし |
| A出典台帳 §9 | main blob `576e52f0be9266884c62eccd215afac8d669f29f` | MED-A07は法律節を新候補から削除、その他の公的出典と適用範囲を維持 |
| B編集稿 §9 | #466 `open/draft`、head `88721568ea0266862986a1587e149f1ff57ef19b`、blob `ab07897b9dce2795b602b50ab49b0132f60bc1fa` | 服薬7・転倒7の非法令引用ブロック。文書draftは公開承認ではない |
| C転倒のみ | #480 `open/draft`、head `b5b73e46e0217ff8ec689c9984d6b837cd7d92cc`、変更6パス | fall `de66e2dfcb0985864be230049ecea44612fd3b05`。home/sitemap/CSS/route/browserを含む。服薬TSXはmainと同一blob `782a1f53c635997817faf46bfe2f4e63721482c2` |
| C服薬のみ | #482 `open/draft`、head `6c64af5924da24ea89a147ad9d42c7f1155c3f45`、変更4パス | medication `8f9876db7dfc81d232e04d3f250b5e115232b540`。旧刑法節・anchor・metadata・e-Gov sourceなし。fall新route/home/sitemap変更なし |
| D独立監査 §13 | #484 head `4972e01591d6c7441a95dd3e3f966c587955aace`、D台帳blob `0f00f2c344f34c36af52e20ea54b4ae733770c6c` | Dが#480/#482の別々のexact headに限定してR01–R07、F01–F05と変更・CIを受入。2範囲 `PASS_LIMITED`、UI単独 `PARTIAL_WITH_GAPS` |
| D文書統合 | PR #484 `merged`、merge SHA `10e26cb3b7cdc016a6dce7eb30d9e8689a9bd99c`、mainのD台帳blob `0f00f2c344f34c36af52e20ea54b4ae733770c6c` をreadback | 変更は監査台帳1文書のみ。**アプリやガイドの公開ではない** |
| 旧#465 / #451 | #465 head `b33f8b166628f7c06fb96cc7ccac95a579e24434` 未統合、#451 head `2dd0e260d0922e18d003905f4a7edf42560f640c` `open/draft` | #465一括merge禁止。#451 `PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED` |

両C候補の元のmerge-baseは `6346300ce6300714646b588c08159f075987b32f`。Dが確認した当時のmainは `254b0aec...` で、現在のmainにはD docs-only mergeが入った。**Dの候補別安全受入は、確認済みcandidate code/test blobが不変であるという限定内のみ**。公開直前にはbase・head・差分・CI・後続変更を改めて照合する。B draftの存在やD `PASS_LIMITED`を人の承認と取り違えない。

## 2. CIのrun/job/step照合（候補別）

GitHub Actionsのworkflow run → job → stepをE自身が再取得。以下の全jobは `completed / success`、該当stepsも `success`。いずれも候補headの機械テストであり、実際の公開・人間の評価ではない。

| 対象 | Workflow | run / job |
| --- | --- | --- |
| #480 `b5b73e46...` | Validate ops site | [38087881729](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38087881729) / `114318106632` |
| #480 | Validate build | [38087881820](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38087881820) / `114318107552` |
| #480 | Verify publication readiness integration | [38087881829](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38087881829) / `114318106839` |
| #482 `6c64af592...` | Validate ops site | [38088336714](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38088336714) / `114319441078` |
| #482 | Validate build | [38088336703](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38088336703) / `114319453112` |
| #482 | Verify publication readiness integration | [38088336705](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38088336705) / `114319441087` |
| D #484 docs-only head | Validate build | [38111090392](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38111090392) / `114386629668` |
| D #484 docs-only head | Verify publication readiness integration | [38111090345](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38111090345) / `114386629456` |

D自身の別実行npm/Playwright、DOM独立実行と、E自身の候補ブラウザ実行は `NOT_RUN`。**2候補の変更を合成したheadのCIは未実施**。共通CSSは同blob `f2a43acf8f062560db9fbf3aa2fffc31e684ed58`、route verifier・browser specは両候補で**異なるblob**。1件の旧base headの成功を、2件の合成版に転用しない。

## 3. Eの範囲別release判断

| 範囲 | D候補別受入 | E判定 | releaseを止める理由 |
| --- | --- | --- | --- |
| ① **既存服薬ガイド改訂** #482 | `PASS_LIMITED`。R04は「候補から法律節が消えた」範囲で限定確認、R01–R07の出典と意味も限定受入 | **`RELEASE_HOLD`** | 人による安全な読解・専門職／事故リスク責任者の確認、native 200%・screen readerなどの実機、出典PDF viewer・実印刷が未実施。#482自体は未merge。旧mainには法律節がまだ残る |
| ② **転倒・転落の静的出典ガイド** #480 | `PASS_LIMITED`。F01–F05と施設向け適用・N24の報告対象／5日目安／様式対象を限定確認 | **`PUBLIC_SOURCE_GUIDE_HOLD`** | 同じ人手・実機確認不足。#480だけを統合すると旧main服薬の法律節が残り、fall→medicationリンクから到達する。残留法令リスクを新しい案内で拡大させない |
| ③ **非医学的UI単独** | `PARTIAL_WITH_GAPS`。専用UI-only実体・head・独立CI・D受入なし | **`RELEASE_HOLD`** | 独立して公開する差分が存在しない。UIは①②の記事と従属して管理。無理な新PRは作らない |

**総合 `PARTIAL_WITH_GAPS / NO_GO`**。Dのexact-head独立受入は達成したが、公開に必要な人手ゲート・合成版ゲート・新production実証は未達。#465の一括merge、#480/#482のアプリmerge、強制deploy、deploy-state marker変更はいずれも実施しない。

### 人手確認に関するEの公開条件（今回新たに明示）

安全に関わる静的出典ガイドであり、読者が現場対応・報告義務・身体拘束・刑事責任を誤解すると実害につながり得る。このため**本Waveで①②を公開する際は、次をすべて必須のpre-release acceptanceとする**。AI・CIの確認、またはChatGPTユーザーの一般的な本作業依頼を、これらの承認と読み替えない。

1. **人間の安全内容受入：** 指名された介護現場／事故リスク管理責任者（必要な医療・法務判断は適切な専門職）による、実際に公開する本文の版番号付き確認。R01–R07/F01–F05のうち該当ケース、事故時は記事より正式手順を優先すること、施設中心の適用範囲、N24の国通知と自治体個別取扱いの区別、本文の危険な読み違い、既存服薬の旧法令節への導線を扱い、承認者・日時・対象exact SHA・判定を記録する。**今回 `NOT_RUN / NO_SIGNOFF`**。
2. **実際のアクセシビリティ受入：** Android Chromeでnative 200%表示と390px相当、キーボード・焦点移動、実スクリーンリーダーで緊急時の注意／見出し／引用・出典リンクの読み順と理解可能性を人が確認し、端末・版・結果・欠陥を記録。headless CSS zoom=2 proxyは代替しない。**`NOT_RUN`**。
3. **出典の利用可能性受入：** リンク先PDFを実際の対象ブラウザ・PDF viewerで開き、少なくとも重要な `#page=2/3/4/28/33/35/41/57` の該当箇所へ到達できるか確認。deep-linkが機種依存で動かない場合、ページ番号を本文に明記し代替動線を人が確認する。紙への実印刷でリード直後の注意と原典URLが失われないことも確認。**`NOT_RUN`**。

この3条件を満たしていない現在は限定GOを選択しない。例外受容の責任者・書面・代替検査証拠も存在しないため、架空のリスク受容は登録しない。#451試作のEX01/EX02/HU01を静的ガイドの人手受入として転用しない。

## 4. 本番・正式markerの現時点の実証と非実施

- EがVercelから再取得した専用project: `kaigo-ops` / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`。alias `ops-site-pi.vercel.app` はdeployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu` を指し、`target=production` / `READY`。repo `Josh-Temple/kaigo-rules`、**runtime exact SHA** `ffd70abb5723e950a0a1036795f28da31614a1f3`。deployment aliases APIも該当aliasを返した。
- GitHubの正式 `deploy-state/kaigo-ops` refを再取得：`e49e770a970e541d2ad95204ad277eca89a485d3`。**`UNCHANGED`**。docs-only mergeをruntime更新と扱わない。
- **本Waveではアプリのコードmergeなし**。したがって新production deployment `NOT_CREATED`、新runtime exact SHA／新alias割当 `NOT_APPLICABLE`、新15/16件の外部HTTP/HTML・headless DOM `NOT_RUN`、正式post-deploy verifier `NOT_RUN`。以前の15/15は**旧runtimeの履歴**。同一の正式検証runがないためmarkerを更新しない。
- 次に新runtimeをreleaseするときの必要確認：home+5 Issue+5 tool=11件を200/HTML、服薬200、#451 404、robots/sitemap各200、転倒GO時は転倒200を追加し**基本16件**（服薬のみは**基本15件**）。転倒HOLDなら追加の転倒404負例は基本15件と別計数。canonical/OG、原典、相互導線、privacy、実DOMを新deployment・同aliasで照合。deploy hook開始後の新deployment、expected exact SHA、READY、repo/project/alias、既存11 routeの200/HTMLを**同一の正式post-deploy verifier run**で立証しなければmarkerを進めない。secret不足時は`BLOCKED`。
- #451は`open/draft / PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`。EX01/EX02未依頼、HU01未承認。公開registry・新Analytics・個人／事故／薬剤入力・flag変更は本Eで行わない。異食、誤嚥・窒息の公開も対象外。

## 5. 次の実行主体と解除条件

**Human（まず最優先）：** ①②それぞれの固定本文への人手安全受入、実機アクセシビリティ、PDFビューア、紙印刷の実測。承認者と対象版、問題・修復を追跡できる受入票を残す。未実施をPASSにしない。

**C（必要な場合のみ）：** 人手で具体的修正が指摘された場合、既存#482/#480に最小修正し、新headの3 CI→D該当差分再受入。A/Bの出典・文意への影響がない場合、A/Bは`NO_CHANGE`。変更があれば担当範囲で最小再審査。

**Eのrelease順序：** 安全な候補と人手ゲートが成立すれば、原則#482（旧法令節の除去）を先に個別公開判断する。次に#480のfall→服薬導線を更新後mainで確認。両方公開する場合はCSS/route/browserの共有ファイルを最新main上で合成し、**新しいbase/head + 3 CI + D合成差分受入**を得てから次のmerge。元#465一括merge禁止。GO成立後にのみVercel新production→外部HTTP/DOM→正式post-deploy verifier→条件を満たすmarker更新を順に行う。

**E今回の完了定義：** D §13の必要なdocs-only統合を完了し、①②③の公開ゲートを個別に閉じ、未実施の人手・新productionを明示する。**判定記録の保存完了≠公開完了**。次Waveでは既存の資料を繰り返し長文再調査せず、欠けた人手受入・必要な合成版ゲートの実施を優先する。
