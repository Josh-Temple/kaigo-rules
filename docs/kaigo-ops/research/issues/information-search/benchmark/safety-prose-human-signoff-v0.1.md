# Safety Prose Human Sign-off v0.1

更新日: 2026-09-23  
状態: **PENDING**

対象:
- `safety-answer-templates-v0.2.json`
- 11 safety cases

## 承認基準

各caseについて、次の5点を人が確認する。

- 結論がdecisionと一致する
- 条件・例外を落としていない
- 機械取込 / 独立機械照合 / 人手確認を混同していない
- 自治体固有事項やscope外を推測していない
- 回答を止める場合に次の確認先・行動が分かる

## Case checklist

- [ ] KS-001 LOCAL — 指定申請の締切・事前相談
- [ ] KS-002 OUT_OF_SCOPE — 地域密着型通所介護
- [ ] KS-003 OUT_OF_SCOPE — 共生型通所介護
- [ ] KS-004 REVIEW_REQUIRED — 基本報酬・加算・減算
- [ ] KS-005 REVIEW_REQUIRED — 地域区分・一単位単価
- [ ] KS-006 REVIEW_REQUIRED_CURRENTNESS — 期限付き経過措置
- [ ] KS-007 METADATA — Q&A corpus 843件
- [ ] KS-008 ANSWER — 看護職員
- [ ] KS-009 ANSWER — 生活相談員
- [ ] KS-010 ANSWER — 署名・押印
- [ ] KS-011 CLARIFY — 曖昧な兼務質問

## Sign-off record

- reviewer:
- reviewed_at:
- result: PENDING
- notes:

## 承認後

全11件に問題がない場合のみ `result: APPROVED` とし、reviewer / reviewed_at を記録する。

修正が必要な場合は、template本文を修正した新versionを作り、旧versionを上書きしない。
