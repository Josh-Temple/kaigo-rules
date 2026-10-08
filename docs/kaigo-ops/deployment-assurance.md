# Kaigo Ops — production deploy verification (Worker B)

Updated: 2026-10-08. This document specifies the deploy-state contract, **not**
a claim that the current production has already passed this new gate.

## Scope

- Workflow: `.github/workflows/daily-vercel-production-deploy.yml`
- Verifier: `scripts/verify_kaigo_ops_production.py`
- Synthetic regression: `tests/test_verify_kaigo_ops_production.py`
- Project: `kaigo-ops` / `prj_7kKmZkto1j9r9Z3otwccx05LAjTp`
- Vercel team: `team_imvRFeaSa1LmNpMJkFiMwNmB`
- Public production alias: `https://ops-site-pi.vercel.app/`

## Required GitHub Actions secret

A Vercel API token with **read access to the above team and project** must be
registered as the GitHub Actions secret `VERCEL_TOKEN`. Configure the token
directly in repository settings; do not include its value in a PR, workflow log,
artifact, documentation, or chat. Existing deploy-hook secret
`VERCEL_DEPLOY_HOOK_KAIGO_OPS` remains necessary.

If the token is absent, the trusted deployment job fails **before** requesting
a new deployment. A deploy-hook URL cannot itself prove which commit Vercel
deployed, whether it reached READY, or which deployment the public alias serves.

The token is exposed only to the trusted non-PR deploy job's credential check
and verification step. PR validation uses synthetic offline tests.

## Marker contract

For a changed Kaigo Ops tree, the deployment job proceeds:

1. Confirm the API credential exists before triggering the hook.
2. Capture the request start timestamp and require successful hook acceptance.
3. Poll the **Kaigo Ops** Vercel project for a newly created production
   deployment with an exact 40-character expected Git SHA and expected GitHub
   repository identity.
4. Inspect the selected deployment; require target `production`, exact SHA,
   correct project, and `READY`.
5. Query the current public alias and require that it resolves to that exact
   deployment ID (not merely an older READY deployment).
6. GET the public home, five Issue and five action tool routes; require HTML
   HTTP 200 and the Kaigo Ops Japanese site shell.
7. Only after all checks pass, advance `deploy-state/kaigo-ops` to the
   verified commit SHA.

The workflow uses an ordinary fast-forward push for the marker; divergence
fails closed rather than overwriting a marker with unconditional force.

## Failure behavior

No marker update on missing API token, rejected hook, missing deployment,
unexpected GitHub repository or SHA, `ERROR` / `CANCELED` / `BLOCKED`,
timeout, stale/wrong alias, inaccessible page or mismatched page shell.
The script never prints the bearer token, hook URL, or API response body.

Changing the workflow and tests does **not** retroactively make the existing
`deploy-state/kaigo-ops` branch a verified-production marker. Only an actual
post-merge verified production run establishes the new meaning.

After merging the Worker B change through the Integrator's release gate,
run `workflow_dispatch` with `force_ops=true` if an Ops redeployment is needed.
Verify the successful workflow run and the exact deployment ID, SHA, READY
state and alias before recording completion. This Worker B branch does not
trigger a production deployment.

## Boundaries

- Kaigo Rules keeps its existing separate version endpoint and release gate.
- No application-side service inference, worksheet storage, analytics event or
  new Issue/tool is added.
- The public HTTP route probes are verification traffic, not a demand signal;
  they do not submit worksheet input or feedback.
- If the team/project/alias changes, revise and independently verify their
  constants before using this verifier.
