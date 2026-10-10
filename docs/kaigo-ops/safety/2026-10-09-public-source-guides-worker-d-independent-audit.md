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

---

## 10. 2026-10-10 final-alignment Wave — D独立安全再監査（限定評価／公開HOLD）

**対象指示**：Library `/Kaigo Ops/Work Instructions/2026-10-10_medication_fall_final_alignment_independent_safety_reaudit_and_staged_release_wave_instructions.md` §6。**評価日**：2026-10-10 JST。GitHub現行PR、コード本文、公式資料、Actions実行記録を別々に取得した。これは**Aの最新版B最終照合、B/C同一版の正式固定後のD最終PASSではない**。過去§9の「転倒記事未実装」は旧C headへの歴史的観察であり、今回のCには適用しない。

### 10.1 実際に監査したID、変更範囲、依存関係

| 取得対象 | 現行の固定識別子・観察 |
| --- | --- |
| `main` | `9dd655fcbd2a37c19d5d8b77606d75149105434d`。E #476の文書統合後。production runtimeではない |
| A #474 | open、head `650bb9bdf3522f263c03d410ccd051468eada922`、出典台帳blob `2849cdc53f3117c908cb6331b0946bdb2aedb80c`。**§7は旧B head `5df748a...`／旧blob `16915a...`参照のまま** |
| B #466 | draft/open、head `97389ce1538978abadcf4e2618493b7258995f27`、編集稿§2/§3/§7 blob `1394df30751e408e997524e431a99bf696e52fe9` |
| C #465 | open、head `ef12b659bc9fca43df4c7ebd15b9cf5471dbcecd`、変更8ファイル。**転倒記事・トップリンク・sitemapは実装済み** |
| C服薬TSX | `f3415366187b47c8a6a93a378f3f223e0971d181` |
| C転倒TSX | `de66e2dfcb0985864be230049ecea44612fd3b05` |
| C tests / UI | browser spec `b7f07446c80e5aaf14b4a872a90c68a9e16b1ccc`、CSS `f2a43acf8f062560db9fbf3aa2fffc31e684ed58`、home `ca0113d6de512236acb87c5346bc6d69bcd8b26e`、sitemap `a85ad4d8069e0d0f4bde400fbda7dfaba2f44175`、route verifier `1f8e9c1e321c4961fa2844bbc3621e934fd1b267` |
| C引継ぎ | `3ce16c69c89af5f471ae116947cb147c033b3cf4`。冒頭に旧C基点 `77eb4b...`が残存。最終headの明示訂正未完 |
| D旧監査 #475 | 旧head `300b4ad53b14f1483539f0b36e5047ba31eb6c9f`／旧台帳 `e5b86536e7e78fba797f324adfc90662e70c5f5b`。§9は旧C `77eb4b...`、旧B `16915a...`の監査 |
| #451 | draft/open/unmerged、`2dd0e260d0922e18d003905f4a7edf42560f640c`、`PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED` |

変更8ファイルはC引継ぎ、CSS、服薬TSX、転倒TSX、home、sitemap、route verifier、Playwright browser spec。Bの最新編集稿とCの**実ファイル**を直接読んだ。PRの自己申告を独立監査の代用にしない。**A §7が最新版B blobを対象に更新されていないため、A→B→C→D final exact-version chainは `NOT_ESTABLISHED`**。

### 10.2 公的原典の独立確認（正式な対象・文書類型・頁）

| ID | 今回確認した原典・頁 | 原典が支持する範囲／未確立 |
| --- | --- | --- |
| G25 | 厚労省・2025年11月 Vol.1436 ガイドライン、https://www.mhlw.go.jp/content/001591418.pdf 。主対象の冒頭、冊子25–27頁／PDF28–30、冊子30頁／PDF33、冊子32頁／PDF35、冊子38–39頁／PDF41–42を独立に閲覧 | 主に**介護保険施設**。転倒は多要因かつ防ぎ難い場合があり、過度な行動制限は身体拘束につながるおそれ。ベッド周辺は個別条件。施設事例の効果を全サービスへ一般化しない |
| N24 | 厚労省2024-11-29 Vol.1332通知、https://www.mhlw.go.jp/content/001574219.pdf 。本文1–3頁／PDF通し2–4頁を直接照合 | PDF2に2021年旧通知の廃止、PDF3に報告対象と第1報5日**目安**、PDF4に共通様式の作成対象サービス。**報告対象≠様式対象≠自治体ごとの具体的義務**。自治体現行の要否・期限は `NOT_ESTABLISHED` |
| R17 | 厚労省掲載2017年「高齢者向け住まい」調査研究、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf 、Ⅰ編45頁／PDF通し57頁を閲覧 | 他人の薬を飲ませた場合に様子見だけとせず受診につなげる旨は**対象限定の研究上の推奨**。全介護サービスの全国一律法的受診義務ではない |
| PMDA | https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html の公式案内を直接読んだ | 一般的なくすり相談案内。個別事故の診断・治療・搬送判断先とは扱わない |
| L211 | e-Gov https://laws.e-gov.go.jp/law/140AC0000000045?occasion_date=20260901 を確認 | 2026-05-21施行版とされるrevisionはA記録にあるが、Dは**当該施行版・刑法211条の公式全文を直接抽出・逐条確認できなかった**。法令原文の同一版直接確認は `NOT_ESTABLISHED`。索引断片を正式全文と称さない |

PDFの冊子印刷頁と通し頁は区別。リンク `#page=2/3/4/28/33/35/41/57` が所定URLに埋め込まれたことと、実Android/PDFビューアで当該頁に遷移することは別。後者 `NOT_RUN`。

