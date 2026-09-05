---
id: ARCH-003-BACKGROUND-002
architecture_id: ARCH-003
title: Maintain shop-scoped active pending-recovery listing index
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
status: complete
priority: 20
executor: copilot
claimed_at: 2026-09-05T08:29:22Z
attempt: 1
depends_on:
  - ARCH-003-BACKGROUND-001
enables:
  - ARCH-003-SHOPIFY-002
created: 2026-09-05
updated: 2026-09-05
---

# Maintain shop-scoped active pending-recovery listing index

## Architecture

`docs/architecture/ARCH-003-admin-operational-ui.md`

## Objective

Provide an efficient shop-scoped Redis index that lets a merchant-facing
consumer list that shop's currently active `pending-recovery-candidates`
without scanning the shared BullMQ queue or the global Redis keyspace.

## Current behavior

Background already owns:

```text
queue:
  pending-recovery-candidates

job:
  evaluate-pending-recovery

candidate data:
  shopId
  shopDomain
  checkoutToken
  cartToken
  abandonedCheckoutUrl
  checkoutCreatedAt
```

It also owns transient O(1) correlation keys:

```text
pending-recovery:index:checkout:<shopId>:<checkoutToken>
pending-recovery:index:cart:<shopId>:<cartToken>
```

Those keys are removed when the candidate matures or is cancelled.

They are excellent for correlation but are not an efficient merchant listing
mechanism. Redis `SCAN MATCH pending-recovery:index:checkout:<shopId>:*` would
still scan the global Redis keyspace, so it must not become the dashboard query
strategy.

## Required shop index

Add a Background-owned sorted set:

```text
pending-recovery:index:shop:<shopId>
```

Member:

```text
<active BullMQ pending-candidate jobId>
```

Score:

```text
scheduledDueAt epoch milliseconds
```

The index is operational/transient Redis state, not durable business history.

## Lifecycle

### New candidate

When a candidate is enqueued:

```text
ZADD pending-recovery:index:shop:<shopId> <dueAtMs> <jobId>
```

The member must use the actual active BullMQ job ID, including the current
tenant-readable format:

```text
<shopId>--pending-recovery-...
```

### Refreshed candidate

When an existing delayed candidate is refreshed:

- preserve current duplicate/legacy compatibility;
- update the candidate data as today;
- update/change the BullMQ delay as today;
- update the shop ZSET member score to the newly scheduled due time;
- do not introduce a duplicate member for the same active job.

If the active job is a retained legacy-format job during rollout, index that
actual active job ID.

### New/legacy duplicate convergence

If both new and legacy jobs exist and the existing logic removes the redundant
legacy job, ensure the shop listing index contains only the surviving active
job ID.

### Cancellation

When a candidate is cancelled:

- remove the BullMQ job as today;
- remove checkout/cart indexes as today;
- `ZREM` the candidate job ID from the shop index.

### Maturity / processing

The candidate remains visible while it is genuinely pending, including the
brief transition through BullMQ `waiting` / `active`.

When the candidate reaches the existing maturity finalisation path, remove it
from the shop index in the same lifecycle cleanup that removes checkout/cart
indexes.

The shop index member must be removed regardless of materialisation outcome
(created, discarded or provider failure), matching the existing definition
that a candidate is no longer pending once it has matured.

### Empty index

When practical, delete an empty per-shop index after the final member is
removed. Do not require a global cleanup scan.

## Scheduling score

The ZSET score must represent the candidate's current scheduled due time.

For a newly delayed or re-delayed candidate:

```text
dueAtMs = scheduling time + recovery delay
```

For a candidate already eligible/processing, a score at or before the current
time is acceptable.

The score is for ordering/display only. BullMQ remains the execution scheduler.

## Consistency

The shop ZSET is a secondary operational index.

BullMQ remains the source of truth for whether a candidate job exists and its
current state.

The implementation must tolerate normal partial-failure/retry behavior:

- duplicate `ZADD` is idempotent;
- duplicate `ZREM` is harmless;
- the index must never be used to create recovery business state;
- no exactly-once assumption is introduced.

## Rollout

This is pre-production development.

No backfill of historical Redis jobs is required.

Only candidates newly scheduled or refreshed after deployment are required to
appear in the shop index.

