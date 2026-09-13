---
id: ARCH-010-ADMIN-005
architecture_id: ARCH-010
title: Manage promotion catalogue, close campaigns and reopen by expiry only
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
executor: copilot
claimed_at: '2026-09-13T18:54:07Z'
priority: 85
attempt: 2
depends_on:
- ARCH-010-ADMIN-004
enables:
- ARCH-010-ADMIN-006
- ARCH-010-SYSTEM-TEST-003
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-ADMIN-005: Manage promotion catalogue, close campaigns and reopen by expiry only

## Objective

Give SUPER_ADMIN a durable catalogue of **all promotions ever created**, with clear running/expired/closed state, append-only lifecycle history, manual close and safe reopen of the **same campaign ID** by changing only its expiry (and status when necessary).

## Required catalogue

Show at minimum:

```text
campaign name
scope
target summary
credit quantity
startsAt
expiresAt
derived running/expired state
persisted status
createdAt/creator
last lifecycle change
```

Support bounded filtering for running, expired/closed, scope and target where current Admin patterns permit it. Do not delete historical campaigns.

## Close

SUPER_ADMIN may close a DRAFT/ACTIVE campaign using the DATABASE-010 state machine. Closing must append `PromotionCampaignEvent(CLOSED)` and make the campaign immediately unavailable for new merchant selection/new promotional reservations.

Closing does not delete existing merchant grant/history and does not claw back committed usage.

## Reopen / extend expiry

Reopen must preserve:

```text
same campaign id
same scope
same target
the same credit quantity
all existing merchant grant/history rows
```

The only campaign commercial field that may change during reopen is `expiresAt`, and the new value must be in the future and after `startsAt`.

For an expired ACTIVE campaign, reopen means advancing `expiresAt` and appending `REOPENED`/`EXPIRY_CHANGED` audit evidence according to the canonical event convention.

For a CLOSED campaign, reopen also restores `status=ACTIVE` and appends the lifecycle evidence.

Reopen MUST NOT:

- clone the campaign;
- grant credits;
- reset any merchant's campaign quantity;
- clear committed usage;
- change target/quantity;
- auto-select the campaign for merchants.

## Concurrency/idempotency

Use optimistic/version/transaction patterns already supported by DATABASE-010. Two conflicting close/reopen actions must not silently overwrite each other.

## Required tests

At minimum prove:

1. catalogue retains DRAFT/ACTIVE/CLOSED/expired campaigns;
2. derived running state uses status + time window;
3. only SUPER_ADMIN can close/reopen;
4. close is audited and immediately prevents running state;
5. reopen keeps same ID;
6. reopen accepts only future expiry;
7. reopen cannot change quantity/scope/target;
8. reopen creates no merchant grant/selection;
9. existing merchant campaign usage remains untouched;
10. concurrent stale mutation fails safely;
11. no delete action removes campaign history.

## Non-goals

Do not implement merchant catalogue/selection, Background consumption, campaign usage analytics, automated scheduling messages or Shopify billing actions.

## Stop conditions

Stop if ADMIN-004/DATABASE-010 state names differ materially; reconcile with `moda_architect` rather than inventing parallel lifecycle values.

## Completion Report

### Status
In Progress.

### Files Changed
- `src/app/(protected)/promotions/page.tsx`
- `src/app/actions/promotions.ts`
- `src/components/admin/promotion-campaign-form.tsx`
- `src/lib/admin/promotion-validation.ts`
- `src/lib/admin/promotions.ts`
- `tests/security/admin-promotions.test.mjs`
- `tests/unit/promotion-validation.test.ts`

