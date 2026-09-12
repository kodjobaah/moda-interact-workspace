---
id: ARCH-010-ADMIN-001
architecture_id: ARCH-010
title: Move lifetime Free grant configuration from plan catalogue to platform billing
  controls
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 42
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-DATABASE-006
enables:
- ARCH-010-ADMIN-008
created: 2026-09-11
updated: 2026-09-12T08:38:03Z
---

# ARCH-010-ADMIN-001: Move lifetime Free grant configuration from plan catalogue to platform billing controls

## Objective

Align the internal Admin UI with the ARCH-010 rule that the lifetime Free recovery grant is a platform/shop-lifetime policy, not an attribute owned by a Shopify Free plan mapping.

Merchants never access `moda-interact-admin`.

## Inspect before editing

```text
src/app/(protected)/billing/controls/page.tsx
src/components/admin/billing-controls.tsx
src/app/actions/billing-controls.ts
src/lib/admin/billing-control-validation.ts
src/lib/admin/billing-controls.ts
src/components/admin/billing-plan-catalog.tsx
src/app/actions/billing-plan.ts
src/lib/admin/billing-plan-validation.ts
src/lib/admin/billing-plan-audit.ts
tests/security/admin-billing-controls.test.mjs
tests/security/admin-billing-plan.test.mjs
database/prisma/schema.prisma
package.json
```

## 1. Platform controls own the default

Add an internal control for:

```text
Lifetime Free recovery grant for newly activated merchants
```

bound to:

```text
PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
```

Validation:

- required integer;
- minimum 0;
- no silent string/NaN coercion;
- mutation remains protected by existing platform-admin authorization and audit requirements.

The UI must explain:

> This value is snapshotted only when a merchant receives its first verified subscription activation. Changing it does not reset or increase existing merchants' lifetime grants.

## 2. Plan catalogue must stop owning the grant

The current plan catalogue exposes `BillingPlan.freeLifetimeConversationAllowance` and requires it for Free plans.

Under ARCH-010:

- remove that field from create/edit authority in the plan-catalog form;
- Free plan mapping validation must no longer require it;
- Paid plan mapping validation must not introduce it;
- do not write a new value to that legacy field from Admin plan actions;
- existing stored legacy values may remain readable in audit/history code where necessary for backward compatibility, but they must not be presented as the current runtime lifetime-grant authority.

Do not drop the database column in this task.

## 3. Audit behaviour

Platform policy mutation must include the lifetime grant in before/after audit data through the existing `PLATFORM_POLICY_CHANGED` mechanism.

Do not create a second audit subsystem.

## Required regression coverage

At minimum prove:

1. platform control renders current lifetime default;
2. valid non-negative integer is accepted;
3. negative/blank/non-integer values are rejected;
4. mutation writes platform policy and audit state through existing protected action;
5. explanatory copy says changes affect future first grants only;
6. Free plan create/edit no longer requires a lifetime allowance field;
7. plan catalogue no longer presents that field as editable authority;
8. Paid plan validation remains correct;
9. legacy plan audit serialization remains readable if existing rows contain the old field;
10. no merchant route or authentication boundary is introduced.

Run the repository-declared focused tests, typecheck/lint/build as applicable.

## Non-goals

Do not:

- expose Admin to merchants;
- mutate existing shops' grants when policy changes;
- implement recovery admission;
- modify Shopify commercial plans;
- drop the legacy BillingPlan column;
- add promotional credits.

## Work Items

- Verified `ARCH-010-DATABASE-006` is complete and exposes the platform-policy field while retaining the legacy plan column.
- Added the lifetime Free recovery grant to platform billing controls with strict non-negative integer parsing, protected SUPER_ADMIN mutation, and existing `PLATFORM_POLICY_CHANGED` before/after audit data.
- Removed `BillingPlan.freeLifetimeConversationAllowance` from plan form authority, validation requirements, hidden toggle inputs, and create/edit writes; tenant reporting now uses the snapshotted counter grant.
- Preserved legacy plan allowance values only in audit snapshot serialization when historical rows provide the field.
- Added focused regression coverage for all ten required behaviors.

## Acceptance Criteria

