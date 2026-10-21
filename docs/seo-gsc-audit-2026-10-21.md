# Google Search Console / SEO監査記録

- 作業日時: 2026-10-21 21:31 JST
- 対象プロパティ: `https://kaigo-rules.vercel.app/`（URL プレフィックス）
- 対象サイト: https://kaigo-rules.vercel.app/
- 監査時点の main SHA: `0e9cf34e880a3209515264a06e8b29ab54d48f01`
- PR番号・報告導入コミットSHA: PR作成後に追記

## 結果の要約

- 公開サイト、robots.txt、sitemap.xml と主要ページ11 URLは HTTP 200。最終URLも各リクエストと同じで、リダイレクトは観測しませんでした。
- Search Consoleには対象のURLプレフィックスプロパティが登録済みでした。新規所有権確認は不要でした。
- 未提出だった sitemap.xml を1回送信し、Search Console は Success と表示。最終読み取り日は2026-10-21、検出55ページ、動画0件です。
- 10月12日更新のページ登録レポートは「登録済み2・未登録0」でしたが、10月21日のURL検査では主要ページに未登録が複数あります。レポートの集計日は古く、現状の確定値として扱えません。
- URL検査のライブテストでは、確認した未登録の主要ページはすべて「URL is available to Google」「Page can be indexed」でした。
- 手動インデックス登録リクエストは `/services/dayservice` に対して1回試しましたが、Googleの日次上限エラーで受理されませんでした。登録完了を示す結果はありません。
- robots.txt、サイトマップ生成、canonical、title / description に修正すべき問題を確認しませんでした。制度解釈や確認状態を変更するコード修正は行っていません。

## Google Search Console

対象の既存プロパティは `https://kaigo-rules.vercel.app/` です。所有権確認やプロパティ追加は行っていません。

ページのインデックス登録レポートは最終更新日が2026-10-12で、その時点の表示は登録済み2、未登録0でした。登録済み例はトップページ（最終クロール2026-10-05）と `/questions/life-counselor-staffing`（最終クロール2026-10-06）です。2026-10-21のURL検査結果と整合しないため、件数の最新値とはみなしません。

| URL | URL検査のインデックス状態（2026-10-21） | ライブテスト |
| --- | --- | --- |
| `/` | 登録済み | 実施不要（登録済み表示） |
| `/questions/life-counselor-staffing` | 登録済み | 実施なし。最終クロールは10月6日 |
| `/databases` | Discovered - currently not indexed。送信後はサイトマップ検出済み | 21:16 JST、取得可能・インデックス可能 |
| `/services/dayservice` | Discovered - currently not indexed。サイトマップ検出済み | 21:21 JST、取得可能・インデックス可能 |
| `/legislation` | Discovered - currently not indexed。サイトマップ検出済み | 21:23 JST、取得可能・インデックス可能 |
| `/law` | Discovered - currently not indexed。サイトマップ検出済み | 21:25 JST、取得可能・インデックス可能 |
| `/rules` | Discovered - currently not indexed。サイトマップ検出済み | 21:26 JST、取得可能・インデックス可能 |
| `/notices` | Discovered - currently not indexed。サイトマップ検出済み | 21:26 JST、取得可能・インデックス可能 |
| `/qa` | Discovered - currently not indexed。サイトマップ検出済み | 21:27 JST、取得可能・インデックス可能 |
| `/fees` | Discovered - currently not indexed。サイトマップ検出済み | 21:27 JST、取得可能・インデックス可能 |

`/databases`、`/law`、`/notices` は最初の検査でGoogleがURLを認識していない表示でした。サイトマップ処理後の再検査ではサイトマップ経由で発見済みになりました。各ページは未クロール（最終クロール N/A）で、発見済みとインデックス登録済みは別の状態です。

## サイトマップとクロール

- 送信先: `https://kaigo-rules.vercel.app/sitemap.xml`
- 送信状況: 以前は未提出。2026-10-21に一度送信し、Search Consoleの一覧で Status `Success`、Last read `Oct 21, 2026`、Discovered pages `55`、Discovered videos `0` を確認しました。重複送信はしていません。
- XML検証: 公開URLから取得した内容をXMLパーサーで検証し、urlsetとして正常、URL 55件・重複なし、全URLが同一ホスト、クエリURL 0件でした。
- 55 URLには39サービスの手引ページが含まれます。共有の法令・基準・通知・国Q&Aページと報酬等の主要案内ページも含まれます。
- 検索クエリ付きURLはサイトマップに含まれません。`/databases/search` は検索結果ページとして noindex が指定され、サイトマップ対象外です。手引の章詳細URLもサイトマップには加えていません。

