# PR #593 / 担当C — 静的配布物の安全監査とActions実行計画

作成：2026-11-04 JST。Cの起点はPR #593 HEAD `5da836c1896656deafab4b8285fc46a6b56e687f`。
**公開判断ではない**。Bが公開対象を選別する実装、Aによる候補照合、Eの固定SHA、Dの独立承認は別工程。
`HOLD_NO_MAIN_MERGE / NO_DEPLOY`。既存のPages/Vercel本番は変更しない。

## 実装した独立ゲート

- `scripts/audit_github_pages_scope_gate.py`：生成済みの**同一ディレクトリ**を変更せずに監査する。HTML/JSON/JS/MJS/CSS/TXT/SVG/XML全件、gzipとの原文一致、全配布ファイルのSHA-256、配布ツリーの集計SHA、容量、symlink、秘密情報の兆候、内部表示、noindex/試験版警告、旧Vercelドメイン文字列の拡張子別件数を点検。
- 法令の`legislation/records.json`・`record-index.json`・IDから導出した直接詳細URL、`databases/search/global.json`・`service-*.json`の行ID、Q&A検索IDと`qa-details/{id}/index.html,reader.html`を、**個別に承認された集合**と照合する。未知・欠落・重複・未承認IDを拒否。
- 非公開の承認情報は対象配布ディレクトリの外側からのみ読み込む。全ファイルの**完全一致ハッシュ**も別承認と照合するため、承認対象にないJS/HTML/JSON等の追加・改変は拒否する。
- 承認情報がない・状態が候補止まり・source SHAが違う・許可集合が空の場合、終了コード2で`HOLD_NO_DEPLOY`。レポートは件数とエラー種別中心で、秘密情報値や全文は含めない。
- **制約**：ハッシュ一致はレビュー済みバイト列との同一性の証拠であり、内容の法令適格性やレビュー権限を暗号学的に証明しない。Aの`CANDIDATE_SOURCE_MATCH`や`publish_approved:false`を承認へ昇格しない。JSで組み立てられるURLの**文字列出現数**は分類できるが、実行時URL・HTMLの意味・全外部リンクの到達可能性・端末操作は別検査。
- `tests/test_github_pages_scope_gate.py`と`tests/test_github_pages_actions_safety.py`に失敗系・CI制御の回帰テストを追加した。**Cセッションではテスト実行環境が揃わず、実行結果はNOT_RUN**。成功を主張しない。

## 独立承認ファイルの契約（例示のみ、未発行）

個人/法律情報を含む未審査コーパス自体を承認ファイルへ転記しない。公開前にDが対象SHAと配布バイトを評価し、EがD承認の所在と独立性を再確認する。承認ファイルは生成物から**自動作成してはならない**。

```json
{
  "schema_version": 1,
  "source_sha": "<exact-40-char-SHA>",
  "decision": "D_ACCEPTED_SCOPED",
  "records": {
    "legal": [{"id": "<legal-id>", "publish_approved": true, "state": "APPROVED_FOR_PUBLICATION", "source_url": "https://..."}],
    "documents": [{"id": "<document-id>", "publish_approved": true, "state": "APPROVED_FOR_PUBLICATION", "source_url": "https://..."}],
    "qa": [{"id": "<qa-id>", "publish_approved": true, "state": "APPROVED_FOR_PUBLICATION", "source_url": "https://..."}],
    "search": {
      "global.json:qa": [{"id": "<qa-id>", "publish_approved": true, "state": "APPROVED_FOR_PUBLICATION", "source_url": "https://..."}]
    }
  },
  "file_sha256": {"index.html": "<exact-64-char-SHA256>", "...": "..."}
}
```

`search`は各`global.json:<group>`と`service-<id>.json:<group>`について、実出力の**全グループと各行ID**を指定する。文書とQAの識別子に別名がある場合はそれも個別承認が必要。承認対象は**実生成物の全ファイル**であり、`.nojekyll`も含める。`mode=beta`は全HTML noindex＋試験版警告、`mode=private`は全HTML noindex、`mode=public`は残留noindex禁止とモード別の安全確認を行う。

## E向け：単一生成物・3監査の実行順

