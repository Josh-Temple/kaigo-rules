# Kaigo Ops Research Checkpoint — Verified Claim Routing Expansion

更新日: 2026-09-22  
状態: **all current ANSWER claims routable / 140-check gate prepared**

## 今回の目的

Issue-level fallbackに依存している状態から、verified Claim自身がqueryを受け持つ構造へ移す。

対象は、`claims-v0.3` 時点でANSWER可能だがrouting metadataを持っていなかった28 claims。

## Before

28件の明確な自然言語queryを作成して `research-coverage-classifier-v0.6.mjs` で評価した。

- ANSWER判定: 27 / 28
- 正しいClaimへ解決: 0 / 28
- Issue-level fallback ANSWER: 26
- false abstention: 1
- wrong Claim resolution: 1

wrong resolutionは、基本面積の「合計面積」が複数室合算claimへ誤着地したもの。

この結果から、

> ANSWERできることと、正しいClaim provenanceを持つことは別

と確認できた。

## 変更

`claims-v0.4.json` で、現在ANSWER可能な30 claimsすべてに明示的routing metadataを持たせた。

同時に以下を修正した。

1. 管理者兼務claimは `勤務表` を除外
2. 通所介護計画の単純交付claimは `電子 / 電磁` を除外
3. 複数室合算claimは、`複数室 / 2室 / 別々の部屋` 等の複数室signalを必須化
4. 基本面積の `合計面積` だけでは複数室claimへ入らない

## Proposed result

事前再生では、

- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external Q&A: 15 / 15
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified claim routing probe: 28 / 28

合計 **140 / 140**。

verified claim probeは28 / 28すべてで期待claim IDまで一致。

## Issue fallback dependency

既存51 verified regressionについて、

### claims-v0.3

- Claim resolution: 0 / 51
- Issue fallback ANSWER: 51 / 51

### claims-v0.4案

- Claim resolution: 34 / 51
- Issue fallback ANSWER: 17 / 51

つまり、既存回帰の約3分の2はClaim provenanceへ移せる。

残る17件は、単純にrouting語彙を増やす前に、

- 複数Claimを同時に尋ねている
- queryがIssue粒度で、単一Claimに固定すべきでない
- 単純に安全な言い換え語が不足している

を分ける必要がある。

## 次

次は17件を個別に分類し、Issue fallbackを機械的にゼロにしない。

目標は、

`Issue fallback = 0`

ではなく、

`単一Claimへ固定できる質問はClaimへ、複数Claim質問は複数Claimへ、曖昧なら止める`

こと。

RAGは引き続き保留する。
