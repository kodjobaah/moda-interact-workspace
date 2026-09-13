---
id: ARCH-011-ADMIN-001
architecture_id: ARCH-011
title: Add tier-topology configuration and same-cycle upgrade audit UI
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-001
- ARCH-011-SHARED-002
- ARCH-010-ADMIN-009
enables:
- ARCH-011-SYSTEM-TEST-001
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-ADMIN-001: Add tier-topology configuration and same-cycle upgrade audit UI

## Objective

Implement the **complete Admin-owned ARCH-011 feature in one task**:

1. manage/view tier topology and existing upgrade-economics configuration safely; and
2. provide read-only provider-cycle/plan-segment/transition/proration audit views.

Admin is **not** the topology authority. Shared is deterministic preflight; DATABASE-001 deferred constraint is final persistence authority.

## Inspect before editing

```text
src/app/actions/billing-plan.ts
src/app/actions/billing-economics.ts
src/lib/admin/billing-plan-validation.ts
src/lib/admin/billing-economics-validation.ts
src/lib/admin/upgrade-economics-guardrail.ts
src/lib/admin/billing-plan.ts
src/lib/admin/billing-economics.ts
src/lib/admin/billing.ts
src/lib/admin/billing-presentation.mjs
src/components/admin/billing-plan-catalog.tsx
src/components/admin/billing-drawers.tsx
src/components/admin/tenant-billing.tsx
src/app/(protected)/billing/page.tsx
tests/security/admin-billing-plan.test.mjs
tests/security/admin-billing-economics.test.mjs
tests/unit/upgrade-economics-guardrail.test.ts

published ARCH-011 Shared primitives
DATABASE-001 bounded topology constraint/error behaviour
ARCH-010-ADMIN-009 accepted economics guardrail
```

## A. Topology display semantics

Display the current validated active chain, for example:

```text
Free -> Starter -> Growth -> Scale
Topology: VALID
```

Copy must explicitly explain:

> The chain defines tier order. Merchants may upgrade directly to any higher tier; they are not restricted to adjacent tiers.

Do not render skip edges (`Free -> Scale`) as required configuration.

## B. Configuration authority and transaction flow

Use existing authenticated SUPER_ADMIN actions/authorization. Do not add unguarded parallel write routes.

For any mutation that changes final topology, including:

```text
activate/deactivate BillingPlan
create/delete/activate/deactivate BillingUpgradeEconomicsEdge
change lower/higher plan endpoints where current UI supports it
```

server-side flow must:

1. authorize with existing SUPER_ADMIN rule;
2. read complete proposed active plan+edge state;
3. run published Shared `validateCanonicalPlanTopology` for preflight/bounded error copy;
4. run applicable ARCH-010 economics guardrail; `FAIL` or `UNVERIFIED` still block;
5. perform all required plan/edge changes in **one database transaction**;
6. allow DATABASE-001 deferred constraint to validate final transaction state;
7. preserve existing BillingAuditEvent conventions;
8. catch/map the bounded DB topology violation if a concurrent/stale write makes final state invalid;
9. commit nothing if final topology/economics invalid.

Shared preflight is not final authority. Never duplicate a different Admin-only graph algorithm.

## C. Atomic chain replacement

Support final-state edits requiring several row operations in one transaction. Example:

```text
before: Growth -> Scale
after:  Growth -> Pro -> Scale
```

Do not make separate commits that leave a temporarily invalid persisted graph.

If current Admin action architecture cannot express atomic replacement, STOP and return exact limitation; do not disable/bypass the DB constraint.

## D. Direction preview

Use published Shared classification only. Required examples:

```text
Free -> Scale = UPGRADE
Starter -> Scale = UPGRADE
Scale -> Starter = DOWNGRADE
```

Do not infer direction from prices, plan names or allowance sizes.

## E. Economics remains a separate guardrail

```text
topology valid != economics valid
economics valid != topology valid
```

