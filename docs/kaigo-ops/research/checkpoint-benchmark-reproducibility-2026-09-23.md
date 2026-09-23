# Kaigo Ops Research Checkpoint — Benchmark Reproducibility Audit

更新日: 2026-09-23  
状態: **harness defect fixed / 191-check rerun pending**

## 発見した不整合

benchmark/checkpointでは自治体queryを25件として扱い、classifier checksを191件として記録していた。

しかし、`research-coverage-classifier-v0.19.mjs` から `v0.22.mjs` までを確認すると、実際に読み込んでいたのは

`municipal-query-sample-v0.4.json` = 15件

だった。

現在の正本は

`municipal-query-sample-v0.5.json` = 25件

であり、大阪市由来のMQ-016〜MQ-025が追加されている。

したがって、旧harnessをそのまま実行した場合の総チェック数は181件で、記録上の191件とは一致しない。

## 対応

`research-coverage-classifier-v0.23.mjs` を作成。

変更:
- municipal sample: v0.4 → v0.5
- classifier version表示: 0.23
- Claim Registry表記: v0.15
- suite cardinalityをfail-closedで検査
- expected total checks: 191 をharness metadataへ明記

classifierのanswerability/routingロジック自体は変更していない。

## 追加10件の静的確認

MQ-016〜MQ-025は全て、
- 「大阪市」という明示的な自治体context
- 指定事業者 / 指定申請 / 指定前 / 先に指定 / 営業開始 等

を含む。

現行の `isLocalAuthoritySpecific()` の条件には静的には一致するため、expected `LOCAL` と整合する。

ただし、これはコード読解による確認であり、実行結果ではない。

## 数値の扱い

旧記録:
- 191 / 191

現在の扱い:
- **historically reported**
- **current harnessでの再現未確認**

再実行するまで、新たに「191/191 PASS」とは記録しない。

## 次

1. Node実行可能な環境でv0.23を実行
2. 実測結果を保存
3. その後、raw RAG holdout 30件の独立ラベル付けを進める

再現性が閉じるまでRAG実装には進まない。
