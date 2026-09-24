# 海外介護DX・AI事例 — Japan Transferability Review v0.1

調査日: 2026-09-22  
状態: Comparative review v0.1

## 目的

海外で使われている介護DX・AIを「日本でも使える / 使えない」と単純評価せず、

- 何がそのまま移せるか
- 何を変更する必要があるか
- 日本固有の制度・運用で詰まりやすい場所はどこか

を明示する。

## 比較軸

1. problem fit — 日本にも同じpainがあるか
2. source/data fit — 必要なdataが揃うか
3. workflow fit — 日本の介護workflowに入るか
4. regulation/privacy — 個人情報・制度判断への影響
5. human-review burden
6. interoperability
7. organization size / support capacity
8. cost / vendor dependency
9. evidence quality
10. smallest safe experiment

---

## Case A — Uniting (Australia): policies / procedures向けGenAI assistant

Source: Australian Government Department of Health, Disability and Ageing  
https://www.health.gov.au/resources/webinars/digital-transformation-tech-talk-19-february-2025

### 実装

Unitingは最初に各部門のpain pointを集め、GenAIの最初のuse caseとしてpolicies and proceduresを選択した。

公開説明では、

- 441件のpolicies/procedures
- 自組織が作成したdata
- PIIを含まないlow-risk use case
- executive / board buy-in
- business testers
- security controls / data classificationと並行
- 後にSharePoint Online全体へ対象を拡大

という段階的導入を行っている。

従業者からは、従来15〜20分かかる探索をpoint of careで秒単位にできるという期待・feedbackが示された。ただし、これはprovider presentation内の報告であり、独立したtime studyではない。

### 日本とのfit

**比較的直接移植しやすい。**

理由:

- 日本の介護事業所にも規程、manual、感染症/BCP資料、研修資料等のcodified knowledgeがある。
- 利用者個人情報を使わずprototypeを開始できる。
- 正誤確認を文書原典と照合できる。
- 「介護ルール」はより安全なpublic-source版testbedになる。

### 必要な変更

大規模providerのMicrosoft/Azure/SharePoint環境を前提にしない設計が必要。

小規模事業所では、

- 文書の版管理が弱い
- ownerが不明
- folder構造が不統一
- security administratorがいない

可能性がある。

したがって日本向けには、AIより先に

`source inventory → owner → current version → scope → access`

を簡単に整備できる仕組みが必要。

### 最小実験

公開制度情報または個人情報を含まない事業所manual 30〜100文書で、

- ordinary search
- FAQ
- RAG

を比較する。

---

## Case B — Peterborough (England): “Hey Geraldine” expert knowledge assistant

Source: Local Government Association  
https://www.local.gov.uk/case-studies/peterborough-city-council-hey-geraldine-personalised-ai-assistant

### 実装

特定の経験豊富な職員へ繰り返し質問が集中していたことを起点に、knowledge assistantを作った。

公開case reportでは、

- testing中1,200超の質問
- OT teamで1 conversationあたり15分削減
- internal teamがbackend contentを更新
- query dashboardから頻出質問・支援gapを確認

と報告されている。

独立評価ではない。

### 日本とのfit

**problem fitは高い。**

介護現場でも、

- 管理者
- ベテラン
- 請求担当
- 研修担当

への問い合わせ集中は起こり得る。

ただし「人の経験」をそのままLLMに入れるのは危険。

### 必要な変更

knowledgeを二分する。

#### Codified
- manual
- rule
- checklist
- FAQ
- approved procedure

→ AI検索対象にできる。

#### Tacit / professional judgment
- 状況判断
- 利用者個別の判断
- informal workaround
- 経験則

→ AIの確定回答にしない。

### 最小実験

1か月、expertへの質問を匿名化したcategoryだけで記録し、

- 頻度
- 反復率
- 文書化可能率
- high-risk判断率

を測る。

反復かつcodified可能な質問だけFAQ/RAGへ移す。

---

## Case C — Newcastle (England): Magic Notes

Source: GOV.UK Algorithmic Transparency Record  
https://www.gov.uk/algorithmic-transparency-records/newcastle-city-council-magic-notes

### 実装

Adult Social Careの会話を録音し、

- speech-to-text
- LLM summary
- practitioner review/edit
- case-management systemへ転記

する。

公式透明性記録では、

- 自動意思決定をしない
- practitionerが全outputをreview
- SSO / MFA
- UK/EEA storage
- vendor/subprocessor controls
- personal / special category dataを処理
- 反対があれば録音しないfallback
- staff training

等が明示されている。

### 日本とのfit

**conditional / substantial adaptation。**

