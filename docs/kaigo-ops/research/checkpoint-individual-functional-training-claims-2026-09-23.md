# 個別機能訓練加算 RH2-001〜006 Claim review checkpoint

更新日: 2026-09-23 JST

## Fresh canonical state

- current main: `dc92f9c82555e8fcb70dcff3c6dca07166d58af3`
- research branch: `docs/kaigo-ops-research-plan`
- promotion/fix head: `c4eeb2fcd4ff21355311960851c9cbcd7a3ebba5`
- PR: #51
- main vs research: diverged
- research ahead: 273
- research behind: 26

main側のsource/dataを正本として扱う方針は維持する。PR #51をそのままmergeしない。

## Review scope

national holdout の以下6件を独立reviewした。

- RH2-001: 個別機能訓練加算(I)イ・ロの配置時間
- RH2-002: (I)ロの同時2名配置
- RH2-003: (I)ロを満たせない日の(I)イ算定
- RH2-004: 病院・診療所・訪問看護ステーション等との連携による人員確保
- RH2-005: (I)ロの算定対象時間帯
- RH2-006: 基準配置の機能訓練指導員と加算要件の関係

## Primary sources

- 厚生労働省「令和6年度介護報酬改定に関するQ&A（Vol.1）」問53〜58（修正版）
  - https://www.mhlw.go.jp/content/001227740.pdf
- 厚生労働省告示第95号・十六「通所介護費における個別機能訓練加算の基準」
  - https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0
- 厚生労働省告示第19号「6 通所介護費」
  - https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- 厚生労働省の現行Q&A掲載ページおよび令和8年度介護報酬改定ページでcurrentnessを確認

Q&A質問文だけではpromotionしていない。問53〜58の回答本文、現行告示第95号、報酬告示を突合し、後続資料による当該論点の変更が確認されないことを確認した。

## Review result

6件をそれぞれatomic Claimとして `ANSWER / VERIFIED_CURRENT` へ昇格した。

1. 配置時間
   - 具体的な時間数の定めはない。
   - ただし、計画策定への主体的関与、直接訓練、効果評価等に必要な時間を踏まえた配置が必要。
   - 専従は必要だが常勤・非常勤は問わない。

2. (I)ロの2名配置
   - 合計で同時に2名以上の配置が必要。

3. (I)ロから(I)イへの日単位切替
   - 1名しか確保できない日は、(I)イの要件を満たす場合に(I)イを算定できる。
   - 実施体制が日によって異なることを利用者へ事前説明する。

4. 外部連携
   - 病院・診療所・訪問看護ステーション等との連携だけで必要人員を確保することはできない。
   - 加算を算定する通所介護事業所への配置が必要。

5. (I)ロの算定対象時間帯
   - 2名以上配置している時間帯に訓練を受けた利用者が(I)ロの対象。
   - それ以外の時間帯は、(I)イの要件を満たす場合に(I)イを算定できる。

6. 基準配置との関係
   - 基準配置の機能訓練指導員が加算の資格・専従要件も満たす場合、(I)イの1名として数えられる。
   - (I)イのために別の1名を追加する必要はない。
   - (I)ロではその者に加えてもう1名以上が必要。

## Implementation

- Claim Registry: `claims-v0.22.json`
  - total 55 claims
  - RH2-001〜006の6 atomic Claimsを追加
- Classifier: `research-coverage-classifier-v0.30.mjs`
- Claim Registry validator: `research-claim-registry-validate-v0.22.mjs`
- Claim Composition validator: `research-claim-compositions-validate-v0.9.mjs`
- Claim promotion benchmark: `claim-promotion-benchmark-v0.2.json`
  - 2 → 8 cases
- national holdout:
  - ANSWER: 6
  - REVIEW_REQUIRED: 14
- remuneration review queue:
  - individual-functional-training = COMPLETE
  - next priority = bathing-assistance

広い `review.remuneration.base-and-addons` は引き続き `REVIEW_REQUIRED`。
`source review COMPLETE` を `answerability COMPLETE` へ一般化していない。

## Classifier gate change

従来は `remuneration-review.json.review_status = IN_PROGRESS` の間、報酬キーワードを含むqueryをatomic Claim matchingより先に一律REVIEW_REQUIREDへ落としていた。

v0.30では、

- 明示的routingに一致する
- answerability = ANSWER
- verification_statusがverified

というatomic Claimが存在する場合だけ、そのClaimを広い報酬gateより先に通す。

該当するatomic Claimがない報酬queryは従来どおりfail-closed。

topic固有のclassifier special-caseは追加していない。

## CI

### run #31

- run id: `35831163720`
- result: FAILURE
- classifier execution自体は成功
- failure: RH2-005が、時間帯専用Claimと「同時2名配置」Claimの両方へroutingされ、後者が選ばれた

対処:
- 「同時2名配置」Claim側へ
  - 時間帯
  - 訓練を受けた
  - 算定対象時間
  をexcluded_termsとして追加。
- Q57/RH2-005を専用atomic Claimへ分離した。

### run #32

- run id: `35831348247`
- result: SUCCESS
- classifier v0.30: **197 / 197 PASS**
- Claim Registry: **55 claims / valid**
- Claim Composition validator: valid
- unit-price review validator: valid
- remuneration base review validator: valid
- remuneration delegated review validator: valid
- fee-guidance reconstruction sync: valid
- fee-guidance human review: valid
- deterministic fee-guidance regeneration: PASS

Run:
https://github.com/Josh-Temple/kaigo-rules/actions/runs/35831348247

## Remaining boundary

- broad remuneration answerability gate: CLOSED
- remaining national remuneration holdout: 14 REVIEW_REQUIRED
- RAG: HOLD

次は `remuneration.bathing-assistance` の RH2-007〜010 を同じ手順でatomic Claim reviewする。
