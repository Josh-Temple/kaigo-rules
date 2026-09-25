# Kaigo Ops Machine Retrieval Benchmark v0.1

作成日: 2026-09-25  
状態: Protocol fixed / result NOT_RUN

## 目的

人間の参加者を必要とせず、Kaigo Rules の情報基盤が次を機械的に再現できるか確認する。

1. 自然な言い換えの検索語から、対応する確認済み実務質問へ到達できる。
2. AI向け context API が、その質問の回答・注意点・根拠 source を欠落させず返す。

この評価は、人間による Field Validation の代替ではない。
人間の探索時間、使いやすさ、生産性についての効果は測定しない。

## 固定データ

正本:

- `machine-retrieval-benchmark-v0.1.json`
- `field-validation-v0.1.json`
- `data/questions.json`
- `data/context-packages/dayservice-questions.generated.json`

Field Validation の固定10問をそのまま使い、各質問に3種類、計30件の検索語を固定する。

3種類には、現在のaliasに近い表現だけでなく、文章型・日常語を含める。
検索に失敗したケースも削除・差替えせず、そのまま改善対象として残す。

## 評価対象

### A. production search

各queryについて:

`/search?q=<query>`

を開き、対象の `/questions/<slug>` が検索結果に含まれるかを確認する。

記録:

- `search_hit`
- `search_rank`
- `top3_hit`

現在の検索結果に明示的なスコアリングはないため、rankはHTML上の確認済み実務質問リンクの出現順を使う。

### B. context API

各固定質問について:

`/api/context/services/dayservice/questions/<slug>`

を取得し、次を確認する。

- HTTP 200
- `package.question.slug` が期待slugと一致
- `package.answer.short_answer` が空でない
- `package.assurance.question_content_status == "verified"`
- `package.evidence.sources` が canonical `source_refs` の source_id をすべて含む

## 指標

- `search_hit_rate`: 30 query中、対象questionが検索結果に出た割合
- `top3_hit_rate`: 対象questionが上位3件に出た割合
- `context_integrity_rate`: context APIが期待内容を保持した割合
- `full_pass_rate`: search hit と context integrity が両方成立した割合

質問別にも3queryの成功数を出す。

v0.1では統計的有意差や人間効果への換算は行わない。

## 実行

productionがcurrent mainへ反映された後:

```bash
python scripts/run_machine_retrieval_benchmark.py \
  --base-url https://kaigo-rules.vercel.app \
  --output /tmp/kaigo-machine-retrieval-v0.1.json
```

fixtureの整合性確認:

```bash
python scripts/validate_machine_retrieval_benchmark.py
```

## 結果の扱い

- 最初のproduction実行結果をbaselineとして保存する。
- 失敗queryを結果を見て削除しない。
- 検索改善後は同じ30queryで再実行し、versionを変えずに比較する。
- canonical question/sourceが変わる場合は、v0.1を勝手に書き換えずHoldして変更理由を記録する。
- 人間実験が後日可能になった場合、Machine Retrievalの結果と別系統で扱う。

## 公開上の制約

Machine Retrievalだけで言えるのは、例えば次までとする。

- 「固定30queryに対して対象ページへ機械的に到達できた割合」
- 「context APIが固定questionのcanonical sourceを保持した割合」

次は言わない。

- 「利用者の探索時間を短縮した」
- 「人間が使いやすい」
- 「業務効率が向上した」
