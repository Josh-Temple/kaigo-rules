# Kaigo Ops Research Checkpoint — Claim Routing Natural-Language Gate

更新日: 2026-09-22  
状態: **natural-language gate complete / 112 classifier checks PASS**

## 目的

claim promotion後に、

- 自然な言い換えでverified claimへ着地できない
- 曖昧な質問がIssue-level fallbackでANSWERになる

という2種類の問題を分けて確認した。

## 初回probe

昇格済み2 claimに対して12問を作成した。

初回の単純な見方では2問がREVIEW_REQUIREDとなったが、意味を確認すると、その2問は「機能訓練のスペース」「訓練用の部屋」としか書かれておらず、食堂・機能訓練室の複数室合算claimと断定するには情報が不足していた。

したがって、ここをfalse abstentionとしてANSWER化するのは不適切と判断した。

## 実際に見つかった問題

classifier v0.5を、意味を固定した12ケースで評価すると 7 / 12。

失敗は2種類。

### False ANSWER — 3件

- サービス調整会議
- 会議
- ケアマネとの会議

これらをサービス担当者会議と断定できないにもかかわらず、生活相談員IssueのfallbackでANSWERになっていた。

### Claim resolution miss — 2件

- 「面積は合算できますか」
- 「2室」「合計面積」

論点は明確でANSWERになるが、Claim Registryの語彙が狭く、Issue-level fallback経由になっていた。

## 修正

Claim Registry v0.3へ、必要な範囲だけrouting metadataを追加した。

- サービス担当者会議claim:
  - `fallback_guard_terms: ["会議"]`
- 地域連携時間candidate:
  - 町内会、自治会、ボランティア、地域連携、社会資源をguard
- 複数室合算claim:
  - 合算、合計面積、2室、2部屋等を明示的な言い換えとして追加
  - 同じ語をfallback guardにも利用

classifier v0.6では、

```text
explicit Claim match
  ↓ no
Claim Registry fallback guard
  ↓ no
Issue-level fallback
```

とした。

## 結果

- natural-language gate: 12 / 12
- verified regression: 51 / 51
- coverage gap: 20 / 20
- false-ANSWER stress: 12 / 12
- external Q&A: 15 / 15
- claim promotion: 2 / 2
- total classifier checks: 112 / 112

## 重要な知見

**false abstentionを減らすこと自体を目的にしない。**

情報が不足している質問までANSWERへ寄せると、今回守っている

`similarity ≠ answerability`

を壊す。

改善対象は、

1. 意味が十分明確なのにClaimへ着地しないケース
2. 意味が不十分なのにIssue fallbackでANSWERになるケース

を分ける必要がある。

## 次

次は2 claimだけのsynthetic probeから広げる。

優先順:

1. 既存verified claimへの自然な質問を増やす
2. 可能なら外部・実利用由来queryを追加する
3. verified claim側へrouting metadataを段階的に移す
4. Issue-level fallback依存率を測る
5. human sign-off
6. その後にRAG比較

production app codeは変更しない。