A mutation affecting both must pass both ARCH-011 topology validation and accepted ARCH-010 economics guardrail. Direct tier skipping does not weaken adjacent-edge economics validation.

## F. Upgrade audit hierarchy

For a selected shop/subscription provide read-only chronological audit:

```text
BillingPeriod
  periodStart / periodEnd
  opening plan snapshots
  status / close reason

BillingPlanSegments
  plan snapshots
  effectiveFrom / effectiveTo
  includedAllowanceSnapshot
  sourceTransitionId

SubscriptionPlanTransitions
  from/to plan snapshots
  REQUESTED / PROVIDER_CONFIRMED / APPLIED / SUPERSEDED / FAILED / NEEDS_ATTENTION
  applicationMode
  provider subscription/cycle/event/effective-time evidence
  targetEntitlementSnapshot
  alreadyGrantedSnapshot
  includedCreditDelta
  timestamps / failureCode
```

Do not recompute historical evidence from current `BillingPlan` rows.

## G. Explain same-cycle versus new-cycle

Render clearly:

```text
SAME_CYCLE_PRORATED
  plan became effective inside the same provider cycle;
  target entitlement and additional grant are shown.

NEW_PROVIDER_CYCLE_FULL_ALLOWANCE
  Shopify opened/advanced to a new provider cycle;
  ARCH-010 opening allowance applied; same-cycle target/delta is N/A.
```

Do not display null same-cycle fields as zero.

## H. Usage-independence audit

For same-cycle APPLIED transition show separately:

```text
targetEntitlementSnapshot
alreadyGrantedSnapshot
includedCreditDelta
```

Current committed/reserved usage may be shown elsewhere as operational state, but label it separately and never imply it was an input to proration.

## I. Multiple-upgrade history

One period may legitimately show:

```text
Free -> Starter -> Growth -> Scale
```

Do not collapse intermediate actual segments because the final plan is Scale. Direct Free -> Scale must show only Free and Scale actual segments.

## J. Evidence safety

For NEEDS_ATTENTION show bounded useful evidence:

```text
provider plan handle
provider cycle
provider lifecycle event ID/effective time when known
failureCode
transition snapshots
```

Never render provider tokens, cookies, credentials or unfiltered secret-bearing JSON.

## Required tests

Prove at minimum:

1. valid 4-plan chain displayed deterministically;
2. copy says direct higher-tier skipping is allowed;
3. direct Free -> Scale preview uses Shared => UPGRADE;
4. invalid proposal blocked in preflight;
5. crafted server action cannot bypass final DB constraint;
6. atomic multi-edge replacement succeeds for valid final chain;
7. no partial write for invalid final chain;
8. DB race/stale topology violation mapped safely;
9. price/name changes do not alter direction;
10. ARCH-010 economics FAIL and UNVERIFIED still block;
11. economics PASS + topology PASS permits authorized mutation;
12. audit events preserved;
13. one-period one-segment audit;
14. multiple same-cycle segments chronological;
15. direct skip contains no fabricated intermediate segment;
16. same-cycle APPLIED shows persisted target/granted/delta;
17. usage displayed separately from calculation evidence;
18. new-cycle transition displays N/A same-cycle fields;
19. SUPERSEDED/FAILED/NEEDS_ATTENTION render bounded statuses;
20. no provider secrets rendered.

## Validation

Run repository-declared equivalents of:

```text
<focused Admin billing/security/economics tests>
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run prisma:validate
npm run build
npm run format:check
git diff --check
```

## Non-goals

No merchant plan change, no provider reconciliation, no entitlement grant, no cash proration, no second topology authority.

## Stop conditions

STOP if:

- Admin cannot atomically express a valid final topology without bypassing DATABASE-001;
- accepted ADMIN-009 economics guardrail would have to be weakened;
- audit rendering would require recalculating missing historical evidence rather than reading persisted snapshots.

## Completion Report

### Status
Not started.

### Architect Review
Pending.
