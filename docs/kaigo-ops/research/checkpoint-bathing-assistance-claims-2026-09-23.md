# 入浴介助加算 RH2-007〜010 Claim review checkpoint

更新日: 2026-09-23 JST

## Fresh canonical state

- current main: `02147c9dcfe53c5702e47ddbc08a5326004db116`
- research branch before checkpoint: `8c7057d7c78b31443ed0d78d7285b2c9fb0e1bb4`
- PR: #51
- main vs research: diverged
- research ahead: 275
- research behind: 28

main側のsource/dataを正本として扱う方針は維持する。PR #51をそのままmergeしない。

## Review scope

national holdout の以下4件を独立reviewした。

- RH2-007: 入浴介助加算(I)の研修内容
- RH2-008: 入浴介助加算(II)のICTを用いた訪問・評価方法
- RH2-009: 入浴介助加算(II)の「居宅」の範囲
- RH2-010: 住宅改修に関する専門的知識及び経験を有する者

## Primary sources

- 厚生労働省「令和6年度介護報酬改定に関するQ&A（Vol.1）」問60〜63
  - https://www.mhlw.go.jp/content/001227740.pdf
- 厚生労働省告示第95号・十四の六「通所介護費等における入浴介助加算の基準」
  - https://www.mhlw.go.jp/web/t_doc?dataId=82ab4584&dataType=0
- 厚生労働省告示第19号「6 通所介護費」
  - https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- 厚生労働省「介護サービス関係Q&A」現行掲載ページ
  - https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/kaigo_koureisha/qa/index.html
- 厚生労働省「令和8年度介護報酬改定について」
  - https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000188411_00073.html

Q&Aの質問文だけではなく回答本文と告示本文を突合した。
令和8年度改定ページも確認し、この4論点を変更する後続資料は確認されなかった。

## Review result

4件をそれぞれatomic Claimとして `ANSWER / VERIFIED_CURRENT` へ昇格した。

### RH2-007 研修内容

問60では、以下が例示されている。

- 脱衣
- 洗髪
- 洗体
- 移乗
- 着衣
- 対象者に必要な入浴介助技術
- 転倒防止
- 入浴事故防止のためのリスク管理・安全管理

列挙は限定列挙ではない。
内部研修・外部研修を問わず、入浴介助技術向上のため継続的に研修機会を確保することも示されている。

告示第95号十四の六イ(2)は、入浴介助に関わる職員への研修等を要件としている。

### RH2-008 ICTを用いた評価

問61では、介護職員と医師等が画面を通して同時進行で評価・助言する必要はない。

医師等の指示の下、

- 利用者の動作: 動画
- 浴室環境: 写真

などを状況に応じて活用し、医師等が評価する方法でも要件を満たし得る。

告示第95号十四の六ロ(2)ただし書でも、医師等による訪問が困難な場合に、医師等の指示の下で介護職員が居宅を訪問し、情報通信機器等で把握した情報を踏まえて医師等が評価・助言できる。

### RH2-009 「居宅」の範囲

問62では、想定される居宅として、

- 利用者の自宅
- 高齢者住宅
  - 居室内浴室
  - 共同浴室
- 利用者の親族の自宅

が示されている。

自宅に浴室がない等の場合の5要件による別取扱いもQ&Aにあるが、これは「居宅」の定義を事業所浴室へ拡張するものとして扱わない。

### RH2-010 住宅改修の専門知識・経験を有する者

問63では、

- 福祉・住環境コーディネーター2級以上の者等

が想定される。

「等」であるため、この資格だけに限定されるとは扱わない。
また、告示第95号が明示する医師、理学療法士、作業療法士、介護福祉士、介護支援専門員、福祉用具専門相談員、機能訓練指導員、地域包括支援センター職員等の評価者範囲を置き換えない。

## Implementation

- Claim Registry: `claims-v0.23.json`
  - 55 → **59 claims**
- 追加:
  - `claim.remuneration.bathing-assistance.training-content`
  - `claim.remuneration.bathing-assistance.ict-asynchronous-evaluation`
  - `claim.remuneration.bathing-assistance.home-scope`
  - `claim.remuneration.bathing-assistance.home-modification-expert`
- Classifier: `research-coverage-classifier-v0.31.mjs`
- Claim Registry validator: `research-claim-registry-validate-v0.23.mjs`
- Claim Composition validator: `research-claim-compositions-validate-v0.10.mjs`
- Claim promotion benchmark: `claim-promotion-benchmark-v0.3.json`
  - 8 → **12 cases**
- national remuneration holdout:
  - ANSWER: **10**
  - REVIEW_REQUIRED: **10**
- remuneration review queue:
  - individual-functional-training = COMPLETE
  - bathing-assistance = COMPLETE
  - next priority = transport-reduction

広い `review.remuneration.base-and-addons` は引き続き `REVIEW_REQUIRED`。
入浴介助加算をumbrella Claimのrouting対象から除外し、明示的なatomic Claimだけでanswerabilityを開く。

## CI

run #34
- run id: `35833886699`
- conclusion: **SUCCESS**
- classifier v0.31: **201 / 201 PASS**
- Claim Registry: **59 claims / valid**
- Claim Composition validator: valid
- unit-price review validator: valid
- remuneration base review validator: valid
- remuneration delegated review validator: valid
- fee-guidance reconstruction sync: valid
- fee-guidance human review: valid
- deterministic fee-guidance regeneration: PASS

Run:
https://github.com/Josh-Temple/kaigo-rules/actions/runs/35833886699

## Remaining boundary

- broad remuneration answerability gate: CLOSED
- remaining national remuneration holdout: **10 REVIEW_REQUIRED**
- RAG: HOLD

次は `remuneration.transport-reduction` の RH2-012〜014 を優先する。
