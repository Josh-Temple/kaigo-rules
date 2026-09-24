# First Deep Issue — 必要な情報を探すのに時間がかかる

調査開始: 2026-09-22  
状態: Discovery / evidence review v0.2

## 1. Issue definition

介護現場の「情報探索」には少なくとも二種類ある。

### Type A — codified knowledge retrieval

- 法令・基準
- 通知
- Q&A
- manual
- policy / procedure
- 製品・補助制度情報
- 事業所内FAQ

これはsourceを限定しやすく、ordinary search、taxonomy、RAG等で比較しやすい。

### Type B — person-specific care information

- 現在の状態
- 生活歴
- 家族関係
- care goals
- QoL
- sensitive information
- 他施設・病院からのhandoff

これは「検索」の問題だけではない。

capture、記録粒度、standardization、timeliness、privacy、相互理解が関係する。[I14]

**最初のbenchmarkはType Aに限定する。**

---

## 2. Evidenceから見える問題構造

### H1: 問題の中心は検索性能だけでなく、情報アーキテクチャとworkflow fragmentation

CanadaのLTC施設研究では、personal notes、facility forms、care plans、medication records、reporting software、books、人への問い合わせなど多数のinformation spacesが併存し、全siteで一定の紙運用が残っていた。[I01]

日本でも、2025年度の全国調査で介護記録software利用回答者3,670件の**44.7%**が、記録から請求までに手入力転記が発生していると回答した。[I11]

したがって、

> 検索を速くする前に、正本・入力元・重複・連携を確認する

ことを標準手順にする。

### H2: digitizationだけでは時間削減を保証しない

Australiaのnursing home前後研究では、electronic documentation導入後にdocumentation timeが単純には減らず、hybrid paper/electronic workflowが負担を残した。[I02]

一方、日本の2025年度実証では、介護記録softwareとworkflow変更を合わせた後、

- 記録・文書: 43.1 → 30.4分 / 480分
- 転記: 21.5 → 8.2分 / 480分

となった。[I10]

対立ではなく、条件差と考える。

**一気通貫化・重複廃止・mobile access等まで含めたworkflow redesignが重要**という仮説が強まった。

### H3: 情報の「検索性」には実務価値がある

令和3年度ICT導入支援事業の導入事業所5,058件の自己申告では、

- 情報共有しやすくなった: 90.3%
- 過去文書の検索性向上: 72.4%
- 文書作成時間短縮: 81.9%

と報告された。[I12]

ただし補助事業参加者によるself-reportなので、独立した効果量として扱わない。

### H4: AI knowledge assistantは、低リスクauthoritative knowledgeから始めやすい

AustraliaのUnitingは、最初のGenAI use caseとして441件のpolicies/proceduresを対象にした。[I05]

- 自組織作成
- current versionを管理可能
- PIIなし
- security riskを限定
- scaleしやすい

という条件を持つ。

これは介護ルールと相性がよい。

### H5: 「詳しい人への問い合わせ」の一部を検索可能にする価値がある

Peterboroughの“Hey Geraldine”では、特定のexpertに集中していた質問をassistant化し、case report上では1,200超のtest questionsとOT conversationあたり15分の時間削減が報告されている。[I06]

ただしcontrolled independent evaluationではない。

このため、Kaigo Opsでは「成功事例」としてではなく、

> expert bottleneckをmeasurement可能なIssueへ変換した実装例

として扱う。

### H6: codified knowledgeとtacit knowledgeは分ける

care-home managersの研究では、研究Evidence以外にtacit knowledge・実践知・状況判断が重視される。[I03]

日本の2026 transitional-care研究でも、QoLやperson-specific情報にはstandardizationしにくいもの、記録しづらいsensitive informationがある。[I14]

したがってAI/RAGの最初の対象は、

- rules
- policies
- procedures
- manuals
- FAQs
- official guidance

に寄せる。

### H7: source qualityが悪ければRAGを足しても解決しない

2025年のLTC documentation systematic reviewや、residential-aged-care LLM評価は、documentation qualityやrobustness/context relevance自体が重要な問題であることを示す。[I18][I20]