Existing queue payload shape and job IDs do not change.

## Scope

### In scope

Likely Background areas include:

```text
src/domain/pending-recovery-candidate.ts
src/services/pending-recovery-candidate.service.ts
```

plus focused tests.

The agent may make the smallest local adjustments needed to pass the active
job ID into cleanup paths.

### Out of scope

- PostgreSQL schema changes;
- new durable candidate table;
- queue payload changes;
- recovery state-machine changes;
- WhatsApp behavior;
- merchant UI;
- queue mutation from the Shopify application;
- global Redis scans;
- backfilling old development queue data.

## Tests

Cover at minimum:

- [x] new candidate is added to the correct shop ZSET;
- [x] score represents current scheduled due time;
- [x] refresh updates the score without duplicate members;
- [x] different shops use different indexes;
- [x] cancellation removes the member;
- [x] maturity cleanup removes the member;
- [x] cleanup remains safe when the member/key is already absent;
- [x] legacy/new duplicate handling leaves only the active job ID indexed;
- [x] existing checkout/cart correlation indexes still behave unchanged;
- [x] existing recovery delay behavior remains unchanged.

## Validation

Run repository-declared validation, including focused tests, full tests,
build/typecheck and `git diff --check`.

Record existing unrelated baseline failures separately.

## Acceptance Criteria

- [x] `pending-recovery:index:shop:<shopId>` exists for shops with active candidates.
- [x] The index is a ZSET of active candidate job IDs.
- [x] Members are ordered by scheduled due time.
- [x] Listing cost is shop-scoped and does not require global SCAN or queue scan.
- [x] Refresh is idempotent and updates ordering.
- [x] Cancelled/matured candidates disappear from the index.
- [x] No database migration is introduced.
- [x] Queue payload and execution semantics remain unchanged.
- [x] tests pass subject only to documented baseline conditions.
- [x] build/typecheck passes subject only to documented baseline conditions.
- [x] `git diff --check` passes.

## Architect Correction — Amendment 001

The implementation is close but requires two corrections before acceptance.

### 1. Remove the `ZCARD` / `DEL` cleanup race

Current implementation:

```text
ZREM member
ZCARD shop-index
if 0:
  DEL shop-index
```

This is a time-of-check/time-of-use race.

Example:

```text
worker A: ZREM last old member
worker A: ZCARD -> 0

producer B: ZADD new candidate

worker A: DEL shop-index
```

The newly scheduled candidate is then lost from the shop listing index.

Redis automatically removes a sorted-set key when `ZREM` removes its final
member. Therefore shop-index cleanup must not use a separate `ZCARD` followed
by `DEL`.

Required behavior:

```text
ZREM pending-recovery:index:shop:<shopId> <jobId>
```

only.

Add focused regression coverage proving cleanup does not perform a destructive
post-`ZREM` delete.

### 2. Do not index retained failed/non-pending jobs

The refresh path currently calls `upsertIndexes(...)` for any existing BullMQ
job state.

Because failed jobs are retained (`removeOnFail: false`), a later duplicate
checkout-created event can find a retained failed job and re-add its ID to:

```text
pending-recovery:index:shop:<shopId>
```

That violates the contract that this index represents active pending
recoveries.

The shop listing index must contain only jobs whose current BullMQ state is:

```text
delayed
waiting
active
```

For an existing job in any other state, including:

```text
failed
completed
unknown
```

do not add/re-add it to the shop listing index. If a stale shop-index member
already exists for that job, remove it.

Do not change the existing checkout/cart correlation behavior in this
correction unless required to preserve current semantics.

Add focused coverage for at least:

```text
retained failed job + duplicate schedule
    -> not present in shop ZSET
```

and preserve:

```text
delayed -> indexed
waiting -> indexed
active  -> indexed
```

### Scope

This is a correction to the existing Attempt 1.

Do not reclaim the task, reset `attempt`, or create a new task.

After correction:

```text
status: review
executor: copilot
attempt: 1
Completion Report: Ready for Review
```

## Completion Report

### Status

Ready for Review.

### Files Changed

- `src/domain/pending-recovery-candidate.ts`
- `src/services/pending-recovery-candidate.service.ts`
- `src/workers/pending-recovery-candidate.worker.ts`
- `tests/unit/services/pending-recovery-candidate.service.test.ts`

