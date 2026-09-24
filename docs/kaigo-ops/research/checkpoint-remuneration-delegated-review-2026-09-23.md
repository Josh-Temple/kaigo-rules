# Kaigo Ops Research Checkpoint — Remuneration Delegated Notices

更新日: 2026-09-23  
判定: **delegated review COMPLETE / overall remuneration review IN_PROGRESS**

## 1. 告示第27号

厚生労働大臣が定める利用者等の数の基準及び看護職員等の員数の基準並びに通所介護費等の算定方法
（平成12年厚生省告示第27号）

current official HTML:
https://www.mhlw.go.jp/web/t_doc?dataId=82aa0261&dataType=0&pageNo=1

reviewed:
- `calc27.dayservice.1`
- `calc27.dayservice.1.capacity`
- `calc27.dayservice.1.staffing`

確認:
- 運営規程の利用定員を超える場合: 所定単位数 × 70%
- 看護職員または介護職員の必要員数を置いていない場合: 所定単位数 × 70%

3 / 3 node reviewed。

## 2. 告示第95号

厚生労働大臣が定める基準
（平成27年厚生労働省告示第95号）

current official HTML:
https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0&pageNo=1

reviewed nodes:
- 十四の三 高齢者虐待防止措置未実施減算
- 十四の四 業務継続計画未策定減算
- 十四の五 生活相談員配置等加算
- 十四の六 入浴介助加算
- 十五 中重度者ケア体制加算
- 十六 個別機能訓練加算
- 十七 認知症加算
- 十八の二 栄養アセスメント加算
- 十九 栄養改善加算
- 十九の二 口腔・栄養スクリーニング加算
- 二十 口腔機能向上加算
- 二十三 サービス提供体制強化加算
- 二十四 介護職員等処遇改善加算
- 四 訪問介護費における介護職員等処遇改善加算（通所介護第24号から準用）

14 / 14 node reviewed。

## 3. Review ledger

`data/remuneration-review.json`:
- base_notice_review: COMPLETE
- delegated_review: COMPLETE
- fee_guidance_review: PENDING
- overall review_status: IN_PROGRESS

source SHA:
- notice27: `222c91e52c7978377047104de2c374c26f5dd2aabfd6376cfe7a8caf1a8c1ff3`
- notice95: `7f1006dd10ce1260b75dec5fe226972af1769ba1502803ba5d58b71d54ae5618`

## 4. Drift guard

`scripts/research-remuneration-delegated-review-validate-v0.1.mjs`

CIで:
- source URL / SHA
- 17 node全件
- notice27 3件
- notice95 14件
- 各node text SHA
をcurrent imported dataと照合する。

## 5. Next gate

残る主作業は老企第36号。

報酬告示と委任基準が正しくても、
加算・減算の実務的な算定方法、例外、経過措置等は留意事項通知を確認する必要がある。

そのため、現段階でclassifierの報酬queryをANSWERへ開放しない。
