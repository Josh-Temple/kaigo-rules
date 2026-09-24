# Kaigo Ops Research Checkpoint — National RAG Holdout Collection v0.1

更新日: 2026-09-23  
状態: **20 national queries frozen / labels not assigned**

## Source

厚生労働省
「令和6年度介護報酬改定に関するQ&A（Vol.1）」
令和6年3月15日。

公式の令和6年度介護報酬改定ページに現在も掲載されている。

## Collection

通所介護関連の問53〜58、60〜73から20件を固定した。

問59は既存external benchmarkに
看護職員の外部連携queryとして既に含まれるため除外した。

## 主な論点

- 個別機能訓練加算
- 入浴介助加算
- 所要時間区分
- 送迎減算
- 3％加算
- 事業所規模区分の特例

## 現段階

- raw queries: 20
- labels: 未付与
- expected Claim: 未付与
- classifier実行: 未実施
- Q&A回答本文をClaim promotionには使用していない

## 次

1. current Claim Registry / review stateとは独立にanswerabilityをラベル付け
2. 後年改正・廃止の有無を確認
3. Batch 1（自治体30件）とのclass distributionを統合
4. ANSWER coverageが極端に少なければ、RAG実装よりClaim coverage拡張を優先する
