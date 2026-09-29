# Issue 03 — 職員教育・引き継ぎが属人化する

更新日: 2026-09-30  
状態: Evidence synthesis v0.1 / public page candidate

## 1. Issue

介護現場の教育・引き継ぎでは、次のような負担が重なりやすい。

- ベテランや管理者へ同じ質問が集中する
- 研修に全員が同時参加できない
- manualや研修資料はあるが、必要な場面ですぐ見つからない
- 文書化された知識と、経験に基づく判断が混在する
- 新人が「誰に聞けばよいか」を覚えること自体がonboardingになる
- 異動・退職時に、知識の所在や更新責任が分からなくなる

このIssueでは「AI tutorを導入するか」ではなく、

> 繰り返し使う知識を正本化し、必要な時に取り出せるようにしつつ、経験判断を無理に自動化しない

ことを扱う。

## 2. 現時点の結論

現時点のEvidenceからは、次の順序が妥当。

1. 質問・引き継ぎ内容を記録し、反復するものを見つける
2. 文書化できる知識と、個別判断・経験知を分ける
3. 正本、owner、更新日、対象職種・場面を決める
4. 検索、FAQ、短い教材、peer learningを整える
5. 研修を一回の集合研修ではなく、業務中に参照できる仕組みにする
6. 必要ならAI検索・AI tutorを追加する
7. 高リスク判断は人間へ戻す

AIは、既存の知識管理と教育設計を置き換えるのではなく、正本へ到達する導線として使う。

## 3. 日本の主要Evidence

### 3.1 研修参加と運用能力の課題

Source:
厚生労働省「介護現場における生産性の向上等を通じた働きやすい職場環境づくりに資する調査研究事業一式」

URL:
https://www.mhlw.go.jp/content/12300000/001712213.pdf

2025年度の大規模調査では、施設・事業所内研修について、

- 全員が参加できない: 49.5%

という課題が報告されている。

またICT導入後の運用面では、

- PC・tablet等で記録することが困難な職員がいる: 44.2%
- トラブル時にPC/softwareの問題へ対応できる人材がいない: 34.4%

とされている。

これは、導入時の一度きりの説明だけではなく、

- 時間をずらして学べる
- 業務中に確認できる
- 困った時に支援へ到達できる

仕組みが必要であることを示す。

## 4. 研究Evidence

### 4.1 LTC workforce trainingのumbrella review

2026年のumbrella reviewでは、high-income countriesを中心とした19件のreviewを統合し、
continuing professional developmentやpeer-led trainingが職員のknowledge / competencyを改善する傾向を報告した。

一方で、元reviewの多くはqualityが低く、outcomeも異質だった。

したがって、

> 「研修を増やせば定着やcare qualityが必ず改善する」

とは言わず、何を学ぶか、どの業務で使うか、学習後の行動をどう確認するかまで設計する。

Source:
"Strategies to improve recruitment, retention, working conditions, and skills among the long-term care workforce: An umbrella review of existing evidence"

### 4.2 Online geriatric education

2026年のsystematic reviewでは、hospital、community、long-term careのnursing staffを対象としたonline educationを整理している。

online教育は柔軟でscaleしやすい一方、

- intervention design
- 対象者
- learning outcome
- 実務への移行

がheterogeneousで、単一の「最良のe-learning形式」を示すEvidenceではない。

重要なのは、集合研修を動画へ置き換えることより、

- 何を学ぶ必要があるか
- いつ参照するか
- 理解したか
- 実務で使えたか

を測ること。

### 4.3 Dementia training

2026年のsystematic reviewでは、13か国の27研究を対象に、social care workforce向けdementia trainingを整理した。

deliveryは、

- remote
- in-person
- blended

のいずれも使われていた。

形式だけで優劣を決めるのではなく、対象職種、内容、現場支援、outcomeによって設計を選ぶ必要がある。

### 4.4 Communities of Practice

2026年のLTCを対象とするsystematic reviewでは、Communities of Practiceのようなpeer learningが、
職員同士の学習やevidence-based practiceの実装を支える方法として整理されている。

ただし、参加時間、facilitation、management supportなどの組織条件に依存する。

「すべてをmanual化する」だけでなく、文書化しにくい実践知を共有する場も必要。

## 5. Digital / AI implementationから見える条件

2026年のgeriatric LTC nursing staffを対象としたsystematic reviewでは、digital technology acceptanceの主な要因として、

- digital competence
- perceived usefulness
- usability
- leadership / organizational support
- training
- staff participation in implementation

が挙げられた。

