---
id: ARCH-009-BACKGROUND-001
architecture_id: ARCH-009
title: Execute human-approved Shopify subscription cancellations
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 4
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-008-BACKGROUND-001
  - ARCH-007-BACKGROUND-008
enables:
  - ARCH-009-ADMIN-002
created: 2026-09-09
updated: 2026-09-11
---

# ARCH-009-BACKGROUND-001

## Objective

Background alone invokes Partner `appSubscriptionCancel`.

## Adopt

Shared 0.9.0 + ARCH-009 schema.

Registry availability was confirmed on 2026-09-10 for `@modainteract/moda-interact-shared@0.9.0`.
The executor must still resolve and verify exactly `0.9.0` during task preflight.

Reuse existing Partner credentials:

```text
SHOPIFY_PARTNER_ORG_ID
SHOPIFY_PARTNER_ACCESS_TOKEN
SHOPIFY_APP_ID
```

## Provider method

Logical interface:

```ts
cancelSubscription({
  shopifyShopId,
  mode,
})
```

Map mode only through Shared:

```text
SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS
```

## Mutation

Partner API 2026-07:

```text
appSubscriptionCancel(
  appId
  shopId
  deferCancellation
  prorate
  skipFinalUsageCharge
)
```

No consumer-created boolean mapping.

## Worker

Batch 25.

Eligible:

```text
APPROVED
RETRYABLE due
PROVIDER_ACCEPTED verification
```

Order createdAt ASC,id ASC.

## Claim

CAS on id+version+status.

Winner:

```text
PROCESSING
processingStartedAt now
lastAttemptAt now
attemptCount +1
version +1
```

10-minute lease.

Stale PROCESSING without providerAcceptedAt -> RETRYABLE.

With providerAcceptedAt -> verification, never blind repeat.

## Identity verification

Before mutation query Partner activeSubscription.

Require:

```text
providerSubscriptionId == snapshot
planHandle == snapshot
```

Mismatch:

```text
NEEDS_ATTENTION
SUBSCRIPTION_IDENTITY_CHANGED
```

No mutation.

## Idempotent already-achieved

END_OF_CYCLE and same subscription cancelAtPeriodEnd=true:

```text
COMPLETED
```

without mutation.

Immediate and activeSubscription=null:

```text
COMPLETED
```

without mutation.

## Retryable

```text
network
408
409
425
429
5xx
```

Permanent/attention:

```text
missing config
400/401/403/404
GraphQL userErrors
identity mismatch
invalid mode
```

Use existing retry/backoff.

## Provider accepted

```text
PROVIDER_ACCEPTED
providerAcceptedAt now
bounded neutral summary
```

No completion message yet.

## Confirmation

END_OF_CYCLE:

```text
same subscription
cancelAtPeriodEnd=true
```

Immediate:

```text
activeSubscription=null
```

Then COMPLETED.

Normal sync produces NO_CONTRACT for full cancellation.

Never Free.

## Message

First COMPLETED:

```text
BILLING_CANCELLATION_COMPLETED
```

exactly once.

## Tests

- four exact mode mappings;
- identity mismatch no call;
- already deferred no duplicate call;
- immediate no contract no call;
- provider accepted not premature completed;
- confirmation rules;
- retry identity preserved;
- stale worker no double cancel;
- concurrent one CAS winner;
- message once;
- no secrets.

## Validation

```bash
npm run test:unit
npm run build
npm run prisma:validate
git diff --check
```

## Stop

Return review and STOP.

## Completion Report

### Status
Ready for Review
### Files Changed
- `src/services/subscription-cancellation.service.ts`
- `tests/unit/services/subscription-cancellation.service.test.ts`
### Work Completed
- Attempt 3 completed the six Architect Review proof areas with a stateful Prisma-shaped lifecycle fake covering stale lease recovery, provider verification, due/future RETRYABLE selection, confirmation outcomes, deterministic completion messaging, approved identity snapshots, and secret-safe persisted provider failures.
- Added explicit confirmation coverage for END_OF_CYCLE and all three immediate cancellation modes, including no-contract and still-active provider states.
- Added exact due selection assertions for `nextAttemptAt = null` or `nextAttemptAt <= now`, and replay assertions keyed by `createMerchantBillingSystemSourceKey`.
- A new secret-safety regression exposed that arbitrary provider error summaries were persisted verbatim; bounded credential-labelled values are now redacted before persistence. No other production behavior changed.
- Attempt 4 fixed the `Authorization: Bearer <token>` ordering defect by redacting complete authorization-bearer, Shopify access-token, access-token, and standalone bearer forms before fallback matching. Added table-driven persistence regressions for all requested credential variants; no cancellation lifecycle behavior changed.
### Validation Results
- Focused cancellation-service tests: passed, 1 file and 38 tests.
- `npm run test:unit`: passed, 44 files and 487 tests.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
### Deviations
The Attempt 3 scope was test-only unless a regression exposed a genuine defect. The secret-summary regression exposed a real persistence safety defect, so `errorSummary` now redacts credential-labelled values before applying the existing 2,000-character bound.
### Assumptions
The accepted Attempt 1/2 cancellation implementation, Shared 0.9.0 contract, database schema, Partner API 2026-07 mutation, and billing-worker integration remain the baseline. The provider contract does not expose credential material in normal errors; the service redaction is defense in depth for credential-labelled provider exceptions.
### Unresolved Issues
None.
### Architectural Concerns
None.

### Git / VCS

