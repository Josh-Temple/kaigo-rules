# 世界の介護DX・AI活用 — Initial Landscape

調査日: 2026-09-22  
状態: First-pass landscape / 継続調査前提  
対象: Long-term care, aged care, elder care, home care, adult social care

> この文書は「何を推奨するか」を決める最終レビューではなく、世界の介護DX・AI活用を分類し、次の深掘り対象を決めるための初回ランドスケープである。

## 1. 初回調査から見えたこと

### 1.1 介護DXの中心は「ロボット」だけではない

各国の政策・実装を見ると、実際の介護DXは次のような広い層で進んでいる。

- 電子記録・データ連携
- センサー・見守り
- 遠隔支援・virtual care
- 記録・要約・情報検索
- シフト・ルート最適化
- 狭い用途のAI評価・予測
- ロボット・支援機器
- 利用者・家族とのデジタル接点
- 行政・請求・バックオフィス自動化

WHOのLTC実装ガイドでも、LTCにおける技術を電子記録、telehealth/telecare、decision support、electronic monitoring、robotics、smart-home等に分けて把握する枠組みが示されている。[S02]

日本でも2025年4月以降の「介護テクノロジー利用の重点分野」は9分野16項目に拡張され、移乗・排泄・見守りだけでなく、機能訓練、食事・栄養、認知症ケア、介護業務支援などまで対象になっている。[S05][S06]

### 1.2 「AIが新しい」ことと「実用価値が高い」ことは別

デンマークでは、自治体がすでに価値を認めているものとして、video visit、digital training、intelligent sensors、RPAなどが挙げられ、2026年にはdata-driven rosteringのスケール支援も始まっている。[S17][S18]

Englandの2025 adult social care provider technology surveyでは、care technologyとしてsensor monitoringが43%で最も一般的だった一方、27%はcare deliveryに使うtechnologyを一つも利用していないと回答した。業務管理ではdigital social care recordsとdigital rosteringが一般的だった。[S08]

このため、サイトでは「最新AI」の新規性より、

- すでに運用されているか
- 何の業務を変えたか
- 効果を測れているか
- 導入条件が分かっているか

を重視する方がよい。

### 1.3 導入事例の多さと、独立した効果Evidenceの厚さには差がある

2022年のAI-enhanced interventions in LTCのsystematic reviewでは31論文が対象となり、social robots、environmental sensors、wearablesが中心だったが、有効性はmixedだった。[S22]

2026年のnursing homesにおけるAI rapid reviewでは28研究が整理され、clinical management、risk prediction、monitoring、wound management、nutrition、staffing/operationsなど対象領域は広がっている。[S23]

一方、fall technologyだけを見ても、
- 2025年のsmart-home systematic review/meta-analysisでは13研究・1,941人を対象にfall incidence低下（RR 0.72, 95% CI 0.57–0.93）が報告された。[S24]
- 別の2025年systematic reviewでは、institutional settingsのdetection systemsは監視を改善してもfall incidenceやinjurious fallsを一貫して減らさず、false alarmや外部検証不足が課題とされた。[S25]

したがって「センサーで転倒対策ができる」という一文にまとめるのではなく、検知・予測・予防を分けて扱う必要がある。

### 1.4 GenAIは「低リスクの情報検索・記録支援」から実装が進み始めている

AustraliaのUnitingは、組織内のpain pointを集め、最初のGenAI use caseとして441件のpolicies and proceduresを対象にしたdigital assistantを選んだ。理由として、自組織が作成した最新データであり、PIIを含まず、低リスクでスケールしやすいことを挙げている。[S15]

同事例では、その後point-of-careでの情報取得、incident reporting、care plan access、将来的なcase note作成を想定しているが、PII/PHIを扱うclinical integrationはsecurity controlsとdata classificationを前提に段階的に進めている。[S15]

