# Cloudflare Workers (vinext) isolated preflight — 2026-10-31

## Scope and control

- This is a **non-deploying experimental branch** only. Do not merge it without independent acceptance.
- Base: `bbe5b716687856e848f18db9f799551e1d63b26c` (`main` at preflight).
- Do not change production Vercel, Cloudflare account, DNS, `main`, or PR #583.
- The workflow has **no credentials**, no deployment steps, and no write permissions.
- Existing `npm run prebuild` is mandatory; it must not be removed or bypassed to obtain a green Workers build.

## Evidence from previous preflight

- Ordinary Next.js build: pass, 250.441 s, 1,428 static pages (local measurement).
- `output: 'export'`: fail on `/notices/[id]` missing `generateStaticParams()`; additional API-route obstacle.
- `npx vinext check`: 9 supported, 1 issue, no actual vinext build.
- Caution: `scripts/export_product_value_scope.mjs` defines `__dirname` using `import.meta.url`; the compatibility warning needs runtime verification.

## CI measurement

`.github/workflows/cloudflare-workers-preflight.yml` performs, in an ephemeral GitHub runner:

1. Install repository dependencies using Node 24 and Python 3.12.
2. Execute the unmodified `npm run prebuild` (handbook + legal data and test validations).
3. Perform `vinext check`; initialize Cloudflare support with `--platform=cloudflare` in the ephemeral checkout.
4. Run `npm run build:vinext` and report build errors and output files.
5. Upload build logs when available for review.

It **does not deploy**; `workers.dev`, preview URLs, DNS, Cloudflare usage, and Vercel remain unchanged.

## Acceptance after CI

Workers build success alone is **not** the release gate. Before any Cloudflare deployment:

- Verify `/databases/search`, `/qa`, `/legislation`, service search, filters, pagination, and all four APIs.
- Verify `/notices/[id]`, `/qa/[id]`, and handbook pages against current Vercel responses.
- **Block public access** to `/handbook-preview` and all unreviewed material; production denial and preview authentication must work on Cloudflare without relying on `VERCEL_ENV`.
- Enforce Cloudflare Access (or equivalent authenticated isolation) before creating a public test endpoint; `noindex` alone is insufficient.
- Measure actual Worker uncompressed bundle size vs 64 MiB; Workers Free CPU (10 ms/request), memory (128 MB), request volume, and price. On failing thresholds, do not assume free-plan suitability.
- Compare canonical, sitemap, robots, Vercel Analytics replacement, status codes, links, and Android browser functionality.
- Do not change the official site URL or remove Vercel until a separate release review approves the cutover and rollback.

References:
- https://developers.cloudflare.com/workers/framework-guides/web-apps/nextjs/
- https://developers.cloudflare.com/workers/platform/limits/
- https://github.com/cloudflare/vinext
