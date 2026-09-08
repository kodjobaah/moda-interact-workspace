---
id: ARCH-007-BACKGROUND-006
architecture_id: ARCH-007
title: Implement Shopify App Events 2026-07 adapter and expiring token cache
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 70
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-SHARED-002
  - ARCH-007-DATABASE-002
enables: 
  - ARCH-007-BACKGROUND-007
created: 2026-09-07
updated: 2026-09-08
---

# ARCH-007-BACKGROUND-006: Implement Shopify App Events 2026-07 adapter and expiring token cache

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Implement a testable low-level Shopify App Events provider adapter with client-credentials bearer-token caching and strict request/error classification, without selecting or mutating UsageEvent rows.

## Context

The user explicitly requires App Events in the first implementation. This task isolates external HTTP semantics from the durable publisher state machine so retries/DB claims are implemented separately.

## Scope

Background provider/client module, configuration validation and unit tests only. No worker/database selection loop.

## Out of Scope

- UsageEvent claiming/state machine (BACKGROUND-007).
- Subscription Partner API reconciler (BACKGROUND-008).
- Admin retry/correction.

## Requirements

- Use exactly `POST https://api.shopify.com/auth/access_token` with JSON client_id/client_secret/grant_type=client_credentials.
- Use returned access_token and `expires_in`; cache in-process and refresh with a bounded safety margin before expiry. Concurrent token requests should share one in-flight refresh or otherwise avoid a token stampede.
- Use `POST https://api.shopify.com/app/2026-07/events` with Bearer token.
- Event request fields: shop_id, event_handle, timestamp, idempotency_key <=64 chars, attributes.value non-zero. Do not add customer PII attributes.
- Do not change provided occurredAt timestamp or idempotency key inside adapter.
- Classify success, authentication-refreshable, throttled/transient/server/transport ambiguous, and definitive request/configuration/period/meter failures into a small typed result/error taxonomy consumed by BACKGROUND-007.
- On one 401 caused by expired token, invalidate cached token and allow one controlled refresh/retry of the same event; do not unbounded retry inside adapter.
- No SDK/raw SQL required; use injected fetch for tests consistent with existing WhatsApp/provider adapters.
- Never log client secret/bearer token.

## Work Items

- [x] Implement environment/config validator for App Events client ID/secret (reuse existing Shopify app credentials only if architecture/config proves they are the correct Dev Dashboard credentials; do not silently assume Partner token).
- [x] Implement token cache/refresh.
- [x] Implement createBillingEvent adapter and typed error classification.
- [x] Add tests for token caching/concurrent refresh, expiry margin, event request shape, <=64 key enforcement, 401 refresh, 429/5xx/timeout/permanent errors and secret redaction.

## Interfaces / Contracts

External API contract is copied into parent ARCH-007. Adapter input must already contain final snapshotted shopId/eventHandle/occurredAt/idempotencyKey/value.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-007

## Acceptance Criteria

