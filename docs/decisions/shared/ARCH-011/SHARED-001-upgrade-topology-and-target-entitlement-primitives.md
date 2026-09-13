---
id: ARCH-011-SHARED-001
architecture_id: ARCH-011
title: Implement canonical upgrade topology and target-entitlement primitives
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 11
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-SHARED-008
enables:
- ARCH-011-SHARED-002
created: 2026-09-13
updated: '2026-09-13'
---

# ARCH-011-SHARED-001: Implement canonical upgrade topology and target-entitlement primitives

## Objective

Implement the **entire pure deterministic ARCH-011 domain contract in one Shared task**:

1. canonical tier-topology validation;
2. plan-direction classification by transitive reachability;
3. whole-provider-period target-entitlement calculation; and
4. additional-grant calculation independent of merchant usage.

No database access and no provider calls are allowed in these primitives.

## Inspect before editing

```text
src/billing.ts
src/billing.test.ts
src/index.ts
package.json
scripts/validate-billing-entrypoint.mjs
```

Preserve all accepted ARCH-010 billing exports.

## A. Canonical topology input contract

Add strict types/schemas equivalent to:

```text
PlanTopologyNode
  id: non-empty bounded string
  shopifyPlanHandle: non-empty bounded string
  active: boolean

PlanTopologyEdge
  lowerPlanId: non-empty bounded string
  higherPlanId: non-empty bounded string
  active: boolean
```

The pure validator operates on the complete supplied plan+edge snapshot. It does not query Prisma.

## B. `validateCanonicalPlanTopology`

Return a deterministic result containing either the ordered active plan IDs/handles or a bounded error code/reason. Do not throw raw graph-library errors to callers.

The valid topology is exactly the DATABASE-001 invariant:

```text
0 active plans => empty order permitted
1 active plan  => zero active edges
>1 plans       => one acyclic connected linear chain across every active plan
```

Reject deterministically:

```text
SELF_EDGE
EDGE_REFERENCES_INACTIVE_OR_UNKNOWN_PLAN
EDGE_COUNT_MISMATCH
MULTIPLE_LOWEST_TIERS
MULTIPLE_HIGHEST_TIERS
BRANCHING
CYCLE
DISCONNECTED_PLAN
DUPLICATE_PLAN_OR_EDGE_IDENTITY
```

Use actual bounded code names consistently in tests.

## C. `classifyPlanDirection`

Add exactly four semantic outcomes:

```text
SAME
UPGRADE
DOWNGRADE
UNRESOLVED
```

Algorithm:

1. validate topology; invalid topology => `UNRESOLVED`;
2. source/target same plan ID => `SAME`;
3. if target appears later than source in canonical order => `UPGRADE`;
4. if target appears earlier => `DOWNGRADE`;
5. missing source/target => `UNRESOLVED`.

Adjacent edges define ordering only. Required examples:

```text
Free -> Starter -> Growth -> Scale

Free -> Scale       UPGRADE
Free -> Growth      UPGRADE
Starter -> Scale    UPGRADE
Scale -> Starter    DOWNGRADE
Growth -> Growth    SAME
```

Never classify from:

```text
price
plan name
allowance size
array/display order supplied by caller
lexicographic order
```

## D. Whole-period target-entitlement primitive

Add a pure function equivalent to:

```text
calculateTargetBillingPeriodEntitlement({
  providerCycleStart,
  providerCycleEnd,
  segments[]
}) -> non-negative integer
```

Each segment input contains exactly the calculation evidence required:

```text
effectiveFrom
effectiveTo
includedAllowanceSnapshot: non-negative integer
```

Validation is binding:

```text
cycleStart < cycleEnd
segments not empty
first.effectiveFrom == cycleStart
last.effectiveTo == cycleEnd
each effectiveFrom < effectiveTo
segments strictly chronological
previous.effectiveTo == next.effectiveFrom
no gap
no overlap
allowance is safe non-negative integer
```

Calculate using integer/BigInt intermediate arithmetic only:

```text
totalDurationMs = providerCycleEnd - providerCycleStart
weightedAllowanceTime = SUM(segmentAllowance * segmentDurationMs)
targetEntitlement = floor(weightedAllowanceTime / totalDurationMs)
```

Do not use IEEE floating-point ratios. Return a normal JavaScript integer only after proving the result is within safe integer range; otherwise fail explicitly.

## E. Additional-grant primitive

Add a pure function or same-call result equivalent to:

```text
additionalGrant = targetEntitlement - alreadyGranted
```

Inputs:

```text
targetEntitlement: non-negative integer
alreadyGranted: non-negative integer
```

Require:

```text
targetEntitlement >= alreadyGranted
```

If false, return/throw a bounded explicit inconsistency. **Do not clamp to zero and do not calculate a clawback.**

The following MUST NOT appear as calculation inputs:

```text
committedQuantity
reservedQuantity
forfeitedQuantity
remaining/available credits
purchased-credit balance
promotional-credit balance
lifetime-Free balance
Shopify monetary proration amount
```

## F. Usage-independence examples

Required deterministic test:

```text
Starter = 100
Growth  = 300
provider cycle exactly half Starter / half Growth

targetEntitlement = 200
alreadyGranted = 100
additionalGrant = 100
```

Run the same calculation conceptually for merchants who have committed 0, 20, 80 or 100 Starter credits. The Shared function receives none of those usage values and always returns the same `100` additional grant.

## G. Multiple-upgrade rounding

Test a whole-cycle sequence such as:

```text
Free 0
Starter 100
Growth 300
Scale 1000
```

with three same-cycle transition times. At each transition, build the complete candidate timeline through cycle end, calculate one whole-period target and subtract already-granted. Prove repeated target recomputation avoids drift that would be introduced by independently flooring each transition's percentage.

## Required tests

At minimum:

1. valid 0/1/4-plan topology;
2. direct skip classification;
3. downgrade/same classification;
4. every invalid topology category above;
5. price/name/allowance changes do not affect direction;
6. exact full-cycle one-plan target;
7. half-cycle Starter/Growth target = 200;
8. usage independence;
9. multiple-upgrade whole-period rounding;
10. gaps/overlaps/reversed timestamps rejected;
11. unsafe numeric range rejected;
12. `target < alreadyGranted` rejected, not clamped;
13. existing ARCH-010 Shared tests and billing entrypoint remain green.

## Validation

Run repository-declared equivalents of:

```text
npm test
npx tsc --noEmit --pretty false
npm run build
node scripts/validate-billing-entrypoint.mjs
npm pack --dry-run --json
git diff --check
```

Do **not** publish in this task.

## Non-goals

No Prisma/database import, no provider API, no UI, no package publication, no cash proration and no entitlement mutation.

## Stop conditions

STOP if implementing these primitives would require changing an accepted ARCH-010 export incompatibly rather than adding the ARCH-011 contract.

## Completion Report

### Status
Not started.

### Architect Review
Pending.
