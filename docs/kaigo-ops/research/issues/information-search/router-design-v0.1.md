# Non-RAG Issue Router v0.1

状態: Research baseline only  
本番利用: **不可**

## 目的

Kaigo Rulesの既存構造を使い、

```text
自然文質問
  ↓
Issue候補
  ↓
明示済みsource relation
  ↓
verification/currentness gate
  ↓
回答材料
```

をLLMなしでどこまで実現できるか確認する。

## Routing

character bigram TF-IDF / cosine。

index:
- title
- aliases
- short_answer
- practical_steps
- cautions

top-3まで保持。

top-1を即答先として固定しない。

## Evidence expansion

Issueに既に紐づく:

- `rule_node_ids`
- `notice_node_ids`
- `qa_item_ids`

をunionする。

検索engineに法令関係を再発見させない。

## Guards

answer routingより先に適用。

1. local-rule guard
2. service-scope guard
3. human-review-status guard
4. currentness guard
5. corpus provenance guard
6. short-query ambiguity guard

## Why top-3

v0.3ではHit@1 92.3%、Hit@3 100%。

top-1に固定すると、
近接Issueの誤選択をそのまま回答へ伝播する。

top-3から、
- relation expansion
- clarification
- future reranking
へ回す余地を残す。

## What this is not

- semantic searchの完成版ではない
- RAGではない
- 法令判断engineではない
- 自治体独自基準を含まない
- 未レビューdataを答える仕組みではない
- free-form answer generatorではない

## Production前に必要

- broader coverage
- real / external query sample
- false-positive guard test
- threshold calibration
- answer-level human review
- latency / UX evaluation
- source state transition test
