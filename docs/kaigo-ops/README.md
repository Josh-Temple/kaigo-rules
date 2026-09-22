# 介護業務改善 / Research & Product Notes

更新日: 2026-09-22

このディレクトリは、介護業務改善サイトと、その背後にある調査・更新方針を残すための記録です。

## 現在の構成

- **介護ルール**
  - 制度、基準、通知、Q&A、原典確認を担う。
  - 利用者が「制度上どうなっているか」を確認する場所。
- **介護業務改善**
  - 現場の困りごとを入口に、改善パターン、国内外の事例、論文、公的資料、導入条件を整理する。
  - AIは解決手段の一つであり、AI導入そのものを目的にしない。
- **Studio Lab**
  - 公開情報、事例、論文、公的資料の調査・比較・更新を担う研究エンジン。
- **Research Site**
  - 深いEvidence Review、方法、検証過程、否定的・不確実な結果を公開する研究側の出口。

## 基本方針

公開サイトの価値は「情報量」ではなく、利用者の検索・比較・判断コストを下げることに置く。

そのため、サイトには結論と行動を簡潔に出し、調査根拠や中間分析はGitHub側に残す。

### 情報の流れ

```text
現場のペイン
    ↓
Studio Lab
公開事例・論文・公的資料・海外事例の調査
    ↓
Research / evidence repository
根拠・比較・不確実性・更新履歴
    ↓
Research Site
Evidence Review / 方法 / 検証
    ↓
介護業務改善
実務向けの判断材料・改善パターン・最初の一歩
    ↕
介護ルール
制度・基準・Q&A・原典
```

## 重要な設計判断

1. 「介護ルール」と「介護業務改善」は利用目的が異なるため、公開面は分ける。
2. 現時点では同じGitHubリポジトリ内で管理し、Vercel Projectは分離する。
3. 介護業務改善は「AI活用サイト」ではなく「介護事業者の業務改善サイト」とする。
4. 技術や製品ではなく、現場の困りごとから情報へ入る。
5. 具体例だけでなく、複数事例・研究から比較的長く使える改善パターンを抽出する。
6. 海外事例は積極的に扱うが、日本への適用可能性を別途評価する。
7. 高頻度更新を目的化しない。初回の深い調査と、定期的な再調査・差分更新を重視する。
8. サイト数はKPIにしない。介護で型を検証してから他業界への展開を判断する。

## Current checkpoint

- [Claim-aware Router v0.1 checkpoint](./research/checkpoint-claim-aware-router-v0.1-2026-09-22.md)
- [Claim Registry v0.1 checkpoint](./research/checkpoint-claim-registry-v0.1-2026-09-22.md)

- [Research checkpoint 2026-09-22](./research/checkpoint-2026-09-22.md)
- [Benchmark v0.2 checkpoint](./research/checkpoint-benchmark-v0.2-2026-09-22.md)
- [Benchmark v0.3 checkpoint](./research/checkpoint-benchmark-v0.3-2026-09-22.md)

## Research outputs

### World landscape

- [World care DX / AI map plan](./world-care-dx-map-plan.md)
- [Initial landscape](./research/world-care-dx-map/initial-landscape.md)
- [Global source register](./research/world-care-dx-map/source-register.csv)
- [Structured case register](./research/world-care-dx-map/case-register.csv)
- [Japan transferability review](./research/world-care-dx-map/japan-transferability-v0.1.md)
- [Search log 2026-09-22](./research/world-care-dx-map/search-log-2026-09-22.md)

### Japan

- [日本の介護DX・ICT — 定量Evidence整理](./research/japan/japan-quantitative-evidence-2026-09-22.md)

### First deep Issue

- [必要な情報を探すのに時間がかかる](./research/issues/information-search/README.md)
- [Evidence register](./research/issues/information-search/evidence-register.csv)
- [Source coverage audit](./research/issues/information-search/source-coverage-audit.md)
- [実験計画](./research/issues/information-search/experiment-plan.md)
- [Benchmark v0.1](./research/issues/information-search/benchmark/README.md)
- [Deterministic baseline v0.1](./research/issues/information-search/benchmark/baseline-v0.1.md)
- [Deterministic baseline v0.2](./research/issues/information-search/benchmark/baseline-v0.2.md)
- [Pre-RAG benchmark suite v0.5](./research/issues/information-search/benchmark/benchmark-v0.5.json)
- [External MHLW Q&A query review](./research/issues/information-search/benchmark/external-qa-query-review-v0.1.md)
- [50-case non-RAG baseline v0.3](./research/issues/information-search/benchmark/baseline-v0.3.md)
- [Non-RAG Issue Router design](./research/issues/information-search/router-design-v0.1.md)
- [Benchmark v0.2 scoring](./research/issues/information-search/benchmark/scoring-v0.2.md)

### Claim-level coverage

- [Claim Registry v0.1](./research/claims/claims-v0.1.json)
- [Claim Registry schema](./research/claims/claim-registry.schema.json)
- [Claim promotion flow](./research/claims/claim-promotion-flow.md)

### Methods

- [Product strategy](./product-strategy.md)
- [Research protocol](./research-protocol.md)
- [Evidence Register Schema](./research/evidence-schema.md)
- [Roadmap](./roadmap.md)

## Reproducible research tools

- `node scripts/research-retrieval-baseline.mjs`
  - verified question / rule corpusに対する決定論的retrieval baseline