EnglandでもAdult Social Careにおいて、
- Kingston: AIによるcase notes / assessments支援。[S09]
- Bradford等: information/signposting向けAI digital assistant。[S10]
- St Helens: Technology Enabled Care選定・care planningへのAI活用。[S11]

などが公開されている。

ただし、これらは主として自治体・事業者による運用報告であり、独立した比較試験とは分けて扱う。

### 1.5 「AI導入」より、データ・権限・運用設計が先に来る

AustraliaのAged Care Data and Digital Strategyは、provider-government間のdata sharing自動化、digital maturity、reference architecture、AI等の安全なpilotを一体で扱っている。[S12]

Uniting事例でも、
- 正本データの限定
- PII/PHIの切り分け
- role-based access
- security controls
- staff feedback
- board/executive governance

が先行条件として扱われている。[S15]

2026年のLTC nursing staffのtechnology acceptance reviewでも、digital competence、perceived usefulness、training、leadership/organizational supportが主要なadoption determinantとして整理されている。ただし対象研究は少なく、evidence gap自体が大きい。[S27]

### 1.6 狭い用途に限定したAIは、比較的評価しやすい

Australiaでは、認知機能低下がある高齢者のpain assessmentにfacial analysisを組み込んだPainChek等が実運用・研究対象になっている。[S28]

この種のnarrow AIは、
- 入力
- 出力
- 評価尺度
- 対象者

を限定しやすいため、汎用GenAIより効果検証しやすい。

一方で、関連研究には製品開発者・株主が含まれるものもあるため、利益相反と独立検証の有無を必ず記録する。[S28]

### 1.7 日本は「実証→Evidence蓄積→政策」の経路が比較的明示されている

厚生労働省は介護テクノロジーによる生産性向上について継続的に実証・効果測定を行い、2026年度も、care qualityとstaff burden reduction等の観点からEvidenceを収集して施策検討につなげるとしている。[S04][S07]

これは本プロジェクトにとって重要である。

海外事例だけでなく、日本の公的実証結果を継続的に取り込むことで、

```text
海外での先行実装
      +
学術Evidence
      +
日本の公的実証
      +
国内事業者事例
      ↓
日本の介護現場への適用条件
```

という形で整理できる。

---

## 2. Initial Landscape

以下の「成熟度」はStudio Labによる暫定的な実装成熟度の見立てであり、医学的Evidenceの強さを示すスコアではない。

| 領域 | 世界で見られる用途 | 暫定成熟度 | Evidenceの状態 | 日本への移植論点 | Source |
|---|---|---|---|---|---|
| 電子記録・データ連携 | digital care records, EHR, API, interoperability | Scaling / Established | 導入は広いがoutcomeは文脈依存 | 既存介護ソフト、LIFE、標準化、二重入力 | S08, S12, S21 |
| 情報検索・knowledge management | policies/procedures検索、職員向けassistant | Emerging → Scaling | LTC固有の独立研究は薄い。運用事例は増加 | 正本管理、更新責任、権限、PII切り分け | S10, S15 |
| 記録・要約 | speech-to-text, case note, assessment summary | Emerging → Scaling | 時間削減の運用報告あり。独立評価は今後 | 個人情報、誤要約、最終確認責任 | S09, S15 |
| 見守り・転倒 | sensors, cameras, radar, wearables, prediction | Scaling | 効果はmixed。検知と予防を分ける必要 | privacy、alarm fatigue、夜間運用、費用 | S08, S24, S25 |
| Virtual care | virtual nursing, video visits, telecare | Scaling | 比較的長い実装歴。一部で新規独立評価進行 | 人員基準との関係、遠隔で代替できる範囲 | S14, S17 |
| シフト・ルート最適化 | algorithmic rostering, route planning | Emerging → Scaling | 運用価値が期待されるがLTC固有比較研究は限定 | 労基・配置基準、資格、希望、利用者継続性 | S17, S18 |
| Narrow AI clinical support | pain assessment, risk prediction, deterioration | Emerging / task-dependent | 狭い用途では検証例あり | 医療機器該当性、責任分界、外部検証 | S23, S28 |
| Social / companion robots | dementia support, interaction, engagement | Research-heavy | 研究多数だが効果mixed | 費用、受容性、本人意思、代替ではなく補完 | S22, S26 |
| Physical / rehab robotics | transfer, rehab, mobility assistance | Task-dependent scaling | rehabは比較的成熟、一般LTCは用途差大 | 機器費、スペース、訓練、事故時責任 | S05, S20 |
| Care planning / decision support | assessment synthesis, TEC selection, reablement planning | Experimental → Emerging | pilot・自治体事例中心 | 生成結果の検証、制度判断との分離 | S11, S13 |
| Training / AR / VR | staff training, assistive-tech education | Experimental → Emerging | implementation evidenceはまだ限定 | 教育時間、端末、現場定着 | S13 |
| Family / citizen digital front door | signposting, chatbot, portal, remote support | Scaling in some systems | access改善の事例あり、equity課題 | 高齢者のdigital divide、個人情報 | S10, S19 |

