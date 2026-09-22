# Information Retrieval Benchmark

作成日: 2026-09-22  
状態: v0.1 seed + deterministic baseline completed

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
  - 11件のsafety / scope / currentness / ambiguity challenge
- `baseline-v0.1.md`
  - deterministic retrievalの初回結果
- `baseline-results-v0.1.csv`
  - question別の結果

## Reproduce

repo root:

```bash
node scripts/research-retrieval-baseline.mjs
```

dependencyは不要。

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

## v0.1 deterministic result

20問seedに対するcharacter-bigram TF-IDF:

- curated FAQ Hit@1: 95%
- curated FAQ Hit@3: 100%
- raw VERIFIED_CURRENT rule Hit@1: 95%
- raw VERIFIED_CURRENT rule Hit@3: 100%

ただし既存title/aliasから作ったseedなのでproduction performanceではない。

重要なのは、**clean small corpusではsimple retrievalがすでに強い**こと。

RAGは、単純なretrieval hitではなく、

- multi-source synthesis
- condition handling
- currentness
- citation correctness
- contradiction
- no-answer / abstention

で追加価値を示す必要がある。

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
11 challenges.

Measure:
- inappropriate answer rate
- stale-source use
- out-of-scope leakage
- unreviewed-source promotion
- false-premise acceptance
- ambiguity handling
- abstention accuracy

## Next

1. challenge setを実行可能なscoring形式にする
2. current navigation baselineを計測
3. simple keyword/full-text baselineを固定
4. curated FAQ answer baseline
5. source-grounded RAG candidate
6. 同一question setで比較
7. independent / unseen queryを追加
8. 50問へ拡張

50問化はDB coverageとhuman reviewの前進に合わせて行う。