### Work Completed
- Added a durable SUPER_ADMIN promotion catalogue projection retaining DRAFT, ACTIVE, CLOSED, and expired campaigns, with bounded state/scope/target filters, persisted status, derived state, scope/target summary, quantity, dates, creator, creation time, and latest lifecycle event.
- Added transactional close and reopen mutations using `PromotionCampaign.version` compare-and-set predicates. Close supports DRAFT/ACTIVE, writes CLOSED audit evidence, and immediately removes the campaign from the running state. Reopen preserves the same campaign ID and commercial terms, changes only expiry (and restores ACTIVE for CLOSED campaigns), and writes REOPENED plus EXPIRY_CHANGED evidence.
- Enforced future expiry and `expiresAt > startsAt` on reopen; lifecycle forms expose no quantity, scope, target, or start-time editing.
- Preserved existing grants, selections, usage, and committed history by keeping lifecycle mutations isolated from those models; no delete action was introduced.
- Added focused validation and static security coverage for role gating, catalogue retention/derived state, lifecycle audit/CAS behavior, commercial-term immutability, preservation boundaries, and absence of deletion.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `node --experimental-strip-types --test tests/unit/promotion-validation.test.ts`: passed, 5 tests.
- `node --test tests/security/admin-promotions.test.mjs`: passed, 12 tests.
- `npm test`: passed.
- `npm run lint`: passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx`.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed; existing BullMQ optional-dependency/critical-dependency warnings remain.
- `git diff --check`: passed.

### Git / VCS
Physical worktree isolation:
	canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
	parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-005`
	parent branch: `task/ARCH-010-ADMIN-005`
	implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-005`
	implementation branch: `task/ARCH-010-ADMIN-005`
	shared workspace checkout switched/mutated for task work: no
	shared implementation checkout switched/mutated for task work: no
	another task worktree reused: no

database submodule initialized: yes
database gitlink expected: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database submodule HEAD: `5443afdd8f0c816dc16e1f3e93f9906c5ca31d94`
database gitlink staged/changed: no

Parent claim commit: `d1b58fc`, pushed to `origin/task/ARCH-010-ADMIN-005` in `moda-interact-workspace`.
Implementation commit: `a8c13cf`, pushed to `origin/task/ARCH-010-ADMIN-005` in `moda-interact-admin`.
Parent report commit: pending publication.
The implementation worktree was clean after publication; main branches were not modified.

### Architect Review
Pending.

## Architect Review — Attempt 1

### Changes Requested

Attempt 1 is **not accepted**. Keep this same task and return it to `ready` for
Attempt 2. Do not create a replacement task and do not start `ARCH-010-ADMIN-006`
or `ARCH-010-SYSTEM-TEST-003`.

Implementation under review:

```text
a8c13cff417e15ca4227b78e8f32ec7f858559b5
```

The implementation commit is exactly one commit after its synchronized parent:

```text
0d72f6f5e926328faa9619adf2bd75a303672023
```

and changes only the declared ADMIN-005 implementation/test files.

Published parent history:

```text
Attempt-1 claim:
  d1b58fcf3d0278d7f9c54293697c00e9cdd51045

Attempt-1 report:
  57bcf2f91916e58f972d7ab851a5e2357d49cd64
```

Preserve that history. Attempt 2 is the next claim; increment `attempt` exactly
once when claimed.

### Attempt-1 work accepted in substance — preserve it

The following implementation is directionally correct and must not regress:

```text
- SUPER_ADMIN page and mutation authorization from ADMIN-004 remains intact;
- catalogue includes persisted status, dates, creator and latest lifecycle evidence;
- close uses id + current status + version compare-and-set;
- reopen uses id + current status + version compare-and-set;
- close appends CLOSED evidence;
- CLOSED reopen restores ACTIVE and appends REOPENED plus EXPIRY_CHANGED evidence;
- expired ACTIVE expiry changes append EXPIRY_CHANGED evidence;
- close/reopen do not clone campaigns;
- close/reopen action payloads expose no quantity/scope/target edits;
- lifecycle mutation code does not create merchant grants/selections/counters or
  Shopify events;
- no campaign delete action is introduced;
- DATABASE-010 gitlink remains unchanged.
```

Do not redesign DATABASE-010 or the accepted ADMIN-004 campaign-authoring flow.

### Correction 1 — ACTIVE before `startsAt` is not EXPIRED

Primary files:

```text
src/lib/admin/promotions.ts
src/app/(protected)/promotions/page.tsx
tests/unit/promotion-catalogue.test.ts   # new preferred file
```

DATABASE-010 explicitly defines:

```text
EXPIRED is derived from expiresAt
```

Attempt 1 currently derives:

```ts
return campaign.startsAt <= now && campaign.expiresAt > now
  ? "RUNNING"
  : "EXPIRED";
