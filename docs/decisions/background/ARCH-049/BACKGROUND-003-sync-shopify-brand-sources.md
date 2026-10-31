---
id: ARCH-049-BACKGROUND-003
architecture_id: ARCH-049
title: Synchronise Shopify Brand API sources into commerce.ShopBrand
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-049-DATABASE-001", "ARCH-049-BACKGROUND-002", "ARCH-049-SHOPIFY-001"]
enables: ["ARCH-049-SYSTEM-TEST-001"]
created: 2026-10-25
updated: 2026-10-30
---

# Synchronise Shopify Brand API sources into commerce.ShopBrand

## Architecture

`ARCH-049` — `docs/architecture/ARCH-049-shopbrand-public-media-configuration.md`; coordinator `moda_architect`. This task is materialised on its canonical parent task branch and prepared for developer Attempt 1.

## Objective

Use the existing Background authenticated Shopify GraphQL client to read the merchant's Brand data and persist platform-neutral ShopBrand source metadata. No new Shopify app ingestion service is created.

## Context

The Shopify app needs `read_brand`, supplied by the narrow SHOPIFY-001 task. The provided snapshot has a token-fetching service and generic GraphQL client path but no ShopBrand writer. Background source sync must reuse BG002's exported row-locked source-update module, not implement a parallel JSONB state machine. The BG002 prerequisite is intentional: this task imports that implementation across Background module boundaries; Shopify grant configuration alone does not supply its persistence operations.

## Scope

- Add `src/services/shop-brand-media-shopify/` with GraphQL request/parser, canonical source mapping, bounded refresh scheduler and typed error handling.
- Reuse `shopify-session.service.ts` authentication and existing Background Shopify GraphQL conventions.
- Persist `brandName`, logo/alt/dimensions, squareLogo when available or explicit fallback, coverImage source, `fetchedAt` and `lastRefreshedAt` via the canonical ShopBrand row.
- Invoke BG002 source updates for changed/removed per-role source, without downloading any image in this module.

## Out of Scope

- Changing Shopify app scopes (SHOPIFY-001), WooCommerce extraction, R2 object storage, template sending or direct WordPress access.

## Requirements

### R1. Shopify provider reads

Query the authenticated Shopify Admin GraphQL `shop { name brand { ... } }` via an API version supported by the installed Shopify client and the `read_brand` scope, using documented `BrandingBrand` fields. Retrieve available default `logo` and `coverImage` source URL, source ID/dimensions, and brand name. The current Admin `BrandingBrand` may not return a dedicated `squareLogo`; **do not invent a nonexistent GraphQL property**. If no independently supported square source exists, record `squareLogoUrl=null` and let the documented derived square-image fallback process the main logo. Treat `brand=null`, no image, missing grant, GraphQL errors, rate limit and disabled Shop separately.

### R2. Mapping

From the verified authenticated shop context, map:

```text
shop.name / configured Brand display name -> ShopBrand.brandName
brand.logo original or supported transformed URL -> ShopBrand.logoUrl
brand.logo dimensions when returned -> ShopBrand.logoWidth/logoHeight
brand.coverImage source URL -> ShopBrand.coverImageUrl
supported square-logo source (if provided) -> ShopBrand.squareLogoUrl
```

Do not fabricate alt text or width/height for unavailable sources. Use provider image ID/update/reference when available to build a stable source fingerprint; the canonical BG002 observation algorithm increments generation when the effective locator changes. Persist shopId derived from the authenticated Shop record, never from untrusted response properties alone.

### R3. Refresh/ordering

Enqueue initial sync for eligible connected Shopify shops and a bounded daily refresh (at most one per 24 hours by default). Rate-limit and back off on 429 and provider failures; do not overwrite current source with null on an **unsuccessful** API response. On a **successful** response proving source removed, mark the relevant role MISSING. Source changes update PostgreSQL and are recovered by BG002 scan even if a queue wake fails. Never fetch/resize images here.

### R4. No unsupported permission workaround

Missing `read_brand` is a per-shop provider-auth failure; log a bounded code and route to Shopify-authorisation work. Do not scrape storefronts or use merchant WordPress endpoints as a workaround.

## Work Items

- [x] Add Shopify brand reader/parser with mocked GraphQL fixture.
- [x] Add initial/daily sync scheduling with per-shop limits.
- [x] Integrate only with ShopBrand row and BG002 source updater.
- [x] Cover null/missing/scope error/rate-limit/change/removal with tests.

## Interfaces / Contracts

Consumes existing Shopify app authentication (`getShopifyAccessToken`) and the BG002 `SourceObservation`/CAS repository; produces original source fields in `commerce.ShopBrand`. No new Shared contract or Shopify app service. `ARCH-049-SHOPIFY-001` owns `read_brand` scope; BG003 owns fetch.

## Dependencies

- ARCH-049-DATABASE-001
- ARCH-049-BACKGROUND-002 — owns the source-update helper consumed by this synchroniser.
- ARCH-049-SHOPIFY-001 — owns the `read_brand` permission and reauthorisation.

## Enables

