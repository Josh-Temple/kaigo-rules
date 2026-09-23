# 送迎減算 RH2-012〜014 Claim review checkpoint

更新日: 2026-09-23 JST

## Fresh canonical state

- current main: `02147c9dcfe53c5702e47ddbc08a5326004db116`
- research branch before checkpoint: `a266ee0f9112d5b173aab7dd741a496e03f90117`
- PR: #51
- main vs research: diverged
- research ahead: 277
- research behind: 28

main側のsource/dataを正本として扱う方針は維持する。PR #51をそのままmergeしない。

## Review scope

national holdout の以下3件を独立reviewした。

- RH2-012: 居宅以外の居住実態のある場所への送迎
- RH2-013: 他事業所従業者による送迎・同乗
- RH2-014: 第三者委託・共同委託による送迎

## Primary sources

- 厚生労働省「令和6年度介護報酬改定に関するQ&A（Vol.1）」問65〜67
  - https://www.mhlw.go.jp/content/001227740.pdf
- 厚生労働省告示第19号「6 通所介護費」注24
  - https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- 厚生労働省・国土交通省「介護サービス事業所・障害福祉サービス事業所の送迎業務の効率化及び地域交通との連携について」（令和6年10月11日）
  - https://kouseikyoku.mhlw.go.jp/chugokushikoku/chiiki_000426575.pdf
- 厚生労働省「介護サービス関係Q&A」現行掲載ページ
  - https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/qa/index.html

Q&A質問文だけでなく回答本文、現行報酬告示、後続通知を突合した。
後続通知は問65〜67を前提に送迎共同化・居住実態のある場所・第三者委託の条件を再整理している。

## Review result

3件をatomic Claimとして `ANSWER / VERIFIED_CURRENT` へ昇格した。

### RH2-012 居宅以外の場所への送迎

送迎は利用者の居宅と事業所間が原則。

ただし、親族宅など利用者の居住実態がある場所について、

- 事業所のサービス提供範囲内である等、運営上支障がない
- 利用者本人の同意
- 利用者家族の同意

を満たす場合に限り、事業所と当該場所間の送迎に送迎減算は適用されない。

任意の場所への送迎を一律に減算対象外とはしない。

### RH2-013 他事業所従業者による送迎・同乗

A事業所の利用者をB事業所の従業者が送迎する場合、原則としてA事業所の従業者が送迎していないため送迎減算が適用される。

ただし、B事業所の従業者がA事業所とも雇用契約を締結していれば、A事業所の従業者でもあるためこの限りではない。

A・B利用者の同乗は、

- 必要な雇用契約
- 費用負担・責任の所在等について事業所間で合意
- 利用者の利便性を損なわない送迎範囲
- 各事業所の通常の事業実施地域内

という条件で差し支えない。

### RH2-014 第三者委託・共同委託

送迎業務を第三者へ委託し、受託事業者が利用者の居宅と事業所間を送迎した場合、送迎減算は適用されない。

別事業所への委託や複数事業所による共同委託でも、

- 委託契約
- 費用負担・責任の所在等について事業者間で合意
- 利用者の利便性を損なわない送迎範囲
- 各事業所の通常の事業実施地域内

を満たす場合、利用者の同乗が可能。

道路運送法上の許可・登録等は対価や契約形態により別論点のため、このClaimだけで判断しない。

## Implementation

- Claim Registry: `claims-v0.24.json`
  - 59 → **62 claims**
- 追加:
  - `claim.remuneration.transport-reduction.other-residence`
  - `claim.remuneration.transport-reduction.other-business-employee`
  - `claim.remuneration.transport-reduction.third-party-outsourcing`
- source node:
  - `fee.dayservice.note.24`
- Classifier: `research-coverage-classifier-v0.32.mjs`
- Claim Registry validator: `research-claim-registry-validate-v0.24.mjs`
- Claim Composition validator: `research-claim-compositions-validate-v0.11.mjs`
- Claim promotion benchmark: `claim-promotion-benchmark-v0.4.json`
  - 12 → **15 cases**
- national remuneration holdout:
  - ANSWER: **13**
  - REVIEW_REQUIRED: **7**
- remuneration review queue:
  - individual-functional-training = COMPLETE
  - bathing-assistance = COMPLETE
  - transport-reduction = COMPLETE
  - next priority = three-percent-scale-exception

広い `review.remuneration.base-and-addons` は引き続き `REVIEW_REQUIRED`。
送迎減算をumbrella Claimのrouting対象から除外し、検証済みatomic Claimだけでanswerabilityを開く。

## CI

run #36
- run id: `35836622274`
- conclusion: **SUCCESS**
- classifier v0.32: **204 / 204 PASS**
- Claim Registry: **62 claims / valid**
- Claim Composition validator: valid
- unit-price review validator: valid
- remuneration base review validator: valid
- remuneration delegated review validator: valid
- fee-guidance reconstruction sync: valid
- fee-guidance human review: valid
- deterministic fee-guidance regeneration: PASS

Run:
https://github.com/Josh-Temple/kaigo-rules/actions/runs/35836622274

## Remaining boundary

- broad remuneration answerability gate: CLOSED
- remaining national remuneration holdout: **7 REVIEW_REQUIRED**
- RAG: HOLD

次は `remuneration.three-percent-scale-exception` の RH2-015〜020 を優先する。
