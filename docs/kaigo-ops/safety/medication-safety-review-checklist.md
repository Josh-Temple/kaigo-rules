# 誤薬・与薬漏れ：独立安全性レビュー・専門職確認チェックシート

作成日: 2026-10-08 JST  
担当範囲: Worker D（Adversarial Safety Review / Privacy / Observability）  
対象: Kaigo Ops「誤薬・与薬漏れを防ぐための服薬業務プロセス点検」の**草案・非公開試作**  
公開承認: **未実施**（本書は承認書ではない）  
関連指示: `/Kaigo Ops/Work Instructions/2026-10-08_accident_prevention_and_medication_safety_foundation_wave_instructions.md`

> **新Wave追補（2026-10-08）**: 下記の「現在の判定」と各表の「未実施」は、前Wave開始時の記録として保持する。今回の独立確認は `medication-safety-test-results.md` 第7節、専門職へのレビュー依頼内容・記録欄は `medication-safety-expert-review-pack.md` を参照。今回の結果は **`SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**。A/B文書とC draft #451のコードは取得・静的検査済みだが、独立の動的ブラウザ検証・実専門職レビューはまだ完了していない。

## 現在の判定と使い方

- 2026-10-08の本レビュー時点でAのsource/risk register、BのIssue draft、Cのtool spec/previewは `main` 上に存在しない。これらの内容を審査済みと扱わない。
- 現時点の安全審査は `SAFETY_PARTIAL_WITH_GAPS`、公開ゲートは **HOLD**、専門職確認は `EXPERT_REVIEW_NOT_DONE`。
- A〜Cの対象版・SHAと対象URLを固定し、**画面の表示・操作・印刷・URL直打ち・通信・フィードバックの全経路**を実査したうえで下表を更新する。
- 「警告文があるからPASS」は禁止。期待動作を満たさない実際の応答が1件でもあれば該当ケースをFAILとする。
- 検証には架空の状況・非識別の選択値だけを使う。**実在利用者・薬剤名・処方内容・未公開事故記録は入力しない**。
- 専門職の氏名・署名・内部資料・実記録を公開GitHubに保存しない。レビュアーIDは非識別の管理用記号とする。

## 1. 一次資料と適用範囲

| ID | 専門職・実務責任者が確認すべき事項 | 記録内容・不合格例 | 結果 |
|---|---|---|---|
| S01 | 公開claimごとに原典URL、版、該当ページ、確認日、サービス類型が追える | URLだけでページ未確認ならNOT_ESTABLISHED | 未実施 |
| S02 | 法令上の義務、通知、ガイドラインの推奨、設計案を区別 | 推奨を「義務」「違反」と表現すればFAIL | 未実施 |
| S03 | 厚労省の施設中心ガイドラインから訪問・通所・居住系へ無条件に一般化していない | 「全サービスで必須」はFAIL | 未実施 |
| S04 | 原典と異なる事故原因・防止効果・頻度を創作していない | 効果量や事故件数の根拠なき記載はFAIL | 未実施 |
| S05 | 介護職・看護職・医師・薬剤師・管理者の権限境界が整合 | 職種が独断で薬剤判断可能と誤読させればFAIL | 未実施 |
| S06 | 個別事例・判断で自治体の報告基準や事業所手順を上書きしない | 「記録がなければ報告不要」はFAIL | 未実施 |

参照候補: 厚生労働省「介護現場におけるリスクマネジメントについて」  
https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/boushi/kaigo_jiko.html

厚生労働省「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」（令和7年11月、冊子38〜39ページ「誤薬・与薬漏れ」）  
https://www.mhlw.go.jp/content/001591418.pdf

**これらは資料候補であり、Worker Dが該当ページの内容をこの時点で独立に再確認した証明ではない。** 原典確認結果と主張の採否はAのclaim registerを参照し、レビュー時に照合する。

## 2. 内容・責任境界

| ID | 実査する条件 | 不合格条件 | 結果 |
|---|---|---|---|
| C01 | 事故や疑義がすでに生じた場合 | 服薬継続・再投与・医療処置の個別指示が表示される | 未実施 |
| C02 | 与薬漏れを入力・相談する場合 | 「今から飲ませる」等の具体的判断を誘導 | 未実施 |
| C03 | 全選択肢が「確認済み」になった場合 | ゼロ事故・安全・法令適合の保証が表示される | 未実施 |
| C04 | 全未回答／対象外／矛盾する入力の場合 | 未確認を安全と取り違える | 未実施 |
| C05 | 一人で担当した架空ケース | 個人を非難し、作業中断・負荷・伝達・人員・環境を検討しない | 未実施 |
| C06 | 本人の拒否・自己決定が関わる架空ケース | 安全名目で本人の意思を一律否定する | 未実施 |
| C07 | 改善案が業務負荷を増やす架空ケース | 「ダブルチェック」等を実施可能性、責任者、再評価なしに義務付け | 未実施 |
| C08 | 公開ページとツールの全CTA/feedback | 実在事故の詳細・薬剤情報・病名を記入するよう促す | 未実施 |

## 3. Privacy / セキュリティ / Analytics

| ID | 実査内容 | PASS条件 | 結果 |
|---|---|---|---|
| P01 | 初期UI、全入力、印刷テンプレート | 選択式の非識別業務状態のみ。氏名・病名・薬剤名・処方・実記録の入力欄なし | 未実施 |
| P02 | 架空選択値変更時のNetwork HAR/DevTools | 選択値が送信されない。通常の公開pageview通信と区別して検査 | 未実施 |
| P03 | URL、history、query、hash、clipboard、feedback prefill | 回答値・薬剤情報を格納せず、コピーは明示的操作のみ | 未実施 |
| P04 | localStorage、sessionStorage、IndexedDB、Cookie | 回答状態を永続化しない（第三者既存cookieと区別） | 未実施 |
| P05 | reset、印刷、offline、reload、戻る操作 | 意図せぬ送信・保存・回答復活なし。印刷には架空・非識別項目のみ | 未実施 |
| P06 | Search Console / Web Analytics | 閲覧値を事故減少や需要の証拠としない。回答内容custom eventなし | 未実施 |
| P07 | feedback公開注意書き | GitHub Issuesで公開保存されること、個人・医療・未公開事故情報を投稿しないことを表示 | 未実施 |

ブラウザのNetwork検証では、HTML/JS/CSSや既存のVercel Analytics通信を「無通信」と主張しない。**回答内容を通信内容へ含めていないこと**をbody/query/header/eventごとに検査する。人工の氏名・薬剤名であっても入力欄が存在しないことを優先確認し、実情報は使わない。

## 4. 操作 / アクセシビリティ / 非公開保持

| ID | 実査内容 | 不合格例 | 結果 |
|---|---|---|---|
| U01 | 390px Android相当、200% zoom | 横はみ出しで主要操作不可、警告が視界から消える | 未実施 |
| U02 | keyboardのみ、screen reader label、focus、aria-live | 入力状態が分からない、reset後focusを失う | 未実施 |
| U03 | empty / default / invalid / 対象外 / reset | 黙って安全と判定、想定外入力を表示へ反映 | 未実施 |
| U04 | Print Preview | 回答や実データの自由欄、隠れた個別情報を含む | 未実施 |
| U05 | 公開registry、sitemap、ナビ、直接URL | **公開承認前に**新Issue/toolがpublicに露出する | 一部実施（registry/sitemapの静的確認のみ） |
| U06 | 既存home + 5 Issue + 5 tool | 既存検索・Rules・feedback・routeが退行 | 旧CI確認のみ／今回未再実行 |

**robots除外、非リンク、未掲載だけで「非公開」と判断しない。** Preview専用deploymentの認証・routeアクセスをブラウザで確かめる。正規public domainに到達するルートがあれば、public registry非登録でも公開とみなして事故情報を掲載しない。

## 5. Red-teamテスト手順

`medication-safety-test-results.md` のR01〜R16を使用する。各ケースについて以下を保存する（氏名・処方等は含めない）。

1. 対象PR / commit SHA、reviewed source register version、preview URL（認証されたものだけ）、テスト環境と実行日時。
2. 操作した架空・非識別の選択値と、実際の画面表示（危険な情報は転記しない）。
3. 期待動作、actual behavior、`PASS / FAIL / NOT_RUN / NOT_APPLICABLE`。
4. 問題があれば修正PR、再実施日、解消証拠。注意書き追加のみで同じ動作を温存する対策は認めない。

## 6. 専門職レビュー / 公開承認

次の2種類のレビューを**別々に**記録する。

| Gate | 必要な役割 | 版・日時・判定の記録 | 現状 |
|---|---|---|---|
| EX01 医療・服薬安全 | 薬剤師、看護職など適切な医療専門職（必要に応じ医師） | non-identifying review ID / 対象SHA / 確認日 / 指摘ID / 是正の有無 / PASSまたはFAIL | `EXPERT_REVIEW_NOT_DONE` |
| EX02 事故防止・介護運用 | 事故防止・リスク管理の実務責任者 | 同上。施設・訪問・通所等の適用境界を確認 | `EXPERT_REVIEW_NOT_DONE` |
| HU01 内容責任者の公開判断 | 公開可否の意思決定権限を持つ責任者 | approval ID / 対象release SHA / 承認日時 / GOまたはHOLD | `HUMAN_APPROVAL_NOT_DONE` |

レビュー対象に重大変更が入った場合は該当箇所を再評価し、旧版のPASSを新SHAへ自動継承しない。

## 7. 合否・引き継ぎ

- `SAFETY_PASS`: A〜Cの対象実装版に対するRケース、privacy、UI、専門職EX01/EX02を実行し、FAIL・重大未確認がなく、記録で追跡可能。
- `SAFETY_PARTIAL_WITH_GAPS`: 監査計画・一部検証は完了、A〜C・実ブラウザ・専門職等に未実施が残る。**公開不可**。
- `SAFETY_BLOCKED`: 個別投薬助言、情報漏えい、誤安心、無断公開等の重大な失敗を確認。是正・再審査まで公開不可。
- 実装の安全審査と、本番公開の最終承認は別判定。DのPASSだけでpublishしない。
- feedback副分類として「安全上の懸念／誤情報の可能性」の**内部トリアージ上の注意フラグ**をEへ提案。既存7分類や利用者フォームは、実証前に勝手に変更しない。

次の担当: Aはsource claim traceを提示、Bはサービス適用範囲とIssue草案、Cは認証付きPreviewとツール・テスト、Dは上記を再実査し証跡更新、Eは独立判定・公開可否を記録する。


---

## 8. 2026-10-08 新Waveの検証更新と未実施ゲート（上の旧台帳を消さずに追補）

**対象固定:** 最新確認時main `d5e5b5f1c3a019c801c81c1af737964183bf7ce4`。C draft PR #451 head `dd7ccdc535aa34acd76d8d54943a72b856345832`。A/Bの前Wave成果物はmainで確認。D検査はソース静的18件、厚労省ガイドライン冊子p38〜39直接確認、productionの11+1ルートHTTP検査。C CIのsuccessは独立動的検査ではない。

| Gate | 新Wave結果 | 精確な残課題 |
| --- | --- | --- |
| S01〜S04（出典・範囲・効果） | **PARTIAL_WITH_GAPS** | 一次資料の誤薬・与薬漏れp38〜39を独立確認。B草案・A claimの一致を限定確認。段落単位traceはmainで未取得、全claim完全照合は未了 |
| S05（職種権限） | **REVIEW_REQUIRED** | 配薬・服薬確認を扱う職種・事業所の正式な権限は未確立 |
| S06（事故報告） | **REVIEW_REQUIRED** | 個別報告要否・自治体運用未審査。サイトは判断していない |
| C01〜C02（事故・再投与） | **STATIC_CONSISTENT / DYNAMIC_NOT_RUN** | 選択式UI・事故時案内を確認、独立の誤解検査とEX01待ち |
| C03〜C04（全確認・未回答・対象外） | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | 固定の非保証文、対象外の再確認を確認。実ブラウザ・印刷・改ざん値の独立試験待ち |
| C05〜C07（職員責任・本人意思・負荷） | **SOURCE_CHECKED / HUMAN_REVIEW_NOT_DONE** | 個人非難を避けた業務条件の文言あり。EX01/EX02の現場妥当性確認待ち |
| C08（feedback） | **NOT_APPLICABLE（C試作にはfeedback CTAなし）** | Bの公開案を作る前に、公開投稿・機微情報禁止の導線を別途レビュー |
| P01 | **STATIC_CONSISTENT** | 実ブラウザ入力DOM／印刷実測待ち |
| P02 | **NETWORK_NOT_RUN** | answer値が通信body/query/header・Analyticsに含まれないことの実測 |
| P03 | **BROWSER_NOT_RUN** | history / query / hash / clipboard / feedback prefill検査 |
| P04 | **STORAGE_RUNTIME_NOT_RUN** | local/session/IndexedDB/cookieを動的検査 |
| P05 | **PRINT_RELOAD_OFFLINE_NOT_RUN** | 印刷、消去、reload、戻る、offline動作 |
| P06 | **ANALYTICS_PAYLOAD_NOT_RUN** | 通常pageviewと回答送信を分けて検証 |
| P07 | **C試作のfeedback導線なし** | 公開時のGitHub Issues注意書きが必須 |
| U01 | **D_BROWSER_NOT_RUN** | 390px・200% zoom。Cの390px CI成功はD独立ではない |
| U02 | **KEYBOARD_SCREENREADER_NOT_RUN** | label/ARIAのコードはあるがfocus・結果通知は動的検査が必要 |
| U03 | **SOURCE_CHECKED / DYNAMIC_NOT_RUN** | 状態変化・型不正をDが実行して再照合 |
| U04 | **PRINT_PREVIEW_NOT_RUN** | 印刷結果・保護文言を実印刷で確認 |
| U05 | **PASS（production新routeがHTTP 404、public registry/sitemap非登録の限定範囲）** | flag-enabled preview URLのアクセス制限は**NOT_ESTABLISHED** |
| U06 | **PASS（既存11公開routeがHTTP 200の範囲）** | 既存5 toolの入出力、390px、keyboardの独立回帰は未実施 |
| EX01 | **`EXPERT_REVIEW_NOT_DONE`** | 医療専門職が版・具体表現・事故時案内を審査 |
| EX02 | **`EXPERT_REVIEW_NOT_DONE`** | 実務責任者がサービス適用・実施可能性・利用者の意思を審査 |
| HU01 | **`HUMAN_APPROVAL_NOT_DONE`** | 内容責任者が対象版・未解決・公開範囲を明示承認 |

### 専門職へ渡す手順と記録の単位

1. 専門職へ送る前に `medication-safety-expert-review-pack.md` の対象main / C head / A/B文書版を再確認し、変更があれば対象版と差分を更新する。
2. EX01とEX02は**別の適任者の実審査**が必要。配薬・服薬確認・事故時対応・職種権限に関する質問を優先する。実在個人の記録を提出しない。
3. レビューが実施された場合のみ、非識別review ID、役割、対象SHA、原典版、実施日、指摘ID、修正commit、再確認、PASS/FAILを記録。氏名・署名・内部資料は公開repoに書かない。
4. 問題が残る場合は対応するR/P/Uを再実行し、旧版のPASSを新しいSHAへ自動的に移さない。
5. EX01/EX02完了後に初めてHU01の明示的公開承認を求める。全て揃うまで、**一般公開・公開registry・sitemap・production flagを変更しない**。

**新Wave D判定:** `SAFETY_PARTIAL_WITH_GAPS`。重大な医療助言・情報漏えいの発生を観測したとの判断ではない。一方、実ブラウザのprivacy・誤安心検証と適任専門職の確認が欠け、`SAFETY_PASS`や公開承認に昇格する根拠もない。Eには `PREVIEW_ONLY / NOT_PUBLIC` を推奨する。


---

## 9. 2026-10-08 D-only independent dynamic checklist — newer evidence

**Target ledger:** main 233f11f60bd53cee4684fd66eb5c0490b2fee926; A trace blob 2cb32c3b4de093d51d410d23c04511e020a43571 (OLD B trace); B draft blob 083ffd0a17419e1533e65205e9230d725f3232ab; B service blob 8138d89832ddd4b706ff1da4751ffd2626e251bb; C draft #451 pinned a1357ad7ebd723c5a8c8fcf754c04b384f7db95d. **Independent run** [37782952341](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37782952341) in D [draft PR #457](https://github.com/Josh-Temple/kaigo-rules/pull/457). No C implementation was edited by D.

- R01–R16: all 16 recorded individually in test-results §9.2. Automated visibility/state assertions completed for selected cases; others retain PARTIAL where human or external environment remains outstanding. Do not represent these as 16 clinical PASS cases.
- P01–P07: all seven recorded in test-results §9.3. Synthetic selections absent from observed request headers, URL and body, history, local/session storage, IndexedDB and cookie; tested conditions **PASS_LIMITED**, Analytics cross-environment and feedback handoff remain partial.
- U01–U06: all six recorded in test-results §9.4. Local 390px, CSS 200% zoom, labeled controls, live-result, print-media and PDF-in-memory, invalid-state and route tests executed. Native zoom, real Android, screenreader, native print preview and remote production journey are not complete.
- Local flag absent and invalid: **HTTP 404 each**, existing 5 Issue / 5 tool local routes passed. Public Vercel HTTP could not be independently retrieved with the current web client; prior successful external check remains historical. Vercel API confirmed same READY deployment and runtime, **not the current direct HTTP**. PREVIEW_ACCESS_NOT_ESTABLISHED.
- No answer is transmitted in observed network traffic, but ordinary pageview requests can occur. No claim of zero communication or permanent no-leak guarantee.
- Version mismatch remains **P0**: old A B paragraph mapping and C labels vs current B proposed labels. **EX01/EX02 NOT_DONE; HU01 NOT_DONE.**
- Disposition **SAFETY_PARTIAL_WITH_GAPS; PREVIEW_ONLY; NOT_PUBLIC**. Reviewed once only for pinned C SHA. New C SHA requires changed-case retest and new expert pack snapshot. This section supersedes only the older NOT_RUN statements for the test dimensions actually exercised.


---

## 10. 2026-10-09 独立再試験版・審査ゲートチェック（旧版の判定履歴は保持）

**現対象版**：C draft #451 `7ec2fe8c644d0526af1650e857a7da397488a0ad`、page blob `cfa6f30633c5c8536b570c4c82b2794cd4353320`、worksheet blob `2ecd0475681f5a822da0f3dbe32c4610a041d47c`、model blob `9580e9202209f5e3fdf3b544b628d68885062295`。B #459 Issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25`、service blob `e3889c26c5b46d4644b29d94c657e628c96206d3`。A #458 trace blob `0b042421f49ae5213f80b71e4cf04c502d32c1f9` は**旧Bへの照合**。現Bを独立照合したことにはならない。

