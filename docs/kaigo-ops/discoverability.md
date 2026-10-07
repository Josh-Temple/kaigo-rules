# Kaigo Ops — Discoverability audit

更新日: 2026-10-07  
対象: Kaigo Ops / Worker D — Discoverability & Public Entry

## 目的

5つのIssueが、公開されているだけでなく、検索・共有・再訪から見つけられる公開入口になっているかを確認する。

SEOのために効果を誇張したり、AIで解決できると断定したり、根拠のない数値や成功表現を追加しない。

## fresh read baseline

Repository:

- latest main: `f0fed0aaf923fa7feaf4bb78949182ffcfb10c3c`

Kaigo Ops production:

- Vercel project: `kaigo-ops`
- project id: `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`
- production deployment: `dpl_3SiLHr9Nf3MEgmACbWmvEy4ihXZq`
- runtime release SHA: `f18b3d7c9eca6ec9108ef0937c677cd7e4ec1ad2`
- public alias: `https://ops-site-pi.vercel.app/`
- deployment state: `READY`

## production audit

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

productionでは:

- home title / description: あり
- 5 Issue title / description: 5 / 5 あり
- canonical: home / 5 Issueとも未設定
- Open Graph metadata: home / 5 Issueとも未設定

各Issueのtitle / descriptionは、内部用語ではなく利用者の困りごとを表す日本語になっている。SEO目的の追加主張は不要と判断した。

### robots / sitemap

productionでは:

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
