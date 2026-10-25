# A：人員配置条件の一次資料限定照合（2026-10-26）

対象起点 main：`5633ff77c3323e9e1dc4893a155f2fb64090ce2d`。対象は手引の `staffing` 4章のみ。新規独立要件を増やさず、既存6要件の説明を原典で確認できた範囲に限って追記した。変更前の原文・対応IDはGit diff及び旧版の変換台帳に保存される。

| サービス | 要件ID | 限定照合のポイント | 原典 |
|---|---|---|---|
| homebath | mesh-d-nurse | 事業所配置（第45条）と訪問時編成・医師意見の確認（第50条第6号）を分離 | [省令37号](https://www.mhlw.go.jp/web/t_doc?dataId=82999404&dataType=0) 第45条、第50条第6号 |
| homenursing | mesh-station-nursing-fte | ステーションの2.5常勤換算、看護職員の常勤1名、リハ職の別枠、病院・診療所の適当数を区別 | 同 第60条第1〜2項 |
| homenursing | mesh-manager-qualification | 管理者の保健師・看護師資格とやむを得ない理由による例外、対象事業所を区別 | 同 第61条第2項 |
| shortstay-life | mesh-full-time-attached-exception | 併設かつ利用定員20人未満の「常勤配置のみ」の例外。利用定員と前年度平均を混同しない | 同 第121条第1・3・5項 |
| community-specific-facility | mesh-point-nine-ratio | 3対1を0.9に緩和する対象条項、分母、全4条件、緩和されない条件を明記 | [省令34号](https://www.mhlw.go.jp/web/t_doc?dataId=82aa7858&dataType=0) 第110条第1・2・4・11項 |
| community-specific-facility | mesh-point-nine-committee | 委員会5事項の検討・定期確認と、残る3条件を区別 | 同 第110条第11項、第129条で準用する第86条の2 |

## 範囲と保留
- 厚生労働省の掲載条文を該当条項に限定して照合。国の解釈通知・個別Q&A・2026年10月26日現在の全改正沿革・横浜市等の条例・施設別適用・有資格者による法的受入は未完了。
- 元の459件の `EVIDENCE_GAP` と `SOURCE_CANDIDATE_UNVERIFIED` は格上げしない。出典候補に未検証リンクや架空の確認日時を追加しない。
- 病院・診療所、一体運営、基準該当、ユニット型等の未変更要件は、この変更をもって確認済みとしない。
- `docs/handbook-quality/2026-10-25-research-mesh-integration.json` の6件分の読者文章hashのみ更新し、元ZIP・REVIEW・INTEGRATE識別子、元ルール及びその他453件は改変しない。
- `tests/a-staffing-20261026-primary-evidence.test.mjs` が6件の固定文章hashと対象条件・未確認状態を検査する。既存の統合・手引回帰試験と併用する。
- Aは独立実装PRまでとし、Dの独立受入およびEのマージ・Production反映は行わない。
