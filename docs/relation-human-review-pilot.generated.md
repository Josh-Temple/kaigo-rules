# Relation Human Review Pilot

> This is a bounded human-review sheet. `READY_FOR_HUMAN_REVIEW` is not `REVIEWED`. AI proposals below are advisory only and must not be copied into the decision ledger as a substitute for human judgment.

- Pilot items: **8**
- Direct primary text on both sides: **4**
- Remaining evidence-pack items outside this pilot: **50**
- Decision ledger: `data/relation-human-review-decisions.json`

A valid human decision must record reviewer identity, decision, rationale, review timestamp, the exact evidence fingerprint reviewed, and `reviewer_attestation = HUMAN_REVIEW_COMPLETED`. If the evidence fingerprint changes later, the old decision is not current.

## 1. REL-001

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 個別機能訓練加算 — `related_to` → 第九十九条 （通所介護計画の作成）

**Relation key:** `fee.dayservice.note.13|related_to|ordinance37.article.99`

### Source

> 13 別に厚生労働大臣が定める基準に適合しているものとして、電子情報処理組織を使用する方法により、都道府県知事に対し、老健局長が定める様式による届出を行った指定通所介護の利用者に対して、機能訓練を行っている場合には、当該基準に掲げる区分に従い、(1)及び(2)については1日につき次に掲げる単位数を、(3)については1月につき次に掲げる単位数を所定単位数に加算する。ただし、個別機能訓練加算(Ⅰ)イを算定している場合には、個別機能訓練加算(Ⅰ)ロは算定しない。 (1) 個別機能訓練加算(Ⅰ)イ 56単位 (2) 個別機能訓練加算(Ⅰ)ロ 76単位 (3) 個別機能訓練加算(Ⅱ) 20単位

- URL: https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- Locator: 6 通所介護費 / 13 別に厚生労働大臣が定める基準に適合しているものとして、電子情報処理組織を使用する方法により、都道府県知事に対し、老健局長が定める様式による届出を行った指定通所介護の利用者に対して、機能訓練を行っている場合には、当該基準に掲げる区分に従い、(1)及び(2)については1日につき次に掲げる単位数を、(3)については1月につき次に掲げる単位数を所定単位数に加算する。ただし、個別機能訓練加算(Ⅰ)イを算定している場合には、個別機能訓練加算(Ⅰ)ロは算定しない。
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Target

> （通所介護計画の作成） 第九十九条 指定通所介護事業所の管理者は、利用者の心身の状況、希望及びその置かれている環境を踏まえて、機能訓練等の目標、当該目標を達成するための具体的なサービスの内容等を記載した通所介護計画を作成しなければならない。 ２ 通所介護計画は、既に居宅サービス計画が作成されている場合は、当該居宅サービス計画の内容に沿って作成しなければならない。 ３ 指定通所介護事業所の管理者は、通所介護計画の作成に当たっては、その内容について利用者又はその家族に対して説明し、利用者の同意を得なければならない。 ４ 指定通所介護事業所の管理者は、通所介護計画を作成した際には、当該通所介護計画を利用者に交付しなければならない。 ５ 通所介護従業者は、それぞれの利用者について、通所介護計画に従ったサービスの実施状況及び目標の達成状況の記録を行う。

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第四節 運営に関する基準 ＞ （通所介護計画の作成） ＞ 第九十九条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Do the primary texts justify this exact cross-layer relation semantics, not just a general thematic connection?

**AI proposal:** KEEP_OPEN. The source and target are resolved, but the exact cross-layer relation label still requires human legal-semantic judgment.

**Competing interpretation / ambiguity:** A general thematic or operational connection may exist without supporting the exact cross-layer relation asserted here.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `f3984f602718ad82cd16fbb6769c692654a9a19b32196becc9896626ab7074bf`

## 2. REL-013

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 食堂及び機能訓練室 — `interprets_or_explains` → 第九十五条 （設備及び備品等）

**Relation key:** `notice.dayservice.equipment.dining-training-room|interprets_or_explains|ordinance37.article.95`

### Source

> 指定通所介護事業所の食堂及び機能訓練室（以下「指定通所介護の機能訓練室等」という。）については、３平方メートルに利用定員を乗じて得た面積以上とすることとされたが、指定通所介護が原則として同時に複数の利用者に対し介護を提供するものであることに鑑み、狭隘な部屋を多数設置することにより面積を確保すべきではないものである。ただし、指定通所介護の単位をさらにグループ分けして効果的な指定通所介護の提供が期待される場合はこの限りではない。