```

for every ACTIVE campaign.

That incorrectly labels:

```text
status = ACTIVE
now < startsAt < expiresAt
```

as `EXPIRED`.

Use a complete derived catalogue state:

```text
DRAFT
SCHEDULED
RUNNING
EXPIRED
CLOSED
```

with exact behavior:

```text
status DRAFT
  -> DRAFT

status CLOSED
  -> CLOSED

status ACTIVE && now < startsAt
  -> SCHEDULED

status ACTIVE && startsAt <= now < expiresAt
  -> RUNNING

status ACTIVE && now >= expiresAt
  -> EXPIRED
```

`SCHEDULED` is a derived Admin presentation state only. Do not add a Prisma enum or
database migration.

The task only requires filters for running and expired/closed, so adding a
`SCHEDULED` filter is optional. `ALL` must still include scheduled campaigns.

Extract the time-state derivation to a pure helper that can be imported by a Node
unit test without booting Next or Prisma. Preferred file:

```text
src/lib/admin/promotion-catalogue.ts
```

Equivalent pure-helper placement is allowed.

Required deterministic tests use a fixed `now` and prove all five states.

### Correction 2 — reopen only expired ACTIVE or CLOSED campaigns

Primary files:

```text
src/app/actions/promotions.ts
src/components/admin/promotion-campaign-form.tsx
src/lib/admin/promotion-validation.ts
tests/unit/promotion-campaign-lifecycle.test.ts
```

The task contract says:

```text
For an expired ACTIVE campaign, reopen means advancing expiresAt.
For a CLOSED campaign, reopen restores status=ACTIVE.
```

Attempt 1 currently allows any ACTIVE row to execute `reopen`, including:

```text
- ACTIVE and scheduled for the future;
- ACTIVE and currently RUNNING.
```

The current form also renders Reopen for every ACTIVE campaign.

Required server behavior:

```text
DRAFT
  -> reject reopen

ACTIVE + now < expiresAt
  -> reject reopen
  -> this includes SCHEDULED and RUNNING campaigns

ACTIVE + now >= expiresAt
  -> allow reopen with a new expiry in the future and after startsAt
  -> keep status ACTIVE
  -> increment version
  -> append EXPIRY_CHANGED
  -> same campaign id

CLOSED
  -> allow reopen with a new expiry in the future and after startsAt
  -> restore status ACTIVE
  -> increment version
  -> append REOPENED
  -> append EXPIRY_CHANGED
  -> same campaign id
```

Do not require `newExpiresAt > oldExpiresAt` for every CLOSED campaign; the canonical
task requirement is specifically that the new expiry is in the future and after
`startsAt`. For an expired ACTIVE campaign, that automatically advances the old
expired value.

Required UI behavior:

```text
ReopenPromotionCampaignForm renders only when:
  campaign.status === CLOSED
  OR campaign.state === EXPIRED
```

Do not render Reopen for `RUNNING`, `SCHEDULED` or `DRAFT`.

Server authorization/state validation is authoritative; the UI condition is not a
security boundary.

### Correction 3 — make target filtering match the target the administrator sees

Primary files:

```text
src/lib/admin/promotions.ts
src/app/(protected)/promotions/page.tsx
tests/unit/promotion-catalogue.test.ts
```

Attempt 1 labels the field:

```text
Target or name
```

but the database filter currently matches:

```text
campaign.name contains query
OR targetPlanId == query
OR targetShopId == query
```

The catalogue displays:

```text
targetPlan.name
targetShop.domain
```

Therefore entering the visible plan name or shop domain does not perform the
required target filter.

Use one normalized, server-bounded query (`trim`, maximum 255 characters) and match
at minimum:

```text
campaign.name contains query, case-insensitive
targetPlan.name contains query, case-insensitive
targetShop.domain contains query, case-insensitive
```

Keeping exact targetPlanId/targetShopId matches as additional alternatives is
allowed.

Do not expose internal target IDs in the UI merely to make filtering work.

Required tests must inspect the produced Prisma `where` object or another pure
query-projection seam and prove:

```text
- plan display-name target is searchable;
- shop domain target is searchable;
- campaign name remains searchable;
- target input is bounded server-side;
- scope filter remains exact and bounded.
```

### Correction 4 — make `lastLifecycleChange` deterministic for CLOSED reopen

Primary files:

```text
src/lib/admin/promotions.ts
tests/unit/promotion-catalogue.test.ts
```

A CLOSED reopen writes both:

```text
REOPENED
EXPIRY_CHANGED
```

inside one database transaction.

`PromotionCampaignEvent.createdAt` uses database `now()`. PostgreSQL transaction
time can therefore be equal for both rows.

Attempt 1 selects:

```ts
events: {
  orderBy: { createdAt: "desc" },
  take: 1
}
```

so the displayed "Last change" can be nondeterministic when the two events share the
same timestamp.

Do not change the database schema.

Make Admin projection deterministic. One acceptable approach is:

```text
- select the latest small event set;
- choose max(createdAt);
- on an equal timestamp use explicit lifecycle priority matching logical write
  order, with EXPIRY_CHANGED after REOPENED for a reopen+expiry operation.
