# 老企第25号 通所介護22項目・独立機械監査

- 監査日: 2026-09-23
- fresh read main SHA: 02147c9dcfe53c5702e47ddbc08a5326004db116
- 機械監査のみ。HUMAN_VERIFIED / VERIFIED_CURRENTではない。

## 判定集計

| 判定 | 件数 |
|---|---:|
| AUDIT_PASS | 0 |
| AUDIT_PASS_WITH_LIMITATION | 0 |
| HOLD | 22 |
| MISMATCH | 0 |

snapshotからの順方向replayでは 22/22 件が、空白除去後に候補と一致。後続改正の網羅性を確認できないため全件HOLD。候補一致は現行性の証明ではない。

## 高リスク項目

- 従業者の員数 (notice.dayservice.personnel.staffing, risk 10/10): 長文・8項目・計算式・数値・H30/R3改正
- 業務継続計画の策定等 (notice.dayservice.operation.bcp, risk 9/10): R3新設後R6に経過措置と一体的策定記述を更新
- 指定通所介護の基本取扱方針及び具体的取扱方針 (notice.dayservice.operation.policy, risk 9/10): R6新③挿入、旧③/④繰下げ、例外・要件・保存期間
- 衛生管理等 (notice.dayservice.operation.hygiene, risk 8/10): R3新設後R6に経過措置文を削除、列挙・複数頁
- 通所介護計画の作成 (notice.dayservice.operation.plan, risk 8/10): H30/R3の条番号・参照番号更新、頁跨ぎ

## 共通所見

- currentness/source coverage: 令和6年版以後の対象項目を網羅する現行統合本文・公式な全改正履歴を確認できない。001453049.pdfは令和7年3月改訂国マニュアルで掲載され、令和8年3月改訂ページでも再掲されているが部分参照。 22項目をHOLDとし、歴史資料からの一致を現行性の証明にしない。
- stale verification provenance: 既存PASS記録はSHA dc92f9c82555e8fcb70dcff3c6dca07166d58af3。fresh read main SHA 02147c9dcfe53c5702e47ddbc08a5326004db116とは異なる。 既存PASSを今回の結論に使用していない。
- unsupported current-as-of metadata: packetのeffective_as_of=2026-09-23は再構成日を示すメタデータであり、この監査で現行性を裏付ける資料ではない。 現在性の証拠が足りない項目はHOLD。
- visual/extraction coverage: 別抽出テキストとMHLW PDF表示を代表的な改正箇所で確認したが、全22項目・全ページを人が目視した監査ではない。 OCR、左右段組み、頁跨ぎ、脚注の残存リスクを個別記録。

## 22項目一覧

| notice_id | 項目 | candidate SHA-256 | 判定 | replay | baseline → amendments |
|---|---|---|---|---|---|
| notice.dayservice.personnel.staffing | 従業者の員数 | abc3729d4687… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 → 平成30年度改正後・新旧対照表 → 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.personnel.life-counselor | 生活相談員 | fbd9bfa5fd41… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 |
| notice.dayservice.personnel.function-training | 機能訓練指導員 | 382d6eb740a2… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成30年度改正後・新旧対照表 |
| notice.dayservice.personnel.manager | 管理者 | 3ebd100c715f… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 |
| notice.dayservice.equipment.office | 事業所 | 2e66494484b4… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 |
| notice.dayservice.equipment.dining-training-room | 食堂及び機能訓練室 | 44a948061e78… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成30年度改正後・新旧対照表 |
| notice.dayservice.equipment.fire-safety | 消火設備その他の非常災害に際して必要な設備 | 4039debb8372… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 |
| notice.dayservice.equipment.shared-equipment | 設備に係る共用 | 174bf34fb6a0… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成30年度改正後・新旧対照表 |
| notice.dayservice.equipment.overnight-service | 指定通所介護事業所の設備を利用し、夜間及び深夜に指定通所介護以外のサービスを提供する場合 | fd775ba78801… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 |
| notice.dayservice.operation.fees | 利用料等の受領 | fbd7941a972a… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 → 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.policy | 指定通所介護の基本取扱方針及び具体的取扱方針 | dbf79626dc9c… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 → 令和6年度改正後・新旧対照表 → 令和6年度改正後・新旧対照表 → 令和6年度改正後・新旧対照表 |
| notice.dayservice.operation.plan | 通所介護計画の作成 | f7ee9ba310e0… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 → 平成30年度改正後・新旧対照表 → 令和3年度改正後文を含む新旧対照表 → 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.rules | 運営規程 | 5e3d5b7d3e12… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 → 平成30年度改正後・新旧対照表 → 令和3年度改正後文を含む新旧対照表 → 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.staffing | 勤務体制の確保等 | ffadabb22e70… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 平成27年度改正後・新旧対照表 → 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.bcp | 業務継続計画の策定等 | fb03a61a735c… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 → 令和6年度改正後・新旧対照表 → 令和6年度改正後・新旧対照表 |
| notice.dayservice.operation.disaster | 非常災害対策 | 30761dfe8e63… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.hygiene | 衛生管理等 | 738776321efe… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 → 令和6年度改正後・新旧対照表 |
| notice.dayservice.operation.community | 地域との連携等 | b92867657a8c… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.accident | 事故発生時の対応 | e6bf847bec76… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.abuse | 虐待の防止 | 9afcfcfaec9f… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.records | 記録の整備 | f221bf8da5cc… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和3年度改正後文を含む新旧対照表 |
| notice.dayservice.operation.incorporation | 準用 | 24dc8d78aa07… | HOLD | EXACT_AFTER_WHITESPACE_REMOVAL | 令和7年3月改訂国マニュアル掲載の部分参照資料 |