- URL: https://www.mhlw.go.jp/content/12404000/001623023.pdf
- Locator: H30新欄。(2)旧②の共用記述は削除され、新設(4)へ再構成された後の本文。
- Pointer status: `MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE`

### Target

> （設備及び備品等） 第九十五条 指定通所介護事業所は、食堂、機能訓練室、静養室、相談室及び事務室を有するほか、消火設備その他の非常災害に際して必要な設備並びに指定通所介護の提供に必要なその他の設備及び備品等を備えなければならない。 ２ 前項に掲げる設備の基準は、次のとおりとする。 一 食堂及び機能訓練室 イ 食堂及び機能訓練室は、それぞれ必要な広さを有するものとし、その合計した面積は、三平方メートルに当該指定通所介護事業所の利用定員（当該指定通所介護事業所において同時に指定通所介護の提供を受けることができる利用者の数の上限をいう。次節において同じ。）を乗じて得た面積以上とすること。 ロ イにかかわらず、食堂及び機能訓練室は、食事の提供の際にはその提供に支障がない広さを確保でき、かつ、機能訓練を行う際にはその実施に支障がない広さを確保できる場合にあっては、同一の場所とすることができる。 二 相談室 遮へい物の設置等により相談の内容が漏えいしないよう配慮されていること。 ３ 第一項に掲げる設備は、専ら当該指定通所介護の事業の用に供するものでなければならない。 ただし、利用者に対する指定通所介護の提供に支障がない場合は、この限りでない。 ４ 前項ただし書の場合（指定通所介護事業者が第一項に掲げる設備を利用し、夜間及び深夜に指定通所介護以外のサービスを提供する場合に限る。）には、当該サービスの内容を当該サービスの提供の開始前に当該指定通所介護事業者に係る指定を行った都道府県知事（指定都市及び中核市にあっては、指定都市又は中核市の市長。以下同じ。）に届け出るものとする。 ５ 指定通所介護…

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第三節 設備に関する基準 ＞ （設備及び備品等） ＞ 第九十五条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Does the notice text actually interpret or explain the target provision, rather than merely sharing a topic or section?

**AI proposal:** KEEP_OPEN. Do not treat topic overlap or reconstructed notice text as proof of interprets_or_explains; compare primary text and adjudicate the exact semantics.

**Competing interpretation / ambiguity:** The notice and ordinance may concern the same topic without the notice actually interpreting or explaining this exact target provision.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `e6bfcabaa109a05d053cde11a6f96b380f81824e49bd49a7857265b21dbcf56d`

## 3. REL-003

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 高齢者虐待防止措置未実施減算 — `operational_basis_related_to` → 第百五条 （準用）

**Relation key:** `fee.dayservice.note.2|operational_basis_related_to|ordinance37.article.105`

### Source

> 2 別に厚生労働大臣が定める基準を満たさない場合は、高齢者虐待防止措置未実施減算として、所定単位数の100分の1に相当する単位数を所定単位数から減算する。

- URL: https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- Locator: 6 通所介護費 / 2 別に厚生労働大臣が定める基準を満たさない場合は、高齢者虐待防止措置未実施減算として、所定単位数の100分の1に相当する単位数を所定単位数から減算する。
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Target

> （準用） 第百五条 第八条から第十七条まで、第十九条、第二十一条、第二十六条、第二十七条、第三十条の二、第三十二条から第三十四条まで、第三十五条、第三十六条、第三十七条の二、第三十八条及び第五十二条の規定は、指定通所介護の事業について準用する。 この場合において、第八条第一項中「第二十九条」とあるのは「第百条」と、同項、第二十七条、第三十条の二第二項、第三十二条第一項並びに第三十七条の二第一号及び第三号中「訪問介護員等」とあるのは「通所介護従業者」と読み替えるものとする。

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第四節 運営に関する基準 ＞ （準用） ＞ 第百五条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Do the primary texts justify this exact cross-layer relation semantics, not just a general thematic connection?

**AI proposal:** KEEP_OPEN. The source and target are resolved, but the exact cross-layer relation label still requires human legal-semantic judgment.

**Competing interpretation / ambiguity:** A general thematic or operational connection may exist without supporting the exact cross-layer relation asserted here.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `096aecc99c772aea9cb2b58f1e1e6fa007d02ebdeb5d5cdf3428d311fe4dc9d2`

## 4. REL-014

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 事業所 — `interprets_or_explains` → 第九十五条 （設備及び備品等）

**Relation key:** `notice.dayservice.equipment.office|interprets_or_explains|ordinance37.article.95`

