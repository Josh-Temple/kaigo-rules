# kaigo-rules

介護制度の公開資料を、実務の疑問から公式根拠へ戻れる形で構造化するプロジェクトです。

## MVP scope

- 対象サービス: 通所介護
- 対象範囲: 全国共通事項
- 初期質問: 12問
- 一次資料確認済み: 12/12
- 開設準備ガイド: v0.1
- 国Q&A構造化: schema + 初期実データ
- AI/Jev: 使用しない
- DB: 使用しない
- 正本: GitHub
- 公開先: Vercel

## Product entry points

1. 実務上の疑問から探す
2. これから通所介護を始める
3. 厚生労働省の国Q&Aから探す
4. 公式根拠資料を確認する

## Design principles

1. 結論より先に根拠の正しさを確保する。
2. 未検証の制度回答は公開しない（fail closed）。
3. 公式原文と当サイトの整理・要約を分離する。
4. 法令・基準省令・報酬基準・通知・Q&A・様式の関係を構造化する。
5. 解釈通知は「最新版の穴あき版 → 過去資料で補完 → 順方向再生で検証」の手順で現行版を再構成する。
6. Q&Aは元の発出文書・番号・日付・収載範囲を保持し、現在の制度ノードへ接続する。
7. 通知の数値基準は、省令本文と通知上の具体化を区別して表示する。

## Data validation

`npm run validate:data` で、質問・条文・通知・Q&A・出典のID参照整合を確認します。
Vercel build の前にも自動実行し、参照切れがある場合は fail closed でビルドを止めます。

## Data

- `data/questions.json`: 実務質問、検索用言い換え、検証済み回答
- `data/sources.json`: 公式資料台帳と収載範囲
- `data/rule-nodes.json`: 条・項・号単位の検証済み制度ノード
- `data/notice-nodes.json`: 解釈通知の構造化ノード
- `data/qa-items.json`: 回答ページへ接続済みのQ&A\n- `data/qa-corpus.json`: 公式XLSから機械取り込みしたQ&A（未レビューを含む）\n- `data/qa-corpus-meta.json`: 取得元URL、ハッシュ、抽出件数などの取り込み証跡
- `data/relationships.json`: 質問と制度ノードの関係
- `data/startup-steps.json`: 開設準備の導線
- `data/amendments.json`: 改正イベント

## Verification

`VERIFIED_CURRENT` は、指定した確認日に一次資料上の現行表示を直接確認した法令ノードです。
通知は現行統合全文の完全性が確認できるまで、部分ソースと再構成状態を分けて管理します。
Q&Aは単独で制度上の結論とせず、法令・通知との関係を保持します。

## Next

1. 厚生労働省Q&Aの公式XLSを取り込み、通所介護・通所系共通・居宅サービス共通・全サービス共通を構造化する
2. Q&A集の公式収載範囲より新しいQ&Aを別ソースから追加する
3. 基準省令の通所介護関連条文を体系的に全件構造化する
4. 解釈通知の通所介護部分を穴あき構造で再構成する
5. 開設準備ページを指定権者・申請書類へつなげる
6. 12問の型をもとに50問へ拡張する

## Q&A candidate linking

`npm run suggest:qa-links` は、12問のタイトル・検索用言い換えと国Q&Aの本文を決定論的に照合し、`data/qa-link-candidates.json` にレビュー候補を出力します。

候補はすべて `CANDIDATE_UNREVIEWED` です。候補になっただけでは回答ページの根拠には使いません。現行法令・解釈通知との整合を確認し、採用するものだけ `data/qa-items.json` と各質問の `qa_item_ids` に接続します。
