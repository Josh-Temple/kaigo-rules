# Issue 04 — 問い合わせ・連携の負担が大きい

更新日: 2026-09-30  
状態: Evidence synthesis v0.1 / public page candidate

## 1. Issue

介護事業では、事業所内だけでなく、

- ケアマネジャー
- 他サービス事業所
- 医療機関
- 家族
- 行政
- システムベンダー

との確認・共有が日常的に発生する。

負担は「連絡回数が多い」だけではなく、

- 同じ内容を電話・FAX・メールへ繰り返し送る
- 誰に聞くべきか分からない
- 相手によって様式・手段が違う
- 送った後の確認電話が必要
- 情報が足りず、聞き直しが発生する
- 緊急度が違う連絡が同じ経路へ流れる
- systemを入れても相手側が使わなければ連携できない

という構造から生じる。

このIssueでは、

> 連絡手段を増やすのではなく、連絡そのものを減らし、必要な情報を一度で渡せる流れを作る

ことを扱う。

## 2. 現時点の結論

現時点のEvidenceからは、次の順序が妥当。

1. 問い合わせ・連携を種類ごとに分ける
2. 何度も発生する確認をFAQ・共有情報へ移す
3. 送る情報・受け取る情報のminimum setを決める
4. 正本・owner・更新責任を明確にする
5. 連絡手段を整理し、緊急連絡と非同期連絡を分ける
6. data exchange / shared systemは相手側の採用条件まで含めて判断する
7. AIは要約・draft・routing補助に限定し、個別判断を確定させない

改善単位は「電話を減らす」ではなく、

> 問い合わせ → 回答 → 転記 → 再確認

という往復全体。

## 3. 日本の主要Evidence

### 3.1 ケアプラン・提供票共有には紙・FAX負担が残る

Source:
厚生労働省「介護事業所におけるデータ連携による生産性向上に関する調査研究等一式 報告書」

URL:
https://www.mhlw.go.jp/content/12300000/R5_ICT_houkokusyo.pdf

一部の調査対象では、ケアプラン・提供票共有業務について、

- 事業所内で保管する文書量が多い: 72.7%
- 郵送・FAX等の共有に時間がかかる: 54.5%

と回答している。

sampleが小さい箇所であり、全国値として一般化しない。

重要なのは、情報共有が「送る作業」だけでなく、

- 印刷
- 保管
- FAX / 郵送
- 到達確認
- 転記

を含むworkflowになっている点。

### 3.2 data exchangeにはnetwork adoptionが必要

同じ調査では、system利用意向が低い回答者で、

- 普及率が低くメリットが小さい: 100%
- 業務負担・業務種類が増える: 64.3%

が理由として挙げられている。

一方、今後利用したい理由では、

- 提供票共有時間の削減を期待: 60.6%
- 事務負担軽減を期待: 48.5%

が上位だった。

これらもsample条件付きで読む。

ここから見える実装条件は、

> 自施設だけの導入では価値が出ない連携業務がある

こと。

単独事業所で完結する業務改善と、複数組織が同じnetworkを使うdata exchangeは分けて考える。

### 3.3 ICT導入支援事業

厚生労働省「ICT導入支援事業 令和3年度 導入効果報告取りまとめ」では、
導入事業所の自己申告として、

- 情報共有がしやすくなった: 90.3%
- 事業所内情報共有が円滑: 88.0%
- 事業所外情報共有が円滑: 56.3%

などが報告されている。

ただし、

- 補助を受けた導入事業所
- 非導入対照群なし
- self-report

であり、因果効果として扱わない。

また多くの事業所が同時にworkflowや情報共有方法を見直していたため、
「systemを入れたから改善した」と単純化しない。

## 4. 日本の情報共有研究から見えること

2026年の日本のtransitional care研究では、病院から介護施設への情報共有について、

- 送る側と受ける側で必要情報の重点が違う
- care facility側が必要とする情報が自動的には揃わない
- timelinessにgapがある
- standardizationだけでは扱いにくい個別情報もある
- sensitive informationは記録自体が難しい場合がある

ことが報告されている。

Source:
Kawasaki et al. (2026)
"Swaying Information About Care: Information-Sharing Challenges in Transitional Care of Older Adults in Japan"

このため、連携改善では、

> 「共通様式を作る」だけでなく、「受け手が何に使う情報か」を先に揃える

必要がある。

## 5. 国際Evidence

### 5.1 Long-term care handoff / Health Information Exchange

2018年のsystematic reviewでは、LTCのpatient handoffにおけるHealth Information Exchangeを扱った22研究を整理した。

主な論点として、

- workflow integration / augmentation
- enhanced communication
- missing / incomplete data
- organizational structure / culture
- inefficiency

などが挙げられた。

重要なのは、連携toolが存在するだけでは不十分で、

> 既存workflowにどう入るか、必要情報が揃うか、組織側が運用できるか

が主要条件になること。

### 5.2 Interprofessional collaboration