## notice.dayservice.personnel.staffing — 従業者の員数

- number_path: 第3 / 六 / 1 / (1)
- candidate SHA-256: abc3729d4687d2d11581103a8e9bbfb8fb4d48fefae285e8aa82604b532cace9
- 判定: HOLD
- independent replay SHA-256: b50bac1fa744e93269155152f658ffa30577a2a8a050ce29120fb3dfd1680363
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.45–49、right欄（改正前|改正後）
- baseline開始: ①指定通所介護の単位とは、同時に、一体的に提供される指定通所介護をいうものであることから、例えば、次のような場合は、２単位として扱われ、それぞれの単位ごとに必要な従業者を確保する必要がある。イ指定通所…
- baseline終了: …者の数と午後の利用者の数が合算されるものではない。⑧同一事業所で複数の単位の指定通所介護を同時に行う場合であっても、常勤の従業者は事業所ごとに確保すれば足りるものである（居宅基準第93条第７項関係）。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.45–49 baseline: H27改正後欄の従業者の員数①〜⑧。H30とR3の後続改正を順方向に適用するbaseline。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
  - 2018 平成30年度改正後・新旧対照表 p.12–12 replace_between: H30で7時間以上9時間未満→8時間以上9時間未満へ更新 (PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa)
  - 2021 令和3年度改正後文を含む新旧対照表 p.30–31 replace_between: R3で看護職員の確保方法をア・イに分けて再構成 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2018-04-01 replace_fragment: 延長サービスに係る人員配置の対象時間を「7時間以上9時間未満」から「8時間以上9時間未満」へ更新。 [source_in_forward_replay]
  - 2021-04-01 replace_fragment: 看護職員の確保方法について、事業所の従業者により確保する場合と、病院・診療所・訪問看護ステーションとの連携により確保する場合をア・イに分けて具体化。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.[12, 12]: PATCH_REPLAYED
  - 2021 令和3年度改正後文を含む新旧対照表 p.[30, 31]: PATCH_REPLAYED
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.45-49を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.personnel.life-counselor — 生活相談員

- number_path: 第3 / 六 / 1 / (2)
- candidate SHA-256: fbd9bfa5fd410c45faaa5fb51150ba36e6d683667dd9bd4a6a0154f77b02c291
- 判定: HOLD
- independent replay SHA-256: 863d598a72a92d44ba19a7e9a37886f2b71a1e57281076b3cd7695c31a0c7771
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.49–49、right欄（改正前|改正後）
- baseline開始: 生活相談員については、特別養護老人ホームの設備及び運営に関する基準（平成11年厚生省令第46号）第５条第２項に定める生活相談員に準ずるものである。…
- baseline終了: …生活相談員については、特別養護老人ホームの設備及び運営に関する基準（平成11年厚生省令第46号）第５条第２項に定める生活相談員に準ずるものである。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.49–49 baseline: H27改正後欄。その後H30/R3/R6では本文変更を示さず略記。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.49-49を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.personnel.function-training — 機能訓練指導員