1. Platform controls render the current `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` value.
2. Strict non-negative integer validation accepts valid values and rejects negative, blank, decimal, and `NaN` input.
3. The existing platform-admin authorization and `PLATFORM_POLICY_CHANGED` audit flow remain in force.
4. Explanatory copy states that the value applies only to future first verified activations and does not alter existing grants.
5. Free plan create/edit no longer requires or presents a lifetime allowance field.
6. Plan actions do not write a new value to the legacy `BillingPlan.freeLifetimeConversationAllowance` field.
7. Paid plan meter and included-allowance validation remains covered and passing.
8. Historical plan audit snapshots remain readable when they contain the legacy field.
9. Existing shop grants are read from the snapshotted entitlement counter and are not mutated by policy changes.
10. The route remains platform-admin protected and introduces no merchant route or authentication boundary.

## Stop conditions

Stop and return to `moda_architect` if:

- DATABASE-006 has not exposed the policy field in the repository Prisma client;
- removing plan-form authority would require changing a contract owned by another repository;
- the current Admin authorization/audit flow differs materially from the inspected implementation.

## Completion Report

### Status
Ready for Review.

### Files Changed
- `src/app/actions/billing-controls.ts`
- `src/app/actions/billing-plan.ts`
- `src/components/admin/billing-controls.tsx`
- `src/components/admin/billing-plan-catalog.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-control-validation.ts`
- `src/lib/admin/billing-controls.ts`
- `src/lib/admin/billing-plan-audit.ts`
- `src/lib/admin/billing-plan-validation.ts`
- `src/lib/admin/billing.ts`
- `src/lib/admin/types.ts`
- `tests/security/admin-billing-controls.test.mjs`
- `tests/security/admin-billing-plan.test.mjs`

### Work Completed
- Platform controls now own `lifetimeFreeRecoveryAllowance`, persist it through the existing audited policy action, and render the future-first-grant explanation.
- Validation uses whole-number syntax and safe-integer checks without string/`NaN` coercion; zero is valid.
- Plan catalogue forms, validation, toggle payloads, and create/edit actions no longer treat `freeLifetimeConversationAllowance` as current authority or write it.
- Tenant Admin billing views use `ShopEntitlementCounter.grantedQuantity` for the shop snapshot; no existing grant is changed by policy mutation.
- Legacy allowance fields remain readable in existing plan audit snapshots.
- No merchant-facing route or authentication boundary was added.
- Corrected the platform-policy upsert create path to send only valid Prisma policy columns; the mutation reason remains audit-only.
- Added regression coverage for first-create lifetime persistence, audit reason retention, and update version/lifetime persistence.
- Validated against accepted DATABASE-006 revision `7523f495bf31f3e0a0e69d0344468faeac64fea8`.

