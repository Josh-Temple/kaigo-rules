# Kaigo Rules GitHub Pages: release criteria and handoff (2026-11-02)

## Authoritative source

- Repository: `Josh-Temple/kaigo-rules`
- Site currently in use: `https://kaigo-rules.vercel.app/`
- Static migration candidate: PR #586, `work/20261031-github-pages-feasibility`
- Unmerged legal-currentness warning: PR #587
- This document **does not** certify legal accuracy, authorize a public deployment, or alter Vercel/DNS.

## Confirmed static integration result (previous CI at b622bbc)

- CI: 4/4 jobs passed.
- 9,662 files / 9,607 HTML pages / 79,859,347 bytes, below the 1,000,000,000-byte review budget.
- 39 service handbooks / 585 chapters.
- 7,392 Q&A detail pages; 1,552 law/rule detail pages.
- 79,861 inspected HTML references, including 13,119 still linking to the Vercel production site.
- Of those old-site fallbacks, 11,110 point to `/legislation` and 1,631 to `/rules`.
- 45,791 local links resolved. These counts reflect internal generated-output inspection, **not** independent sign-off.
- Some notice, legal browser, fee/unit-price and API-dependent pathways are still not equivalent.
- The pilot HTML is labeled unpublished and includes `noindex`: it cannot be shipped unchanged as a finished public site.

## Changes added after the above run

- Fixed the nested `/fees/guidance` and `/fees` static directory conflict.
- Added read-only numeric audit of site size, missing links, Vercel fallbacks, unsafe URLs, blocked raw-data paths, private-preview markers and `noindex`.
- Added release-gate unit tests and `.github/workflows/kaigo-pages-release.yml`.
- The publication workflow is **manual only**, requires the exact `main` SHA, and refuses upload/deployment unless all report blockers are zero and an independent acceptance JSON exists for exactly that SHA. No approval file has been created.
- PR #586 retains its separate validation and browser tests. Do **not** mistake a passing build for release authorization.

## Remaining work before a genuine migration

1. Complete static implementations for legacy `/legislation`, service-specific legal/notice/fee flows and API-dependent interactions. Retain exact source/scope/version warnings and preserve search parity. Merely rewriting all old links to a generic search landing page is not functional equivalence.
2. Integrate the validated 2026 treatment-improvement warning from PR #587, and independently check related content/print copies against the official source.
3. Review every exported field and all public corpus groupings against the publication allowlist. Do not export original `data/`, previews, raw Next.js hydration data or unpublished evidence.
4. Convert the pilot-specific private/noindex presentation to a reviewed public presentation, retaining the substantive limitation warnings.
5. Re-run total-output size, full routing and search checks, responsive layout, Android/printing and independent security/legal acceptance.
6. Record an acceptance file at `docs/pages-release-acceptance.json` with an independent reviewer, `decision=APPROVED_FOR_PUBLICATION`, exact main `source_sha`, and true values for all named categories in `scripts/check_github_pages_release_gate.py`. **Never mark a category true without direct evidence.**
7. Ensure GitHub Settings > Pages > Source is **GitHub Actions**, then run the explicitly gated release workflow on `main`, pinned to the approved SHA. Verify the returned Pages URL, rendered routes, search and mobile behavior. Only then consider canonical-link and DNS migration.

## Current decision

**HOLD_NO_DEPLOY / NO_MERGE for PR #586 itself.** Leave the existing Vercel service running. The user has authorized proceeding toward public publication; authorization alone does not establish the unresolved factual, legal or technical release conditions.
