# Worker C — 同一版コード引継ぎ（2026-10-10）

- 対象PR: #465（未マージ・E判定待ち）
- 対象基点: C head `77eb4b391ac722adc1a34024e6c7a33b35179949`、base tree `bba9b7d274355df07535a38ec4c132b9dccebb14`
- 文章正本: B PR #466 commit `97389ce1538978abadcf4e2618493b7258995f27`、編集稿blob `1394df30751e408e997524e431a99bf696e52fe9`（§2, §3, §7固定表）。§7で旧通知の廃止はPDF2頁への独立直接リンクを要求するため反映。
- 出典正本: A統合済み#470、`docs/kaigo-ops/safety/2026-10-09-accident-prevention-public-source-claim-audit.md` blob `7f373c396f9358e0179021f09d95cb2698ce9b1f`（§6）
- 新記事route: `/guides/fall-prevention-sources`。
- Cは独立した出典採否・医学／法的判断・専門職審査を行わない。A/B変更が生じた場合は差分を再照合してDを再実施する。

## B確定文章→表示の追跡表

| B原稿 | C表示コード | A主張 | 直接参照 | 備考 |
| --- | --- | --- | --- | --- |
| §2.1 最初の安全注意 | medication page / lead直後 `.sourceGuidePriority` | MED-A01/A08 | G25 冊子25–26、PDF28 | サイトの用途境界 |
| §2.2 研究推奨・PMDA | medication page `#minor` | MED-A02/A03 | R17 I編45/PDF57、PMDA | 全サービスに義務化しない |
| §2.3 事故報告・様式対象 | medication page `#report` | MED-A04/A05、X-02 | N24 本文2–3/PDF3–4 | 様式の対象と報告義務を区別 |
| §2.4 再発防止 | medication page `#prevent` | MED-A06 | G25 冊子38–39/PDF41 | 施設中心の例示 |
| §2.5 刑法 | medication page `#law` | MED-A07 | e-Gov 刑法211条 | 正文全文直読はA/D未確立、掲載判断HOLD |
| §3 リード・安全注意 | fall page hero | FALL-01/02/03、X-01/02 | G25、N24 | 個別事故判定禁止 |
| §3 F-01 | fall page `#factors` | FALL-01 | G25 冊子30/PDF33 | 効果率・過失断定なし |
| §3 F-02 | fall page `#dignity` | FALL-02 | G25 冊子30/PDF33 | 身体拘束の個別法的判断なし |
| §3 F-03 | fall page `#bed` | FALL-03 | G25 冊子32/PDF35 | 機器設定の指示なし |
| §3 F-04 | fall page `#report` | MED-A04/A05、X-02 | N24 本文2–3/PDF3–4 | 事故報告判定なし |

## 検証ゲート

- PR latest C head、各blob、Actions CI、Playwrightの終了結果は新commit後に再取得して追記。旧head `77eb4b391ac722adc1a34024e6c7a33b35179949`のPASSを新headのPASSとしない。
- ローカル `npm ci`、`npm test`、`npm run build`、`npm run test:browser`、`npm run verify:routes`：このconnector環境では実行しておらず、`NOT_RUN`。GitHub Actionsを別に確認する。
- 機械検証：旧11ルート、2記事、preview default 404、robots/sitemap、canonical/OG、390px、keyboard、CSS 200% proxy、reduced-motion、印刷CSS／URL、入力非追加。機械結果はActionsと別に照合。
- Android実機・native 200%、人による読み上げ・印刷現物、専門職レビュー：`NOT_RUN`。
- #451 preview/flag、既存5 Issue/5 tool、Analytics event、公開registry、deploy-state、productionは変更しない。
- 本PRはEの公開承認ではない。Dによる**このPR最新headとB/A blobの同一版独立安全審査**まで`RELEASE_HOLD`／`PUBLIC_SOURCE_GUIDE_HOLD`。


---

## 2026-10-10 C追補 — 現行8ファイル実体と検証境界（本Wave）

