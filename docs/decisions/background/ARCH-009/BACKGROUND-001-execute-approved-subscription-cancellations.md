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
attempt: 3
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
- `tests/unit/services/subscription-cancellation.service.test.ts`
### Work Completed
- Attempt 3 completed the six Architect Review proof areas with a stateful Prisma-shaped lifecycle fake covering stale lease recovery, provider verification, due/future RETRYABLE selection, confirmation outcomes, deterministic completion messaging, approved identity snapshots, and secret-safe persisted provider failures.
- Added explicit confirmation coverage for END_OF_CYCLE and all three immediate cancellation modes, including no-contract and still-active provider states.
- Added exact due selection assertions for `nextAttemptAt = null` or `nextAttemptAt <= now`, and replay assertions keyed by `createMerchantBillingSystemSourceKey`.
- A new secret-safety regression exposed that arbitrary provider error summaries were persisted verbatim; bounded credential-labelled values are now redacted before persistence. No other production behavior changed.
### Validation Results
- Focused provider/cancellation tests: passed, 2 files and 50 tests.
- `npm run test:unit`: passed, 44 files and 480 tests.
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
  commit: `3828b8fccf4260b6736318ff347c8390da97cea0`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/background/ARCH-009/BACKGROUND-001-execute-approved-subscription-cancellations.md`
  claim commit: `b9d8955`
  review handoff commit: `cec6e92ff597dc555c28e940846f5f3a8429644f`
  metadata finalization commit: `ae22676`
  final parent branch tip: `0e1d4074bf4e87385fd8ad57c97596f9ef4a50d4`
  remote branch: `origin/task/ARCH-009-BACKGROUND-001`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 3 successfully closes the complete lifecycle/regression contract from the prior review.

Verified:

- stale PROCESSING with `providerAcceptedAt != null` is exercised end-to-end through recovery -> PROVIDER_ACCEPTED verification -> completion without another cancellation mutation;
- stale PROCESSING without provider acceptance returns through the RETRYABLE path without inventing provider acceptance;
- END_OF_CYCLE confirmation is explicitly covered for achieved, not-yet-achieved and no-active-subscription states;
- all three immediate modes are explicitly covered for both `activeSubscription = null` completion and still-active verification/retry;
- due RETRYABLE, future RETRYABLE and PROVIDER_ACCEPTED eligibility are exercised behaviorally;
- approved request snapshots remain authoritative and there is no local Subscription projection substitution;
- the completion SYSTEM message uses the deterministic canonical billing source key and is logically idempotent;
- retryable and permanent provider failures are persisted with bounded summaries;
- exact-status claim CAS and stale provider-error cleanup from Attempt 2 remain intact.

The cancellation lifecycle implementation is otherwise accepted.

One security defect remains in the new Attempt-3 error-summary redaction helper.

#### 1. Fix `Authorization: Bearer <token>` redaction

Attempt 3 added:

```ts
.replace(
  /((?:access[_ -]?token|authorization|bearer)\s*[:=]?\s*)(\S+)/gi,
  "$1[REDACTED]",
)
```

This does not safely redact the common authorization-header shape:

```text
Authorization: Bearer secret-token
```

The `authorization` alternative consumes `Bearer` as the value being redacted, leaving the actual credential after it. The persisted result is effectively:

```text
Authorization: [REDACTED] secret-token
```

That violates the task's explicit `no secrets` requirement and the prior Architect Review's requirement that persisted `providerErrorCode` / `providerResponseSummary` cannot contain Partner access-token or credential material.

Attempt 4 must harden the sanitizer.

Minimum required behavior:

```text
Authorization: Bearer secret-token
Authorization=Bearer secret-token
Bearer secret-token
access_token=secret-token
access-token: secret-token
access token = secret-token
X-Shopify-Access-Token: secret-token
```

must all remove the credential value from the returned/persisted summary.

One acceptable implementation approach is to redact the full authorization-bearer form FIRST, then apply the existing access-token/bearer-value patterns. Preserve the existing 2,000-character bound.

#### 2. Add exact persistence regressions

Add focused service-level tests for at least:

```text
Authorization: Bearer partner-secret
X-Shopify-Access-Token: partner-secret
access_token=partner-secret
Bearer partner-secret
```

For both retry/permanent persistence paths where practical, prove:

```text
providerResponseSummary does not contain partner-secret
providerResponseSummary length <= 2000
providerErrorCode remains the expected bounded code
```

At minimum, `Authorization: Bearer ...` MUST be tested through the actual service persistence path because that is the shape the current sanitizer mishandles.

Also add a small table-driven sanitizer/persistence regression for the listed header/token variants so a future regex simplification cannot reopen the leak.

#### 3. Do not change the cancellation lifecycle

Attempt 4 is security-only.

Do NOT change:

- Partner API contract or cancellation mutation;
- Shared cancellation-mode mapping;
- claim CAS;
- retry/backoff policy;
- provider identity checks;
- stale lease state machine;
- confirmation rules;
- completion transaction/message behavior;
- worker integration;
- database schema/submodule pointer.

Only modify production cancellation code if required to fix the sanitizer and its direct tests.

#### 4. Completion Report metadata

Attempt 3 implementation branch is correctly published at:

```text
3828b8fccf4260b6736318ff347c8390da97cea0
```

and the actual final parent branch tip is:

```text
0e1d4074bf4e87385fd8ad57c97596f9ef4a50d4
```

The Attempt 3 Completion Report currently names `ae22676` as the metadata finalization commit but does not separately record `0e1d407...` as the final pushed branch tip.

Attempt 4 must record distinctly:

```text
review handoff commit
metadata/report commit(s)
final parent branch tip
```

so the report matches the published branch state exactly.

### Positive Findings To Preserve

Attempt 3 has now established the full cancellation behavior requested across the previous reviews:

- exact four Shared cancellation mode mappings;
- provider identity mismatch => no mutation;
- already-deferred END_OF_CYCLE => idempotent completion;
- immediate cancellation with no contract => idempotent completion;
- Partner acceptance != local completion;
- exact confirmation rules for END_OF_CYCLE and all three immediate modes;
- retry identity preservation;
- stateful stale-worker verification with no blind repeat;
- exact selected-status CAS / one claimant;
- deterministic exactly-once logical completion message;
- due/future retry selection;
- bounded provider error persistence;
- worktree isolation and synchronization evidence.

No further functional lifecycle changes are requested.

### Validation Reviewed

Agent-reported Attempt 3:

```text
focused provider/cancellation: 50 passed
npm run test:unit:              480 passed
npm run build:                  passed
npm run prisma:validate:        passed
git diff --check:               passed
```

The supplied archive does not contain `node_modules`, so npm validation was not independently rerun by the architect.

### Published Git Verification

Implementation:

```text
repository: moda-interact-background
branch: task/ARCH-009-BACKGROUND-001
tip: 3828b8fccf4260b6736318ff347c8390da97cea0
parent: e7ad61ebafcf5ea572ad78394deadea5f75632a4
```

Parent workspace:

```text
branch: task/ARCH-009-BACKGROUND-001
tip: 0e1d4074bf4e87385fd8ad57c97596f9ef4a50d4
parent: ae22676aa08aa2b0416b7ae06359fd63573b92aa
```

### Architecture Conformance

Changes required — security sanitizer only.

### Follow-up

Attempt 4 remains on the SAME `ARCH-009-BACKGROUND-001` task and canonical mirrored task branches/worktrees.

Attempt 4 scope:

1. fix bearer/access-token redaction so no credential value survives;
2. add the exact persistence/table-driven secret-safety regressions above;
3. do not modify unrelated cancellation lifecycle behavior;
4. rerun:
   - focused provider/cancellation tests;
   - `npm run test:unit`;
   - `npm run build`;
   - `npm run prisma:validate`;
   - `git diff --check`;
5. update the Completion Report with Attempt 4 files, validation, worktree/sync evidence, implementation commit, report/handoff commits and final parent branch tip;
6. preserve this Architect Review until the next architect decision;
7. return the same task to `review`;
8. STOP.

`ARCH-009-ADMIN-002` remains Pending until BACKGROUND-001, BACKGROUND-002 and ADMIN-001 are all architect-accepted Complete.