eligible studyは3件に限られており、強い一般化はできない。

それでも、

> 新しいtoolを配ることと、職員が実務で使えることは別

という実装上の注意を裏付ける。

## 6. 属人化を分解する

### A. 文書化できる知識

例:

- 手順
- approved manual
- FAQ
- 制度確認の入口
- system操作
- 研修資料
- checklist
- escalation先

→ 正本化、検索、FAQ、短い教材、AI検索の対象にしやすい。

### B. 文書化できるが更新責任が曖昧な知識

例:

- 「前はこうしていた」
- 古い様式
- 個人PCにある手順
- unofficial memo

→ AIへ入れる前に、owner / version / scopeを決める。

### C. 経験知・専門判断

例:

- 利用者ごとの状況判断
- ケアの優先順位
- 例外時の判断
- 対人調整
- 暗黙のworkaround

→ AIの確定回答へしない。mentor、peer review、case discussion等で扱う。

## 7. 海外ケースからの補助線

### Peterborough City Council — Hey Geraldine

Local Government Associationのcase reportでは、経験豊富な職員へ繰り返し質問が集中していたことを起点に、
social care staff向けknowledge assistantを構築した。

公開caseでは、

- testingで1,200件超の質問
- OT teamで1 conversationあたり15分削減と報告
- internal teamがcontentを更新
- query dashboardで頻出質問・knowledge gapを確認

とされている。

ただし、これは独立評価ではなくprovider/local-government case report。

Kaigo Opsで参考にするのは「15分」という数字より、

> 質問log → 反復知識を正本化 → 職員が検索 → 質問logから教育gapを再発見

というfeedback loop。

## 8. 改善パターン

### Pattern A — 質問logを取る

1〜2週間、

- 誰が
- 何を
- 誰に
- 何回
- 何分かけて

聞いたかを、個人情報を含めずcategoryで記録する。

反復する質問から優先する。

### Pattern B — 1テーマ1正本にする

各themeに、

- owner
- current version
- updated_at
- 対象職種
- 適用場面
- escalation先

を付ける。

### Pattern C — 研修を短く分解する

一回60分の研修だけでなく、

- 5〜10分のmicrolearning
- 業務別checklist
- FAQ
- その場で開ける手順
- case-based practice

を組み合わせる。

### Pattern D — peer learningを残す

すべてをdocumentへ押し込まず、

- case conference
- mentor
- peer review
- Communities of Practice

など、経験知を扱う経路を残す。

### Pattern E — AIは正本への入口にする

AIを使う場合も、

- source
- version
- updated_at
- applicable scope
- uncertainty

を返せる構造を先に作る。

個別ケア判断や制度上の確定判断を、training botの回答だけで完結させない。

## 9. AIを使わない選択肢

- FAQ
- wiki
- searchable manual
- checklist
- short video
- microlearning
- mentor制度
- peer review
- case discussion
- office hours
- onboarding checklist

普通の検索・教育・peer supportで十分ならAIを追加しない。

## 10. 小さな実験

### 2週間の質問log pilot

1. よく聞かれる質問をcategoryだけで記録
2. 上位10問を抽出
3. それぞれを
   - 文書化可能
   - 要専門判断
   - 個別case依存
   に分類
4. 文書化可能な上位5問だけFAQ / short guide化
5. 2週間後に
   - 同じ質問回数
   - 回答までの時間
   - 誤った自己解決
   - expertへのescalation
   を確認

FAQで十分ならAIを追加しない。

自然言語での検索負担が残る場合だけ、同じ5問でAI検索と比較する。

## 11. 現時点で言わないこと

- e-learningなら対面研修より優れている
- AI tutorなら教育時間を大幅に削減できる
- expert knowledgeをAI化すれば引き継ぎ問題が解決する
- peer learningをdigital化すれば離職率が下がる
- 海外caseの15分削減が日本の介護現場でも再現する

## 12. 次に確認すること

- 日本の介護現場におけるonboarding / training timeの定量Evidence
- 研修受講と実務能力の関係
- microlearning / blended learningのLTC固有Evidence
- expertへの質問集中の実態
- 質問logからtraining gapを抽出する運用
- AI assistantで誤答・outdated knowledgeをどう検出するか
- staff turnover時のknowledge continuity

## 13. 公開ページへの要約

公開ページでは、

1. 結論
2. 日本の研修課題
3. 属人化の3分類
4. Evidence
5. 改善パターン
6. AIを使う場合 / 使わない場合
7. 2週間の小さな実験
8. 分かっていないこと
9. 出典

に圧縮する。
