# Kaigo Ops — 公的出典ガイドの本番確認・事故防止情報拡充：Worker E 統合判定

- 判定日：2026-10-09 JST
- 対象指示書：Library `/Kaigo Ops/Work Instructions/2026-10-09_public_source_guides_release_verification_and_accident_prevention_expansion_wave_instructions.md`
- Repository：`Josh-Temple/kaigo-rules`、main参照点：`9f6e0a4f2c841f5f55840f3ae8ab7399397c3207`（A/D監査文書統合後。**本番runtime SHAではない**）
- 対象：静的な公的出典情報ページ。回答選択型の服薬安全試作は**別の安全・人間承認ゲート**に従う。
- 総合：**PARTIAL_WITH_GAPS**
- 新規静的記事：**PUBLIC_SOURCE_GUIDE_HOLD**（テーマごとに下記判定）
- 既存服薬ガイドの本番実閲覧：**PRODUCTION_NOT_VERIFIED / FRESH_HTTP_NOT_ESTABLISHED**
- 選択式試作：**PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED**
- 本E実行の新規production release：**なし**。deploy-stateの更新：**なし**。

## 1. 取得した正本と統合の実績

| 区分 | exact対象・観察 | 判断 |
| --- | --- | --- |
| main | 実行開始時 `ab457495632032e3640f398ddbd4b8cbdda319f5`。A #467およびD #468の監査文書を通常PR mergeし、統合後main `9f6e0a4f2c841f5f55840f3ae8ab7399397c3207`。 | 監査の記録のみ更新。Webアプリ本文・機能は未変更。 |
| A [#467](https://github.com/Josh-Temple/kaigo-rules/pull/467) | head `b456de2c523649c31cbaa332fdaaac21d2573836`、source ledger blob `1ee8dc07a2d7e01d34e1d83ee666bcadb1d778e3`、build/公開整合CI成功。merge commit `96a77bffeb908e65160d1410a56084fb7bab0eb1`。 | **PASS_LIMITED**／一次資料の出典・主張対応だけを採用。医療判断・本番確認の認定なし。 |
| B [#466](https://github.com/Josh-Temple/kaigo-rules/pull/466) | draft head `e58adc57410a8377d37dfc857e99eecc9a1d7487`。編集草稿 blob `06fd8b627fa12fb1be0b0a484ff1203d3e9e7712`、文書CI成功。 | **DRAFT / HOLD**。A採否前と記載された暫定草稿。Aの最終推奨・主張IDを反映した最終版ではないため未merge。 |
| C [#465](https://github.com/Josh-Temple/kaigo-rules/pull/465) | head `8e18f9bd54662d246081f4620728ba8c8ff38665`。変更は `ops-site/app/globals.css`、既存服薬ガイド `page.tsx`、新Playwright specの3ファイル。Actions `37934959505` ops／`37934959236` publication／`37934959246` build、いずれもsuccess。 | 目次、印刷、390px、CSS zoom代替試験の改善は確認。ただし **DがこのC headのUI/diffを独立再確認した証拠なし**。未merge／production未反映。 |
| D [#468](https://github.com/Josh-Temple/kaigo-rules/pull/468) | head `281464ed0c6daaca16bfde29b8bdae193b4f9ccf`、独立監査文書、文書CI成功。merge commit `9f6e0a4f2c841f5f55840f3ae8ab7399397c3207`。 | **PARTIAL_WITH_GAPS**。7件の誤読ケース、施設主対象の注意、HTTP未確立を記録。DはC最新版やB公開最終文面の独立承認ではない。 |
| 旧試作 [#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) | draft/open/unmerged head `2dd0e260d0922e18d003905f4a7edf42560f640c` を再確認。 | **NOT_PUBLIC**。一般公開・registry追加・feature flagの本番有効化禁止。 |

A/Dのmergeは監査文書だけ。#466/#465/#451の内容はmainへ入れていない。Cの自動試験成功をDの独立本番ブラウザ成功と扱わない。

## 2. 既存服薬事故ページの文言評価

基準となる公開ページソース：`ops-site/app/guides/medication-incident-sources/page.tsx` blob `782a1f53c635997817faf46bfe2f4e63721482c2`、資料台帳 `docs/kaigo-ops/safety/2026-10-09-medication-incident-public-source-guide-evidence.md`。

- **維持可能な範囲（A/Dの出典照合による限定的判断）**：2017年の高齢者向け住まい調査研究の受診推奨を全国法令に一般化しないこと、2024年通知の第1報5日を「目安」と表記すること、刑法211条の成立を「誤薬だけで自動的に確定」としないこと、専門職の実レビュー未実施を表示すること。
- **是正候補 P1**：法的責任の見出し「重大な結果」は刑法211条の文言「人を死傷させた」と比べて狭く誤読される可能性がある。A/Bの案を突き合わせ、法的断定・恐怖訴求を避けた見出しに修正してD再確認。本文の現行断定が直ちに犯罪成立を示すと評価したものではない。
- **是正候補 P1**：2024年事故報告通知の対象サービスとその他サービスの扱いを、本文の報告節でも読める位置に示す。自治体の独自運用・短い期限、2021年旧通知廃止を混同しない。全国共通の個別報告要否・期限をサイトが判定しない。
- **原典の限界**：厚労省2025年施設中心ガイドライン／2017年住まい研究事業／2024年通知／PMDA一般相談案内／刑法211条は文書類型が異なる。Aによればe-Govの動的な条文本文は直接抽出できず検索表示で要旨照合した。Eは法令の最新正文を独自に再検証したとは認定しない。単一施設事例から効果数値、職種の一律義務、全サービス適用を導かない。
- **未反映**：上の文面修正は案であり今回の本番ページには未実装。C #465も本文の医学・法的主張は変更していない。

## 3. 追加3テーマの公開判定（A/B/C/Dの依存関係）

| テーマ | Aの限定根拠 | B／C／Dの差分と不足 | E判定 |
| --- | --- | --- | --- |
| 転倒・転落 | `FALL-01/02/03`：施設向け厚労省2025年ガイドライン冊子p30・32、PDF通し33・35頁の範囲で `SOURCE_SUPPORTED`。事例の因果効果は不可。 | Bには`F-01～04`草案があるがA正式採否を反映していない。C新記事未実装、D最終HTML未監査。 | **PUBLIC_SOURCE_GUIDE_HOLD** |
| 誤嚥・窒息 | `ASP-01/02`：同冊子p34–35、PDF37–38頁。専門職評価・共有・個別検討という一般的注意に限る。 | B`S-01～04`草案。具体的な食形態・救命処置・嚥下判定は除外。C記事と同一版D監査なし。 | **PUBLIC_SOURCE_GUIDE_HOLD** |
| 異食（広い意味の誤飲と同一視しない） | `ING-01/02`：同冊子p36–37、PDF39–40頁。物品管理・尊厳とのバランスに限定。 | Aは先行候補に推奨したがBの正式記事草稿がなく、C実装・D最終レビューなし。毒性・誤飲処置は除外。 | **PUBLIC_SOURCE_GUIDE_HOLD** |

**差異**：Aが先行を推奨した組合せは「転倒・転落＋異食」、Bが草稿にした組合せは「転倒・転落＋誤嚥・窒息」。優先候補は未確定。Aの主張採否、Bの改訂、Cの完成コード、Dの同一head独立審査が一致するまで新記事を公開しない。最大2件という上限は維持する。

## 4. Vercel productionと実到達性を分離

- 対象project：`kaigo-ops` / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`（Kaigo Rulesの別projectではない）。
- Vercel production list：最新 `dpl_9r41Hq62ViHcU2YAtMyuoMGmqUbu`、`READY`、target `production`、GitHub `Josh-Temple/kaigo-rules`、runtime SHA **`ffd70abb5723e950a0a1036795f28da31614a1f3`**。
- Vercel alias exact lookup：`ops-site-pi.vercel.app` → 同 deployment ID。**platform identity / alias assignment は確認**。
- `deploy-state/kaigo-ops`：branch先頭は **`e49e770a970e541d2ad95204ad277eca89a485d3`**。前Waveのmarkerであり、新deploymentを正式なcontractでHTTP検証したmarkerには進めない。
- **本Eの直接HTTP試行**：`https://ops-site-pi.vercel.app/guides/medication-incident-sources` を実行環境のPython HTTPクライアントでGET → `NameResolutionError: Temporary failure in name resolution`。Web経由の同URL・`/robots.txt`も取得不能。**HTTPレスポンス未取得であって404・5xxと認定しない**。
- **HTTP実測判定**：home + 5 Issue + 5 action tool（計11）、既存服薬ガイド、試作404、robots、sitemap、canonical、OG、出典アンカー・原文リンク＝**FRESH_HTTP_NOT_ESTABLISHED**。ソース/CI上のassertionは実URLのステータス測定と別。
- **実ブラウザ**：production 390px Android Chrome、native zoom 200%、読み上げ、キーボード、印刷実操作＝**NOT_RUN**。CのChromium localhost CIとCSS 200% proxyを実機ブラウザ成功と呼ばない。
- deploy verification contractの必須条件（同一deployment ID・READY・exact runtime SHA・alias・全11 route HTTP 200の実証）が**揃わない**ためmarker更新禁止。DNS到達性を改善した別のネットワークで実測する。復旧可否は本判定では確約しない。
- production変更：**本Eでは新規deployment作成、promote、alias切替、preview flag変更を実施していない**。

## 5. 次の作業と責任分担

1. **本番HTTP P0（E／ネットワーク到達可能な実行環境の担当者）**：対象alias／deploymentの両URLから、既存11+服薬ガイド・非公開試作・robots/sitemapを取得し、status/HTML/canonical/出典リンクを保存。READYとURL到達を別々に記録。別途390px実ブラウザ、native 200%、読み上げ／印刷を実査。全部揃うまでは`PRODUCTION_NOT_VERIFIED`。
2. **既存服薬記事の文言 P1（A→B→C→D）**：刑法211条の見出し、2024年通知のサービス対象・自治体運用の位置、資料類型・原典への直接リンクを最新版で修正。個別処置は増やさない。C #465の変更についてDがexact head/diffとページ・テストを独立再監査してから統合判断する。
3. **新記事 P1（A→B→C→D→E）**：Aの`FALL/ASP/ING`をBの`F/S`主張と文単位に対応させ、採用テーマを最大2つ選ぶ。Aの支持しない断定を削除。C静的記事、CI、Dの同一版監査が揃ったものだけEが限定的GO判定する。
4. **旧服薬安全点検試作（独立HOLD）**：[#451](https://github.com/Josh-Temple/kaigo-rules/pull/451) はdraft・未マージ、`MEDICATION_SAFETY_PREVIEW`本番無効。`EX01/EX02=NOT_REQUESTED / EXPERT_REVIEW_NOT_DONE`、`HU01=HUMAN_APPROVAL_NOT_DONE`。今回の方針に従い、専門職の探索・依頼・送付・日程調整・予定済タスク化はしない。
5. **既存の運用を維持**：公開Issue 5／action tool 5、Issue 6「収支・コスト構造」候補、Search Console `UNKNOWN`、Analytics既存pageview schema、2026-10-21前後～11-04前後の観測レビューは変更しない。データ収集eventも追加しない。

## 6. 証拠区分と終端

- **確定**：A/D監査の提出・main統合、B draftとC open、C head Actions 3件成功、Vercel production READYとaliasの対応、`deploy-state`旧SHA、旧試作のdraft未統合。
- **別の担当者が報告した限定証拠**：A/Dの主張と一次資料の照合・7つの誤読検査。Eはその内容・対象と不一致を統合判断したが、専門職や実利用者による検証ではない。
- **未確立**：本番全route HTTP、UI/Android/200%/読み上げ/印刷、C最新版のD独立再検査、新規記事3テーマのA→B→C→D完成、法令・自治体差の全サービス現行性。
- **不実施**：新記事merge・release、C #465 merge、B #466 merge、C #451 merge、Vercel promotion、deploy-state更新、EX01/EX02依頼、HU01承認。
- **公開上の区分**：既存の静的服薬出典案内はすでにGitHub mainとVercel READYに反映されているが、今回の実HTTP到達・閲覧は未認定。新記事はすべてHOLD。個別医療判断を行う選択式試作はNOT_PUBLIC。

**公的資料の出典があること、公的機関による監修や医学的な対処方法の承認ではない。**
