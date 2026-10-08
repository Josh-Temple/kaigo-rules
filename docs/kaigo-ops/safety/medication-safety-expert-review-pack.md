# 誤薬・与薬漏れ：専門職レビュー用資料（Worker D）

作成日: 2026-10-08 JST  
状態: **REVIEW_PACK_READY / EXPERT_REVIEW_NOT_DONE / NOT_PUBLIC**  
目的: 「服薬業務の安全点検シート」の設計・草案を、介護・医療・リスク管理の実務者が独立審査できるようにする。**本資料の作成は、依頼・審査・承認が完了したことを意味しない。**

## 1. レビュー対象を固定する

| 対象 | 確認済みの版・所在 | 注記 |
| --- | --- | --- |
| 基準main | `d5e5b5f1c3a019c801c81c1af737964183bf7ce4` | A/B/旧D/Eの資料まで統合、Cのコードは含まない |
| A claim register | `docs/kaigo-ops/safety/medication-safety-source-register.md` | MS-01〜20。特にMS-07/13/14/15/17〜20の留保を確認 |
| B draft | `docs/kaigo-ops/safety/medication-safety-issue-draft.md` | MHLW-01〜07、サービス別適用表を含む草案 |
| C 試作 | [draft PR #451](https://github.com/Josh-Temple/kaigo-rules/pull/451)、`dd7ccdc535aa34acd76d8d54943a72b856345832` | 本番未公開。実装変更があれば版を更新して再審査 |
| C UI | `ops-site/app/tools/medication-safety-preview/page.tsx` / `worksheet.tsx`（#451 head） | エラーメッセージ、結果、印刷用DOMも対象 |
| C 判定関数 | `ops-site/lib/medication-safety-review.ts`（#451 head） | 選択状態の全組合せ・不正値の挙動 |
| Dの独立検証 | `medication-safety-test-results.md` の「2026-10-08 新Wave追補」 | 静的確認、実HTTP、動的未実施を分ける |
| Aの段落trace / Bの新版 / Cの実測台帳 | 現時点のmainで **NOT_ESTABLISHED** | 追加された場合、差分と対象SHAを再固定する |

公式一次資料: 厚生労働省、[令和7年11月「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」Vol.1436](https://www.mhlw.go.jp/content/001591418.pdf)、冊子p38〜39（PDFゼロ起算p40〜41）、および[事故報告様式等Vol.1332](https://www.mhlw.go.jp/content/001574219.pdf)。ガイドラインの推奨・掲載事例・通知・法令義務を区別する。サービスと職種ごとの適用範囲は未確立のまま扱う。

**配布範囲**: 非識別の草案・コード・チェック表のみ。実在利用者・職員・事故、薬剤、処方、個人用アクセスリンク・認証情報・HARを送らない。レビュー用の実画面を使う際はローカルまたは認証を実証した制限環境のみとする。

## 2. 先に読んでもらう説明

> この試作は、服薬業務の工程（手順、役割、中断、変更情報、相談先、振り返り）を非識別の選択肢で整理する補助です。投薬の可否、処方、再投与、症状・緊急度、事故報告要否を判断しません。実際に事故・疑義が生じた場合は所属先の正式な事故対応手順、管理者と関係する医療専門職、必要な緊急対応を優先してください。厚労省のガイドラインは施設サービスを主に対象としており、訪問・通所・居住系に同じ服薬手順を適用できるとの確認はありません。

## 3. Gate別のレビュー依頼事項

### EX01：薬剤師・看護職等の適切な医療職（必要に応じ医師）

- 「配薬」「服薬確認」「指示変更」の語から、誰にどの医療行為・確認行為が認められると誤読されるか。サービス別・職種別で意図せず業務権限を示唆していないか。
- 「確認できる（自己申告）」「対象外（要確認）」が、投薬の正確さ、安全性、監査合格と受け取られないか。
- 服薬漏れ・誤薬・拒否が発生した場合、シートが再投与・中止・受診要否・報告要否などの判断へ誘導しないか。固定の事故時案内は過不足ないか。
- 配薬後の確認工程の表現は、ガイドラインp38の推奨を越えた個別手技の指導になっていないか（MS-07）。
- 利用者の意思・尊厳を尊重しつつ、個別医療判断に介入しない説明になっているか。
- 事故例、薬剤、処方、症状、利用者属性、具体的な現場データを**試作へ入力しなくても**内容審査できるか。

### EX02：介護事故防止・リスク管理の実務責任者

- 6つの点検項目は、現実の人員・兼務・中断・引き継ぎ・変更連絡に照らして実行可能な業務点検か。追加負担・作業停滞や責任の曖昧さを招かないか。
- ダブルチェック、専任配置、施設事例を一律の法的義務や唯一の対策として誤認させないか。
- 介護保険施設、短期入所、居住系、通所、訪問、居宅介護支援等のそれぞれについて、服薬業務の有無・役割・指示経路の確認が必要な箇所はどこか。
- 事故発生時はサイトの点検を中止し、正式手順に移れるか。自治体報告の方法・要否・期限を本ツールが決めていないか。
- チームと管理者の責任、再評価、本人・家族との関係を適切に扱い、職員個人の「不注意」だけへ原因を帰属させていないか。
- シート結果を正式記録、医療判断、事故報告、個人評価の代替として使う危険がないか。

### HU01：内容・公開の責任者（**EX01・EX02とは別の承認**）

- 審査した対象commit・資料版、未解決指摘、対象サービス範囲、問い合わせ・訂正・更新担当が記録されているか。
- R01〜R16、P01〜P07、U01〜U06の**独立動的試験**と必要な再試験が成立しているか。
- 本番で有効化してよいroute、公開文言、登録・検索対象、Analyticsの回答情報非送信について明示的な決定を出せるか。
- `GO`が出なければ公開登録、flag有効化、production deploymentをしない。

## 4. レビューの記録欄（匿名・空欄を維持）

公開リポジトリには氏名、所属、署名、メールアドレス、実際の症例を保存しない。関係者との本人確認や資格確認は別の適切な経路で行う。以下は**未記入テンプレート**であり、未記入を承認と解釈しない。

| 欄 | EX01 | EX02 | HU01 |
| --- | --- | --- | --- |
| 必要な役割 | 医療・服薬安全の適任専門職 | 介護事故防止・リスク管理実務責任者 | 内容・公開責任者 |
| 匿名review / approval ID | 未付与 | 未付与 | 未付与 |
| 対象C commit SHA | 未記録 | 未記録 | 未記録 |
| 対象A/B文書版・取得日 | 未記録 | 未記録 | 未記録 |
| 原典の版・該当ページ | 未記録 | 未記録 | 未記録 |
| 確認日（JST） | 未記録 | 未記録 | 未記録 |
| 指摘ID／対象文・画面 | 未記録 | 未記録 | 未記録 |
| 重大度と処理内容 | 未記録 | 未記録 | 未記録 |
| 修正commit／再確認日 | 未記録 | 未記録 | 未記録 |
| 明示的結果 | `EXPERT_REVIEW_NOT_DONE` | `EXPERT_REVIEW_NOT_DONE` | `HUMAN_APPROVAL_NOT_DONE` |

判定を記録する場合は、少なくとも `review ID / role / document versions / tool SHA / date / findings / fix refs / recheck / decision` を満たす。異議や未解決項目が1件でもあれば、それを消さずにHOLDとする。審査後に実装・文面が意味上変更された場合は、変更範囲と再確認の要否を明記する。

## 5. レビュアー向け具体的確認シナリオ（架空のみ）

1. 配薬準備と配薬の担当が分かれ、途中で別業務への対応が入る。責任者が工程・中断・申し送りを整理する際、シートの問いは適切か。
2. 与薬漏れの疑義が生じた。シートで服薬可否や事故報告を判断できると思い込ませる文言はないか。
3. 訪問系サービスで1人の職員が対応する。施設事例の人数・職種の確認を、法的義務や実施可能な手順として誤読しないか。
4. 服薬に本人の拒否がある。シートが個別対応の正解や強制を指示しないか。
5. 全項目「確認できる」を選ぶ。結果・印刷物が安心証明や法令適合の証明になっていないか。
6. 項目すべて「対象外」を選ぶ。理由や正式手順の確認なしに「終了」と受け取らないか。

上記の状況設定に実際の事故記録や薬剤情報を追加して提出しない。審査者に伝える必要がある場合も、必要最小限の抽象化した論点に限定する。

## 6. 現在の阻害条件・引き渡し

- **未実施**：EX01、EX02、HU01。専門職へ連絡した事実や審査実績を作らない。
- **未実施**：R/P/Uのflag-enabled実ブラウザ独立検証、Network payload・Storage・200%・印刷プレビュー、認証済みレビュー環境の検証。静的検査とCIの結果を代わりにしない。
- **未確定**：Aの段落単位のclaim trace、Bの独立したサービス適用資料、Cの実測台帳との対象版一致。無断でサービス適用を拡大しない。
- **確認済み限定事項**：2026-10-08の独立した静的監査と本番HTTPでは、公開登録に誤薬試作の追加はなく、本番試作routeは404、既存11ページは200。これは本番公開を承認する証拠ではない。

Dの安全判定: **`SAFETY_PARTIAL_WITH_GAPS`**。公開判定はEの権限であり、現時点の推奨は **`PREVIEW_ONLY / NOT_PUBLIC`**。次はA/Bのtrace・Cの固定SHAとアクセス制限付き実行証拠を受けてDが再検証し、人間のレビュー後にEが公開可否を再判定する。


---

## 7. 2026-10-08 independent validation handoff — authoritative review snapshot

This section updates the older §1/§6 snapshots; those remain historical. **REVIEW_PACK_READY is not expert approval.** Reviewed code is still an **unmerged draft**, and materials remain **NOT_PUBLIC**.

| Item | Fixed review version / evidence |
| --- | --- |
| Main at D audit | 233f11f60bd53cee4684fd66eb5c0490b2fee926 |
| A trace | 2cb32c3b4de093d51d410d23c04511e020a43571 (maps old B paragraphs; current mapping P0 incomplete) |
| B Issue B-00..B-13 | 083ffd0a17419e1533e65205e9230d725f3232ab |
| B service matrix | 8138d89832ddd4b706ff1da4751ffd2626e251bb |
| C preview UI/model/print | [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) pinned a1357ad7ebd723c5a8c8fcf754c04b384f7db95d |
| D independent browser report | [#457](https://github.com/Josh-Temple/kaigo-rules/pull/457), [CI run 37782952341](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37782952341), 13 D-only browser tests PASS; absent/invalid flag 404 and existing routes PASS in localhost |
| Official source | MHLW Vol.1436 guideline printed p38, p39 and p46 (PDF zero-index 40/41/48), 2025-11-07; Vol.1332 notice PDF zero-index p2, 2024-11-29; reopened 2026-10-08 JST |
| Current D decision | SAFETY_PARTIAL_WITH_GAPS / PREVIEW_ONLY / NOT_PUBLIC |
| Actual medical/safety reviewer | EX01 / EX02 = EXPERT_REVIEW_NOT_DONE |
| Content owner public approval | HU01 = HUMAN_APPROVAL_NOT_DONE |

### High-priority human review questions before any external invitation

**EX01 (appropriate pharmacist / nurse, and doctor if needed)**:
1. Compare B-00..B-13 and the pinned C initial/result/print copy. Does any phrase sound like a decision to re-administer, withhold, independently verify medication correctness or grant a worker a clinical scope of practice?
2. Do C old labels, especially 「確認できる（自己申告）」「対象外（要確認）」, convey false assurance? Is the proposed B replacement more appropriate for facility vs day/visit/residential services?
3. Are p38 recommendations or p39 one-facility example overstated as a universal method? Is the real accident/doubt warning unambiguous, while respecting the person's wishes?

**EX02 (care safety / operational risk owner)**:
1. Can the six fields be used without adding unsafe workload, unworkable staffing, interruptions or blame? Distinguish facility workflow from visit/day/residential and care-management settings.
2. Is treating all six checks as self-report rather than a safety/compliance score clear in result and printed output? Should any stage or choice be withdrawn pending service-specific evidence?
3. Are incident-report responsibilities and communication boundaries clear without deciding reportability/deadlines for individual cases?

**HU01 (authorized owner, only after actual EX01/EX02)**:
1. Approve a **named new C SHA and exact B/A blobs**, target service scope, page copy, technical environment and remaining documented risks, or explicitly HOLD.
2. Require native browser zoom, Android, actual screen reader, print preview, production URL/preview access verification and D re-run against changed C SHA.
3. Record owner for corrections/updates and do not make publication/feature-flag changes without a separate explicit GO.

### Outstanding blockers and safe handoff order

1. **A + B + C:** produce exact current text/claim/choice crosswalk, update C language and print output on C's own branch, fix source/service scope gaps without inventing a universal protocol.
2. **D:** pin revised SHA and repeat dynamic tests. Existing successful run is valid **only for a1357ad...** and measured local conditions.
3. **Human EX01 / EX02:** external contact and review are **NOT_REQUESTED / NOT_DONE**; no mails, invites or approvals were sent. Use anonymous review IDs in public records and keep identities outside the public repository.
4. **HU01:** human public-approval decision **NOT_DONE**. E must retain **NOT_PUBLIC** until all technical and human gates are satisfied.

All previous blank review-ID/date/decision fields remain blank. The test-results §9 tables provide R01–R16/P01–P07/U01–U06 case evidence, scope, limitations and retest conditions. No individual patient, actual accident, medicine or prescription details are included.


---

## 8. 2026-10-09 最終版の専門職審査に向けた非公開pack（履歴を保持）

**状態**：`REVIEW_PACK_READY`（版付き質問票を準備したことのみ）/ `REVIEW_REQUESTED=false` / `EX01=EXPERT_REVIEW_NOT_DONE` / `EX02=EXPERT_REVIEW_NOT_DONE` / `HU01=HUMAN_APPROVAL_NOT_DONE` / `NOT_PUBLIC`。レビュー実施者・署名・承認結果は存在しないため記録しない。

### 8.1 審査対象の版台帳と資料

| 対象 | 固定参照・再確認方法 | 現状態 |
| --- | --- | --- |
| 公式資料 | 厚労省介護保険最新情報Vol.1436（2025-11-07）冊子38/39/46頁・PDFゼロ起算40/41/48頁、Vol.1332（2024-11-29）PDFゼロ起算p2。一次資料と通知/推奨/一事例/法令義務を分離 | D限定再閲覧。全サービス実施権限はNOT_ESTABLISHED |
| main / E前回 | `1360bd78d971266c5e635c7a3416d5b4629e1c0e`、2026-10-08 content alignment decision | 前回HOLD、docsのみ |
| B Issue / service | PR #459 head `364519815a41143560b068cfa459e7a04962f18f`; Issue blob `e0cc354e2b78a28912c80c0611ccf3c165d00b25`、service blob `e3889c26c5b46d4644b29d94c657e628c96206d3` | B案固定。サービス・専門職権限はREVIEW_REQUIRED |
| A trace | PR #458 head `cbdaddd843db2d1b193b34738272c538086039d1`、blob `0b042421f49ae5213f80b71e4cf04c502d32c1f9` | **旧Bへの独立trace**。最終B blobの認証ではない |
| C candidate | draft PR #451 `7ec2fe8c644d0526af1650e857a7da397488a0ad`; page blob `cfa6f30633c5c8536b570c4c82b2794cd4353320`; worksheet blob `2ecd0475681f5a822da0f3dbe32c4610a041d47c`; model blob `9580e9202209f5e3fdf3b544b628d68885062295` | Draft / unmerged、localhost以外のflag-enabledを使わない |
| D独立CI | [PR #457](https://github.com/Josh-Temple/kaigo-rules/pull/457) / [CI #37844281038](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37844281038)（新C target）。旧CI #37782952341は旧C版のみ | [29ケース台帳 §10](./medication-safety-test-results.md)、限定測定結果とNOT_RUNを区別 |
| production / exposure | Vercel `kaigo-ops` `dpl_Ae1BwiQChp3CfmK1izUcNQH8wL8S` READY、runtime `e49e770a970e541d2ad95204ad277eca89a485d3`、alias `ops-site-pi.vercel.app` | C branch deployment 0件観測、preview access restriction = NOT_ESTABLISHED |

このpackは安全性・事故防止効果・服薬行為の適法性を示すものではない。レビュー対象のCまたはBの意味・版に変更があった場合、変更後のSHA/blob、対応するA独立追跡とD再試験の実測を差し替え、版が揃うまで審査の最終PASSを保留する。

### 8.2 EX01：実在する薬剤師・看護職等への確認質問（未依頼）

1. Vol.1436冊子p38（MS-07）に服薬後確認工程についての推奨があることを正しく説明できているか。掲載の方法を本ツールが全サービス・全職種に指示したように読めないか。
2. 画面開始時、全6項目confirmed、全6項目not-applicable、混合、架空例、結果・印刷の各状態で、医療判断・再投与・投薬可否・事故報告の要否が決まったかのように見えないか。
3. 「配薬準備」「服薬確認」「指示変更」の語が、介護職・看護職・医師・薬剤師の権限や、指示の正しさ／変更の有効性を暗黙に認定しないか。
4. 本人が服薬を拒否する場合、個別医学的対応を決めずに本人意思と尊厳を尊重できる文言か。事故・服薬疑義が現にある場合の正式手順への案内は適切か。
5. 結果・印刷の固定文 `WORKFLOW_BOUNDARY` と他の表示警告の意味の差、情報の視認順序、印刷後の独り歩きに問題はないか。必要な修正文を文面/画面位置ごとに示してほしい。

### 8.3 EX02：実在する介護事故防止・リスク管理責任者への確認質問（未依頼）

1. 中断・兼務・変更情報受領・連携・役割・振り返りの6項目が、職員個人の「不注意」に原因を還元せず実務として使えるか。新たな負担や不合理な二人確認義務に見えないか。
2. 介護保険施設、短期入所、認知症GH・特定施設、住宅型・サ高住、通所、訪問、居宅介護支援・介護予防支援について、実在する業務と職種の権限・正式手順をそれぞれ確認できるか。施設の一事例が全サービスへ転用されていないか。
3. 全confirmed／全担当範囲外の結果が誤安心につながらず、管理者・関係職種との確認が必要だと伝わるか。
4. 実際の事故や疑義がある場合に点検シートから離れて正式な組織内対応に移れるか。自治体報告の要否・期限はサイトが自動決定しないか。
5. このシートが正式な事故記録や法令遵守チェック・職員評価・事故件数減少の証拠に転用されないよう、追加すべき注意書きはあるか。

### 8.4 HU01：実在の内容・公開責任者への承認項目（EX01/EX02実査後のみ）

1. BのIssue/service最終blob、Aによるその**正確なB版**へのsource trace、C候補3 blob、D最終run、EX01/EX02の具体的修正・再審査結果が同一の公開版を指すか。
2. 対象サービス・職種・掲載場所・訂正窓口・改訂責任者・問い合わせ責任者・誤情報に対する緊急HOLD手順を明示できるか。
3. Android、ブラウザネイティブ拡大、スクリーンリーダー、印刷実物、privacy network、公開route・preview access制御の未実施項目を解決しているか。
4. 上記の全ゲートの証拠があって初めて `GO_FOR_PUBLICATION` か `HOLD` を、指定したcommit/blobsとサービス/公開範囲に対して**本人が明示**したか。

### 8.5 非識別・未記入の実レビュー記録様式（**未実施**）

| 必須記録 | EX01 | EX02 | HU01 |
| --- | --- | --- | --- |
| 実際の担当者（公開しない）への資格・権限確認 | 未実施 | 未実施 | 未実施 |
| 匿名review ID | 未付与 | 未付与 | 未付与 |
| 審査対象C commit / B issue+service blobs / A trace blob | 未確認 | 未確認 | 未確認 |
| source edition・冊子/PDF pages | 未確認 | 未確認 | 未確認 |
| 実施日時（JST）・実施形態 | 未実施 | 未実施 | 未実施 |
| 指摘ID・対象文/画面・重大度 | 未記入 | 未記入 | 未記入 |
| 修正commit/blob・再試験run・再審査結果 | 未記入 | 未記入 | 未記入 |
| 明示結果 | `EXPERT_REVIEW_NOT_DONE` | `EXPERT_REVIEW_NOT_DONE` | `HUMAN_APPROVAL_NOT_DONE` |

**安全な実施手順**：正当な権限と明示の送付許可を得た後、対象版を再取得し非識別の情報だけで専門職へレビューを依頼する。実際に完了した時だけ匿名ID・役割・版・指摘・対応・再検査・結果・日時を記録する。実名・所属・署名・連絡先、本人・薬剤・処方・事故記録はpublic repositoryへ保存しない。EはEX01/EX02の実記録とHU01本人の明示承認がなければ公開HOLDを維持する。

**引き渡し判定**：`REVIEW_PACK_READY`（質問と固定対象資料まで）/ `EXPERT_REVIEW_NOT_DONE` / `HUMAN_APPROVAL_NOT_DONE` / `SAFETY_PARTIAL_WITH_GAPS` / `PREVIEW_ONLY / NOT_PUBLIC`。試作は未承認・非公開を維持する。