### 10.3 claim→B確定段落→C表示コードの独立突合

| Claim | B最新版と根拠 | C `ef12b659...`で直接読んだ表示実装・差分 |
| --- | --- | --- |
| MED-A01、A08 | B §2.1、G25冊子25–26／PDF28–29 | 服薬ページのlead直後に `sourceGuidePriority`。事故時は安全確保・正式手順・医療職を優先。**意味一致**、個別救急・服薬判断なし |
| MED-A02 | B §2.2第1段落、R17Ⅰ編45／PDF57 | 服薬 `#minor` で「高齢者向け住まいの研究推奨」「一律法律義務ではない」。**意味一致** |
| MED-A03 | B §2.2第2段落、PMDA | 服薬 `#minor` で一般的相談窓口と個別事故診断・治療を区別。**意味一致** |
| MED-A04、A05、X-02 | B §2.3の報告対象→第1報5日目安・旧通知廃止→様式対象3段落、N24 PDF2–4 | 服薬 `#report` の3段落、該当PDFへの直リンク、様式対象サービスの列挙・自治体差・目安が近接。**意味一致**。自治体別義務 `NOT_ESTABLISHED` |
| MED-A06 | B §2.4、G25冊子38–39／PDF41–42 | 服薬 `#prevent`。全国一律二人確認義務・再現可能な削減効果を主張しない。**意味一致** |
| MED-A07 | B §2.5、新見出し「服薬の間違いだけで、刑事責任が決まるわけではありません。」 | 服薬 `#law` に同じ見出し・限定要旨・e-Govリンク。**見出し・意味一致**、ただしL211公式同一版全文未確認につき法的根拠の最終PASSなし |
| FALL-01 | B §3 F-01、G25冊子30／PDF33 | 新転倒ページ `#factors` に多要因・本人の状況・環境・全転倒予防/過失断定否定。**一致** |
| FALL-02 | B §3 F-02、G25冊子30／PDF33 | `#dignity` に過度制限への注意と個別の身体拘束適法性非判定。**一致** |
| FALL-03 | B §3 F-03、G25冊子32／PDF35 | `#bed` にベッド周辺と本人の状態、機器設定・介助を一律指示しない注意。**一致** |
| FALL報告 | B §3 F-04、N24 PDF3/4 | `#report` に国通知の事故報告対象・5日目安・様式対象差・自治体運用確認。**一致** |

一致は**TSX上の文章とB候補の比較**を意味し、productionでrender済みという主張ではない。B文章とCは大半が逐語または意味上一致する一方、Aの**旧B参照**とC引継ぎの旧基点が未解消であるため、正式な文書間identity chainを成立済みとは判断しない。

### 10.4 12件の危険な誤読：旧／B修正候補／現C／残留

| ケース | 誤読・旧リスク → B候補 | 今回のCコード独立確認 → 残余 |
| --- | --- | --- |
| R01 | 軽微だから何もしなくてよい → R17の限定的な受診推奨を明記 | `#minor` で職員のみの様子見判定を否定。限定表現あり／実人の読み取り未実測 |
| R02 | 全国一律に医師連絡・受診が法定義務 → 研究と法令の分離 | R17は高齢者向け住まい限定と明記。一律受診義務を否定／個別状況の判断不可 |
| R03 | 医療相談したから行政報告不要 → 国通知の手続を分離 | 医療相談と市町村報告を別の手続と表示／具体的報告要否は自治体確認 |
| R04 | 誤薬だけで犯罪成立 → MED-A07非断定見出し | 新見出しを反映／**L211正式施行版全文 `NOT_ESTABLISHED`** |
| R05 | 静的記事を個別救急手順と誤認 → lead直後に優先行動境界 | 2記事とも緊急時は記事より正式手順を優先／実使用・専門職レビュー未実施 |
| R06 | 施設ガイドを訪問・通所等へ義務化 → 主対象・対象差を近接表示 | G25の施設中心とN24様式対象の差を明示／各サービス固有義務は未立証 |
| R07 | 厚労省監修・実在専門職承認済み → 非監修・未審査を明示 | 2記事ともサイト未監修／専門職による個別審査なしと表示／実専門職安全確認未実施 |
| F01 | 全転倒は防止でき、発生時は職員の過失 → 多要因・予防限界 | `#factors` で両断定を否定／個別過失判断なし |
| F02 | この記述で身体拘束の合法性を決定 → 非判定 | `#dignity` とpriorityに個別適法性は判定しないと記載 |
| F03 | ベッド柵・センサー・介助工程を一律設定 → 個別環境の検討のみ | `#bed` で特定機器・配置・介助の共通指示なし |
| F04 | 転倒後の診断・受診・搬送をこのサイトが指示 → 正式手順優先 | priorityとscopeで医療判断を明確に除外 |
| F05 | 単一施設の事例・事故率で全国的効果・事故ゼロを保証 → 定量効果除外 | 転倒本文には効果率や事故ゼロ保証なし |

**12ケースのうち、新しい明白な危険断定はCのTSXに確認しなかった**。この限定評価を、専門職承認・全国の法的適用・実際の事故時安全性・正式公開承認に拡大しない。

### 10.5 GitHub Actions／URL・表示・privacy／未実施

