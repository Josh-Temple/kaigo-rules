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
