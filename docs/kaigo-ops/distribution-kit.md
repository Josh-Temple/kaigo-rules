# Kaigo Ops — Public Distribution Kit

更新日: 2026-10-08  
状態: canonical public-entry / shareability record  
対象: Kaigo Ops

## 目的

Kaigo Opsの既存Issueを第三者へ直接共有するとき、トップページの文脈がなくても、

- 何の困りごとか
- 何が根拠で、何が改善案か
- 最初に何を試せるか
- 制度確認をどこで行うか
- どこへfeedbackを返せるか

が分かる公開入口として扱えるようにする。

この文書にある紹介文は外部共有用の**文案**であり、X、note、メール、SNS、コミュニティ等への投稿をWorkerへ許可するものではない。

## 2026-10-08 fresh audit baseline

Repository:

- fresh main: `61620d77976b0fb692256c4b18993ef1498e4116`

Kaigo Ops production:

- project: `kaigo-ops`
- project id: `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`
- production deployment: `dpl_63FnsT15tnNQ1YDmTkJAYNyNh27v`
- runtime release SHA: `b7a29a0da5c24787a9792bb6c55e6a14a330f897`
- public alias: `https://ops-site-pi.vercel.app/`
- deployment state: `READY`

Productionでhome、5 Issue、5 action toolをfresh確認し、すべてHTTP 200だった。

優先2 Issueはproductionでいずれも、

- 困りごとをh1と冒頭説明で提示
- 根拠と改善案を別セクションで提示
- AI / DXを目的化しない説明
- 小さく試す手順
- action toolへの導線
- Kaigo Rulesへの制度確認導線
- GitHub Issuesへのfeedback導線
- canonical URL
- Open Graph title / description

を確認した。

390px journeyはcurrent production releaseのcanonical verificationでPASS済み。今回のWorker C差分ではlayout / CSS / navigation structureを変更しない。

## Direct-entry audit

| 項目 | 情報探索 | 記録・文書 | 判定 |
|---|---|---|---|
| 最初の画面で困りごとが分かる | h1とleadで明示 | h1とleadで明示 | PASS |
| 根拠と提案を区別できる | 根拠・結論・改善順序を分離 | 根拠・改善順序・AI / 非AIを分離 | PASS |
| AI導入が目的に見えない | 情報の土台を先に整える | 重複・転記を先に減らす | PASS |
| 最初の小さな実行が分かる | よく聞かれる10問から測る | 1週間、記録作業を4区分で測る | PASS |
| action toolへ進める | 情報探索の棚卸しシート | 記録業務の見直しシート | PASS |
| Kaigo Rulesへ戻れる | contextual link + home | contextual link + home | PASS |
| feedbackへ進める | GitHub Issues | GitHub Issues | PASS |
| share metadata | canonical / OG / Twitter summary | canonical / OG / Twitter summary | PASS |
| mobile | current production 390px verification済み。Cではlayout/CSS変更なし | 同左 | PASS / no structural change |

Auditで確認できた軽微な品質不整合は、情報探索Issueの

- 「人間による人間による現場検証」という重複表現
- ページ上部の「最終更新: 2026-10-07」とfooterの「最終更新: 2026-09-29」の不一致

の2点だった。shareabilityのための新しいclaimや広告的CTAは追加せず、この2点だけを修正対象とする。

---

## 推奨共有対象 1 — 情報探索

URL:

`https://ops-site-pi.vercel.app/issues/information-search`

### 対象者

- 制度、通知、Q&A、マニュアル、事業所内資料を探す時間が長い現場
- 情報の正本、更新責任、保管場所が分散している事業所
- AI検索を導入する前に、通常検索や情報管理を見直したい担当者

### このページでできること

- 情報探索の負担を「検索性能」だけでなく、正本・重複・更新経路の問題として整理する
- AIを追加する前に、不要情報の削減、正本の明確化、通常検索の改善を順に検討する
- よく聞かれる質問を使った小さな確認方法を把握する
- 情報探索の棚卸しシートへ進み、正本・保管場所・更新責任・探索経路を並べる
- 制度判断が必要な場合はKaigo Rulesと一次資料へ戻る

### このページが主張しないこと

- 人間の探索時間が短縮されたこと
- AI検索が通常検索より優れていること
- Machine Retrieval Benchmarkが現場の使いやすさや業務効率を実証したこと
- 個別事業所の制度適合
- pageviewや共有数から推定した需要や改善効果

### 紹介文案

制度・通知・Q&A・事業所内資料が散らばり、必要な根拠を探すのに時間がかかるときの見直し方を整理したページです。AI検索ありきではなく、不要な情報を減らし、正本・更新責任・検索導線を整える順序と、棚卸しシートを使った小さな確認方法を紹介します。

---

## 推奨共有対象 2 — 記録・文書作成

URL:

`https://ops-site-pi.vercel.app/issues/documentation`

### 対象者

- 介護記録、報告、転記、後追い記録に時間がかかる現場
- 記録ソフトを導入しても紙・別システム・請求等への再入力が残る事業所
- 音声入力や生成AIを試す前に、記録業務そのものを見直したい担当者

### このページでできること

- 記録作業を不要な記録、正本、転記、入力方法、AI下書きの順に分けて検討する
- 公的資料の数値を、一般的な効果率ではなく条件付きの観測として確認する
- 1週間の作業計測で、必要な記録・転記・探索・後追い記録を分ける
- 記録業務の見直しシートへ進み、改善前後を同じ条件で比較する
- 制度上必要な記録はKaigo Rulesと一次資料で確認する

### このページが主張しないこと

- 生成AI単体で記録時間が一定割合減ること
- 音声入力やAI要約によって記録品質が向上すること
- 小規模実証の前後差を一般的な因果効果として適用できること
- action toolへの入力だけで改善成功や制度適合を確認できること
- 個人情報や介護記録本文をKaigo Opsへ送信・保存すること

### 紹介文案

介護記録・報告・転記などの文書作業をどこから見直すかを、公的資料と研究をもとに整理したページです。生成AIありきではなく、不要な記録・重複入力・転記を先に減らし、その後にICTやAIによる下書きを比較します。記録業務の見直しシートで小さく試せます。

---

## Feedbackを求める場合の一文

実際に試した方は、「何を試したか」「どこで止まったか」「何が足りなかったか」の3点だけでもフィードバックいただけると、次の改善に役立ちます。GitHub Issuesは公開・保存されるため、氏名、利用者情報、介護記録、事業所の非公開情報は記載しないでください。

## 共有時の運用境界

- 共有先の困りごとに合うIssueを1本だけ渡すことを基本とする。
- 「AIで解決できる」「時間が何％減る」など、ページ本文が支持していない表現を追加しない。
- 制度上の判断はKaigo Opsで確定せず、Kaigo Rulesと一次資料へ戻す。
- 紹介文のクリック数、pageview、feedback件数だけから需要や効果を断定しない。
- 外部投稿はユーザーが明示的に許可した場合だけ実行する。
