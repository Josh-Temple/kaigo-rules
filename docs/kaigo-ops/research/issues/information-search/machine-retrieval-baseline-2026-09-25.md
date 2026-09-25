# Machine Retrieval Benchmark v0.1 — 初回production baseline

実測日時: 2026-09-25 21:40 JST  
対象production SHA: `eb7ef817e05372b4a38baee353271d7c42f5ed34`  
GitHub Actions run: `36136235293`  
artifact: `10864586181`  
artifact digest: `sha256:6f06c7053f14b6eb8f2095c3fbce7b3e34d1c8e01cded8b1f22571e3be4fc66e`

## 結果

- search hit rate: **10 / 30 = 33.3%**
- top-3 hit rate: **10 / 30 = 33.3%**
- context integrity rate: **10 / 10 = 100%**
- full pass rate: **10 / 30 = 33.3%**

10問すべてで、短いキーワード型のA queryは対象ページへ到達した。
一方、文章型・日常語を含むB/C queryは20件すべてmissとなった。

context APIは10問すべてでHTTP 200、期待slug、short_answer、verified status、canonical source_idsを保持した。

## 診断

情報基盤そのものより、検索入力の解釈が現在のボトルネックになっている。

初回productionの実務質問検索は、入力を空白で区切り、各termをAND条件で照合していた。
日本語の自然文は空白を含まないことが多いため、たとえば
「管理者は介護職員も兼ねられる？」が1つの長いtermとして扱われ、既存aliasへ一致しなかった。

この結果は、人間の使いやすさや探索時間を測ったものではない。
固定queryに対するproduction検索と構造化contextの機械的再現性だけを示す。

## 次の改善

固定30queryは変更しない。

確認済み実務質問についてのみ、次を導入する。

1. 代表的な言い換えをcanonical化する。
2. title / aliases / short_answerとの文字bigram類似度を計算する。
3. aliasesを最も強く、titleを次に強く、short_answerを補助的に評価する。
4. 閾値未満は表示しない。
5. 同じ30queryで対象質問がtop3に残ることをCI回帰テストにする。

基準省令・報酬告示・Q&Aの検索条件は今回変更しない。
