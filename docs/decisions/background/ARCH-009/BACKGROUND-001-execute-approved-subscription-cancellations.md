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
status: ready
priority: 40
executor: null
claimed_at: null
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
Changes Requested

### Review Notes

Attempt 1 gets the main architecture right: Background is the only component invoking Partner `appSubscriptionCancel`; the four modes are sourced from Shared `SHOPIFY_SUBSCRIPTION_CANCELLATION_ARGS`; the worker is bounded to 25 and ordered `createdAt ASC, id ASC`; provider identity is re-read before mutation; already-achieved cancellation is handled without another mutation; provider acceptance is separated from confirmation; completion is guarded by the claimed version/state and the completion SYSTEM message uses an idempotent source key.

Three corrections are required before acceptance.

#### 1. Claim CAS must use the exact status that was selected

The task requires:

```text
CAS on id+version+status
```

The current `claim(id, version, now)` uses:

```ts
status: {
  in: [APPROVED, RETRYABLE, PROVIDER_ACCEPTED]
}
```

That proves only that the row is in some eligible state, not that it is still in the same status that was selected.

Attempt 2 must:

- pass the selected request status into `claim`;
- use exact equality in the `updateMany` predicate:

```text
id == selected id
version == selected version
status == selected status
```

- retain the existing winner transition:
  - `PROCESSING`;
  - `processingStartedAt = now`;
  - `lastAttemptAt = now`;
  - `attemptCount + 1`;
  - `version + 1`;
- do not broaden the claim predicate back to an eligible-status set;
- add a regression proving that a row selected as one lifecycle state cannot be claimed if its status has changed before the CAS, even where the version is unchanged in the test fixture;
- retain the existing concurrent single-winner regression.

This is an exact task-contract correction, not a schema change.

#### 2. Successful provider acceptance must clear a prior provider error code

A request may enter `RETRYABLE` with `providerErrorCode` populated and later succeed.

The current successful mutation transition writes:

```text
status = PROVIDER_ACCEPTED
providerAcceptedAt = now
providerResponseSummary = neutral accepted summary
```

but leaves the old `providerErrorCode` untouched.

That can produce a truthful lifecycle status paired with a stale error code from a previous attempt.

Attempt 2 must set:

```text
providerErrorCode = null
```

when the mutation is successfully recorded as `PROVIDER_ACCEPTED`.

Preserve:

- the bounded neutral provider summary;
- `providerAcceptedAt`;
- no completion message at provider acceptance;
- confirmation-only processing on the next provider verification pass.

Add a regression beginning from a retryable/error-bearing request and proving successful provider acceptance clears the old error code.

#### 3. Complete the mandatory cancellation regression matrix

The current focused cancellation service file covers identity mismatch, already-deferred completion, immediate/no-contract completion, provider-accepted-not-completed, one immediate confirmation case, and a simplified concurrent winner case.

The authoritative task also requires explicit proof of the remaining lifecycle/retry/lease/message/security behavior.

Attempt 2 must add deterministic focused tests for:

1. **batch and ordering**
   - default `take: 25`;
   - `createdAt ASC, id ASC`;
   - RETRYABLE is selected only when due;
   - PROVIDER_ACCEPTED is selected for verification.

2. **exact claim CAS**
   - exact selected status is part of the CAS;
   - changed status loses the claim;
   - two concurrent claimants still yield one provider mutation.

3. **confirmation rules**
   - END_OF_CYCLE + same identity + `cancelAtPeriodEnd=true` -> COMPLETED without another cancellation mutation;
   - END_OF_CYCLE + same identity + `cancelAtPeriodEnd=false` after provider acceptance -> RETRYABLE, not another mutation;
   - END_OF_CYCLE + `activeSubscription=null` after provider acceptance -> not falsely COMPLETED;
   - each immediate mode completes only when `activeSubscription=null`;
   - immediate mode with the original subscription still active remains verification/retry and does not blindly issue another cancellation after `providerAcceptedAt`.

4. **retry classification**
   - network failure -> RETRYABLE;
   - HTTP 408/409/425/429 and representative 5xx -> retryable;
   - HTTP 400/401/403/404 -> permanent / NEEDS_ATTENTION;
   - missing Partner configuration -> permanent / NEEDS_ATTENTION;
   - GraphQL `userErrors` -> permanent / NEEDS_ATTENTION;
   - invalid cancellation mode -> permanent / NEEDS_ATTENTION.

   Provider-level tests may assert `ShopifyPartnerBillingError.retryable` and service-level tests must prove the corresponding lifecycle transition where useful.

