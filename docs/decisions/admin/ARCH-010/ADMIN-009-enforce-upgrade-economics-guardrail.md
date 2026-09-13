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
status: ready
priority: 89
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-010-ADMIN-007
- ARCH-010-ADMIN-008
enables:
- ARCH-010-SYSTEM-TEST-005
created: 2026-09-12
updated: '2026-09-13'
---

# ARCH-010-ADMIN-009: Hard-enforce upgrade economics on plan and recovery-pack configuration


> **Readiness release — 2026-09-13:** `ARCH-010-ADMIN-008` is architect-accepted Complete at Attempt 2. `ARCH-010-ADMIN-007` was already Complete, so every dependency of this task is now Complete and this task is Ready.

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
Review.

### Files Changed
- `moda-interact-admin/src/app/actions/billing-plan.ts`
- `moda-interact-admin/src/app/actions/billing-economics.ts`
- `moda-interact-admin/src/components/admin/billing-plan-catalog.tsx`
- `moda-interact-admin/src/i18n/locales/en.json`
- `moda-interact-admin/src/i18n/required-keys.ts`
- `moda-interact-admin/src/lib/admin/billing-plan.ts`
- `moda-interact-admin/src/lib/admin/billing-plan-guardrail.ts`
- `moda-interact-admin/tests/security/admin-billing-plan.test.mjs`
- `moda-interact-admin/src/app/(protected)/billing/page.tsx`

### Work Completed
- Reused the accepted ADMIN-007 single-pack evaluator through a shared Admin adapter.
- Re-read current policy, active adjacent edges, latest verified snapshots, and proposed plan values inside the mutation transaction.
- Blocked `FAIL` and `UNVERIFIED` outcomes before plan, feature, pack, or edge activation writes.
- Preserved transaction atomicity and recorded `UPGRADE_ECONOMICS_EVALUATED` evidence with evaluator inputs, result, and snapshot IDs.
- Guarded edge creation/reactivation and economics-affecting plan updates/toggles.
- Added deterministic per-edge capacity, pack, cost, premium, status, and evidence explanations using Admin ICU keys.
- Added focused regression coverage for guard outcomes, audit evidence, mutation blocking, and server-side enforcement.

### Validation Results
- `npm test`: 163 passed, 0 failed, 3 skipped.
- `node --test tests/security/admin-billing-plan.test.mjs`: 11 passed, 0 failed.
- `npx tsc --noEmit --pretty false`: passed.
- `npm run lint`: 0 errors; two existing `queue-monitor.tsx` hook warnings.
- `npm run prisma:validate`: passed.
- `npm run build`: passed; existing BullMQ optional-dependency/critical-dependency warnings remain.
- Prettier check and `git diff --check`: passed.

### Git / VCS
- Implementation worktree: `moda-interact-workspace.worktrees/ARCH-010-ADMIN-009`.
- Branch: `task/ARCH-010-ADMIN-009`.
- Claim commit: `97bed1e`.
- Implementation commit: `19f649a` (`feat(admin): enforce upgrade economics guardrail`).
- Remote branch: `origin/task/ARCH-010-ADMIN-009`.

### Architect Review
Pending.

## Architect Review

### Attempt 1 — Changes Requested

Attempt 1 is **not accepted**. Keep this same task and return it to `ready` for
Attempt 2. Do not create a replacement task and do not begin
`ARCH-010-SYSTEM-TEST-005`.

The implementation at
`19f649a3dd903705485750878b211be3022334e7` is directionally useful and should be
preserved unless the corrections below prove a concrete defect requiring a bounded
change.

The parent publication history also needs forward reconciliation. The Attempt-1
claim commit is:

```text
97bed1e1d28d9c8dcc87bb1b57e61a87066b5d26
```

and the published report commit is:

```text
5a177551d12ba7ac6825430550f2bfd9d6bbeb77
```

Those commits are divergent siblings from the same merge base. Do not rewrite
history. Attempt 2 must start from a parent branch that contains both commits and
must preserve the corrected `ready / attempt: 1` frontmatter recorded by this
architect review.

#### Correction 1 — fail closed when local pack configuration no longer matches the verified snapshot

Primary file:

```text
moda-interact-admin/src/lib/admin/billing-plan-guardrail.ts
```

Related mutation/tests:

```text
moda-interact-admin/src/app/actions/billing-plan.ts
moda-interact-admin/tests/security/admin-billing-plan.test.mjs
```