### Work Completed

- Added the shop-scoped ZSET `pending-recovery:index:shop:<shopId>`.
- Indexed active BullMQ job IDs with scheduled due-time scores on enqueue and refresh.
- Kept refresh idempotent and removed stale legacy members during duplicate convergence.
- Removed members during cancellation and maturity with a single idempotent
  `ZREM`, avoiding a `ZCARD`/`DEL` cleanup race.
- Indexed only `delayed`, `waiting`, and `active` jobs; retained failed and
  other non-pending jobs are removed from the shop index while existing
  checkout/cart correlation behavior remains unchanged.
- Passed the actual BullMQ job ID through worker maturity cleanup.
- Added focused coverage for membership, scoring, refresh, isolation, cleanup,
  legacy handling, missing-member safety, state eligibility, and race-safe
  cleanup.

### Validation Results

- Focused service tests: 17 passed.
- `npm run build`: passed, including TypeScript compilation.
- `npm test`: 103 passed, 4 skipped, 2 unrelated failures: the documented
  `tests/unit/services/recovery-routing.service.test.ts` Prisma mock lacks
  `customerPhone.findMany`, and `tests/integration/commerce.agent.integration.test.ts`
  failed because the external Groq response contained malformed tool-call JSON.
- No lint script is defined in the Background repository.
- Changed-file diagnostics: no errors.
- `git diff --check`: passed.

### Deviations / Notes

- Matured cleanup accepts an optional job ID for compatibility with direct callers;
  the worker supplies the actual BullMQ ID.
- Existing historical Redis jobs are not backfilled.

### Unresolved Issues

None in the Amendment 001 implementation. The two full-suite failures are
unrelated to the changed files and are recorded above.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1, including Amendment 001, is architect-accepted Complete.

The reviewed implementation now maintains the Background-owned shop-scoped
active pending-recovery index:

```text
pending-recovery:index:shop:<shopId>
```

as a Redis sorted set whose members are active BullMQ pending-candidate job IDs
and whose scores represent scheduled due time.

### Amendment 001 verified

The two requested corrections are present.

#### Race-safe removal

Shop-index cleanup now performs only:

```text
ZREM <shop-index> <jobId>
```

There is no post-`ZREM` `ZCARD` / `DEL` sequence in the relevant source.

This avoids deleting a newly-created same-shop index member during concurrent
candidate cleanup.

#### Active-state eligibility

For an existing BullMQ job, shop-index membership is retained only when the
current state is:

```text
delayed
waiting
active
```

A retained failed or other non-pending job is removed from the shop index and
is not re-added.

The existing checkout/cart correlation behavior remains unchanged.

### Lifecycle reviewed

The implementation covers:

- new candidate ZSET membership;
- due-time scoring;
- delayed refresh / score update;
- waiting and active membership;
- retained failed-job exclusion;
- cancellation cleanup;
- maturity cleanup;
- same-shop and cross-shop isolation;
- legacy/new job-ID convergence;
- idempotent `ZADD` / `ZREM`;
- actual BullMQ `job.id` propagation from the worker into maturity cleanup.

No global Redis `SCAN` or BullMQ queue scan was introduced.

No queue payload, database schema, migration, recovery delay, retry, or
business-state semantics were changed by this task.

### Validation Reviewed

Implementing-agent evidence:

- focused service tests: 17 passed;
- build / TypeScript compilation: passed;
- changed-file diagnostics: no errors;
- `git diff --check`: passed;
- full suite: 103 passed, 4 skipped, 2 unrelated failures.

The two reported full-suite failures are outside this task:

1. the existing `recovery-routing.service.test.ts` Prisma mock does not define
   `customerPhone.findMany`;
2. `commerce.agent.integration.test.ts` depends on an external Groq response
   and received malformed tool-call JSON.

The Background repository has no lint script.

### Result

`ARCH-003-BACKGROUND-002` is Complete.

`ARCH-003-SHOPIFY-002` is promoted to Ready.

Live integrated verification of the ZSET-to-merchant-dashboard path remains
owned by `ARCH-003-SYSTEM-TEST-002`.
