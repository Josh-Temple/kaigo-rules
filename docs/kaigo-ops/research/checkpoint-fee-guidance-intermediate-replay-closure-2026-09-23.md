# Kaigo Ops Research Checkpoint — Fee Guidance Intermediate Replay Closure

更新日: 2026-09-23  
判定: **5 COMPLETE / 3 REVIEW_REQUIRED / overall IN_PROGRESS**

## 1. 追加確認した一次資料

平成30年度介護報酬改定の老企第36号新旧対照表:
https://www.mhlw.go.jp/content/12404000/1.pdf

令和3年度介護報酬改定の老企第36号新旧対照表:
https://www.mhlw.go.jp/content/12404000/000772367.pdf

## 2. fee-guidance.dayservice.4

「2時間以上3時間未満の通所介護を行う場合の取扱い」

確認した連鎖:
- H27: baseline本文
- H30: 通所介護費7(1)・(2)は新旧とも「略」
  - 当時7(2)だった短時間利用の本文変更は示されていない
- R3: 通所介護費7(1)〜(3)は新旧とも「略」
  - 当時7(2)の本文変更は示されていない
- R6: 高齢者虐待防止措置未実施減算・BCP未策定減算を7(2)・7(3)へ新設
  - 旧7(2)系統は現行7(4)へ番号移動
- R7: 通所介護部分の変更なし
- R8 3月: 6〜9変更なし
- R8 5月: 7(1)〜(24)変更なし

判定:
**HUMAN REVIEW COMPLETE**

candidate SHA:
`953fce60c7811569750a43586280f920a83b7146359c7e8f4b2068a4d1da55c8`

## 3. fee-guidance.dayservice.7

「災害時等の取扱い」

確認した連鎖:
- H27: baseline本文
- H30: 通所介護費7(5)は新旧とも「略」
  - 本文変更は示されていない
- R3: 通所介護費7(5)は新旧とも「略」
  - 本文変更は示されていない
- R6: 2項目新設により旧7(5)系統は現行7(7)へ番号移動
- R7: 通所介護部分の変更なし
- R8 3月: 6〜9変更なし
- R8 5月: 7(1)〜(24)変更なし

判定:
**HUMAN REVIEW COMPLETE**

candidate SHA:
`99bb42d59dc56461fa57c0e206c105395cff1909c21fbcd731e6f21fb1c17417`

## 4. Current state

老企第36号8候補:
- COMPLETE: 5
  - dayservice.4
  - dayservice.7
  - dayservice.7-2
  - dayservice.24
  - dayservice.25
- REVIEW_REQUIRED: 3
  - dayservice.5
  - dayservice.6
  - dayservice.18

残る3件は、いずれも現在のbaseline候補本文そのものに「略」が残る。

## 5. Fail-closed

更新:
- `data/fee-guidance-replay-coverage.json`
- `data/fee-guidance-review.json`
- `data/remuneration-review.json`
- `research-fee-guidance-sync-validate-v0.1.mjs`
- `research-fee-guidance-review-validate-v0.1.mjs`

生成candidate自体の `human_verification_status` は変更しない。
human reviewはreview ledgerとreplay ledgerに分離して保持する。

## 6. Next

残る3件:
1. 延長加算 — ①〜③の省略部分
2. 事業所規模 — ③・④の省略部分
3. 栄養改善 — ①、③、④イ〜ハ・ホ・ヘ、⑤等の省略部分

別の公式資料から欠落本文を埋め、
改正履歴をcurrentまでreplayできる場合のみCOMPLETEへ進める。

報酬全体のClaim gateはまだ開けない。
RAGもHOLDを維持する。
