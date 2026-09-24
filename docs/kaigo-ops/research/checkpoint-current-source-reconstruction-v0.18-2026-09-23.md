# Kaigo Ops Research Checkpoint — Current-Source Reconstruction

更新日: 2026-09-23  
状態: **source limitation 7 → 1 / decision boundary unchanged**

## 目的

`VERIFIED_WITH_SOURCE_LIMITATION` を、古い改正文の再確認ではなく、現在の厚生労働省一次資料・公式Q&A・現行掲載資料から再検証する。

## 結果

対象7 Claimのうち6件を `VERIFIED_CURRENT` へ更新した。

### 1. 看護職員の外部連携

`claim.staff.nurse.external-linkage`

令和6年度Q&A問59が、

- 病院・診療所・訪問看護ステーションとの契約
- 営業日ごとの健康状態確認
- 提供時間帯の連絡体制

を現在の運用前提として扱っていることを確認。

### 2. BCP研修・訓練

`claim.training.bcp.annual-frequency`

厚生労働省の現行BCP支援ページ掲載資料で、

- 通所系・訪問系: 研修 年1回
- 通所系・訪問系: 訓練 年1回

を再確認。

### 3. 感染症研修・訓練

`claim.training.infection.annual-frequency`

令和6年度の厚労省解釈通知資料・通所介護部分で、

- 研修 年1回以上
- 新規採用時の研修が望ましい
- 訓練 年1回以上

を直接確認。

### 4. 虐待防止研修

`claim.training.abuse.annual-newhire`

現在の厚労省資料で、

- 通所介護: 年1回以上
- 在宅系: 年1回以上
- 新規採用時にも必ず実施することが重要

を再確認。

### 5. 生活相談員のサービス担当者会議時間

`candidate.staff.life-counselor.service-meeting-time`

平成24年度Q&Aの回答が、令和8年度まで更新されている現在の厚労省公式Q&A体系に保持されていることを確認。

### 6. 食堂・機能訓練室の複数室合算

`candidate.facility.dining-training.multi-room`

- 現行基準省令
- 現行厚労省解釈通知HTMLの原則・例外
- 公式Q&Aの具体例

を突合して現行性を閉じた。

## 据え置き

`claim.service.outdoor.conditions`

のみ `VERIFIED_WITH_SOURCE_LIMITATION` を維持。

屋外提供条件そのものは根拠があるが、今回確認した令和6年度新旧対照表から当該条項の現行統合本文を直接再構成できなかった。

古い全文断片 + 後年の部分改正だけで `CURRENT` に上げない。

## 判定境界への影響

`claims-v0.13 → v0.14` を機械比較した。

変更なし:

- issue_id
- answerability
- routing
- superseded_by

差分は **0件**。

変更した6 statusは、いずれもclassifierが既にverified系として扱っていた

`VERIFIED_WITH_SOURCE_LIMITATION → VERIFIED_CURRENT`

のみ。

したがって、直前の191/191判定結果を変えるdecision-affecting changeはない。

## 現在の正本

- Claim Registry: `claims-v0.14.json`
- Composition Registry: `claim-compositions-v0.5.json`
- Classifier: `research-coverage-classifier-v0.21.mjs`
- Benchmark: `benchmark-v0.18.json`

## 次

次の優先順位は、

1. safety proseのhuman sign-off
2. 屋外サービス1件のcurrent integrated source reconstruction
3. その後にcontrolled RAG comparison

RAGはまだ実装しない。
