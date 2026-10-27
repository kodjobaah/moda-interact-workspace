---
id: ARCH-049-SHOPIFY-001
architecture_id: ARCH-049
title: Authorise Shopify read_brand scope without implementing synchronisation
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: ["ARCH-049-BACKGROUND-003"]
created: 2026-10-25
updated: 2026-10-27
---

# Authorise Shopify read_brand scope without implementing synchronisation

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`.

## Execution Ownership Amendment

On 2026-10-27, `/moda_developer_create ARCH-049-SHOPIFY-001` was invoked as an explicit developer takeover. Execution and completion authority are now `developer`; logical ownership remains `assigned_agent: moda_app` and `repository: moda-interact`.

## Objective

Add and validate the Shopify Admin brand-read permission required by the Background-owned Shopify ShopBrand synchroniser. No brand fetch or ShopBrand persistence belongs in this task.

## Context

The uploaded Shopify app scope string contains `write_products,write_metaobjects,write_metaobject_definitions` but not `read_brand`. Shopify Admin GraphQL `shop.brand`/BrandingBrand requires `read_brand`. The earlier full Shopify ingestion task is superseded in scope by Background-003.

## Scope

- Add `read_brand` to the app `access_scopes.scopes` in the canonical `moda-interact/shopify.app.toml` while preserving every existing scope.
- Verify any applicable production app configuration variant and existing `app/scopes_update`/reauthorisation flow; document how already installed shops regain the grant.
- Add focused config tests/evidence proving the declared scope is present and brand read is unavailable without it.

## Out of Scope

- Shopify provider brand GraphQL queries and polling, modifications to Background, ShopBrand database writes, brand-image processing, changing unrelated Shopify scopes or webhook contracts.

## Requirements

### R1. Exact scope change

Existing scope list in the supplied snapshot is:

```toml
scopes = "write_products,write_metaobjects,write_metaobject_definitions"
```

Add `read_brand` exactly once, retain all existing scopes and the current `app/scopes_update` registration. Confirm the deployed configuration is the one being edited; do not assume that a development-only TOML file controls a different production app.

### R2. Permission/reauthorisation

A live already-installed merchant may need Shopify's permitted authorisation refresh after scope changes. Provide the normal Shopify re-authorisation path and test missing-scope reporting. Do not silently attempt brand reads with a token that lacks scope.

### R3. Stop boundary

This task is **configuration/authentication only**. `BACKGROUND-003` owns all brand API retrieval and ShopBrand source persistence.

## Work Items

- [x] Update relevant Shopify app configurations and focused scope/authentication tests.
- [x] Document the re-authorisation procedure for existing installations.
- [x] Record the two applicable app configurations, required `read_brand` declaration, runtime `SCOPES` caveat and distinction between declared and actually granted scope.

## Interfaces / Contracts

Produces the `read_brand` permission for the existing authenticated Shopify GraphQL client. It does not create any new HTTP/queue contract or write brand records.

## Dependencies

None.

## Enables

- ARCH-049-BACKGROUND-003

## Acceptance Criteria

- [x] `read_brand` is present exactly once in both inspected app configurations without dropping prior scopes; both TOMLs parse.
- [x] Installed-shop permission refresh is documented; missing/granted scope status is tested using authenticated-webhook reporting and isolated scope parsing.
- [x] No Shopify brand retrieval, ShopBrand write or brand synchronisation was added.

## Validation

- [x] Parse both TOML configurations and execute focused scope tests. All ARCH-049-specific tests passed in the supplied 11:05 log; see baseline-test exception in Completion Report.
- [x] Inspect and run the affected `app/scopes_update` and authentication tests. Those affected tests passed; one additionally included ARCH-045 configuration test failed on a discrepancy already present in the original snapshot.
- [x] `git diff --check` (recorded in the 11:05 session and independently verified by applying the exact committed patch to a clean reconstruction).

Additional checks were attempted: Prisma Client generation, lint and production build passed in the 11:54 log. A post-generation `npm run typecheck` and live Shopify scope approval are not evidenced and must not be treated as passed.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Developer Self-Review Passed — Attempt 1, claimed at `2026-10-27T10:21:58Z`. Implementation commit `884d08346bee33227f2f009209cda1ceeaca5311` is published on `origin/task/ARCH-049-SHOPIFY-001`; its worktree is clean. The canonical parent review handoff is committed and pushed at `20aca762f56a18bb738f22b829576d2c1c621ca8`. Review transition clears `executor` and `claimed_at`; `attempt: 1` is unchanged. Current `origin/main` advanced after the attempt began; no mainline merge is performed during review.

### Files Changed

Implementation repository `moda-interact` (9 files; 206 insertions, 2 deletions):

- `shopify.app.toml`
- `shopify.app.moda-interact.toml`
- `app/routes/webhooks/app/scopes-update/route.jsx`
- `app/services/shopify-brand/shopify-brand-read-scope.ts` (new)
- `app/services/webhooks/shopify-webhook-observability.server.ts`
- `docs/arch-049/SHOPIFY-001-brand-read-permission.md` (new)
- `tests/unit/routes/scopes-update.test.jsx`
- `tests/unit/services/shopify-brand-read-scope.test.ts` (new)
- `tests/unit/webhooks/shopify-brand-scope-config.test.ts` (new)

This parent-workspace handoff updates only this canonical task file; it does not change an architecture index, parent architecture or implementation repository source.

### Work Completed

1. Added required `read_brand` exactly once in each existing Shopify app configuration while retaining each app's own pre-existing scopes. Registered the previously absent `app/scopes_update` subscription in the named `shopify.app.moda-interact.toml` variant; the default variant already had it. No unrelated subscription was added.
2. Added an exact-match `GRANTED | MISSING` brand-read scope helper. The authenticated `APP_SCOPES_UPDATE` handler now passes a bounded permission observation to the existing shared-logger-backed webhook outcome. This observation is not treated as proof of the persisted offline installation grant.
3. Preserved existing discount-catalogue scope-change processing and its transaction/queue boundary. Added focused tests for both TOMLs, scope parsing, and the existing scope-update route; retained existing authentication tests.
4. Added `docs/arch-049/SHOPIFY-001-brand-read-permission.md` explaining which app configuration to deploy, existing-merchant approval, `currentAppInstallation.accessScopes` verification, offline session gating, and the separately configured runtime `SCOPES` value.
5. Kept Shopify brand GraphQL retrieval, ShopBrand persistence, media handling and any brand-sync scheduling out of this task, as required by `ARCH-049-BACKGROUND-003` ownership.

### Validation Results

- **PASS — implementation patch equivalence:** The 9 modified files in the uploaded `moda-interact-workspace-ARCH-049-SHOPIFY-001.zip` are byte-identical to applying `ARCH-049-SHOPIFY-001-attempt1.patch` to the original 09:29 snapshot; independent `git apply --check --whitespace=error-all`, `git apply` and `git diff --check` passed in a temporary reconstruction.
- **PASS — TOML parse and invariant checks:** Python `tomllib` parsed both configurations; original scope lists were preserved in their existing order and `read_brand` appears exactly once per configuration; the `app/scopes_update` subscription is present in both. Independently checked using the two supplied workspace snapshots.
- **PASS — ARCH-049-focused Vitest (11:05 log):** `shopify-brand-scope-config.test.ts` (4), `shopify-brand-read-scope.test.ts` (9), `scopes-update.test.jsx` (5), and `auth-catchall.test.ts` (4) — **22/22 passed** in these four relevant suites.
- **EXISTING UNRELATED FAILURE — extra ARCH-045 Vitest (11:05 log):** `shopify-whatsapp-consent-config.test.js` reported 1 failed/1 passed, because it expects `customers_whats_app_marketing_consent/update` in the named app's webhook configuration. The original 09:29 snapshot also omitted this subscription. Aggregate log: 23 passed/1 failed (24 tests). This ARCH-045 discrepancy is not changed in SHOPIFY-001.
- **PASS — Prisma Client generation (11:54 log):** `npm run prisma:generate` generated Prisma Client v6.19.3 using the checked-out `database/prisma/schema.prisma`.
- **PASS — lint, as recorded (11:54 log):** `npm run lint` emitted no ESLint diagnostic; shell continued into the build. An explicit `echo $?` was not captured.
- **PASS — production build (11:54 log):** `npm run build` completed both the client and server React Router builds. Non-fatal Vite/Rollup/Prisma-browser warnings are present; no build failure is shown.
- **INVALID TEST TARGETS — later `npm test -- ...` (11:54 log):** `tests/unit/services/shop-brand-media` and `tests/unit/services/platform-configuration/service.test.ts` do not exist in this Shopify worktree. Vitest returned `No test files found` (exit 1); this does **not** replace the successful ARCH-049-focused test run above.
- **PASS — post-Prisma-generation typecheck (2026-10-27 review):** `npm run typecheck` passed in the canonical implementation worktree after Prisma Client v6.19.3 generation; `react-router typegen && tsc --noEmit` emitted no diagnostics. This resolves the earlier evidence gap; the pre-generation failure remains historical and is not represented as a current failure.
- **PASS — focused task suites independently rerun (2026-10-27 review):** from the canonical implementation worktree, the four task suites `shopify-brand-scope-config.test.ts`, `shopify-brand-read-scope.test.ts`, `scopes-update.test.jsx`, and `auth-catchall.test.ts` passed **22/22**. An initial invocation from the shared checkout resolved aliases against that checkout and failed to import `@/shopify.server`; the rerun from the canonical task worktree passed and is the authoritative result.
- **PASS — patch checks (2026-10-27 review):** parent task `git diff --check` and implementation `git diff --check origin/main...HEAD` passed.
- **CURRENT WORKTREE/PUBLICATION EVIDENCE:** parent HEAD `20aca762f56a18bb738f22b829576d2c1c621ca8` equals `origin/task/ARCH-049-SHOPIFY-001`; implementation HEAD `884d08346bee33227f2f009209cda1ceeaca5311` equals `origin/task/ARCH-049-SHOPIFY-001`. Both canonical worktrees are clean and registered on the expected branch. Recursive submodule status is `8f3d58542372fb9a71d97e5b340c2fc33a7ac8cf database (heads/main)`; this records the currently checked-out pinned gitlink, not a claim that submodules were absent.
- **LIVE CONFIG/GRANT NOT VERIFIED:** No Shopify CLI deployment, installed-shop approval, effective runtime `SCOPES` value, or live `currentAppInstallation.accessScopes` result is included. The rollout runbook explicitly gates Background brand reads on an actual offline grant.

### Deviations

The optional, additional ARCH-045 consent webhook configuration test has a baseline mismatch; its failure was not fixed here because modifying unrelated webhook contracts is excluded by this task. No implementation-scope deviation was identified.

### Assumptions

Both supplied Shopify app TOML variants are relevant to local validation, but they refer to **different Shopify app client IDs**. Which one is deployed in the target environment, along with the external runtime `SCOPES`, must be established at deployment. No claim is made that a merchant has approved `read_brand` or that a live offline session has it.

### Unresolved Issues

- **Review evidence:** The 11:54 log names dedicated parent and implementation worktree paths and shows the implementation-branch push, but the launcher-prepared start-of-attempt synchronization packet and parent task-branch publication evidence were not included. Supply these for final architectural review; the task is not architect-accepted on the basis of this handoff.
- **RESOLVED — review evidence:** The canonical parent branch now contains the review handoff at `20aca762f56a18bb738f22b829576d2c1c621ca8`; both task branch heads and clean worktrees were independently checked during this reconciliation. The original launcher-prepared packet is not reconstructed; report only the observed current worktree, commit and ancestry evidence.
- **RESOLVED — validation gap:** Post-Prisma-generation `npm run typecheck` passed during this reconciliation. The focused ARCH-049 suites also passed 22/22.
## Developer Self-Review Passed — Attempt 1

### Review Decision

Attempt 1 passes developer self-review. Required Work Items and Acceptance
Criteria are checked complete. The implementation is limited to Shopify
configuration, permission observation, documentation and focused tests; it does
not implement brand retrieval or persistence. The missing post-generation
typecheck evidence is resolved by a passing rerun. The known ARCH-045 baseline
test discrepancy and live deployment/merchant-grant verification remain
explicitly outside this task's local validation and must not be presented as
passed.

### Evidence Reviewed

- Parent task worktree is clean on `task/ARCH-049-SHOPIFY-001` at
	`20aca762f56a18bb738f22b829576d2c1c621ca8`, matching its origin task branch.
- Shopify implementation worktree is clean on `task/ARCH-049-SHOPIFY-001` at
	`884d08346bee33227f2f009209cda1ceeaca5311`, matching its origin task branch.
- `npm run typecheck` passed after Prisma Client generation.
- The four focused ARCH-049 suites passed 22/22 from the canonical
	implementation worktree; both task diffs pass `git diff --check`.
- The existing separate ARCH-045 consent webhook configuration test mismatch
	remains unchanged. Live app deployment, merchant scope approval and effective
	runtime `SCOPES` remain unverified rollout checks; no such result is claimed.

### Attempt State

Transitioned to `review`; `executor: null`, `claimed_at: null`, `attempt: 1`.
`completion_mode: developer` remains in force, so explicit developer completion
is pending. No dependent task was started, and no branch was merged to `main`.

## Architect Review
- **Separate baseline issue:** ARCH-045 consent webhook configuration test mismatch remains in its owning scope.
- **Deployment:** Live scope approval, installed-offline-token verification and deployment selection remain untested; record at rollout, before any Background brand GraphQL read.

### Architectural Concerns

The scope-update webhook report is an observation, not a substitute for an authenticated offline-token grant check. Background-003 must independently enforce missing-scope behaviour before Shopify brand reads. No new cross-service contract, schema or background workflow is introduced.

## Architect Review

### Review Status

Pending.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not reviewed.

### Follow-up

None.
