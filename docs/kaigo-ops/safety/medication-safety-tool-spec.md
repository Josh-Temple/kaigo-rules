# 服薬業務の安全点検シート — Worker C preview specification

Status: **PREVIEW_ONLY / NOT_FOR_PUBLICATION**  
Prepared: 2026-10-08 JST  
Repository: `Josh-Temple/kaigo-rules`  
Base for C: `main` at `a90119e9d9e9de3050a563178daa0bf6d7c47bb8`

## 1. 目的・責任境界

服薬業務の工程、手順の明文化、担当・引き継ぎ、作業中断、変更情報の共有、相談経路、振り返りを、**個人を特定しない選択肢**で棚卸しする。職員個人の過失や安全度を判定しない。

事故・疑義が発生している場合、使用者は事業所の正式な事故対応手順、管理者・関係医療専門職への連絡、必要な緊急対応、関係する法令・自治体のルールに従う。本ツールが処方・投薬・再投与・医療対応・事故報告要否を判定することはない。

初期ソース: Library の `2026-10-08_accident_prevention_and_medication_safety_foundation_wave_instructions.md`。この試作の選択肢・相談文章は **DESIGN_PROPOSAL** であって、一次資料による特定サービス向けの安全手順・法令義務ではない。Worker Aのsource registerとWorker BのIssue草案はmainに資料として統合済み。ただし試作UIの各文章・選択肢との段落単位の照合と専門職承認は未了である。サービス別適用性は `NOT_ESTABLISHED`。

## 2. 入力契約・出力

- 工程1個: 未選択／変更情報の受領・共有／配薬準備の運用／配薬・服薬確認に関する運用／記録・引き継ぎ。実在する工程・職種権限を本ツールが認定するものではない。
- 点検6項目: 手順、役割、作業中断、変更情報、相談経路、振り返り。
- 各項目の状態（B草案blob `083ffd0a17419e1533e65205e9230d725f3232ab` のB-05に対応）: まだ確認していない／取扱いを把握している（自己申告・未検証）／相談したい点がある／取り決めが見つからない／自分の担当範囲では扱わない（責任者確認前）。選択肢は独自の設計提案であり、原典の検証済み尺度ではない。
- 初期値: 工程=未選択、すべて=まだ確認していない。架空例ボタンは固定の選択肢のみ。
- 出力: 工程未選択・まだ確認していない・相談したい点がある・取り決めが見つからない・担当範囲では扱わない、を相談事項として表示。全項目『取扱いを把握している』でも自己申告・未検証の注意書きを表示し、スコアや安全宣言に変換しない。
- 全項目「取扱いを把握している」でも安全宣言を返さない。未回答・担当範囲外の自己申告を合格扱いしない。
- 不正な構造・選択値・余分な項目は `valid=false` とし、元の入力を反映しない固定のエラーだけを表示する。
- 印刷用概要には工程・選択項目・固定文言だけを出力し、実名・薬剤・事故詳細などの入力欄は設けない。

現場での正式手順の採用や職種の権限の確定は、管理者・関係専門職と所属事業所に属する。

## 3. 実装・公開分離

- Pure model: `ops-site/lib/medication-safety-review.ts`
- Feature-gated page: `ops-site/app/tools/medication-safety-preview/page.tsx`
- Client form: `ops-site/app/tools/medication-safety-preview/worksheet.tsx`
- Scoped CSS: `ops-site/app/tools/medication-safety-preview/preview.css`
- Unit + source invariants: `ops-site/tests/medication-safety-review.test.mjs`
- Browser regression: `ops-site/tests/browser/medication-safety-preview.spec.mjs`

`MEDICATION_SAFETY_PREVIEW` **未設定/未一致の場合は必ず404**。有効化はローカルホスト上のCI、または実証済みアクセス制限付きの非公開環境に限定する。匿名到達可能なVercel Previewには絶対に有効化しない。route は `force-dynamic`、metadata は `noindex, nofollow, nocache`。このURLは公開registry、ホーム、sitemap、Issue→tool一覧に登録しない。

**重要:** Previewでflagを有効にすると、URLを知る人にはアクセス可能となり得る。flagと`noindex`は認証・秘密性の代替ではない。専門職レビューまで一般公開できない場合はアクセス制限付き環境、またはローカル実行のみで点検する。PRのmerge/production releaseはIntegrator Eと人の許可を要し、flagをproductionでは有効にしない。

## 4. Privacy / security / observability

- クライアントのReact stateのみ。個人・利用者・薬・病名・処方・施設名・事故本文・自由記述・アップロード欄はない。
- シートの値に対する `fetch` / `XMLHttpRequest` / `sendBeacon` / サーバー保存 / `localStorage` / `sessionStorage` / クエリ埋め込み / 共有URL / 外部feedback転送はない。
- 印刷は利用者によるボタン操作のみ。ブラウザの「印刷/PDF保存」は端末側で行われる。
- **留意:** 既存の`app/layout.tsx`にはVercel Analyticsがある。プレビューの閲覧自体が匿名のページビュー計測対象となり得るが、選択回答をイベント・URL・payloadに載せない。Preview閲覧は実利用需要・安全改善の証拠に含めない。イベント追加も行わない。
- DOMには原則固定テキストと、固定選択肢の対応表示のみを出す。未知入力を表示しない。

## 5. 検証とゲート

実行コマンド（`ops-site/`を作業ディレクトリとする）:

```sh
npm ci
npm test
npm run build
npm run test:browser                      # flagなし: preview 404 + 既存5 tool regression
npm run start -- -p 3100                 # 別端末で起動後
npm run verify:routes -- http://127.0.0.1:3100
```

