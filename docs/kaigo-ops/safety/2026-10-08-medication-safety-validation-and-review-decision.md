# Kaigo Ops — 服薬業務の安全点検シート：検証・専門職レビュー準備の統合判定（Worker E）

- checked_at: 2026-10-08 JST（GitHubのmain / PR、Vercel API、production HTTP応答を本Waveで再取得）
- Wave: Medication-Safety Validation & Expert Review Readiness
- 統合開始時main: `d5e5b5f1c3a019c801c81c1af737964183bf7ce4`
- A/B/D資料統合後のmain: `bab39f09d85a00dbca6d6e78d7b956889c22575d`
- Worker E integration: [PR #456](https://github.com/Josh-Temple/kaigo-rules/pull/456) / `worker-e/medication-validation-gates-20261008`。merge commitはGitHubのPR metadataと最終実行報告で照合する（記録作成時は未マージ）。
- **Wave判定: `PARTIAL_WITH_GAPS`**
- **独立安全判定: `SAFETY_PARTIAL_WITH_GAPS`**
- **公開判定: `PREVIEW_ONLY / NOT_PUBLIC`。新Issue/toolを一般公開しない。**
- 試作は研究・限定CI検証の範囲に留保し、公開用PRへの変換、feature flagの一般環境での有効化、本番releaseを実施しない。

## 1. PR別の固定証拠と統合

| 担当 | PR、対象head、docs merge SHA | 主な変更／確認したcheck |
| --- | --- | --- |
| A（根拠と段落） | [#453](https://github.com/Josh-Temple/kaigo-rules/pull/453), `cb18da48d6d3e59b8237f9d6d3317b8450a67d30`, main `b14bb127c6c54bb9a0b6985b8606c4bca4b68b5e` | `medication-safety-claim-to-content-trace.md`新設と`source-register.md`訂正。build / publication-readiness success。20 claimの採否に未確立を残す。 |
| B（公開候補文と適用性） | [#454](https://github.com/Josh-Temple/kaigo-rules/pull/454), `aaa0585597acba75b10335ed8294af302c113e21`, main `7fed025e86174e15de48c844629598663bba088b` | `issue-draft.md`修正、`service-applicability.md`新設。build / publication-readiness success。文面は未公開・要レビュー。 |
| C（隔離試作） | [draft #451](https://github.com/Josh-Temple/kaigo-rules/pull/451), 最新head `a1357ad7ebd723c5a8c8fcf754c04b384f7db95d`、**未マージ** | preview route / component / review model / test / spec / `prototype-verification.md`。headのbuild×2・publication-readiness・preview・disabledがsuccess。公開条件への合格ではない。 |
| D（独立検証・レビュー準備） | [#455](https://github.com/Josh-Temple/kaigo-rules/pull/455), `615b3ed5bfc4e09320623b3e6b41e00eb0fd1d53`, main `bab39f09d85a00dbca6d6e78d7b956889c22575d` | `test-results.md`と`review-checklist.md`追補、`expert-review-pack.md`新設。build / publication-readiness success。Dの独立動的検証と実在専門職レビューは未完了。 |

PR A/B/Dはdocsのみであり、各headのCI成功と変更ファイル・相互非競合を確認して、この順でmainへsquash統合した。**Cのコードはmainへ取り込んでいない**。

## 2. 根拠・本文・UIの意味上の突合

出典の正本：[厚生労働省ガイドライン／介護保険最新情報Vol.1436](https://www.mhlw.go.jp/content/001591418.pdf)（冊子38〜39頁など）、[事故報告関係Vol.1332](https://www.mhlw.go.jp/content/001574219.pdf)。このWaveでの原典再照合の記録はAのclaim traceとDの結果台帳を参照する。E自身が全原典・全20 claimを新たに独立検証したとは主張しない。

- A [claim-to-content trace](./medication-safety-claim-to-content-trace.md): `MS-01〜20`を再分類。特にMS-07（服薬後の具体的方法）、MS-08（特養の事例）、MS-13（事故報告と自治体運用）、MS-15（通所・訪問への転用）は`PARTIAL_WITH_GAPS`、MS-17〜20は`NOT_ESTABLISHED / DO_NOT_PUBLISH`。
- B [Issue草案](./medication-safety-issue-draft.md): `B-00`に事故・疑義発生時の使用禁止と正式対応経路を前置。`B-01〜13`は根拠支持・設計提案・要レビュー・未確立を区別。`B-04`／`B-05`の工程・選択肢は制度基準ではなく設計提案。
- B [サービス別留保](./medication-safety-service-applicability.md): 施設中心のガイドラインを、居住系・通所・訪問・短期入所・居宅介護支援等の服薬工程や職種権限へ一般化しない。業務工程が存在するか、担当権限、自治体運用は追加確認前に断定しない。
- C [試作仕様](https://github.com/Josh-Temple/kaigo-rules/blob/worker-c/medication-safety-preview-20261008/docs/kaigo-ops/safety/medication-safety-tool-spec.md): 選択式6項目・固定出力・自己申告。医療判断・再投与・事故報告の要否や期限を判定しない。

**固定版の限界（公開前に必ず解消）**：
1. A traceは旧B草案blob `4418af5405044be3a74268c7fa9ff85e6759126f` の`B-P01〜15`行に紐付く。現在mainのB草案blobは`083ffd0a17419e1533e65205e9230d725f3232ab`、段落IDも`B-00〜13`へ改訂。両文書の主張上限は概ね同じ方向だが、**同一本文を全段落再照合した証拠ではない**。`B-P`→`B-`の固定新版crosswalkと指摘対応表が必要。
2. C headは検証記録で対象とした`54b84cd85981c785110b1a9459a5f8852fddd64f`より1 commit進んだ。差分は試作検証記録の新規追加と仕様文書変更で、コード差分は比較上検出されない。一方、最新版headの機械CIは成功したため**そのheadに対するCI限定PASS**と記録する。Dのソース検査は旧C head `dd7ccdc535aa34acd76d8d54943a72b856345832`が対象であり、D独立実測PASSを意味しない。
3. Bが提案した「取扱いを把握している（自己申告・未検証）」等の改善語彙はCの既存`確認できる（自己申告）`等へ完全反映されていない。UI、結果、印刷物が安全認証と誤読されないかEX01/EX02と独立利用者評価が必要。
4. 出典のガイドラインによる推奨・単一事例、事故報告の通知、法令上の義務は区別。職種の業務権限や個別事故の対処法は`NOT_ESTABLISHED`。

## 3. 実行テストと独立検証の強さ

- C [検証記録](https://github.com/Josh-Temple/kaigo-rules/blob/worker-c/medication-safety-preview-20261008/docs/kaigo-ops/safety/medication-safety-prototype-verification.md): GitHub-hosted Ubuntu / Node 22 / localhost Chromium、flag enabled job（13 PASS / 1 skip）、disabled job（8 PASS / 6 skip）、無効・誤設定時404。run [37761326870](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37761326870)。テスト内のNetwork URL/header/bodyでは合成選択値4種の送信が検出されず、URL・local/session Storage・IndexedDBの名称確認も限定PASS。390px、CSS zoomによる200%模擬、keyboard、print CSSとPDF headerの自動検査も限定PASS。**既存のAnalytics一般通信までゼロではない**。
- C最新head `a1357ad...`: [GitHub check-runs](https://github.com/Josh-Temple/kaigo-rules/commit/a1357ad7ebd723c5a8c8fcf754c04b384f7db95d/checks) は `preview`、`disabled`、`build`×2、`publication-readiness` **success**。前段の検証台帳が参照するrunと分けて扱う。
- D [結果台帳](./medication-safety-test-results.md): R01〜R16はコードや文章の有限な静的照合が中心で、独立flag-enabled browserの個別動的実行は**NOT_RUN**。P01〜P07も通信payload・Storage・Analyticsの独立動的検査は**NOT_RUN**（P07はpreview上のfeedback入力導線がないためN/A）。U01〜U06は本番HTTP検査とUI source inspectionを含むが、200%ネイティブ拡大、実Android、スクリーンリーダー、人手の印刷評価は**NOT_RUN**。静的検査18/18は、そのうち1件が200%試験不足の検出であり、18件の安全試験PASSという意味ではない。
- **結論**：Cの限定機械テストは前進。Dの独立動的red-teamと、アクセス制御を証明したレビュー環境の検証は未成立。Cの成功でDの不足を埋めない。安全上の重大漏えいを観測したわけではないため`BLOCKED`と断定する証拠もない。

## 4. EX/HU gate：準備と実施を分離

| Gate | 必須担当 | 現在 | 公開に必要な追加証拠 |
| --- | --- | --- | --- |
| EX01 | 薬剤師・看護職等の適任医療職 | **EXPERT_REVIEW_NOT_DONE** | 実在レビューの匿名ID、審査版、日付、指摘、修正、再確認、明示判定 |
| EX02 | 介護事故防止・リスク管理実務責任者 | **EXPERT_REVIEW_NOT_DONE** | 現場負荷・中断・引継ぎ・権限・尊厳・サービス差分に関する同形式の実レビュー |
| HU01 | 内容・公開責任者 | **HUMAN_APPROVAL_NOT_DONE** | EX01/EX02とDの独立試験後、対象版と公開範囲を示す明示的GO/HOLD |

[専門職レビュー用pack](./medication-safety-expert-review-pack.md)は**REVIEW_PACK_READY**であり、外部レビューを依頼・実施した証拠ではない。実在利用者・薬剤・処方・事故本文、レビュアー個人情報・認証情報は公開リポジトリへ入れない。

## 5. Production / release assuranceと既存5 Issue/5 tools

- Kaigo Ops専用Vercel project: `kaigo-ops` / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`。
- 再照合時のproduction: deployment `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`、target `production`、state `READY`、runtime SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `https://ops-site-pi.vercel.app/`が同deploymentを指す。
- 本WaveのVercel HTTP取得: home `/`、既存Issue 5件、既存tool 5件（計11公開route）はすべて **HTTP 200**。`/sitemap.xml` **200**、`/tools/medication-safety-preview`は**404**。`/robots.txt`はこのE実行のfetchがセキュリティ理由で拒否され、**今回のfresh HTTPは未確認**（過去の成功記録は保持）。
- 現行main `ops-site/app/issues/registry.ts`に5件、`ops-site/lib/action-tools.ts`に5件だけ登録。`app/sitemap.ts`はトップとIssue registryのみ。試作未登録。
- 既存5 Issue→tool、Kaigo Rules制度確認、feedback、canonical、Analytics、390pxの対話式**本番ブラウザ回帰は今回Eとして未実施**。前Wave CI・production回帰の証拠を保持し、今回のHTTP検査と混同しない。
- `deploy-state/kaigo-ops` markerは `e49e770a970e541d2ad95204ad277eca89a485d3` とproduction runtimeに一致。mainはdocs更新により先行しているが、新runtimeをreleaseしたことにはしない。
- 新安全機能をproduction releaseしないため、新しいdeployment ID・runtime SHAは**存在しない**。GitHub Actions日次verifierの`VERCEL_TOKEN`配置と実運用完走は未確認の運用課題。

観測: Analyticsは従来の`RECEIVE_CONFIRMED`（初回2026-10-07）の記録を継承。EはPV再集計を実施していない。Search Consoleは`UNKNOWN`。計測定義・custom event・feedback分類・観測起点は変更せず、既存5 Issue/5 toolsを2026-10-21前後〜11-04前後に2〜4週間レビュー。PVと安全・事故削減効果を混同しない。

## 6. 決定・blocker・次の担当

**総合 `PARTIAL_WITH_GAPS`、公開 `PREVIEW_ONLY / NOT_PUBLIC`を維持。** 版のズレ、独立動的検証、専門職審査、公開承認が未達である。Cの試作を一般公開する根拠はない。docsの安全な統合のみ行い、prototype PR #451をdraftのまま保つ。

1. **A + B（根拠・本文の責任者）**：最新版B blob `083ffd0...`の`B-00〜13`とA trace・原典を文／段落単位で再固定。MS-07、MS-13、MS-15の射程、居住・訪問・通所などの適用・担当権限を未確立に保ち、根拠のない断定は削除する。
2. **C（ツール担当）**：Bの語彙変更を安全・結果・印刷文まで整合させ、同一headで再CI。`MEDICATION_SAFETY_PREVIEW=enabled`をlocalhostまたは認証済み制限環境に限定し、第三者に開かれたpreviewに有効化しない。
3. **D（独立監査者）**：A/B/Cの固定した同一版に対しR01〜R16、P01〜P07、U01〜U06を個別動的に再試験。Network payload、Storage、印刷、200%ネイティブ拡大、keyboard/focus、Android、previewアクセス制御の実行証拠を記録。CのCIは独立検証の代替にしない。
4. **EX01/EX02（実在の専門職・実務責任者）**：改訂版の[review pack](./medication-safety-expert-review-pack.md)でレビュー。匿名review ID・対象版・指摘・是正・判定を残す。外部連絡は内容責任者等の明示的依頼があってから行う。
5. **HU01（内容責任者）**：上記ゲートを確認したうえで対象サービス・公開文面・更新責任者・問合せ経路を明示してGO/HOLDを発行。**Eが代理承認しない**。
6. **E（統合・リリース担当）**：GO前は公開registration、feature flag有効化、本番releaseを行わない。条件が満たされたときのみ最新版で公開判定を再実施し、承認版に対するCI・Vercel exact SHA/READY/alias・11既存+新route・390px等を確認する。
7. **production運用担当**：別トラックで日次deploy verifierとSearch Console認証を確認。今回の医療安全公開判定に便乗して観測定義を変えない。

新規公開Issue番号は未付与。既存roadmapのIssue 6「収支・コスト構造」を維持する。**成果物を整えたことと公開条件を満たしたことを区別して、本Waveを限定完了とする。**
