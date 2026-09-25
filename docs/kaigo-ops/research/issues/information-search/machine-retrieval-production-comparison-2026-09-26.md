# Machine Retrieval Benchmark v0.1 — production比較

記録日: 2026-09-26 JST

## 結論

同じ固定30query、同じcontext integrity条件で、productionのMachine Retrieval Benchmark v0.1は次のように改善した。

| 指標 | 初回production | 更新後production | 差 |
| --- | ---: | ---: | ---: |
| search hit rate | 10/30 = 33.3% | 30/30 = 100% | +66.7pt |
| top-3 hit rate | 10/30 = 33.3% | 30/30 = 100% | +66.7pt |
| context integrity rate | 10/10 = 100% | 10/10 = 100% | 0pt |
| full pass rate | 10/30 = 33.3% | 30/30 = 100% | +66.7pt |

更新後productionではsearch miss、context integrity failureともに0件だった。

この比較は、固定queryに対するproduction検索と構造化contextの機械的再現性を示す。人間の探索時間短縮、使いやすさ、業務効率を示すものではない。

## 初回production baseline

- production SHA: `eb7ef817e05372b4a38baee353271d7c42f5ed34`
- observed at: 2026-09-25 21:40:47 JST
- GitHub Actions run: `36136235293`
- artifact: `10864586181`
- artifact digest: `sha256:6f06c7053f14b6eb8f2095c3fbce7b3e34d1c8e01cded8b1f22571e3be4fc66e`

初回ではA queryの10件だけがhitし、文章型・日常語を含むB/C query 20件がmissだった。context integrityは10問すべてPASSしていた。

## 更新後production

scheduled deployment run `36165237901` がmain SHA `530c6ec226e1822472691984bdd6d4074820331d` をproductionへ反映した。

deployment jobでは以下がSUCCESSした。

1. kaigo-rules production deploy hook
2. exact SHAを使うfield-validation production gate
3. Machine Retrieval Benchmark v0.1
4. benchmark artifact upload
5. deploy-state更新

更新後artifact:

- production SHA: `530c6ec226e1822472691984bdd6d4074820331d`
- workflow run: `36165237901`
- artifact: `10877841329`
- artifact digest: `sha256:33f702a8d0d04ead2ae68faa4e12ec925314e223ef3ae3b754c53f4bfbacc959`
- artifact created: 2026-09-26 02:09:33 JST
- search hit: **30/30**
- top-3 hit: **30/30**
- context integrity: **10/10**
- full pass: **30/30**
- search misses: **none**
- context integrity failures: **none**

10個のField Validation質問すべてで3queryずつfull passした。

## 解釈

今回の改善は、初回productionで特定した「自然文queryを固定質問へroutingできない」というボトルネックについて、同一benchmark上では解消したことを示す。

一方、次は以下を分けて考える。

- 固定30queryでの再現性: productionで100%
- 別queryへの一般化: main上のholdout v0.1 / v0.2で追加検証済みだが完全blindではない
- 人間の実利用: まだ別評価が必要
- canonical answerや法的正確性: retrieval benchmarkの対象外。既存のsource verification / human review状態を優先する

したがって、「本番の固定Machine Retrieval Benchmarkは100%」とは言えるが、「自然文検索が一般に100%正しい」「人間の探索時間が改善した」とは言わない。

## scheduled deployの遅延観測

workflowのcron上の予定時刻は2026-09-25 21:17 JSTだったが、run `36165237901` のcreated_atは2026-09-26 02:08:33 JSTだった。

- nominal: 2026-09-25 21:17:00 JST
- observed workflow start: 2026-09-26 02:08:33 JST
- observed lag: 約4時間51分

ここでは実測された遅延のみ記録し、原因は断定しない。production deploy自体、exact-SHA gate、benchmark、artifact upload、deploy-state更新は正常終了している。

## 次の評価

検索品質について次に価値が高いのは、開発者が作ったparaphraseではなく、実際の利用者に近い外部・将来queryを事前固定して評価すること。

候補は、Field Validationで収集した実利用query、将来の検索ログ、または検索ロジックを見ていない別担当が作成したblind query set。既存v0.1 / v0.2を直接調整材料に使った場合、それらは以後回帰セットとして扱う。