Preview明示動作確認（通常の公開設定とは別のローカル/アクセス制限付き実行）:

```sh
MEDICATION_SAFETY_PREVIEW=enabled npm run start -- -p 3100
# 別端末: MEDICATION_SAFETY_PREVIEW=enabled npm run test:browser
```

Tests cover: initial/unanswered/not-applicable; deterministic consultation list; invalid-value fail-closed; public registry non-mutation; no free-text/network/storage code; feature flag; synthetic example; print/reset; keyboard; 390px horizontal overflow. **200% zoom、専門職・現場利用者の操作評価、実ブラウザのローカル/Preview稼働、source-to-claim照合、productionでの不存在確認は、人手またはCI証拠がそろうまで未検証。**

| Gate | Status at implementation |
|---|---|
| No medical decision / no risk score | Source design; machine tests added |
| Choice-only / no worksheet persistence or transmission | Source design; machine tests added |
| Patient autonomy / service applicability | REVIEW_REQUIRED / NOT_ESTABLISHED |
| Worker A source register & B issue-scope review | main資料は存在。Cへの最終内容照合はREVIEW_REQUIRED |
| Expert / safety-owner review | EXPERT_REVIEW_NOT_DONE |
| Existing 5 Issue/5 tools | Code untouched; regression must pass |
| Mobile/200% zoom/a11y | 390px browser test added; 200% manual pending |
| Production publication | **NOT AUTHORIZED** |

## 6. 公開阻害条件と引き継ぎ

1. Aの一次資料の該当箇所と推奨/義務・対象サービスの対応が未統合。
2. BのIssue草案、正式手順・責任境界・サービス別適用の確認が未統合。
3. Dのadversarial reviewと関係専門職・事故防止責任者による確認が未完了。
4. 200%表示・Chrome Android等の実ブラウザ検証、CI regression・privacy監査を完了確認できていない。
5. 内容責任者による公開承認がない。Eによるpublic registry付加、公開判定とproduction exact SHA/alias確認も未実施。

判定の提案: **PREVIEW_ONLY**。Cの実装は安全点検の設計・検証対象であり、安全効果の実証でも正式な投薬業務マニュアルでもない。公開を急がず、A→B→Cの内容整合とD/Eのrelease gateを満たしてから再判定する。


## 7. 2026-10-08 第2回C検証追補（初版の未実施記述を更新）

- 検証対象アプリコードコミット：`54b84cd85981c785110b1a9459a5f8852fddd64f`（その後のドキュメントコミットは動作変更ではない）。
- 最新main比較時点：`d5e5b5f1c3a019c801c81c1af737964183bf7ce4`。PR #451はdraftのまま、mainへ統合しない。
- GitHub Actions run [37761326870](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37761326870)：flag enabled jobは13 PASS / 1 conditional skip、flag absent jobは8 PASS / 6 conditional skip。両jobで`npm ci`、`npm test`、`npm run build`、`npm run test:browser`、`npm run verify:routes`が成功。flag不正値のroute 404はHTTP smokeで確認。
- 回答の選択値について、Chromiumのrequest URL・headers・postData、URL/history、localStorage/sessionStorage、IndexedDBのデータベース名を動的に点検し、検査対象の選択値の露出を検出しなかった。ただしこれは限定された合成値・環境での試験であり、全環境での送信不存在を保証しない。
- 390px幅の操作と、1280px環境でのCSS zoom 200%模擬、label/focus/aria-live、印刷media/PDF生成、連続reset・cancel/reloadをChromiumで確認。**実Android端末、ブラウザUIのネイティブ200%ズーム、利用者の人手操作、スクリーンリーダーの実聴取は未実施**。
- 最初のCI run [37760983338](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37760983338) はbrowser history遷移先を固定値としたテストの誤前提で1 FAIL。修正コミット`54b84cd`で戻り先に依存しないURL漏えいと再訪問時初期化の検査へ変更し、上記runで再PASS。
- Cの詳細な実行台帳：`docs/kaigo-ops/safety/medication-safety-prototype-verification.md`。
- 公開可否は依然として`PREVIEW_ONLY / NOT_PUBLIC`。Dの独立検証、EX01/EX02とHU01の実承認、公開環境アクセス制限検証、正式な適用範囲判定は別ゲートとして未完了である。

## 8. 2026-10-08 第3回C：文言整合の固定条件

- 対象正本：B Issue draft `083ffd0a17419e1533e65205e9230d725f3232ab` の B-00、B-04〜06、B-09、B-12〜13。A claim trace `2cb32c3b4de093d51d410d23c04511e020a43571` は旧B段落に対応した版であり、最新版BへのAの独立再追跡はこのC実装では代行していない。
- `PROCESS_STAGES`と`CHECK_STATES`のラベルだけをBの語彙に合わせ、選択値の識別子は変更しない。ブラウザ状態・履歴・永続化・通信とのインタフェースを増やさない。
- 画面冒頭、状態選択の近接箇所、結果、印刷に、**平時の業務点検・自己申告・未検証・実施権限を判定しないこと・事故発生時の使用禁止**を配置する。ガイドラインの施設中心の適用範囲を一般化しない。
- B-05の表現はサイト独自の設計提案であり、出典に裏付けられた安全点検スコアではない。全確認・担当範囲外の自己申告でも安全確認済みと表示しない。
- 変更した文言のunit／Chromium期待値、request URL・headers・body、cookie、URL/history/storage、印刷の照合を再実行し、CI run・コードSHA・制約をCの検証台帳へ追記する。
- 手動の実Android Chrome・ネイティブ200%拡大・スクリーンリーダー、専門職EX01/EX02、公開承認HU01、Dの独立動的検査はいずれも本CでPASSとみなさない。