- C exact head `ef12b659...` のActionsをDが取得：[`Validate ops site` run 38007012548](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012548)、job `114078018376` は **success**。生ログで `npm ci`、`npm test` **20/20**、`npm run build`（2記事のrouteが生成）、Chromium `npm run test:browser` **15/15**、`npm run verify:routes`（服薬・転倒・#451 404・robots/sitemap）を確認。[`Validate build` run 38007012580](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012580) job `114078086527` success、[`Verify publication readiness integration` run 38007012539](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012539) job `114078018545` success。**旧C headのCI結果は流用していない**。ローカルnpmは `NOT_RUN`。
- Cの `verify-routes.mjs` とbrowser specで、従来11（home+5 Issue+5 tool）、既存服薬200・新転倒200・#451試作404・robots/sitemap各200の**16 URL相当のローカルCI smoke**を確認。これは新production 16/16 HTTP確認ではない。CI coverageはテスト記述＋成功ログの範囲に限る。
- 2記事のmetadata pathからcanonical/OGを生成し、homeとsitemapで転倒へ導線、相互記事リンク、原文リンク、ページ内目次、印刷URLを実装。Playwright sourceと成功ログで390px、keyboard、CSS zoom=2 proxy、reduced-motion、印刷CSSを評価。**headless/CSS zoomとAndroid native 200%または実印刷・読み上げを同一視しない**。
- C差分内に事故詳細・利用者／職員名・薬剤情報の入力フォーム、新Analyticsイベント、#451公開flag、registry追加は確認されない。コード差分外を含むサイト全体の不存在の証明ではない。#451はdraft/unmerged、CIの404確認あり。EX01/EX02=`NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE`、HU01=`HUMAN_APPROVAL_NOT_DONE`。
- **独立の未実施**：Android実機、native 200%、人間のスクリーンリーダー、実紙印刷、実PDF `#page` viewer挙動、専門職審査、実production HTTP/DOM、Vercel新deployment/alias/runtime、正式deploy-state contractはすべて `NOT_RUN / NOT_ESTABLISHED`。既存productionの15/15外部HTTPや旧deploy-stateで今回Cの公開を裏付けない。

### 10.6 Dの範囲別判定とEへの引継ぎ

| 対象 | **今回の独立D判定** | Eの公開ゲート |
| --- | --- | --- |
| **既存服薬本文の改訂** | `BLOCKED`。B→Cの文章とCIは限定的に整合するが、A台帳が**B旧blob**を指す。L211の対象施行版条文全文の独立確認も未確立 | `RELEASE_HOLD` |
| **転倒・転落の新しい静的記事** | `PARTIAL_WITH_GAPS`。記事・資料リンク・TSX文章・同headのCIを確認したが、A最終B照合、C引継ぎ版、実機・本番は未完 | `PUBLIC_SOURCE_GUIDE_HOLD` |
| **非医学的UI（導線・引用アンカー・印刷・回帰）** | `PASS_LIMITED`（現Cコード＋exact-head CIの範囲のみ） | 医療・法律本文と同じ**8ファイルのC PRをそのまま一括merge不可**。UIのみを公開するなら安全な独立PR差分へ分離し、**新head CIとD再監査**を要する |
| 異食／誤嚥・窒息 | 本Wave公開範囲外 | 各 `PUBLIC_SOURCE_GUIDE_HOLD` |
| **Wave D全体** | `PARTIAL_WITH_GAPS`。A/B/C/D最終同一版=`NOT_ESTABLISHED` | **release GOの根拠は出さない。main merge・production・deploy-stateはDから操作しない** |

**修復順序**：A #474§7でMED-A01〜08、X-02、FALL-01〜03を**最新版B 1394df...の逐語段落へ再突合した新blob**を確定→Bの編集稿とA採否を再固定→C #465の現行headと全blobs・引継ぎの旧head訂正・必要なCIを最終化→**Dが変化した最終同一版を再独立評価**。head/blob変更後に今回の限定判定を無条件継承しない。Eが範囲別GO/HOLDと実際のmerge/productionを判断する。

**変更の境界**：D監査台帳の追補のみ。既存監査の旧節を削除せず、A/B/C、アプリ、#451、専門職接触、Analytics、Vercel、deploy-state、予定済タスク、公開機能を変更していない。

---

## 11. 2026-10-10 D_FINAL_TUPLE_INDEPENDENT_REACCEPTANCE — 最終A/B/C独立差分再監査（E判定用）

**checked_at:** 2026-10-10T13:29:48.123Z UTC（JST +09:00）。**Instruction:** Library `/Kaigo Ops/Work Instructions/2026-10-10_medication_fall_exact_tuple_independent_reacceptance_scoped_release_and_verified_production_wave_instructions.md` §6。**実施区分:** GitHubの不変ファイル・PR・比較・Actionsジョブ/生ログと、公的原典の直接表示に対するD独立監査。旧§9/§10は当時の観察として保持し、本§11を最終版の評価として優先する。**Dはアプリ修正・merge・deployを行わない。**

### 11.1 監査したexact tuple（mainとruntimeは別）

