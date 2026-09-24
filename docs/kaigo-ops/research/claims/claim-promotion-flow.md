# Claim Promotion Flow

更新日: 2026-09-22  
状態: v0.1 / first promotion trial completed 2026-09-22

## 目的

Q&Aや未レビュー資料を「見つけた」だけで回答可能にしない。

```text
candidate source
  ↓
subtopic identification
  ↓
primary/current source check
  ↓
claim statement fixed
  ↓
boundary / exclusions fixed
  ↓
review status promoted
  ↓
benchmark added
  ↓
answerable
```

## Status

### CANDIDATE_UNREVIEWED

質問・論点の存在だけを把握。

- Q&A question preview
- machine extraction
- search result

など。

**回答根拠には使わない。**

### REVIEW_REQUIRED

公式資料は存在するが、
現在の統合状態・要件・関係をまだ確認していない。

例:
- 報酬
- 一単位単価
- current guidance reconstruction

### VERIFIED_WITH_SOURCE_LIMITATION

中核claimは確認できているが、
sourceが部分資料や改正後文で、
全体のcurrent reconstructionが未完了。

回答時にはsource limitationを保持する。

### VERIFIED_CURRENT / VERIFIED_SOURCE_TEXT

現在の正本として利用可能。

## Promotion rule

CANDIDATE_UNREVIEWED → VERIFIEDへ直接上げない。

最低限:

1. current official sourceを確認
2. claim本文を1つの命題へ固定
3. 適用scopeを固定
4. exception / boundaryを確認
5. source locatorを記録
6. reviewed_atを記録
7. benchmark questionを追加
8. previous false-ANSWER caseが解消するか確認

## Q&Aの扱い

Q&Aは有用だが、
大Issueのverified statusを自動で広げない。

例:

```text
生活相談員の基本配置 VERIFIED
        ↓
サービス担当者会議時間 ?
地域連携活動時間 ?
```

この2つは別claimとしてreviewする。

## Candidate selection priority

review queueは次の順で優先する。

1. 実際のqueryでREVIEW_REQUIREDが多い
2. public Q&Aに繰り返し登場
3. 間違えると実務影響が大きい
4. sourceが明確でreview costが低い
5. 既存Issueのcoverageを大きく広げる

## Re-research

verified claimも永久ではない。

- source hash change
- amendment
- superseding Q&A
- source removal
- conflict discovery

でre-review対象へ戻す。

## Public UI

利用者へ内部status名だけを見せない。

例:

- VERIFIED_CURRENT
  → 「確認済み」
- VERIFIED_WITH_SOURCE_LIMITATION
  → 「確認済み。ただし通知全体の統合確認を継続中」
- REVIEW_REQUIRED
  → 「公式資料は取得済みですが、内容確認中」
- CANDIDATE_UNREVIEWED
  → 原則として回答には表示しない

## RAGとの関係

RAGが参照できる資料と、
回答claimとして採用できる資料を分ける。

```text
retrievable corpus ≠ answerable corpus
```

未レビュー資料を探索候補として検索することはあっても、
verified claimへ昇格するまでは最終回答の根拠にしない。


## 実地検証

2026-09-22に以下2件で初回promotionを実施した。

- 生活相談員のサービス担当者会議時間
- 食堂・機能訓練室の複数室合算

いずれも、公式資料確認 → claim固定 → boundary固定 → source limitation付与 → benchmark追加 → ANSWER化、の順で処理した。

履歴保持のため、昇格前snapshotは上書きせず、Claim Registry v0.2へ進めた。