RAG benchmarkではmodel qualityだけでなく、

- version
- currentness
- source coverage
- contradiction
- missing source

を試験対象にする。

---

## 3. 日本で特に見えた三つの分断

### 3.1 文書内の分断

同じ利用者・業務情報が複数文書に散る。

### 3.2 system間の分断

介護記録softwareを使っていても手入力転記が残る。[I11]

### 3.3 組織間の分断

病院と介護施設では必要な情報の重点が違い、標準化だけでは解けないhandoff gapがある。[I14]

この三つを同じ「検索問題」として扱わない。

---

## 4. 解決策の階層

### Level 0 — 不要情報・不要業務を減らす

- 重複文書廃止
- 古い版廃止
- 不要な転記廃止
- 不要な確認手順廃止

### Level 1 — 正本を決める

最低限:

- authoritative source
- owner
- version
- updated_at
- applicable_scope
- superseded_by

### Level 2 — ordinary retrievalを改善

- taxonomy
- tags
- full-text search
- task-oriented navigation
- structured FAQ
- source filters

ここで十分ならAIを足さない。

### Level 3 — source-grounded RAG

自然言語質問に対し、

- short answer
- source
- exact relevant section
- publication/update date
- scope
- uncertainty / no-answer

を返す。

### Level 4 — workflow integration

検索結果を業務へつなぐ。

例:
- checklist
- form
- opening procedure
- training
- change alert

### Level 5 — personal / clinical information

care plan、case note、利用者情報。

別risk class。

human review、privacy、retention、access control、consent/objection等を前提にする。

NewcastleのMagic Notes透明性記録では、AIはdraft transcript/summaryを作るだけで、practitionerによるreviewを必須とし、自動判断を行わない設計になっている。[I17]

---

## 5. このIssueに対するKaigo Rulesの役割

既存「介護ルール」は、

> authoritative knowledge retrievalを検証するtestbed

として使える。

強み:

- public source
- provenance
- 法令・告示・Q&A
- 人間が正誤判定しやすい
- 個人情報を使わずに実験できる

ここでordinary search vs RAGを比較し、RAGが勝たなければ無理に入れない。

---

## 6. Kaigo Ops自体が解ける情報ペイン

2026年の愛知県LTC施設調査[I09]:

- 導入施設でも利用可能な機器の情報不足: 55.2%
- 未導入施設でも情報不足: 55.7%
- 未導入施設の費用制約: 91.1%
- 費用対効果への懸念: 62.1%

つまり利用者は、

> 「どんなtechnologyがあり、どの条件なら意味があるのか」

を探すこと自体に困っている。

Kaigo Opsの世界事例・Evidence・日本への適用条件DBは、その問題へ直接価値を出せる可能性がある。

---

## 7. 現時点で言えること

- LTCの情報は複数媒体・複数systemに分散しやすい。[I01][I11]
- digitizationだけではworkload reductionは保証されない。[I02]
- workflow redesignと一体になった日本の公的実証では、記録・転記時間減少が観測されている。[I10]
- 導入事業所は検索性・情報共有改善を多く自己申告している。[I12]
- training/support/interoperabilityが重要な導入条件である。[I04][I12][I15][I16]
- low-risk authoritative knowledgeはGenAIの初期use caseとして実装されている。[I05]
- personal care informationには検索性以外の構造問題がある。[I14]

## 8. まだ言えないこと

- RAGが日本の介護ルール検索でordinary searchより優れるか
- 何分の短縮になるか
- hallucination / stale answerを実務許容水準まで抑えられるか
- small providerでの費用対効果
- 長期使用時の効果維持
- knowledge assistantの効果がcare qualityへ波及するか

---

## 9. 次の実証

[experiment-plan.md](./experiment-plan.md) に従い、

1. 介護ルールDB coverage audit
2. benchmark 30〜50問
3. navigation / full-text / structured FAQ / RAG比較
4. unsupported answer / stale source / conflicting source / no-answer試験
5. human correction effort測定

を行う。

## Sources

詳細は [evidence-register.csv](./evidence-register.csv)。