`robots.txt` の内容は以下でした。公開ページを許可し、`/api/` のみ除外し、正しいサイトマップURLを指定しています。

```text
User-Agent: *
Allow: /
Disallow: /api/

Sitemap: https://kaigo-rules.vercel.app/sitemap.xml
```

## HTTP・メタデータ・導線

2026-10-21の確認で `curl` のHTTPステータスと最終URLを取得しました。以下はすべてHTTP 200です。

- `/`
- `/robots.txt`
- `/sitemap.xml`
- `/databases`
- `/services/dayservice`
- `/legislation`
- `/law`
- `/rules`
- `/notices`
- `/fees`
- `/qa`

ブラウザーでトップ、DB一覧、通所介護ページも表示できました。トップと主要導線は `/databases`、`/services`、`/legislation`、`/start`、`/sources` へつながります。サービス一覧から39サービスの手引に移動できます。DB一覧は介護保険法、基準省令、解釈通知、国Q&Aの入口を持ち、報酬はサービス別ページへ案内されます。

ライブHTMLで確認した代表メタデータは次の通りです。いずれも自ページを指すcanonicalがあり、robots noindexはありません。

| ページ | title | description / canonical |
| --- | --- | --- |
| `/` | 介護ルール \| 制度の根拠と実務をつなぐ | 説明文あり、canonical `https://kaigo-rules.vercel.app` |
| `/databases` | 介護制度DB一覧 \| 介護ルール | 説明文あり、canonical `https://kaigo-rules.vercel.app/databases` |
| `/services/dayservice` | 通所介護の手引 \| 介護ルール | 説明文あり、canonical `https://kaigo-rules.vercel.app/services/dayservice` |

通所介護ページは「作成中の手引」であることを画面上で明示しています。未確認の内容を確認済みへ変えず、公式資料の案内と独自の説明の確認状態も変更していません。

## 登録申請・変更内容

- sitemap.xml: 未提出状態を解消するため、Search Consoleで一度送信。処理成功を確認しました。
- インデックス登録リクエスト: `/services/dayservice` のライブテスト後に1回実行しました。Googleは「daily quotaを超過したため処理できない。明日再試行」と表示しました。申請は受理されていません。他URLへの登録リクエストは送信していません。
- コード変更: なし。公開済みのrobots.txt、サイトマップ、canonical、title、description、内部リンクにGooglebotを妨げる不具合を確認しませんでした。既存のnoindex境界、未確認ラベル、法令解釈の状態を維持しました。
- Vercel設定変更: なし。

## GitHub・CI・Vercel

- 監査記録の専用ブランチ: `docs/seo-gsc-audit-2026-10-21`
- PR番号・報告導入コミットSHA: PR作成後に追記
- GitHubの設定画面ではclassic branch protection rulesもrepository rulesetsも設定されていませんでした。PRの承認要件は表示されません。
- `.github/workflows/validate-build.yml` はmain宛ての全PRで実行されます。変更はドキュメントだけですが、既存のCIをPR上で実行し、その結果を確認します。手動でActionsを再実行しません。
- 本番Vercelデプロイ: `dpl_Btmz5inYNK72g6V44cdLrjmMWgQw`、状態 `READY`、production。デプロイSHA `0e9cf34e880a3209515264a06e8b29ab54d48f01`。2026-10-21 20:23 JSTごろREADY。
- SEOコード変更がないため、監査記録のPRから本番デプロイは作成していません。本番URLは上記HTTP検証で再確認済みです。

## Google側の反映待ち・次の対応

- sitemap.xmlの読み取りは成功しましたが、登録済みページ数に反映されるまでのGoogle側の更新待ちです。
- URL検査で主要な法令・基準・通知・報酬・国Q&Aページが未登録と表示され、いずれも未クロールです。ライブテストの取得可能表示はインデックス登録を保証しません。
- 日次上限がリセットされた後、必要に応じて `/services/dayservice` など未登録の主要URLで登録リクエストを再試行し、受理表示とページレポートを別々に確認してください。上限を回避した送信は行っていません。
- 今後、サイトマップのLast read、検出URL数、登録済み・未登録ページの最新集計をSearch Consoleで再確認してください。

## 証拠・制約

- Search Consoleサイトマップ一覧の画面証拠は監査実施時に取得しました。アカウント名、認証情報、セッション情報は記録していません。
- Search Consoleページレポートの最終更新日は2026-10-12であり、10月21日時点の個別URL検査と数が食い違います。最新の総登録数・未登録理由を示すレポートはまだ確認できていません。
- HTTP応答は公開URLへのcurl確認値です。GSCライブテストはURL到達性とインデックス可能性の表示であり、実際の検索結果登録とは区別しています。
