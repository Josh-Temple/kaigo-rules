# Machine Retrieval Holdout v0.2 — main評価記録

評価日: 2026-09-25 JST

## 目的

PR #164で実務質問のaliasを拡張した後の検索について、v0.1およびdevelopment setとは異なる30queryを使い、同じ10個のcanonical questionへ到達できるかを確認した。

この評価は検索導線の機械評価であり、人間の探索時間短縮、使いやすさ、業務効率を示すものではない。

## 評価対象

- Repository: `Josh-Temple/kaigo-rules`
- 評価対象main SHA: `8218c4a0651ff64c58888b36aab2bb3c1b4a1df4`
- PR #164: practical-question alias expansion
- 判定: expected questionがtop 3に入ればPASS
- threshold: current implementationの既定値 `0.75`

PR #164では、holdout v0.1の実queryを回帰テストへ直接移さず、別のdevelopment set 12件を使用した。development setは変更前7/12、変更後12/12。既存固定Machine Retrieval Benchmark v0.1は30/30を維持した。

## v0.2結果

- case count: 30
- expected question top-3: **30 / 30**
- top-3 rate: **100%**
- miss: **0 / 30**

全10問について3種類の新規queryがexpected canonical questionへtop-3到達した。

一部はrank 2だった:
- H2-02-B: `life-counselor-staffing` rank 2
- H2-09-C: `annual-training` rank 2

したがって、100%は「常にrank 1」を意味しない。今回の評価基準は既存Machine Retrievalと同じtop-3到達である。

## 独立性の制約

v0.2はv0.1およびdevelopment setとqueryを分離したが、PR #164のalias改善後に、current search designを把握した同一セッションで作成・評価した。そのため完全blindではない。

この結果は、少なくとも別表現30件に対して改善が崩れていないことを示す回帰外の追加材料として扱う。より強い一般化性能の主張には、別担当・外部ログ・将来の実検索queryなどから事前固定した評価セットが必要。

## productionとの切り分け

この評価はcurrent main `8218c4a...` 上の計算であり、production実測ではない。productionは評価時点で旧SHA `eb7ef817...` のまま。

次回production deploy後には、exact SHA gateを通したうえで既存Machine Retrieval Benchmark v0.1の固定30queryをproductionに対して再実行し、旧production baseline 33.3%と同一条件で比較する。

## 今後

- v0.2を今後の検索調整に利用した場合、以後は回帰セットへ降格する。
- 新しい検索改善を行う場合、次の独立評価はv0.3など別versionを作る。
- productionで改善を確認するまで、「本番検索が100%」とは表現しない。