| 領域 | 直接取得した固定値 | 観察と境界 |
| --- | --- | --- |
| main | `6f659c51459d82d3d70f48e05f9b341f76ae266f`（GitHub main branch API） | A #474 docs-only統合済み。production runtimeではない |
| A main §8 | `docs/kaigo-ops/safety/2026-10-09-accident-prevention-public-source-claim-audit.md` blob `b603592b3b91f303cf021af283b953bd8b9e05d1` | MED-A01〜08/X-02/FALL-01〜03を**B最終版**の段落へ採否済み。旧A §7の旧B参照は履歴、未修復ではない |
| B #466 | draft/open、head `0b192a57674681952afcc4766d4cd03ce523e331`、`docs/kaigo-ops/safety/2026-10-09-public-source-guides-worker-b-editorial-drafts.md` blob `4549faac7651b6c3f88291740548e179e74e037a` | §2/§3読者用文章・§7/§8照合記録を取得。draftは公開承認ではない |
| C #465 | open/unmerged、head `b33f8b166628f7c06fb96cc7ccac95a579e24434`、changed paths **8** | 転倒ページは既に存在。旧D §9の「転倒ページなし」は旧版の事実 |
| C medication | `ops-site/app/guides/medication-incident-sources/page.tsx` blob `f3415366187b47c8a6a93a378f3f223e0971d181` | 新文面実装済み。ただしproduction反映とは別 |
| C fall | `ops-site/app/guides/fall-prevention-sources/page.tsx` blob `de66e2dfcb0985864be230049ecea44612fd3b05` | 静的出典案内として実装済み |
| C home / sitemap / CSS | `ca0113d6de512236acb87c5346bc6d69bcd8b26e` / `a85ad4d8069e0d0f4bde400fbda7dfaba2f44175` / `f2a43acf8f062560db9fbf3aa2fffc31e684ed58` | home導線、相互リンク、掲載範囲、印刷・reduced-motionを確認 |
| C route/browser tests | `ops-site/scripts/verify-routes.mjs` blob `1f8e9c1e321c4961fa2844bbc3621e934fd1b267` / `ops-site/tests/browser/public-source-guides.spec.mjs` blob `b7f07446c80e5aaf14b4a872a90c68a9e16b1ccc` | 11旧route＋2記事＋#451 404＋robots/sitemap等をテスト |
| C handoff | `docs/kaigo-ops/safety/2026-10-10-worker-c-medication-fall-implementation-handoff.md` blob `2f9c3003e4839505e22195ce685e8d7f5587bebb` | 末尾の最新追補に新headを反映。冒頭の旧snapshotを最新として読まない |
| D §10（旧） | #475 head `4694ca9ee6ce383be03c0f661baeacb067c5a20d` / ledger blob `a72a7fbf6af813d7c7de38f3a033014c1c9584c3`（本追補前） | 旧A/B、旧C headを監査した履歴。本§11と区別 |
| #451 | 既存draft/unmergedの試作。Cのroute検査では `/tools/medication-safety-preview` が404 | `PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`。EX01/EX02未依頼、HU01承認なし |

**GitHub compareによる差分再検査：** B旧監査head `97389ce1...`→現 `0b192a57...` はB編集文書のみ **+56/-0**（§8等の追補と出典リンク照合）。C旧監査head `ef12b659...`→現 `b33f8b16...` は **C引継ぎ文書だけ +51/-0**。Cの服薬TSX・転倒TSX・CSS・home・sitemap・route/browser testsのblobは§10と全て一致。この7コード/テストblobのリスクテストは**不変証拠として差分再利用**できる。Aの旧 `2849cdc...`→main `b603592...` は§8のB最終版への新採否を含み、**実体を直接読み直した**。A旧B参照が現在も未解決、C転倒未実装、C最新head不明という旧blockerは今回の現状に転記しない。**A/B/C final tupleとしてのソース・編集・コードidentityは確立**、安全上の未確立は別判定。

### 11.2 原典・claim→編集稿→コードの独立照合

**N24（厚労省 2024-11-29 Vol.1332、通知）** `https://www.mhlw.go.jp/content/001574219.pdf`：公式PDFの本文1頁/PDF2頁で2021-03-19旧通知の廃止、本文2頁/PDF3頁で**原則報告対象**（死亡、医師診断後に投薬・処置等の治療が必要な事故）とその他の自治体判断、および第1報の「遅くとも5日以内」**目安**、本文3頁/PDF4頁で**別紙様式の対象サービス**を別々に直接確認。B §2.3の3引用ブロックとC medication `#report` の3表示段落は対象・目安・PDF **#page=3 / #page=2 / #page=4** の近接リンクを保持。B §3転倒報告2段落とC fall `#report` もPDF3/4を保持。**「報告対象≠様式の対象≠各自治体の報告義務・期限」**を維持。後者は `NOT_ESTABLISHED`。

**G25（厚労省 2025年11月 Vol.1436、ガイドライン）** `https://www.mhlw.go.jp/content/001591418.pdf`：公式PDF冊子30頁/PDF33頁を直接視認し、多要因・防ぎ難い転倒・過度制限と身体拘束懸念を確認。冊子32頁/PDF35頁で個別評価とベッド周辺を確認。B §3 F-01/02/03とC fall `#factors / #dignity / #bed` は**一般論・主に介護保険施設向け**に制限され、具体的ベッド柵・機器設定、身体拘束の適法性や保証された予防効果は追加していない。服薬B §2.1/§2.4とC `.sourceGuidePriority / #prevent` は安全優先・施設向け**推奨／事例**として対応し、別施設の効果率や二人確認の全国的法定義務を断定しない。冊子25–26・38–39頁は既存A/D§10の参照と現C表示を照合したが、**本§11で当該全頁を新たに独立実視認したとは主張しない**。

**R17（厚労省掲載2017年高齢者向け住まい研究）** `https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/73_aruteppu.pdf`：Ⅰ編45頁/PDF57頁を直接視認。事業者が別人の薬を服薬させた事例について自己判断の経過観察を避け受診につなげる研究上の推奨。B §2.2第1引用→C medication `#minor` は研究・対象限定と法律上の一律義務**不成立**を近接表示。一般の全サービスへの拡大はなし。

**PMDA** `https://www.pmda.go.jp/safety/consultation-for-patients/on-drugs/0003.html`：公的一般くすり相談ページを確認。B §2.2第2引用→C medication `#minor` は一般相談と医療診断・受診搬送の個別判断を分けている。サイト自身が緊急医療判断を代行する説明はない。

