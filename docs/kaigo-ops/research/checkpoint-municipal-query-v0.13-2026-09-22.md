# Kaigo Ops Research Checkpoint — Municipal External Query Gate

更新日: 2026-09-22  
状態: **municipal query 15 / 15, full checks 181 / 181**

## 目的

厚生労働省Q&A候補プール以外の実務的な質問表現で、Claim-aware routingをstress testする。

今回は横浜市の公開Q&Aと東京都の指定申請関連公開情報から質問文を抽出した。

自治体回答は国基準のground truthには使っていない。

## 初回結果

自治体query:

**11 / 15**

失敗4件:

1. 重要事項説明書の変更時同意を、既存の「文書内容」ClaimがANSWERしてしまった
2. 看護師が一時的に抜ける質問を、単一の基本配置Claimへ寄せた
3. 東京都の「内法」質問をLOCALにできなかった
4. 東京都の「新規指定前研修」質問をLOCALにできなかった

## 修正

### claims-v0.9

- 重要事項文書のcontent Claimから「変更」「改定」等を除外
- `review.important.change-consent` を追加
- 変更時の再説明・同意は、提供開始時Claimから自動拡張しない

### claim-compositions-v0.3

看護職員のpresence/linkage compositionに、

- 抜ける
- 不在
- 人員欠如
- 提供時間

などの自然表現を追加。

### classifier v0.15

自治体名・指定権者contextがあり、

- 新規指定
- 事前相談
- 移転
- 専用区画
- 用途変更
- 内法
- 新規指定前研修

等を含む質問をLOCALへ送る。

## Result

- municipal query: **15 / 15**
- MHLW external query: **33 / 33**
- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- claim promotion: 2 / 2
- natural-language routing: 12 / 12
- verified Claim routing: 28 / 28
- multi-claim routing: 5 / 5
- important-matters routing: 3 / 3

合計 **181 / 181**。

## 現在の正本

- Claim Registry: `claims-v0.9.json`
- Composition Registry: `claim-compositions-v0.3.json`
- Classifier: `research-coverage-classifier-v0.15.mjs`
- Benchmark: `benchmark-v0.13.json`

## 次

次の有力なreview候補は、

- 重要事項変更時の再説明・同意
- 機能訓練指導員の提供日・単位ごとの配置
- サービス提供中の散髪・訪問診療・外出レクリエーション

など。

ただし、自治体Q&A回答をそのまま全国基準へ昇格させない。必要なものだけ厚労省の現行一次資料で独立reviewする。

RAGは引き続き保留する。
