# Kaigo Ops — Current Projection

Updated: 2026-10-07
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

2026-10-07のWorker E releaseで、Kaigo Opsはrelease main SHA `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2` をproduction deployment `dpl_3SiLHr9Nf3MEgmACbWmvEy4ihXZq` として反映し、`READY` とproduction alias割当を確認した。

Vercel Web Analyticsのclient implementationは存在し、productionではcompatibility routeとResilient Intake scriptのHTTP 200配信を確認した。2026-10-07のWorker A fresh確認では、開始時 `visitors: 0 / pageviews: 0` だったWeb Analytics APIが、その後 `visitors: 1 / pageviews: 1`、requestPath `/` = 1となった。受信browserはFirefox / desktopで、controlled PlaywrightのChromium trafficとは一致しない。

controlled Playwrightではpageview callが `window.vaq` に積まれる一方、deployed Analytics scriptの自動化判定により送信されないことも確認した。このtrafficは実利用値に含めない。

したがってAnalytics stateは **production pageview receive confirmed / observation started 2026-10-07** とする。1 pageviewから需要や改善効果は判断しない。

初期観測はpageviewだけとし、対象・解釈・非収集データは `docs/kaigo-ops/measurement.md` を正本として確認する。

継続観測と2〜4週間レビューは `docs/kaigo-ops/usage-observation.md`、feedbackの内部triageは `docs/kaigo-ops/feedback-triage.md`、公開入口・indexabilityの監査結果は `docs/kaigo-ops/discoverability.md` をcanonical projectionとして参照する。

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

2026-10-07 Utilization & Actionability Wave:

- integration PR: #421
- release main SHA: `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2`
- Kaigo Ops deployment: `dpl_3SiLHr9Nf3MEgmACbWmvEy4ihXZq`
- deployment state: `READY`
- production alias: `https://ops-site-pi.vercel.app/`
- five public Issues: maintained
- five action tools: integrated
- contextual Kaigo Rules bridge: 5 / 5 Issues
- generic Kaigo Rules bridge: 5 / 5 Issues
- minimal feedback path: 5 / 5 Issues

Repository-side `Validate ops site` passed `npm test`, `npm run build`, and route smoke verification on the integrated release source. Vercel deployment metadata confirms the same release SHA and READY state。

Production verification also passed the public route/journey checks and 390px browser verification for the home page, all 5 Issue routes, all 5 action-tool routes, and all 5 Issue → tool / Kaigo Rules / feedback journeys. Analytics script delivery is confirmed, and Worker A subsequently confirmed Vercel-side production pageview receive.

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
