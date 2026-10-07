# Kaigo Ops — 利用観測の初期契約

更新日: 2026-10-07  
対象: Kaigo Ops / Vercel project `kaigo-ops`

## 目的

Kaigo Opsの利用状況を、まずpageviewだけで観測する。

pageviewは「次にどこを改善するか」を考えるための観測値として使い、業務改善効果や需要を直接示す指標として扱わない。

## 2026-10-07 fresh確認結果

Repository `main`:

- HEAD: `a3bb60b3d59fefb783c88e9fc710101b076ffe01`

Vercel:

- project: `kaigo-ops`
- project id: `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`
- current production deployment: `dpl_BEgyNYKuDHwikkU2W9zPSKGVcZ9U`
- deployment state: `READY`
- production implementation SHA: `b79a26a75644ede56dd8712bd8208fcd34968f29`
- public alias: `https://ops-site-pi.vercel.app/`

Client implementation:

- `@vercel/analytics` version `2.0.1`
- root layoutに `<Analytics />` が存在する
- production bundleにもAnalytics componentとVercelのclient configが含まれる

Production delivery:

- `/_vercel/insights/script.js`: 404
- production bundleに埋め込まれたcurrent unique intake pathの `script.js`: 404
- 同じunique intake pathの `view` をGETした場合も404
- Web Analytics pageview APIは問い合わせ可能だが、確認時点の値は `visitors: 0 / pageviews: 0`

したがって、**コードは組み込まれているが、productionでpageview収集が開始されたことは確認できない**。

Vercel側のproject-level enable flagは、現在利用できるproject取得結果には露出していない。Activity Log取得は権限制約で403となり、利用可能なVercel操作にはWeb Analyticsを有効化するactionもないため、このWorkerから有効化状態の確定・変更はできなかった。

## 必要な人手操作

Vercel Dashboardで `kaigo-ops` → Analytics を開き、Web Analyticsが未有効ならEnableする。既に有効なら有効状態を確認する。

その後の次回production deploymentでAnalytics用routeが生成されたことを確認し、script配信・pageview送信・Vercel側受信を順に再確認する。

## 最初に観測するページ

custom eventは追加せず、pageviewだけを対象とする。

- `/`
- `/issues/information-search`
- `/issues/documentation`
- `/issues/training-handover`
- `/issues/communication-collaboration`
- `/issues/productivity-utilization`
- `/tools/documentation-review`

B/Cで新しいaction toolが統合された場合は、production反映後に同じpageview対象へ加える。

## 解釈上の注意

次の読み替えは禁止する。

- PVが多い = 改善効果が高い
- PVが少ない = 需要がない
- tool page閲覧 = tool利用完了
- Kaigo Rules遷移 = 制度理解完了

pageviewは、閲覧の偏りや改善候補を見つけるための観測値に限定する。

## 今回収集しないもの

今回の初期観測では、次を追加収集しない。

- custom event
- 検索欄への入力内容
- worksheetへの入力内容
- 利用者名、職員名その他の個人識別情報
- 介護記録本文
- tool利用完了や改善成功を示す独自フラグ

pageviewだけでは次の改善判断ができないことが確認できた場合に限り、必要最小限のcustom eventを別途検討する。

## 観測開始日

未確定。

productionでtracking scriptが正常配信され、pageview送信とVercel側受信を確認できた日を初回観測日として記録する。
