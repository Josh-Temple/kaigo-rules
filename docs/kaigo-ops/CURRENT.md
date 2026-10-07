# Kaigo Ops — Current Projection

Updated: 2026-10-08
Status: current routing projection

このファイルは、Kaigo Opsで「現在そのまま再利用してよい知識」と「まだcurrent verified factとして扱わない知識」を短く確認するためのprojectionです。

正本を置き換えません。詳細な根拠・研究・検証状態は必ずリンク先で確認してください。

## Precedence

現在状態について矛盾がある場合は、次の順で扱います。

1. current `main` のcanonical data / review ledgers
2. `docs/kaigo-ops/research/README.md` のcurrent-state guard
3. current issue research
4. historical / recovered checkpoint

historical checkpointにある完了表現を、そのままcurrent verifiedへ昇格しません。

## Currently reusable

### 記録・文書作成

Current issue:
`docs/kaigo-ops/research/issues/documentation/README.md`

現在のEvidence synthesisから再利用できる実務上の順序:

1. 不要な記録・重複入力を特定する
2. 正本と入力元を決める
3. 一度入力した情報を再利用する
4. 紙・FAX・別システム間の転記を減らす
5. その後で音声入力、要約、AI draftを比較する
6. AI出力を正式記録へ入れる場合は、人間の確認責任を残す

AI導入自体を目的にせず、通常のICT・workflow改善で十分なら生成AIを追加しない。

### Information retrieval

Machine retrieval benchmarkの結果は、固定queryに対する検索導線・context integrityの機械的再現性として利用できる。

ただし、人間の探索時間短縮、使いやすさ、業務効率向上の実証とは扱わない。

Human field validationは `OPTIONAL_EXTERNAL_VALIDATION / NOT_RUN`。

## Measurement state

2026-10-08のPublic Discovery & Observation Operations Waveでは、integration PR #434をmainへ統合したruntime release SHA `81a307738d7a40562ad033c3d2491cd05a2f2337` を、Kaigo OpsとKaigo Rulesの両productionへexact SHAで反映した。

- Kaigo Ops: `dpl_6JuE6Cm2UnxFVvQdDZTV4cCRkhY1` / `https://ops-site-pi.vercel.app/` / `READY`
- Kaigo Rules: `dpl_5Ee8hKCoxAaQywaxxQGhJWypNDru` / `https://kaigo-rules.vercel.app/` / `READY`

Vercel Web Analyticsは **RECEIVE_CONFIRMED** を維持し、first confirmed observation dateは **2026-10-07**。release後のfresh aggregateでも、home `/` = **7 pageviews / 6 visitors** で、5 Issueと5 action toolにはrequestPath集計行がない。browserはChrome 6 pageviews / 5 visitors、Firefox 1 / 1、deviceTypeはdesktop 7 / 6だった。

この値は閲覧の観測値であり、外部実利用者数、需要、改善効果、tool実行完了を示さない。今回のproduction verificationはheadless / webdriverで実施しており、deployed Analytics scriptの既存自動化除外を前提にcontrolled verification trafficを実利用値へ読み替えない。

Kaigo Ops feedbackはtitle prefix `[Kaigo Opsフィードバック]` でopen / closedとも0件。0件を失敗、満足、需要なしの証拠にはしない。

Search Consoleは認証済み接続が利用できないため、property、sitemap submission、major 6 URL index state、Google-selected canonicalは `UNKNOWN`、indexing requestは `NOT_RUN`。詳細は `docs/kaigo-ops/search-discovery-observation.md` を正本とする。

custom eventは **CUSTOM_EVENT_NOT_JUSTIFIED**。現時点ではpageviewだけでは答えられない具体的な意思決定が特定されておらず、観測母数も極小のため追加しない。earliest review targetは **2026-10-21前後**、broader review windowは **2026-10-21〜2026-11-04前後**。

### Public discovery / contextual entry

Kaigo Ops productionでは、home + 5 Issue + 5 action tool、`robots.txt`、`sitemap.xml`、Issueページのcanonical / Open Graph、Analytics script deliveryを確認済み。390px production verificationでも11 routeと5つのIssue → tool / Kaigo Rules / feedback journeyがPASSした。

Kaigo Rules productionの `/databases/search` には、制度上の要件を確認した後に業務見直しへ進む文脈付き入口を反映済み。direct linkは情報探索と記録・文書の2 Issueに限定し、Kaigo Opsが制度適合を確定しない境界を同じ入口で明示する。

