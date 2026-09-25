# 介護業務改善 / Research & Product Notes

更新日: 2026-09-25

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

- [Combined Staffing Claim Promotion](./research/checkpoint-combined-staffing-promotion-2026-09-23.md)
- [Claim Promotion v0.23](./research/checkpoint-claim-promotion-v0.23-2026-09-23.md)
- [Benchmark Reproducibility Audit](./research/checkpoint-benchmark-reproducibility-2026-09-23.md)
- [National RAG Holdout Labeling](./research/checkpoint-rag-holdout-national-labeling-v0.1-2026-09-23.md)
- [Controlled RAG Protocol v0.21](./research/checkpoint-controlled-rag-protocol-v0.21-2026-09-23.md)
- [Safety Prose v0.20 checkpoint](./research/checkpoint-safety-prose-v0.20-2026-09-23.md)
- [Outdoor Service Source Audit v0.19](./research/checkpoint-outdoor-source-audit-v0.19-2026-09-23.md)
- [Current-Source Reconstruction checkpoint](./research/checkpoint-current-source-reconstruction-v0.18-2026-09-23.md)
- [Second Municipal Source checkpoint](./research/checkpoint-second-municipal-source-v0.17-2026-09-23.md)
- [Hairdressing / Visiting Medical checkpoint](./research/checkpoint-hairdressing-visiting-medical-v0.16-2026-09-23.md)
- [Outdoor Service checkpoint](./research/checkpoint-outdoor-service-v0.15-2026-09-22.md)
- [Municipal Claim Review checkpoint](./research/checkpoint-municipal-claim-review-v0.14-2026-09-22.md)
- [Expanded External Query checkpoint](./research/checkpoint-external-query-v0.12-2026-09-22.md)
- [Important Matters Claims checkpoint](./research/checkpoint-important-matters-claims-v0.1-2026-09-22.md)
- [Multi-Claim Composition checkpoint](./research/checkpoint-multi-claim-composition-v0.1-2026-09-22.md)
- [Issue Fallback Audit checkpoint](./research/checkpoint-issue-fallback-audit-v0.1-2026-09-22.md)
- [Verified Claim Routing checkpoint](./research/checkpoint-verified-claim-routing-v0.1-2026-09-22.md)
- [Claim Routing Natural-Language checkpoint](./research/checkpoint-claim-routing-natural-language-v0.1-2026-09-22.md)
- [First Claim Promotion checkpoint](./research/checkpoint-claim-promotion-v0.2-2026-09-22.md)
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

2026-09-25時点では、current `data/questions.json` の verified 質問から10問を固定し、Kaigo Rulesによって正しい原典への到達負担を減らせるかを測る小規模検証を準備済み。結果はまだ `NOT_RUN` であり、効果の主張は行わない。

- [必要な情報を探すのに時間がかかる](./research/issues/information-search/README.md)
- [Field Validation v0.1 — 固定10問](./research/issues/information-search/field-validation-v0.1.json)
- [Field Validation v0.1 — 実施プロトコル](./research/issues/information-search/field-validation-protocol-v0.1.md)
- [Field Validation v0.1 — blind scoring](./research/issues/information-search/field-validation-scoring-v0.1.md)
- [Field Validation v0.1 — 採点テンプレート](./research/issues/information-search/field-validation-adjudication-template-v0.1.csv)
- [Field Validation v0.1 — 実施準備状況 / deployment gate](./research/issues/information-search/field-validation-readiness-2026-09-25.md)
- [Field Validation v0.1 — 記録テンプレート](./research/issues/information-search/field-validation-run-template-v0.1.csv)
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

- [Claim Registry v0.18](./research/claims/claims-v0.18.json)
- [Claim Registry v0.16](./research/claims/claims-v0.16.json)
- [Claim Registry v0.15](./research/claims/claims-v0.15.json)
- [Safety answer templates v0.2](./research/issues/information-search/benchmark/safety-answer-templates-v0.2.json)
- [Safety prose human sign-off v0.1](./research/issues/information-search/benchmark/safety-prose-human-signoff-v0.1.md)
- [Controlled RAG comparison protocol v0.1](./research/issues/information-search/benchmark/controlled-rag-comparison-protocol-v0.1.md)
- [Controlled RAG eval contract v0.1](./research/issues/information-search/benchmark/controlled-rag-eval-contract-v0.1.json)
- [Claim Registry v0.14](./research/claims/claims-v0.14.json)
- [Claim Registry v0.13](./research/claims/claims-v0.13.json)
- [Claim Composition Registry v0.5](./research/claims/claim-compositions-v0.5.json)
- [Claim Registry v0.11](./research/claims/claims-v0.11.json)
- [Claim Registry v0.10](./research/claims/claims-v0.10.json)
- [Claim Registry v0.8](./research/claims/claims-v0.8.json)
- [Claim Registry v0.6](./research/claims/claims-v0.6.json)
- [Claim Registry v0.5](./research/claims/claims-v0.5.json)
- [Claim Composition Registry v0.2](./research/claims/claim-compositions-v0.2.json)
- [Claim Registry v0.3](./research/claims/claims-v0.3.json)
- [Claim Registry v0.2](./research/claims/claims-v0.2.json)
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