D独立検証：[#457](https://github.com/Josh-Temple/kaigo-rules/pull/457)、[workflow run #37844281038](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038)。flag enabled（localhostのみ）と absent/invalid（localhost route 404）を別ジョブとした。29行の詳細と検査済み／未実施区別は [medication-safety-test-results.md §10](./medication-safety-test-results.md) を正本とする。runが進行中・失敗なら`PASS_LIMITED`は成立しない。

| 審査観点 | D機械検査と残る人の確認 | 2026-10-09の判定 |
| --- | --- | --- |
| **R01〜R16 誤安心・医療判断・サービス・組織責任** | 全確認/全担当外/混合、事故・疑義時停止と専門職への案内、再投与・自治体報告の非判断、本人意思・職員負荷、型改ざん。実務上の妥当性はEX01/EX02待ち | **PARTIAL**、対象コード/CIの有限なassertionのみ |
| **P01〜P07 選択値・privacy** | 合成enumのrequest URL/header/body、URL/history、local/session/IndexedDB/Cookie、印刷、resetとfeedback無し。通常Analytics pageviewと回答送信を分ける | **PASS_LIMITEDを含むPARTIAL**。送信全件・本番・clipboard・offlineは未保証 |
| **U01〜U06 mobile/accessibility/exposure** | Chromium 390px、CSS 200%模擬、keyboard/label/aria-live、印刷DOM/PDF header、localhostの無効flagと既存11路線 | **PARTIAL**。native 200%、実Android、screen-reader、native印刷、実本番操作はNOT_RUN |
| **U05 非公開維持** | mainのpublic registry・sitemap非登録、Cがdraft・未マージ。Vercel C branch deployment一覧0、既存production `READY` | **PREVIEW_ACCESS_NOT_ESTABLISHED**：SSO設定だけで全previewへの匿名到達不可を証明できない |
| **根拠と版の同一性** | 厚労省G25冊子38/39/46頁、N24通知PDF p2、サービスの推奨/事例/報告様式を区別。B現blobとA traceにズレ | **A_FINAL_B_TRACE_NOT_DONE / REVIEW_REQUIRED** |
| **EX01 実在薬剤師/看護職等** | MS-07の服薬後確認、再投与・指示変更の境界、服薬拒否と意思尊重、結果と印刷の文言、職種別権限 | **EXPERT_REVIEW_NOT_DONE** |
| **EX02 介護事故防止・リスク管理実務責任者** | 中断、兼務、連絡、本人意思、負荷、責任分担、施設事例の他サービス転用、全確認/対象外 | **EXPERT_REVIEW_NOT_DONE** |
| **HU01 内容・公開責任者** | 最終B/A/C/D固定版と差分、修正済み指摘、対象サービスと公開範囲、訂正・問い合わせの責任者、明示GO/HOLD | **HUMAN_APPROVAL_NOT_DONE** |

**Review packへの引き継ぎ**： [medication-safety-expert-review-pack.md §8](./medication-safety-expert-review-pack.md) へ、版・質問・未解決課題・非識別の記録空欄を追加。実在の専門職へ連絡、招待、資料送付、承認の代行は行っていない（`REVIEW_REQUESTED=false`）。架空の事例だけを審査に用い、氏名・所属・署名・事故・処方・内部資料はpublic repositoryへ置かない。

**D safety**：`SAFETY_PARTIAL_WITH_GAPS`。Eへの公開推奨：`PREVIEW_ONLY / NOT_PUBLIC`。医学的安全性・法令適合・事故予防効果の承認ではない。DはC本体/公開設定/main/本番を変更しない。


### 10.1 2026-10-09 追補：独立CI完走とA現行B traceの読戻し

前表のA未照合行は、当初スナップショットを示す。**現行判定**は以下が優先する。

- **D独立run [#37844583974](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844583974)**：`independent-enabled=SUCCESS`（D専用Chromium **15/15 PASS**）、`independent-disabled=SUCCESS`（flag未設定／不正時localhost HTTP **404**、既存5 Issue/5 tool route PASS）。GitHub CIの実行ログで確認。これは実端末/専門職/外部previewの合格ではない。
- **A現行B traceは完成**：PR #458 head `37fc213301e93442f71efc4509af5cfa49567c88`、trace blob `271560deb7ea848690e12d97fd23661583511198`、対応するB issue/service blobs `e0cc354e2b78a28912c80c0611ccf3c165d00b25` / `e3889c26c5b46d4644b29d94c657e628c96206d3`。B-00〜13、MHLW-01〜07、8サービス群、5状態対応についてA独立静的追跡。**A判定自体はPARTIAL_WITH_GAPS**、医学的妥当性の合格ではない。
- **C最新PR head** `a61797393f20e897247d985ab0861f6443a0a74e` はDの検証対象 `7ec2fe8c644d0526af1650e857a7da397488a0ad` からdocsのみ変更。page/worksheet/modelは同一blob。コードが変われば改めてD再試験する。
- **残る主ゲート**：EX01/EX02実専門職確認 `NOT_DONE`、HU01 `NOT_DONE`、実機/accessibility/ネイティブ印刷・本番外部アクセスとpreview認証の証明不足。よって **`SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`** を維持。E以外が公開可否を決定しない。

確認詳細は [test-results §10.4–10.5](./medication-safety-test-results.md)。古いNOT_RUN/P0の行は当該時点の履歴として保持し、最新版を無断で過去へ遡ってPASS扱いしない。


---

## 11. 2026-10-09 D独立監査・実在審査開始前チェック（最新版）

**Version lock（JST 2026-10-09確認）:** main `8d824ce35be176dd05de976709ee1f81944b65d1`、B issue/service blobs `e0cc354e2b78a28912c80c0611ccf3c165d00b25` / `e3889c26c5b46d4644b29d94c657e628c96206d3`、A trace `271560deb7ea848690e12d97fd23661583511198`。C candidate head `a61797393f20e897247d985ab0861f6443a0a74e` はD tested code SHA `7ec2fe8c644d0526af1650e857a7da397488a0ad` から文書のみ追加。C page / worksheet / model blobs `cfa6f30633c5c8536b570c4c82b2794cd4353320` / `2ecd0475681f5a822da0f3dbe32c4610a041d47c` / `9580e9202209f5e3fdf3b544b628d68885062295` は一致。

**主要証拠:** [全29-case個別台帳§10.2/§11](./medication-safety-test-results.md)、[最新EX/HU審査pack§9](./medication-safety-expert-review-pack.md)、[D旧15 test成功run 37844583974](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844583974)、[追加2件を含む新run 37857899198](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37857899198)（完了とログは実測した場合のみ確定）。旧29-case台帳：**R16 + P7 + U6 = 29、11 PASS_LIMITED / 18 PARTIAL**。Dのtest数とは一致しない。

| 対象 | 実際に確認済みのこと | 未確認・次に必要なこと |
| --- | --- | --- |
| CI workflow/PR権限 | `contents: read`、Action full commit pin、C checkout exact SHA、`persist-credentials: false`、secret受領指定なし、artifacts uploadなし、enabled試験はlocalhostのみ | Dはworkflow/code含有PRでdocs-onlyではない。commit更新ごとのrun/jobs/logsと権限diffを再確認 |
| Privacy P01–P07 | 合成enumとChromium request/URL/history/Storage/Cookie/IndexedDB、feedbackリンク非存在、print/reload/reset。新D追加testはdemo→print→reset後のrequest混入も対象 | 本番/別端末/全Analytics宛先/clipboard/offline、HAR非保存条件での独立確認。一般pageview通信はあり得る |
| Safety R01–R16 | 確定出力は自己申告・非保証。医療、再投与、個別事故報告判定を行わないソースと一部DOM assertion。原典はG25施設推奨・特養一事例、N24は報告通知 | EX01/EX02による事故時導線、本人意思・職種権限・8サービス群・正式手順・全confirmed/NAの誤安心実査 |
| UI/accessibility U01–U04 | headless Chromium 390px、CSS zoom 200%模擬、ラベル・keyboard・aria-live・印刷media/PDF in memory。新D追加testはDOM live更新 | **ネイティブ200% zoom、実Android Chrome、読み上げ実聴取、実印刷プレビューとPDF/紙の目視はNOT_RUN** |
| U05/U06 非公開と既存機能 | C draft/unmerged。無効flag localhost 404、既存11 routes。Vercel projectのproduction READY・runtime SHA `e49e770a970e541d2ad95204ad277eca89a485d3`・alias確認 | 本番direct HTTPは今回web clientで取得エラー、実公開11route/操作は未実行。**全previewの第三者アクセス制限はPREVIEW_ACCESS_NOT_ESTABLISHED** |
| 実在レビュー/公開 | packと質問表・非識別欄が存在 | **REVIEW_REQUESTED=false / EX01, EX02 EXPERT_REVIEW_NOT_DONE / HU01 HUMAN_APPROVAL_NOT_DONE**。送付明示許可なし。専門職・責任者の代行はできない |

**差戻し条件:** B文面またはservice表の意味変更→A出典trace→C選択/結果/印刷→Dの関連29-case＋privacy/accessibility再試験→EX01/EX02対象版の再審査。C 3 code blobs変更時もCIを更新して再試験。documentだけのhead変化なら実差分・3blob一致を検査し、無条件にPASSを転記しない。

**Dの現判定:** `SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`。重大な事故誘導・個人情報漏洩・公衆preview露出の実証は現時点でないが、未実施を安全PASSに昇格できない。**公開判定はE、医療上の判断は適任の実在専門職、公開許可はHU01本人に残す**。


### 11.1 新Dテストの完走確認と実査HOLD

2026-10-09 JST時点の最終コード固定D追加spec `28161729ba8b602a45920c292da6b2db476646bc`。前回の確認ダイアログ未承認による新test失敗（run #37857899198、16/17 pass）はtest harnessで修復。[run #37858180696](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858180696) = `completed/success`、enabled **17/17 pass**、disabled/invalid local flag HTTP 404・既存11 route検証成功。**前回の失敗を無かったことにせず履歴として保持**。[29ケース台帳§11.4](./medication-safety-test-results.md)参照。追加観測は選択→架空例→印刷media→reset時の合成値のrequest混入と、DOM live-region更新。実Android・native 200%・実音声読み上げ・紙/PDF目視・本番privacy・preview認証は継続して`NOT_RUN/NOT_ESTABLISHED`、EX01/EX02・HU01は`NOT_DONE`。**公開HOLD**。


### 11.2 A/B/C並行変更を反映したゲート更新（JST 2026-10-09）

**更新された版**：A #458 head `87b9d67a08b3c9503a47e9914a1abe5af16ca21c` / trace blob `3264cb93cc2c7f867abe7fb42def68be03bf98e6`（§9の原典・EX質問追加）、B #459 head `9c7b8639380802224bd9b5518f52800ff0b56af8`（issue/service blobs不変、審査補足blob `64feae5962df5614d0d86a6fc36ed24687bae16b`新設）、C #451 head `2dd0e260d0922e18d003905f4a7edf42560f640c`（**docs + C browser testだけ変更、アプリpage/worksheet/model blobsは不変**）。C側browser試験run [37858189100](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858189100) はSUCCESS、D独立run [37858180696](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858180696) の17/17成功とは別のもの。D自身の後続run [37858370661](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37858370661) もSUCCESS。現在A文書を旧traceに戻さず、レビューpack§9.6で質問表を照合する。旧§11の当時のhead表記を現行値と解釈しない。**29ケース11 `PASS_LIMITED` / 18 `PARTIAL`**、human reviews未依頼・未実施、現物・実機・access gate未検証。**`SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC`**を維持。
