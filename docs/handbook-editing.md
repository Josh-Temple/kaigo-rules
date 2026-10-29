# サービス別手引の追記

全39サービスに15章ずつの手引があります。

- サービスの目次と概要：`/services/<service_id>`
- 各章の詳細：`/handbook/<service_id>/<章IDのアンダースコアをハイフンにした値>`
- 法令等を条文順に読む：`/legislation`

`/legislation` はサービス・資料の種類・法令／通知・キーワードで絞り込めます。ページ送りと項目ごとの固定リンクでも条件を保持します。法令は枝番号を含む条番号順、通知・報酬は収載元の並びで表示します。未収載の本文を推測して生成しません。

## 解説を追記する

`data/handbook-content.json` にサービス・章ごとの追記を書きます。

```json
{
  "schema_version": 1,
  "services": {
    "homebath": {
      "chapters": {
        "staffing": {
          "summary": "この章の概要を記載します。",
          "paragraphs": ["追記する説明文です。"],
          "checkpoints": ["確認する項目を記載します。"]
        }
      }
    }
  }
}
```

指定した項目だけ置き換えます。章のID、順番、資料の対応、確認状態はこのファイルから変更しません。原典や資料の対応を追加する場合は、既存のサービス別scope・索引・共有コーパスへ追記します。

```bash
npm run build:handbook
npm run check:handbook
npm run test:handbook
npm run build
```

生成される2ファイルは直接編集せず、Gitには含めません。開発サーバー起動前・本番ビルド前に、コミット済みの正本から自動生成します。編集内容と生成スクリプトをコミットします。

- `data/handbook.generated.json`：39サービス・585章の概要、確認項目、資料ID。
- `data/legal-browser.generated.json`：共有条文、通知・報酬索引、既存のサービス参照。

## 掲載内容と確認状態

2026-10-19の利用者指示に従い、確認前の解説・資料対応を作成中の手引として公開します。既存の人手確認、現行性、適用範囲、受入判定の正本は更新しません。旧版、改正対照資料、通知の整理メモ、数値のみの索引は区別して表示します。準用条文の本文は読替え前の原文です。

従来のDB・詳細ページと限定プレビューは従来の経路を保持します。今回の新しい作成中手引を、旧Waveの独立受入完了や人手確認完了と扱いません。

## 通所介護の表示

通所介護の手引は国の原典を項目ごとに読む専用の表示を使います。対応表は `lib/handbook/dayservice-national-reader.ts`、表示は `components/dayservice-handbook.tsx` です。`handbook-content.json` の自作説明をそのまま出す経路とは区別します。編集方針・Q&Aの原問照合記録は [通所介護の構成変更](dayservice-national-reader-20261030.md) を参照してください。