### Source

> 事業所とは、指定通所介護を提供するための設備及び備品を備えた場所をいう。原則として一の建物につき、一の事業所とするが、利用者の利便のため、利用者に身近な社会資源（既存施設）を活用して、事業所の従業者が当該既存施設に出向いて指定通所介護を提供する場合については、これらを事業所の一部とみなして設備基準を適用するものである。

- URL: https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf
- Locator: H27改正後欄。H30以後は当該項目を略として保持。
- Pointer status: `MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE`

### Target

> （設備及び備品等） 第九十五条 指定通所介護事業所は、食堂、機能訓練室、静養室、相談室及び事務室を有するほか、消火設備その他の非常災害に際して必要な設備並びに指定通所介護の提供に必要なその他の設備及び備品等を備えなければならない。 ２ 前項に掲げる設備の基準は、次のとおりとする。 一 食堂及び機能訓練室 イ 食堂及び機能訓練室は、それぞれ必要な広さを有するものとし、その合計した面積は、三平方メートルに当該指定通所介護事業所の利用定員（当該指定通所介護事業所において同時に指定通所介護の提供を受けることができる利用者の数の上限をいう。次節において同じ。）を乗じて得た面積以上とすること。 ロ イにかかわらず、食堂及び機能訓練室は、食事の提供の際にはその提供に支障がない広さを確保でき、かつ、機能訓練を行う際にはその実施に支障がない広さを確保できる場合にあっては、同一の場所とすることができる。 二 相談室 遮へい物の設置等により相談の内容が漏えいしないよう配慮されていること。 ３ 第一項に掲げる設備は、専ら当該指定通所介護の事業の用に供するものでなければならない。 ただし、利用者に対する指定通所介護の提供に支障がない場合は、この限りでない。 ４ 前項ただし書の場合（指定通所介護事業者が第一項に掲げる設備を利用し、夜間及び深夜に指定通所介護以外のサービスを提供する場合に限る。）には、当該サービスの内容を当該サービスの提供の開始前に当該指定通所介護事業者に係る指定を行った都道府県知事（指定都市及び中核市にあっては、指定都市又は中核市の市長。以下同じ。）に届け出るものとする。 ５ 指定通所介護…

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第三節 設備に関する基準 ＞ （設備及び備品等） ＞ 第九十五条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Does the notice text actually interpret or explain the target provision, rather than merely sharing a topic or section?

**AI proposal:** KEEP_OPEN. Do not treat topic overlap or reconstructed notice text as proof of interprets_or_explains; compare primary text and adjudicate the exact semantics.

**Competing interpretation / ambiguity:** The notice and ordinance may concern the same topic without the notice actually interpreting or explaining this exact target provision.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `866cef28391a37db80ca4098899454a0d45ae00fcb3a25e0279d380c4b1350a6`

## 5. REL-002

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 認知症加算 — `related_to` → 第九十八条 （指定通所介護の具体的取扱方針）

**Relation key:** `fee.dayservice.note.15|related_to|ordinance37.article.98`

### Source

> 15 別に厚生労働大臣が定める基準に適合しているものとして、電子情報処理組織を使用する方法により、都道府県知事に対し、老健局長が定める様式による届出を行った指定通所介護事業所において、別に厚生労働大臣が定める利用者に対して指定通所介護を行った場合は、認知症加算として、1日につき60単位を所定単位数に加算する。ただし、注7を算定している場合は、算定しない。

- URL: https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- Locator: 6 通所介護費 / 15 別に厚生労働大臣が定める基準に適合しているものとして、電子情報処理組織を使用する方法により、都道府県知事に対し、老健局長が定める様式による届出を行った指定通所介護事業所において、別に厚生労働大臣が定める利用者に対して指定通所介護を行った場合は、認知症加算として、1日につき60単位を所定単位数に加算する。ただし、注7を算定している場合は、算定しない。
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Target

