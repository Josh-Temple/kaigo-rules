# Kaigo Ops Research Checkpoint — Fee Guidance 8/8 Source Review Closure

更新日: 2026-09-23  
対象: 老企第36号「7 通所介護費」reconstruction / human review  
判定: **source review COMPLETE / answerability gate CLAIM_COVERAGE_PENDING**

## 1. 結果

machine-reconstructed candidate 8件:
- dayservice.4: COMPLETE
- dayservice.5: COMPLETE
- dayservice.6: COMPLETE
- dayservice.7: COMPLETE
- dayservice.7-2: COMPLETE
- dayservice.18: COMPLETE
- dayservice.24: COMPLETE
- dayservice.25: COMPLETE

8 / 8 human review COMPLETE。

## 2. 今回閉じた3件

### dayservice.5 — 延長加算

H30現行側候補に残っていた `①～③（略）` を、
H27改正後欄の一次資料本文で補足。

補足後candidate SHA:
`52299586ab944552d50be716a41824cf72ff8a9ab4ef637cd3bfa9e96ce87d69`

確認:
- ① 9時間の通所介護後に5時間延長
- ② 前2時間＋後3時間 = 5時間 / 250単位
- ③ 8時間通所介護＋5時間延長 = 通算13時間、4時間分 / 200単位
- 事業所設備を利用した宿泊との組合せでは延長加算を算定しない取扱い
- H30の時間区分改正後、R3・R6・R7・R8で当該具体例の後続変更が示されていない

### dayservice.6 — 事業所規模

R3候補の `③・④（略）` をH27改正後欄から補足。

補足後candidate SHA:
`ab291bceb57f5bbf6afb2e3ea07893d04df7a31973d639af98d6556224b258c2`

確認:
- ③ 前年度実績6月未満等の場合の平均利用延人員数の便宜計算
- ④ 3月31日時点で継続事業を行う場合の前年度平均利用延人員数
- H30・R3・R6・R7・R8の改正履歴を確認
- ⑤感染症・災害特例は既存candidateで保持

### dayservice.18 — 栄養改善

R3候補で「略」とされた不変部分をH27本文から補足し、
H30/R3で実際に改正された部分はR3 candidate側を維持。

補足後candidate SHA:
`feacaff9cc903477ca248e9611fa5ee2bec333672701a0e9a08a5288cbf0717a`

確認:
- H30: 管理栄養士を外部連携でも確保可能とする②の改正
- R3: ②の連携先詳細化、④ニの居宅訪問による食事状況等の把握を追加
- その他の①、③、④イ〜ハ・ホ・ヘ、⑤は一次資料で補足
- R6・R7・R8で当該本文の後続変更が示されていない

## 3. 再構成設計

追加:
`data/fee-guidance-verified-text-supplements.json`

原則:
- machine extractを人手で上書きしない
- 補足本文をsource evidenceとして別管理
- assemblerは明示された省略markerだけを置換
- marker不存在・重複はfail
- candidate hashをhuman review ledgerに固定
- CIでassemblerを再実行し、checked-in candidateとdiffゼロを要求

## 4. Review ledger

`data/fee-guidance-review.json`
- review_status: COMPLETE
- reviewed_nodes: 8 / 8
- blocked_nodes: 0

`data/remuneration-review.json`
- base_notice_review: COMPLETE
- delegated_review: COMPLETE
- fee_guidance_review: COMPLETE
- source_review_status: COMPLETE
- answerability_gate_status: CLAIM_COVERAGE_PENDING
- review_status: IN_PROGRESS

## 5. なぜremuneration overallをCOMPLETEにしないか

source reviewの完了と、任意の報酬質問への回答可能性は別。

外部national holdout 20件には、
- 個別機能訓練加算
- 入浴介助加算
- 送迎減算
- 3%加算
- 事業所規模特例

等の細かなQ&Aが含まれる。

これらを広い `review.remuneration.base-and-addons` 1件で一括ANSWERにすると、
「資料を確認した」ことを「全subtopicをClaim検証した」ことへ誤って拡張する。

したがって:
- source review: CLOSED
- Claim coverage: OPEN
- answerability gate: CLOSED

と分離する。

## 6. 次

1. national holdout 20件をsubtopic群へ分解
2. current MHLW Q&A + 告示 + 老企36を使ってClaim作成/独立review
3. Claim-level regressionを追加
4. 報酬answerability gateの再判定
5. その後controlled RAG comparisonを検討

RAGはまだ実装しない。
