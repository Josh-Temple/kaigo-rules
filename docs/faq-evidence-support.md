# FAQ根拠補助データの位置づけ

更新日：2026-09-25

## 目的

Kaigo Rulesの実務FAQは、制度情報基盤へ入るための厳選されたナビゲーション層です。

FAQ詳細ページとAI向けQuestion Context Packageでは、読みやすさのために次の小さな補助データを使います。

- `data/rule-nodes.json`
- `data/notice-nodes.json`
- `data/qa-items.json`

これらはFAQごとに必要な根拠を取り出しやすくした表示・検索用の補助データであり、制度レイヤー全体の正本ではありません。

## 正本との関係

| 補助データ | 役割 | 正本・確認先 |
| --- | --- | --- |
| `rule-nodes.json` | 基準省令のFAQ向け抜粋・読替え後表現 | `ordinance37-nodes.json` / `/rules/[article]` |
| `notice-nodes.json` | 解釈通知のFAQ向け要約・部分根拠 | `notice-current-skeleton.json` / `/notices` |
| `qa-items.json` | FAQで直接使う国Q&Aの小さな構造化抜粋 | `qa-corpus.json` / `/qa` |

正本側の本文確認、現行性、人手確認は `data/verification-registry.json` と各レイヤーの監査・レビュー台帳で管理します。

## `verified` の意味

`data/questions.json` の `status: verified` は、

> そのFAQの結論と、FAQに列挙した根拠との対応を確認した

ことを示します。

次の意味ではありません。

- 解釈通知全体の現行統合版が確定した
- 根拠レイヤー全体の人手確認が完了した
- 関連するすべての関係エッジが独立監査済みである
- 指定権者独自の取扱いまで確認済みである

公開画面ではこの意味を「FAQ根拠対応を確認済み」と表示します。

## 運用ルール

1. 補助データの状態を、そのまま制度レイヤー全体の確認状態として扱わない。
2. 正本DBに対応する入口がある場合、FAQから正本DBへ戻れる導線を維持する。
3. 正本スコープ外の根拠を無理に正本IDへ変換しない。公式資料への直接リンクを残す。
4. AI向けContext Packageでは、補助データに `evidence_role: FAQ_PRESENTATION_SUPPORT` と `canonical_authority: false` を付与する。
5. FAQの根拠対応と、relation edgeの独立監査結果は別の保証情報として扱う。

## CI

`scripts/validate_faq_evidence_support.py` が次を検査します。

- manifestが3つの補助データを明示していること
- FAQからの参照切れがないこと
- 公式source参照が存在すること
- 基準省令の補助IDから正本の条文入口へ戻れること、または明示的な例外理由があること
- FAQページに確認範囲の説明と正本への導線があること
- AI向けContext Packageに補助データの役割が明示されていること

このvalidatorは `npm run validate:data` とunit testの両方から実行されます。