> （指定通所介護の具体的取扱方針） 第九十八条 指定通所介護の方針は、次に掲げるところによるものとする。 一 指定通所介護の提供に当たっては、次条第一項に規定する通所介護計画に基づき、利用者の機能訓練及びその者が日常生活を営むことができるよう必要な援助を行う。 二 通所介護従業者は、指定通所介護の提供に当たっては、懇切丁寧に行うことを旨とし、利用者又はその家族に対し、サービスの提供方法等について、理解しやすいように説明を行う。 三 指定通所介護の提供に当たっては、当該利用者又は他の利用者等の生命又は身体を保護するため緊急やむを得ない場合を除き、身体的拘束等を行ってはならない。 四 前号の身体的拘束等を行う場合には、その態様及び時間、その際の利用者の心身の状況並びに緊急やむを得ない理由を記録しなければならない。 五 指定通所介護の提供に当たっては、介護技術の進歩に対応し、適切な介護技術をもってサービスの提供を行う。 六 指定通所介護は、常に利用者の心身の状況を的確に把握しつつ、相談援助等の生活指導、機能訓練その他必要なサービスを利用者の希望に添って適切に提供する。 特に、認知症（法第五条の二第一項に規定する認知症をいう。以下同じ。）である要介護者に対しては、必要に応じ、その特性に対応したサービスの提供ができる体制を整える。

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第四節 運営に関する基準 ＞ （指定通所介護の具体的取扱方針） ＞ 第九十八条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Do the primary texts justify this exact cross-layer relation semantics, not just a general thematic connection?

**AI proposal:** KEEP_OPEN. The source and target are resolved, but the exact cross-layer relation label still requires human legal-semantic judgment.

**Competing interpretation / ambiguity:** A general thematic or operational connection may exist without supporting the exact cross-layer relation asserted here.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `a74d4b8731bd042477e4a7c1857d2dadb8607833d42c9ff28d5f6622f8d48166`

## 6. REL-019

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 機能訓練指導員 — `interprets_or_explains` → 第九十三条 （従業者の員数）

**Relation key:** `notice.dayservice.personnel.function-training|interprets_or_explains|ordinance37.article.93`

### Source

> 機能訓練指導員は、日常生活を営むのに必要な機能の減退を防止するための訓練を行う能力を有する者とされたが、この「訓練を行う能力を有する者」とは、理学療法士、作業療法士、言語聴覚士、看護職員、柔道整復師、あん摩マッサージ指圧師、はり師又はきゅう師の資格を有する者（はり師及びきゅう師については、理学療法士、作業療法士、言語聴覚士、看護職員、柔道整復師又はあん摩マッサージ指圧師の資格を有する機能訓練指導員を配置した事業所で６月以上機能訓練指導に従事した経験を有する者に限る。）とする。ただし、利用者の日常生活やレクリエーション、行事を通じて行う機能訓練については、当該事業所の生活相談員又は介護職員が兼務して行っても差し支えない。

- URL: https://www.mhlw.go.jp/content/12404000/001623023.pdf
- Locator: H30改正後欄。はり師・きゅう師に関する資格要件追加後の本文。
- Pointer status: `MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE`

### Target

> （従業者の員数） 第九十三条 指定通所介護の事業を行う者（以下「指定通所介護事業者」という。）が当該事業を行う事業所（以下「指定通所介護事業所」という。）ごとに置くべき従業者（以下この節から第四節までにおいて「通所介護従業者」という。）の員数は、次のとおりとする。 一 生活相談員 指定通所介護の提供日ごとに、当該指定通所介護を提供している時間帯に生活相談員（専ら当該指定通所介護の提供に当たる者に限る。）が勤務している時間数の合計数を当該指定通所介護を提供している時間帯の時間数で除して得た数が一以上確保されるために必要と認められる数 二 看護師又は准看護師（以下この章において「看護職員」という。） 指定通所介護の単位ごとに、専ら当該指定通所介護の提供に当たる看護職員が一以上確保されるために必要と認められる数 三 介護職員 指定通所介護の単位ごとに、当該指定通所介護を提供している時間帯に介護職員（専ら当該指定通所介護の提供に当たる者に限る。）が勤務している時間数の合計数を当該指定通所介護を提供している時間数で除して得た数が利用者（当該指定通所介護事業者が法第百十五条の四十五第一項第一号ロに規定する第一号通所事業（旧法第八条の二第七項に規定する介護予防通所介護に相当するものとして市町村が定めるものに限る。）に係る指定事業者の指定を併せて受け、かつ、指定通所介護の事業と当該第一号通所事業とが同一の事業所において一体的に運営されている場合にあっては、当該事業所における指定通所介護又は当該第一号通所事業の利用者。以下この節及び次節において同じ。）の数が十五人までの場合にあっては一以上、十五…

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第二節 人員に関する基準 ＞ （従業者の員数） ＞ 第九十三条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Does the notice text actually interpret or explain the target provision, rather than merely sharing a topic or section?

**AI proposal:** KEEP_OPEN. Do not treat topic overlap or reconstructed notice text as proof of interprets_or_explains; compare primary text and adjudicate the exact semantics.

