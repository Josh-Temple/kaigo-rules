# Search Console SEOフォローアップ：章詳細noindexと本番反映

- 記録日時: 2026-10-21 22:09 JST
- 初回監査記録: [docs/seo-gsc-audit-2026-10-21.md](./seo-gsc-audit-2026-10-21.md)
- 初回監査PR #546 は2026-10-21にmainへマージ済み。マージSHA: `73a971db8c330ee8ab46c4fdd8f38d552fd75a22`。

## 追加で見つかった問題

初回監査の後、`/handbook/{service}/{chapter}` の章詳細ページを確認しました。これらのURLはサイトマップ外でしたが、内部リンクがあり、metadata関数の既定値でインデックス可能でした。ライブページには「作成中・未確認の内容を含みます」と表示されていました。例として `/handbook/homebath/equipment` は修正前にHTTP 200、自ページcanonical、robots metaなしでした。

## 修正

- PR #547: https://github.com/Josh-Temple/kaigo-rules/pull/547
- `app/handbook/[serviceId]/[chapter]/page.tsx` で章詳細のみ `noindex, follow` を指定しました。ページは公開HTTP 200のまま、内部リンクはfollow可能で、自ページcanonicalと未確認表示も維持します。
- 39サービスの入口ページ、サイトマップ、法令説明、制度情報、確認状態は変更していません。検索結果や未確認の章本文を登録済みと見せる変更も行っていません。
- 実装コミット: `add4920d5f1effeffb8e98543cea8c27a8c08258`
- 回帰テスト追加コミット: `d1ec9cf88d1ddae0e0fb872f22b6d166b91aa8ef`
- PRマージSHA（main）: `d7fda86f09a78f96086794c6512ed45d27176295`

## CIと本番反映

- PR #547 の `Validate build` と `Verify publication readiness integration` は両方成功しました。
- 使用した既存デプロイworkflow: [Daily conditional Vercel production deploy run #53](https://github.com/Josh-Temple/kaigo-rules/actions/runs/39603947623)。force_rules / force_ops は両方falseでmainを実行しました。
- 計画ステップは成功し、rules / ops 両プロジェクトに変更ありと検出しました。介護ルールのdeploy hookは受理され、フィールド検証本番ゲート、machine retrieval baseline、rulesのdeploy-state記録は成功しました。
- 介護ルールのmachine retrieval baseline: production SHAは上記main SHA、search hit、top-3 hit、context integrity、full passは各100%、miss / integrity failureは0件でした。
- 共有workflow全体の状態はFailureです。介護業務改善側の `VERCEL_TOKEN` が未設定と判定され、Opsの本番デプロイ・検証はスキップされました。Opsをデプロイしたり、認証確認を迂回したりしていません。介護ルール側のゲートが成功したことと、共有workflow全体の失敗は区別します。

Vercel本番:

- プロジェクト: `kaigo-rules` (`prj_C63ec6TX92jB7EMx9RVgA2qq08uG`)
- Deployment ID: `dpl_ABW5HMYKAGmCfXeUJmf7D6P2cwp6`
- 状態: `READY`, target `production`, alias `https://kaigo-rules.vercel.app`
- GitHub SHA: `d7fda86f09a78f96086794c6512ed45d27176295`
- READY時刻: 2026-10-21 22:04:09 JST

## 公開URLの再検証

デプロイ後、以下12 URLすべてでHTTP 200を確認しました。`url_effective` は入力URLと同じで、リダイレクトはありませんでした。

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
- `/handbook/homebath/equipment`

本番HTML:

- `/handbook/homebath/equipment`: HTTP 200、self-canonical、robots meta `noindex, follow`、未確認の注意書き表示あり。
- `/services/dayservice`: HTTP 200、self-canonical、robots noindexなし。既存のWIP説明を維持。

## Search Consoleのライブテスト

- `/handbook/homebath/equipment` のインデックス側状態は検査時に `URL is unknown to Google`、未クロールでした。2026-10-21 22:07 JSTのライブテストはページ取得Successful、Crawl allowed Yes、Indexing allowed No（robots metaのnoindexを検出）、user-declared canonicalは自ページでした。noindexはライブテストで認識されました。登録リクエストボタンは無効で、登録申請はしていません。
- `/services/dayservice` の2026-10-21 22:08 JSTライブテストは `URL is available to Google`、`Page can be indexed` でした。インデックス側は引き続きURL未認識・未クロールと表示されました。登録リクエストは送信していません。
- サイトマップは前回送信済みの1件を維持。Search ConsoleはStatus `Success`、Last read 2026-10-21、検出55ページ・動画0件でした。XMLはURL55件・重複なし・同一host・クエリなしです。
- 日次上限により前回の `/services/dayservice` 登録リクエストは受理されていません。以後、手動登録リクエストは送信していません。

## Google側の反映待ち・残る課題

- Search Consoleのページ登録レポートは最終更新が2026-10-12のため、登録済み2・未登録0という集計は最新値として使えません。次回のレポート更新を待ち、URL検査と突合します。
- `/handbook/{service}/{chapter}` のnoindex反映は、Googleが次回クロールしてから検索インデックス側へ反映されます。ライブテストで設定を検出したことは、過去のインデックス状態が即時削除されたことを意味しません。
- 39サービスの手引入口と法令・基準・通知・報酬・国Q&Aページは引き続きサイトマップと内部リンクから辿れます。未確認状態を保ったまま、章詳細だけを検索対象外にしました。
- 共有Vercel workflowの介護業務改善側検証には `VERCEL_TOKEN` が必要ですが、未設定のため実行されていません。値の取得や設定変更は行わず、失敗を成功とは扱いません。
