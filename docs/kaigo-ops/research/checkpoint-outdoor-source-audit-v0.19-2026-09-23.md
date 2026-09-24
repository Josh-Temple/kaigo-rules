# Kaigo Ops Research Checkpoint — Outdoor Service Source Audit v0.19

更新日: 2026-09-23  
状態: **source limitation retained / provenance strengthened / decision boundary unchanged**

## 目的

`claim.service.outdoor.conditions` について、現行の厚生労働省一次資料から屋外提供条件の統合本文を直接確認できるかを再監査する。

## 確認した一次資料

### 1. 老企第25号 厚生労働省HTML

- https://www.mhlw.go.jp/web/t_doc?dataId=00ta4369&dataType=1
- 通所介護の3(2)「指定通所介護の基本取扱方針及び具体的取扱方針」を直接確認
- 現在のHTML表示では①〜③の後に(3)「通所介護計画の作成」へ進み、屋外提供条件の④は掲載されていない

したがって、このHTMLだけを使って「事業所内提供が原則」「通所介護計画への事前位置付け」「効果的な機能訓練等」という条項全文を現行統合本文として直接再構成することはできない。

### 2. 介護保険サービスと保険外サービスを組み合わせて提供する場合の取扱いについて

- https://www.mhlw.go.jp/web/t_doc?dataId=00tc3681&dataType=1
- 厚生労働省の2018年通知
- 利用者個人の希望による保険外の外出同行支援と区別して、「機能訓練の一環として通所介護計画に位置づけられた外出」を明示

この通知により、通所介護計画に基づく外出が制度上の前提として扱われていることは補強できる。

ただし、この通知は老企第25号の屋外提供条項を全文再掲しておらず、「効果的な機能訓練等」の条件まで含む統合本文の代替にはならない。

## 判定

`claim.service.outdoor.conditions` は **VERIFIED_WITH_SOURCE_LIMITATION を維持**する。

変更:
- provenanceへ `mhlw-noninsurance-combination-2018` を追加
- review noteを今回の直接監査内容へ更新

変更しない:
- statement
- answerability
- verification_status
- routing
- boundaries
- superseded_by

## Decision invariance

`claims-v0.14 → v0.15` について以下を比較した。

- issue_id
- answerability
- verification_status
- routing
- superseded_by

decision-affecting diff: **0件**

したがって、直前baseline **191/191 PASS** を変更する判定ロジック差分はない。

## main source layerとの整合

研究ブランチの `data/sources.json` へ、mainで追加された老企第36号関連7ソースを同期した。

ID競合:
- differing source IDs: **0**
- main-only sources: **7件追加**
- research-only sources: 維持

報酬・一単位単価の独立機械照合はmainで強化されているが、人手review台帳は未完了であるため、研究router上の `REVIEW_REQUIRED` を自動昇格させない。

## 現在の正本

- Claim Registry: `claims-v0.15.json`
- Composition Registry: `claim-compositions-v0.5.json`
- Classifier: `research-coverage-classifier-v0.22.mjs`
- Benchmark: `benchmark-v0.19.json`

## 次

1. safety proseのhuman sign-off
2. 屋外提供条項について、 exact two-condition clause を含む現行統合の厚労省資料が見つかった場合だけ再昇格判定
3. 上記gateを閉じた後にcontrolled RAG comparison

RAGはまだ実装しない。
