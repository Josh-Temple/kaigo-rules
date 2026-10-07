# Kaigo Ops — Discoverability audit

更新日: 2026-10-08  
対象: Kaigo Ops / discoverability・public entry

## 目的

5つのIssueが、公開されているだけでなく、検索・共有・再訪から見つけられる公開入口になっているかを確認する。

SEOのために効果を誇張したり、AIで解決できると断定したり、根拠のない数値や成功表現を追加しない。

## Worker D fresh read baseline（integration前）

Repository:

- latest main: `f0fed0aaf923fa7feaf4bb78949182ffcfb10c3c`

Kaigo Ops production:

- Vercel project: `kaigo-ops`
- project id: `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`
- production deployment: `dpl_3SiLHr9Nf3MEgmACbWmvEy4ihXZq`
- runtime release SHA: `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2`
- public alias: `https://ops-site-pi.vercel.app/`
- deployment state: `READY`

## Worker D production audit（integration前）

Vercel経由でproduction aliasを取得した結果:

- home: HTTP 200
- 5 Issue routes: 5 / 5 HTTP 200
- 5 action tool routes: 5 / 5 HTTP 200
- homeには5 Issueへの公開リンクがある
- 各Issueには5 Issue間のnavigationがある
- Issue → action tool / Kaigo Rules / feedbackの導線がある
- action tool → 元Issue / evidenceの戻り導線がある
- action tool → feedbackはWorker Cの同Wave実装対象であり、Dでは重複変更しない

### metadata

integration前productionでは:

- home title / description: あり
- 5 Issue title / description: 5 / 5 あり
- canonical: home / 5 Issueとも未設定
- Open Graph metadata: home / 5 Issueとも未設定

各Issueのtitle / descriptionは、内部用語ではなく利用者の困りごとを表す日本語になっている。SEO目的の追加主張は不要と判断した。

### robots / sitemap

integration前productionでは:

- `/robots.txt`: HTTP 404
- `/sitemap.xml`: HTTP 404

404ページにはNext.jsの `noindex` が付くが、これはpublic page自体のnoindexを意味しない。homeと5 Issueにはnoindex metadataは確認されなかった。

## 今回の修正

1. production alias `https://ops-site-pi.vercel.app` をmetadata baseとして固定する
2. homeと5 Issueへcanonicalを設定する
3. homeと5 IssueへOpen Graph / Twitter summary metadataを追加する
4. `robots.txt` を生成し、public crawlingを許可する
5. `sitemap.xml` にhome + 5 Issueを掲載する
6. action toolはsitemapへ積極掲載しない

action toolは公開・crawl可能なまま維持するが、Kaigo Opsの公開入口は「困りごと → Issue」を基本とするため、今回のsitemapでは主要入口6ページに限定する。toolをnoindexにはしない。

## canonical safety

Vercel projectにはproduction alias以外にもVercel生成ドメインが存在する。

そのため、canonicalをproduction aliasへ固定し、preview / generated deployment URLを正規URLとして示さない。

## Worker E post-release production verification

Observation Activation & Learning Loop Waveのintegration PR #428をmainへ統合し、次のruntimeをproductionへ反映した。

- runtime release SHA: `b7a29a0da5c24787a9792bb6c55e6a14a330f897`
- production deployment: `dpl_63FnsT15tnNQ1YDmTkJAYNyNh27v`
- deployment state: `READY`
- production alias: `https://ops-site-pi.vercel.app/`

Repository CIではcanonical / social metadata、robots、sitemapの回帰テストとproduction buildがPASSした。release後のproduction verificationでは、`robots.txt` と `sitemap.xml` の配信、home・5 Issue・5 action toolのroute、5つのIssue → tool / Kaigo Rules / feedback journey、390px表示を確認し、すべてPASSした。

したがって、Worker Dのintegration前auditで確認したcanonical未設定、Open Graph未設定、`robots.txt` / `sitemap.xml` 404はcurrent productionの状態ではない。今回対象とした技術的discoverability範囲では、release blockerとなる重大な欠落は残っていない。

## 外部indexing state

次は今回確認していない。

- Google Search Consoleへのproperty登録
- sitemap送信状態
- Googleによるindex登録状態
- 実際の検索流入

`robots.txt` や `sitemap.xml` の存在から、Search Console登録・index・検索流入を推測しない。

## 境界

今回の変更はdiscoverabilityの技術的入口だけを整える。

- 検索順位を成果指標にしない
- pageviewを需要や改善効果へ読み替えない
- custom eventを追加しない
- Issue数を増やさない
- action toolやfeedbackの内容改善はA〜Cとの責任境界を維持する


## Worker B — Kaigo Rules → Kaigo Ops contextual entry（2026-10-08）

### fresh read baseline

Repository:

- branch start main: `61620d77976b0fb692256c4b18993ef1498e4116`
- Kaigo Rules current production deployment: `dpl_EM9H4r6hK7QsVkRU4H1TRjZ3atzR`
- Kaigo Rules current production runtime SHA: `a3bb60b3d59fefb783c88e9fc710101b076ffe01`
- Kaigo Rules production alias: `https://kaigo-rules.vercel.app/`
- Kaigo Ops current production deployment: `dpl_63FnsT15tnNQ1YDmTkJAYNyNh27v`
- Kaigo Ops current production runtime SHA: `b7a29a0da5c24787a9792bb6c55e6a14a330f897`
- Kaigo Ops production alias: `https://ops-site-pi.vercel.app/`

Kaigo Rulesのhome / DB hub / DB横断検索 / 実務ガイド / 共通navigationをfresh readし、Kaigo Ops側の5 Issue registryも確認した。Kaigo Rules側には、制度確認後の業務改善へ文脈付きで移る公開入口はまだなかった。

### selected entry

過剰な相互リンクを避けるため、最初の接続箇所は `/databases/search` の**検索実行後**に限定する。

役割分担を次のように明示する。

- 介護ルール: 法令・基準・通知・報酬・Q&Aから「制度上どうなっているか」を確認する
- 介護業務改善: 制度確認後に、業務の見直し方・改善の選択肢・小さな試し方を検討する
- 介護業務改善側で制度適合を確定しない。制度判断は介護ルールの検証状態と原典へ戻す

接続対象は、今回の優先Issueである次の2件に限定する。

1. 情報探索: `https://ops-site-pi.vercel.app/issues/information-search`
2. 記録・文書作成: `https://ops-site-pi.vercel.app/issues/documentation`

検索語からIssueを自動推定・自動mappingしない。5 Issueすべてを並べることもしない。

### production destination check

実装前のfresh checkで、上記2 Issueのcurrent production destinationはいずれもHTTP 200を返した。

Kaigo Rules側の変更はWorker B branch上であり、この時点ではcurrent productionへ未反映。production releaseとpost-release verificationはIntegrator / Worker Eの責任範囲とする。

### validation contract

`tests/database-global-search.test.mjs` に、次を回帰条件として追加する。

- 制度確認 → 業務改善という役割説明が残る
- 情報探索 / 記録・文書の2 Issueだけを直接案内する
- 他の3 Issueをこの入口へ自動追加しない
- Kaigo Opsが制度適合を確定しない旨を保持する