```

Equivalent deterministic projection is allowed. Do not rely on random CUID lexical
order as chronology.

Required test:

```text
REOPENED and EXPIRY_CHANGED have identical createdAt
-> lastLifecycleChange is deterministically EXPIRY_CHANGED.
```

### Correction 5 — required lifecycle tests must be behavioral, not only source regex

Attempt 1's new lifecycle coverage in:

```text
tests/security/admin-promotions.test.mjs
```

is primarily source-text matching.

That is useful as a static security/non-goal guard, but it does not prove the task's
transactional lifecycle behavior or stale-write safety.

Add one narrow production lifecycle seam used by the real server action.

Preferred file:

```text
src/lib/admin/promotion-campaign-lifecycle.ts
```

Suggested ownership:

```ts
applyPromotionCampaignClose(...)
applyPromotionCampaignReopen(...)
```

or one discriminated lifecycle function.

The real `mutatePromotionCampaignAction(...)` must call this seam inside the existing
`prisma.$transaction(...)`.

The seam must operate on a passed transaction object and must own:

```text
- current campaign reread/state validation;
- id/status/version CAS;
- permitted update fields;
- lifecycle-event creation;
- stale count=0 failure.
```

Do not move authentication out of the server action. The server action still owns:

```text
requirePlatformAdminMutation()
SUPER_ADMIN check
audit admin id resolution
FormData command parsing
revalidatePath()
```

Use deterministic fake-transaction unit tests. No new testing framework/package is
required.

At minimum permanently prove task requirements 1-11:

```text
1. catalogue state projection retains DRAFT/ACTIVE-window/CLOSED/expired history,
   including SCHEDULED before start;

2. derived state uses persisted status + startsAt/expiresAt correctly;

3. SUPER_ADMIN mutation/page guard remains in static security coverage;

4. close DRAFT and ACTIVE:
   exact id/status/version CAS
   -> status CLOSED
   -> version increment
   -> CLOSED event only after successful CAS;

5. reopen:
   same campaign id is updated;
   no campaign create/clone;

6. reopen:
   expiry must be parseable, > startsAt and > now;
   running/scheduled ACTIVE is rejected;

7. reopen update payload contains no:
   quantity
   scope
   targetPlanId
   targetShopId
   startsAt
   name/merchant description mutation;

8. lifecycle seam performs no merchant grant or MerchantPromotionSelection creation;

9. lifecycle seam performs no mutation of grant committed/reserved/usage history;

10. stale close/reopen CAS where updateMany.count = 0:
    -> bounded "changed; reload and retry" error
    -> no lifecycle event is appended;

11. no production campaign delete/deleteMany action exists.
```

Static source checks may continue to prove 3 and 11. Requirements 4-10 must be
behavioral.

### Correction 6 — preserve audit convention exactly

Required event behavior:

```text
Close DRAFT/ACTIVE:
  CLOSED

Reopen expired ACTIVE:
  EXPIRY_CHANGED
  oldExpiresAt = persisted old expiry
  newExpiresAt = accepted new expiry

