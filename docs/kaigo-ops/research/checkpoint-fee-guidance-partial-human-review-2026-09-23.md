# Kaigo Ops Research Checkpoint — Fee Guidance Partial Human Review

更新日: 2026-09-23  
対象: 老企第36号「7 通所介護費」machine-reconstructed candidates  
判定: **3 COMPLETE / 5 REVIEW_REQUIRED / overall IN_PROGRESS**

## 1. Currentness

厚生労働省「介護保険最新情報掲載ページ」を2026-09-23時点で確認した。

確認範囲:
- 最新掲載: Vol.1544（2026-09-18）
- 通所介護費7(4)〜7(25)の本文について確認した最新の改正: Vol.1502（2026-05-08）
- Vol.1523（2026-07-13）: 改正通知発出等に伴うQ&A Vol.2
- Vol.1524（2026-07-14）: 令和6年度介護報酬改定Q&A Vol.18

Vol.1523は協力医療機関連携加算、
Vol.1524は訪問リハビリテーション・介護老人保健施設等の論点であり、
今回対象の通所介護費7(4)〜7(25)の通知本文変更ではない。

2026-09-23時点の掲載一覧を確認した範囲で、
Vol.1502より後に当該通所介護費本文を改める通知は確認できなかった。

## 2. Human COMPLETE

### fee-guidance.dayservice.7-2

「感染症又は災害の発生を理由とする利用者数の減少が一定以上生じている場合の取扱いについて」

- R3導入時の本文を確認
- R6で番号移動・本文略を確認
- R7で通所介護部分の変更なし
- R8 3月改正で6〜9の変更なし
- R8 5月改正で7(1)〜(24)の変更なし

candidate SHA:
`889bc5c82bd620fe503433dd2f652971d10faed7bb95f67880a42b06ae654cf9`

### fee-guidance.dayservice.24

「定員超過利用に該当する場合の所定単位数の算定について」

- H27 baseline全文を確認
- H30: 本文変更なし・番号移動
- R3: 本文変更なし・番号移動
- R6: 現行7(24)への番号継続
- R7: 通所介護部分変更なし
- R8 3月: 6〜9変更なし
- R8 5月: 7(1)〜(24)変更なし

PDF text layerの欠落括弧は、公式ページ画像との突合に基づくdeclarative correctionを使用。

candidate SHA:
`94ff666fb351f24ee9081321d7aefdaac1f00afab078264e5570c0b7f5a885c4`

### fee-guidance.dayservice.25

「人員基準欠如に該当する場合の所定単位数の算定について」

- H27 baseline全文を確認
- H30: 本文変更なし・番号移動
- R3: 本文変更なし・番号移動
- R6: 現行7(25)への番号継続
- R7: 通所介護部分変更なし
- R8 3月: 6〜9変更なし
- R8 5月: ②にホを追加
- R8 patchは③の前へ挿入することを公式新旧対照表で確認

R8追加内容の要旨:
- 突発的で想定困難な事象
- 1割以内の人員不足
- a〜dを全て満たす場合
- 1年に1回
- 翌々月まで減算適用を猶予
- 別紙様式7と有効な求人票写しを都道府県知事へ報告

candidate SHA:
`7a2ebce94e4700736c6db527a095c4373581328eeacea435818c39b904b32031`

## 3. REVIEW_REQUIRED

### fee-guidance.dayservice.4

2時間以上3時間未満。

candidate本文は一次資料で確認できる。
ただしbaselineからR6までの中間改正を現在のreplay ledgerが十分に明示していない。
現行全文としてのCOMPLETEは保留。

### fee-guidance.dayservice.7

災害時等の取扱い。

candidate本文は一次資料で確認できる。
R3・R6以降は追跡できるが、H30を含む中間改正連鎖が十分に明示されていない。
COMPLETEは保留。

### fee-guidance.dayservice.5

延長加算。

H30 baselineに `①～③（略）` が残る。
全文候補ではないためCOMPLETE不可。

### fee-guidance.dayservice.6

事業所規模による区分。

R3 baselineに `③・④（略）` が残る。
⑤欠落は既に修正済みだが、全文候補ではない。

### fee-guidance.dayservice.18

栄養改善加算。

R3 baselineに複数の `（略）` が残る。
全文候補ではない。

## 4. Review ledger

`data/fee-guidance-review.json`:
- review_status: IN_PROGRESS
- COMPLETE: 3
- REVIEW_REQUIRED: 5
- currentness checked: 2026-09-23

`data/remuneration-review.json`:
- base_notice_review: COMPLETE
- delegated_review: COMPLETE
- fee_guidance_review: IN_PROGRESS
- overall: IN_PROGRESS

## 5. Drift guard

`scripts/research-fee-guidance-review-validate-v0.1.mjs`

検査:
- COMPLETE 3件のID
- REVIEW_REQUIRED 5件のID
- candidate SHA
- baseline snapshot
- patch snapshot
- 「略」を含む3候補の誤昇格防止
- remuneration reviewとの整合

## 6. Next

優先順位:
1. dayservice.4 のH30/R3中間状態を補完
2. dayservice.7 のH30状態を補完
3. dayservice.5 / .6 / .18 の省略部分を別の公式資料から埋める
4. 5件が閉じたらfee-guidance overall COMPLETEを再判定
5. その後にのみremuneration overall COMPLETEとclassifier gateの開放を検討

RAG実装は引き続きHOLD。
