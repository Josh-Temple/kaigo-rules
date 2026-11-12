# 公開先の切り分け（2026-11-13 決定）

Kaigo Rules の **正式版（本番）は GitHub Pages** とする。

- 正式版: https://josh-temple.github.io/kaigo-rules/
- Vercel 版（kaigo-rules.vercel.app）は正式版ではない。旧公開の凍結扱いとし、
  新規の正規デプロイ先としては使わない。
- kaigo-ops（ops-site）は別プロダクトであり、この決定の対象外
  （従来どおり Vercel へデプロイする）。

## 移行ステップ

1. GitHub Pages の生成・監査スクリプト群とテストを、現在の固定コミット
   （`14ec4a26…`）側のツリーから main へ移植する。公開範囲・現行性・
   実機・印刷の独立受入を前提とし、省略しない。
2. Pages ワークフロー（`.github/workflows/kaigo-pages-public-beta-main.yml`）を
   main 追随に変更する: 固定コミットのチェックアウトをやめ、main への push と
   同一SHAで再デプロイする。安全監査と noindex、出典に関する注意書きは維持する。
3. 日次 Vercel ワークフロー（`.github/workflows/daily-vercel-production-deploy.yml`）
   から kaigo-rules のデプロイ・本番検証・状態記録を除去し、kaigo-ops のみを
   対象にする。除去後に Secret `VERCEL_DEPLOY_HOOK_KAIGO_RULES` を削除する。
4. 凍結した Vercel 版プロジェクトの削除要否は、Pages 正式版の表示と内容を
   実画面で確認した後に別途判断する。

## 留意事項

- この文書は決定の記録であり、main へのマージや公開そのものを許可するものではない。
- noindex は、独立した出典審査が整うまで維持する。
- 未確認の制度情報の扱い（確認状態の区別）は従来方針を変えない。
