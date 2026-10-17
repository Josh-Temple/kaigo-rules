# 第2段階・12件の原典候補 → 15章手引（試用のみ）

**HOLD_NO_GO / DRAFT_UNREVIEWED / NOT_ESTABLISHED / 人手レビュー未了**

このディレクトリは、2026-10-17のLibrary-only固定キュー12件の出典案内を、2サービスの15章へ紐付けた**追加の未レビュー候補**です。原典の新しい法的確認や現行法令の承認ではありません。

## 使い方（ローカル限定）

- **通所介護**：親Draft #495、修正Draft #499から継承する `../dayservice-handbook.html` の「第2段階原典照合からの追加確認候補」で11文が章別に表示されます。既存65文と27+11の原典候補、端末メモの保存・書出しは維持します。
- **通所リハビリテーション**：`../dayrehab-evidence-handbook.html` をローカルに保存・開いてください。18文を15章の暫定配置で表示します。6文は条項を個別に特定できておらず、ID欄に `NOT_ESTABLISHED` と表示します。

HTMLは`docs/prototypes/`配下にあり、`app/`・`public/`・公開ルート・サイトマップ・公開allowlist・DB・法令review registryには接続しません。端末から自動で外部サイトへ通信しません。**Repositoryのソース公開は秘密性を意味しません**。利用者情報や機微情報は入力しないでください。

## provenance / 境界

- 本ブランチはDraft #499の固定HEAD `0560a808b6771e94b34ae2b65df6bc1b584b0762` からのスタックです。親 #495、#499 のマージ／受入／公開を意味しません。
- `dayservice.json` と `dayrehab.json` はLibraryから原バイト照合後に取得した当時の候補JSONをGitHubへ写したものです。JSON内の `scope=LIBRARY_ONLY_DRAFT_BRIDGE_NOT_CANONICAL`、`github_changes=NONE` は**生成時点の歴史的スナップショット**を表し、今回のGitHub反映後の現在状態を示す項目ではありません。
- 元Libraryの原バイトSHA-256：通所介護 `6f56b25783088ea6b9cdcfc05333aa3748fabab8bab1662150c4272c795a989c`／通所リハ `8773748d93f8d0aa854313e7482cac60211dcc5fe580d751b2e32c891cb88508`。
- 各項目には `KR-BRIDGE-NNN-XX`、`KR-EVIDENCE-NNN`、Library ID、元出典の識別子候補と文章を保持します。これは**候補への参照**であり、正確な原文・施行版・準用・条例・Q&A・算定適用の確認ではありません。
- 第2段階の12件にある`NOT_ESTABLISHED`や原典PDFの「（略）」を補完・昇格しません。
- 通所リハの15章IDは非公開39サービス骨格との機械的一致を確認済みですが、ドメイン上の**正式な章割当承認ではありません**。

## 検証

```bash
python -m unittest discover -s tests -p 'test_handbook_evidence_bridges.py' -v
python -m unittest discover -s tests -p 'test_dayservice_handbook*.py' -v
```

確認ポイント：15章IDの一意性、サービス混入排除、11+18件の候補ID重複防止、参照Library ID、公開・人手レビューの否定状態、2つのHTMLへの固定データ埋込、既存65草稿と27+11原典候補の保存、`connect-src 'none'` と安全なテキストDOM構築、既存メモ処理の残存。

コード検証がPASSでも、Android・実ブラウザ動作、人手による法令現行性の確認、本番適用・公開は**別ゲート**です。Draftのまま保持し、明示の承認なしにmainへマージしたりサイトへ出さないでください。
