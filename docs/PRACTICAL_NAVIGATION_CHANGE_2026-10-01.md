# 実務質問から公式根拠への導線修復

## 確認した正本

- GitHub main: df06dcf3cc348a5082b350ce55ea44c169c2759a。Repository内AGENTS.mdなし。
- production /api/version及びVercel metadata: 同SHA。
- Structure Queue QUEUE!A1:AD1200 fresh read: dayrehab 23行（864〜886）、DONE_STAGING、validator NOT_RUN。Queue状態を公開データの検証状態へ継承しない。
- Cycle 3 Committer Review全文、報酬・算定留意事項Resultのsource manifest / scope inventoryを再取得。既存mainのsource-specific公開を確認。

## 観測と変更

本番の看護職員FAQ→問50検索は0件だった。自然文検索では看護職員以外の運営規程・重要事項説明書・研修FAQも展開された。通知relationにはQ&A一覧が混ざっていた。これらを固有IDの詳細ルート、版の説明、同じ通知source resolver、質問文の定型表現の弱化と強い一致を基準にした相対順位で修正した。個別FAQの順位はハードコードしていない。

Q&A corpusの問番号は欠落しているため、番号文字列をキーにしていない。旧問50はcanonical curated ID→保存済みcorpus IDを明示対応した。2024年問59のPDF物理36ページには旧問50の修正であることが明記されており、別版・別IDで直接接続する。旧問の発出文書PDFへの固有ページリンクは未確立で、公式Excelのサービス・論点・発出資料locatorを表示している。旧問を現行扱いしない。

通所リハのナビは専用基準・通知・報酬・限定検索ルートを維持する。通所介護または共通台帳へ移るリンクは対象範囲を明示する。通所リハ検索は基準省令のみで、他レイヤーは出典別一覧への導線。全レイヤー横断全文検索の完成とは主張しない。

確認状態のpresentationは原文の機械照合・現行性・人手確認を分け、HOLD/GAP/旧資料のみを隠さない。現行性調査の対象末日とreceiptパスを表示し、現行性確認済みの日付とは表示しない。

## 通所リハの残レイヤー

開始時点で報酬基準と算定上の留意事項はmain・本番へbounded publication済みだった。重複実装を加えず、独立laneを再実行した。42親項目/14基本報酬区分/70値/24注/令和8差分6率、R6留意事項33slot/88child markerを独立再確認。PASSはsource inventoryの限定一致であり、全文転記・PDF列配置・現行統合本文・人手レビューを保証しない。現行性GAP・人手NOT_REVIEWEDを維持する。

## 回帰と価値の限界

5問の実務検索→FAQ→該当条文→公式資料に加え、看護職員のQ&A修正と通知項目、通所リハ5ルートを自動検証する。HTMLのscript内payloadは表示証拠に数えない。条番号・canonical ID・条件・公式PDFの該当ページ本文まで確認する。既存CIとproduction release pathにも継続回帰を追加した。

既存product-value snapshotの件数・coverageは変更していない（1557/1557、FAQ根拠経路12/12）。これらは静的収録・参照整合の指標であり、今回のような0件導線を検出できる指標とは異なる。新規の利用回帰5問の結果はCI/release artifactで記録する。外部利用者の所要時間・判断改善は未測定。

## GAP

- 通所リハ報酬・算定留意事項の現行性、全改正履歴、人手確認は引き続き未確定。
- 旧Q&A問50は原発出PDFの該当ページへの直接接続が未確立。公式Excelの論点locatorから確認する。
- 既存Q&A corpusの問番号欠落を推測補完していない。
- 共通ナビの一部は通所介護または共通台帳へ移る。対象範囲を明示し、未公開サービスのデータは混ぜない。

一回限りのworkflowは追加していない。shortstay-lifeの公開設定は変更していない。
