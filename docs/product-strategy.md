# Kaigo Rules product strategy

Updated: 2026-09-25

## Problem to solve

Kaigo Rules is not primarily a FAQ site.

The underlying problem is that official long-term-care information exists, but the structure is difficult to follow in practice. Laws, ministerial ordinances, fee schedules, interpretation notices, Q&A, and amendment history are published separately, so users often cannot tell which document answers which question or how the sources relate.

A second problem is practical. Repeated inquiries from providers reveal a smaller set of questions that people actually get stuck on. That operational knowledge is valuable, but it should be used as an entry point into the official information structure rather than expanded into an unbounded answer collection.

## Product value

Kaigo Rules should connect two layers.

### Layer 1 —制度情報基盤

The primary product is a service-specific information foundation that lets a user trace:

1. 介護保険法
2. 基準省令
3. 解釈通知
4. 報酬告示・算定留意事項
5. 厚生労働省Q&A
6. related official sources and amendment evidence

The site should make the role of each source, its relationship to other sources, and its verification/currentness state visible.

### Layer 2 —実務上の疑問

FAQ is a curated navigation layer over the information foundation.

It should not aim to reproduce every possible question. It should prioritize questions that meet one or more of these conditions:

- providers ask about them repeatedly;
- an incorrect interpretation can materially affect staffing, operations, claims, or compliance;
- the ordinance text alone does not resolve the practical question;
- several source types must be read together;
- the issue commonly results in an inquiry to the designated authority.

A useful FAQ should lead back to the relevant official sources and show what conditions must be checked. It should not become a substitute for the source structure.

## Product principle

The product is best described as:

> 介護制度を検索するだけでなく、制度の構造と実務で迷うポイントをつなぐ情報基盤。

The differentiator is not the volume of copied official information or the number of FAQ entries. It is the combination of:

- first-party source traceability;
- service-specific structure;
- explicit relation between law / ordinance / notice / fee / Q&A;
- separated verification, currentness, and human-review states;
- practical prioritization informed by real provider inquiries.

## Information architecture

The public site should have two clear entry modes:

1. 制度からたどる
   - see the source hierarchy;
   - open the relevant database;
   - move between related layers;
   - inspect source and verification state.

2. 実務の疑問から入る
   - start from a curated operational question;
   - see a concise answer with conditions and cautions;
   - return to the underlying official sources.

The first mode is the foundation. The second is an accelerator.

## FAQ scope policy

Do not scale FAQ by raw count.

For the current MVP:

- keep the existing curated set small;
- do not add questions only to increase coverage;
- add a question when practical inquiry experience or usage evidence shows recurring value;
- avoid near-duplicate questions that differ only in wording;
- prefer one strong page that explains conditions over several shallow answers;
- every published FAQ should retain source links and verification state.

A future FAQ backlog may be large internally, but publication should remain selective.

## Near-term priority

1. Strengthen the information foundation and make its structure visible in the UI.
2. Connect existing law / ordinance / notice / fee / Q&A layers more clearly.
3. Complete the second-service ingestion pattern without copying service-specific infrastructure.
4. Keep the existing FAQ set curated and improve source navigation from each question.
5. Add new FAQ only when practical value is demonstrated.

## Non-goals

- becoming a generic article or SEO content site;
- reproducing every MHLW Q&A as a hand-written FAQ;
- hiding uncertainty or currentness gaps to make the site appear complete;
- replacing official sources or designated-authority decisions;
- adding service breadth by duplicating repositories, workflows, or source corpora.
