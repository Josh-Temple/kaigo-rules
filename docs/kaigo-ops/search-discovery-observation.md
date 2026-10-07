# Kaigo Ops — Search Discovery Observation

更新日: 2026-10-08
対象: Google Search discovery / Search Console observation
状態: canonical observation record

## checked_at

`2026-10-08T00:12:35+09:00`

## Fresh production state

開始時にlatest `main`、open PR、Kaigo Ops current productionをfresh確認した。

- latest main: `61620d77976b0fb692256c4b18993ef1498e4116`
- Vercel project: `kaigo-ops`
- production deployment: `dpl_63FnsT15tnNQ1YDmTkJAYNyNh27v`
- runtime release SHA: `b7a29a0da5c24787a9792bb6c55e6a14a330f897`
- deployment state: `READY`
- production alias: `https://ops-site-pi.vercel.app/`

current productionを直接取得して確認した。

- `/robots.txt`: HTTP 200
- `robots.txt` は `Allow: /` と production `sitemap.xml` を宣言
- `/sitemap.xml`: HTTP 200
- sitemap掲載URL: home + 5 Issueの主要6 URL
- home + 5 Issue: 6 / 6 HTTP 200
- home + 5 Issue: 6 / 6でsite-declared canonicalがproduction URLと一致

対象Issue:

- `/issues/information-search`
- `/issues/documentation`
- `/issues/training-handover`
- `/issues/communication-collaboration`
- `/issues/productivity-utilization`

したがって、Googleへ提示するcrawl / sitemap / site-declared canonicalの技術的入口はcurrent productionで成立している。

## Search Console observation state

この実行環境では、ユーザーのGoogle Search Consoleへ認証済みでアクセスできる接続がない。利用可能な外部連携も確認したが、Search Console連携は未接続だった。

Search Console未確認を登録済み・未登録・index済み・未indexのいずれにも読み替えない。

| item | state | blocker |
| --- | --- | --- |
| URL-prefix property `https://ops-site-pi.vercel.app/` | UNKNOWN | authenticated Search Console access unavailable |
| sitemap submission | UNKNOWN | authenticated Search Console access unavailable |
| home index state | UNKNOWN | URL Inspection unavailable |
| information-search index state | UNKNOWN | URL Inspection unavailable |
| documentation index state | UNKNOWN | URL Inspection unavailable |
| training-handover index state | UNKNOWN | URL Inspection unavailable |
| communication-collaboration index state | UNKNOWN | URL Inspection unavailable |
| productivity-utilization index state | UNKNOWN | URL Inspection unavailable |
| Google-selected canonical | UNKNOWN | URL Inspection unavailable |
| indexing request | NOT_RUN | Search Console access unavailable |

site-declared canonicalは主要6 URLすべてで確認済みだが、Google-selected canonicalとは区別する。

## Exact next action

Search Consoleへアクセス可能なGoogleアカウントで、次の順に確認する。

1. property selectorでURL-prefix property `https://ops-site-pi.vercel.app/` の有無を確認する。
2. propertyが存在しない場合は、同じURLをURL-prefix propertyとして追加し、Search Consoleが提示する利用可能な所有権確認方法のいずれかで確認する。
3. propertyが存在する、または確認完了後、Sitemapsで `https://ops-site-pi.vercel.app/sitemap.xml` の送信状態を確認する。未送信ならこの1件だけ送信する。
4. URL Inspectionでhome + 上記5 Issueの主要6 URLだけを確認し、GoogleによるURL認識、index state、last crawl（取得可能な場合）、user-declared canonical、Google-selected canonicalを記録する。
5. 未indexで、Live Testが正常かつindexingを妨げる理由がないURLに限り、必要なら「インデックス登録をリクエスト」を実行し、実行日時を記録する。
6. tool route全件や大量URLのindexing requestは行わない。

`site:` 検索結果やsitemap配信だけでindex stateを確定しない。

## Worker A completion

A-7の代替完了条件を満たす。

- public production baseline: CONFIRMED
- property state: UNKNOWN
- sitemap submission state: UNKNOWN
- major 6 URL index state: UNKNOWN
- Google-selected canonical: UNKNOWN
- indexing request: NOT_RUN
- exact blocker: RECORDED
- exact next action: RECORDED

runtime変更は行っていないため、Kaigo Opsのredeployは不要。