Reopen CLOSED:
  REOPENED
  EXPIRY_CHANGED
  EXPIRY_CHANGED.oldExpiresAt = persisted old expiry
  EXPIRY_CHANGED.newExpiresAt = accepted new expiry
```

All event writes must remain in the same transaction as the winning CAS so a failed
event insert rolls back the status/expiry change.

Do not introduce a persisted `EXPIRED` state.

### Correction 7 — workflow metadata/evidence

The Attempt-1 claim correctly recorded:

```text
executor: copilot
claimed_at: 2026-09-13T18:37:03Z
attempt: 1
```

The Attempt-1 report commit removed `executor` and `claimed_at` rather than leaving
execution history intact as required by the agent handoff protocol.

This architect review normalizes the task back to:

```yaml
status: ready
executor: null
claimed_at: null
attempt: 1
```

Do not rewrite Attempt-1 history.

Attempt 2 must include actual observed values for:

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-005
  parent branch: task/ARCH-010-ADMIN-005
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-005
  implementation branch: task/ARCH-010-ADMIN-005
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Database submodule:
  database submodule initialized: yes
  database gitlink expected: <full SHA>
  database submodule HEAD: <full SHA>
  database gitlink staged/changed: no

Task history:
  Attempt-1 claim d1b58fcf3d0278d7f9c54293697c00e9cdd51045
    ancestor of parent HEAD: yes
  Attempt-1 report 57bcf2f91916e58f972d7ab851a5e2357d49cd64
    ancestor of parent HEAD: yes

Handoff:
  parent worktree clean: yes
  implementation worktree clean: yes
```

Record observed values only.

### Attempt 2 allowed scope

Expected production files:

```text
src/app/(protected)/promotions/page.tsx
src/app/actions/promotions.ts
src/components/admin/promotion-campaign-form.tsx
src/lib/admin/promotion-validation.ts
src/lib/admin/promotions.ts
```

Allowed new pure/testable helpers:

```text
src/lib/admin/promotion-catalogue.ts
src/lib/admin/promotion-campaign-lifecycle.ts
```

Expected tests:

```text
tests/security/admin-promotions.test.mjs
tests/unit/promotion-validation.test.ts
tests/unit/promotion-catalogue.test.ts
tests/unit/promotion-campaign-lifecycle.test.ts
```

Do not modify:

```text
database/**
ADMIN-004 accepted task history
Shopify merchant promotion selection/runtime
Background promotional reservation/consumption
PromotionalCreditGrant schema/accounting
MerchantPromotionSelection schema
Shopify billing/App Events
other repositories
```

If a correction requires schema changes or another repository, STOP and return to
`moda_architect`.

### Required Attempt 2 validation

Run from the canonical Admin implementation worktree:

```bash
npm run prisma:validate
npm run prisma:generate

node --experimental-strip-types --test \
  tests/unit/promotion-validation.test.ts \
  tests/unit/promotion-catalogue.test.ts \
  tests/unit/promotion-campaign-lifecycle.test.ts

node --test tests/security/admin-promotions.test.mjs

npm test
npx tsc --noEmit --pretty false
npm run lint
npm run build
git diff --check
```

Acceptance requires:

```text
- SCHEDULED/RUNNING/EXPIRED derivation is correct;
- Reopen is restricted to expired ACTIVE or CLOSED;
- displayed plan-name/shop-domain target filtering works;
- last lifecycle change is deterministic on CLOSED reopen;
- lifecycle CAS/audit behavior is permanently tested through the production seam;
- stale close/reopen produces no audit event;
- no lifecycle path mutates merchant grants/selections/usage;
- full Admin validation remains green;
- only the documented existing lint/BullMQ warnings remain;
- database gitlink remains unchanged;
- git diff --check passes.
```

### Attempt 2 stop conditions

STOP and return to `moda_architect` if:

1. correct derived catalogue state requires a persisted schema enum;
2. safe close/reopen requires modifying DATABASE-010 constraints;
3. deterministic lifecycle evidence requires changing event schema;
4. merchant grant/selection code must change;
5. another repository must change.

When complete:

```text
- set this same task to review;
- publish implementation commit(s);
- update this task's Completion Report with exact commands/results/evidence;
- publish parent task branch;
- STOP for moda_architect review.
```