```bash
set -euo pipefail
test "$(git rev-parse HEAD)" = "$FIXED_SHA"
# まずPython・Node小テスト。生成はEが承認条件確認後に原則1回。
python -m unittest tests/test_github_pages_scope_gate.py tests/test_github_pages_actions_safety.py tests/test_github_pages_migration_readiness.py tests/test_github_pages_legacy_links_audit.py
node --test tests/github-pages-static-history.test.mjs tests/github-pages-static-search-more.test.mjs
# 正当な承認ファイルが存在しない段階では一切アップロードしない。
# PRIVATE_SITE はEの非公開・短命な場所で作った固定SHAの実出力。
python scripts/audit_github_pages_migration_readiness.py "$PRIVATE_SITE" > "$PRIVATE_EVIDENCE/readiness.json"
python scripts/audit_github_pages_legacy_links.py "$PRIVATE_SITE" --output "$PRIVATE_EVIDENCE/legacy.json"
# 承認前はexit 2 + HOLD_NO_DEPLOYが**期待結果**。監査出力だけを保存する。
python scripts/audit_github_pages_scope_gate.py "$PRIVATE_SITE" --source-sha "$FIXED_SHA" --mode private --hash-inventory "$PRIVATE_EVIDENCE/file-hashes.json" > "$PRIVATE_EVIDENCE/scope.json"
```

最後のコマンドは承認なしで**非ゼロ終了**するため、Eは安全なHOLDを期待する場合だけ明示的に捕捉する。ファイルハッシュ一覧は`$PRIVATE_EVIDENCE`のみに保存し、公開Actions artifact/Pagesへアップロードしない。真正な独立承認受領後だけ`--approval "$PRIVATE_EVIDENCE/approved-scope.json"`を指定する。リリース変換後のバイトは**別の完全一致承認**を要求する。配布後にファイル追加・改変しない。

## workflowの条件と予算

| workflow | 起動条件・実行する内容 | Cの変更と節約 |
|---|---|---|
| `kaigo-pages-continuous-beta.yml` | PRは安全小テスト、main push/manualはowner変数＋mode fileが必要 | **第三条件：独立承認ファイル存在**がなければpackageジョブに進まない。upload直前に同一出力の全ファイル監査 |
| `github-pages-feasibility.yml` | main向けPRは安全小テスト、manualは計測用フルビルド | C監査テストをPRに追加。フルビルドの自動化なし |
| `kaigo-pages-release.yml` | 手動のみ、main固定SHA＋別レビューcommitが必要 | ビルド前に個別承認ファイル2件の存在確認、変換前・変換後の全配布ファイルを別々に承認照合 |
| `validate-build.yml` | main／指定ブランチpush、main向けPR、manual | 重い全件検証は残し、既存必須チェックを削除していない |
| `verify-publication-readiness-integration.yml` | data/scriptsを含むPR、manual | 法令・公開範囲変更では引き続き起動。自動無効化しない |
| `kaigo-issue569-browser-acceptance.yml` | 対象パスを変えたmain等向けPR、manual | Dの独立実ブラウザ受入が必要。Cでは起動せず |
| 現行性監視・Vercel条件付きdeploy | schedule/manual（一部PR/push） | 未編集・未停止 |

**新規runner使用：Cによる手動起動0回。** ブランチ作成/commitだけでは主なmain push/PRワークフローを起動しない。GitHub側の全run照合・請求分換算は別記録でfresh確認。Wave共通runner目標30分以内。Eは小テスト→承認/対象集合のゲート→必要時だけ一度の非公開フル生成の順で実施。Dのブラウザ/印刷runはEのビルドとSHA一致時だけ再利用可。CIが成功してもDの受入とはみなさない。

## 保留事項

1. Aによる現行版照合と、Dの**実際の公開承認ID集合**が未提出。ファイルハッシュの承認receiptは生成しない。
2. Bが出力する検索行ID・法令文書ID・QA別名・公開対象制限をEが本監査スキーマと照合し、必要なら範囲を拡大せず両者を調整する。
3. 実HTML/JSON/JS/CSS/gzipの全件件数・容量・旧Vercel残件・リンク切れは**未測定**。DのChromium・印刷・実AndroidもC担当では未実施。
4. 本監査は原典の現行性、ブラウザの実挙動、JS構築URLのすべて、悪意ある漏えいの完全な不在を保証しない。false positive/negativeはD・Eが別途検証する。
5. 承認の真正性は外部のレビュー手続に依存する。JSONの`decision`文字列だけでは、Dの署名や権限検証にはならない。

**引渡し**：EはC branchから6変更ファイルと本手順をファイル単位で精査して取り込み、Bが変更した生成処理に合わせてテストを通す。禁止事項は変わらない。