5. **retry identity preservation**
   - a retry must retain the approved:
     `providerSubscriptionIdSnapshot`,
     `planHandleSnapshot`,
     `mode`,
     and request identity;
   - the next provider attempt must still verify/cancel against those approved snapshots rather than a newer local projection.

6. **stale lease recovery / no blind repeat**
   - stale PROCESSING with `providerAcceptedAt = null` returns to RETRYABLE;
   - stale PROCESSING with `providerAcceptedAt != null` returns to PROVIDER_ACCEPTED verification;
   - the provider-accepted stale path must call `getActiveSubscription` for verification and must not call `cancelSubscription`;
   - if a recovered request already exposes the required achieved provider state, it completes without a duplicate cancellation call.

7. **message exactly once**
   - first successful COMPLETED transition creates/upserts exactly one
     `BILLING_CANCELLATION_COMPLETED` message;
   - replay/concurrent completion cannot create a second logical message;
   - provider-accepted and retryable states emit no completion message.

8. **no secrets**
   - Partner token is never present in `providerErrorCode` or persisted `providerResponseSummary`;
   - missing-config and HTTP failure summaries remain bounded/non-secret;
   - cancellation provider tests must not assert or snapshot the actual token value into error output.

The tests may use a stateful in-memory Prisma-shaped fake. Prefer that over mocks which return `{count: 1}` for every non-claim update, because lifecycle/CAS behavior needs to be proved rather than assumed.

### Positive Findings To Preserve

- exact Shared dependency `@modainteract/moda-interact-shared@0.9.0`;
- accepted ARCH-009 database submodule revision;
- Partner API `2026-07`;
- mutation variables come only from Shared's cancellation mapping;
- no consumer-created cancellation boolean mapping;
- `getActiveSubscription` verifies provider subscription id and plan handle;
- identity mismatch becomes `NEEDS_ATTENTION / SUBSCRIPTION_IDENTITY_CHANGED` with no mutation;
- END_OF_CYCLE already deferred is idempotently completed;
- immediate no-contract is idempotently completed;
- successful mutation moves to `PROVIDER_ACCEPTED`, not directly to COMPLETED;
- 10-minute stale recovery separates provider-accepted verification from ordinary retry;
- completion uses a Serializable transaction and an idempotent SYSTEM-message source key;
- normal subscription projection is not directly rewritten to Free by this worker;
- cancellation processing is wired into the existing billing worker scheduler;
- worktree isolation and start-of-attempt synchronization evidence are present and conformant.

### Validation Reviewed

Agent-reported Attempt 1:

```text
npm run test:unit:       442 passed
focused cancellation:    12 passed
npm run build:           passed
npm run prisma:validate: passed
git diff --check:        passed
```

The supplied review archive does not contain `node_modules`, so npm validation was not independently rerun by the architect. Source, focused tests, package state, schema pointer and published Git diffs were inspected directly.

### Published Git Verification

Implementation:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-001
commit: 52664cebe7dca8133ce41386cbe7f036af750bd6
ahead of main: 1
behind main: 0
```

Parent task handoff:

```text
repository: moda-interact-workspace
branch: task/ARCH-009-BACKGROUND-001
commit: a29b2443b56f0955ce795b4676fc480b1ed3f965
```

The published implementation diff is limited to the expected ARCH-009 database/shared adoption, billing entrypoint, Partner provider, cancellation service, and focused tests.

### Architecture Conformance
Changes required.

### Follow-up

Attempt 2 must remain on the SAME `ARCH-009-BACKGROUND-001` task and mirrored `task/ARCH-009-BACKGROUND-001` branches.

Attempt 2 scope is intentionally narrow:

1. make claim CAS exact on selected `id + version + status`;
2. clear stale `providerErrorCode` on successful PROVIDER_ACCEPTED transition;
3. complete the mandatory regression matrix above;
4. do not redesign the provider mutation, schema, Shared mapping, or worker topology;
5. rerun:
   - `npm run test:unit`;
   - focused provider/cancellation tests;
   - `npm run build`;
   - `npm run prisma:validate`;
   - `git diff --check`;
6. update the Completion Report with Attempt 2 files, validation, worktree/sync evidence, implementation commit and parent handoff commit;
7. preserve this Architect Review until the next architect decision;
8. return the same task to `review`;
9. STOP.

`ARCH-009-ADMIN-002` remains Pending until BACKGROUND-001, BACKGROUND-002 and ADMIN-001 are all architect-accepted Complete.