Task branch: `task/ARCH-009-BACKGROUND-001`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-009-BACKGROUND-001`
  parent branch: `task/ARCH-009-BACKGROUND-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-009-BACKGROUND-001`
  implementation branch: `task/ARCH-009-BACKGROUND-001`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: already-current
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: already-current
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-background`
  commit: `c92da43d21d042653338e2000d62327718523d21`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-009/BACKGROUND-001-execute-approved-subscription-cancellations.md`
  claim commit: `f544549`
  review handoff commit: `c64061aad065f554c555ab0afd8de1e1e5c3a315`
  metadata/report commit(s): `c64061aad065f554c555ab0afd8de1e1e5c3a315`
  final parent handoff / branch tip: `f465028d36f9dbe3ff3e92142f407c5d7e82a4ae`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Accepted

### Review Notes

Attempt 4 closes the final security-only Changes Requested contract.

The cancellation lifecycle itself had already satisfied the functional contract at Attempt 3.
Attempt 4 changes only the persisted-error sanitizer and its direct persistence regressions.

Verified sanitizer behavior removes credential values for the required forms:

```text
Authorization: Bearer <token>
Authorization=Bearer <token>
X-Shopify-Access-Token: <token>
X-Shopify-Access-Token=<token>
access_token=<token>
access-token: <token>
Bearer <token>
```

The implementation now redacts complete Authorization/Bearer forms before applying the
generic access-token and bearer fallbacks, preserving the existing 2,000-character summary
bound.

The focused persistence tests exercise these credential forms through
`SubscriptionCancellationService.processDue()` and prove:

- the request reaches the correct RETRYABLE state for the retryable provider error;
- `providerErrorCode` remains the expected bounded provider code;
- `providerResponseSummary` does not contain the supplied secret;
- the persisted summary remains at or below the 2,000-character bound.

The pre-existing permanent-failure regression continues to prove bounded secret-free
persistence for the permanent / NEEDS_ATTENTION path.

No Partner mutation, retry, lease, confirmation, identity, completion-message, worker,
schema, or Shared mapping behavior changed in Attempt 4.

### Functional Contract Preserved

The accepted cumulative BACKGROUND-001 implementation provides:

- Partner `appSubscriptionCancel` only from Background;
- Shopify Partner API `2026-07`;
- exact Shared `SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS` mode mapping;
- batch 25 with deterministic `createdAt ASC, id ASC`;
- exact selected `id + version + status` claim CAS;
- 10-minute stale PROCESSING recovery;
- provider-accepted stale work returns to verification and never blindly repeats mutation;
- exact provider subscription and plan-handle snapshot verification before mutation;
- identity mismatch -> `NEEDS_ATTENTION / SUBSCRIPTION_IDENTITY_CHANGED`;
- END_OF_CYCLE already-deferred idempotent completion without mutation;
- immediate-mode no-contract idempotent completion without mutation;
- retryable classification for network / 408 / 409 / 425 / 429 / representative 5xx;
- permanent attention classification for missing config / 400 / 401 / 403 / 404 /
  GraphQL userErrors / identity mismatch / invalid mode;
- successful provider acceptance -> `PROVIDER_ACCEPTED`, clears stale provider error,
  and does not prematurely emit completion;
- END_OF_CYCLE completion only when the same subscription reports
  `cancelAtPeriodEnd = true`;
- all three immediate modes complete only when `activeSubscription = null`;
- exact-once logical `BILLING_CANCELLATION_COMPLETED` SYSTEM message;
- retry identity preservation;
- stateful stale-worker/no-double-cancel and concurrency regressions;
- bounded secret-safe persisted provider summaries.

### Validation Reviewed

Agent-reported Attempt 4:

```text
focused cancellation-service tests: 38 passed
npm run test:unit:                487 passed
npm run build:                    passed
npm run prisma:validate:          passed
git diff --check:                 passed
```

The supplied review archive does not contain `node_modules`, so npm commands were not
independently rerun by the architect. The architect inspected the actual sanitizer,
persistence tests, cumulative task source and published Git state directly.

### Published Git Verification

Implementation repository:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-001
Attempt 3: 3828b8fccf4260b6736318ff347c8390da97cea0
Attempt 4: c92da43d21d042653338e2000d62327718523d21
```

Attempt 4 is exactly one commit after Attempt 3 and changes only:

```text
src/services/subscription-cancellation.service.ts
tests/unit/services/subscription-cancellation.service.test.ts
```

The cumulative task branch is four commits ahead of `main`, zero behind.

Published parent workspace branch tip:

```text
f465028d36f9dbe3ff3e92142f407c5d7e82a4ae
```

The parent tip follows the Attempt-4 review handoff and records the final task evidence.

### Architecture Conformance
Accepted.

### Follow-up

`ARCH-009-BACKGROUND-001` is Complete.

Do not automatically promote `ARCH-009-ADMIN-002` from this branch alone. Its authoritative
dependencies are:

```text
ARCH-009-ADMIN-001
ARCH-009-BACKGROUND-001
ARCH-009-BACKGROUND-002
```

This acceptance satisfies BACKGROUND-001. BACKGROUND-002 has been separately architect-
accepted on its own task branch, but this B001 parent worktree does not materialize that
separate acceptance, and ADMIN-001 remains Ready rather than Complete here.

Promote ADMIN-002 only after the common parent workspace state records all three individual
dependencies as Complete.

`ARCH-009-SYSTEM-TEST-001` remains terminal/manual-gated and must not execute automatically.