The current adapter calculates `lowerPackEvidenceMismatch`, but it does not make the
result fail closed. It can evaluate a proposed local pack size/handle using the old
Shopify usage-pricing snapshot and return `PASS`.

That is not valid commercial evidence.

When the proposed lower-plan state has top-ups enabled, the verified lower snapshot
must match the proposed local pack mapping exactly:

```text
recoveryCreditPackEnabledSnapshot == true
recoveryCreditsPerPackSnapshot == proposed recoveryCreditsPerPack
shopifyRecoveryCreditPackEventHandleSnapshot == proposed shopifyRecoveryCreditPackEventHandle
```

If any required mapping differs, the mutation must be `UNVERIFIED` and blocked
before BillingPlan/BillingPlanFeature/edge writes. Do not price a new local pack
mapping using stale Shopify snapshot evidence.

Use the existing ADMIN-007 evaluator semantics. Do not change
`validateSinglePackShopifyEconomics(...)` arithmetic.

Required permanent tests:

1. same verified snapshot + same local enabled pack size/handle can evaluate normally;
2. changing only `recoveryCreditsPerPack` against the old snapshot is UNVERIFIED and the server mutation is blocked atomically;
3. changing only `shopifyRecoveryCreditPackEventHandle` against the old snapshot is UNVERIFIED and the server mutation is blocked atomically;
4. no BillingPlan, BillingPlanFeature, edge, or pack configuration write occurs before either blocked result.

#### Correction 2 — top-ups OFF must be PASS / NO_TOPUPS_AVAILABLE

Binding matrix scenario 52 requires:

```text
Toggling top-ups OFF allows mutation with NO_TOPUPS_AVAILABLE for that edge.
```

When the proposed lower-plan state sets:

```text
recoveryCreditPackEnabled = false
```

the adapter must call ADMIN-007 with top-ups disabled for the **proposed state**.
Historical snapshot enablement must not force `topUpsEnabled=true`.

Expected result:

```text
PASS
NO_TOPUPS_AVAILABLE
```

The plan mutation may then proceed, with audit evidence recorded atomically.

Required permanent server-action test:

```text
enabled current pack + verified enabled snapshot
-> crafted update proposes recoveryCreditPackEnabled=false
-> evaluator result PASS / NO_TOPUPS_AVAILABLE
-> mutation succeeds
-> audit evidence records that result
```

#### Correction 3 — prove required hard-gate scenarios behaviorally

The existing security additions contain useful source-presence checks, but source
strings are not sufficient evidence for ADMIN-009.

Add behavioral server-action tests for at least:

```text
48 pack enable/create re-evaluates lower->higher
49 pack-size change re-evaluates lower->higher
50 lower included allowance evaluates previous->lower and lower->higher
51 higher allowance evaluates lower->higher and higher->next
52 top-ups OFF PASS / NO_TOPUPS_AVAILABLE
53 top-ups ON without current compatible evidence blocks UNVERIFIED
54 PASS commits and writes complete audit evidence
55 FAIL leaves BillingPlan and BillingPlanFeature unchanged
56 UNVERIFIED leaves BillingPlan and BillingPlanFeature unchanged
57 crafted server action with FAIL is blocked
58 currency mismatch blocks
59 no next edge -> no invented plan/evaluation
60 top plan -> no invented higher plan
```

For FAIL/UNVERIFIED tests, assert the mutation transaction performs no catalog write
before rejection. Mocking only the evaluator result or searching source text is not
sufficient.

Keep SUPER_ADMIN authorization regressions and the accepted ADMIN-007 direct
evaluator example tests.

#### Correction 4 — complete the required UI explanation contract

Primary files:

```text
moda-interact-admin/src/components/admin/billing-plan-catalog.tsx
moda-interact-admin/src/i18n/locales/en.json
moda-interact-admin/src/i18n/required-keys.ts
moda-interact-admin/src/lib/admin/billing-plan.ts
```

The Admin plan page must permanently prove scenarios 59 and 65–69.

For each real edge, render:

```text
lower plan
higher plan
capacity gap
required pack units
top-up path / packSummary
stay + top-ups cost
upgrade cost
actual premium
required premium
PASS / FAIL / UNVERIFIED
```

Also:

