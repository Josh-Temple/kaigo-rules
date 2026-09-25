# Kaigo Ops 情報探索 Field Validation v0.1 — blind scoring calibration

作成日: 2026-09-25  
状態: Protocol fixed / result NOT_RUN

## 位置づけ

この文書は `field-validation-scoring-v0.1.md` の判定項目・成功条件・A/B割付を変更しない。
実測前に、既存の採点基準で判断がぶれやすい境界を固定するためのキャリブレーション資料とする。

## 判定を分ける原則

### answer_correct と conditions_preserved

- `answer_correct` は、回答の中心的な結論が canonical `short_answer` と矛盾しないかを見る。
- `conditions_preserved` は、その結論を実務上誤解させないための重要な限定条件が保持されているかを見る。
- 結論自体は正しいが重要な限定条件が抜けている場合、`answer_correct=TRUE` / `conditions_preserved=FALSE` とする。
- `cautions` の文言をすべて再現することは求めない。抜けると判断が変わる条件だけを対象にする。

例:

- 「通所介護計画への署名は国基準上の必須手段ではない」だけなら中心結論は正しい。
  ただし「利用者の同意は必要」が落ち、同意自体が不要と読める場合は `conditions_preserved=FALSE`。
- 「看護職員は1人以上必要」は中心結論の一部として正しいが、「営業時間中ずっと事業所内に常駐」と断定した場合は `answer_correct=FALSE`。

### authoritative_source_reached と source_correct

- `authoritative_source_reached` は、canonical `source_refs` と対応する公的資料の、回答に必要な箇所まで到達できたかを見る。
- `source_correct` は、提出した `source_url` / `source_locator` が実際の `answer_text` の根拠として対応しているかを見る。
- 公的資料に到達していても、locator が別条文・別論点なら両方FALSEとなり得る。
- canonicalな資料へ到達したが、提出回答の追加主張をその箇所が支えていない場合は、`authoritative_source_reached=TRUE` / `source_correct=FALSE` となり得る。
- 複数資料型の質問では、提出回答を成立させるのに複数資料が必要なら、一部資料への到達だけで「回答に必要な該当箇所まで特定」とは扱わない。

例:

- BCP研修で省令の「定期的」だけを確認し、「年1回以上」まで回答した場合、年1回以上を示す通知根拠がなければ `source_correct=FALSE`。
- 重要事項説明で第8条だけに到達し、ウェブ掲載義務まで回答した場合、その追加主張を支える根拠箇所が記録されていなければ `source_correct=FALSE`。

## human_correction_sec の計測

- boolean 4項目の判定を終えた後、canonical水準へ修正する作業を開始した時点で計測を開始する。
- 回答文と根拠が canonical水準になった時点で停止する。
- 修正不要は0秒。
- canonical自体に曖昧さが見つかった場合、推定時間を入れず pilot をHoldし、`adjudication_notes` に理由を残す。

## 採点時の固定手順

1. condition・時間・clicks・query_reformulations・confidenceを見ない。
2. canonical question の `short_answer` / `cautions` / `source_refs` を読む。
3. `answer_correct` を判定する。
4. `conditions_preserved` を判定する。
5. `authoritative_source_reached` を判定する。
6. `source_correct` を判定する。
7. 必要な場合だけ修正時間を測る。
8. 判断に迷った境界は `adjudication_notes` に残し、結果を見て基準を変更しない。

## 事前監査で確認した主な失敗モード

- 正しい結論と、限定条件の保持を同じフラグで処理してしまう。
- 「厚労省URLである」だけで source を正しいと判定し、該当条項・見出しを確認しない。
- 複数資料型で、一つの資料だけを見て回答全体の根拠が揃ったと扱う。
- Condition A/B を知った後で「この程度なら正解」と許容範囲を変える。
- canonical側の曖昧さを参加者の失敗として採点する。

上記が生じた場合は、既存 scoring protocol の不一致時・Holdルールを優先する。