第三者へ直接共有する場合の対象・紹介文・non-claimsは `docs/kaigo-ops/distribution-kit.md` をcanonical public-entry recordとする。外部投稿は明示的な許可なしに実行しない。

## Actionability / public journey

2026-10-07のUtilization & Actionability Waveでは、5つの公開Issueすべてに「読んだ後に試す」入口を揃えた。

- 情報探索: `/tools/information-inventory`
- 記録・文書: `/tools/documentation-review`
- 教育・引き継ぎ: `/tools/training-handover-inventory`
- 問い合わせ・連携: `/tools/communication-review`
- 稼働率・生産性: `/tools/work-time-review`

新規4ツールはclient-side中心で、accountやserver保存を前提にしない。氏名、利用者情報、介護記録本文などの入力を求めず、ツール利用だけで改善成功や制度適合を判定しない。

5 Issueすべてで、具体的なKaigo Rulesの公開DB検索への導線と、Kaigo Rulesトップへの汎用導線を併存させる。サービス適用範囲はKaigo Ops側で推定せず、Kaigo Rules側の検証状態と一次資料へ戻って確認する。

フィードバックはGitHub Issuesを再利用し、「何を試したか」「どこで止まったか」「何が足りなかったか」を最小入力として案内する。投稿はGitHub上で公開・保存されるため、個人情報、介護記録、事業所の非公開情報を記載しないよう明示する。

Issue 6「収支・コスト構造」は開始していない。Analyticsの実受信は確認できたが母数はまだ極小のため、現時点で需要や改善効果は断定しない。

## Production release state

2026-10-08 Public Discovery & Observation Operations Waveのproduction state:

- integration PR: #434
- integrated runtime SHA: `81a307738d7a40562ad033c3d2491cd05a2f2337`
- Kaigo Ops deployment: `dpl_6JuE6Cm2UnxFVvQdDZTV4cCRkhY1`
- Kaigo Ops alias: `https://ops-site-pi.vercel.app/`
- Kaigo Rules deployment: `dpl_5Ee8hKCoxAaQywaxxQGhJWypNDru`
- Kaigo Rules alias: `https://kaigo-rules.vercel.app/`
- both deployments: `READY`
- integration CI: `Validate build` PASS
- Kaigo Ops CI: `Validate ops site` PASS
- publication-readiness integration: PASS
- production verifier run: `37653052826` PASS
- Kaigo Ops home + 5 Issue + 5 action tool: PASS
- Issue → tool / Kaigo Rules / feedback: 5 / 5 PASS
- Kaigo Rules → Kaigo Ops contextual entry: PASS
- canonical / Open Graph / robots / sitemap: PASS
- Analytics script delivery: PASS
- 390px verification: PASS
- custom event: not added
- Issue 6 / new feature: not added

The current production runtime for both public surfaces is the integrated SHA above. Documentation-only finalization after this release does not require a runtime redeploy.

## Current non-claims

現時点では、次をcurrent verified factとして一般化しない。

- 「生成AIで介護記録の作業時間が○％減る」
- 「AIなら介護記録時間を大幅に減らせる」
- 「音声要約で記録品質が上がる」
- 「生成AIの方が通常入力より費用対効果が高い」
- machine retrieval benchmarkのPASSを、人間の時間削減や使いやすさの証拠とすること

特に、現在のKaigo Ops researchには、日本の介護現場におけるGenAI documentationのvalidated human time-reduction percentageを、そのまま再利用できる形では保持していない。

外部ICT導入調査、workflow変更を伴う効果測定、self-report、machine benchmarkの数値を、生成AI単体の因果効果へ変換しない。

## Regulation boundary

制度上の義務・要件・許容範囲はKaigo Opsで確定しない。

- 法令
- 基準省令
- 報酬
- 解釈通知
- 国Q&A
- current verification state

は、同じRepositoryの介護ルール側canonical dataへ戻って確認する。

## Update rule

このprojectionを更新するのは、次のいずれかが変わったときだけ。

- current issue researchの結論またはnon-claim
- human validation state
- canonical review ledger / answerability gate
- 公開siteで再利用するcurrent knowledge boundary

記事追加やhistorical checkpoint追加だけでは更新しない。