- FAIL must clearly say the activation/change is blocked;
- UNVERIFIED must name the missing/incompatible commercial evidence;
- a plan with no configured next edge must display/document `NO_UPGRADE_EDGE` and must not invent/evaluate a next plan;
- currency formatting happens only after integer-minor arithmetic;
- the UI must explicitly label these values as **verified Shopify economics evidence used by the Admin guardrail** and must not imply the local snapshot is Shopify charging authority.

Add deterministic component/render tests, not only source-presence checks.

#### Correction 5 — audit evidence must remain exact and secret-free

Retain the current `UPGRADE_ECONOMICS_EVALUATED` audit path and prove successful
guarded mutations include:

```text
lowerPlanId
higherPlanId
lowerSnapshotId
higherSnapshotId
minimumUpgradePremiumBps
lowerMonthlyIncluded
higherMonthlyIncluded
recoveryCreditsPerPack
packUnitsNeeded
topUpPath
topUpCostMinor
stayAndTopUpCostMinor
upgradeCostMinor
requiredMinimumMinor
premiumBps
status
code
```

Prove the audit payload contains no Partner tokens, credentials, access secrets, or
raw provider responses.

#### Attempt 2 workflow and synchronization

Before implementation, use only the canonical isolated worktrees:

```text
canonical workspace root:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace

parent worktree:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-009

implementation worktree:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-009
```

Start Attempt 2 by fetching and synchronizing each task branch with its own remote,
then incorporate current `origin/main`.

Because the parent task history had a claim/report sibling divergence, first verify
that the parent branch contains both:

```text
97bed1e1d28d9c8dcc87bb1b57e61a87066b5d26
5a177551d12ba7ac6825430550f2bfd9d6bbeb77
```

If either is not an ancestor of the synchronized parent HEAD, STOP and return the
exact graph. Do not force-push or rewrite either historical commit.

Record this exact evidence in the Attempt 2 Completion Report:

```text
Physical worktree isolation:
  canonical workspace root: <absolute path>
  parent worktree: <absolute path>
  parent branch: task/ARCH-010-ADMIN-009
  implementation worktree: <absolute path>
  implementation branch: task/ARCH-010-ADMIN-009
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Parent history reconciliation:
  Attempt-1 claim 97bed1e... ancestor of parent HEAD: yes
  Attempt-1 report 5a17755... ancestor of parent HEAD: yes
```

#### Attempt 2 allowed scope

Production changes are limited to the ADMIN-009 guardrail integration and UI:

```text
src/lib/admin/billing-plan-guardrail.ts
src/app/actions/billing-plan.ts
src/app/actions/billing-economics.ts
src/lib/admin/billing-plan.ts
src/components/admin/billing-plan-catalog.tsx
src/app/(protected)/billing/page.tsx
src/i18n/locales/en.json
src/i18n/required-keys.ts
tests/security/admin-billing-plan.test.mjs
```

A narrowly-scoped new Admin unit/component test under `tests/**` is allowed when
needed to test evaluator-adapter or UI behavior without source-presence assertions.

Do not modify:

```text
src/lib/admin/upgrade-economics-guardrail.ts
database/**
Shared/Shopify/Background/Messaging/Gateway repositories
merchant runtime billing/admission
Shopify prices or App Events
```

If a required behavioral test proves the accepted ADMIN-007 evaluator itself must
change, STOP and return to `moda_architect`.

#### Required Attempt 2 validation

Run from the canonical Admin implementation worktree:

```bash
npm run prisma:validate

node --test tests/security/admin-billing-plan.test.mjs

npm test

npx tsc --noEmit --pretty false
npm run lint
npm run build

git diff --check
```

In addition, run any new focused adapter/component test file explicitly and record
its exact command/result.

Acceptance requires:

```text
- every changed/new focused test passes;
- scenarios 43–69 are behaviorally evidenced where ADMIN-009 owns them;
- top-ups OFF proves PASS / NO_TOPUPS_AVAILABLE;
- stale size/handle snapshot evidence proves UNVERIFIED and atomic rejection;
- UI proves top-up path, NO_UPGRADE_EDGE, and verified-evidence wording;
- typecheck/build/diff check pass;
- no new lint warnings beyond the two documented pre-existing queue-monitor hook warnings;
- no new build warnings beyond the documented BullMQ warnings.
```

When complete, set this same task to `review`, publish the implementation and parent
report branches, and STOP for architect review.
