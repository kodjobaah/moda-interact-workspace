---
id: ARCH-010-ADMIN-009
architecture_id: ARCH-010
title: Hard-enforce upgrade economics on plan and recovery-pack configuration
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 89
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-ADMIN-007
- ARCH-010-ADMIN-008
enables:
- ARCH-010-SYSTEM-TEST-005
created: 2026-09-12
updated: '2026-09-12'
---

# ARCH-010-ADMIN-009: Hard-enforce upgrade economics on plan and recovery-pack configuration

## Objective

Integrate the accepted ADMIN-007 evaluator into Admin plan/pack mutations so unsafe or unverifiable economics cannot be activated by UI or crafted server action.

**PASS is required. FAIL and UNVERIFIED both block economics-affecting activation/mutation.**

This is a commercial Admin safety gate only. It does not change runtime merchant admission or Shopify charging.

## Inspect before editing

```text
src/app/actions/billing-plan.ts
src/lib/admin/billing-plan-validation.ts
src/lib/admin/billing-plan-audit.ts
src/components/admin/billing-plan-catalog.tsx
src/components/admin/billing-recovery-packs.tsx
src/components/admin/billing-drawers.tsx
tests/security/admin-billing-plan.test.mjs
tests/security/admin-billing-controls.test.mjs
src/lib/admin/upgrade-economics-guardrail.ts
database/prisma/schema.prisma
```

## Binding evaluator

Use ADMIN-007 exactly. Do not reimplement guardrail arithmetic inside actions/components.

For the current single-pack model call:

```text
validateSinglePackShopifyEconomics(...)
```

Build inputs from:

- exact lower/higher `BillingPlan` rows referenced by `BillingUpgradeEconomicsEdge`;
- lower/higher **latest verified economics snapshots**;
- `PlatformBillingPolicy.minimumUpgradePremiumBps`;
- current/proposed local `includedRecoveryConversationAllowance` and `recoveryCreditsPerPack` values.

### Monthly-capacity mapping

Production input MUST be:

```text
FREE plan monthlyIncludedConversations = 0
PAID_METERED = includedRecoveryConversationAllowance
```

Never add lifetime-Free, promotional or purchased credits.

## Mutations that require re-evaluation

Before commit, calculate affected edges for any mutation that can alter structural economics.

At minimum:

```text
create/activate plan mapping
change kind where allowed
change includedRecoveryConversationAllowance
enable/disable recoveryCreditPackEnabled
change recoveryCreditsPerPack
change shopifyRecoveryCreditPackEventHandle
change active state when it enters/leaves an economics edge
```

Evaluate both adjacent edges when relevant:

```text
previous -> current
current  -> next
```

Do not invent an edge when none exists.

Changing the **snapshot/policy itself** does not silently rewrite BillingPlan. Admin UI should show newly failing edges and require the plan/pack config to be corrected before the next guarded activation/change.

## Server-side hard gate

The mutation transaction/action must:

1. authorize SUPER_ADMIN according to existing rules;
2. parse proposed values;
3. re-read plans, policy, edges and latest snapshots server-side;
4. construct proposed economics state (do not evaluate stale pre-edit values);
5. run ADMIN-007 evaluator for every affected edge;
6. if any result is `FAIL` or `UNVERIFIED`, throw a bounded merchant-safe/Admin-safe error **before plan mutation**;
7. only if all applicable edges PASS, commit the plan/feature mutation;
8. write `BillingAuditEvent(UPGRADE_ECONOMICS_EVALUATED)` with calculation evidence and snapshot IDs in the same logical operation/audit flow.

Client-side disabled buttons are supplemental only.

## Result presentation

Render a deterministic explanation panel per edge:

```text
Starter -> Growth
Capacity gap: 300
Required pack units: 6
Stay + top-ups: £95.00
Upgrade: £75.00
Premium: 26.7%
Required: 20.0%
PASS
```

FAIL must clearly say activation/change is blocked.

UNVERIFIED must name the missing/incompatible evidence, for example:

```text
Top-up Shopify pricing evidence is missing.
Recurring currencies do not match.
No valid usage-price tiers were recorded.
```

Never convert UNVERIFIED to PASS.

## Required tests — all scenarios

Implement integration/UI scenarios **43–69** in:

```text
docs/contracts/ARCH-010-upgrade-economics-guardrail-test-matrix.md
```

These are mandatory, not examples.

Additionally include direct regression tests proving the supplied examples still produce their expected PASS/PASS/FAIL results through the shared evaluator.

### Atomicity tests

For FAIL and UNVERIFIED cases verify all of the following remain unchanged:

```text
BillingPlan
BillingPlanFeature rows
pack enablement/size/handle
```

No partial catalog write may precede the guardrail result.

### Audit tests

For successful guarded mutations prove audit evidence includes at minimum:

```text
lowerPlanId
higherPlanId
lowerSnapshotId
higherSnapshotId
minimumUpgradePremiumBps
lowerMonthlyIncluded
higherMonthlyIncluded
recoveryCreditsPerPack
packUnitsNeeded/topUp path
topUpCostMinor
stayAndTopUpCostMinor
upgradeCostMinor
requiredMinimumMinor
premiumBps
status
code
```

No Partner secrets/tokens/raw credentials.

## Non-goals

Do not:

- create/change Shopify prices;
- call App Events;
- add paid overage;
- include promos/lifetime Free/current merchant balances in economics;
- implement profitability/margin guardrail;
- make Admin merchant-facing.

## Stop conditions

Stop if ADMIN-007 reference semantics would need to be changed, if DATABASE-013 economics evidence cannot be read atomically enough for a safe mutation, or if the existing BillingPlan action has changed materially such that a separate mutation path would bypass the guardrail.

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