### Validation Results
- Accepted DATABASE-006 revision `7523f495bf31f3e0a0e69d0344468faeac64fea8` was initialized and checked out detached in the implementation worktree; its `PlatformBillingPolicy` contains `lifetimeFreeRecoveryAllowance Int @default(5)`. The detached submodule state was not staged or committed.
- `npm run prisma:generate` passed against that revision.
- `npm run prisma:validate` passed against that revision.
- `node --test tests/security/admin-billing-controls.test.mjs tests/security/admin-billing-plan.test.mjs` passed: 19 tests.
- `npm run lint` passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx` for missing `refresh` hook dependencies; no errors.
- `npm run build` passed; it reported existing BullMQ optional-dependency and critical-dependency warnings only.
- `git diff --check` passed.

### Git / VCS
- Physical worktree isolation:
  - canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  - parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-001`
  - parent branch: `task/ARCH-010-ADMIN-001`
  - implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-001`
  - implementation branch: `task/ARCH-010-ADMIN-001`
  - shared workspace checkout switched/mutated for task work: no
  - shared implementation checkout switched/mutated for task work: no
  - another task worktree reused: no
- Start-of-attempt synchronization:
  - parent remote task branch fast-forwarded: not-needed
  - parent `origin/main` incorporated: already-current
  - implementation remote task branch fast-forwarded: not-needed
  - implementation `origin/main` incorporated: already-current
- Parent synchronization merge: `6d0d601`.
- Parent attempt 2 claim commit: `a0ea441`, pushed to `origin/task/ARCH-010-ADMIN-001`.
- Implementation correction commit: `4dc8d87`, pushed to `origin/task/ARCH-010-ADMIN-001`.
- No parent submodule gitlink was staged or committed.

### Attempt 2 Correction Checklist

- Correction 1 implemented: policy create data explicitly enumerates valid Prisma columns; `reason` is retained only in `PLATFORM_POLICY_CHANGED` audit data; focused regression covers create, audit, lifetime persistence, and versioned update.
- Correction 2 implemented: accepted DATABASE-006 revision `7523f495bf31f3e0a0e69d0344468faeac64fea8` was initialized, verified, and used successfully for Prisma generation, schema validation, focused tests, lint, and build.
- Scope guard satisfied: no promotional-credit controls, merchant routes, commercial-plan changes, legacy-column removal, or existing-grant mutation were introduced.

### Architect Review

#### Review Status

Accepted

#### Attempt 1 — Changes Requested

The core ARCH-010-ADMIN-001 implementation is architecturally aligned:

- `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` is rendered in protected platform billing controls;
- strict whole-number validation accepts zero and rejects blank, negative, decimal and `NaN` input;
- the existing SUPER_ADMIN and `PLATFORM_POLICY_CHANGED` audit path is retained;
- explanatory copy correctly states that the value is snapshotted only for future first verified activations;
- Free plan create/edit/toggle surfaces no longer own or write `BillingPlan.freeLifetimeConversationAllowance`;
- Paid plan validation remains intact;
- legacy plan audit snapshots continue to serialize the old field when it exists;
- tenant/Admin allowance presentation now reads the durable `FREE_RECOVERY_LIFETIME` counter's `grantedQuantity`;
- no merchant route or authentication boundary was introduced;
- the recorded worktree-isolation and start-of-attempt synchronization evidence is complete.

Attempt 1 cannot be accepted because the platform-policy mutation has an untested create-path defect.

##### Correction 1 — keep audit reason out of Prisma `PlatformBillingPolicy` data

`parsePlatformBillingPolicyForm(...)` returns:

```text
globalPauseNewRecoveries
globalPauseAutomatedWhatsapp
absoluteOutboundHardLimit
defaultWarningPercent
lifetimeFreeRecoveryAllowance
reason
```

but `mutatePlatformBillingPolicyAction(...)` currently uses:

```ts
platformBillingPolicy.upsert({
  where: { id: "default" },
  create: { id: "default", ...values },
  ...
})
```

`reason` is audit metadata; it is not a column of `billing.PlatformBillingPolicy`.

The accepted DATABASE-006 schema contains:

```text
globalPauseNewRecoveries
globalPauseAutomatedWhatsapp
lifetimeFreeRecoveryAllowance
absoluteOutboundHardLimit
defaultWarningPercent
version
createdAt
updatedAt
```

and no `reason` field.

The database migration adds the policy field but does not guarantee that the `id="default"` row already exists; the seed creates it only in seeded environments. Therefore the `upsert` create branch is a legitimate runtime path and must work.

Correct the mutation so Prisma create/update data is constructed explicitly from platform-policy fields. `values.reason` must be used only for the `BillingAuditEvent.reason`.

Do not add a `reason` column to `PlatformBillingPolicy`.

Add focused regression coverage proving that:

1. the policy create path contains only valid policy columns;
2. `lifetimeFreeRecoveryAllowance` is persisted on first creation;
3. `reason` is retained in `PLATFORM_POLICY_CHANGED` audit data but is not sent as policy model data;
4. the existing update path still increments `version` and persists the new lifetime default.

##### Correction 2 — validate against the actual DATABASE-006 Prisma dependency

The Completion Report records that:

```text
npm run prisma:generate
npm run prisma:validate
npm run build
```

were not executed successfully because the tracked Admin `database` submodule was uninitialized in the task worktree.

This task directly depends on `ARCH-010-DATABASE-006` and directly references the field introduced by that dependency. Before acceptance, the implementation must be validated against the published/accepted DATABASE-006 schema rather than only against a stale generated client or source assumptions.

For Attempt 2:

1. reclaim the same task through `/moda-task`;
2. initialize/synchronize the tracked `database` submodule in the canonical implementation worktree using the normal repository/submodule workflow;
3. verify the checked-out database revision contains `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`;
4. run the repository-declared:
   - `npm run prisma:generate`
   - `npm run prisma:validate`
   - focused security tests
   - `npm run lint`
   - `npm run build`
   - `git diff --check`
5. do not stage or commit an incidental database gitlink change unless the task explicitly requires a dependency pointer update;
6. record the exact dependency revision and validation outcomes in the Completion Report.

Repository-wide pre-existing formatting/lint warnings outside changed files remain non-blocking if unchanged and correctly documented.

##### Scope guard

Attempt 2 remains ADMIN-001 only.

Do not:

- add promotional-credit controls;
- mutate existing shop grants;
- change merchant routes;
- drop `BillingPlan.freeLifetimeConversationAllowance`;
- change Shopify commercial plans;
- redesign platform billing policy.

The existing implementation should otherwise be preserved.

Reclaiming the task after this architect decision should produce:

```text
attempt: 2
```

**Architect decision: Changes Requested — Attempt 1.**

#### Attempt 2 — Accepted

Architect review verified that the two Attempt-1 corrections are satisfied:

- `mutatePlatformBillingPolicyAction(...)` no longer spreads the parsed form object into Prisma `PlatformBillingPolicy` create data;
- the create branch explicitly enumerates only valid policy columns:
  `globalPauseNewRecoveries`, `globalPauseAutomatedWhatsapp`,
  `absoluteOutboundHardLimit`, `defaultWarningPercent` and
  `lifetimeFreeRecoveryAllowance`;
- `reason` remains audit-only and is written through the existing
  `PLATFORM_POLICY_CHANGED` `BillingAuditEvent`;
- the update branch continues to persist `lifetimeFreeRecoveryAllowance` and
  increments `version`;
- focused regression coverage protects the Prisma-safe create shape, first-create
  lifetime value, audit reason separation and versioned update shape;
- the accepted DATABASE-006 dependency revision
  `7523f495bf31f3e0a0e69d0344468faeac64fea8` is present in the task worktree and
  its `PlatformBillingPolicy` model contains
  `lifetimeFreeRecoveryAllowance Int @default(5)`;
- the Completion Report records successful `prisma:generate`,
  `prisma:validate`, 19 focused security tests, lint, build and
  `git diff --check` against that accepted dependency revision;
- architect-side execution of the packaged
  `admin-billing-controls.test.mjs` passes all nine contained tests. The second
  focused test file cannot be independently executed from the review archive
  because the archive intentionally does not include installed npm dependencies;
  its successful execution is therefore accepted from the canonical worktree
  validation evidence rather than treated as a failure;
- relative to Attempt 1, the actual Admin correction is bounded to
  `src/app/actions/billing-controls.ts` and
  `tests/security/admin-billing-controls.test.mjs`; the apparent database-subtree
  additions in the review archive are the previously uninitialized DATABASE-006
  submodule materialized for required validation, not a new database
  implementation owned by this task;
- the generated ignored `next-env.d.ts` in the review archive is not part of the
  declared implementation change;
- the canonical worktree/isolation evidence, start-of-attempt synchronization
  evidence, implementation commit `4dc8d87`, parent report commit `a0ea441`, and
  non-staged database gitlink state are recorded in the Completion Report;
- all previously reviewed ADMIN-001 architecture remains conformant: platform
  controls own the lifetime Free default, Free/Paid plan-catalogue actions no
  longer make the legacy plan allowance authoritative, existing shop grants are
  read from the durable lifetime counter, legacy audit serialization remains
  readable, and no merchant/Admin authentication boundary was introduced.

**Architect decision: Accepted — Attempt 2.**

Because `completion_mode: automatic`, `ARCH-010-ADMIN-001` is now `complete`.
`attempt: 2` is preserved and there is no active executor/claim.

Dependency reconciliation:

- `ARCH-010-ADMIN-008` remains `pending`; ADMIN-001 is now satisfied, but its other
  prerequisite `ARCH-010-DATABASE-012` is still `ready`, not `complete`;
- no other task becomes Ready solely from this acceptance.
