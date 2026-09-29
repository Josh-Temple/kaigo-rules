# Issue 02 — 記録・文書作成に時間がかかる

更新日: 2026-09-29  
状態: Evidence synthesis v0.1 / public page candidate

## 1. Issue

介護現場では、記録そのものだけでなく、

- 同じ内容の転記
- 複数様式への再入力
- 記録後の請求・報告へのつなぎ直し
- 過去記録の検索
- 紙と電子の併用
- 記録を作るための移動・待ち時間

が負担になり得る。

このIssueでは「文章生成AIを導入するか」ではなく、

> 必要な記録を保ちながら、重複入力・転記・待ち時間・確認負担をどこまで減らせるか

を扱う。

## 2. 現時点の結論

現時点のEvidenceからは、次の順序が妥当。

1. 不要な記録・重複入力を特定する
2. 正本と入力元を決める
3. 一度入力した情報を再利用できるようにする
4. 紙・FAX・別システム間の転記を減らす
5. そのうえで音声入力、要約、AI draftなどを検討する
6. AI出力を正式記録へ入れる場合は、人間の確認責任を残す

「AIで文章を速く作る」だけでは、転記や分断が残れば全体最適にならない。

## 3. 日本の主要Evidence

### 3.1 厚生労働省 令和7年度効果測定

Source:
厚生労働省「介護テクノロジー等による生産性向上の取組に関する調査及び効果測定事業 報告書 II/III」

URL:
https://www.mhlw.go.jp/content/12300000/001690572.pdf

訪問・通所系6事業所で、介護記録ソフト導入とオペレーション変更の前後を比較した小規模実証。

介護職員1人1日480分換算:

- 記録・文書作成: 43.1分 → 30.4分
- 転記: 21.5分 → 8.2分

ただし、

- 事前 n=43、事後② n=36
- randomized trialではない
- ソフト導入と同時に業務フローも変更
- 紙の複写廃止、mobile参照、直行直帰、記録→請求の一気通貫化などを含む

ため、観測差を「ソフト単体の因果効果」とは扱わない。

重要な示唆は、**技術導入とworkflow redesignを分けないこと**。

### 3.2 厚生労働省 令和7年度全国調査

Source:
「介護現場における生産性の向上等を通じた働きやすい職場環境づくりに資する調査研究事業一式」

URL:
https://www.mhlw.go.jp/content/12300000/001712213.pdf

介護記録ソフト利用回答者 n=3,670 のうち、

- 手入力による転記あり: 44.7%
- 転記なし: 44.0%
- 無回答: 11.3%

だった。

これは「記録が電子化されている」ことと「データ連携されている」ことが別であることを示す。

同調査では、導入後の運用課題として、

- PC・tablet等で記録することが困難な職員がいる: 44.2%
- トラブル時にPC/softwareの問題へ対応できる人材がいない: 34.4%

も報告されている。

### 3.3 ICT導入支援事業 令和3年度

Source:
厚生労働省「ICT導入支援事業 令和3年度 導入効果報告取りまとめ」

URL:
https://www.mhlw.go.jp/content/12300000/001124036.pdf

補助事業所5,371、効果報告5,058。

自己申告では、

- 文書作成時間が短くなった: 81.9%
- 入力済み情報の再利用: 84.8%
- 記録時間が削減: 78.7%
- 紙文書量が削減: 77.2%

が報告された。

一方、

- 記録・報告様式の見直し: 84.9%
- 情報共有方法の見直し: 87.7%
- 業務の明確化・役割分担見直し: 82.0%

も同時に行われている。

このため、ICT単体ではなく、業務見直しと一体の導入として読む。

## 4. 海外・研究Evidenceからの補助線

### Newcastle City Council — Magic Notes

Source:
GOV.UK Algorithmic Transparency Record

URL:
https://www.gov.uk/algorithmic-transparency-records/newcastle-city-council-magic-notes

Adult Social Careの会話を録音し、

- speech-to-text
- LLM summary
- practitioner review/edit
- case-management systemへ転記

する運用。

公開記録では、

- 自動意思決定をしない
- practitionerが全outputをreview
- access control
- retention
- personal / special category dataの取扱い
- staff training
- fallback

等を明示している。

ここで参考になるのはmodel名ではなく、

> AI outputをdraftとして扱い、正式記録と判断責任を人間へ残す

という運用設計。

### Long-term care documentation研究

既存の研究では、

- 電子記録化してもhybrid paper/electronic workflowが残る
- workflow fit、training、infrastructure、supportが実装成否に影響する
- resident documentationのdata quality自体が下流AIの前提になる

ことが示されている。

Kaigo Opsでは「AI精度」だけでなく、入力品質、workflow、運用責任を同じIssue内で扱う。

## 5. 改善パターン

### Pattern A — 記録を減らす

先に確認すること:

- 同じ情報を複数様式へ書いていないか
- 誰も使わない記録が残っていないか
- 制度上必要な記録と慣行上続いている記録を分けられるか
- 紙と電子の二重管理が残っていないか

制度上必要な記録要件はKaigo Rules側で確認する。

### Pattern B — 一度入力した情報を再利用する

- master data
- 利用者基本情報
- schedule
- service provision record
- billing
- report

の間で、再入力や転記がどこにあるかを可視化する。

### Pattern C — 記録する場所と時間を変える

- mobile入力
- point-of-care入力
- 直行直帰
- offline対応
- voice input

などで、事務所へ戻るためだけの時間や後追い記録を減らせるかを見る。

### Pattern D — AIはdraft作成に限定して試す

AIを使う場合は、まず

- 非個人情報の定型文
- 会議メモ
- internal draft
- structured dataからの文章化

等の低リスク用途から始める。

個人情報・要配慮個人情報を含む正式な介護記録では、

- access
- retention
- vendor / subprocessor
- human review
- correction
- fallback
- 説明・同意が必要な場面

を別途確認する。

## 6. AIを使わない選択肢

- 様式統合
- checkbox / structured form
- template
- master data再利用
- shortcut / dictation
- system連携
- paper廃止
- 入力タイミング変更
- 役割分担見直し

普通のICT・workflow改善で十分なら、生成AIを追加しない。

## 7. 小さな実験

1週間、記録関連作業を次の4分類で測る。

1. 本当に必要な記録
2. 転記・再入力
3. 探す・確認する時間
4. 後から思い出して書く時間

その後、最も大きい一つだけを選び、

- 様式統合
- data reuse
- mobile入力
- voice input
- AI draft

のどれが最小変更で効くかを比較する。

AIあり / なしを同じ指標で比較する。

## 8. 現時点で言わないこと

現時点では次を一般化しない。

- 介護記録ソフトを入れれば30%時間短縮できる
- AIなら記録時間を大幅に減らせる
- 音声要約を使えば記録品質が上がる
- 生成AIの方が通常入力より費用対効果が高い

公開されている数値は、調査設計、対象、workflow変更、self-report等の条件付きで示す。

## 9. 次に確認すること

- 日本の介護現場でのGenAI documentationの独立評価
- voice inputとLLM summaryを分けた効果
- error correctionにかかる時間
- 記録品質への影響
- 個人情報を含む運用時の実装条件
- 小規模事業所での費用対効果
- どのサービス種別で転記負担が大きいか

## 10. 公開ページへの要約

公開ページでは、

1. 結論
2. 日本のEvidence
3. 改善の順序
4. AIを使う場合 / 使わない場合
5. 小さな実験
6. Safety boundary
7. 分かっていないこと
8. 出典

に圧縮する。