**本節が上記「対象基点 77eb4b...」の記載を更新する。** 旧headは履歴であり、本節の検証対象ではない。対象指示：`/Kaigo Ops/Work Instructions/2026-10-10_medication_fall_final_alignment_independent_safety_reaudit_and_staged_release_wave_instructions.md` §5。以下のコード・テストSHAは**追補前のC実装head**からGitHubでreadbackした値。この文書の更新commitは別途PR metadataから取得し、自己参照する最終head SHAをこの本文に推測記載しない。

- **取得時main**：`9dd655fcbd2a37c19d5d8b77606d75149105434d`。C実装head `ef12b659bc9fca43df4c7ebd15b9cf5471dbcecd` はmainとdiverged（ahead 12／behind 13、共通祖先 `ab457495632032e3640f398ddbd4b8cbdda319f5`）。PR #465：open、non-draft、mergeable=true（取得時点。将来の統合成功は未保証）。
- **A #474**：head `650bb9bdf3522f263c03d410ccd051468eada922`、台帳blob `2849cdc53f3117c908cb6331b0946bdb2aedb80c`。§7のB参照は旧head `5df748a...`／旧blob `16915a...` のまま。**A→B最終版の確定突合は未完了**。Aの本Wave最終採否が新たに出るまで、Cが出典採否を代行して確定しない。
- **B #466**：draft、head `97389ce1538978abadcf4e2618493b7258995f27`、編集本文blob `1394df30751e408e997524e431a99bf696e52fe9`（§2、§3、§7）。CのTSXにある§2と§3の**読者向け引用16ブロック**を、Bの引用文からリンク説明を除き、Markdown強調・JSX表示タグ・空白を正規化して静的照合し、**16/16一致**。これはsource-code逐語照合であり、ブラウザDOM実測やAの再採否／D独立承認ではない。Bの旧記載「Cには未実装」は履歴情報であり、以下のC版では**既存服薬の修正と転倒新routeが実装済み**。

### 追補前Cコード・検証ファイルのGitHub blob（全8 changed paths）

| changed path | blob SHA（C実装head `ef12b659bc9fca43df4c7ebd15b9cf5471dbcecd`） |
| --- | --- |
| `docs/kaigo-ops/safety/2026-10-10-worker-c-medication-fall-implementation-handoff.md` | `3ce16c69c89af5f471ae116947cb147c033b3cf4` |
| `ops-site/app/globals.css` | `f2a43acf8f062560db9fbf3aa2fffc31e684ed58` |
| `ops-site/app/guides/fall-prevention-sources/page.tsx` | `de66e2dfcb0985864be230049ecea44612fd3b05` |
| `ops-site/app/guides/medication-incident-sources/page.tsx` | `f3415366187b47c8a6a93a378f3f223e0971d181` |
| `ops-site/app/page.tsx` | `ca0113d6de512236acb87c5346bc6d69bcd8b26e` |
| `ops-site/app/sitemap.ts` | `a85ad4d8069e0d0f4bde400fbda7dfaba2f44175` |
| `ops-site/scripts/verify-routes.mjs` | `1f8e9c1e321c4961fa2844bbc3621e934fd1b267` |
| `ops-site/tests/browser/public-source-guides.spec.mjs` | `b7f07446c80e5aaf14b4a872a90c68a9e16b1ccc` |

### 主張／編集段落 → C表示位置・直接根拠（コード確認）

