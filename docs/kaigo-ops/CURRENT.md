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

2026-10-07のfresh確認では、Kaigo Ops production bundleにVercel Web Analyticsのclient implementationは存在する。

一方、current productionではAnalytics script / intake routeが404で、pageview収集開始は確認できない。Web Analytics APIの確認値も `visitors: 0 / pageviews: 0`。

したがって現時点では、Analyticsを「稼働済み」「観測開始済み」と扱わない。

初期観測はpageviewだけとし、対象・解釈・非収集データは `docs/kaigo-ops/measurement.md` を正本として確認する。

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
