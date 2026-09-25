# Kaigo Ops 情報探索 Field Validation v0.1 — 実施手順

作成日: 2026-09-25  
状態: Fixed before first measured attempt / result NOT_RUN

## 位置づけ

この文書は `field-validation-protocol-v0.1.md` を実施するときの操作手順を固定する。

質問、A/B割付、主指標、採点項目、成功条件、Hold条件は変更しない。
ここで定めるのは、未定義だった開始・終了、時間切れ、クリック数等の記録方法である。

最初の実測開始後は、この手順を結果に合わせて変更しない。

## 実測を開始する条件

参加者へ最初の質問を見せる前に、次をすべて満たす。

1. current GitHub main の `Validate build` が成功している。
2. production の `/api/version` の40桁SHAが、`deploy-state/kaigo-rules` のSHAと一致する。
3. production SHAから実測開始時のmain SHAまでに、production挙動へ影響する未反映差分がない。
4. `scripts/verify_field_validation_production.py --expected-sha <production_sha>` が固定10問を含めてPASSする。
5. `scripts/validate_kaigo_ops_field_validation.py` がPASSする。
6. 固定質問・canonical answer・sourceに未解決の変更がない。

3の確認では、daily production deployと同じproduction対象パスを使う。

- `app`
- `components`
- `data`
- `scripts`
- `public`
- `package.json`
- `package-lock.json`
- `tsconfig.json`
- `next-env.d.ts`
- `vercel.json`

production SHAとcurrent main SHAが異なっていても、差分が `docs/` 等のproduction非対象ファイルだけであれば開始条件を満たせる。
逆に、上記production対象パスに差分がある場合は、SHAが近くても実測を開始しない。

実測開始時に次の2つを固定する。

- `study_main_sha=<40桁SHA>`
- `production_sha=<40桁SHA>`

各試行の `observer_notes` には少なくとも `production_sha=<40桁SHA>` を残す。
pilot全体の管理記録には `study_main_sha` も残す。

同一の20試行ではproduction SHAを原則として固定する。
途中でproduction SHAが変わった場合は、そのまま継続せずHoldして影響を確認する。
mainがdocs-onlyで進んだだけの場合はpilotを自動Holdしないが、production対象パスに変更が入った場合は影響確認が終わるまで再開しない。

## 実施環境

- 同じ種類の端末・ブラウザを可能な範囲で使用する。
- 参加者ごとにprivate/incognito sessionを開始する。
- 各試行は新しいタブから開始し、前の質問のページを再利用しない。
- ブックマーク、保存済み回答、生成AI、過去の試行メモは使わない。
- ブラウザの履歴や前試行の検索結果から回答へ移動しない。

### Condition A の開始画面

一般検索を行える検索エンジンの開始画面を事前に読み込んでおく。

### Condition B の開始画面

Kaigo Rules production の `/search` を事前に読み込んでおく。

開始画面の初回ネットワーク読込時間は計測対象に含めない。

## 1試行の開始

1. 開始画面を表示する。
2. 回答者に質問文を見せる。
3. 回答者が操作可能になった時点でタイマーを開始する。
4. 探索中、観察者は正誤を教えない。

## 1試行の上限

1試行は **600秒（10分）** を上限とする。

600秒に達したら、それ以上探索せず、その時点の最善の回答を提出する。
「分からない」も回答として保存し、空欄のまま終了しない。

この時間上限は最初の実測前に固定し、Condition A/Bで同じとする。

## time_to_first_authoritative_source_sec

探索中に回答者が、

- 回答根拠として使う公的資料を特定し、
- 条・項、ページ、資料内見出し等の該当箇所を示した

時点でlapを記録する。

観察者はその場で正誤判定しない。
後のblind adjudicationで `authoritative_source_reached` を判定する。

回答者が600秒までに根拠資料を特定しなかった場合、この時間は空欄とし、
`observer_notes` に `TIMEOUT_NO_SOURCE` を記録する。

集計時、原典到達時間は `authoritative_source_reached=TRUE` と判定された試行だけで算出し、
原典到達率を必ず併記する。失敗試行を成功時間として600秒に置換しない。

## time_to_answer_submission_sec

回答者が、

- `answer_text`
- `source_url`（根拠なしの場合は空欄）
- `source_locator`（根拠なしの場合は空欄）

を確定して提出した時点を記録する。

600秒に達した場合は600秒で打ち切り、その時点の最善回答を提出する。

## clicks

端末差を減らすため、次を1回として数える。

- リンク・ボタン・検索結果のclick/tap
- Back/Forward等のナビゲーション操作
- Enterキー等で検索を送信した場合も1回のclick相当として数える

文字入力、スクロール、ページ内の単なるテキスト選択は数えない。

## query_reformulations

最初に入力した検索語は0とする。

その後、検索意図を保ったまま検索語を追加・削除・言い換えて再検索するたびに1増やす。
同じ検索語の再送信や誤字修正だけは増やさない。

Condition BでKaigo Rules内の検索語を変更した場合も同じ扱いとする。

## source_locator

URLだけでなく、第三者が同じ根拠を再確認できる粒度で残す。

例:

- 第93条第1項第2号
- 「業務継続計画の策定等」研修・訓練
- PDF p.12
- Q&Aの項目名・問番号

「厚労省PDF」「基準省令」のような資料名だけでは完了としない。

## confidence_1_5

回答提出後に入力する。

- 1: ほぼ確信なし
- 2: 確信は低い
- 3: どちらともいえない
- 4: かなり確信
- 5: 強く確信

正誤判定とは独立した自己評価であり、観察者は誘導しない。

## 技術的な中断

参加者の探索とは無関係なネットワーク障害、production 5xx、計測器停止等が起きた場合、
その場で続行・やり直しを決めない。

`observer_notes` に事象を記録してpilotをHoldし、同じ質問への再露出による学習効果を含めて対応を決める。

## 20試行終了後

1. raw run dataを固定する。
2. `scripts/prepare_kaigo_ops_field_adjudication.py` で、raw run dataからblind adjudication CSVを生成する。手作業で列を削除・転記しない。
3. 生成CSVに `condition`・時間・clicks・query_reformulations・confidence・observer_notes が含まれていないことを確認する。
4. `field-validation-scoring-v0.1.md` と
   `field-validation-scoring-calibration-v0.1.md` に従って採点する。
5. 全採点終了後にのみraw dataと結合する。
6. `scripts/analyze_kaigo_ops_field_validation.py` で集計する。
7. 小標本のため、スクリプトは記述統計を出すだけで、成功判定や有意差判定を自動で行わない。

### blind adjudication CSV の生成

実測後にGoogle Sheetの「記録」をCSVとして保存し、次を実行する。

```bash
python scripts/prepare_kaigo_ops_field_adjudication.py \
  --run /path/to/field-validation-run.csv \
  --output /path/to/field-validation-adjudication-blind.csv
```

このスクリプトは、固定20試行の attempt / question 対応とraw schemaを検証し、採点に必要な6列だけを転記する。採点フラグ・adjudicator欄は空欄のまま出力する。
