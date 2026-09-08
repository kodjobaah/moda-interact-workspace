---
id: ARCH-007-BACKGROUND-007
architecture_id: ARCH-007
title: Publish paid UsageEvents idempotently with retries and compensating corrections
task_kind: publication
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 110
executor: null
claimed_at: null
attempt: 3
depends_on: 
  - ARCH-007-BACKGROUND-003
  - ARCH-007-BACKGROUND-006
enables:
  - ARCH-007-BACKGROUND-008
  - ARCH-007-BACKGROUND-009
  - ARCH-007-ADMIN-003
created: 2026-09-07
updated: 2026-09-08
---

# ARCH-007-BACKGROUND-007: Publish paid UsageEvents idempotently with retries and compensating corrections

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Implement the database-driven outbox publisher that claims due Shopify-reportable UsageEvents, sends exactly one App Event request per row using BACKGROUND-006, and persists retry/reported/needs-attention state without affecting business usage.

## Context

Paid recovery creation commits locally before Shopify billing publication. Horizontal billing workers and external timeouts are expected, so claim/idempotency/retry state must be explicit.

## Scope

Publisher service/processor and focused unit + disposable PostgreSQL concurrency tests. A full independent worker entrypoint/reconciliation scheduler is BACKGROUND-008.

## Out of Scope

- Subscription reconciliation.
- Creating positive recovery usage (BACKGROUND-003).
- Admin correction UI (ADMIN-004).

## Requirements

- Select a bounded page of due `PENDING|RETRYABLE` rows ordered by due/occurredAt/id with supporting indexes. Never unbounded scan.
- Claim each row with conditional Prisma update from eligible state to IN_FLIGHT and increment/report attempt metadata. Zero affected rows means another worker owns it.
- Validate reportable row has non-null shop Shopify GID, event handle, permanent idempotency key and non-zero quantity before provider call; missing mapping becomes NEEDS_ATTENTION without network send.
- Call App Events adapter once per claimed attempt using persisted/snapshotted values exactly.
- Success => REPORTED, reportedAt, bounded provider response, clear retry fields.
- Transient/ambiguous => RETRYABLE with bounded exponential-or-scheduled backoff and same idempotency key. Do not rely on generic BullMQ retries to change event identity.
- Definitive meter/subscription/period/configuration rejection => NEEDS_ATTENTION with code and reconciliation-needed signal; do not retry forever.
- Correction UsageEvents with negative quantity use the same path and their own idempotency key. Do not edit original positive event.
- If process crashes after Shopify accepts but before DB marks REPORTED, next attempt sends same permanent key; Shopify deduplication makes this safe.
- Redis scheduling failure after durable retry/pending state must be recoverable by BACKGROUND-008 reconciliation scan.

## Work Items

- [x] Implement bounded due query and atomic conditional claim.
- [x] Implement provider result -> durable state transition/backoff.
- [x] Support positive and negative quantities.
- [x] Add unit tests for classifications/crash window.
- [x] Add concurrent publisher PostgreSQL test proving at most one provider invocation for two workers that can both see the same row before claim (mock provider call after claim).
- [x] Test accepted-provider then DB-update failure replay uses same key.

## Interfaces / Contracts

State machine:

```text
PENDING/RETRYABLE -> IN_FLIGHT -> REPORTED
                              -> RETRYABLE
                              -> NEEDS_ATTENTION
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-BACKGROUND-008
- ARCH-007-ADMIN-003

## Acceptance Criteria

- [x] Two workers cannot independently claim one due row.
- [x] Crash after provider success cannot create a different App Event identity.
- [x] Negative correction publishes without original mutation.
- [x] Permanent configuration failure stops retry storm and is Admin-visible.
- [x] Redis failure cannot lose durable due state.
- [x] No raw SQL; concurrency test and repository validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


## Completion Report

### Status

Ready for Review (Attempt 3)

### Files Changed

- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/tests/unit/services/shopify-usage-event-publisher.service.test.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-007-durable-shopify-billing-publisher.md`

### Work Completed

- Preserved the bounded due selection, conditional claims, stale-claim recovery, report validation, permanent idempotency keys, provider classifications, compensating negative quantities, durable transitions, and response summaries from Attempt 1.
- Lazily create and cache the default `ShopifyAppEventsClient` once per publisher service instance; explicitly injected providers remain unchanged and concurrent scans share the cached client.
- Defer default-client construction until after stale recovery, due-row selection, claim, and reportability validation; empty scans do not require App Events credentials.
- Key retry backoff to the post-claim attempt number, producing 60 seconds, 120 seconds, 240 seconds and a 60-minute cap without jitter.
- Updated the unit harness to model Prisma-style `{ increment: 1 }`, due-time filtering, selected-row snapshots and stale claim recovery.
- Added regressions for zero-due lazy construction and invalid default configuration transitioning a claimed valid event to `NEEDS_ATTENTION`, while preserving provider reuse and retry timing coverage.

