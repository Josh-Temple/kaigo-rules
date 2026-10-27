# 地域密着型特養 — Research Mesh A5/A6のみの隔離統合・根拠台帳

- 目的：Research Mesh PR #567 の **45候補**から「通常型の準用」「ユニット型の準用」の **2件だけ**を現行main基点でDraftに採用する。
- 元PR：https://github.com/Josh-Temple/kaigo-rules/pull/567
- 元候補固定HEAD：`c987613441ded6d9e9814e85e7103543b20790f0`
- 元候補JSON Git blob：`bdaeb14b44d2faebd8b9d6193cef874dba0bed71`
- 基準main：`ae39c263948c8ec40c46f3748cbfb57250a28e6b`
- 基準データGit blob：`c20c5568d176a74d0260cde25f32db5af03315bf`
- メッシュ元原本ZIP：`libfile_e6ecd2d1280481918a85ffc0ac017908`; SHA256 `05fe2930af084099b2043311f4c35ea475cab645226d112b025e866cbf525e6e`
- 状態：`DRAFT_CANDIDATE_ONLY` / `D_HOLD_NO_MERGE` / `NO_PRODUCTION_RELEASE`。
- **Research Mesh公式Control PlaneのNO_GOは変更しない。**

## 独立して一次資料照合した事実（確認範囲限定）

厚生労働省「指定地域密着型サービスの事業の人員、設備及び運営に関する基準」（平成18年厚生労働省令第34号）の公式掲載本文を確認。

- **原文・第3条の11第1項**：定期巡回・随時対応型訪問介護看護の提供開始に際し、要介護認定の申請が既にあるかを確認し、ない場合に必要な援助を行う内容。
- **第157条（通常型）**：この原文を地域密着型介護老人福祉施設へ準用し、原文の「提供の開始に際し」を含む所定文言を、独立に「入所の際に」と読み替える。
- **第169条（ユニット型）**：同じ第3条の11の原文から、独立に「入居の際に」と読み替える。**第157条で一度「入所」に読み替えた結果をさらに「入居」に再読替えするものではない。**
- **残留する不確実性**：厚労省掲載ページの該当文面との限定一致は確認したが、全改正附則、2026-10-28施行版、自治体条例、個々の指定/併設施設への適用、運営解釈通知・Q&A、具体的な援助手続は全件独立確認していない。

公式根拠：https://www.mhlw.go.jp/web/t_doc?dataId=82aa7858&dataType=0 （同頁の第3条の11、第157条、第169条）。
過去のD判定台帳：`/Kaigo Rules/Wave Outputs/2026-10-26_kaigo_pr568_independent_acceptance_browser_release_remaining_mesh/C_remaining_45_candidate_triage.json`。

## 統合の境界・法的取扱い

1. **2件の要件ID `mesh-b-a5` / `mesh-b-a6` のみ**を `services.community-elderly-facility.chapters.applicability.rule_sections` に追加。元PR #567から残る43件の指定・加減算・基本報酬の要件、A1〜A4・A7/A8の不採用候補は含まない。
2. 読者向け見出しと適用範囲を通常型/ユニット型で明確にし、請求関連の紛らわしい文言を説明から除去。**条文対応以外の義務・資格・金額を生成しない。**
3. 要件 `verification_state='EVIDENCE_GAP'`、出典 `SOURCE_CANDIDATE_UNVERIFIED` を厳守。公式文書を今回部分確認できても、候補オブジェクトにはURLや確認日・格上げは書き込まず、状態を偽らない。
4. 他584章を無変更。対象章の元 `paragraphs`、`checkpoints` と全既存項目は変更なし。検証器の `RULE_TARGETS` に **applicabilityだけ**を追加。
5. 39サービス585章・459旧Mesh候補・原文フィールドの不変性、2件以外の導入禁止、施行版の留保を `test:handbook` の回帰テストで検査する。
6. スコープを狭く保つため、**現在の読者第一PR #570とは独立**のDraft PRでD受入まで保留。#567の一括マージ、mainへの直接push、本番公開、Research Mesh Pilotの権限変更は実施しない。

## 受入条件

- 追加要件に対する固定HEADの全GitHub Actions CIと手引生成・安全性・39/585/459保全検証。
- 第157・169条の施行日・最新法令、指定権者の条例、具体的援助の適用・併設施設を人手で独立照合。
- 読者向け表示/noindex/SSOと手機・狭幅の実Chrome確認。
- 同一最終HEADの独立D `ALLOW_MERGE`。それまでは *Draft/HOLD*。
