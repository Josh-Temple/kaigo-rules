# Kaigo Ops 情報探索 Field Validation v0.1 — 実施準備状況

更新日時: 2026-09-26 JST

## 状態

**OPTIONAL_EXTERNAL_VALIDATION / NOT_RUN**

人間による Field Validation v0.1 は protocol を維持したまま保留可能とする。
参加者の確保は、Kaigo Rules / Kaigo Ops の開発・情報基盤整備・サービス範囲拡張の必須条件ではない。

この文書に記録された過去のSHAを current state として扱わない。
実施する場合は、その時点で GitHub main、CI、Vercel production を fresh readする。

## 人間評価を残す理由

人間による次の主張を検証できるのは、引き続きこの系統である。

- 正しい原典へ到達する時間が短くなるか
- 操作負担が減るか
- 回答の条件保持や根拠正確性を落とさず使えるか

Machine Retrieval Benchmark の結果だけでは、これらの主張は行わない。

## 現在の代替進行路

参加者を必要としない `Machine Retrieval Benchmark v0.1` を主な次工程とする。

評価対象:

1. 固定10問 × 3言い換え = 30 query の production search到達率
2. 対象questionの検索順位
3. AI向け context API のquestion / answer / canonical source保持
4. question別、single/multi-source別の弱点抽出

人間評価はこの機械評価と独立しており、後から追加できる。

## 人間評価を再開する条件

実施する場合のみ、次を確認する。

1. current main の `Validate build` が成功
2. production `/api/version` が `deploy-state/kaigo-rules` のSHAと一致
3. production SHAから実測開始時mainまでに、daily deploy対象パスの未反映差分がない
4. production field-validation gate がproduction SHA指定でPASS
5. 固定10問のvalidatorがPASS
6. 少なくとも2人の実参加者を確保
7. 20試行中は同じproduction SHAを原則維持

production SHAとcurrent main SHAの完全一致は必須にしない。
差分が `docs/` 等のproduction非対象ファイルだけなら、production挙動は同一として実測開始を妨げない。
一方、`app` / `components` / `data` / `scripts` / `public` およびbuild設定等に未反映差分がある場合は開始しない。

実測開始時のmain SHAは `study_main_sha`、実際のproduction SHAは `production_sha` として別々に固定・記録する。

実測データを推定・代替生成しない。

## 公開上の扱い

人間評価が `NOT_RUN` の間は、

- 「探索時間を短縮した」
- 「利用者の作業効率が上がった」
- 「使いやすさを実証した」

とは表現しない。

一方、Machine Retrievalで実測した範囲については、
「固定queryで対象ページへ到達できた割合」や
「context APIがcanonical sourceを保持した割合」のように、
機械評価の射程を明記して公開できる。
