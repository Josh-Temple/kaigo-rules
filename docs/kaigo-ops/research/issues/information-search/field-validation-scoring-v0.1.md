# Kaigo Ops 情報探索 Field Validation v0.1 — 採点基準

作成日: 2026-09-25  
状態: Protocol fixed / result NOT_RUN

## 目的

Condition A / B の違いを見た採点バイアスを減らすため、探索時間の記録と回答品質の採点を分離する。

採点者は原則として、次を見ない状態で判定する。

- condition
- time_to_first_authoritative_source_sec
- time_to_answer_submission_sec
- clicks
- query_reformulations
- confidence_1_5

採点に渡すのは次だけとする。

- attempt_id
- question_id
- question_slug
- answer_text
- source_url
- source_locator

## Canonical reference

採点時の正本は current main の:

- `data/questions.json`
- 各 question の `short_answer`
- `cautions`
- `source_refs`

とする。

採点開始前に `scripts/validate_kaigo_ops_field_validation.py` が成功していることを確認する。

## 判定項目

### authoritative_source_reached

TRUE:

- 回答者が記録した source が、その質問の canonical `source_refs` のいずれかと対応する公的資料である
- かつ、回答に必要な該当箇所まで特定できている

FALSE:

- 検索結果一覧や二次解説までしか到達していない
- URLは公的資料でも、回答に必要な箇所を特定できていない
- 別論点の資料を根拠としている

### answer_correct

TRUE:

- 回答内容が canonical `short_answer` と矛盾しない
- 結論を逆転させる誤りがない

FALSE:

- 結論が誤っている
- 必須要件を任意扱いしている
- 条件付きの事項を無条件に断定している

### conditions_preserved

TRUE:

- `cautions` に含まれる重要な限定条件を、回答の意味を変えない範囲で保持している

FALSE:

- 限定条件を落としたため、実務上の意味が変わる
- 例: 「同意は必要だが署名は必須手段ではない」を「署名も同意も不要」と読める回答にしている
- 例: 「看護職員1以上」を「営業時間中ずっと常駐1人」と誤って固定している

### source_correct

TRUE:

- source が canonical `source_refs` と整合する
- locator が回答根拠として妥当である

FALSE:

- source は公的でも別の条文・別の対象サービス
- locator が不足し、該当根拠を再現できない

### human_correction_sec

回答を canonical 水準へ直すために、採点者またはレビュー担当が追加で要した時間。

修正不要なら 0。

## 採点順序

1. condition と時間情報を見ない
2. question_slug から canonical question を読む
3. answer_text を answer_correct / conditions_preserved の順に判定する
4. source_url / source_locator を authoritative_source_reached / source_correct の順に判定する
5. 必要なら修正内容と human_correction_sec を記録する
6. 全試行の採点完了後にのみ condition と結合して集計する

## 不一致時

採点者間で不一致が出た場合:

- どちらかに合わせるのではなく `adjudication_notes` に論点を残す
- canonical source へ戻って再確認する
- canonical 自体に曖昧さが見つかった場合、その試行を結果から都合よく除外せず pilot を Hold する

## 禁止

- Condition B に有利になるよう採点基準を変える
- 結果を見て `cautions` の重要度を変更する
- 失敗した質問を別の質問へ差し替える
- 回答内容を保存せず、正誤フラグだけを残す
