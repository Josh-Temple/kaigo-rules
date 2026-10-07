# Kaigo Ops — 利用観測の初期契約

更新日: 2026-10-07  
対象: Kaigo Ops / Vercel project `kaigo-ops`

## 目的

Kaigo Opsの利用状況を、まずpageviewだけで観測する。

pageviewは「次にどこを改善するか」を考えるための観測値として使い、業務改善効果や需要を直接示す指標として扱わない。

継続観測の台帳、2〜4週間レビュー、判断ルールは `docs/kaigo-ops/usage-observation.md` をcanonical operational ledgerとする。このファイルは計測対象・非収集データ・初回観測日の技術契約を担い、観測値の解釈と履歴はusage observation側で管理する。

## 2026-10-07 pre-release fresh確認結果

Repository baseline:

- pre-release main: `a3bb60b3d59fefb783c88e9fc710101b076ffe01`

Pre-release Vercel baseline:

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


## Worker E production release

2026-10-07のUtilization & Actionability Waveは、integration PR #421をmainへ統合し、Kaigo Ops projectへexact SHAでproduction releaseした。

- integration PR: #421
- release main SHA: `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2`
- Kaigo Ops production deployment: `dpl_3SiLHr9Nf3MEgmACbWmvEy4ihXZq`
- deployment state: `READY`
- deployment Git SHA: `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2`
- production alias: `https://ops-site-pi.vercel.app/`
- alias error: none

release後のproduction verificationでは `/_vercel/insights/script.js` がHTTP 200となり、tracking scriptの配信は確認できた。

release直後のVercel Web Analytics pageview APIは `visitors: 0 / pageviews: 0`で、path別集計も空だった。

## Worker A observation activation verification

2026-10-07に、current `main`、production deployment、public alias、Analytics client implementation、script delivery、Web Analytics APIをfresh確認した。

Starting state:

- main: `f0fed0aaf923fa7feaf4bb78949182ffcfb10c3c`
- production deployment: `dpl_3SiLHr9Nf3MEgmACbWmvEy4ihXZq`
- production implementation SHA: `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2`
- public alias: `https://ops-site-pi.vercel.app/`
- `@vercel/analytics`: `2.0.1`
- root layout: `<Analytics />` present

Delivery / browser diagnosis:

- compatibility route `/_vercel/insights/script.js`: HTTP 200
- productionが挿入するResilient Intake script: `/f130755abdc7617b/script.js`: HTTP 200
- script tagは `data-view-endpoint="/f130755abdc7617b/view"` を持つ
- controlled Playwrightではpageview callが `window.vaq` に積まれることを確認した
- deployed Analytics scriptには `navigator.webdriver || navigator.userAgent.includes("Headless")` の自動化判定があり、Playwright trafficではqueueが送信処理へ進まなかった
- したがってcontrolled Playwright trafficは実利用として数えず、positive receive testにも使わない

Vercel receive:

- verification開始時: `visitors: 0 / pageviews: 0`
- その後のfresh API確認: `visitors: 1 / pageviews: 1`
- requestPath: `/` = 1 pageview
- browserName: Firefox
- deviceType: desktop
- この受信はcontrolled PlaywrightのChromium trafficとは一致しない

以上から、**production Web AnalyticsのVercel側pageview受信は確認済み** とする。受信した1 pageviewは需要・効果の証拠とは扱わず、controlled verification trafficとも混同しない。

## Worker E Observation Activation & Learning Loop release

2026-10-07にintegration PR #428をmainへ統合し、Kaigo Opsのruntime変更をexact integration SHAでproductionへ反映した。

- integration PR: #428
- runtime release SHA: `b7a29a0da5c24787a9792bb6c55e6a14a330f897`
- production deployment: `dpl_63FnsT15tnNQ1YDmTkJAYNyNh27v`
- deployment state: `READY`
- production alias: `https://ops-site-pi.vercel.app/`
- alias error: none

Repository-sideでは、integration headに対して `Validate ops site`、`Validate build`、publication-readiness integrationがすべて成功した。

release後のproduction verificationでは、home、5 Issue、5 action tool、5つのIssue → tool / Kaigo Rules / feedback journey、`robots.txt`、`sitemap.xml`、Analytics script delivery、390px browser journeyを確認し、すべてPASSした。

release後のWeb Analytics fresh確認:

- `visitors: 2 / pageviews: 2`
- requestPath: `/` = 2
- browserName: Chrome = 1 / Firefox = 1
- deviceType: desktop = 2

この2 pageviewは個々のアクセス由来を確定していない。controlled browser verificationは実利用として扱わず、現在のpageview数から需要、改善効果、tool利用完了を推定しない。

Analytics stateは **RECEIVE_CONFIRMED** を維持し、first confirmed observation dateは **2026-10-07** のままとする。

## 次の確認

Web Analytics有効化の手作業はblockerではなくなった。以後はpageviewを継続観測し、2〜4週間程度の母数ができるまでは需要・改善効果を断定しない。

自動化ブラウザはAnalytics側で除外されるため、将来のproduction verificationでもPlaywright pageviewを実利用値として扱わない。

## 最初に観測するページ

custom eventは追加せず、pageviewだけを対象とする。

- `/`
- `/issues/information-search`
- `/issues/documentation`
- `/issues/training-handover`
- `/issues/communication-collaboration`
- `/issues/productivity-utilization`
- `/tools/documentation-review`
- `/tools/information-inventory`
- `/tools/training-handover-inventory`
- `/tools/communication-review`
- `/tools/work-time-review`

4つの新規action toolは今回の統合対象に含める。production反映後、これらも同じpageview対象として扱う。

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

**2026-10-07**

productionでVercel側のpageview受信を初めて確認できた日を初回観測日とする。

この日付は「需要が確認できた日」「業務改善効果が確認できた日」ではない。初回受信の1 pageviewについても、利用価値や需要を推定する根拠には使わない。
