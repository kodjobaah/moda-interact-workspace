---
id: ARCH-053-API-004
architecture_id: ARCH-053
title: Resolve Woo recovery URLs using the canonical configured recovery lifetime
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-016-DATABASE-002
  - ARCH-053-API-002
enables:
  - ARCH-053-SYSTEM-TEST-001
created: 2026-10-31
updated: 2026-10-31
---

# ARCH-053-API-004 — Use canonical lifetime for Woo recovery-link resolution

## Architecture

- Initiative: `ARCH-053`.
- Architecture: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`.
- Coordinator: `moda_architect`.
- Portable definition, **defined but not materialised**; no developer branch, worktree, commit or push is asserted.

## Objective

Replace the resolver's hardcoded seven-day checkout-activity cutoff with the **single persisted platform recovery lifetime** (`public."BackgroundRuntimeConfig"."checkoutRecoveryLifetimeDays"`), without changing token security, tenant isolation, generation selection, restoration response v1 or WordPress customer-facing behaviour.

## Context

In the 2026-10-31 09:57 snapshot, `moda-interact-api/src/woocommerce/recovery-restore/service.ts` declares `MAX_RECOVERY_AGE_MS = 7 * 24 * 60 * 60 * 1000` and accepts `lastExternalActivityAt >= now - MAX_RECOVERY_AGE_MS`. This may reject a newly issued link for a recovery whose merchant configured a seven-day abandonment delay, even while the recovery remains active. The accepted expiry service uses the global `checkoutRecoveryLifetimeDays` setting (default 21 days) with `lastExternalActivityAt <= cutoff` as the expiry boundary. ARCH-016-DATABASE-002 removes the 1–90 PostgreSQL policy restriction. No new URL-expiration setting is authorized.

## Scope

Changes are strictly within `moda-interact-api` plus this assigned task's execution metadata.

1. **Modify** `src/woocommerce/recovery-restore/service.ts`: delete `MAX_RECOVERY_AGE_MS`; obtain `checkoutRecoveryLifetimeDays` from the `id='default'` row of the canonical `public."BackgroundRuntimeConfig"` while resolving an authenticated recovery, validate it, and enforce the strict lifetime predicate on the same recovery's `lastExternalActivityAt`.
2. **Retain** the existing parameterized recovery/shop/installation/latest-generation query and token authorization. Prefer a single parameterized SQL query that `LEFT JOIN`s the global runtime-config row (and selects `checkoutRecoveryLifetimeDays`) rather than a second independently cached configuration; missing config must be detectable and never interpreted as an eligible result. Keep the `Database` port test-injectable.
3. **Modify** `tests/unit/woocommerce/recovery-restore/service.test.ts` and `tests/integration/woocommerce/recovery-restore/service.postgres.test.ts` to add the policy matrix and reject missing/invalid policy, including SQL-backed verification in disposable PostgreSQL.
4. **Update** `scripts/test-arch053-recovery-restore-postgres.mjs` only if the existing disposable fixtures need to create/update the canonical global config row for new test cases; retain cleanup and the existing package script.
5. **Modify** `src/woocommerce/recovery-restore/routes.ts` only if needed to preserve the current uniform 404 for ineligible links and the existing 503 for an unexpected configuration/DB failure. No WordPress/browser changes.

No schema migration, Shared contract publication, additional endpoint, Redis job, new configuration cache or merchant-specific expiry override is allowed.

## Out of Scope

- Background conversation wrappers, template preparation, final Woo send guard and checkout expiry worker (owned by `ARCH-053-BACKGROUND-005` and ARCH-016).
- Restoring coupons, changing an outreach offer or calling WooCommerce merchant endpoints.
- Renewing a link on click, resetting `lastExternalActivityAt`, rotating the generation token, relaxing revocation, changing HTTP v1 request/response shape, or introducing v2/v3.
- Changes to Admin or the ARCH-016 database migration; no new checkout expiration policy.

## Requirements

### Canonical source and exact cutoff

The configuration source is exactly `public."BackgroundRuntimeConfig"` with `id='default'` and integer column `checkoutRecoveryLifetimeDays`. Accept a **non-negative whole number** representable by the existing PostgreSQL `INTEGER`, with default 21, **no artificial maximum**. `0` means a recovery link is age-ineligible immediately, even if all other gates pass. Negative, fractional, missing and non-integer values fail closed. Do not replace missing config with a hardcoded seven-day/21-day fallback.

Apply the same rule as `CheckoutRecoveryExpiryService` to the persisted recovery:

```ts
const ageMs = BigInt(now.getTime()) - BigInt(recovery.lastExternalActivityAt.getTime());
const permittedMs = BigInt(checkoutRecoveryLifetimeDays) * 86_400_000n;
const withinLifetime = ageMs >= 0n && ageMs < permittedMs;
```

Validate both dates before `BigInt` conversion and validate the days as an integer first. Use exact integer-millisecond arithmetic so a valid large PostgreSQL `INTEGER` cannot overflow `Date` construction or lead to a new implicit range cap. At exactly the lifetime cutoff, reject. A future timestamp is invalid. A value of zero is never eligible. Apply the global policy on **every resolver request**, not only after the periodic expiry job has run.

### Resolver behavior and failure classification

- Preserve existing `WooInstallationAuthenticator` principal ownership and `POST /v1/woocommerce/recovery-restore/resolve` contract `woo.restore.resolve.v1` (request: recovery ID and bearer token; positive response: supported snapshot and `outreachOffer`). Never derive a shop from phone number, merchant URL or request body.
- Keep the original strict bearer-token check, latest `(shopId, checkoutToken, generation)`, recovery status, `completedAt`, `expiredAt`, current installation/revocation/credential, Shop.domain/HTTPS/path and supported-snapshot guards. Preserve read-only semantics; no database writes, queued work or customer checkout mutation.
- A correctly configured but too-old/zero-lifetime recovery returns the **same `404 {"error":"restore_unavailable"}`** as all other ineligible links. No precise expiry reason exposed to the plugin/browser.
- A missing/invalid global config or unexpected query/dependency error is **not** a valid negative customer result. Fail closed and propagate to the existing API operational `503` handling (without leaking details to the Woo storefront). Keep errors private, logged through the shared structured Node logger with bounded context and preserved, redacted original error details. Never log the recovery token, complete URL, coupon or customer PII.
- Do not change how completed or superseded recoveries are denied; shortening the Admin lifetime affects the next resolve without changing any recovery row.

## Work Items

- [ ] Inspect the current resolver SQL, route error mapping and accepted ARCH-016 PostgreSQL migration.
- [ ] Remove the seven-day constant; query and validate the canonical configuration on every resolve using an injected/testable database boundary.
- [ ] Apply one strict, safe lifetime comparison against `lastExternalActivityAt`; retain all existing authorization and read-only checks.
- [ ] Update focused unit and disposable-PostgreSQL tests for `0`, `1`, `21`, `91`, `180`, `365`, large PostgreSQL integer, future activity, exact cutoff and config failure.
- [ ] Run declared validations and record worktree, submodule and test-container evidence.

## Interfaces / Contracts

- **Persisted configuration:** `public."BackgroundRuntimeConfig"("id" = 'default', "checkoutRecoveryLifetimeDays" INTEGER NOT NULL)`; owned by ARCH-016. The API reads but does not update it.
- **Persisted recovery:** `commerce."CheckoutRecovery"("id","shopId","checkoutToken","generation","lastExternalActivityAt","status","expiredAt","completedAt", "checkoutUrl", "wooRestoreSnapshot")`, joined to existing Shop/installation identity.
- **Existing endpoint:** `POST /v1/woocommerce/recovery-restore/resolve` using the published `WooRestoreResolveRequestV1Schema` and `WooRestoreResolveResponseV1Schema`. Do not introduce a new wire schema.
- **Responses:** Valid and eligible 200; ineligible 404 `restore_unavailable`; malformed 400; configuration/DB dependency unavailable 503 via existing route mapping.

## Dependencies

- `ARCH-016-DATABASE-002` — accepted migration removing the fixed 1–90 database CHECK constraint.
- `ARCH-053-API-002` — accepted authenticated generation-bound resolver.

## Enables

- `ARCH-053-SYSTEM-TEST-001` once all other terminal-test dependencies complete.

## Acceptance Criteria

- [ ] `MAX_RECOVERY_AGE_MS` and any other API seven-day checkout URL guard are gone; the field-only canonical persisted config read is in effect for every resolution.
- [ ] With lifetime 21, a link whose activity is eight days old is eligible if all other existing guards pass; after exactly 21 days it is rejected. A six-minute-old checkout is not age-rejected.
- [ ] Tests prove `0` always denies, `1` uses the precise cutoff, `91/180/365` and the PostgreSQL `INTEGER` maximum are permitted without a business cap; negative/fractional/missing configuration never grants access.
- [ ] Same strict expiry boundary as Background's expiry worker (`lastExternalActivityAt <= now - lifetimeDays` is ineligible), including one millisecond before versus exactly at cutoff and future timestamps.
- [ ] A switch of the persisted policy from 21 to 1 (or 0) changes the **next** resolver outcome without a service restart or requiring an expiry sweep; no mutable in-memory policy fallback.
- [ ] Verified tenant isolation, installation revocation, token comparison, URL host/subpath, latest generation, supported snapshot and terminal order/status checks remain effective.
- [ ] Uniform customer-denial response; config outage surfaces as internal 503; no token, URL, phone or coupon exposure in logs or returned messages.
- [ ] No changes to API HTTP v1 and Shared v1 contracts, database migration, Admin, Woo plugin or unrelated ARCH-052 discount logic.

## Validation

- [ ] `npx tsx --test tests/unit/woocommerce/recovery-restore/service.test.ts tests/unit/woocommerce/recovery-restore/routes.test.ts`
- [ ] `npm run test:arch053-recovery-restore:postgres` (isolated disposable PostgreSQL, cleanup in finally).
- [ ] `npm run typecheck` and `npm run lint`.
- [ ] `git diff --check` and verified implementation/parent worktree isolation with approved database submodule pin.

## Stop Condition

After the defined Work Items, Acceptance Criteria and Validation have passed, complete only the assigned task's execution metadata and Completion Report, change `status: review`, return to `moda_architect`, and **STOP**. Do not start downstream tasks or update `_index.md` or other repositories.

## Implementation Notes

This is one API task because it owns one API resolver. Do not import `moda-interact-background` source into the API or implement the expiry service again. Duplicated local **business policy** is prohibited; matching the canonical cutoff formula at the API authorization boundary is required for safety and does not justify an additional Shared package release.

## Completion Report

### Status

Not Started — defined but not materialised.

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

The task's prerequisite migration and currently accepted API-002 code will be present in the prepared implementation worktree.

### Unresolved Issues

None asserted. Return any incompatible dependency to `moda_architect` rather than improvising an alternate expiry value.

### Architectural Concerns

None asserted before implementation.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be reviewed.

### Follow-up

None.