2026年のsystematic reviewでは、LTC physicianとmedical specialistの連携を扱った16研究を整理し、

- teleconsultation
- on-site consultation
- multidisciplinary collaboration

の3類型を確認した。

reviewはquality of care / quality of life改善の可能性を示しているが、
study designとoutcomeの異質性が大きく、どの要素が最も有効かは確定していない。

したがって、

> 「オンライン連携を増やせば質が上がる」

とは言わない。

## 6. 問い合わせ・連携を四つに分ける

### A. 定型問い合わせ

例:

- 様式の書き方
- 提出先
- 締切
- status確認
- よくある制度確認

→ FAQ、self-service、status表示、検索で減らしやすい。

### B. 定型的な情報共有

例:

- ケアプラン
- 提供票
- report
- 定型連絡
- 更新通知

→ data exchange、shared template、structured form、通知設計が有効になり得る。

### C. 判断を伴う相談

例:

- 例外対応
- 医療との調整
- 利用者状態の変化
- service coordination

→ asynchronous messageだけで完結させず、責任者・専門職へescalationする。

### D. 緊急連絡

例:

- 急変
- 事故
- 即時判断が必要な事象

→ 通常の問い合わせqueueと分ける。

AIやticket systemへ統合しすぎない。

## 7. 改善パターン

### Pattern A — 問い合わせlogを取る

1〜2週間、

- 誰から
- 何について
- どのchannelで
- 何回
- 回答まで何分
- 再問い合わせがあったか

をcategoryで記録する。

個人情報は不要。

### Pattern B — 反復問い合わせをself-service化する

上位の定型問い合わせを、

- FAQ
- status page
- checklist
- guide
- searchable knowledge

へ移す。

問い合わせ窓口を増やす前に、問い合わせ自体を減らす。

### Pattern C — minimum information setを決める

連携相手ごとに、

- 必須情報
- 任意情報
- 緊急時情報
- 更新時だけ必要な情報

を整理する。

「全部送る」は避ける。

### Pattern D — channelを用途別にする

例:

- 緊急: phone
- 定型提出: system / structured form
- 非同期確認: message / email
- status確認: self-service

目的とchannelを対応させる。

### Pattern E — network adoptionを先に確認する

複数事業所間systemは、

- 相手が使うか
- 両側にaccountがあるか
- 既存systemと二重入力にならないか
- adoption率が低い時のfallback

を先に確認する。

### Pattern F — AIはroutingとdraftから

AIを使うなら、

- 問い合わせ分類
- FAQ候補提示
- reply draft
- 長文要約
- escalation候補

などから始める。

個別ケア判断、医療判断、制度上の確定判断をAI単独で返さない。

## 8. AIを使わない選択肢

- FAQ
- shared inbox
- ticket
- status page
- structured form
- template
- phone tree
- contact matrix
- escalation rule
- shared calendar
- data exchange
- notification rule

多くの定型問い合わせは、AIよりworkflow整理の方が再現しやすい。

## 9. 小さな実験

### 2週間のcommunication audit

1. 問い合わせ・連携をcategoryで記録
2. 上位10種類を抽出
3. それぞれを
   - eliminate
   - self-service
   - structured exchange
   - human judgment
   - emergency
   に分類
4. 上位3つだけ改善
5. 再度、
   - 件数
   - 往復回数
   - response time
   - escalation
   - 二重入力
   を測る

AIは、FAQやchannel整理後にも残る問い合わせだけで比較する。

## 10. Safety boundary

問い合わせ削減を優先しすぎると、

- 必要な相談まで抑制する
- 緊急連絡が遅れる
- 個別性の高い情報を定型formへ押し込む
- 誤ったself-service回答で相談が止まる

可能性がある。

したがって、

> 減らすのは「不要な往復」であって、「必要な相談」ではない

ことを明確にする。

制度上の判断が必要な問い合わせは、Kaigo Rules側の原典・検証状態へ接続する。

## 11. 現時点で言わないこと

- data exchangeを導入すれば必ず連携時間が減る
- 電話を減らせば業務効率が上がる
- AI chatbotで問い合わせ対応を自動化できる
- teleconsultationだけでcare qualityが改善する
- FAXを廃止すれば連携問題が解決する

## 12. 次に確認すること

- 日本の介護事業所での問い合わせ件数・通話時間の定量Evidence
- care manager / provider間の実際の往復回数
- ケアプランデータ連携システムのcurrent adoptionと実利用
- family communicationの負担とchannel設計
- structured messagingとphoneの使い分け
- AI routing / reply draftのerror correction cost
- small providerでのshared inbox / ticket運用コスト

## 13. 公開ページへの要約

公開ページでは、

1. 結論
2. 日本のdata exchange Evidence
3. 問い合わせ・連携の4分類
4. network adoption
5. 改善パターン
6. AI / non-AI
7. 2週間のcommunication audit
8. safety boundary
9. 分かっていないこと
10. 出典

に圧縮する。
