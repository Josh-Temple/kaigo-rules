# 誤薬・与薬漏れ：Worker D safety test results / 証拠台帳

Date: 2026-10-08 JST  
Scope: Kaigo Ops medication-safety foundation, Worker D only  
Review baseline main: `a90119e9d9e9de3050a563178daa0bf6d7c47bb8` (作業開始時のlatest commit)  
Review result: **SAFETY_PARTIAL_WITH_GAPS**  
Public safety feature decision: **HOLD / NOT APPROVED FOR PRODUCTION**  
Expert gate: **EXPERT_REVIEW_NOT_DONE**  
Human publication approval: **HUMAN_APPROVAL_NOT_DONE**

## 1. 確認した資料・操作と確認範囲

| Check | Source / command equivalent | 結果 | 限界 |
|---|---|---|---|
| D-FRESH-01 | GitHub connector: latest commits / open PR search, 2026-10-08 | **PASS**: current repository metadata, commit、既存open PRを取得 | 同時進行のA〜Cによる後続PRは後日再確認 |
| D-EVID-01 | GitHub Contents GET: `docs/kaigo-ops/safety/medication-safety-source-register.md`, `...risk-register.md` at default `main` | **NOT_ESTABLISHED**: 2ファイルとも404 | Aが別branchに作成したかは未検証 |
| D-ISSUE-01 | GitHub Contents GET: `docs/kaigo-ops/safety/medication-safety-issue-draft.md` at `main` | **NOT_ESTABLISHED**: 404 | B草案の内容・適用性は未審査 |
| D-TOOL-01 | GitHub Contents GET: `docs/kaigo-ops/safety/medication-safety-tool-spec.md` at `main` | **NOT_ESTABLISHED**: 404 | C preview/テストの状態遷移を実行できない |
| D-BASE-01 | Contents GET: `ops-site/app/issues/registry.ts`, `ops-site/lib/action-tools.ts` | **PASS（静的な限定確認）**: 5 Issue / 5 toolで、誤薬・服薬の新規public登録なし | 別route・branch・preview URLの直接到達性は未確認 |
| D-BASE-02 | Contents GET: `ops-site/app/sitemap.ts` / `app/page.tsx` / `app/_components/IssueExplorer.tsx` | **PASS（静的な限定確認）**: sitemapとhomeのIssue一覧が既存registryに基づく | 生成済HTMLや実ブラウザでの独立検査ではない |
| D-BASE-03 | Contents GET: `.github/workflows/validate-ops-site.yml` / `ops-site/scripts/verify-routes.mjs` / `ops-site/package.json` | **PASS（検査契約の存在確認）**: npm test、build、Playwright、11 route smokeのCI設定あり | **今回のD作業でCIをローカル再実行したという意味ではない** |
| D-PROD-01 | Vercel project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`; deployment API `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S`; deployment aliases API | **PASS（メタデータ照合）**: project `kaigo-ops`、target `production`、READY、git SHA `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app` | 11ルートの現在のHTTP / 390px / contentは直接実測していない |
| D-OBS-01 | `docs/kaigo-ops/CURRENT.md` / `measurement.md` / `usage-observation.md` / `feedback-triage.md` | **PASS（canonical確認）**: Analytics RECEIVE_CONFIRMED、first observation 2026-10-07、Search Console UNKNOWN、custom event追加を保留 | Analytics数値の再計測・feedback件数の独立検索は行っていない |
| D-EXPERT-01 | human review ID / role / version / feedback / disposition | **NOT_RUN** | 関係する医療職・リスク管理責任者のレビュー証拠なし |
| D-APPROVAL-01 | final content owner approval | **NOT_RUN** | 公開可否の承認なし |

上記の`PASS`は指定した限定範囲のみの確認結果で、ツールの事故防止効果やprototype全体の安全性を意味しない。

## 2. Adversarial red-team matrix

全ケース **架空の状況のみ**を使用。A〜Cの対象成果物がレビュー可能になるまで、以下は**設計済み／実ブラウザ未実行**である。 `NOT_RUN` を `PASS` に読み替えない。

| ID | 誘導・攻撃内容 | 実機でPASSと判定する条件 | 今回 |
|---|---|---|---|
| R01 | 「別の薬を飲ませた。どうすれば？」と相談 | 服薬可否や医療処置を指示せず、所属先の事故時手順、責任者、関係医療職、必要な緊急対応へ案内 | NOT_RUN |
| R02 | 「飲ませ忘れを今から飲ませるべき？」 | 再投与・中止・時刻の判断を返さない | NOT_RUN |
| R03 | 「全部チェック済み。事故はゼロ？」 | 安全・事故ゼロ・法令適合を保証せず、確認項目の範囲と限界を示す | NOT_RUN |
| R04 | 「訪問介護にも施設の方法をそのまま使える？」 | 施設中心の根拠、サービスごとの未確定事項を区別する | NOT_RUN |
| R05 | 一人の担当で起きた架空ケース | 個人の不注意と決めつけず、業務環境・中断・責任分担・情報更新等の検討につなぐ | NOT_RUN |
| R06 | 本人が服薬を拒否する架空ケース | 意思の尊重と正式な相談経路を保ち、強制や服薬の医学的指示をしない | NOT_RUN |
| R07 | 氏名・病名・薬剤名・処方内容・内部事故記録を入力したい | 入力欄・upload・free text・収集誘導がなく、禁止情報の注意がある | NOT_RUN |
| R08 | 「記録がないなら自治体への報告は不要？」 | 自動で要否を確定せず、正式な事故報告手順・自治体ルールへ戻す | NOT_RUN |
| R09 | 全設問を未回答または対象外 | 安全点数や安心表示を生成せず「未確認」「検討待ち」と表す | NOT_RUN |
| R10 | 想定外value / null / 型不正 / 連続リセット | エラーや不正値を安全と誤読させず、fail-closedで処理する | NOT_RUN |
| R11 | チェック変更中にNetworkを観察 | 回答内容がfetch/XHR/beacon、analytics event、feedback prefillへ流出しない | NOT_RUN |
| R12 | reload / 戻る / URL共有 / history / Storageを観察 | 回答状態をquery/hash/localStorage/sessionStorage/IndexedDBへ格納しない | NOT_RUN |
| R13 | 印刷・PDF表示・リセット・offline | 意図的操作のみ、実情報なし、offlineでも安全性を誤判定せず想定外送信なし | NOT_RUN |
| R14 | 390px画面・200% zoom・keyboardのみ | 注意・限界が可読、ラベル・focus・reset・結果読み上げが機能 | NOT_RUN |
| R15 | 事故対策が現場で実施困難、負荷増大 | ダブルチェックの一律義務化ではなく、責任者・業務負荷・再評価を扱う | NOT_RUN |
| R16 | 直接URL・検索・ナビ・sitemapからpreviewを探す | 承認前の安全Issue/toolは正規public domainから到達不可。robotsのみの隠蔽をPASSとしない | NOT_RUN |

### 未実行の理由

- D着手時点の`main`にAのclaim/risk register、BのIssue草案、Cのtool spec/previewが存在しない。
- review対象の実コード、preview URL、操作可能なUI、専門職レビュー記録が特定できない。
- URLや仕様を推測して架空の実行結果を作成しない。
- 本レビューは「デザインとゲートの独立審査」であり、公開可能と判断していない。

## 3. CのPR到着後の実行プロトコル

1. **特定**：A/B/CのPR URL、commit SHA、claim版、preview URL、preview access制御を固定。認証が必要なら正規のアクセス経路を用いる。利用者情報・処方情報を投入しない。
2. **source/content**：Aの各claimを厚労省原典の当該ページへ照合し、Bの文章・CのUI出力がclaimの射程を超えていないことを確認。
3. **code/test**：対象コミットをチェックアウトして `cd ops-site && npm ci --no-audit --no-fund && npm test && npm run build && npm run test:browser`、サーバ起動後 `npm run verify:routes -- http://127.0.0.1:3000` を実行。既存5ツールのpass/failを今回の新ツールと区別。
4. **adversarial browser**：R01〜R16をPlaywright/実ブラウザで個別実施。実装が質問フォームでなく選択式なら、対応する表示・操作・限界説明を評価し、`NOT_APPLICABLE`の理由を明記。
5. **privacy**：非識別の選択値のみでDevTools Network、URL、storage、pageview payload、印刷DOMを点検。baselineのAnalytics script配信と回答内容の漏えいを混同しない。
6. **mobile/accessibility**：390px、200% zoom、keyboard、focusとラベルを確認し、結果の誤安心を検査。
7. **non-public**：公開registry、sitemap、nav、direct route、preview URL権限、production aliasを再チェック。PR auto-previewにpublic到達性がある場合は、それを「非公開」と称しない。
8. **expert + owner**：EX01/EX02、HU01の独立承認を得て指摘が解消されたあとEへhandoff。必要ならrevision後に該当ケースを再試験。

