---
id: ARCH-010-DATABASE-006
architecture_id: ARCH-010
title: Move the one-time lifetime Free recovery grant to platform policy and snapshot it per shop
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-09-11T13:02:11Z
attempt: 3
depends_on:
  - ARCH-007-DATABASE-002
  - ARCH-007-DATABASE-003
enables:
  - ARCH-010-ADMIN-001
  - ARCH-010-BACKGROUND-001
  - ARCH-010-BACKGROUND-003
  - ARCH-010-BACKGROUND-011
  - ARCH-010-SHOPIFY-002
  - ARCH-010-SHOPIFY-003
  - ARCH-010-SHOPIFY-009
created: 2026-09-11
updated: 2026-09-11T13:02:11Z
---

# ARCH-010-DATABASE-006: Move the one-time lifetime Free recovery grant to platform policy and snapshot it per shop

## Objective

Make the existing five lifetime Free recoveries a **shop-lifetime introductory entitlement** that is granted once when a merchant first obtains any verified Moda subscription, whether Free or Paid.

The grant MUST NOT be owned by the current `BillingPlan` and MUST NOT reset on upgrade, downgrade, renewal, uninstall or reinstall.

## Inspect before editing

```text
prisma/schema.prisma
prisma/seed.mjs
prisma/migrations/**
scripts/validate-billing-policy-schema.mjs
scripts/validate-recovery-credit-pack-schema.mjs
package.json
```

Also inspect the accepted ARCH-007 migrations that introduced:

```text
BillingPlan.freeLifetimeConversationAllowance
PlatformBillingPolicy
ShopEntitlementCounter
BillingAllowanceAdjustment
```

Do not remove a legacy column without an explicit migration/compatibility reason.

## Required schema change

Add to `billing.PlatformBillingPolicy`:

```prisma
lifetimeFreeRecoveryAllowance Int @default(5)
```

Required invariant:

```text
lifetimeFreeRecoveryAllowance >= 0
```

Add a database CHECK constraint for the non-negative invariant.

The platform-policy value is a **template for a shop's first grant**. It is not a live balance and MUST NOT retroactively change existing shops when an administrator changes the default later.

## Existing BillingPlan field

`BillingPlan.freeLifetimeConversationAllowance` currently exists and is used by ARCH-007 code.

For this task:

- keep the column for backward compatibility;
- do not drop/rename it;
- document it as legacy/non-authoritative for ARCH-010 runtime entitlement;
- dependent ARCH-010 application/background tasks MUST stop reading it as the lifetime-grant authority.

A later cleanup architecture may remove it after all consumers are migrated.

## Shop-level snapshot semantics

The durable per-shop base grant is:

```text
ShopEntitlementCounter
  counter = FREE_RECOVERY_LIFETIME
  grantedQuantity = grant captured once at first verified activation
```

After creation:

- `grantedQuantity` is never reset because the Shopify plan changes;
- `grantedQuantity` is never replaced merely because `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` later changes;
- `committedQuantity` and `reservedQuantity` are lifetime usage state;
- signed `BillingAllowanceAdjustment` rows remain additive administrative adjustments and are separate from the base grant;
- `refundingQuantity` is not used to make lifetime Free credits refundable.

## Existing-shop migration/backfill

Existing merchants may already have completed onboarding while their `FREE_RECOVERY_LIFETIME` counter has `grantedQuantity = 0`, because the old runtime derived the allowance from `BillingPlan.freeLifetimeConversationAllowance`.

The migration MUST backfill only shops with:

```text
ShopSettings.onboardingCompleted = true
```

For each such shop:

1. if no `FREE_RECOVERY_LIFETIME` counter exists, insert one with:

```text
grantedQuantity   = 5
committedQuantity = 0
reservedQuantity  = 0
refundingQuantity = 0
version            = 0
```

2. if the counter exists and `grantedQuantity = 0`, set `grantedQuantity = 5` and increment `version` exactly once;
3. if `grantedQuantity > 0`, preserve it exactly;
4. preserve every existing `committedQuantity`, `reservedQuantity` and `refundingQuantity` exactly;
5. do not create a grant for a fresh shop whose onboarding is incomplete;
6. do not inspect current plan kind when deciding whether an already-onboarded shop receives the backfill.

The value `5` is the current agreed product grant for the migration cohort. Future first activations read the current platform-policy value instead.

The SQL migration must be deterministic and idempotent under normal migration replay protections. If inserting IDs directly in SQL, use a deterministic text identifier derived from shop id/counter rather than relying on unavailable Prisma `cuid()` generation.

## Seed/default state

Update seed/default platform policy so:

```text
lifetimeFreeRecoveryAllowance = 5
```

