# Kaigo Ops — Worker D 独立安全監査：公的資料による事故防止情報

- 実施日：2026-10-09 JST
- 対象Wave：`/Kaigo Ops/Work Instructions/2026-10-09_public_source_guides_release_verification_and_accident_prevention_expansion_wave_instructions.md`
- 基準：GitHub `main` `ab457495632032e3640f398ddbd4b8cbdda319f5`（作業直前にrefを再取得）
- 対象コード：`ops-site/app/guides/medication-incident-sources/page.tsx` blob `782a1f53c635997817faf46bfe2f4e63721482c2`
- 既存根拠記録：`docs/kaigo-ops/safety/2026-10-09-medication-incident-public-source-guide-evidence.md` blob `e59615586e85747500f0ceda2f07e613d3479d78`
- 判定：**PARTIAL_WITH_GAPS**。既存静的情報ページの原典との整合性は **PASS_LIMITED**。本番HTTP/実ブラウザは **NOT_ESTABLISHED / NOT_RUN**。新規3テーマの公開安全承認は **NOT_GIVEN**。
- 本文はDの独立監査であり、Aの原典確定、Bの文章最終版、Cの実装／テスト、Eの統合公開判定、人間の専門職審査の代替ではない。

## 1. 同定・出典実査

GitHub/Vercel API の独立再取得：
- `main` head `ab457495632032e3640f398ddbd4b8cbdda319f5`。PR [#463](https://github.com/Josh-Temple/kaigo-rules/pull/463) / [#464](https://github.com/Josh-Temple/kaigo-rules/pull/464) はmerged。
- Vercel project `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`、latest production deployment `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`、target `production`、`READY`、runtime `ffd70abb5723e950a0a1036795f28da31614a1f3`。Vercel alias APIでは `ops-site-pi.vercel.app` → **同deployment ID**。
- `deploy-state/kaigo-ops` branchは依然 `e49e770a970e541d2ad95204ad277eca89a485d3`。契約上の公開ルート実測が未達なので変更しない。
- [C #451](https://github.com/Josh-Temple/kaigo-rules/pull/451) はopen/draft/unmerged。main の `ops-site/app/tools/` は既存5ディレクトリのみ。mainのIssue registryは5件、公開sitemapに試作はなし。
- **一次資料を直接開き、該当PDFページの画像も確認**：
  1. 厚労省「介護保険施設等における事故予防及び事故発生時の対応に関するガイドライン」[介護保険最新情報 Vol.1436、2025-11-07](https://www.mhlw.go.jp/content/001591418.pdf)。冊子25、26、30、32、34、35、36、37、38、39頁（PDFの0起点それぞれ+2）。通知本文では施設サービスを主対象とし、居宅系・住まい等の内容も含むと明記。
  2. [2017年3月「高齢者向け住まいにおける事故予防及び虐待予防の対応方策に関する調査研究事業 報告書」](https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf)、Ⅰ編45頁（PDF 0起点56頁）。高齢者向け住まいで「入居者に飲ませる薬でない薬」を飲ませた場合の受診推奨。**法令の一律義務ではない**。
  3. [厚労省「介護保険施設等における事故の報告様式等について」、2024-11-29](https://www.mhlw.go.jp/content/001574219.pdf)、通知PDF 0起点2〜3頁。死亡・医師が治療を必要とした事故の原則報告、その他の自治体取扱い、初報5日「目安」、対象サービスを確認。**2021年通知は2024年通知により廃止**と通知本文に明示。
  4. [PMDAくすり相談窓口](https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html)。飲み合わせ等の相談を扱うが診断・治療は扱わず、自身の薬は医師や薬局・薬剤師へ相談する案内を確認。
  5. [e-Gov刑法211条](https://laws.e-gov.go.jp/law/140AC0000000045)。公式検索結果に「業務上必要な注意を怠り、よって人を死傷させた者」とあることを確認。ただし本実行環境では法令検索URLの全文表示はできず、他資料と同等の全文画面実査とは扱わない。

## 2. 既存服薬事故ページの主張別照合（原典と断定）

| ID | 公開主張と対応箇所 | 判定 | 適用限界／要求 |
| --- | --- | --- | --- |
| D-M01 | 「事故の疑いがあるとき安全確保・施設内報告と看護職等連携、手順書」（Vol.1436冊子25〜26） | **PASS_LIMITED** | 主に施設サービスの助言。この記事を救急要請・投薬・治療の手順書にはしない。 |
| D-M02 | 「本人が飲むべきでない薬を飲ませた場合、職員判断のみで様子見にしない」（2017年報告Ⅰ編45） | **PASS_LIMITED** | **高齢者向け住まいの研究報告書内の推奨**。「全誤薬は法的に必ず受診・かかりつけ医に電話」へ一般化しない。見出し「別の人の薬」は原典の例より狭く、今後「本人が飲むべきではない薬」への表現統一を提案。 |
| D-M03 | 「飲み合わせ等の心配は医師・薬剤師へ」（PMDA） | **PASS_LIMITED** | PMDAは診断／個別治療は扱わない。リンクと趣旨は一致。 |
| D-M04 | 「死亡・医師の治療を要する事故は原則報告、その他自治体取扱い／初報5日目安」（2024通知PDF2） | **PARTIAL_WITH_GAPS / P1要明確化** | 主張自体は合うが、**通知PDF3の対象サービス（施設、認知症GH、特定施設、高齢者向け住まい等、居宅等への様式活用推奨）を本文の報告段落に近接して明示**すること。報告の制度上の根拠・市町村運用は個別確認。全サービス一律期限・一律義務を示さない。2021旧通知を現行根拠として使わない。 |
| D-M05 | 「多段階確認、作業中断の抑制、組織で再発防止」（Vol.1436冊子38〜39） | **PASS_LIMITED** | p39は単一施設の事例。全職種に二人確認を法律上要求していない点は適切。定量的な事故減少効果は主張しない。 |
| D-M06 | 「誤薬発生＝刑事罰確定ではない」（刑法211条） | **PASS_LIMITED** | 条文要件に言及し断定回避。公式法令の全文表示は未検証。罰則を連絡の強制理由に使わない。 |
| D-M07 | 原文リンク、資料種別、適用範囲、非監修・入力なしの明示 | **PASS_LIMITED** | source anchorsは `#source-...` と末尾の各`id`にコード上で対応。PDFの該当頁への直接深いリンク、実ブラウザでのフォーカス／読み上げは未検証。 |

**法的・医療的に致命的な一律断定は現行mainの静的本文からは確認されなかった**。ただしこれは原典とコードの**限定的**な照合であり、人による臨床妥当性の承認ではない。

## 3. 7つの独立レッドチームケース

| Case | 誤読の試み | 現行本文の防止策／不足 | 判定 |
| --- | --- | --- | --- |
| D-R01 | 「軽微なら受診不要・様子見」 | 自己判断で済ませない＋2017資料の限定明示 | PASS_LIMITED |
| D-R02 | 「全国法令で必ずかかりつけ医へ電話」 | そのような一律法令でない旨を明示 | PASS_LIMITED |
| D-R03 | 「医療職への連絡＝市町村報告済み」 | 別判断であると明記。ただし2024通知の対象範囲を近接表示する余地あり | PARTIAL_WITH_GAPS |
| D-R04 | 「誤薬しただけで刑事罰確定」 | 211条の結果・注意義務等の条件を明示 | PASS_LIMITED |
| D-R05 | 「記事をそのまま緊急対応フローにする」 | 現実の安全、正式手順、医療職判断を優先する明示あり。ただし緊急時の視認性は実ブラウザ未検証 | PASS_LIMITED |
| D-R06 | 「施設向け記述を通所・訪問・居宅支援にそのまま適用」 | 最終節の注意はある。報告段落と各具体的推奨の近くにも対象を置くと安全 | PARTIAL_WITH_GAPS |
| D-R07 | 「公的機関・専門職が本サイトを監修済み」 | 実在医療専門職による個別審査なしと明記 | PASS_LIMITED |

## 4. 次の3テーマ：独立出典確認と公開境界

現行mainの `ops-site/app/guides/` にあるのは服薬事故記事のみ。以下は**原典が支持する記述の候補範囲**をDが限定したものであり、Aによる最終出典台帳やB文面の承認を意味しない。

| テーマ | 原典（Vol.1436の冊子頁） | 原典に基づく公開候補の範囲 | 公開禁止・保留 |
| --- | --- | --- | --- |
| 転倒・転落 | 転倒p30、転落p32（PDF 0起点32/34） | 「個々の状況と生活環境を踏まえ、事故の予防・再発防止策を検討する」「身体拘束につながる過度な制限には注意」等、資料紹介としては**SOURCE_SUPPORTED** | 転倒はすべて予防できる／すべて施設の過失、個別の拘束・転倒後診断・移動方法の一律指示、見守り機器の効果数値は**EXCLUDE/REVIEW_REQUIRED** |
| 誤嚥・窒息 | p34〜35（PDF 0起点36/37） | 「嚥下機能等の評価を専門職と共有し、利用者ごとの食事提供を検討する」等、施設向け**SOURCE_SUPPORTED** | 誤嚥時の処置手順、食品・食形態・食事姿勢の個別指示、食物のサイズの一律指定、単一施設事例の効果の一般化は**REVIEW_REQUIRED/EXCLUDE** |
| 異食・誤飲 | 原典見出しは**「異食」** p36〜37（PDF 0起点38/39） | 「危険な物品を把握して管理方法を見直す」「生活制限や尊厳とのバランスを考慮」等、施設向け**SOURCE_SUPPORTED** | 「異食」と医薬品誤飲／薬剤関連事故の概念を無条件で同一視しない。誤飲時の毒性診断・対処、特定物品についての救命手順は**REVIEW_REQUIRED/EXCLUDE** |

**Dからの条件**：Aの主張単位の版・対象・根拠確認 → B最終文章の確定 → C実装のexact blobとCI → Dの**同一版**独立再検証までは、新規記事の安全GOを出さない。医療・処置に入る文章は静的ページから除外。

## 5. コード・公開境界・SEO

- mainでは`app/tools`直下に既存5 action toolディレクトリのみ。Issue registry5件、`lib/action-tools.ts`を変更した証拠なし。試作パスはmainにない。別ブランチのC #451をマージ／有効化しない。
- 服薬ガイドはReact/Nextの静的内容と外部原文リンクだけ。薬剤名・利用者氏名・事故記録の入力UI、症状判定、データ送信、追加custom Analytics eventのコードは見られない。既存 `<Analytics />` はlayoutにあるため、アクセス統計そのものがゼロとは主張しない。
- `buildPublicPageMetadata` → page canonical/OG/Twitter、`metadataBase=OPS_SITE_URL`、sitemapの追加ルート、robotsのsitemap指定を**ソース照合**した。実レスポンスの正規化URL/OGタグ/robots/sitemap内容は未実測。
- `sourceLinks` 5件の公開URLはいずれも公式ホスト。厚労省3 PDF と PMDA HTML は当監査で実際に取得・内容確認。e-Gov は公式検索表示で刑法211条の存在・趣旨を確認したが本文フルページの機械取得は不可。
- CIの証拠は既存文書 [#463](https://github.com/Josh-Temple/kaigo-rules/pull/463) に依拠する過去の実行であり、**このDが新たに npm/ブラウザテストを実行したものではない**。D自身のブラウザ結果をPASSとしない。

## 6. 本番公開の5層を分離した再検証

| 層 | Dが確認した証拠 | 判定 |
| --- | --- | --- |
| ① Vercel deployment作成／READY | Vercel APIからproduction/project/runtime SHAをreadback | PASS（プラットフォーム同定のみ） |
| ② alias割当 | Vercel alias APIで同deployment IDをreadback | PASS（割当のみ） |
| ③ 公開ホストのHTTP 200、旧11ルート、ガイド、試作404 | `curl`でhostがDNS解決できずHTTP 000。別のWeb取得手段も同URLにアクセスできない | **NOT_ESTABLISHED**（404/200とも主張しない） |
| ④ DOM／canonical／sitemap／sourceアンカーの実レスポンス | ③が失敗したため取得不可。GitHubソースの整合のみ確認 | **NOT_RUN** |
| ⑤ 390px Android／200% zoom／読み上げ／印刷 | 実端末ブラウザ操作を行っていない | **NOT_RUN** |

**再現**：DNSの利用可能なネットワークから `curl -iL https://ops-site-pi.vercel.app/guides/medication-incident-sources`、公開ホーム＋11既存ルート、`/tools/medication-safety-preview`、`/robots.txt`、`/sitemap.xml`をGETし、status/Content-Type/body/canonical/sourceアンカーを保存する。Vercel deployment/alias/runtime SHA と照合し、Android Chrome実機の表示・拡大・読み上げ・印刷確認とは別記録にする。**DNS失敗をアプリ404の証拠にしてはいけない**。確認完了まで `deploy-state` を進めない。外部ネットワークまたは担当者の実機検証が必要。

## 7. D→Eの引継ぎ・修正要求

1. **P1／文面の適用範囲**：2024年通知のサービス範囲（PDF p3）と2021年通知廃止の関係をA/Bに確認してもらい、自治体報告の段落・出典一覧を必要に応じて明確化する。**現時点で一般法令違反の断定があるとは判定していない**。
2. **P1／次の記事**：「異食」と広義の「誤飲」を混同しない。個別の処置・診断・用量・搬送基準は公開候補から除外する。
3. **P0／release closure**：本番URLのHTTP/DOM/実ブラウザが未確立。環境を変えて再試験し、同一deploymentの到達性を記録する。VercelのREADYと閲覧PASSを取り違えない。
4. **ゲート不変更**：EX01/EX02=`EXPERT_REVIEW_NOT_DONE`、HU01=`HUMAN_APPROVAL_NOT_DONE`、外部レビュー依頼=`NOT_REQUESTED`。C #451はdraft・未マージ・一般公開不可。専門職レビュー依頼の探索・送付・予定済みタスク登録を行わない。
5. **再検証の条件**：A/B/Cの新しいPRができたら、今回固定したpage/evidence blobとの差分、追加文のsource mapping、サービス範囲、既存5+5/試作route公開境界を同一headで再監査する。このD文書は後続変更の自動承認ではない。

**Worker D 最終判定：`PARTIAL_WITH_GAPS`（既存静的情報ページの出典整合`PASS_LIMITED`、公開到達性`NOT_ESTABLISHED`、新規テーマ`NOT_GIVEN`）。** 本文や法的・医学的結論に重大な断定追加があったときはrelease HOLDと再監査。Eの公開承認・deploy-state変更を先取りしない。

---

## 8. 2026-10-10追補 — #465 exact-head独立再監査／追加記事の公開境界

- 実施：2026-10-10 JST。今回の正本：Library /Kaigo Ops/Work Instructions/2026-10-10_public_source_guide_http_closure_and_claim_aligned_release_wave_instructions.md。
- fresh repository main参照：1c7771add72d91b58673d758dcb13ec65a14998a（GitHub commit検索の最新結果。production runtimeではない）。
- C #465：open、非draft、未マージ。**exact head 8e18f9bd54662d246081f4620728ba8c8ff38665**、base表示 ab457495632032e3640f398ddbd4b8cbdda319f5。変更3ファイルをPR patchと当該headのファイルで再照合した。
  - ops-site/app/globals.css、head blob 0a5993402fc634526fec1e9d9270cf8043a9728d
  - ops-site/app/guides/medication-incident-sources/page.tsx、head blob a3a18dfea9f0944f37ee64b7ead2f72ab506f23a
  - ops-site/tests/browser/public-source-guides.spec.mjs、head blob 17b9a9cd827e7b72ff40aa06eb3c5dbad257759f
- 当時のmain公開ガイド page blob 782a1f53c635997817faf46bfe2f4e63721482c2。#465のpage差分はmainのclass付加と6項目目次の追加で、既存の医療・法的本文を改稿していない。
- B #466：draft／未マージ、head e58adc57410a8377d37dfc857e99eecc9a1d7487。A採否前と記載した編集草案であり、**A採否→B最終文章→C表示→D再審査の最終同一版は未成立**。C #451：draft／未マージ、head 2dd0e260d0922e18d003905f4a7edf42560f640c。公開禁止は継続。

### 8.1 原典の独立再確認（該当箇所のみ）

1. 厚生労働省、2025-11-07介護保険最新情報Vol.1436、https://www.mhlw.go.jp/content/001591418.pdf ：通知p2（PDF index 1）で**介護保険施設サービスが主対象**、居宅系・住まいにも一部記述と確認。ガイド冊子p25–26（PDF index 27–28）の初動・組織手順、p30（index 32）の転倒・身体拘束への注意、p32（index 34）の転落、p34–35（index 36–37）の誤嚥・窒息、p36–37（index 38–39）の異食、p38–39（index 40–41）の誤薬・与薬漏れをPDF画像で直接再確認。施設の事例や推奨を全サービスの法定義務や定量効果へ置換しない。
2. 厚生労働省、2024-11-29事故報告通知Vol.1332、https://www.mhlw.go.jp/content/001574219.pdf ：PDF index 2の「死亡に至った事故」「医師の診断を受け投薬、処置等何らかの治療が必要となった事故」は原則全報告。その他は自治体の取扱い。初報5日以内は**目安**。index 3は様式の対象として施設、認知症対応型共同生活介護、特定施設、有料老人ホーム等を掲げ、他サービスは可能な限り活用するよう述べる。**様式の対象サービス説明を全サービス同一の全国義務へ読み替えない**。2021年通知の廃止も本文に明示。
3. 厚労省掲載2017年高齢者向け住まい研究事業報告、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf 、Ⅰ編45頁（PDF index 56）を画像で再確認。本人に飲ませるべきでない薬を飲ませた例での受診推奨であり、全国統一の法律上の電話・受診義務ではない。
4. PMDA「くすり相談窓口」https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html は公式ページを開いて存在確認。個別の診断・処方の正当化に使わない。
5. 刑法211条、https://laws.e-gov.go.jp/law/140AC0000000045 はe-Gov法令検索本体HTMLの本文機械取得ができなかった。e-Gov公式の検索結果（2026-05-21施行と表示）に「業務上必要な注意を怠り、よって人を死傷させた者」と記載されることを確認したが、**この実行によるe-Gov本文全文の直接照合はNOT_ESTABLISHED**。公開文面の法的解釈・個別要件判定は保留。

### 8.2 公開本文・C変更の独立レッドチーム（修正前／修正後）

| Case | 実際の現行・C head表示テキストからの観察 | 判定／必要な是正 | 修正後再試験 |
| --- | --- | --- | --- |
| R01「軽微だから連絡不要」 | 職員の独断で様子見を避ける旨がある。2017年住まい研究の限定も記載。 | PASS_LIMITED。個別医療判断を肯定しない。 | 未実施（B/C改稿なし） |
| R02「かかりつけ医への連絡が全国法定義務」 | そのような一律法律上の電話義務ではない、と明記。 | PASS_LIMITED。原典類型を節直近でも保持。 | 未実施 |
| R03「医療職に連絡すれば市町村報告不要」 | 医療職相談と市町村報告を分けている。ただし通知の**対象サービス一覧が報告節の近くにない**。 | **P1修正要求**。通知の対象・様式活用推奨・自治体の現行取扱いを明示。 | 未実施 |
| R04「誤薬だけで犯罪成立」 | 本文は自動成立を否定。ただし見出し「重大な結果」は211条の死傷という要件より狭く読める。 | **P1修正要求**。B案の「服薬の間違いだけで、刑事責任が決まるわけではありません。」等をA確定後に採用し、Dが再審査。 | 未実施 |
| R05「静的ガイドを緊急対応手順にする」 | 初動の安全・正式手順・医療職判断が先と記載。事故対応を遅らせない旨は冒頭セクション後段。 | PASS_LIMITED／P1視認性改善。緊急対応の医学的分岐は加えない。 | 未実施 |
| R06「施設工程を全サービスに強制」 | 末尾で施設中心と限定。2025ガイドの主対象と通知の様式対象は異なる。 | **P1修正要求**。節の根拠のすぐ近くに適用対象・資料種別を表示。 | 未実施 |
| R07「厚労省公認・専門職監修済み」 | 実在の医療専門職による個別審査なしと明記。 | PASS_LIMITED。厚労省の資料案内でありサイト監修承認ではない。 | 未実施 |
| 新規：転倒と身体拘束の一律法的判断 | B草案は特定対応の身体拘束該当性を断定しない。A原典p30で一般的なリスクを確認。 | 候補の限界のみPASS_LIMITED。**最終文面・実装なしのため公開HOLD**。 | 未実施 |
| 新規：誤嚥・窒息の食事形態・救命方法 | 厚労省冊子p34–35は専門職評価・個別検討の説明で、技術的指示への転用は危険。 | 具体的食形態／誤嚥時の応急処置を公開ガイドへ追加しない。**HOLD**。 | 未実施 |
| 新規：異食の毒性・物品別救命方法 | 原典見出しは「異食」。p36–37の環境整備と尊厳を広義の誤飲すべてへ拡張しない。 | 物品ごとの毒性／処置を静的記事から除外。B正式稿・C実装なしで**HOLD**。 | 未実施 |

### 8.3 #465 exact-headの変更差分・技術境界

- 変更全件：CSS（目次・sourceRow折返し・印刷時のURL表示、reduced-motion）、guide page（main class追加、6件の目次アンカー）、Playwright spec（5テスト）。**公開registry、sitemap、robots、metadata、Analytics、薬剤入力フォーム、C #451試作コード・flag、action toolはPR diffの変更対象外**。
- #465 headの静的検査：原典sourceLinksは5件の公式リンクで変わらず、記事に入力欄・チェックシート・診断結果UIを加えていない。目次リンクはfirst-step/minor/report/prevent/law/sources各IDを指す。出典参照は依然「本文→ページ内出典欄→原典」の**二段階リンク**。Bの段落直結リンク要件は未実装。mainのsitemap・robots・canonical/OG metadata設定は読んだが、**#465変更後の実HTTPレスポンス検証ではない**。
- 自動テスト5件：home→guideとアンカー、390px headless viewportとキーボードEnter、**CSS zoom=2の代替**、print media CSS、localhostのsitemap/robots/試作404。印刷PDF出力の目視、native Android 200% zoom、スクリーンリーダー実聴、実端末操作の根拠にはならない。既存11ルートと新guideの回帰はCI上の範囲でのみ確認。
- C head 8e18f9... に対するGitHub Actions成功（Dが外部runnerの結果を再取得）：Validate ops site run **37934959505**（npm ci、npm test、npm run build、Chromium tools、route smokeの各step success）、publication-readiness run **37934959236**、Validate build run **37934959246**。GitHub ActionsのCI結果であって**Dがnpmを独立実行した記録ではない**。npm run test:browser / npm run verify:routes の個別コマンド実行をこの結果だけから別途認定しない。Cの新版・merge commitへ自動継承しない。

### 8.4 本番は5層に分ける

| 検証層 | 2026-10-10 Dの独立取得と限界 | 判定 |
| --- | --- | --- |
| Vercel production identity | 正しいproject prj_7kKmZkto1j9r9Z3otwccx05LAjTpでdeployments APIを再取得。最新dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbuはproduction／READY、runtime ffd70abb5723e950a0a1036795f28da31614a1f3。 | PLATFORM_IDENTITY_PASS |
| alias割当 | Vercel alias APIでops-site-pi.vercel.appが同じdeployment IDを指すことを再取得。 | ALIAS_ASSIGNMENT_PASS |
| 外部HTTP | この実行環境ではPython socket DNS が [Errno -3] Temporary failure in name resolution。HTTPS GETもDNS段階で失敗。公開Web取得ツールもaliasとdeployment URLのガイド取得不可。**HTTP応答コードは取得していない**。 | PRODUCTION_NOT_VERIFIED（200/404/5xxいずれも未観測） |
| 実HTML/DOM | 外部HTTP不可のためHTML、canonical/OG、source anchor、sitemap/robots、11 route、非公開previewの実statusを直接読めない。 | NOT_RUN |
| 実ブラウザ/実機 | production Android Chrome 390px、native 200%拡大、読み上げ、キーボード、印刷実査はDでは行っていない。 | NOT_RUN |

**deploy-state/kaigo-opsの検証markerを変更しない**。旧marker e49e770a970e541d2ad95204ad277eca89a485d3 は過去の検証位置であり、今回のproduction HTTP確認ではない。Web取得手段が利用できる別の実行環境とEの正式verifier contractに委ねる。

### 8.5 Dの確定引継ぎ・終了判定

- **既存公開ガイド本文**：原典の限定照合はPASS_LIMITED。P1は刑法211条の見出し、2024年事故報告の対象サービスと自治体差、段落→原典の直接リンク、実事故対応注意の視認性、資料の種類と対象の近接表示。B最終稿、C改稿後のhead/blob、再実行CIとD同一版再監査まで本文改稿を**RELEASE_HOLD**。
- **#465 UI変更**：変更3ファイルのexact-head差分とCI結果は確認。新しい危険な入力機能・医学的判定は発見しなかった。**コード監査PASS_LIMITED、全体公開ゲートPARTIAL_WITH_GAPS**。印刷・200%などの実機は非検証、本文修正を含む最終公開同一版としてはまだGOしない。
- **転倒・転落／異食／誤嚥・窒息**：Aの一部SOURCE_SUPPORTEDは編集・実装・D最終監査の代替にならない。3テーマ全て**PUBLIC_SOURCE_GUIDE_HOLD**。次にDが審査する際は各articleのexact SHA/blob、claim→段落→出典・対象、source direct link、スクリーン・CI証拠を固定する。
- **選択式C #451**：PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED。EX01/EX02=NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE、HU01=HUMAN_APPROVAL_NOT_DONE。専門職への依頼・日程調整はしない。
- **Wave D終端：PARTIAL_WITH_GAPS**。新しい危険な断定の確認なしという限定評価と、P1未修正、B最終文面未確定、実HTTP/実ブラウザ不成立を両立して記録。Eはこの追補だけでrelease GOまたはdeploy-state更新を行わない。



---

## 9. 2026-10-10 Worker D — medication + fall exact-head independent safety review (current-state limited audit)

**Instruction:** Library \`/Kaigo Ops/Work Instructions/2026-10-10_medication_and_fall_source_guides_exact_head_safety_review_and_controlled_release_wave_instructions.md\`, §6. This is an **independent pre-final review**, not final same-version approval: A/B copy is not yet rendered in C, and C has not submitted the new fall route. Earlier sections remain historical and must not be retroactively treated as checking this head.

### 9.1 Freshly fixed immutable identity and deployment boundary

| Evidence | Exact identity at audit | Scope |
| --- | --- | --- |
| repository main | \`6c170418cbc178c7efebc32e76c46b8cbf4c3b32\` | source baseline; **not** production runtime |
| A #470 merged | head \`b98ff0e527d6bd6b18ea48e461fafc9660a079b9\`; current ledger blob \`7f373c396f9358e0179021f09d95cb2698ce9b1f\` | claim limits, source decisions; §6 crosswalk predates B latest |
| B #466 draft/open | head \`5df748a60b0d3699c751643b47fe77e90aa9a8d2\`; editorial blob \`16915a0d6573e534c2661ed24d2cf758ad4c9164\` | proposed final medication revision and fall text; **not rendered** |
| C #465 open/unmerged | head \`77eb4b391ac722adc1a34024e6c7a33b35179949\`; \`globals.css\` blob \`0a5993402fc634526fec1e9d9270cf8043a9728d\`; medication page blob \`3fa8965bc2abc4841c0c5699e1f8b7855a76d1e8\`; browser spec blob \`6f6787c630d273bd76be47ce09c3758da388cfcb\` | navigation/source-direct-link/print regression only; no B clinical/legal rewrite or fall page |
| current main medication page | blob \`782a1f53c635997817faf46bfe2f4e63721482c2\` | existing published source code; does not incorporate B |
| prior D #471 merged | head \`c65e366acb5e61bd960d8efe7750470140072b21\`; audited old C \`8e18f9bd54662d246081f4620728ba8c8ff38665\` | **not** same-version approval for C latest |
| E #473 | head \`30ba214ad9bee2418b32e1b095f90e46a3886115\`; open/unmerged at read | prior-wave document-only closure; not this release approval |
| preview #451 | draft/open head \`2dd0e260d0922e18d003905f4a7edf42560f640c\` | PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED |

**C exact changed-path inventory** (GitHub paginated PR filenames + unified diff): only \`ops-site/app/globals.css\`, \`ops-site/app/guides/medication-incident-sources/page.tsx\`, \`ops-site/tests/browser/public-source-guides.spec.mjs\`. Changes from previous D-reviewed C head include the paragraph citation-to-original link and its matching print/navigation test, not changes to the statutory/medical body. No new fall page, sitemap fall entry, new form, action tool, published registry, medication preview flag, or Analytics event occurs in the three changed paths. No site-wide absence of features is inferred solely from the PR diff.

### 9.2 Primary-source independent reading (2026-10-10)

- **G25** — MHLW, 2025-11-07, Vol.1436, \`https://www.mhlw.go.jp/content/001591418.pdf\`; official PDF page 2 explicitly calls long-term-care insurance facility services the **main** audience and notes selected home/residential contexts. The original booklet p30 (PDF 1-based p33) explicitly says complex physical/mental/environmental causes, some falls are difficult to prevent, and overrestriction can amount to physical restraint; booklet p32 (PDF 1-based p35) discusses personalized bed-area environment. Those two PDF pages were independently viewed in original form, not inferred from GitHub. One facility case study does not prove general effectiveness. No independent bed-rail, sensor setting, restraint legality or emergency triage claim is accepted.
- **N24** — MHLW, 2024-11-29, Vol.1332, \`https://www.mhlw.go.jp/content/001574219.pdf\`; official PDF pages 3–4 directly checked. The notice distinguishes death / medically treated accidents as in-principle reporting targets, other accidents according to local authorities, and first notification within five days **as a guideline**. Page 4 specifies the categories for the unified reporting form (facilities, group homes incl. preventive, specified facilities incl. community-based/preventive, and residential categories), and encourages use for other home-care services where possible. Do not infer identical legal reporting duties, destinations or deadlines for every service. Local rules remain **NOT_ESTABLISHED**.
- **R17** — MHLW-hosted March 2017 study on housing for older people, \`https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf\`; Part I p45 / PDF p57 independently viewed. It advises medical examination rather than unilateral watchful waiting after administration of someone else's medication in that housing context. **Research recommendation**, not blanket statutory consultation/examination duty.
- **PMDA** — official drug consultation page \`https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html\` accessible as public HTML; not a basis for case-specific prescribing, emergency transport or medical triage.
- **L211** — e-Gov \`https://laws.e-gov.go.jp/law/140AC0000000045\` resolves to a dynamic page but the current complete article text was not independently extracted. Official indexed e-Gov text for the version marked **2026-05-21 effective** displays the phrase about neglect of precautions required in the course of business **resulting in death or injury** (「人を死傷させた」); the article's **full current authoritative text by direct retrieval remains NOT_ESTABLISHED**, not falsely promoted to fully verified. The B summary is conservative and does not determine individual criminal liability. Hold any stronger statutory/legal statement pending exact-law-version full-text retrieval.

PDF page numbers above are 1-based including the cover; deep-link \`#page=N\` navigation in a real Android/browser PDF viewer is **NOT_TESTED**.

### 9.3 Claim-to-paragraph-to-code crosswalk (audit, not approval)

| ID | Source and final B candidate | Observed C exact head | D decision |
| --- | --- | --- | --- |
| MED-A01/A08 | B §2.1: immediate incident -> prioritize safety/formal protocol/professionals, immediately after lead; G25 p25–26 | C still places the strongest warning after initial section paragraph, **not immediately after lead** | **BLOCKED for medication revision** |
| MED-A02/A03 | B §2.2: R17 explicitly scoped housing recommendation; PMDA general consultation | C original wording retains scope, but does not reproduce B final approved paragraphs | **PARTIAL_WITH_GAPS; text integration required** |
| MED-A04/A05; X-02 | B §2.3: N24 report-vs-form target services, five-day guideline, local implementation; links to PDF pp3–4 | C report section still lacks explicit notice reporting-form target-service categories directly alongside the claim | **BLOCKED for medication revision** |
| MED-A06 | B §2.4: facility-centered risk management, no universal double-check duty or general causal effectiveness | C carries existing conservative warning; latest B wording not integrated | **PARTIAL_WITH_GAPS** |
| MED-A07 | B §2.5 heading “服薬の間違いだけで、刑事責任が決まるわけではありません。” and narrower explanation | C still shows old heading “重大な結果と注意義務違反があれば、刑事責任が問題になる場合もある。” | **P1 wording fix absent; BLOCKED** |
| FALL-01/02/03 | B §3 F-01/02/03: facility scope, individualized risks, overrestriction and bed-area; G25 booklet 30/32 | no new fall route in C changed-path inventory; no rendered paragraphs | **BLOCKED for new guide** |
| MED-A04/A05; X-02 (fall F-04) | B §3 fall reporting: notice targets, five-day guideline, locality/service differences | no rendered fall paragraph | **BLOCKED for new guide** |

**Critical distinction:** A's SOURCE_SUPPORTED + B exact editor blob + C's green CI are **three different artifacts**. C did not implement B. Therefore no final same-version A→B→C→D chain is established. D's review of the current C head covers only its non-medical navigation/test changes.

### 9.4 Red-team outcomes (before / candidate after / actual residual)

| Case | Actual C head (before) / B candidate (not yet rendered) | Residual / result |
| --- | --- | --- |
| D-R01 “minor so no action” | C avoids unilateral watchful waiting; B keeps housing-only research caveat | low misreading risk in existing C; B integration untested |
| D-R02 “universal call/medical-visit duty” | C disclaims blanket statutory doctor-call rule; B further narrows the housing research | no observed universal legal mandate; final new copy untested |
| D-R03 “medical contact substitutes for municipal report” | C separates procedures but lacks notice form-service category alongside report; B §2.3 adds it | **P1 unresolved** |
| D-R04 “medication error automatically criminal” | C rejects automatic liability but old “重大な結果” title; B heading fixes it | **P1 unresolved**; L211 exact full text not established |
| D-R05 “the static article is an emergency protocol” | C warning follows the first section; B places urgent boundary immediately after lead | **P1 placement unresolved** |
| D-R06 “facility advice mandates all care services” | C limits in last section; B brings precise notice scope closer to report claim | **P1 proximity unresolved** |
| D-R07 “MHLW/expert-endorsed website” | C says no individual expert review; B says source guide not clinical approval | limited safe boundary retained; EX/HU still incomplete |
| D-F01 “every fall avoidable / every fall negligence” | B expressly rejects both; G25 p30 recognizes difficult-to-prevent falls | not implemented; **fall release HOLD** |
| D-F02 “this page rules whether restraint lawful” | B expressly excludes individual restraint judgments | not implemented; **fall release HOLD** |
| D-F03 “uniform bedrail/sensor/transfer settings” | B excludes universal device, placement and care procedures | not implemented; **fall release HOLD** |
| D-F04 “individual examination/ambulance decision after fall” | B excludes clinical triage; prioritizes professional/emergency channels | not implemented; **fall release HOLD** |
| D-F05 “one facility case proves nationwide reduction effect” | B claims no quantitative effectiveness; G25 case studies do not establish national effect | not implemented; **fall release HOLD** |

### 9.5 UI / test / privacy / release boundary

1. **Code:** C's \`Citation\` now links both index \`#source-id\` and the unchanged corresponding original public source URL, opening the original in a new tab with a descriptive aria-label and \`rel="noreferrer"\`. Original five source URLs have official hosts. These links point to **document-level** URLs, not B's newly proposed paragraph-specific PDF deep links; actual deep-link behavior remains untested. Focusable six-anchor in-page contents, responsive source wrapping, reduced-motion override and printable source URLs are present.
2. **Browser tests:** C added five Playwright tests for heading/canonical/OG/source match, mobile 390px overflow and keyboard, CSS zoom=2 proxy, print media source URL, sitemap/robots and hidden preview 404. Static review of the test source finds correct targets and no collection form. CSS proxy ≠ native Android zoom; print CSS assertion ≠ printed paper/preview; Playwright ≠ screen-reader human check.
3. **Exact-head CI verified independently from GitHub:** C \`77eb4b391ac722adc1a34024e6c7a33b35179949\`, Validate ops site run [37957413246](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37957413246) success; steps \`npm ci --no-audit --no-fund\`, \`npm test\`, \`npm run build\`, Chromium via \`npm run test:browser\`, and route smoke via \`npm run verify:routes\` were green under [validate-ops-site.yml](../../../../.github/workflows/validate-ops-site.yml); publication-readiness [37957413269](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37957413269) success; generic build [37957413305](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37957413305) **success** (previous C PR body described it as pending, now superseded by live check). No new C head after those checks was observed in this audit.
4. **Privacy/held prototype:** C changed paths contain no form/input/personal information capture/custom Analytics events; no published route/registry/flag changes. Current main sitemap includes original medication page but no fall page. #451 remains draft/unmerged; held interactive preview 404 is asserted in C localhost CI. **Actual production route status, React hydrated DOM, screen-reader, native Android 200%, human print and source deep-link PDF viewer experience NOT_RUN by D**.
5. **Production evidence:** Previous external HTTP probe [37993334787](https://github.com/Josh-Temple/kaigo-rules/actions/runs/37993334787) reportedly checked previous deployed 15 routes. No new deployment or alias reallocation is established by this D audit; **old 15/15 HTTP does not prove this unmerged C head, any future fall page or future deployment**. The \`deploy-state/kaigo-ops\` marker stays E-controlled; this audit did not advance it.

### 9.6 D independent scoped conclusion and mandatory re-review trigger

| Unit | D finding | E instruction |
| --- | --- | --- |
| Existing **medication article text revision** | **BLOCKED** — B \`16915a0d...\` is not rendered in C \`3fa8965...\`; P1 legal/report/lead copy outstanding | \`RELEASE_HOLD\`; re-audit exact B paragraph ↔ new C page blob and full CI before any merge |
| New **fall/bed-fall static source page** | **BLOCKED** — B §3 has limited source-supported draft but **no C rendered page/route/SEO/tests** | \`PUBLIC_SOURCE_GUIDE_HOLD\`; require exact TSX route, all paragraphs, sources, metadata, 16-route regression and new D evidence |
| Non-medical **#465 contents/links/print/Playwright improvements only** | **PASS_LIMITED** (code + matching CI head); still **PARTIAL_WITH_GAPS** for direct PDF-page behavior and human accessibility | E may evaluate this narrow UI-only diff separately, but it cannot be used as approval for B words, new article or production |
| Foreign-object ingestion / aspiration/choking | **BLOCKED for this Wave's release** (outside requested scope) | \`PUBLIC_SOURCE_GUIDE_HOLD\` for both |
| D Wave as a whole | **PARTIAL_WITH_GAPS** (nonclinical UI evidence established; same-version content chain **not established**) | **No full release GO**; re-run D after A revised limits, B latest text, C final code and exact-head CI align |

**Handoff for A/B/C/E:** A should expressly resolve any claim-scope changes and L211 authoritative-version gap. B should preserve paragraph-level text + source+PDF page and notify C of final immutable editorial blob. C should integrate only those sentences, retain #465 source navigation, implement **one** fall page if supported, and submit a new exact head with tests/changed-path inventory. D then rechecks that same B/C head, all twelve red-team attempts, official source URLs and CI and records a new result. E alone decides merge, scoped release, new deployment verification, and deploy-state contract. **No expert outreach, HU01 approval, #451 merge/enablement, production deployment, or marker update was performed by D.**