記録負担というpainは共通だが、Type Aのknowledge searchよりriskが高い。

### 日本で先に必要なもの

- 個人情報・要配慮個人情報の取扱い整理
- recordingの説明
- access control
- retention
- vendor/subprocessor確認
- transcript/summaryの人間確認責任
- AI outputと正式記録の境界
- error correction
- fallback

### 重要な原則

Magic Notesで参考になるのはmodel名より、

> **AI outputをdraft扱いにし、最終記録と意思決定を人間へ残すoperating model**

である。

---

## Case D — Denmark: digital training / video visits

Sources:
- KL welfare technology program
- KL Technology Radar 2026

https://www.kl.dk/sundhed-og-aeldre/aeldrereformen/implementering-af-aeldrereformen/velfaerdsteknologi-i-aeldreplejen
https://www.kl.dk/videncenter/teknologier/kommunernes-teknologiradar-2026/teknologierne-paa-sundheds-og-aeldreomraadet

### 実装状況

KL Technology Radar 2026では、回答自治体の

- digital training: 82%が運用
- video visits: 67%が利用

とされる。

同調査では、video solutionsを最大のvalue creatorとした回答が合計40%。

これはclinical trialの効果率ではなく、municipal respondentsのadoption/value perceptionである。

Denmarkではさらに、個別pilotの羅列より、成熟したsolutionを他自治体へscaleする枠組みを作っている。

### 日本とのfit

**technology fitは比較的高いが、service-design fitはconditional。**

remote interaction自体は日本でも可能だが、

- 訪問介護・看護等の制度上の取扱い
- 対面サービスをremoteへ置き換えられる範囲
- 利用者のdigital literacy
- device / network support
- emergency escalation
- family support

を分けて検討する必要がある。

### 日本への示唆

製品より、Denmarkの

`pilot → effect measurement → mature solution selection → cross-municipality scaling`

の流れが参考になる。

---

## Case E — Denmark: data-driven routing / rostering

Source:
https://www.kl.dk/oekonomi-og-administration/digitalisering-og-teknologi/indsatser-og-fokusomraader/velfaerdsteknologi

KLはscale対象として、

- video visits
- digital training
- data-driven route planning
- data-driven rostering

を挙げている。

### 日本とのfit

**conditional。**

最適化problemは共通だが、日本ではconstraintが多い。

例:

- 人員基準
- 資格
- 常勤換算
- 兼務
- service-specific rules
- 労働時間
- 希望休
- 利用者との継続性
- 移動時間
- 地理

### 重要な示唆

AI/optimizationは「自動で勤務表を作る」より、

> hard constraintsを機械で守りながら、人間がsoft constraintsを調整する

用途から始めた方が安全。

日本のMHLW小規模実証でも、AI schedule toolで「作成」より「転記・職員間調整」の時間減少が大きかった。

---

## 6. Transferability matrix

| Case | pain fit | data risk | 日本への移植 | 最初に試す範囲 |
|---|---|---|---|---|
| Uniting policy assistant | 高い | 低〜中 | relatively direct | 個人情報なしの規程・manual |
| Hey Geraldine | 高い | 低〜中 | conditional | 反復するcodified FAQ |
| Magic Notes | 高い | 高い | substantial adaptation | まず非個人情報documentationで運用設計検証 |
| Denmark video visits | 中〜高 | 中 | conditional | 対面代替ではなく補完use case |
| Denmark digital training | 中〜高 | 中 | conditional | 対象者を限定したrehab/support |
| Route / rostering | 高い | 低〜中 | conditional | hard constraint check / coordination support |

## 7. 共通する「移植できる原則」

技術そのものより、次が繰り返し現れる。

### 1. pain-first
technologyを決めてから使途を探さない。

### 2. low-risk first
個人情報やcare decisionに直結しない領域から始める。

### 3. authoritative source
AIが参照する正本を定義する。

### 4. human review
高risk outputはdraftとして扱う。

### 5. feedback loop
質問log、誤り、利用頻度から改善する。

### 6. scale after evidence
pilot数を増やすのではなく、効果が確認できたものを横展開する。

### 7. non-AI baseline
FAQ、検索、workflow変更だけで解けるかを比較する。

---

## 8. Kaigo Opsへの反映

海外事例ページでは、製品紹介より次を表示する。

- solved pain
- setting
- intervention
- evidence class
- reported outcome
- independent verification
- implementation conditions
- failure / limitation
- Japan transferability
- smallest experiment
- checked_at

これにより「海外ではこんなAIがある」から、

> **この方法は日本のどの介護業務に、どの条件なら使えそうか**

へ情報価値を変える。