**L211（刑法第211条）** `https://laws.e-gov.go.jp/law/140AC0000000045`、候補revision `140AC0000000045_20260521_507AC0000000039`、API `https://laws.e-gov.go.jp/api/2/law_data/140AC0000000045_20260521_507AC0000000039`：対象revisionのJSON endpointは存在するが、このD監査で**該当施行版の第211条正文全文を読み出して逐条検証できた証拠はない**。検索表示やAの要旨を正文の独立確定に昇格させない。B §2.5の非断定見出し・限定本文がC medication `#law` に再現されていることは**CODE一致のみ**。現行法令の内容・施行版を直接保証する法的審査では **`NOT_ESTABLISHED`**。e-Gov正式正文を同一revisionで直接取得・確認するか、A/Bが法律節の削除を判断し、Cがその範囲を削除してCI・D再監査する必要がある。

**読者向け引用16ブロック**：B §2/§3の候補引用をCの該当実TSX表示と独立に対応づけ、施設中心／住まい研究／国通知／一般相談／非断定の境界、緊急時注意のlead直後配置、出典原文リンク・本文/冊子/PDF通し頁を確認。Markdownのリンク説明・強調・JSXの分割を除いた本文意味差は確認しなかった。**DOMの直接独立実測は行っておらず、逐語表示の保証はコード+Actions browser testsに限定**する。

### 11.3 危険な誤読12ケース：最終版に対する独立差分審査

判定 `PASS_LIMITED` は **B最終本文＋C TSX＋確認済み原典＋該当CIテストの範囲のみ**。実際の人間の誤読率・医療適切性・自治体別法解釈の保証ではない。

| Case / 旧リスク | 最終B / 最終C・直接観察 | 原典・実施方法 | observed / 判定 | 残リスク・修復owner |
| --- | --- | --- | --- | --- |
| **R01** 軽微だから無対応 | B §2.2 R17研究限定、C `#minor` は現場のみの様子見判断を退ける | R17Ⅰ45/PDF57を直接視認、B/C逐語意味比較 | 限定的推奨と正式判断を明記／`PASS_LIMITED` | 現場症例別判断なし、人の理解未確認。E/HUMAN |
| **R02** 全国一律受診義務 | B §2.2は住まい研究を法定義務にしない、C `#minor` も同じ | R17/PDF57・C文面独立確認 | 研究と法律を分離／`PASS_LIMITED` | 他サービス義務は`NOT_ESTABLISHED`。A/B |
| **R03** 医療相談すれば行政報告不要 | B §2.3、C `#report` は手続を分離 | N24本文2/PDF3＋本文3/PDF4直接視認 | 報告対象・第1報5日**目安**・様式対象を区別／`PASS_LIMITED` | 自治体固有の報告要否・期限`NOT_ESTABLISHED`。E/事業所 |
| **R04** 誤薬だけで犯罪成立 | B §2.5非断定見出し＋要旨、C `#law` に同文 | B/Cコード直接比較、e-Gov現行正文の逐条読取未成立 | 誤薬のみの自動犯罪認定は否定。ただし法令正文照合未完／**`BLOCKED`** | **公開前に法律節の削除または正式同版正文の独立確認**。A/B→C→D |
| **R05** 静的案内を緊急手順と誤認 | B §2.1/§3冒頭、C 2記事lead直後 `.sourceGuidePriority` | C TSXのDOM構造・browser source/成功ログを直接確認 | 記事閲覧より安全確保・正式手順等を優先／`PASS_LIMITED` | 実際の事故時の利用・専門職レビューは未実施。E/HUMAN |
| **R06** 施設事例を全サービス義務へ拡大 | B §2.4/§3、C `#prevent/#factors/#bed` 等で主対象を明記 | G25冊子30/32視認、A出典台帳とN24対象差を再照合 | 施設向けと住まい研究を別の出典と表示／`PASS_LIMITED` | 通所・訪問等の独自制度・運用の確認は本件外。A/E |
| **R07** 厚労省監修／専門職承認済み | B用途境界、C両記事scopeで未監修・未審査 | C TSXで表示確認、監査IDはコメント内のみ | 監修済みの誤表示なし／`PASS_LIMITED` | 実在専門職のレビュー`NOT_RUN`。E/HUMAN |
| **F01** 全転倒を防げる／全件過失 | B §3 F-01、C fall `#factors` に反対の説明 | G25冊子30/PDF33直接視認 | 多要因と防ぎ難い事例を確認／`PASS_LIMITED` | 個別事故の過失判定なし。E |
| **F02** 身体拘束の適法性を一律判定 | B §3 F-02、C fall `#dignity` とpriorityが非判定 | G25冊子30/PDF33直接視認 | 過度な制限の懸念だけを提示／`PASS_LIMITED` | 個別の適法性は`NOT_ESTABLISHED`。E/専門職 |
| **F03** ベッド柵・機器・介助の一律指示 | B §3 F-03、C fall `#bed` が一律設定を否定 | G25冊子32/PDF35直接視認 | 本人の状態と周辺環境に限定／`PASS_LIMITED` | 個別機器使用法は本文で扱わない。E |
| **F04** 転倒後の受診・搬送を記事が判定 | B §3冒頭とF-04、C fall priority/報告/scope | N24/PDF3-4とC TSXを独立確認 | 医療・緊急時判断を除外／`PASS_LIMITED` | 実際の救急運用・Android利用未検証。E/HUMAN |
| **F05** 一施設事例で全国的効果保証 | B §3に効果率なし、C fallに事故ゼロ率・効果数値なし | G25施設ガイドの性質、C表示コードとbrowserテストを確認 | 全国的保証を表示しない／`PASS_LIMITED` | 各施設での実効性は実証していない。E |