- ARCH-049-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Shopify brand changes and removals reflect in correct ShopBrand roles without cross-tenant writes.
- [x] Missing `read_brand`, provider error or rate limit preserves last known source state and produces clear failure, not arbitrary null erasure.
- [x] Daily sync is bounded and no image decoding/R2 work is duplicated.

## Validation

- [x] GraphQL fixture tests including data/missing media, 403 missing grant, 429, stale observation and change.
- [x] Focused authenticated tenant tests and due-scheduling validation.
- [x] Relevant Background lint/typecheck/tests and `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation are complete, record the Completion Report and change task status to `review`; hand off to `moda_architect` and STOP. Do not continue into a dependent task or change an `_index.md`.

## Implementation Notes

All task work must use the canonical launcher-provided **dedicated parent and implementation worktrees**, synced task/<TASK_ID> branches and start-of-attempt evidence. Inspect the actual pinned package scripts, source and existing conventions before editing. Do not merge branches, push main, edit another repository, start an enabled task or change any `docs/decisions/**/_index.md`. Use structured logging via `@modainteract/moda-interact-shared/logging`; secrets and full untrusted URLs must not enter diagnostics. Document changed files, relevant test commands, results, security/tenant checks, commits and worktree evidence in the Completion Report.

No additional assumptions are authorised.

## Completion Report

### Status

Attempt 2 passed developer self-review on 2026-10-31 and is submitted for architect review. `completion_mode: developer`; explicit developer completion remains pending. Attempt 1's changes-requested review is preserved below.

### Files Changed

Implementation repository `moda-interact-background`, task branch `task/ARCH-049-BACKGROUND-003` at `bcac6ed` (matching `origin/task/ARCH-049-BACKGROUND-003`):

- `database` submodule gitlink, updated to `f16d5fc` while synchronizing Background `origin/main`.
- `docs/arch049-shopify-brand-sources.md` and `package.json`.
- `src/entrypoints/recovery.ts`.
- `src/services/shop-brand-media-orchestration/contracts.ts`, `repository.ts`, and `state.ts`.
- New `src/services/shop-brand-media-shopify/contracts.ts`, `mapping.ts`, `reader.ts`, `runner.ts`, and `service.ts`.
- New `tests/integration/shopify-brand-sources.integration.test.ts` and unit tests under `tests/unit/services/shop-brand-media-shopify/`.
- Attempt 2 correction in `src/services/shop-brand-media-orchestration/repository.ts`: pass the current Shop domain from the row-locked transaction into BG002 claim/complete/fail transitions and retain the domain in `ScannedBrandRow`.
- Attempt 2 test correction in `tests/unit/services/shop-brand-media-shopify/scheduler.test.ts`: pass a valid Shopify domain to `claimRole` in the durable metadata-preservation test.

The assigned agent `moda_background` provided the requested bounded implementation assistance for the two Attempt 2 corrections. The developer reviewed and validated the changes. No submodule pointer, architecture index, or `main` branch was modified.

### Work Completed

- Added authenticated Shopify Admin GraphQL Brand source reading, provider-image identity mapping, explicit square-logo fallback, typed provider failures, and bounded response/request handling.
- Added bounded initial/daily source scheduling over active Shopify shops, per-shop leases, persisted retry/cadence metadata, and Recovery-worker startup/shutdown wiring.
- Integrated source observations and original ShopBrand fields through the BG002 repository's row-locked JSONB update path; added reader/scheduler unit tests and PostgreSQL integration scenarios for removals, failed reads, stale claims, role ordering, and tenant/platform isolation.
- The implementation does not fetch or resize media and does not add a new Shopify permission, queue, table, or column.
- Restored the Background implementation worktree's installed packages using `npm ci`; the existing lockfile pins Shared `2.7.2`, and the restored package exposes `./woocommerce`. No manifest or lockfile change resulted.

### Validation Results

- **PASS** — `npm run test:arch049-shopify-brand:unit`: 53/53 tests in 5 files, rerun on 2026-10-31 after the Attempt 2 corrections and lockfile dependency restoration.
- **PASS** — `npm run test:arch049-shopify-brand:postgres`: 5/5 PostgreSQL integration tests, rerun on 2026-10-31.
- **PASS** — `npx tsc --noEmit`: no diagnostics after `npm ci` installed the lockfile-pinned `@modainteract/moda-interact-shared@2.7.2` (which includes the declared `./woocommerce` export). The prior TS2307 was caused by stale installed Shared `2.5.1`, not source changes.
- **PASS** — `npm run build`: Prisma Client 6.19.3 generation and TypeScript compilation completed successfully after dependency restoration.
- **PASS** — `npx eslint src/services/shop-brand-media-orchestration/repository.ts tests/unit/services/shop-brand-media-shopify/scheduler.test.ts`.
- **BASELINE FAILURE, UNRELATED** — `npm run lint` reports one `preserve-caught-error` diagnostic in unchanged `src/services/translation-reconciliation.service.ts:218`. Its blob `997f365833a0518c1410da31c262d2babf6f4bc0` matches `origin/main`; both Attempt 2 changed files pass ESLint.
- **PASS** — `git diff --check origin/main...HEAD` and `git diff --check bcac6ed^..bcac6ed`.
- **PASS** — Implementation branch is clean at `bcac6edc1c4c6aaca8fb506f8fc2b0c8653a4065`, matching `origin/task/ARCH-049-BACKGROUND-003` (`rev-list` divergence 0/0). Parent claim branch is clean at `24a9449480f09d3bc6304315ef769504a9504297`, matching its origin task branch. Parent report update for this review is committed/published separately.
- A live Shopify merchant grant and production provider read were not tested; no live-provider result is claimed.

### Deviations

- The implementation task branch includes the `origin/main` synchronization and database gitlink update described above. No other cross-repository source was edited.
- Full repository lint retains the explicitly documented unrelated baseline diagnostic. The changed files pass focused lint; all implementation-focused tests, PostgreSQL integration, typecheck, and build pass.

### Assumptions

None beyond the explicit architecture/task contract.

### Unresolved Issues

- Live Shopify scope approval and a production-provider read remain rollout/system-test evidence; they were not prerequisites available in this local task run and are not claimed as passed.
- The repository-wide lint baseline issue remains in unchanged `translation-reconciliation.service.ts:218`; it is outside this task's changed-file scope.

### Architectural Concerns

No additional architecture change is identified. The blocking issue is an incomplete integration with BG002's domain-pinned repository API, not a reason to create a parallel ShopBrand state machine.

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

## Execution Ownership Amendment and Claim

- On 2026-10-27, `/moda_developer_create ARCH-049-BACKGROUND-003` explicitly took over the ready agent-owned task for developer execution. `assigned_agent: moda_background` is unchanged; `execution_mode` and `completion_mode` are now `developer`.
- Developer Attempt 1 was claimed at `2026-10-27T15:57:14Z` after verifying `ARCH-049-DATABASE-001`, `ARCH-049-BACKGROUND-002`, and `ARCH-049-SHOPIFY-001` were complete and preparing both canonical task worktrees.
- Parent task branch `task/ARCH-049-BACKGROUND-003` was created from current parent `origin/main`; implementation branch `task/ARCH-049-BACKGROUND-003` was created from current Background `origin/main`. Both task worktrees were clean before the claim. The shared Background `main` checkout's nine local-only commits were not used or modified.

## Developer Self-Review - Changes Requested (Attempt 1)

- Review outcome: **Changes Requested**. Attempt 1 remains the reviewed attempt; this transition does not claim Attempt 2.
- The task-specific PostgreSQL integration suite passed 5/5, and the task diff passes `git diff --check`.
- The focused unit suite failed 1/53 in the BG002 media-claim metadata-preservation test. The test invokes the current `claimRole` API without its required shop domain.
- `npx tsc --noEmit` reported 12 changed orchestration type errors caused by the incomplete domain-aware `editLocked`/`ScannedBrandRow` contract, plus one unresolved Shared `woocommerce` export in unchanged `src/events/woo-checkout-capture.ts`.
- Required before the next review: complete and typecheck the BG002 domain-aware repository/scanner integration; update the affected unit fixture to the valid `claimRole` contract; establish the baseline status of the unchanged Shared export diagnostic; rerun focused tests, PostgreSQL integration, typecheck/build, lint, and whitespace checks.
- Lifecycle transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. The next `/moda_developer_create` claim increments the attempt exactly once. No downstream task was started and no task branch was merged to `main`.

## Developer Self-Review Passed (Attempt 2, 2026-10-31)

- Outcome: **passed**. The domain-aware BG002 repository integration and affected fixture are corrected; the task Work Items, Acceptance Criteria, and focused validation are complete.
- `editLocked` now forwards the Shop domain returned under the existing `FOR UPDATE OF brand, shop` lock. BG002 claim, completion, and failure paths retain their domain-pinned state checks; Shopify media scans carry `domain` into the scanner. No tenant/domain validation was weakened.
- Updated the metadata-preservation fixture to pass a valid `shop-1.myshopify.com` domain to `claimRole`.
- The assigned agent `moda_background` made these two bounded changes at the developer's request. Implementation commit `bcac6edc1c4c6aaca8fb506f8fc2b0c8653a4065` is published on `origin/task/ARCH-049-BACKGROUND-003`; implementation worktree is clean and synchronized.
- Validation passed: focused unit **53/53**, PostgreSQL integration **5/5**, `npx tsc --noEmit`, `npm run build`, focused ESLint for both changed files, and `git diff --check`.
- Environment correction: `npm ci` restored the lockfile-pinned Shared `2.7.2`; the earlier TS2307 was from stale installed `2.5.1` and is resolved. Full `npm run lint` still reports one unrelated existing diagnostic in `translation-reconciliation.service.ts:218`; the file is unchanged and identical to `origin/main`.
- Live Shopify grant/production-provider read was not performed and is not represented as a pass.
- Transition: `status: review`, `executor: null`, `claimed_at: null`, `attempt: 2`. Since `completion_mode: developer`, explicit developer completion remains pending. No dependent task was started and no branch was merged to `main`.
