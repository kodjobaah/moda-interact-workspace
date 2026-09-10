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
attempt: 2
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
 - `src/services/subscription-cancellation.service.ts`
 - `tests/unit/providers/shopify-partner-billing.provider.test.ts`
 - `tests/unit/services/subscription-cancellation.service.test.ts`
### Work Completed
- Corrected cancellation claims to compare the selected request status as part of the `id + version + status` CAS.
- Cleared stale `providerErrorCode` when a successful Partner mutation enters `PROVIDER_ACCEPTED`.
- Added Attempt 2 regressions for exact claim races, batch/due ordering, confirmation/no-contract rules, retry identity preservation, stale lease paths, exactly-once completion replay, HTTP/GraphQL/configuration/invalid-mode classification, and secret-safe provider errors.
### Validation Results
- Focused provider/cancellation tests: passed, 2 files and 34 tests.
- `npm run test:unit`: passed, 44 files and 464 tests.
- `npm run build`: passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
### Deviations
None.
### Assumptions
The Attempt 1 implementation and accepted Shared/database revisions remain the baseline; Attempt 2 changes only the Architect-requested service behavior and regressions.
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
  commit: `e7ad61e`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-009/BACKGROUND-001-execute-approved-subscription-cancellations.md`
  claim commit: `681d7ff`
  review handoff commit: `1308909`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 2 closes both production-code defects from Attempt 1:

- claim CAS now uses the exact selected `id + version + status`;
- successful Partner acceptance now clears stale `providerErrorCode`.

The production cancellation path is therefore acceptable as implemented. No further service/provider redesign is requested.

The remaining issue is regression completeness. The prior Architect Review explicitly required deterministic coverage of the stale-lease/no-blind-repeat, confirmation, retry identity, message-idempotency and secret-safety paths. Attempt 2 materially expands the suite, but several of those required proofs are still only partial or are asserted as mock call shapes rather than exercised as lifecycle behavior.

Attempt 3 is TEST-ONLY unless a new test exposes a genuine implementation defect.

#### 1. Exercise stale provider-accepted lease recovery end-to-end

The current test:

```text
"recovers stale processing leases into retry and provider verification paths"
```

only proves that the two recovery `updateMany` calls are issued. Its fake does not mutate the durable row into the recovered status and therefore does not exercise the subsequent provider-verification path.

Add a stateful regression that starts with:

```text
status = PROCESSING
processingStartedAt <= now - 10 minutes
providerAcceptedAt != null
```

and proves one `processDue()` pass:

1. recovers the row to `PROVIDER_ACCEPTED`;
2. selects/claims that recovered row for verification;
3. calls `getActiveSubscription`;
4. NEVER calls `cancelSubscription`;
5. if the provider already reports the required achieved state:
   - END_OF_CYCLE + same identity + `cancelAtPeriodEnd=true`, or
   - an immediate mode + `activeSubscription=null`,
   then the request completes and emits the completion message without another Partner cancellation mutation.

Also add the sibling stale path:

```text
status = PROCESSING
processingStartedAt <= now - 10 minutes
providerAcceptedAt = null
```

and prove it becomes RETRYABLE/due and does not inherit a false provider-accepted state.

Use a stateful Prisma-shaped fake or focused DB integration; do not satisfy this by only inspecting the recovery query arguments.

#### 2. Complete explicit confirmation coverage

Add direct PROVIDER_ACCEPTED confirmation tests for:

- `END_OF_CYCLE` + exact identity + `cancelAtPeriodEnd=true`
  -> COMPLETED, no `cancelSubscription`;
- `END_OF_CYCLE` + exact identity + `cancelAtPeriodEnd=false`
  -> RETRYABLE, no `cancelSubscription`;
- `END_OF_CYCLE` + `activeSubscription=null`
  -> RETRYABLE / not completed;
- each of:
  - `IMMEDIATE_NO_PRORATION`;
  - `IMMEDIATE_PRORATED`;
  - `IMMEDIATE_SKIP_FINAL_USAGE`;
  with `activeSubscription=null`
  -> COMPLETED, no `cancelSubscription`;
- each immediate mode with the original exact active subscription still present
  -> RETRYABLE verification, no repeated `cancelSubscription`.

Attempt 2 already proves several halves of these branches; consolidate them into an explicit parameterized confirmation matrix rather than relying on inference from production source.

#### 3. Prove due RETRYABLE selection rather than only query shape

The batch/order test correctly checks:

```text
take: 25
createdAt ASC
id ASC
```

but it only checks that a RETRYABLE branch exists in the query.

Add exact assertions proving the selection condition contains:

```text
nextAttemptAt = null
OR
nextAttemptAt <= now
```

and a stateful behavior test showing:

- due RETRYABLE is processed;
- future RETRYABLE is not processed;
- PROVIDER_ACCEPTED remains eligible for verification.

#### 4. Strengthen retry-identity preservation

The current retry test proves the same cancellation mode is sent, but the prior review also required the approved identity snapshots to remain authoritative.

Add a regression where an unrelated/newer local projection would differ, while the approved request retains:

```text
providerSubscriptionIdSnapshot = original
planHandleSnapshot = original
mode = approved mode
```

Prove the worker verifies against the request snapshots and does not substitute a newer local identity.

If the service intentionally has no local Subscription read at all, assert that contract explicitly through the database fake and provider inputs.

#### 5. Prove completion-message logical idempotency

The existing `"emits one completion message when completion is replayed"` test gets one message because the simple fake allows only one claim. That is useful concurrency coverage, but it does not directly prove the deterministic message identity.

Add assertions that first completion uses:

```text
systemCode = BILLING_CANCELLATION_COMPLETED
sourceKey = createMerchantBillingSystemSourceKey(
  shopId,
  BILLING_CANCELLATION_COMPLETED,
  request.id,
  ARCH007_BILLING_CONTRACT_SCHEMA_VERSION
)
```

and that replay/upsert of the same logical completion cannot create a second logical message.

This can be proved with a stateful message fake keyed by `sourceKey`.

Also retain:

- PROVIDER_ACCEPTED emits no completion message;
- RETRYABLE verification emits no completion message.

#### 6. Prove persisted error summaries are secret-safe

Provider tests correctly prove classification and that provider-thrown errors do not expose the access token.

Add service-level persistence assertions showing a retry/permanent provider failure stores:

```text
providerErrorCode
providerResponseSummary
```

without the Partner access token or credential material.

At minimum cover:

- one retryable provider failure;
- one permanent/provider-attention failure.

The persisted summary must remain bounded to the existing maximum.

#### 7. Preserve all accepted production behavior

Do NOT change the following unless a new regression exposes an actual defect:

- exact selected-status CAS;
- `providerErrorCode = null` on successful `PROVIDER_ACCEPTED`;
- Shared 0.9.0 mapping;
- Partner API 2026-07 mutation;
- identity verification;
- already-achieved cancellation behavior;
- retry/backoff;
- stale lease transitions;
- provider-accepted intermediate state;
- Serializable completion transaction;
- idempotent completion-message source key;
- billing worker integration;
- database schema/submodule pointer.

### Validation Reviewed

Agent-reported Attempt 2:

```text
focused provider/cancellation: 34 passed
npm run test:unit:              464 passed
npm run build:                  passed
npm run prisma:validate:        passed
git diff --check:               passed
```

The supplied archive does not contain `node_modules`, so npm validation was not independently rerun by the architect.

Architect source review confirmed the two production corrections and inspected the full focused test files.

### Published Git Verification

Implementation branch:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-001
Attempt 1: 52664cebe7dca8133ce41386cbe7f036af750bd6
Attempt 2: e7ad61ebafcf5ea572ad78394deadea5f75632a4
Attempt 2 parent: 52664cebe7dca8133ce41386cbe7f036af750bd6
ahead of main: 2
behind main: 0
```

