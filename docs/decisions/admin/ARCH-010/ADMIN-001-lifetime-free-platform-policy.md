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
status: ready
priority: 42
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-010-DATABASE-006
enables: []
created: 2026-09-11
updated: 2026-09-11T17:44:41Z
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

## Stop conditions

Stop and return to `moda_architect` if:

- DATABASE-006 has not exposed the policy field in the repository Prisma client;
- removing plan-form authority would require changing a contract owned by another repository;
- the current Admin authorization/audit flow differs materially from the inspected implementation.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.
