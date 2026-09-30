# Dayrehab Article 119 and interpretation-layer release notes

Date: 2026-10-01

This release deepens the existing dayrehab public preview without collapsing legal-source or verification states.

## Article 119 incorporation

The current e-Gov text of Ordinance 37 Article 119 is treated as the authority for the dayrehab incorporation set.

- 25 explicit incorporated article targets are stored as service-specific relations.
- A separate minidom + Japanese article-reference parser reproduced the same 25 targets from live e-Gov XML.
- Four explicit read-as evidence groups in Article 119 are also checked.
- 24 incorporated articles already exist in the shared Ordinance 37 corpus and are therefore available on local dayrehab routes.
- Article 64 is part of the verified Article 119 relation set but is not currently present in the shared corpus. Its text is not fabricated; the public surface points to e-Gov instead.
- This relation PASS does not mean HUMAN_VERIFIED or VERIFIED_CURRENT.

The direct Chapter 8 text audit remains bounded to Articles 110–119 (including 118-2). Incorporated articles do not inherit the dayrehab direct-text audit.

## Rouki 25 interpretation notice

The official historical MHLW HTML section "第九 通所リハビリテーション" is published as nine principal items.

- An importer extracts the bounded section from the official MHLW HTML.
- An independent HTML-text extraction path confirms all nine committed item texts.
- The source is explicitly labeled historical.
- The 2024/R6 old-new comparison PDF is retained as separate amendment evidence.
- Ellipses, new-item markers, and deletions from the old-new comparison are not mechanically applied to produce a synthetic current integrated text.
- Currentness therefore remains GAP_HISTORICAL_SOURCE_ONLY.
- Human review remains NOT_REVIEWED.

The historical interpretation notice is not used to define the current Article 119 incorporation set.

## Product and assurance boundaries

The public product now counts:
- 35 locally available dayrehab standards article routes: 11 direct + 24 Article 119 incorporated;
- 9 dayrehab interpretation-notice items.

The new Article 119 lane adds 25 relations to the tracked relation inventory and independently verifies all 25, so the pre-existing 107 unverified relations do not increase.

Shortstay-life remains unpublished. Care Insurance Act, remuneration, and fee-guidance publication for dayrehab remain outside this release.


## Fresh verification run

The 2026-10-01 integration refresh (GitHub Actions run 36790961204) regenerated the three pinned receipts against the partitioned service index:

- direct Chapter 8 text/structure: PASS, 69 nodes / 11 articles;
- current Article 119 relations: PASS, 25/25;
- bounded Rouki 25 historical-source text: PASS, 9/9 principal items.

The three receipts share the same feature input SHA for this refresh. No human-review or VERIFIED_CURRENT state was promoted.
