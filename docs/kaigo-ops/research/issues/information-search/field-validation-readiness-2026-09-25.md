# Kaigo Ops 情報探索 Field Validation v0.1 — 実施準備状況

更新日時: 2026-09-25 12:15 JST

## 状態

**READY_TO_RUN_AFTER_DEPLOYMENT_GATE**

研究上の結果状態は引き続き `NOT_RUN` とする。

参加者による計測を開始する前に、Kaigo Rules の本番環境がこの pilot の基準となる current main を含むことを確認する。

## Canonical baseline

この準備確認時点の GitHub main:

`c02347ac2e49cd641e6c2beacfe2acc48780d09b`

この commit には少なくとも次が含まれる。

- PR #148: Kaigo Ops の最初の公開 Issue
- PR #149: FAQ の検証範囲と canonical evidence link の明確化
- PR #150: 10問の Field Validation protocol と fail-closed validator

質問セットの正本は:

- `data/questions.json`
- `field-validation-v0.1.json`

である。

## 技術的な実施準備

10問はすべて current `data/questions.json` の `verified` 質問を参照している。

Kaigo Rules の `app/questions/[slug]/page.tsx` は `data/questions.json` の全質問から静的パスを生成するため、固定10問は question route の生成対象になる。

verified 質問ページでは、質問に紐づく範囲で次を表示する。

- 基準省令
- 解釈通知
- curated Q&A
- その他の公的 source reference
- 原典へのリンク

`scripts/validate_kaigo_ops_field_validation.py` は、固定10問について canonical state との drift を fail-closed で検知する。

直近の PR #150 では:

- Validate build: SUCCESS
- Validate ops site: SUCCESS

を確認済み。

## 計測キット

参加者2人 × 10問の記録用 Google Sheet を準備済み。

シートには次を用意している。

- 実施手順
- 固定10問と P1 / P2 の counterbalance
- 20試行分の記録欄
- TRUE / FALSE および confidence の入力制約
- Condition A / B の自動集計

Google Sheet は個人 Drive の運用資料であり、公開リポジトリには URL を保存しない。

## Deployment gate

2026-09-25 12:15 JST の fresh Vercel read では、Kaigo Rules の最新確認可能な production deployment は:

- Git branch: `main`
- Git SHA: `1d9246789b30bb1a16f7aced4ca30f08b042a1cf`
- state: `READY`

だった。

これは pilot baseline `c02347ac2e49cd641e6c2beacfe2acc48780d09b` より前の状態である。

そのため、**現在の production alias を使った人間計測は開始しない。**

開始条件:

1. Vercel production deployment が `main` から作成されている。
2. その production commit が少なくとも baseline `c02347ac2e49cd641e6c2beacfe2acc48780d09b` を含む。
3. production 上で `/search` と固定10問の `/questions/<slug>` が利用可能である。
4. 原典リンクが参加者のブラウザから開ける。
5. 上記確認後も `field-validation-v0.1.json` が validator を通る。

現在の運用方針では Vercel の production deployment は原則1日1回に制限しているため、この readiness check のために追加の強制 deploy は行わない。

## 計測時に固定すること

計測開始後は、結果を見て次を変更しない。

- 10問の構成
- A/B 割付
- 主指標
- success / Hold 条件
- canonical answer

途中で canonical question や source に変更が生じた場合、その質問を都合よく差し替えず、v0.1 を Hold して変更理由を記録する。

## 次のアクション

deployment gate を通過した後に:

1. production routes を再確認する
2. P1 / P2 の計測を開始する
3. Google Sheet に生データを記録する
4. 20試行終了後に集計する
5. 結果を成功例だけでなく失敗例も含めてレビューする
6. その後にのみ Kaigo Ops の公開ページへ効果結果を反映するか判断する

現時点では「Kaigo Rules で探索時間が短縮する」という効果主張は行わない。