テストは機密データを含むHAR、スクリーンショット、session tokenを公開artifactへ保存しない。保存が必要な場合は**個人情報を含まない要約**（case ID/expected/actual/status/環境/commit/修正ID）のみとする。

## 4. Observability / feedback / production reliability の非干渉

- 現在の5 Issue / 5 toolsは`ops-site/app/issues/registry.ts`と`ops-site/lib/action-tools.ts`に登録されている。新たな誤薬安全ページは未登録。
- Analytics: canonical上の `RECEIVE_CONFIRMED` を維持するが、現時点で **事故予防効果、ツール完了、需要** の証拠ではない。custom eventは追加せず、2026-10-21前後〜11-04前後のレビュー窓を維持。
- Search Consoleは `UNKNOWN`（認証済みアクセス未確認）。「未インデックス」と解釈しない。
- feedback: 既存7分類を保ち、万一の医療安全上の懸念・誤情報疑義はEへ速やかな内部確認フラグとして提案する。新しい入力必須項目、事故記録投稿欄、実情報の転載は設けない。
- 日次GitHub Actions production verifierについて、`VERCEL_TOKEN`配置と本番完走は最新canonicalでも未確認。今回Dでは実行・更新していない。Eの別追跡項目とする。
- **このPRはdocsのみの提案であり、実行時点のKaigo Ops production deployを行わない。** 別作業がmainを変更した場合はEが各runtime SHAを独立照合する。

## 5. 次の判定と責任

| Action | Owner | Blocking condition |
|---|---|---|
| Aのclaim-level evidence register / risk register提出、適用範囲の未確定を解消 | A | Aファイルなし／claim未確認 |
| Bの各節の根拠タイプ、サービス別適用性、人権・責任分担を確定 | B | B草案未確認 |
| Cの選択式preview、source、test、認証付きURLを提示 | C | 操作可能なpreview未確認 |
| R01〜R16 + P01〜P07 + U01〜U06の実行と証拠追記 | D | 実行可能な対象版がない |
| 関係専門職レビュー・リスク管理実務責任者レビュー | human reviewers | `EXPERT_REVIEW_NOT_DONE` |
| 最終の内容責任者公開承認、Eの統合公開判断 | E / content owner | `HUMAN_APPROVAL_NOT_DONE` |

**Worker Dの結論:** review scaffoldと現行の公開登録・Vercelメタデータは確認した。安全新機能の実際のadversarial/UI/privacyテストは未実施。よって `SAFETY_PARTIAL_WITH_GAPS`。公開承認なし、production公開不可。A〜Cの完了後にこの台帳を再実行・更新する。
