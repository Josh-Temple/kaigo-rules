# Machine Retrieval Holdout v0.1 — main評価記録

評価日: 2026-09-25 JST

## 目的

PR #162で改善した実務質問検索について、既存の固定30queryとは異なる自然文・表記揺れ・余分語を含むqueryを使い、同じ10個のcanonical questionへ到達できるかを確認した。

この評価は検索導線の機械評価であり、人間の探索時間短縮、使いやすさ、業務効率を示すものではない。

## 評価対象

- Repository: `Josh-Temple/kaigo-rules`
- 評価対象main SHA: `7b1a51e080a2f3d8c685a123736562d24912aef5`
- Search implementation: `lib/question-search.ts`
- Question data: `data/questions.json`
- Holdout definition: `machine-retrieval-holdout-v0.1.json`
- 判定: expected questionがtop 3に入ればPASS
- threshold: current implementationの既定値 `0.75`

評価開始前のfresh readでは、open PR / Issueは0、Validate build #722はSUCCESSだった。

## productionとの切り分け

評価時点のproductionは `eb7ef817e05372b4a38baee353271d7c42f5ed34` のまま。Vercel production deployment `dpl_Ba1o4pGoAK1gsAcTPXduWN1mEnDH` はREADY。

したがって、この文書の86.7%は**current mainをローカル計算相当で評価した値**であり、productionの実測値ではない。既存production baseline 33.3%との直接比較で「productionが改善した」とはまだ言わない。

## 結果

- case count: 30
- expected question top-3: 26 / 30
- top-3 rate: **86.7%**
- top-3 miss: 4 / 30

失敗した4件:

| ID | query | expected | observed |
| --- | --- | --- | --- |
| HO-04-A | 食堂と訓練スペースを一緒にしてもいい？ | `dining-training-area` | MISS。threshold以上の候補なし |
| HO-08-C | 利用者から口頭同意だけでも計画は有効ですか | `care-plan-signature` | MISS。threshold以上の候補なし |
| HO-09-A | デイサービスで定期的にやる研修をまとめて知りたい | `annual-training` | expectedはMISS。`bcp-training`のみscore 0.760でhit |
| HO-10-C | 業務継続の訓練は毎年やる必要がありますか | `bcp-training` | expected rank 4。top 3は `annual-training`, `operation-rules-content`, `important-matters-content` |

## 追加観察

HO-08-B「通所介護計画に押印は必要ですか」は、expectedの `care-plan-signature` がrank 3でPASSした一方、より直接的な `care-plan-seal` がrank 1だった。これは検索失敗ではなく、Field Validation由来expected labelと、後から増えたより具体的なcanonical questionが競合している例として扱う。結果を見てexpectedを変更せず、そのまま記録した。

また、既存の2026-09-23作成holdout（`rag-holdout-labeled-v0.1.json`, `rag-holdout-national-labeled-v0.1.json`）も確認したが、前者はLOCAL/OUT_OF_SCOPE中心、後者は報酬claim routing中心で、今回の10問canonical question retrievalとは評価対象が異なるため代用しなかった。

## 解釈

26/30という結果は、PR #162の検索改善が、調整に使った固定30queryだけに完全に閉じてはいないことを示す材料にはなる。ただし、このholdoutはPR #162の調整には未使用でも、作成セッションがcurrent search implementationを確認済みであり、完全なblind評価ではない。

4件の失敗は、少なくとも次の弱点を示す。

- `訓練スペース`のような未登録言い換えを `機能訓練室` へ結び付けられない。
- `口頭同意`のようにcanonical title/aliasから語彙距離がある意図を拾えない。
- 「定期的にやる研修」のような広い集合質問で、個別のBCP質問に吸われる。
- `業務継続`を `業務継続計画` と同一視しておらず、一般語の「毎年」などが別質問を過大評価する場合がある。

## 次の扱い

このv0.1の4件を直接見ながら検索ロジックを修正した場合、v0.1は以後「未使用holdout」ではなく回帰セットになる。改善案は別dev queryで設計し、独立確認には新しいholdout v0.2を用意するのがよい。

次回production deployではexact SHAを確認したうえで、既存のMachine Retrieval Benchmark v0.1（固定30query）をproduction上で再実行する。main上のholdout 86.7%とproduction baseline 33.3%を同じ指標の改善量として混同しない。
