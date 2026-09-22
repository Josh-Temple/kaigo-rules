# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: v0.1 seed

## 目的

介護ルールを使って、

- navigation
- full-text / keyword search
- structured FAQ
- source-grounded RAG

を同じground truthで比較する。

## Files

- `questions-v0.1.csv`
  - 現在の検証済み12問
  - そのうち8問のparaphrase
  - 計20問
- `challenges-v0.1.csv`
  - 10件のsafety / scope / currentness challenge

## Rule

### Ground truthは先に固定する

回答systemの出力を見てgold answerを変更しない。

### verified sourceだけで採点する

`INGESTED_UNREVIEWED` や `NOT_STARTED` review layerを、
正解根拠へ勝手に昇格させない。

### Answerabilityも採点対象

正答だけでなく、

- abstain
- ask for missing condition
- point to local authority
- distinguish unreviewed source

が正解になるquestionを含める。

## v0.1 evaluation

### Core
20 questions.

Measure:
- exact/semantic answer correctness
- required condition retention
- source correctness
- citation entailment
- time to correct source

### Safety
10 challenges.

Measure:
- inappropriate answer rate
- stale-source use
- out-of-scope leakage
- unreviewed-source promotion
- false-premise acceptance
- abstention accuracy

## Next

1. benchmark runner formatを決める
2. current navigation baselineを計測
3. simple keyword/full-text baselineを作る
4. curated FAQ baseline
5. RAG candidate
6. 同一question setで比較
7. 50問へ拡張

50問化はDB coverageとhuman reviewの前進に合わせて行う。
