# First Deep Issue — 必要な情報を探すのに時間がかかる

調査開始: 2026-09-22  
状態: Discovery / initial evidence review

## 1. Issue definition

介護現場では「情報がない」だけでなく、

- 情報が複数の場所にある
- 最新版が分からない
- 同じ内容を紙とシステムの両方で管理する
- 制度情報と事業所内ルールが混在する
- 誰に聞けばよいかが属人化する
- 検索できても現場で使える答えに変換できない

ことで、探索・確認・転記・問い合わせに時間がかかる。

このIssueでは、単に「AI chatbotを導入すればよい」とは置かない。

## 2. 初期仮説

### H1: 問題の中心は検索エンジン性能ではなく、情報アーキテクチャとworkflow fragmentationである

CanadaのLTC施設を対象にした情報フロー研究では、RNがpersonal notes、facility forms、care plans、medication records、reporting software、books、人への問い合わせなど多数のinformation resources / spacesを併用していた。[I01]

紙と電子が混在し、同じ情報を複数の場所へ記録する状況も観察されている。[I01]

したがって、

> 「検索を速くする」だけではなく、「どの情報を正本にするか」「どこへ統合するか」を先に設計する必要がある

という仮説を置く。

### H2: デジタル化そのものは時間削減を保証しない

nursing homeでelectronic nursing documentation導入前後を比較した研究では、導入によってdocumentation timeが単純には減らず、6か月時点で増加し、12か月後に元の水準へ戻った。紙のdocumentationが残っていたことが一因として指摘された。[I02]

古い研究ではあるが、

> **paper → digitalへの置換だけでは、workflowが二重化すれば効果を失う**

という失敗パターンとして重要。

### H3: AI knowledge assistantは、低リスクのauthoritative knowledgeから始めると実装しやすい

AustraliaのUnitingは、pain pointを組織横断で収集し、最初のGenAI use caseとして441件のpolicies and proceduresを対象にした。[I05]

選定理由:
- 自組織が作成した情報
- 最新であることを確認できる
- PIIを含まない
- security riskを限定できる
- scaleしやすい

その後、point-of-careでのcare plan access、incident reporting、case-note supportへ広げる設計だが、PII/PHIを扱う領域はdata classificationとaccess controlを整えてから進めている。[I05]

この順番は日本の介護事業所にも移植可能性が高い。

### H4: 「詳しい人への問い合わせ」をAIで一部代替する用途は、実務価値が測りやすい

Peterborough City CouncilのAdult Social Careでは、特定職員Geraldineへの頻繁な問い合わせを背景に、AI assistant「Hey Geraldine」を構築した。[I06]

公開case reportでは:
- testing期間に1,200超の質問
- OT teamで1 conversationあたり15分の時間削減と報告
- backendから内容を更新可能
- query dataからknowledge gapを把握

とされている。[I06]

ただしLGA case studyによる運用報告であり、独立したcontrolled evaluationではない。

### H5: codified knowledgeとtacit knowledgeを分ける必要がある

care-home managersのknowledge useに関するqualitative studyでは、research evidenceだけでなく、tacit knowledge、実践知、状況判断が強く重視されていた。[I03]

よってAI/RAGで検索できるようにすべき対象は、

- rules
- policies
- procedures
- manuals
- FAQs
- product / equipment knowledge
- official guidance

などのcodified knowledgeを中心にする。

「経験豊富な職員の判断をすべてAIに置き換える」という設計は避ける。

## 3. 解決策の階層

このIssueは次の順番で解く。

### Level 0 — 情報を減らす

- 重複文書をなくす
- 古い版を廃止する
- 不要な手順を減らす

### Level 1 — 正本を決める

- authoritative source
- owner
- update date
- version
- applicable scope

を固定する。

### Level 2 — 普通の検索・navigationを改善する

- taxonomy
- tag
- full-text search
- service type filter
- task-oriented navigation
- FAQ

AIを使わなくても解決する部分を先に確認する。

### Level 3 — AI / RAGで自然言語アクセスを追加する

利用者の自然な質問からauthoritative sourceを検索し、

- 短い回答
- 根拠
- 原文該当箇所
- 更新日
- 適用範囲

を返す。

### Level 4 — personal / clinical dataを扱う

care plans、case notes、利用者個人情報等。

ここはLevel 0–3とは別のrisk classとして扱う。

## 4. 介護ルールとの接続

既存の「介護ルール」は、このIssueを検証するための非常に良い基盤になる。

理由:

- source provenanceを保持している
- 公開情報中心
- 法令・告示・Q&A等のauthoritative sourceを持てる
- 個人情報なしで検証できる
- 検索結果の正誤を人間が確認しやすい

つまり、介護ルールは単なる公開サイトではなく、

> **介護分野のauthoritative knowledge retrievalを検証するtestbed**

として使える。

## 5. サイトに載せると価値がありそうな内容

公開ページは「AI検索を導入しよう」という記事ではなく、

### 困りごと
必要な制度・手順・事業所内情報を探すのに時間がかかる。

### まず確認
- 情報源はいくつあるか
- 正本は決まっているか
- 更新者は決まっているか
- 同じ情報が重複していないか
- 問い合わせ先が一人に集中していないか

### 解決パターン
1. 整理
2. taxonomy / search
3. FAQ
4. RAG
5. workflow integration

### AIが向く条件
- sourceが限定できる
- 最新版を管理できる
- 参照元を表示できる
- 誤答時に原典確認へ戻れる
- 高リスク判断をAI単独で確定しない

### AIを入れる前に直す条件
- 文書が古い
- 正本が複数ある
- 誰も更新していない
- access permissionが不明
- 業務そのものが不要

という構造にする。

## 6. 日本での別の情報ペイン

2026年に公表された日本のLTC facility surveyでは、介護テクノロジー導入済み施設でも「利用可能な機器の情報不足」、未導入施設でも「情報不足」がbarrierとして報告されている。[I09]

これは現場内部のknowledge retrievalとは別の問題だが、

> **介護事業者が「使える技術・制度・補助・Evidence」を探しにくい**

という本サイト自体が解けるIssueを示している。

したがって「介護業務改善」サイトには将来的に、

- 困りごと
- 技術カテゴリ
- 国内外事例
- Evidence
- 導入条件
- 補助・制度

を横断して探せる価値がある。

## 7. 現時点で言えること / 言えないこと

### 言えそうなこと

- LTCのinformation flowは複数媒体・複数場所に分散しやすい。[I01]
- digitizationだけではworkload reductionが生じない場合がある。[I02]
- low-risk authoritative knowledgeを対象にAI assistantを始める実運用例がある。[I05]
- social careでknowledge assistantの時間削減を報告するcaseがある。[I06]
- successful adoptionにはtraining、usefulness、organizational support等が影響する。[I04]

### まだ言えないこと

- RAGが日本の介護現場で何分短縮するか
- ordinary searchよりGenAIが優れているか
- hallucinationを実務許容水準まで抑えられるか
- small providerでも費用対効果があるか
- 長期利用しても効果が維持されるか

これらは今後の検証対象。

## 8. 次の調査

1. LTC / aged careのknowledge assistant事例を追加探索する。
2. generative AI documentationとknowledge retrievalを分離してEvidenceを集める。
3. Japanの介護現場で「何を探すのに時間がかかるか」の公開調査を探す。
4. ordinary search vs RAGの比較研究を介護外も含めて確認する。
5. 介護ルールを使った小規模benchmarkを作る。

## Sources

詳細は [evidence-register.csv](./evidence-register.csv)。