| B段落とA主張 | C TSX表示位置 | 原典・冊子／PDF通し頁 | 確認 |
| --- | --- | --- | --- |
| §2.1 MED-A01/A08 | 服薬 `.issueHero .sourceGuidePriority`、lead直後 | G25 初動25–26／28–29 | 逐語一致。用途境界は編集上の注意 |
| §2.2 MED-A02/A03 | 服薬 `#minor`、R17/PMDA各原文へ直接リンク | R17 Ⅰ編45／57、PMDA更新型案内 | 逐語一致。研究推奨と一般相談に限定 |
| §2.3 MED-A04/A05/X-02 | 服薬 `#report`、N24 PDF `#page=3/2/4` | N24 本文2–3／PDF3–4、旧通知廃止は本文1／PDF2 | 逐語一致。報告対象と様式対象と5日目安を区別 |
| §2.4 MED-A06 | 服薬 `#prevent` | G25 冊子38–39／PDF41–42 | 逐語一致。施設向け例示、効果率を断定しない |
| §2.5 MED-A07 | 服薬 `#law` | L211 e-Gov（2026-05-21施行版全文直読未確立） | 見出し・限定本文が一致。個別刑事責任を判定しない |
| §3リードと緊急注意 | 転倒 `.issueHero`、lead直後 | G25施設中心／サイトの用途境界 | 逐語一致。個別診断等をしない |
| §3 F-01/02/03 | 転倒 `#factors`／`#dignity`／`#bed` | G25冊子30／PDF33、冊子32／PDF35 | 各本文逐語一致。身体拘束・機器設定の個別判断なし |
| §3 F-04 MED-A04/A05/X-02 | 転倒 `#report`、N24 PDF `#page=3/4` | N24本文2–3／PDF3–4 | 2段落逐語一致。自治体・サービス別義務は未確立 |

### exact実装headのCI（2026-10-10 UTC実行ログの再取得）

| workflow/run | job | 主な成功ステップ／証拠境界 |
| --- | --- | --- |
| Validate ops site / [38007012548](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012548) | `build` job `114078018376` success | `npm ci --no-audit --no-fund`、`npm test`（20 pass）、Chromiumを導入、`npm run build`（2記事route生成）、`npm run test:browser`（15件を実行・job success）、`npm run verify:routes`（服薬・転倒、#451 404、sitemap/robots、既存5 Issue/5 toolのPASSログ） |
| Validate build / [38007012580](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012580) | `build` job `114078086527` success | install／build／metadata・sitemap／基本route smoke、deployment verifier compile等がsuccess |
| Verify publication readiness integration / [38007012539](https://github.com/Josh-Temple/kaigo-rules/actions/runs/38007012539) | `publication-readiness` job `114078018545` success | canonical regeneration／bounded publication readiness がsuccess |

**検証の境界：** 上記Actionsは`ef12b...`のC**実装head**に対するものであり、この追補commit後のheadに対しては改めてActionsのrun/stepを取得する。手元の`npm ci`・`npm test`・`npm run build`・`npm run test:browser`・`npm run verify:routes`は`NOT_RUN`。CIのheadless Chromiumと実Android/native 200% zoom・人のスクリーンリーダー聴取・実印刷・PDFビューア上の`#page`移動は別。実機・人間による試行はすべて`NOT_RUN`。production HTTP、Vercel、deploy-stateは**本C作業では更新も実測もしていない**。

**公開単位：** 今回は8ファイルの既存PR #465を維持。服薬改訂と転倒記事は同一PR内で関連リンク・home導線・sitemapを持ち、どちらか一方の部分公開には**HOLDページとそのリンク・sitemap登録を含まない新しい安全な実体**への分離、新headでのCIおよびD再監査が必要。現時点では分離・merge・production公開をしない。想定本番HTTP検査は両記事公開の場合16 URL、転倒保留の場合15 URL相当だが、**新release実測はNOT_RUN**。

**D/Eへのゲート：** A #474の最新B blob突合未完、L211現行全文直読`NOT_ESTABLISHED`、自治体個別運用`NOT_ESTABLISHED`、D #475は旧C `77eb4b...`の監査のみで`ef12b...`の転倒記事を独立検査していない。したがって服薬`RELEASE_HOLD`／転倒`PUBLIC_SOURCE_GUIDE_HOLD`を維持し、Dへこのコード実体＋最新版B＋A再採否を渡す。#451は`PREVIEW_ONLY / NOT_PUBLIC / HUMAN_REVIEW_DEFERRED`、EX01/EX02は未依頼・未実施、HU01未承認。既存5 Issue/5 tool／Analytics／flag／登録ルートへの本Wave追加変更なし。
