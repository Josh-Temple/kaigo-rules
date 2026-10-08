# 誤薬・与薬漏れ：独立安全性レビュー・専門職確認チェックシート

作成日: 2026-10-08 JST  
担当範囲: Worker D（Adversarial Safety Review / Privacy / Observability）  
対象: Kaigo Ops「誤薬・与薬漏れを防ぐための服薬業務プロセス点検」の**草案・非公開試作**  
公開承認: **未実施**（本書は承認書ではない）  
関連指示: `/Kaigo Ops/Work Instructions/2026-10-08_accident_prevention_and_medication_safety_foundation_wave_instructions.md`

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
