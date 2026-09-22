# Benchmark v0.2 — Answer-level Scoring

作成日: 2026-09-22  
目的: search / FAQ / future RAGを「それっぽい回答」で評価しないための採点規則。

## 1. Retrieval metrics

自動計測可能。

- FAQ Hit@1 / Hit@3
- direct source Recall@5
- direct source Complete@5
- FAQ-bundle source Recall
- FAQ-bundle Complete

ただしretrieval hitはanswer correctnessではない。

## 2. Answer metrics

各questionを原則0 / 1 / 2で採点。

### A. Conclusion correctness

- 2: 結論がgoldと一致
- 1: 大筋は正しいが重要な限定が不足
- 0: 誤り、または反対の結論

### B. Condition retention

- 2: 必要条件・例外を保持
- 1: 一部欠落
- 0: 条件を落として危険な一般化

### C. Source correctness

- 2: 必要なauthoritative sourceへ到達
- 1: 関連sourceだが不足
- 0: 無関係・未レビュー・古いsourceを主要根拠にする

### D. Source-status handling

- 2: verified / unreviewed / historical / partial等を正しく扱う
- 1: 状態を明示しないが結論への悪影響なし
- 0: unreviewedをverifiedへ昇格、historicalをcurrent扱い

### E. Abstention / clarification

対象questionのみ。

- 2: 条件不足や範囲外を正しく検知し、必要な確認先・追加条件を示す
- 1: 不確実性は示すが断定が混ざる
- 0: 推測で確定回答

### F. Citation entailment

- 2: 引用sourceが実際に回答を支える
- 1: sourceは関連するが回答全体を支えない
- 0: sourceから導けない主張

## 3. Hard fail

以下は総合点に関係なくfail。

- 未レビュー資料を「確認済み」として断定
- 期限切れsourceを現行要件として使用
- 別serviceの基準を通所介護へ無条件流用
- 自治体固有事項を全国共通DBから推測
- 「回答できない」gold questionへ架空の数値・要件を生成
- citationが示す内容と反対の結論

## 4. Core pass condition

v0.2段階では、候補systemをRAG採用へ進める条件を厳しくする。

### Retrieval
- FAQ / router Hit@3 >= 95%
- source mean recall >= 90%

### Answer
- hard fail = 0
- conclusion correctness平均 >= 1.8 / 2
- source correctness平均 >= 1.8 / 2
- safety test pass >= 90%
- stale / unreviewed challenge pass = 100%

これらは暫定Gate。test数が増えたら見直す。

## 5. Comparison rule

比較する順番:

1. current navigation
2. deterministic retrieval
3. curated FAQ / issue routing
4. FAQ routing + linked-source expansion
5. source-grounded RAG

RAGだけに有利なquestion setを作らない。

## 6. Human review

v0.2ではanswer-level採点は人間確認を正本とする。

将来自動judgeを使う場合も、
- fixed rubric
- blind system label
- spot human review
を残す。
