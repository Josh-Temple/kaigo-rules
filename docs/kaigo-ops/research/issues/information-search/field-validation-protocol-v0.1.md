# Kaigo Ops 情報探索 Field Validation v0.1

作成日: 2026-09-25  
状態: Protocol fixed / result NOT_RUN

## 目的

Kaigo Ops の最初の Deep Issue「必要な情報を探すのに時間がかかる」について、

> 介護制度に関する実務質問で、正しい原典へ到達するまでの負担を減らせるか

を小規模に検証する。

AI導入の有無を評価する試験ではない。最初は、現在の一般的な原典探索と Kaigo Rules を使った探索を比較する。

## 固定した質問

質問セットは `field-validation-v0.1.json` を正本とする。

current main の `data/questions.json` にある verified 質問12件から、近い論点の重複を避けて10件を選んだ。

含める領域:

- 人員・勤務
- 設備
- 運営
- 計画・記録
- 説明・同意・署名
- 研修・委員会・訓練

単一資料で解ける問いと、通知等を含む複数資料の確認が必要な問いを混ぜる。

除外した2件:

- `multiple-roles`: 管理者兼務と論点が近く、10問では重複が大きい
- `care-plan-seal`: 署名の問いと近く、10問では重複が大きい

## 比較条件

### Condition A — 通常の原典探索

Kaigo Rules を使わず、厚生労働省・e-Gov等の公開情報から回答根拠を探す。

利用可能:

- 一般検索
- 厚生労働省サイト
- e-Gov
- ブラウザ内検索

利用しない:

- Kaigo Rules
- Kaigo Ops
- 生成AIによる回答生成

### Condition B — Kaigo Rules

Kaigo Rules の検索・ナビゲーション・実務質問ページを利用する。

利用可能:

- Kaigo Rules 内の検索
- 制度レイヤー
- 実務質問ページ
- 原典リンク

利用しない:

- 外部の生成AIによる回答生成

## 割付

同じ参加者が同じ質問を A/B 両方で解くと、1回目の学習効果が大きいため避ける。

参加者ごとに10問を5問ずつ A/B に分ける。

- Participant 1: FV-01〜05 = A、FV-06〜10 = B
- Participant 2: FV-01〜05 = B、FV-06〜10 = A

3人目以降はこの2パターンを交互に使う。

少なくとも2人で1セットとし、参加者数が増えても質問セット自体は変更しない。

## 記録と採点の分離

探索中は正誤判定を行わず、まず生データとして回答文・根拠URL・該当箇所を保存する。

回答品質は全試行終了後、`field-validation-scoring-v0.1.md` に従って condition と時間情報を伏せて採点する。

- 生データ: `field-validation-run-template-v0.1.csv`
- 採点: `field-validation-adjudication-template-v0.1.csv`

これにより、Condition A / B を知った状態で正誤を付けることによる観察者バイアスを減らす。

## 計測項目

各試行について次を記録する。

1. `time_to_first_authoritative_source_sec`
   - 正しい一次資料または公的資料へ最初に到達するまでの秒数
2. `time_to_answer_submission_sec`
   - 回答者が回答文と根拠を確定して提出するまでの秒数
3. `answer_text`
   - 回答者が確定した回答そのもの
4. `source_url`
   - 到達した根拠資料のURL
5. `source_locator`
   - 条・項、資料内見出し、ページ等の該当箇所
6. `clicks`
7. `query_reformulations`
8. `confidence_1_5`
   - 回答者自身の確信度。正しさとは別に記録する

次は採点時に付与する。

9. `authoritative_source_reached`
10. `answer_correct`
11. `conditions_preserved`
12. `source_correct`
13. `human_correction_sec`

## 最重要指標

主指標:

> 正しい原典へ到達するまでの時間

副指標:

- 正答到達時間
- 根拠到達率
- 条件保持率
- 誤答率
- クリック数
- 検索語の修正回数

## 成功条件

v0.1 では小標本のため、有意差検定を成功条件にしない。

Kaigo Rules を次段階へ進める目安:

- 根拠到達率を悪化させない
- 条件保持率を悪化させない
- 10問全体または複数カテゴリで、原典到達時間が明確に短くなる傾向がある
- human correction が増えない

時間短縮が見られても、誤答や条件落ちが増える場合は成功と扱わない。

## 中止・Hold条件

次のいずれかが発生した場合、その質問は効果測定から外して source review へ戻す。

- `data/questions.json` で status が verified ではなくなる
- title / category / last_verified が固定時点から変わる
- 参照する source が失効・差替えとなる
- canonical answer 自体に再確認が必要となる
- 現行制度かどうかを正本から確認できない

質問を都合よく別の質問へ差し替えず、変更理由を記録して v0.2 を作る。

## 結果の扱い

生データは `field-validation-run-template-v0.1.csv`、採点結果は `field-validation-adjudication-template-v0.1.csv` を使う。

v0.1 の計測前に、公開サイトで「時間が短縮した」「効率化できた」とは記載しない。

結果公開時は平均値だけでなく、

- 質問別
- 単一資料 / 複数資料
- 成功 / 失敗
- 条件落ち
- 探索が遅くなった例

も残す。

## 次の判断

結果に応じて次を選ぶ。

- Kaigo Rules のナビゲーション改善
- 検索導線改善
- FAQ / curated answer の改善
- 情報源の再整理
- それでも残る探索負担に限り、source-grounded AI 検索との比較

RAGを先に導入することは、この pilot の目的ではない。
