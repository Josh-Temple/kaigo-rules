# Research Mesh成果物の手動統合（2026-10-25）

利用者の統合指示に基づき、main `39298844165ce5df7c2ac0ae02fe8a599719c5e3` に未収載の13サービス・20章へ、459件の説明候補を追加する。元の概要・段落・確認項目と既存の職種別要件は変更しない。これは作成中の手引への候補収載であり、法令確認済み・行政承認・Research Mesh正式採用を意味しない。

## 固定入力と選択

Research Meshのoutputsを全399件・2ページ（cursor終端）取得して入力集合を固定した。20件とも、別REVIEWとINTEGRATEの限定合格がある最新版ZIPを使用し、全ZIPのSHA-256をINTEGRATE報告に記載された外部固定値と照合した。現行manifestの1,151ファイルのSHA-256・バイト数を照合し、同梱のオフラインunittestを459件実行した。ZIP内の過去版manifestは当該版の現行manifestと区別した。ZIPのhash整合やテスト成功は法令の意味的正確性の証明ではない。

| サービス | 章 | 追加候補 |
|---|---|---:|
| `community-elderly-facility` | `business_continuity` | 14 |
| `community-elderly-facility` | `equipment` | 47 |
| `community-elderly-facility` | `incident_and_infection` | 34 |
| `community-elderly-facility` | `notifications` | 8 |
| `community-elderly-facility` | `operations` | 36 |
| `community-elderly-facility` | `records` | 26 |
| `community-elderly-facility` | `safeguarding` | 10 |
| `community-elderly-facility` | `staffing` | 45 |
| `community-specific-facility` | `staffing` | 30 |
| `homebath` | `staffing` | 13 |
| `homenursing` | `staffing` | 11 |
| `preventive-homebath` | `staffing` | 14 |
| `preventive-shortstay-life` | `staffing` | 38 |
| `preventive-shortstay-medical` | `staffing` | 16 |
| `preventive-specific-facility` | `staffing` | 39 |
| `regular-round` | `staffing` | 7 |
| `shortstay-life` | `staffing` | 31 |
| `shortstay-medical` | `staffing` | 13 |
| `specific-facility` | `staffing` | 21 |
| `specific-preventive-welfare-equipment-sale` | `staffing` | 6 |

原本ID、ZIP全体のhash、REVIEW/INTEGRATEのID、元ルールと表示要件の対応、表示文章のhashは同日付のJSON台帳に記録する。既存の8サービス63候補は全件保持する。

特定介護予防福祉用具販売は11件中、人員・管理者・資格・条件付きみなしの6件を採用した。給付区分、他サービスとの比較、運営準用、未確認通知scopeの5件は人員配置要件へ再分類せず、除外理由と元ルールを台帳に保持する。定期巡回は6職種と連携型の適用条件を別に表示する。

## 表示・安全性

- 全459要件を `EVIDENCE_GAP`、出典を `SOURCE_CANDIDATE_UNVERIFIED` とし、確認日時と未検証URLを表示しない。根拠未確認の警告、施行版・条例・個別適用の未確認、適用範囲、条件・例外は常時表示する。
- 人員章は既存の `role_sections` を使用する。地域密着型介護老人福祉施設の設備・運営・記録・虐待防止・事故感染症・BCP・届出の7章だけに、同じ厳格な要件schemaを使う `rule_sections` を許可する。その他のサービス・章への追加は拒否する。
- 国の基準と横浜市条例を区別する。届出の市規則・国様式・案内を省令や条例へ誤分類しないため、この8要件では本文に参照候補を明示し、既存の出典種別へ無理に登録しない。正確な種別と候補URLは内部台帳に保持する。
- 数字・比率・標準と義務の違いを保持する。短期入所生活介護REV2の通常・予防の利用者範囲、常勤と常勤換算、看護・介護比率緩和の全条件、記録完結時からの保存期間、横浜市の対象限定と経過措置を残す。
- 既存のURL検証、HTML/control文字拒否、Reactのエスケープ、noindex、sitemap除外、SSO、SEO設定は緩和しない。

## 保留

地域密着型介護老人福祉施設の「当初指定」は、固定一覧ではREVIEWのPASS_SCOPEDまでで別INTEGRATEが未取得のため追加しない。法令・条例の全面現行性、個別施設への適用、専門家による法的受入も未実施であり、これらの状態を確認済みに変更しない。Meshの公式 `CUTOVER_CANARY / NO_GO` と `real_project_work_enabled=false`、予定済タスク、Control Planeには書き込まない。

## 検証の範囲

同日付の回帰テストは、mainの585章の全フィールドをhash比較し、20章への追加以外の変更を拒否する。元ルールの日本語条件・例外・数値と変換後本文の対応、出典分類、適用範囲のallowlist、虚偽の検証昇格、XSSと不正URLの拒否も確認する。従来の手引テストは新しい追加フィールドだけを除いて旧fixtureとの厳密比較を継続する。

統合PRのHEAD、CI・画面確認・マージ・本番結果は、確定後に別のWORK結果報告へ記録する。この文書の作成をもって未実行の検証を成功とは扱わない。