- number_path: 第3 / 六 / 1 / (3)
- candidate SHA-256: 382d6eb740a2fd95e3bac8dd58a80b4635b44ea039433a89984e4c4cc9780dec
- 判定: HOLD
- independent replay SHA-256: 3360aac5a9fe5b882a3b4f5a7698687bb37756391ffa565386f032cb2b6f8ebf
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成30年度改正後・新旧対照表、https://www.mhlw.go.jp/content/12404000/001623023.pdf、PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa、p.12–13、left欄（新|旧）
- baseline開始: 機能訓練指導員は、日常生活を営むのに必要な機能の減退を防止するための訓練を行う能力を有する者とされたが、この「訓練を行う能力を有する者」とは、理学療法士、作業療法士、言語聴覚士、看護職員、柔道整復師、…
- baseline終了: …機能訓練指導に従事した経験を有する者に限る。）とする。ただし、利用者の日常生活やレクリエーション、行事を通じて行う機能訓練については、当該事業所の生活相談員又は介護職員が兼務して行っても差し支えない。
- 改正順:
  - 2018 平成30年度改正後・新旧対照表 p.12–13 baseline: H30改正後欄。はり師・きゅう師に関する資格要件追加後の本文。 (PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2018-04-01 replace_fragment: 一定の実務経験を有するはり師・きゅう師を機能訓練指導員の資格対象へ追加。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.12-13を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.personnel.manager — 管理者

- number_path: 第3 / 六 / 1 / (4)
- candidate SHA-256: 3ebd100c715f289ecea6d7c4ab3edd4f33db26a609f131b7075ac083c845d644
- 判定: HOLD
- independent replay SHA-256: 07192aebdf8a93ad79eb52dc650448b33c9ca4237a8fe93e18464dd7454161bd
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.49–49、right欄（改正前|改正後）
- baseline開始: 訪問介護の場合と同趣旨であるため、第三の一の１の⑶を参照されたい。…
- baseline終了: …訪問介護の場合と同趣旨であるため、第三の一の１の⑶を参照されたい。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.49–49 baseline: H27改正後欄。その後の通所介護人員節改正で本文変更を示されていない。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.49-49を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.equipment.office — 事業所

- number_path: 第3 / 六 / 2 / (1)
- candidate SHA-256: 2e66494484b422ae15e2f9ff0a03689281c1f2901ed46f19eadc671160ef5492
- 判定: HOLD
- independent replay SHA-256: b844f47f438eab5884707101d799d730d925c13ee03e472ec14dba91ea5ed1d6
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.49–49、right欄（改正前|改正後）
- baseline開始: 事業所とは、指定通所介護を提供するための設備及び備品を備えた場所をいう。原則として一の建物につき、一の事業所とするが、利用者の利便のため、利用者に身近な社会資源（既存施設）を活用して、事業所の従業者が…
- baseline終了: …用者の利便のため、利用者に身近な社会資源（既存施設）を活用して、事業所の従業者が当該既存施設に出向いて指定通所介護を提供する場合については、これらを事業所の一部とみなして設備基準を適用するものである。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.49–49 baseline: H27改正後欄。H30以後は当該項目を略として保持。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.49-49を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.equipment.dining-training-room — 食堂及び機能訓練室

- number_path: 第3 / 六 / 2 / (2)
- candidate SHA-256: 44a948061e780d24c9cba1727139c0eb8f451e6e6017780e8cd31600c932ca01
- 判定: HOLD
- independent replay SHA-256: 0f960c22e6788167cb29ecb7d92dde77d30f7e0b1a9947c8318144c864ddc116
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成30年度改正後・新旧対照表、https://www.mhlw.go.jp/content/12404000/001623023.pdf、PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa、p.13–13、left欄（新|旧）
- baseline開始: 指定通所介護事業所の食堂及び機能訓練室（以下「指定通所介護の機能訓練室等」という。）については、３平方メートルに利用定員を乗じて得た面積以上とすることとされたが、指定通所介護が原則として同時に複数の利…
- baseline終了: …であることに鑑み、狭隘な部屋を多数設置することにより面積を確保すべきではないものである。ただし、指定通所介護の単位をさらにグループ分けして効果的な指定通所介護の提供が期待される場合はこの限りではない。
- 改正順:
  - 2018 平成30年度改正後・新旧対照表 p.13–13 baseline: H30新欄。(2)旧②の共用記述は削除され、新設(4)へ再構成された後の本文。 (PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2018-04-01 split_and_relocate_fragment: 設備(2)の旧②にあった併設施設との共用記述を(2)から外し、対象範囲を拡張した「設備に係る共用」を新(4)として独立。改正後の(2)は旧①相当の本文のみ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.13-13を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.equipment.fire-safety — 消火設備その他の非常災害に際して必要な設備

- number_path: 第3 / 六 / 2 / (3)
- candidate SHA-256: 4039debb83727a49cac04ab90b4f2519c8fc409e19689bec2630b73e9bfe7cdc
- 判定: HOLD
- independent replay SHA-256: 590b0fb44d183e6ecfb631b02fdaa444a75859606b75db26c2e11085336552a3
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.50–50、right欄（改正前|改正後）
- baseline開始: 消火設備その他の非常災害に際して必要な設備とは、消防法その他の法令等に規定された設備を示しており、それらの設備を確実に設置しなければならないものである。…
- baseline終了: …消火設備その他の非常災害に際して必要な設備とは、消防法その他の法令等に規定された設備を示しており、それらの設備を確実に設置しなければならないものである。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.50–50 baseline: H27改正後欄。H30新欄では(3)を略として保持。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.50-50を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.equipment.shared-equipment — 設備に係る共用

- number_path: 第3 / 六 / 2 / (4)
- candidate SHA-256: 174bf34fb6a0451b20770a507e86e793053d495017dc5fec2a0ce6c346c49c60
- 判定: HOLD
- independent replay SHA-256: f8fc792eaecfe600343e8eab37246ada8d4a376ea49151fae78d5b0dda700203
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成30年度改正後・新旧対照表、https://www.mhlw.go.jp/content/12404000/001623023.pdf、PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa、p.13–14、left欄（新|旧）
- baseline開始: 指定通所介護事業所と指定居宅サービス事業所等を併設している場合に、利用者へのサービス提供に支障がない場合は、設備基準上両方のサービスに規定があるもの（指定訪問介護事業所の場合は事務室）は共用が可能であ…
- baseline終了: …準第104条第２項において、指定通所介護事業者は、事業所において感染症が発生し、又はまん延しないように必要な措置を講じるよう努めなければならないと定めているところであるが、衛生管理等に一層努めること。
- 改正順:
  - 2018 平成30年度改正後・新旧対照表 p.13–14 baseline: H30新設(4)の改正後本文。 (PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2018-04-01 insert: 設備に係る共用を(4)として新設し、併設事業所等との設備共用条件を整理。 [source_in_forward_replay]
  - 2018-04-01 split_and_relocate_fragment: 設備(2)の旧②にあった併設施設との共用記述を(2)から外し、対象範囲を拡張した「設備に係る共用」を新(4)として独立。改正後の(2)は旧①相当の本文のみ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.13-14を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.equipment.overnight-service — 指定通所介護事業所の設備を利用し、夜間及び深夜に指定通所介護以外のサービスを提供する場合

- number_path: 第3 / 六 / 2 / (5)
- candidate SHA-256: fd775ba78801b82202c02f079e81a01c2e9c6fdeadddc3fa4d6ebabb2e0ac845
- 判定: HOLD
- independent replay SHA-256: f5c99ca3f367afc280faa2d9609ef823e0b65fd1999b47c0cd0ad8d2fe188c1e
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.50–51、right欄（改正前|改正後）
- baseline開始: 指定通所介護の提供以外の目的で、指定通所介護事業所の設備を利用し、夜間及び深夜に指定通所介護以外のサービス（以下「宿泊サービス」という。）を提供する場合には、当該サービスの内容を当該サービスの提供開始…
- baseline終了: …場合は、変更の事由が生じてから10日以内に指定権者に届け出るよう努めることとする。また、宿泊サービスを休止又は廃止する場合は、その休止又は廃止の日の１月前までに指定権者に届け出るよう努めることとする。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.50–51 baseline: H27新設(4)の本文。H30で本文変更を示さず(5)へ繰下げ。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2015-04-01 insert: 設備基準に、通所介護事業所の設備を利用して夜間・深夜に宿泊サービスを提供する場合の届出等の取扱いを新設。 [source_in_forward_replay]
  - 2018-04-01 renumber: 設備に係る共用の新設に伴い、宿泊サービス関係項目を(4)から(5)へ繰下げ。 [locator_only_not_independently_closed]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.50-51を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.fees — 利用料等の受領

- number_path: 第3 / 六 / 3 / (1)
- candidate SHA-256: fbd7941a972a46acbba8e528485034f121c81089015ca1df90d4e361ee81a9a1
- 判定: HOLD
- independent replay SHA-256: ea292e22c0f4c2fa7570b8295ebfb759a51e949a77559b21e9af0677a22bfe22
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.51–51、right欄（改正前|改正後）
- baseline開始: ①居宅基準第96条第１項、第２項及び第５項の規定は、指定訪問介護に係る第20条第１項、第２項及び第４項の規定と同趣旨であるため、第三の一の３の⑽の①、②及び④を参照されたい。②同条第３項は、指定通所介…
- baseline終了: …びに食事の提供に係る利用料等に関する指針（平成17年厚生労働省告示第419号。以下「指針」という。）の定めるところによるものとし、ホの費用の具体的な範囲については、別に通知するところによるものとする。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.51–51 baseline: H27改正後の(1)全文。R3で①の参照先だけ更新。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
  - 2021 令和3年度改正後文を含む新旧対照表 p.31–31 replace_between: R3で訪問介護側の参照番号を⑽→⑾へ更新 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
  - 2021-04-01 replace_fragment: 利用料等の受領①の訪問介護側参照番号を⑽から⑾へ更新。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.[31, 31]: PATCH_REPLAYED
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.51-51を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.policy — 指定通所介護の基本取扱方針及び具体的取扱方針

- number_path: 第3 / 六 / 3 / (2)
- candidate SHA-256: dbf79626dc9cbabfb63a973d2e77275233066ad5626ed892cd4887116b6ba0da
- 判定: HOLD
- independent replay SHA-256: 1b2d7ddd551d27199b284f095c7056a06b9ee76b9dd8315dd50ca17f13477d62
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.51–52、right欄（改正前|改正後）
- baseline開始: 指定通所介護の基本取扱方針及び具体的取扱方針については、居宅基準第97条及び第98条の定めるところによるほか、次の点に留意するものとする。①指定通所介護は、個々の利用者に応じて作成された通所介護計画に…
- baseline終了: …が、次に掲げる条件を満たす場合においては、事業所の屋外でサービスを提供することができるものであること。イあらかじめ通所介護計画に位置付けられていること。ロ効果的な機能訓練等のサービスが提供できること。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.51–52 baseline: H27改正後の(2)本文。R6で身体的拘束等の新③が入り、旧③④が④⑤へ繰下げ。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
  - 2024 令和6年度改正後・新旧対照表 p.20–21 replace_literal: R6新③挿入に伴う旧③→④ (PDF SHA-256 eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4)
  - 2024 令和6年度改正後・新旧対照表 p.20–21 replace_literal: R6新③挿入に伴う旧④→⑤ (PDF SHA-256 eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4)
  - 2024 令和6年度改正後・新旧対照表 p.20–21 insert_before: R6の身体的拘束等に関する新③を挿入 (PDF SHA-256 eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [locator_only_not_independently_closed]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [locator_only_not_independently_closed]
  - 2024-04-01 replace_or_insert_fragment: 基本取扱方針・具体的取扱方針に身体的拘束等に関する説明・記録の取扱いを追加。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2024 令和6年度改正後・新旧対照表 p.[20, 21]: PATCH_REPLAYED
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: fragment_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.51-52を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.plan — 通所介護計画の作成

- number_path: 第3 / 六 / 3 / (3)
- candidate SHA-256: f7ee9ba310e079af629257f4f2a93719c93ee2ffc17724cade256a10ee220483
- 判定: HOLD
- independent replay SHA-256: 9ca3c2d9acc3f9ad976850c475e006520c5f3121066b07ca07c2e77eba9cfdb0
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.52–53、right欄（改正前|改正後）
- baseline開始: ①居宅基準第99条で定める通所介護計画については、介護の提供に係る計画等の作成に関し経験のある者や、介護の提供について豊富な知識及び経験を有する者にそのとりまとめを行わせるものとし、当該事業所に介護支…
- baseline終了: …行うものとする。⑥居宅サービス計画に基づきサービスを提供している指定通所介護事業者については、第三の一の３の⒀の⑥を準用する。この場合において、「訪問介護計画」とあるのは「通所介護計画」と読み替える。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.52–53 baseline: H27改正後の(3)全文。H30とR3の④、R3の⑥を順方向に更新するbaseline。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
  - 2018 平成30年度改正後・新旧対照表 p.14–14 replace_between: H30で保存記録の参照条文を第104条の3へ更新 (PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa)
  - 2021 令和3年度改正後文を含む新旧対照表 p.31–31 replace_between: R3で保存記録の参照条文を第104条の4へ更新 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
  - 2021 令和3年度改正後文を含む新旧対照表 p.31–31 replace_to_end: R3で訪問介護側の参照番号を⒀→⒁へ更新 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
  - 2018-04-01 replace_fragment: 通所介護計画④の保存記録参照を居宅基準第104条の2第2項から第104条の3第2項へ更新。 [source_in_forward_replay]
  - 2021-04-01 replace_multiple_fragments: 通所介護計画④の保存記録参照を第104条の4へ、⑥の訪問介護側参照番号を⒁へ更新。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.[14, 14]: PATCH_REPLAYED
  - 2021 令和3年度改正後文を含む新旧対照表 p.[31, 31]: PATCH_REPLAYED
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.52-53を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.rules — 運営規程

- number_path: 第3 / 六 / 3 / (4)
- candidate SHA-256: 5e3d5b7d3e1254fe44184a924baa3ae8df8153d8235df31fc3cccfa7773fac9f
- 判定: HOLD
- independent replay SHA-256: 8a20ab633199900834ef5cfcde89f4168d45abfc1ffa30dc04c448f9bab362c4
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.53–54、right欄（改正前|改正後）
- baseline開始: 居宅基準第100条は、指定通所介護の事業の適正な運営及び利用者に対する適切な指定通所介護の提供を確保するため、同条第１号から第10号までに掲げる事項を内容とする規程を定めることを指定通所介護事業所ごと…
- baseline終了: …７号についても同趣旨）。⑤非常災害対策（第９号）⑹の非常災害に関する具体的計画を指すものであること（居宅基準第117条第８号、第137条第８号、第153条第６号及び第189条第８号についても同趣旨）。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.53–54 baseline: H27改正後の(4)全文。H30で①、R3で導入部と⑤を更新。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
  - 2018 平成30年度改正後・新旧対照表 p.15–15 replace_between: H30で延長サービス対象時間を8時間以上9時間未満へ更新 (PDF SHA-256 7a3a439fca5bfadd04aa4e46058326e6e643d92e66f18e2f893e1b40ce6eabaa)
  - 2021 令和3年度改正後文を含む新旧対照表 p.32–32 replace_between: R3で列挙号数を第1号〜第11号へ更新 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
  - 2021 令和3年度改正後文を含む新旧対照表 p.32–32 replace_to_end: R3で非常災害対策の参照を⑺へ更新 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
  - 2018-04-01 replace_fragment: 運営規程①の延長サービス対象時間を7時間以上9時間未満から8時間以上9時間未満へ更新。 [source_in_forward_replay]
  - 2021-04-01 replace_multiple_fragments: 運営規程の対象号数を第1号から第11号までへ更新し、非常災害対策⑤の参照を⑹から⑺へ更新。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.[15, 15]: PATCH_REPLAYED
  - 2021 令和3年度改正後文を含む新旧対照表 p.[32, 32]: PATCH_REPLAYED
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.53-54を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.staffing — 勤務体制の確保等

- number_path: 第3 / 六 / 3 / (5)
- candidate SHA-256: ffadabb22e707d80aa4b5ed968872b547046dc74a802a4bc6382f2d7d8024321
- 判定: HOLD
- independent replay SHA-256: e36824922201b417494156288b03710f7133ceb2f24c1001bd9408c3ecd82331
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 平成27年度改正後・新旧対照表、https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf、PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568、p.54–54、right欄（改正前|改正後）
- baseline開始: 居宅基準第101条は、利用者に対する適切な指定通所介護の提供を確保するため、職員の勤務体制等について規定したものであるが、このほか次の点に留意するものとする。①指定通所介護事業所ごとに、原則として月ご…
- baseline終了: …定通所介護事業所の従業者たる通所介護従業者によって指定通所介護を提供するべきであるが、調理、洗濯等の利用者の処遇に直接影響を及ぼさない業務については、第三者への委託等を行うことを認めるものであること。
- 改正順:
  - 2015 平成27年度改正後・新旧対照表 p.54–54 baseline: H27改正後の(5)本文①②。R3で③④を追加。 (PDF SHA-256 b4eb9f73695e05b1a4b15d3109ff2712b7561ebe47700d01aa151a3722065568)
  - 2021 令和3年度改正後文を含む新旧対照表 p.32–32 append: R3で③④を追加 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
  - 2021-04-01 append_fragments: 勤務体制の確保等に、居宅基準第101条第3項・第4項に関する留意事項③④を追加。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2018 平成30年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2021 令和3年度改正後文を含む新旧対照表 p.[32, 32]: PATCH_REPLAYED
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.54-54を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.bcp — 業務継続計画の策定等

- number_path: 第3 / 六 / 3 / (6)
- candidate SHA-256: fb03a61a735c93ec0b36d4997736ac48dcfbd22e2a5ce04d23c2da982cf4452c
- 判定: HOLD
- independent replay SHA-256: 419bbf181d87b61aa8f974ec8cf5f2620b0ede4a1390c6ca06cfbe25ce550f73
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.32–34、left欄（新|旧）
- baseline開始: ①居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第30条の２は、指定通所介護事業者は、感染症や災害が発生した場合にあっても、利用者が継続して指定通所介護の提供を受けられるよ…
- baseline終了: …ついては、非常災害対策に係る訓練と一体的に実施することも差し支えない。訓練の実施は、机上を含めその実施手法は問わないものの、机上及び実地で実施するものを適切に組み合わせながら実施することが適切である。
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.32–34 baseline: R3新設(6)の改正後全文。R6で①・②の一部が更新されるためbaselineとして利用。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
  - 2024 令和6年度改正後・新旧対照表 p.21–21 replace_between: R6: 経過措置終了文を除いた①に置換 (PDF SHA-256 eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4)
  - 2024 令和6年度改正後・新旧対照表 p.21–22 replace_between: R6: ②導入部を更新し、R3のイ・ロと③・④を継承 (PDF SHA-256 eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 insert: 業務継続計画の策定等を新設。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
  - 2024-04-01 replace_fragment: 経過措置終了に伴う記載整理やガイドライン表現等を更新。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.[21, 21]: PATCH_REPLAYED
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: fragment_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.32-34を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.disaster — 非常災害対策

- number_path: 第3 / 六 / 3 / (7)
- candidate SHA-256: 30761dfe8e638f4e930dde13c4f0da309a01d62c2bd6aa5cbf0e6638fe89c8e0
- 判定: HOLD
- independent replay SHA-256: cebf2f1f285ab48bc100f735382964adf2c6439b3d753e937f29bc170ce4b544
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.34–35、left欄（新|旧）
- baseline開始: ①居宅基準第103条は、指定通所介護事業者は、非常災害に際して必要な具体的計画の策定、関係機関への通報及び連携体制の整備、避難、救出訓練の実施等の対策の万全を期さなければならないこととしたものである。…
- baseline終了: …との密接な連携体制を確保するなど、訓練の実施に協力を得られる体制づくりに努めることが必要である。訓練の実施に当たっては、消防関係者の参加を促し、具体的な指示を仰ぐなど、より実効性のあるものとすること。
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.34–35 baseline: R3改正後(7)本文。R6・2026では(7)略として保持。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.34-35を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.hygiene — 衛生管理等

- number_path: 第3 / 六 / 3 / (8)
- candidate SHA-256: 738776321efe1d14275b46dee7a4f9dea686530fc065b85192d83145c8787849
- 判定: HOLD
- independent replay SHA-256: 6468c4ab10f253c5f29a7b34d549ced63ec4ef2da6fd5302b3a65862be3b847d
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.34–36、left欄（新|旧）
- baseline開始: ①居宅基準第104条は、指定通所介護事業所の必要最低限の衛生管理等について規定したものであるが、このほか、次の点に留意するものとする。イ指定通所介護事業者は、食中毒及び感染症の発生を防止するための措置…
- baseline終了: …分担の確認や、感染対策をした上でのケアの演習などを実施するものとする。訓練の実施は、机上を含めその実施手法は問わないものの、机上及び実地で実施するものを適切に組み合わせながら実施することが適切である。
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.34–36 baseline: R3改正後(8)全文。R6で②の経過措置文のみ削除されるためbaselineとして利用。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
  - 2024 令和6年度改正後・新旧対照表 p.22–22 replace_between: R6: 経過措置終了文を削除した②導入部に置換 (PDF SHA-256 eebad7611a307f02205dce894a5375634f8f84ca66d8555c9a9da0085750e4b4)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
  - 2024-04-01 delete_expired_transition_fragment: 衛生管理等(8)②から、令和6年3月31日まで努力義務とする令和3年改正省令附則の経過措置文を削除。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.[22, 22]: PATCH_REPLAYED
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: fragment_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.34-36を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.community — 地域との連携等

- number_path: 第3 / 六 / 3 / (9)
- candidate SHA-256: b92867657a8cad57deefa53aaca2c547bfdd517cf83ce090eb63771a13b3e276
- 判定: HOLD
- independent replay SHA-256: 20ba79506e2c723f87bd1a0ed3bb5c48317a790cbfbbff2d0141549ab5cd302c
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.36–37、left欄（新|旧）
- baseline開始: ①居宅基準第104条の２第１項は、指定通所介護の事業が地域に開かれた事業として行われるよう、指定通所介護事業者は、地域の住民やボランティア団体等との連携及び協力を行う等の地域との交流に努めなければなら…
- baseline終了: …その他の非営利団体や住民の協力を得て行う事業が含まれるものである。③同条第３項の規定は、指定訪問介護に係る居宅基準第36条の２第２項と基本的に同趣旨であるため、第３の一の３の（29）②を参照されたい。
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.36–37 baseline: R3で新設・再編された(9)本文。R6・2026では(9)〜(12)略として保持。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.36-37を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.accident — 事故発生時の対応

- number_path: 第3 / 六 / 3 / (10)
- candidate SHA-256: e6bf847bec769dcd5b124e8301b2e41a5c01dda620ad4f67cae33a7c20923988
- 判定: HOLD
- independent replay SHA-256: 3b063bea8e158527d196d1eba7b24420fb5e678381d33ff98ade0dca3c97ebbb
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.37–37、left欄（新|旧）
- baseline開始: 居宅基準第104条の３は、利用者が安心して指定通所介護の提供を受けられるよう、事故発生時の速やかな対応を規定したものである。指定通所介護事業者は、利用者に対する指定通所介護の提供により事故が発生した場…
- baseline終了: …たものである。なお、居宅基準第104条の４第２項の規定に基づき、事故の状況及び事故に際して採った処置についての記録は、２年間保存しなければならない。このほか、以下の点に留意するものとする。①～③（略）
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.37–37 baseline: R3改正後(10)本文。R6・2026では(9)〜(12)略として保持。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.37-37を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.abuse — 虐待の防止

- number_path: 第3 / 六 / 3 / (11)
- candidate SHA-256: 9afcfcfaec9f6b90cc0d59f0a2586e1438997d889d998e1a8531c37274367322
- 判定: HOLD
- independent replay SHA-256: ac01bdfb97cbb40ad748556888e540b1861dcc79763cfbe5967fcede2a8e7e4b
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.37–37、left欄（新|旧）
- baseline開始: 居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第37条の２の規定については、訪問介護と同様であるので、第３の一の３の(31)を参照されたい。…
- baseline終了: …居宅基準第105条の規定により指定通所介護の事業について準用される居宅基準第37条の２の規定については、訪問介護と同様であるので、第３の一の３の(31)を参照されたい。
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.37–37 baseline: R3新設(11)本文。R6・2026では(9)〜(12)略として保持。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.37-37を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.records — 記録の整備

- number_path: 第3 / 六 / 3 / (12)
- candidate SHA-256: f221bf8da5cc08bcefc34d88ed80993529e1cb1d0f3e8f54a8c55e83df34db29
- 判定: HOLD
- independent replay SHA-256: 4c2552ffadf61f649674a3a8fb7d150c42a93d349153f0ccd9f500885de54822
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和3年度改正後文を含む新旧対照表、https://www.mhlw.go.jp/content/12300000/000869798.pdf、PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486、p.37–38、left欄（新|旧）
- baseline開始: 居宅基準第104条の４第２項は、指定通所介護事業者が同項各号に規定する記録を整備し、２年間保存しなければならないこととしたものである。なお、「その完結の日」とは、個々の利用者につき、契約終了（契約の解…
- baseline終了: …こととしたものである。なお、「その完結の日」とは、個々の利用者につき、契約終了（契約の解約・解除、他の施設への入所、利用者の死亡、利用者の自立等）により一連のサービス提供が終了した日を指すものとする。
- 改正順:
  - 2021 令和3年度改正後文を含む新旧対照表 p.37–38 baseline: R3新設(12)本文。R6・2026では(9)〜(12)略として保持。 (PDF SHA-256 83a9c86d0ad03c9399fbc1fd599ab53c9b5f78a449abd04cf0e3dcb6d187b486)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [source_in_forward_replay]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [source_in_forward_replay]
- baseline後の公式赤線資料（未適用は不改正の証明にしない）:
  - 2024 令和6年度改正後・新旧対照表 p.None: NOT_IN_REPLAY_NO_NO_CHANGE_INFERENCE
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.None: PARTIAL_REFERENCE_ONLY
- 2025年3月掲載の部分参照: not_full_target_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.37-38を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## notice.dayservice.operation.incorporation — 準用

- number_path: 第3 / 六 / 3 / (13)
- candidate SHA-256: 24dc8d78aa074711d32b295b462a452c6b44c334ae5b98805d1a5c1c17cc88bb
- 判定: HOLD
- independent replay SHA-256: e43bebe348dcd01f41df6629c70b33b5d934113a09edde01bdf4ae58a45ce47a
- candidate comparison: EXACT_AFTER_WHITESPACE_REMOVAL (Whitespace removal only. No NFKC normalization; punctuation, digits, symbols, and numeral glyphs are retained.)
- baseline: 令和7年3月改訂国マニュアル掲載の部分参照資料、https://www.mhlw.go.jp/content/12304250/001453049.pdf、PDF SHA-256 36dbf483345fa9e9512f6610249989ef4b4acbe8daa19030c12e2220a8a66791、p.22–22、left欄（新|旧）
- baseline開始: 居宅基準第105条の規定により、居宅基準第８条から第17条まで、第19条、第21条、第26条、第27条、第30条の２、第32条から第34条まで、第35条、第36条、第37条の２、第38条及び第52条は…
- baseline終了: …供に係る利用料等に関する指針（平成17年厚生労働省告示第419号）一のハに規定するウェブサイトへの掲載に関する取扱いは、準用される居宅基準第32条に関する第３の一の３の(24)の①に準ずるものとする。
- 改正順:
  - 2025-03 令和7年3月改訂国マニュアル掲載の部分参照資料 p.22–22 baseline: 2026年3月厚労省参照資料の新欄に現れる(13)準用の現行側全文。 (PDF SHA-256 36dbf483345fa9e9512f6610249989ef4b4acbe8daa19030c12e2220a8a66791)
- amendment-event索引との照合（索引はlocator扱い）:
  - 2021-04-01 insert_multiple: 地域との連携等、虐待の防止、記録の整備等を追加し、事故発生時の対応・準用を含む運営項目を(13)まで再編。 [locator_only_not_independently_closed]
  - 2021-04-01 renumber: BCP新設に伴い、非常災害対策を(6)→(7)、衛生管理等を(7)→(8)へ繰下げ。 [locator_only_not_independently_closed]
  - 2024-04-01 insert_fragment: 準用に関連してウェブサイト掲載の取扱いを追記。 [locator_only_not_independently_closed]
- 2025年3月掲載の部分参照: full_text_in_2026_partial_reference
- currentness: 未解決。2024年以後の対象項目を網羅する現行統合通知または公式な完全改正履歴を確認できない。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料で、令和8年3月改訂ページでも再掲されているが、網羅性の証明にはならない。
- 残存リスク: 後続改正の網羅性を一次資料で確証できていない。 001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料であり、令和8年3月改訂ページで再掲されていても対象の現在性を単独で保証しない。 PDF全該当ページの左右欄・改ページ・脚注・項目境界を全件目視した状態ではない。
- reviewer確認点: 後続改正を網羅する厚労省一次資料または現行統合本文を入手し、令和6年以降も確認する。 baseline PDF p.22-22を表示し、改正後欄、前後見出し、頁跨ぎ、項目境界を確認する。 各patchの旧文・新文・適用順を確認し、数字、単位、条番号、列挙順、括弧、ただし書きを照合する。
- baseline本文、独立再構成全文、patchの旧文・新文はmachine JSONに保存。

## 調査経路と再現

一次資料は厚生労働省公開PDF。各項目のPDF URL、SHA-256、ページ、改正後列、baseline本文とpatchの旧文／新文をmachine JSONに記録した。001453049.pdfは2025年3月の公式親ページ掲載を確認できる部分参照資料としてのみ使用し、令和8年3月改訂ページでも同じURLが再掲されている。

既存independent verifierのPASS記録（main SHAは古い）を今回の結論には使用していない。追加replayはsource snapshot本文から開始した。ただし本builder自体はPDFの再ダウンロード・再抽出を行わず、全22項目の全ページ目視でもない。

厚労省の令和6年改正ページ、令和8年改定ページ、介護保険最新情報索引、通知名と老企第25号の令和7・8年検索を確認した。後続改正が検索結果に見つからないことは不改正の証拠とせず、網羅的な改正履歴が確認できないため全件HOLDとした。

再実行コマンド:

    python3 scripts/build_notice_rouki25_audit_report.py --check && python3 scripts/validate_notice_rouki25_audit.py && npm run validate:data

human review状態は変更していない。Machine report: data/notice-rouki25-independent-audit.json