---

## 3. Country / Region snapshots

### Japan

政策側で介護テクノロジーの重点分野を明示し、導入支援・実証・効果測定を継続している。[S04][S05][S06][S07]

特徴:
- 生産性向上を「職員負担軽減」だけでなくcare qualityと同時に評価しようとしている。
- 重点分野が公式に定義されている。
- 実証報告書・事例集が継続的に蓄積されている。

今後の深掘り:
- 令和7年度・8年度の効果測定報告書から、technology category別の定量成果を抽出する。
- 「導入した」ではなく、勤務時間、夜間訪室、記録時間、事故、ケア時間等のoutcomeを揃える。

### England

2025 provider surveyでtechnology adoptionの現在地を定量把握できる。[S08]

Adult Social CareではGenAIの実用事例が複数公開されている。[S09][S10][S11]

特徴:
- administrative burden削減
- citizen-facing information
- Technology Enabled Care
- governance / DPIA / privacy

が同時に扱われている。

### Australia

国としてAged Care Data and Digital Strategyを持ち、digital maturity、data exchange、AI pilot、virtual careを並行している。[S12][S13][S14]

UnitingのGenAI journeyは、本プロジェクトの「pain-first」に近い。[S15]

特に重要な実装原則:
- technology-firstにしない
- pain pointを先に集める
- low-risk use caseから始める
- authoritative dataを限定する
- feedback loopを入れる
- clinical data integrationは後段にする

### Denmark

「welfare technology」を高齢者ケアの持続可能性と結び付け、自治体間で成熟技術をscaleする仕組みがある。[S17]

2026 technology radarでは、digital training / video visits、intelligent sensor、RPA等が価値を生む技術として扱われている。[S18]

またdata-driven rosteringを自治体へ広げる取組が開始されている。[S17]

これは「単発pilotを並べる」のではなく、「成熟したものを横展開する」という観点で参考になる。

### Singapore

国のhealth/ageing政策では、community-based careとAI・roboticsを組み合わせる方向が明示されている。[S19]

community ageingではNANAなどのAI initiativeも進められている。[S20]

ただしhealthcareとlong-term care/community careの境界が日本と異なるため、事例ごとのsetting確認が必要。

### United States

NIAはArtificial Intelligence and Technology Collaboratoriesを通じ、wearables、home sensors、dementia care等のAI/technology研究基盤を支援している。[S21]

一方で、米国はsystem fragmentationが大きいため、「国全体のLTC導入率」と個別innovationを混同しない。

### Europe

EUでは以前からtelecare、smart-home、integrated health/social careを複数地域で実証してきた。[S03]

2026年のEuropean LTC overviewでも、technology-enabled optionsを含むcommunity-based/person-centred modelへの移行が確認されている。[S03]

---

## 4. Evidence gap map

### 4.1 実装は進むが、独立研究が追い付いていない

特に:
- GenAI documentation
- internal knowledge assistant
- AI front door
- AI care-plan drafting
- algorithmic rostering