**Competing interpretation / ambiguity:** The notice and ordinance may concern the same topic without the notice actually interpreting or explaining this exact target provision.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `74d3af43386b2a0c6239a35363fb5ffa4ff6ac3d7955d46219a8738d30a0b58a`

## 7. REL-004

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 業務継続計画未策定減算 — `operational_basis_related_to` → 第三十条の二 （業務継続計画の策定等）

**Relation key:** `fee.dayservice.note.3|operational_basis_related_to|ordinance37.article.30-2`

### Source

> 3 別に厚生労働大臣が定める基準を満たさない場合は、業務継続計画未策定減算として、所定単位数の100分の1に相当する単位数を所定単位数から減算する。

- URL: https://www.mhlw.go.jp/web/t_doc?dataId=82aa0253&dataType=0
- Locator: 6 通所介護費 / 3 別に厚生労働大臣が定める基準を満たさない場合は、業務継続計画未策定減算として、所定単位数の100分の1に相当する単位数を所定単位数から減算する。
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Target

> （業務継続計画の策定等） 第三十条の二 指定訪問介護事業者は、感染症や非常災害の発生時において、利用者に対する指定訪問介護の提供を継続的に実施するための、及び非常時の体制で早期の業務再開を図るための計画（以下「業務継続計画」という。）を策定し、当該業務継続計画に従い必要な措置を講じなければならない。 ２ 指定訪問介護事業者は、訪問介護員等に対し、業務継続計画について周知するとともに、必要な研修及び訓練を定期的に実施しなければならない。 ３ 指定訪問介護事業者は、定期的に業務継続計画の見直しを行い、必要に応じて業務継続計画の変更を行うものとする。

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第二章 訪問介護 ＞ 第四節 運営に関する基準 ＞ （業務継続計画の策定等） ＞ 第三十条の二
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Do the primary texts justify this exact cross-layer relation semantics, not just a general thematic connection?

**AI proposal:** KEEP_OPEN. The source and target are resolved, but the exact cross-layer relation label still requires human legal-semantic judgment.

**Competing interpretation / ambiguity:** A general thematic or operational connection may exist without supporting the exact cross-layer relation asserted here.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `a116fc01dd02661d0f0fa229c39d6487e882bde8e1dd952a86ffdafc2c1fa70c`

## 8. REL-021

**Status:** `READY_FOR_HUMAN_REVIEW`

**Relation:** 管理者 — `interprets_or_explains` → 第九十四条 （管理者）

**Relation key:** `notice.dayservice.personnel.manager|interprets_or_explains|ordinance37.article.94`

### Source

> 訪問介護の場合と同趣旨であるため、第三の一の１の⑶を参照されたい。

- URL: https://www.mhlw.go.jp/file/06-Seisakujouhou-12300000-Roukenkyoku/0000080875.pdf
- Locator: H27改正後欄。その後の通所介護人員節改正で本文変更を示されていない。
- Pointer status: `MACHINE_RECONSTRUCTED_PRIMARY_CANDIDATE`

### Target

> （管理者） 第九十四条 指定通所介護事業者は、指定通所介護事業所ごとに専らその職務に従事する常勤の管理者を置かなければならない。 ただし、指定通所介護事業所の管理上支障がない場合は、当該指定通所介護事業所の他の職務に従事し、又は他の事業所、施設等の職務に従事することができるものとする。

- URL: https://laws.e-gov.go.jp/law/411M50000100037
- Locator: 第七章 通所介護 ＞ 第二節 人員に関する基準 ＞ （管理者） ＞ 第九十四条
- Pointer status: `DIRECT_PRIMARY_TEXT_POINTER`

### Judgment

**Question:** Does the notice text actually interpret or explain the target provision, rather than merely sharing a topic or section?

**AI proposal:** KEEP_OPEN. Do not treat topic overlap or reconstructed notice text as proof of interprets_or_explains; compare primary text and adjudicate the exact semantics.

**Competing interpretation / ambiguity:** The notice and ordinance may concern the same topic without the notice actually interpreting or explaining this exact target provision.

**Decision options:** `CONFIRM_RELATION`, `REJECT_RELATION`, `NEEDS_MORE_EVIDENCE`

**Currentness caveat:** Relation evidence readiness and source currentness are separate assurance axes. Supporting references may be historical, redline, amendment-only, partial, or current-source evidence as labelled; this pack makes no currentness promotion.

**Evidence fingerprint:** `0a8cb98ced9fa6e976b57aa07665b728d5af696ff5eafc0ebdeb2d9e26fd0bbe`

