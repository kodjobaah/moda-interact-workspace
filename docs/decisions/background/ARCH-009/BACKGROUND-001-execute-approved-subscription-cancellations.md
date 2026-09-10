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
status: review
priority: 40
executor: copilot
claimed_at: 2026-09-10T21:26:12Z
attempt: 1
depends_on:
  - ARCH-009-DATABASE-001
  - ARCH-009-SHARED-001
  - ARCH-008-BACKGROUND-001
  - ARCH-007-BACKGROUND-008
enables:
  - ARCH-009-ADMIN-002
created: 2026-09-09
updated: 2026-09-10
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
 - `database` submodule pointer to accepted `ARCH-009-DATABASE-001` revision
 - `package.json`
 - `package-lock.json`
 - `src/entrypoints/billing.ts`
 - `src/providers/shopify-partner-billing.provider.ts`
 - `src/services/subscription-cancellation.service.ts`
 - `tests/unit/providers/shopify-partner-billing.provider.test.ts`
 - `tests/unit/services/subscription-cancellation.service.test.ts`
 - `tests/unit/runtime/observability-startup.test.ts`
### Work Completed
- Adopted Shared `@modainteract/moda-interact-shared@0.9.0` and the accepted ARCH-009 database schema revision.
- Added Partner API 2026-07 `appSubscriptionCancel` using the exact Shared cancellation mapping and bounded provider error classification.
- Added the batch-25 cancellation worker with APPROVED/RETRYABLE/PROVIDER_ACCEPTED eligibility, deterministic ordering, ten-minute lease recovery, version/status CAS claims, identity verification, already-achieved handling, retry/permanent handling, provider-accepted transitions, confirmation, and exactly-once completion messaging.
- Wired cancellation processing into the existing billing worker scan.
- Added focused mode-mapping and lifecycle concurrency/idempotency coverage.
### Validation Results
- `npm run test:unit`: passed, 44 files and 442 tests.
- Focused provider/cancellation tests: passed, 2 files and 12 tests.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
### Deviations
The existing observability startup test required its exact Shared-version assertion to be updated from `0.8.0` to the ARCH-009-required `0.9.0`.
### Assumptions
- The accepted ARCH-009 database task revision `6e91680` is consumed through the implementation repository's database submodule pointer.
- A bounded neutral provider summary is sufficient because Partner acceptance is not local completion.
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
  parent remote task branch fast-forwarded: not-needed; branch did not exist
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed; branch did not exist
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-background`
  commit: `52664ce`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-009/BACKGROUND-001-execute-approved-subscription-cancellations.md`
  claim commit: `b74ad09`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Pending
### Review Notes
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