は、運用事例が先行している。

ここは「成功事例一覧」ではなく、
- 誰の自己報告か
- baselineは何か
- time savingの測り方
- quality degradationはないか
- long-term adoptionは続いたか

を追跡する価値が高い。

### 4.2 技術性能とcare outcomeを混同しやすい

fall detectionでは、
- detection accuracy
- alarm speed
- actual fall reduction
- injurious fall reduction
- hospitalization
- staff workload

は別outcomeである。[S24][S25]

AI siteでは、このoutcome hierarchyを明示する。

### 4.3 staff acceptance / implementation scienceが薄い

2026 reviewでは、LTC nursing staffのdigital technology acceptanceに関する適格研究は少数だった。[S27]

しかし実装上は、
- training
- perceived usefulness
- leadership
- workflow fit
- digital competence

が重要とされる。

本サイトでは「製品性能」と同じくらい「導入条件」を扱う必要がある。

---

## 5. First deep Issueへの示唆

初回の深掘りIssueは、現時点でも

> **必要な情報を探すのに時間がかかる**

を第一候補とする。

理由:

1. 既存の「介護ルール」と直接接続できる。
2. 個人情報を扱わないlow-risk prototypeを作りやすい。
3. AustraliaのUnitingが、まさにpolicies and procedures searchを最初のGenAI use caseに選んでいる。[S15]
4. Englandでもcitizen-facing information assistantやinternal supportの実装がある。[S10]
5. clinical prediction等より、安全に効果測定しやすい。
6. 「AIなしの改善」と比較できる。
   - 検索改善
   - 文書体系整理
   - FAQ
   - taxonomy
   - navigation
   - RAG
7. 既存の介護ルールDBそのものを実験基盤として使える。

ただし現段階では、GenAI/RAGが介護現場の情報探索を改善するというLTC固有の独立Evidenceは十分とは言えない。

したがってFirst deep Issueでは、

```text
情報を探せない原因
  ↓
文書整理・検索改善だけで解ける部分
  ↓
RAG / AIで追加価値が出る部分
  ↓
誤回答・更新漏れ・権限問題
  ↓
介護ルールDBで小規模検証
```

まで扱う。

---

## 6. 次の調査

### A. 日本の効果測定を定量化する

- MHLW令和7年度効果測定報告書
- MHLW令和8年度実証
- パッケージ導入モデル
- 重点分野別普及率

からoutcomeを抽出する。

### B. GenAI / knowledge searchを深掘りする

対象:
- Uniting
- UK Adult Social Care AI cases
- aged care / nursing homeのRAG・policy search
- case note / voice documentation
- independent evaluation

### C. Denmarkの「scaleした技術」を確認する

pilotではなく、municipality-levelで横展開されている
- video visits
- digital rehabilitation
- sensors
- route planning
- rostering

の成果指標を確認する。

### D. Fall / monitoringは別Evidence Reviewにする

研究数が多く、結果も単純ではないため独立Issueとして扱う。

### E. Japan transferability frameworkを実例に当てる

Australia / England / Denmarkの各1事例に対して、
- regulation
- workforce
- data
- workflow
- cost
- vendor dependence
- privacy

を比較する。

---

## 7. 現時点の結論

初回調査だけでも、介護DX・AIを定期的に再調査して整理する価値は十分ありそうである。

理由は「新しい製品が毎月出る」ことではない。

むしろ、

- 実装が進んでいる領域
- 研究が追い付いていない領域
- 研究では有望だがscaleしていない領域
- 国によって普及条件が違う領域
- 前回の結論が変わった領域

を継続的に整理できることに価値がある。

公開サイトではニュースフローを追うのではなく、

> **世界の事例を定期的に再調査し、何が実用段階に入り、何がまだ実験段階なのかを更新する**

ことを中核価値の一つにする余地がある。

---

## Sources

Source IDの詳細は [source-register.csv](./source-register.csv) を参照。
