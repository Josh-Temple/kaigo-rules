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
- `data/rule-nodes.json`: 回答ページへ接続済みの検証済み制度ノード\n- `data/ordinance37-nodes.json`: e-Gov現行XMLから生成する基準省令第37号の通所介護関連ノード\n- `data/ordinance37-relations.json`: 条・項・号の包含関係と第105条の準用関係\n- `data/ordinance37-application-rules.json`: 第105条の読替え規則\n- `data/ordinance37-meta.json`: e-Gov取得元、SHA-256、現行改正情報、件数、レビュー状態\n- `data/ordinance37-review.json`: 人手確認のオーバーレイ台帳。確認時の条文SHA-256を保持\n- `data/ordinance37-scope.json`: 通所介護DBとして取り込む条文範囲の正本
- `data/notice-nodes.json`: 回答ページへ接続済みの解釈通知ノード
- `data/notice-current-skeleton.json`: 老企第25号の現行骨格（通所介護・共通定義）
- `data/notice-source-chain.json`: 再構成に使う公式資料チェーンと完全性区分
- `data/notice-ordinance-relations.json`: 解釈通知ノードと基準省令ノードの対応候補
- `data/notice-amendment-events.json`: 2021年・2024年等の改正イベント
- `data/notice-current-meta.json`: 再構成状態・件数・安全条件
- `data/notice-current-review.json`: 人手確認のオーバーレイ台帳
- `data/notice-historical-backfill.json`: 過去HTMLから機械抽出した本文候補（現行扱い禁止）
- `data/notice-historical-backfill-meta.json`: 過去HTML取得元・SHA-256・抽出件数
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


## 基準省令データベース

基準省令（平成11年厚生省令第37号）は、手作業で本文を転記せず、e-Gov法令APIの現行XMLから生成します。

初期スコープは次のとおりです。

- 通所介護の直接規定：第92条〜第105条（第104条の2〜4を含む）
- 第105条で準用される共通規定：第8条〜第17条、第19条、第21条、第26条、第27条、第30条の2、第32条〜第36条、第37条の2、第38条、第52条
- 共生型通所介護（第105条の2・3）と基準該当通所介護（第106条〜第109条）は初期DBから分離

`npm run import:ordinance37` で、条・項・号の構造、準用関係、読替え規則、e-Govの改正情報を生成します。
生成直後の状態は `IMPORTED_NEEDS_HUMAN_CHECK` です。機械取り込みの成功だけで `VERIFIED_CURRENT` には昇格しません。


## 人手レビュー方式

e-Govから生成した `ordinance37-nodes.json` 自体には人手確認結果を書き込みません。
確認済み情報は `ordinance37-review.json` に別管理し、条文ID・確認時の `text_sha256`・確認日を記録します。
その後のe-Gov更新で確認済み条文のハッシュが変わった場合は、`validate:data` が stale review として失敗し、再確認が必要になります。


## 解釈通知の現行再構成

老企第25号は、令和6年度改正資料を「現行統合全文」として扱いません。公式資料は新旧対照表であり、現行骨格の確認に使える箇所と、過去資料を遡らないと本文が得られない箇所を分離します。

再構成は次の順です。

1. 最新の新旧対照表から現行側の番号・見出し・改正後文を配置する
2. 空いている箇所を令和3年度以前の資料から `INHERITED_UNVERIFIED` として補完する
3. 信頼できる過去版から改正イベントを順方向に再生する
4. 現在の骨格・本文と一致したものだけ人手確認へ進める
5. 順方向再生完了前は「現行統合版」と表示しない

`/notices` はこの再構成状況を確認するためのレビュー画面です。


### 過去HTMLからのバックフィル

`Extract historical notice backfill candidates` workflow は、厚生労働省の老企第25号HTMLから旧「通所介護に関する基準」部分を機械抽出します。
抽出先は `notice-historical-backfill.json` で、状態は必ず `HISTORICAL_BACKFILL_CANDIDATE` です。

この本文はそのまま現行本文へ昇格させません。2021年・2024年等の改正イベントを順方向に再生し、現在側の資料と整合した場合に限って次の確認段階へ進めます。


## 報酬ルールDB

通所介護の報酬は、報酬告示（厚生省告示第19号）、利用者数・人員等の算定方法を定める別告示（第27号）、算定上の留意事項通知を別レイヤーとして保持します。

`remuneration-current-skeleton.json` は通所介護費の骨格です。ベース本文をそのまま現行確定とはせず、令和8年度改定の新旧対照表を改正イベントとして順方向に再生してから確認します。共生型通所介護に固有の注7・注8はコア範囲外として分離します。