Do not use the Free `BillingPlan` seed row as the source for this platform-policy value.

## Required validation

Add/update deterministic schema tests proving:

1. `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance` exists;
2. it defaults to 5;
3. negative values are rejected by database integrity;
4. the legacy `BillingPlan.freeLifetimeConversationAllowance` column still exists for compatibility;
5. migration backfill targets onboarded Free merchants;
6. migration backfill targets onboarded Paid merchants;
7. incomplete onboarding is not granted;
8. missing counter receives one grant;
9. existing zero-grant counter receives one grant and preserves usage;
10. existing positive grant is not overwritten;
11. committed/reserved/refunding quantities are preserved;
12. migration does not create a period entitlement counter.

Run the repository-declared Prisma/schema validations from `package.json`; do not invent unavailable scripts.

## Non-goals

Do not:

- change runtime recovery routing;
- change merchant UI;
- change Shopify plan configuration;
- remove the legacy BillingPlan field;
- add promotional-credit semantics;
- make lifetime Free credits refundable;
- reset an existing merchant's lifetime usage.

## Stop conditions

Stop and return to `moda_architect` if:

- the current schema no longer contains the expected counter/platform-policy models;
- a safe existing-shop backfill cannot distinguish completed onboarding;
- existing data contains a conflicting representation that would require destructive entitlement rewriting;
- implementation would require changing another repository.

## Completion Report

### Status
In Progress — Attempt 3 correction

### Files Changed
- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/seed.mjs`
- `moda-interact-database/prisma/migrations/20260911121000_move_lifetime_free_grant_to_platform_policy/migration.sql`
- `moda-interact-database/scripts/validate-billing-policy-schema.mjs`
- `moda-interact-database/package.json`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`

### Work Completed
- Added `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance Int @default(5)` and retained the legacy `BillingPlan.freeLifetimeConversationAllowance` field as non-authoritative.
- Added a database non-negative CHECK constraint for the platform allowance.
- Added an idempotent migration-cohort backfill for onboarding-completed shops, independent of plan kind, preserving positive grants and all usage quantities while excluding incomplete onboarding and period counters.
- Added the platform policy seed/default and deterministic billing-policy schema assertions.
- Regenerated the tracked ERD artifacts.

### Validation Results
- `npm ci` completed successfully.
- `npm run format` passed.
- `npm run prisma:generate` passed.
- `npm run validate` passed.
- `npm run test:billing-policy` passed.
- `npm run test:recovery-credit-packs` passed.
- `npm run test:billing-lifecycle` passed.
- `npm run erd` passed.
- `git diff --check` passed.

### Attempt 2 Completion Report

#### Physical worktree isolation

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-006
  parent branch: task/ARCH-010-DATABASE-006
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-006
  implementation branch: task/ARCH-010-DATABASE-006
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current
```

#### Attempt 2 corrections

- Confirmed `ARCH-007-DATABASE-002` and `ARCH-007-DATABASE-003` are complete before claiming the attempt.
- Strengthened `scripts/validate-billing-policy-schema.mjs` to reject plan-kind restrictions, require explicit `grantedQuantity = 5` for the existing zero-grant update, require its `grantedQuantity = 0` predicate, and reject writes to committed, reserved, or refunding usage quantities.
- Preserved the reviewed schema and migration without churn; `docs/generated/erd.png` was refreshed by the required ERD validation command.

#### Attempt 2 validation

- `npm run format` passed.
- `npm run prisma:generate` passed.
- `npm run validate` passed.
- `npm run test:billing-policy` passed.
- `npm run test:recovery-credit-packs` passed.
- `npm run test:billing-lifecycle` passed.
- `npm run erd` passed.
- `git diff --check` passed.

### Git / VCS
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-DATABASE-006`
- Implementation branch: `task/ARCH-010-DATABASE-006`
- Published commits: `a8ca715`, `6a0a711`
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-DATABASE-006`
- Parent branch: `task/ARCH-010-DATABASE-006`

### Architect Review

#### Review Status

Changes Requested

#### Attempt 1 — Changes Requested

The ARCH-010-DATABASE-006 schema and migration implementation is architecturally sound, but acceptance is blocked by workflow-evidence and focused-validation gaps.

Implementation findings verified by architect review:

- `billing.PlatformBillingPolicy.lifetimeFreeRecoveryAllowance Int @default(5)` is present.
- The migration adds the non-negative database CHECK constraint.
- `BillingPlan.freeLifetimeConversationAllowance` remains present and is documented as legacy/non-authoritative for ARCH-010 runtime entitlement.
- The migration backfill is gated by `ShopSettings.onboardingCompleted = true`, does not inspect plan kind, inserts a missing `FREE_RECOVERY_LIFETIME` counter with grant 5 and zero usage, upgrades only existing zero-grant counters to 5, increments `version` once, preserves positive grants, and leaves committed/reserved/refunding quantities untouched.
- The insert uses deterministic shop-derived text identity and `ON CONFLICT (shopId, counter) DO NOTHING`.
- The platform-policy seed/default is 5 and is not sourced from the Free BillingPlan row.
- The generated ERD exposes the new platform-policy field.
- No schema/migration change is requested by this review.

The following corrections are required before acceptance.

##### 1. Restore mandatory task-worktree evidence

The Completion Report must contain the full evidence block required by `docs/agent-worktree-isolation-policy.md`, including:

```text
Physical worktree isolation:
  canonical workspace root: <launcher-resolved path>
  parent worktree: <launcher-resolved path>
  parent branch: task/ARCH-010-DATABASE-006
  implementation worktree: <launcher-resolved path>
  implementation branch: task/ARCH-010-DATABASE-006
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Attempt 2 must begin by synchronizing both canonical task worktrees according to that policy and recording the actual outcomes.