### Validation Results

- Focused publisher unit suite: 10 tests passed.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- Disposable PostgreSQL concurrency test: 1 test passed (`npm run test:integration -- tests/integration/shopify-usage-event-publisher.concurrency.integration.test.ts`).
- Full background suite: 316 passed, 7 skipped; 2 unrelated existing failures remain in `tests/unit/services/pending-recovery-candidate.service.test.ts`.
- Editor diagnostics for the changed publisher source/test: no errors.
- `git diff --check`: passed.

### Deviations

The full suite retains the two documented pending-recovery candidate baseline failures; no unrelated production code was changed.

### Assumptions

The accepted BACKGROUND-006 adapter remains the owner of bearer-token caching and single-flight refresh; the publisher only reuses its client instance. Configuration failures are durable publisher state, not network attempts.

### Unresolved Issues

The two unrelated pending-recovery candidate failures remain for architect review and are outside BACKGROUND-007's publisher scope.

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is architect-accepted Complete.

The final Attempt 2 correction is implemented correctly:

- default App Events client construction no longer occurs at the start of `publishDue()`;
- stale-claim recovery and bounded due-row selection occur without requiring provider credentials;
- an empty due scan does not call the provider factory;
- a valid claimed row resolves the provider only inside the existing per-row provider/state-transition try/catch;
- default client configuration failure therefore transitions the claimed UsageEvent to `NEEDS_ATTENTION` instead of escaping and aborting the scan;
- no provider network call occurs when configuration validation fails.

The accepted Attempt 2 behavior remains intact:

1. successful default `ShopifyAppEventsClient` construction is cached once per `ShopifyUsageEventPublisherService` instance;
2. consecutive/concurrent scans on one service instance share the BACKGROUND-006 token cache and single-flight refresh;
3. explicitly injected providers are unchanged;
4. claimed-attempt retry backoff remains:
   - attempt 1 -> 60 seconds;
   - attempt 2 -> 120 seconds;
   - attempt 3 -> 240 seconds;
   - bounded at 60 minutes;
5. the permanent Shopify idempotency key remains unchanged across retries/replays;
6. bounded `PENDING|RETRYABLE` selection and stale `IN_FLIGHT` recovery remain durable;
7. conditional `updateMany` claim prevents two workers from independently owning the same row;
8. provider success -> `REPORTED`;
9. transient/ambiguous provider failure -> `RETRYABLE`;
10. definitive configuration/request/period/meter failure -> `NEEDS_ATTENTION`;
11. positive and negative UsageEvents use the same path;
12. accepted-provider / DB-update crash replay retains the same permanent Shopify event identity;
13. the publisher remains generic/report-state-driven and has NO `RECOVERY_CONVERSATION` metric filter;
14. later reportable metrics such as `RECOVERY_CREDIT_PACK_PURCHASE` can use the same publisher after their schema/Shared tasks are accepted;
15. no raw SQL is introduced.

### Reviewed Files

- `moda-interact-background/src/services/shopify-usage-event-publisher.service.ts`
- `moda-interact-background/tests/unit/services/shopify-usage-event-publisher.service.test.ts`
- `moda-interact-background/tests/integration/shopify-usage-event-publisher.concurrency.integration.test.ts`
- `moda-interact-background/src/providers/shopify-app-events.provider.ts`
- `docs/decisions/background/ARCH-007/BACKGROUND-007-durable-shopify-billing-publisher.md`

### Validation Reviewed

Attempt 3 Completion Report records:

- focused publisher unit suite: 10/10 passed;
- build: passed;
- Prisma validation: passed;
- disposable PostgreSQL concurrency test: passed;
- full suite: 316 passed, 7 skipped, with 2 documented unrelated baseline failures;
- diagnostics: clean;
- `git diff --check`: passed.

Architect inspection additionally verified:

- `getProvider()` is called only after claim/reportability validation and inside the provider try/catch;
- the no-due regression proves the provider factory is not called;
- invalid default configuration produces a durable `NEEDS_ATTENTION` result without rejecting `publishDue()`;
- the existing cached-provider reuse regression remains;
- the existing claimed-attempt retry/idempotency regression remains;
- the PostgreSQL concurrency regression remains unchanged.

The architect did not rerun the Node suite from the extracted review archive because installed dependencies were not included.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-BACKGROUND-007` is Complete.

Downstream consequences:

- `ARCH-007-BACKGROUND-009` remains Pending because `ARCH-007-DATABASE-005` and `ARCH-007-SHARED-006` are not yet Complete.
- `ARCH-007-BACKGROUND-008` remains Pending because BACKGROUND-005 and BACKGROUND-009 are not yet Complete.
- Any Admin task whose remaining sole dependency is BACKGROUND-007 may be promoted only after its current task YAML/index is checked by `moda_architect`.

No system-test task is automatically started.