Attempt 2 changes only:

- `src/services/subscription-cancellation.service.ts`;
- `tests/unit/providers/shopify-partner-billing.provider.test.ts`;
- `tests/unit/services/subscription-cancellation.service.test.ts`.

Parent workspace branch tip:

```text
3b4b446c464caa0b62f1dc51d060b9dad511562c
```

which follows review handoff:

```text
130890946675e207f0df73feb0069de72c936284
```

Worktree isolation and start-of-attempt synchronization evidence are present and conformant.

### Architecture Conformance
Production implementation accepted in principle; regression contract remains incomplete.

### Follow-up

Attempt 3 remains on the SAME `ARCH-009-BACKGROUND-001` task and canonical mirrored task branches/worktrees.

Attempt 3 scope:

1. TEST-ONLY unless a new regression exposes an actual production defect;
2. implement the six missing proof areas above;
3. prefer a small stateful Prisma-shaped fake for lifecycle/lease/message behavior;
4. do not churn provider/service production code merely to create a new commit;
5. rerun:
   - focused provider/cancellation tests;
   - `npm run test:unit`;
   - `npm run build`;
   - `npm run prisma:validate`;
   - `git diff --check`;
6. update the Completion Report with Attempt 3 files, test counts, validation, physical worktrees, start sync, implementation commit and final parent handoff;
7. preserve this Architect Review until the next architect decision;
8. return the same task to `review`;
9. STOP.

`ARCH-009-ADMIN-002` remains Pending until BACKGROUND-001, BACKGROUND-002 and ADMIN-001 are all architect-accepted Complete.
