# 介護保険法 shared corpus

## 目的

介護保険法本文をサービスごとに複製せず、全サービスDBで再利用できる共有ソース層として保持する。

共有コーパスの存在と、個別サービスへの適用は別の状態として扱う。

- source corpus node: `data/care-insurance-act-nodes.json`
- source-derived containment: `data/care-insurance-act-relations.json` の `contains`
- service applicability: service-specific scope / generated index
- semantic / cross-layer relation: `contains` 以外のrelation
- independent verification receipt: `data/egov-content-independent-audit.json`
- source freshness: `.github/workflows/verify-egov-source-freshness.yml`

## 変更前の評価

従来のCare Insurance Act corpusは、通所介護を起点に選んだ11条を共有ファイルへ格納していた。

収載条文は第8条、第41条、第70条、第70条の2、第73条、第74条、第75条、第76条、第76条の2、第77条、第78条であり、node ID自体は共有可能だったが、source selectionは通所介護scopeに由来していた。

したがって「共有ファイルに置かれた部分コーパス」であり、全サービスDBの共有法令基盤としては不足していた。

## shared source selection

共有ソース層のselectionは `data/care-insurance-act-corpus-scope.json` を正本とする。

初期共有範囲は次の制度構造に限定する。

1. 第1条〜第8条の2: 総則・サービス定義
2. 第18条〜第26条: 保険給付の通則
3. 第40条〜第61条の4: 介護給付・予防給付
4. 第69条の2〜第115条の44: 介護支援専門員、事業者、施設、介護予防サービス、情報公表等
5. 第115条の45〜第115条の49: 地域支援事業等との制度境界

これは全条文を無条件に複製する方針ではない。被保険者、認定手続、給付制限、事業計画・費用負担・審査請求・罰則等は、サービスDBの共有本文として必要性が確立するまで明示的に範囲外に置く。

e-Gov法令APIの現行法令XMLをsource of truthとし、selection rangeはXML中の条文順序で解決する。

## stable source node

既存node IDは変更しない。

例:

- `careact.article.8`
- `careact.article.8.p.7`
- `careact.article.41.p.4.i.1`

新規収載条文も同じ規則でstable IDを生成する。

source nodeの `service_scope` は `SHARED_CORPUS` とし、corpus内に存在することをサービス適用の証拠として使用しない。

## service applicability

既存の通所介護scope `data/care-insurance-act-scope.json` は互換性のため維持する。

訪問介護は次を参照する。

- `data/services/homevisit/care-insurance-act-scope.json`
- `data/services/shared/designated-home-service-core.json`
- `data/services/homevisit/care-insurance-act-index.generated.json`

今後の各サービスも、共有本文をコピーせず、scope/index/relationで参照する。

共有コーパスに条文が存在しても、service scopeがなければ `lib/service-scope.ts` は適用を推測せずfail closedを維持する。

## relation separation

`contains` はsource-derived structureであり、独立e-Gov reparseの対象とする。

既存の非`contains` relationは別レイヤーとして保持する。

- 通所介護固有のCare Act → 基準省令/報酬relation: `SERVICE_SPECIFIC`
- 指定居宅サービスに共通するCare Act内部relation: `SHARED_DESIGNATED_HOME_SERVICE_STRUCTURE`

共有本文を拡張しただけでは、新規サービスのrelationを生成しない。

## verification and currentness

production importerは `xml.etree.ElementTree` を使用する。

独立検証は `xml.dom.minidom` で現行e-Gov XMLを再解析し、以下だけを照合する。

- node ID
- article / paragraph / item structure
- official text
- parent relation
- `contains` relation
- live XML hash

非`contains` semantic relationはこのPASSに含めない。

監査receiptは入力blob SHAを固定し、scope/data/verifierのいずれかが変わればstaleとしてfail closedする。

source freshness workflowは、法令XML、改正履歴、current revision metadataのdriftを監視する。freshness PASSはhuman reviewやサービス適用PASSを意味しない。

## compatibility

共有コーパス拡張で次を維持する。

- 既存Care Act node ID
- 通所介護service scope
- 訪問介護generated index
- `/law` のglobal corpus表示
- `/law?service=...` のservice filter
- verification/currentness/human review/publicationの分離
- public route gate

global `/law` とdatabase-wide searchは共有コーパスの拡張分を利用できる。サービス指定時は既存scope contractで絞り込む。

## remaining service-scope work

このworkerでは、共有本文の拡張をサービス適用済みにしない。

残る作業は、各サービスについて個別に次を確定すること。

- service definition paragraph
- benefit/payment provisions
- provider/facility designation provisions
- governing standards delegation
- incorporation / substitution / read-as relation
- service-specific currentness boundary
- relation verification
- human review / publication decision

特に新規サービスは、共有コーパスに対応条文が存在していても `SERVICE_SCOPE_NOT_DEFINED` 相当の状態を維持できることが前提である。

## current source note

この設計時点ではe-Gov上の現在施行版は2026-10-01施行版として取得する。e-Govには未施行改正も表示されるため、current enforced revisionと将来施行予定を同一視しない。実データの版・hashは `data/care-insurance-act-meta.json` とfreshness workflowを正本とする。
