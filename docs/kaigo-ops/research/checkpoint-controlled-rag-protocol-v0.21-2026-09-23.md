# Kaigo Ops Research Checkpoint — Controlled RAG Protocol v0.21

更新日: 2026-09-23  
状態: **protocol fixed / implementation not started**

## 今回の判断

RAG実装へ直行せず、比較条件を先に固定した。

理由:
- 現在の190-case suiteはrouter改善に繰り返し使われている
- baselineのdecision layerは既に強い
- RAGの価値は既存setへのfitではなく、未知表現・新しいsource coverageで測る必要がある

## 固定した比較

- Arm A: current Claim-aware non-RAG
- Arm B: verified-only RAG candidate
- Arm C: broad-corpus retrieval negative control

Arm Cはproduction候補ではなく、未レビュー資料を広く検索した場合のcontamination測定用。

## 重要な順序

```text
answerability gate
 ↓
retrieval
 ↓
Claim / source consistency
 ↓
optional generation
```

RAGをanswerability判定の代替にしない。

## Test strategy

既存190 cases:
- frozen regression suite

新規:
- 30〜50件のexternal holdout
- current registryを見ながら質問を作らない
- query収集後にexpected label / Claim / sourceを別工程で固定

## Hard fail

- false ANSWER
- LOCALの全国化
- scope外類推
- REVIEW_REQUIREDの確定回答化
- currentness違反
- unreviewed source leakage
- verified Claimの意味すり替え

## 現在

RAG code / vector DB / embeddingはまだ導入していない。

次はholdout作成から進める。