##### 2. Strengthen deterministic validation to cover the task contract

`validate-billing-policy-schema.mjs` currently verifies important migration fragments, but it does not deterministically prove all required backfill semantics.

Add focused assertions proving at least:

1. the backfill is genuinely plan-kind independent, so an onboarded Free merchant and an onboarded Paid merchant are both in scope. The validator should fail if the migration later adds a BillingPlan/plan-kind restriction;
2. the existing-zero-grant UPDATE explicitly sets `grantedQuantity = 5`;
3. the existing-zero-grant UPDATE does not write/reset `committedQuantity`, `reservedQuantity`, or `refundingQuantity`;
4. the positive-grant preservation condition remains enforced by limiting the UPDATE to `grantedQuantity = 0`.

The existing static CHECK assertion for the non-negative platform value may remain; this review does not require a new live-database harness solely for that invariant.

##### 3. Rerun the task-required validation

After synchronizing the canonical implementation worktree and updating the focused validator, rerun the repository/task validation contract:

```text
npm run format
npm run prisma:generate
npm run validate
npm run test:billing-policy
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd
git diff --check
```

Record the results in the Attempt 2 Completion Report.

##### Scope guard

Do not change the ARCH-010-DATABASE-006 schema or migration merely to create churn. The reviewed migration semantics are already acceptable. Implementation changes for Attempt 2 should be limited to the focused validation correction plus any synchronization-generated artifact refresh that is genuinely required after incorporating current `origin/main`.

Return the same task to `review` after publishing the implementation and parent report branches.

#### Attempt 2 — Changes Requested (one remaining validator guard)

Attempt 2 successfully remediated the workflow evidence and three of the four requested focused-validation gaps.

Architect re-review verified:

- complete canonical parent/implementation worktree isolation evidence is now present;
- all four start-of-attempt synchronization outcomes are recorded;
- all task-required validation commands were rerun successfully;
- the reviewed schema and migration semantics remain unchanged;
- the focused validator now directly requires the zero-grant UPDATE to set `grantedQuantity = 5`;
- the focused validator requires the UPDATE predicate `counter."grantedQuantity" = 0`;
- the focused validator rejects writes to `committedQuantity`, `reservedQuantity`, and `refundingQuantity`.

One validation guard remains incomplete.

##### Required correction — make plan-independence protection cover `ShopSettings.plan`

The task requires the backfill to cover every onboarding-completed merchant regardless of current plan, including both Free and Paid merchants.

The current validator uses:

```js
assert.doesNotMatch(
  migration,
  /BillingPlan|billingPlan|planId|planKind|PAID_METERED/
);
```

That does not protect the actual plan-bearing field already present in the schema:

```prisma
ShopSettings.plan String?
```

For example, a later regression such as:

```sql
AND settings."plan" = 'starter'
```

would still pass the current validator while silently restricting the backfill to one plan cohort.

Strengthen the deterministic assertion so the migration cannot introduce any plan-based eligibility predicate through `ShopSettings.plan` (or an equivalent plan handle/kind restriction). A simple acceptable approach is to assert that the backfill SQL contains no reference to `settings."plan"` and no BillingPlan/plan-kind/plan-handle eligibility term.

Do not modify the reviewed schema or migration; this is a validator-only correction unless synchronization legitimately refreshes generated artifacts.

Also update the Attempt 3 Completion Report / Git-VCS evidence so it records the current implementation commit produced for the validator correction rather than leaving only the Attempt 1 implementation commits.

After synchronization, rerun:

```text
npm run format
npm run prisma:generate
npm run validate
npm run test:billing-policy
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd
git diff --check
```

Return the same task to `review`.

