# 2026-10-24 — Unreviewed service handbook overview noindex gate

## Incident / motivation
Post-merge audit of PR #557 and PR #558 found that service handbook **chapter** pages used `pageMetadata(..., false)` (noindex), while service **overview** pages at `/services/<service_id>` still inherited indexable defaults. The overview component shows `作成中` commentary including 63 new unverified Research Mesh staffing candidate requirements across 8 services. The direct legal evidence source status is **not** equivalent to reviewer-approved legal applicability.

## Scoped fix
- Set `robots: { index: false, follow: true }` on all 39 service handbook overview pages through the generic route and the dedicated dayservice/dayrehab routes.
- Remove the former `/services/dayservice` curated SEO entry and all `/services/<service_id>` dynamic pages from `sitemap.xml`. Indexable directory `/services` and established top-level entry pages are unchanged.
- Preserve canonical paths, direct navigation, source listing, detailed chapter routes, existing chapter noindex, existing Vercel deployment protection and all 585 handbook chapters.
- Add regression checks for the three route implementations and the sitemap exclusion.
- This is **not** a robot disallow: direct links remain crawlable so search engines can see `noindex`.

## Release gate
GitHub PR CI `Validate build` and `Verify publication readiness integration` must succeed at the exact PR HEAD; verify no accidental handbook data or publication-gate changes. The next Vercel production deployment must use the **exact released main SHA** and preserve SSO/auth settings, domains and release checks. Do not equate source availability to legal verification.

The user asked to proceed with **prepublication safety checks and Vercel production rollout**. This patch is intentionally limited to search-index behavior of unreviewed handbook pages. Research Mesh itself remains `NO_GO` / `real_project_work_enabled=false`.