- [x] One token is reused until refresh margin; no token-per-event behavior.
- [x] Event endpoint/version/request matches Shopify 2026-07 contract.
- [x] Permanent billing idempotency key is passed unchanged.
- [x] No PII/secret logging.
- [x] Typed errors let publisher distinguish retry from needs-attention.
- [x] Unit/build validation passes.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact Shared dependency: `@modainteract/moda-interact-shared@0.7.3`. Use the accepted Shopify billing/idempotency helpers rather than defining local substitutes.


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-background/src/providers/shopify-app-events.provider.ts`
- `moda-interact-background/tests/unit/providers/shopify-app-events.provider.test.ts`

### Work Completed

- Added a dedicated Shopify App Events 2026-07 client using the required token and event endpoints with injected fetch and clock dependencies.
- Added dedicated environment credential validation, in-process token caching with bounded expiry margin, and single-flight concurrent refresh.
- Added exact billing event payload construction that preserves the supplied timestamp and idempotency key, rejects invalid values and keys over 64 characters, and emits only the bounded `value` attribute.
- Added one controlled 401 token invalidation/refresh retry and typed classification for authentication, throttling, transient, server, transport, request, period and meter outcomes.
- Added focused coverage for token lifecycle, request shape, retry behavior, error taxonomy, timeout/transport handling and secret redaction.
- Made controlled 401 recovery generation-aware so staggered concurrent rejections of the same stale token share the replacement refresh and both retries use the newer cached token.
- Classified token-endpoint 401/403, event-endpoint 403, and a second event-endpoint 401 after the controlled retry as definitive configuration failures requiring attention.

### Validation Results

- Focused App Events provider suite: 17 tests passed, including the generation-aware concurrent-401 and definitive-authentication regressions.
- `npm run build`: passed, including Prisma generation and TypeScript compilation.
- `npm run prisma:validate`: passed.
- `npm test`: 286 passed, 6 skipped; 3 unrelated baseline failures remain in recovery-routing and pending-recovery-candidate tests.
- `git diff --check`: passed.
- Editor diagnostics for the provider and tests: no errors.

### Deviations

- The published Shared 0.7.3 package exposes billing identity helpers but no App Events client contract, so the provider remains local to `moda-interact-background` as required by the task scope.
- No package publication or version change was performed.

### Assumptions

- Dedicated `SHOPIFY_APP_EVENTS_CLIENT_ID` and `SHOPIFY_APP_EVENTS_CLIENT_SECRET` variables are the Dev Dashboard credentials for App Events; existing merchant Admin API credentials are not silently reused.
- Permanent idempotency and durable UsageEvent selection remain owned by BACKGROUND-007; this adapter forwards the supplied identity unchanged.

### Unresolved Issues

- The three unrelated baseline test failures remain for architect review and are outside this task's changed production path.

### Architectural Concerns

- None within BACKGROUND-006 scope. The adapter intentionally does not select or mutate UsageEvent rows.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted.

The correction pass satisfies both Attempt 1 rework requirements.

1. **Generation-aware stale-token recovery**
   - `createBillingEvent` preserves the token used by the rejected request.
   - `refreshAfterUnauthorized(rejectedToken)` invalidates the cache only when the cached token is still the rejected token.
   - Replacement acquisition returns through the normal cache/single-flight path.
   - A staggered second 401 for the old token therefore reuses the already-installed replacement token instead of clearing it and creating a third token generation.
   - The focused concurrency regression proves two initial event requests use `token-1`, both retries use `token-2`, only one replacement token request is made, and no `token-3` refresh occurs.

2. **Definitive authentication rejection after the controlled retry boundary**
   - token-endpoint HTTP 401/403 -> `configuration`, `retryable: false`, `needsAttention: true`;
   - event-endpoint HTTP 403 -> definitive `configuration` with no token refresh;
   - first event 401 still receives exactly one controlled refresh/retry;
   - a second event 401 after that retry is classified definitive `configuration` and no second internal event retry occurs.

The adapter continues to preserve the ARCH-007 App Events contract: exact 2026-07 endpoints/payload, supplied timestamp/idempotency identity, bounded token cache, injected fetch, secret-safe errors, no UsageEvent claiming/mutation, and no raw SQL.

### Reviewed Files

- `moda-interact-background/src/providers/shopify-app-events.provider.ts`
- `moda-interact-background/tests/unit/providers/shopify-app-events.provider.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-006-shopify-app-events-client.md`
- `docs/decisions/background/ARCH-007/BACKGROUND-007-durable-shopify-billing-publisher.md`

### Validation Reviewed

Completion Report records:

- focused App Events provider suite: 17 passed;
- full suite: 286 passed, 6 skipped, with 3 documented unrelated baseline failures;
- build: passed;
- Prisma validation: passed;
- editor diagnostics: clean for the changed provider/tests;
- `git diff --check`: passed.

No task-scope regression was identified during architect inspection.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-BACKGROUND-007` is now Ready because both dependencies, `ARCH-007-BACKGROUND-003` and `ARCH-007-BACKGROUND-006`, are architect-accepted Complete.

This acceptance does not change the separate `ARCH-007-BACKGROUND-004` blocker: BACKGROUND-004 remains Blocked on `ARCH-007-DATABASE-004`.
