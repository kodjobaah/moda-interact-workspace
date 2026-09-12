---
id: ARCH-010-ADMIN-001
architecture_id: ARCH-010
title: Move lifetime Free grant configuration from plan catalogue to platform billing controls
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 42
executor: copilot
claimed_at: 2026-09-12T00:00:00Z
attempt: 1
depends_on:
  - ARCH-010-DATABASE-006
enables: []
created: 2026-09-11
updated: 2026-09-12T01:15:00Z
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

### Validation Results
- `npm ci` passed in the isolated implementation worktree.
- `node --test tests/security/admin-billing-controls.test.mjs tests/security/admin-billing-plan.test.mjs` passed: 18 tests.
- `npm run lint` passed with two pre-existing warnings in `src/components/admin/queue-monitor.tsx` for missing `refresh` hook dependencies; no errors.
- Editor diagnostics for all changed TypeScript files: no errors.
- `git diff --check` passed.
- `npm run prisma:generate` blocked: `database/prisma/schema.prisma` is absent because the tracked Admin database submodule is uninitialized in the task worktree.
- `npm run prisma:validate` blocked by the same missing schema path.
- `npm run build` blocked in its Prisma generation step by the same missing schema path.
- Repository-wide `npm run format:check` reports 78 pre-existing files outside this task; changed files were formatted explicitly with Prettier.

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
- Parent claim commit: `57fc3f4`, pushed to `origin/task/ARCH-010-ADMIN-001`.
- Implementation commit: `cd8a84b`, pushed to `origin/task/ARCH-010-ADMIN-001`.
- No parent submodule gitlink was staged or committed.

### Architect Review
Pending.
