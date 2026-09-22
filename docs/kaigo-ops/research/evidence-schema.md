# Evidence Register Schema

更新日: 2026-09-22  
目的: 事例、研究、公的資料を「同じEvidence」として混ぜないための共通schema。

## 1. Core fields

| field | purpose |
|---|---|
| evidence_id | 一意ID |
| issue_id | 紐づくIssue |
| title | 資料名 / 研究名 |
| year | 公開年 |
| country_or_region | 地域 |
| setting | residential / home care / adult social care / hospital transition等 |
| source_type | government / peer-reviewed / provider case / vendor / media等 |
| url | 原典 |
| checked_at | 最終確認日 |
| next_review_at | 再確認予定 |

## 2. Claim classification

`claim_type`:

- official_statistic
- official_evaluation
- peer_reviewed_primary
- systematic_review
- independent_evaluation
- provider_self_report
- vendor_claim
- implementation_description
- Studio_Lab_analysis

数値だけを抜き出して、claim_typeを失わない。

## 3. Evaluation design

`evaluation_design`:

- randomized_controlled
- controlled_before_after
- before_after
- longitudinal_observational
- cross_sectional
- qualitative
- mixed_methods
- systematic_review
- meta_analysis
- case_report
- descriptive_policy

## 4. Outcome hierarchy

同じ「効果」を混ぜない。

### Process
- documentation_time
- search_time
- transcription_time
- scheduling_time
- clicks
- response_time
- data_reentry
- paper_volume

### Workforce
- workload
- stress
- overtime
- retention
- training_burden
- support_requests

### Care / user
- direct_care_time
- care_quality
- safety
- falls
- hospitalization
- satisfaction
- QoL

### Financial
- labor_cost
- implementation_cost
- recurring_cost
- avoided_cost
- ROI

### Technical
- accuracy
- recall
- false_alarm
- uptime
- source_accuracy
- hallucination
- abstention_accuracy

## 5. Quantitative fields

可能なら以下を残す。

- sample_n
- unit
- baseline_value
- post_value
- absolute_change
- relative_change
- confidence_interval
- p_value
- observation_period

欠けている値を推測で補わない。

## 6. Independence / bias

`evidence_independence`:

- independent
- public_body_evaluation
- provider_report
- vendor_involved
- vendor_funded
- unclear

追加:

- conflict_of_interest
- selection_bias_note
- attrition_note
- self_report_flag
- co_intervention_flag

## 7. Implementation conditions

- authoritative_source_available
- workflow_redesign_required
- staff_training_required
- local_support_required
- interoperability_required
- network_adoption_required
- personal_data_used
- sensitive_data_used
- human_review_required
- fallback_process_available

## 8. Japan transferability

単純なscoreにしない。最低限以下を記述する。

- regulation_fit
- reimbursement_fit
- workforce_fit
- workflow_fit
- data_fit
- privacy_fit
- interoperability_fit
- cost_fit
- infrastructure_fit
- vendor_dependency
- evidence_gap

結果は、

- relatively_direct
- conditional
- substantial_adaptation
- unclear

程度の粗いclassificationにとどめ、理由を文章で残す。

## 9. Re-research

再調査では全sourceを読み直すのではなく、Evidence単位で差分確認する。

- last_checked
- status: active / superseded / withdrawn / unavailable
- new_followup_found
- claim_changed
- conclusion_impact: none / minor / material
- change_note

## 10. Publication rule

公開ページへ数値を載せるときは最低限、

> 誰が / 何を / 何件で / どの期間に / どう測ったか

が説明できるものを優先する。

「最大○%削減」のように条件を落とした数字だけを独立させない。