**要修復ケース=R04（法令正文未確立）。** 11ケースは限定した静的表現レベルで新たな重大な危険断定を認めなかったが、`PASS_LIMITED`を実事故利用・専門職監修・公開承認へ拡張しない。R04の本文は非断定であっても公的法令と接続して法的説明を行うため、直接確認ができない限り安全審査として許可しない。

### 11.4 CI、技術安全、privacy、実測と未実施

**C最新head `b33f8b166628f7c06fb96cc7ccac95a579e24434` のGitHub Actionsを再取得**：全3件 completed/success、各ジョブ・手順もsuccess（旧 `ef12b...` のrunを流用しない）。

| workflow / run | job / step（実測） | 証拠境界 |
| --- | --- | --- |
| [Validate ops site #38046418244](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418244) | job `114196759226` success。npm ci、npm test、Next build、Chromium `npm run test:browser` **15/15 passed**、`npm run verify:routes`、5 tool smokeの各step success。生ログで2記事PASS、5 Issue+5 toolのPASS、#451 404/sitemap/robotsを確認 | PR候補headのCIローカルサーバー。**新本番HTTPではない** |
| [Validate build #38046418248](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418248) | job `114196759098` success。build、metadata/sitemap、production gate verifier compile、key route smokeなどsuccess | 別workflowのbuild検証 |
| [Verify publication readiness integration #38046418246](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418246) | job `114196759065` success。canonical regenerationとbounded publication readinessのsteps success | 既存publication readiness、**記事公開の承認ではない** |

**技術確認の独立範囲：** Cの8 changed pathsを取得し、`verify-routes.mjs`、browser specの期待条件と上記の成功ログを照合。旧11公開route（home＋5 Issue＋5 action tool）、服薬/転倒候補route、#451試作404、robots/sitemap、原典PDF `#page`直リンク、home導線、2記事相互リンク、canonical/OG、390px、キーボードfocus/アンカー、reduced-motion、CSS zoom=2 **proxy**、print mediaとURL表示をコード上とheadless CI上で確認。コード差分の2記事は閲覧専用で、事故状況・患者・薬剤・職員情報の入力欄、新Analytics event、#451 flag有効化、公開registry追加を確認しない。**差分外のサイト全体における不存在まで断定しない**。静的案内の内部claim IDはTSXコメントにあり、画面本文への露出なし。CIログ中の初回localhost接続失敗はサーバー起動待ちのリトライで、後続のrouteチェックはPASS。

**未実施・境界を混同しない：** 手元の `npm ci/npm test/npm run build/npm run test:browser/npm run verify:routes` は `NOT_RUN`（Actionsのみ実測）。独立のページDOMブラウザ手動実測、Android Chrome **native 200%**、スクリーンリーダー実聴、紙印刷、人間の理解テスト、PDF `#page=N` の実ビューア遷移は **`NOT_RUN`**。自治体別義務・施行版L211正式全文照合は **`NOT_ESTABLISHED`**。このD作業ではVercel新deployment、runtime exact SHA・alias、新15/16 URL production HTTP/HTML/DOM、正式post-deploy verifier、deploy-state markerを実行・更新していない（各`NOT_RUN`、marker`UNCHANGED`）。main commitをproduction SHAに読み替えない。

### 11.5 3公開範囲の独立判定／Eへの決定条件

| 公開候補 | Dの独立結論（このexact tuple限定） | Eへの判断条件 |
| --- | --- | --- |
| **①既存服薬本文の改訂** | **`BLOCKED`**：A/B/C最終版の照合とTSX/headless CIは成立。ただしL211正文同一施行版の独立逐条検査は未確立のまま `#law` が公開候補にある。R04未解決。 | **`RELEASE_HOLD`要求**。A/Bが法律節の安全な削除・編集採否を確定しCが最小修正→新head CI→D該当ケース再監査するか、正式同版正文直接確認と危険誤読の再評価を行う。 |
| **②転倒・転落の静的出典記事1件** | **`PASS_LIMITED`**（G25/N24の直接確認済み範囲、B§3→C fall TSX、C exact-head CIのみ）。L211法律節を含まず、12ケース中F01–F05は限定PASS。自治体別運用、実機、原典ビューアは未検証。 | **暫定 `PUBLIC_SOURCE_GUIDE_HOLD`**。Dの条件付き限定審査は完了。Eが人手ゲート、実装の混在、差分の安全な分離、required CI、最終main/本番検証の条件を決めるまで公開不可。 |
| **③非医学的UI（リンク・導線・印刷・回帰）** | **`PASS_LIMITED`**（CコードとActions headless検査のみ）。相互リンク/ホーム/sitemapは①②と混在する。 | **暫定 `RELEASE_HOLD`**。UIだけを公開するならHOLD記事/route/導線/sitemap/医学・法律本文を排除した**新規の安全な実体PR**、そのheadのCIとD独立再審査を要する。C #465の8ファイルを一括mergeしてはならない。 |

**総合：`PARTIAL_WITH_GAPS`（D監査の実行・記録は完了、公開承認ではない）。** 最終A/B/C identityの旧版問題は解消した。一方、①服薬のR04は`BLOCKED`。②転倒/③UIの`PASS_LIMITED`は**新productionのPASSではない**。Eは**3範囲を独立にGO/HOLD判断**し、HOLDを含む8ファイルを一括統合しないこと。実現可能な公開範囲がなければ全HOLDを選ぶ。

**次owner:** A/B（L211正文の同版確認または法律節削除の採否・文面）→C（その修正・必要な分離と新head CI）→D（変更後の該当ケースを再受入）→E（範囲別GO/HOLD、必要時のみmerge・Kaigo Ops専用新deployment・exact runtime/alias・15/16 URL HTTP/DOM・正式deploy-state）。#451、異食、誤嚥・窒息は公開せず、実在専門職への依頼もしていない。既存5 Issue/5 tool・no new analytics・no incident inputを保持する。



---

## 12. 2026-10-11 D_ISOLATION_REACCEPTANCE_PREFLIGHT — 新候補未成立時点の独立差分監査と再受入保留

**checked_at:** 2026-10-11 06:28 JST（GitHubおよび公式e-Govの読取。時刻は監査時点の目安）。**Wave:** Library `/Kaigo Ops/Work Instructions/2026-10-11_medication_legal_section_resolution_fall_guide_isolation_independent_reacceptance_and_conditional_release_wave_instructions.md` §6。**性質:** 新しい実装候補の最終受入証明**ではない**。A/B/Cの新しい保存後の実体、独立分離PR、およびそのheadでの3 CIがまだ存在しない時点の差分確認とfail-closedのゲート記録。§11の確定済み審査をやり直さず、不変証拠のみ限定的に継承する。DはA/B/Cの文書・コードを修正せず、merge/production/deploy-stateを操作しない。

### 12.1 fresh-read identity・新候補の有無

| 対象 | GitHubで再取得した正確な版／状態 | このWaveに必要な差分・不足 |
| --- | --- | --- |
| main | `6346300ce6300714646b588c08159f075987b32f` | 前E #478までdocs-only統合済み。runtime SHAではない。 |
| A本体 | mainの出典台帳 blob `b603592b3b91f303cf021af283b953bd8b9e05d1`、§8 | 新たな法令採否追補なし。MED-A07の同版正文直接照合は未確立、候補掲載にとどまる。 |
| B #466 | `open/draft`、head `0b192a57674681952afcc4766d4cd03ce523e331`、編集稿 blob `4549faac7651b6c3f88291740548e179e74e037a` | 前D§11と同じ。§2.5に刑法第211条の要旨・直接リンクが**残る**。削除・限定維持の**新確定稿は未取得**。 |
| C #465 | `open/unmerged`、head `b33f8b166628f7c06fb96cc7ccac95a579e24434`、8 changed paths | 旧同一版の混在PR。転倒単独／服薬単独／UI単独の新独立PRは、2026-10-11 06:28 JST時点のopen PR一覧には見つからない。**この8ファイル一括merge不可**。 |
| C旧候補の主要blob | medication `f3415366187b47c8a6a93a378f3f223e0971d181`、fall `de66e2dfcb0985864be230049ecea44612fd3b05`、home `ca0113d6de512236acb87c5346bc6d69bcd8b26e`、sitemap `a85ad4d8069e0d0f4bde400fbda7dfaba2f44175`、browser `b7f07446c80e5aaf14b4a872a90c68a9e16b1ccc` | いずれも前D§11のblobと一致。新候補の変更blobとして誤表示しない。CSS `f2a43acf8f062560db9fbf3aa2fffc31e684ed58`、route script `1f8e9c1e321c4961fa2844bbc3621e934fd1b267`も前§11の記録値であり、分離新版の回帰証拠ではない。 |
| 現行main服薬 | `ops-site/app/guides/medication-incident-sources/page.tsx` blob `782a1f53c635997817faf46bfe2f4e63721482c2` | #465の服薬改訂blobとは**異なる**。転倒単独分離時には必ずこのmain blobを保持する。なお現行main記事にも旧 `#law` と刑法211条の記載があるため、分離のみでサイト全体の法令節が消えるとは言えない。 |
| D正本 | main同台帳 blob `ebc71f6ebd8424d682856fd2bc37c6c376318f09`、§11 | 前D 12リスク中11 `PASS_LIMITED`・R04 `BLOCKED`。この§12は候補未成立の状態確認と次の再監査条件。 |
| #451 | `open/draft/unmerged`、head `2dd0e260d0922e18d003905f4a7edf42560f640c` | `PREVIEW_ONLY / NOT_PUBLIC`。旧C検証はローカル404だが、本Waveの本番HTTP実測ではない。 |

**旧C CIの再取得:** #465 head `b33f8b...` のActionsは `Validate ops site` run [38046418244](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418244) / job `114196759226`、`Validate build` run [38046418248](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418248) / job `114196759098`、`Verify publication readiness integration` run [38046418246](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38046418246) / job `114196759065`、全て`completed/success`。各jobの関連stepsもsuccessを取得した。**いずれも新しい独立PR/headのCIではない**。新候補のrun/job/stepは`NOT_RUN`（候補未成立）。

### 12.2 危険な誤読と修正影響の独立切り分け

| 検査範囲 | 今回見た差分・コードの観察 | Rケース／判断 |
| --- | --- | --- |
| 法令節（服薬改訂） | B §2.5は「服薬の間違いだけで、刑事責任が決まるわけではありません」と刑法211条の要旨およびe-Gov URLを保持。C #465の服薬TSX `id="law"`、目次 `href="#law"`、`penalcode` source、刑事責任文、metadata内「法的責任」が残存。削除が実装された版は**存在しない**。 | **R04 `BLOCKED`継続**。公式e-Gov画面と候補API URL（`140AC0000000045_20260521_507AC0000000039`）へ再アクセスしたが、施行時点を確定した**同一版第211条正文全文を抽出・逐条検証する証拠は得られず**、`NOT_ESTABLISHED`。A/B/Cが改訂を固め、法律節を維持するならD自身の全文直接照合、削除するなら見出し・目次・本文・citation/source・相互リンク・metadata・testsの削除差分とrendered HTMLを独立再検査する。 |
| 旧11ケース | A/B・C既存候補のblobに§11以降の変更なし。出典→B→Cの限定一致の評価範囲は同じ。 | R01–03、R05–07、F01–05は**旧§11 `PASS_LIMITED`を当該旧tupleにのみ維持**。新しい公開候補へ受入を継承しない。対象・断定の強さに変更があれば該当ケースを差分再監査する。 |
| 転倒単独候補 | #465の転倒TSXはG25の施設中心・多因子、過剰制限、ベッド周辺、N24の報告対象・様式対象・第1報5日目安を分記し、医療・身体拘束・刑事責任の個別判定をしないコード。ただし`/guides/medication-incident-sources`へリンクする。専用の新しいmain起点PRとそのdiffは未取得。 | F01–F05の旧限定監査は参照可。ただし`fall page / source / home / sitemap / CSS / browser tests / legacy medication unchanged`の**新候補identityは`NOT_ESTABLISHED`**。main服薬をblob同一に保ち、相互リンクが**既存のmain服薬**だけを指すこと、CSSの共有影響、旧11ルートを再検査するまで独立受入不可。 |
| 非医学的UI | #465ではCSS/home/sitemap/routes/browser testsが服薬改訂と転倒新記事の両方に結合。browser specには#465服薬版の目次6リンク、リード直後のpriority、直接PDFリンク、転倒への相互導線等を期待するテストがあり、main旧服薬に無修正で移植できるとは限らない。 | UI単独の実体と新headは`NOT_ESTABLISHED`。HOLD記事・法令節・未公開routeを含まない差分、既存11ルート、legacy服薬、keyboard/focus、print、390px、reduced motion、CSS 200% proxy、canonical/OG、sitemap、privacyを新headで検証した場合だけ再受入候補となる。 |
| プライバシー・#451 | #465既存差分にincident/患者/薬剤の入力フォームや新Analyticsイベント・秘密情報・公開flagを追加する証拠は前§11で見出されていない。#451はGitHub上draftで未統合。 | 新しい候補が未成立のため**新候補に対するPASSは出さない**。現行本番の#451 404・外部HTTPを今回再実測できなかったため`NOT_RUN`、テストの旧CI成功と区別。 |

**独立観察手段:** GitHub main/PR API、A/B/C/D各固定blobとC旧PRの差分、CI run/job/step、e-Gov公式URLのアクセス可能範囲。**今回独立実測していないもの:** 新候補のブラウザDOM・ローカルnpm/Playwright、Android Chrome native 200%、実スクリーンリーダー、紙印刷、実PDF viewer `#page=N`、人間の理解テスト、専門職レビュー、自治体別の報告義務／期限、Kaigo Ops新Vercel runtime/alias、正式post-deploy verifier、deploy-state進行。各`NOT_RUN`または`NOT_ESTABLISHED`とし、旧Cのheadless結果を実機やproductionに転用しない。

### 12.3 公開対象別のD判定（新候補未成立、Eへ）

| 範囲 | **このWaveの新候補に対するD判定** | 受入再開の必要条件 |
| --- | --- | --- |
| ①既存服薬本文の改訂 | **`BLOCKED / RELEASE_HOLD`**。R04が残り、削除または正文同版直接確認の新A/B/C版は未成立。 | A採否→B保存後head/blob→C服薬のみの変更blob/PR→そのheadで3 CI（run/job/step）→R04の本文・原典・表示のD独立再評価。既存mainの法律節を変更する場合、その影響も審査。 |
| ②転倒・転落の静的記事 | **`PARTIAL_WITH_GAPS / PUBLIC_SOURCE_GUIDE_HOLD`**。旧#465のF01–F05は`PASS_LIMITED`だが、**分離PRの新head受入は未実施**。 | main起点のfall専用PR、main服薬blob同一、必要CSS/home/sitemap/routes/browser testsだけのdiff、G25/N24原典とF01–05、旧11route/服薬・#451回帰、新head 3 CI、Dのexact-head受入。 |
| ③非医学的UI | **`PARTIAL_WITH_GAPS / RELEASE_HOLD`**。独立UI差分・headなし。 | 本文/route/HOLD導線を含まない有意義なUI専用PR（成立する場合のみ）、旧11route/服薬不変、SEO/keyboard/print/privacy回帰、3新head CIとDの独立受入。 |

**全体：`PARTIAL_WITH_GAPS`、Dの開始時点の独立prefight記録のみ完了、**新候補の最終`D_ACCEPTED`は **`NOT_ESTABLISHED`**。この記録自体は公開許可ではなく、#465の8 changed paths一括merge・production・deploy-state更新は認めない。D§11の旧合格を別PRへ貼り替えることも禁止。

**Eへの引継ぎ:** 新A/B/C head・blobs/候補差分・CIが現れた後にこの§12を最終合格へ読み替えず、**実体ごとにDが追加再審査**する。新候補のD受入がない範囲はEでHOLD。A/BがR04削除・法律根拠を決める、Cがfall/服薬/UIを安全に分離する、Dが該当部分を独立再評価する、EがGOした対象のみmerge/本番検証する。新production HTTP/DOM・Vercel/deploy-stateの値について本D作業は`NOT_RUN`、marker操作なし。

