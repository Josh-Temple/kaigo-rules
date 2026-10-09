# Worker C — 同一版コード引継ぎ（2026-10-10）

- 対象PR: #465（未マージ・E判定待ち）
- 対象基点: C head `77eb4b391ac722adc1a34024e6c7a33b35179949`、base tree `bba9b7d274355df07535a38ec4c132b9dccebb14`
- 文章正本: B PR #466 commit `5df748a60b0d3699c751643b47fe77e90aa9a8d2`、編集稿blob `16915a0d6573e534c2661ed24d2cf758ad4c9164`（§2, §3）
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
