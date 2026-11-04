# Pages reviewed-scope generator — private candidate only

This is **not** a publication gate or deployment authorization. It deliberately does not copy the older private full-site pilot. The full pilot remains an unpublished research output and must not be passed through the beta/public presentation scripts as though its raw corpus were approved.

## Run

From the repository root, only after an independently reviewed, ID-specific approval record exists:

```sh
python scripts/build_github_pages_reviewed_scope.py \
  --approvals /private/approved-ids.json \
  --legal /private/verified-legal-records.json \
  --qa data/qa-corpus.json \
  --qa-meta data/qa-corpus-meta.json \
  --private-output /tmp/kaigo-reviewed-scope-unique
python -m unittest discover -s tests -p 'test_github_pages_reviewed_scope.py'
```

The output path must be new, outside the repository, and below the OS temporary directory. **Do not upload this tree to Pages or a public Actions artifact.** This builder generates only a minimal scoped search/index/detail preview (not the full handbook, fee database, or existing integrated beta).

## Approval manifest contract

```json
{
  "schema": "kaigo-reviewed-scope-v1",
  "purpose": "PRIVATE_ACCEPTANCE_ONLY",
  "approvals": []
}
```

The empty example intentionally **fails**. Each record must include an exact `kind` (`legal` or `qa`), `id`, `state: "APPROVED_FOR_SCOPED_REVIEW"`, `publish_approved: true`, `approved_by`, `approved_at` (YYYY-MM-DD), `approval_reference`, `evidence_reference`, `row_sha256`, `period_start` and `period_end` (YYYY-MM), and `source_url` under an explicitly supported official host. Legal entries also need `document_id` and complete `service_ids`; Q&A entries need `service_code`.

These fields are a *machine-readable admission contract*, not proof that a reviewer or authority actually approved the records. A/C/D must verify provenance and scope independently. Never set a record or corpus to reviewed merely to bypass an error.

- Legal source rows require `state: REVIEWED_CURRENT` and exact document, period, services, row content hash and official URL. An unknown period fails.
- Q&A rows require `review_state: REVIEWED_CURRENT`, exact month and service code, an original issuance reference, and Q&A metadata `review_status: REVIEWED_SCOPE_ONLY`. Current `INGESTED_UNREVIEWED` metadata fails.
- Duplicate, missing, changed, or unknown rows fail before creating the output. Unreviewed records never appear in detail HTML, `rows.json`, `rows.json.gz` or JavaScript-embedded data.
- Every emitted HTML retains `noindex` and a conspicuous Japanese review warning. HTML links and search JSON hrefs must resolve locally or to the restricted official hosts. The generated CSS and JS contain no legacy origin fallback.
- The generated client provides basic search, no-results messages, pagination and Back/Forward URL-state restoration; this is **not** proof of search-rank parity or independent browser/Android/A4 acceptance.

## Explicitly unresolved

1. A's source-matched **candidate** findings do not constitute `publish_approved: true`. No actual approved allowlist is provided in this commit.
2. Existing `build_github_pages_integrated_pilot.py --with-details`, full generated search JSON, Q&A details, and legislation pilot remain **private-only**. This new builder does not make those outputs safe to deploy. E/C must ensure the actual release workflow cannot bypass this separation.
3. The older presentation helpers can remove `noindex` from a raw tree. They must not be invoked for this reviewed-scope output without a separate reviewed release change and D acceptance.
4. Full-source records, 39-service coverage, Vercel-link counts for the old full build, all generated static pages and interactive browser/print/Android checks remain **NOT_VERIFIED**.
5. No Actions are required for the local synthetic tests. Do not set beta mode flags or perform main merge, public upload or deployment.

Hand-off: compare the fixed branch SHA with PR #593 and integrate file-by-file. The B-specific files are `scripts/build_github_pages_reviewed_scope.py`, `tests/test_github_pages_reviewed_scope.py`, and this note.