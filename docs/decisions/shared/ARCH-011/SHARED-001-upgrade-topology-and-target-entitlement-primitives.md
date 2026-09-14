---
id: ARCH-011-SHARED-001
architecture_id: ARCH-011
title: Implement exact ARCH-011 topology and entitlement primitives
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
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-011-SHARED-001

## Authorized implementation surface
Edit only:

```text
src/billing.ts
src/billing.test.ts
```
Do not add another billing module or change existing ARCH-010 exports.

## Exact exports to add to `src/billing.ts`

```text
APP_PRICING_UPGRADE_INITIAL_RECONCILE_DELAY_MS = 60_000
APP_PRICING_UPGRADE_REQUEST_WINDOW_MS = 1_800_000
PlanTopologyNodeSchema
PlanTopologyEdgeSchema
validateCanonicalPlanTopology(nodes, edges)
classifyPlanDirection(chain, sourcePlanId, targetPlanId)
calculateTargetBillingPeriodEntitlement(input)
calculateAdditionalIncludedCreditGrant(targetEntitlement, alreadyGranted)
```

`PlanTopologyNodeSchema` fields exactly: `{id, shopifyPlanHandle, active}`; strings trim/min1/max128. `PlanTopologyEdgeSchema` exactly `{lowerPlanId,higherPlanId,active}` with same string bounds. Use strict Zod objects.

`validateCanonicalPlanTopology` returns discriminated union:

```text
{ok:true, orderedPlanIds:string[]}
{ok:false, code: TopologyErrorCode}
```

`TopologyErrorCode` exact literals:
`SELF_EDGE`, `EDGE_REFERENCES_INACTIVE_OR_UNKNOWN_PLAN`, `EDGE_COUNT_MISMATCH`, `MULTIPLE_LOWEST_TIERS`, `MULTIPLE_HIGHEST_TIERS`, `BRANCHING`, `CYCLE`, `DISCONNECTED_PLAN`, `DUPLICATE_PLAN_OR_EDGE_IDENTITY`.
Sort any otherwise unordered diagnostic traversal by plan ID before choosing a bounded error so input array order cannot affect result.

`classifyPlanDirection` exact return literals: `SAME|UPGRADE|DOWNGRADE|UNRESOLVED`; invalid topology or absent source/target => UNRESOLVED; do not inspect price/name/allowance.

`calculateTargetBillingPeriodEntitlement` input exact shape:

```text
{
 providerCycleStart: Date;
 providerCycleEnd: Date;
 segments: readonly {effectiveFrom:Date; effectiveTo:Date; includedAllowanceSnapshot:number}[];
}
```

Require full contiguous cycle coverage, chronological order, no gap/overlap, safe non-negative integer allowances. Use BigInt millisecond durations and `floor(weighted/totalDuration)`. Throw bounded `Error` messages prefixed `ARCH011_ENTITLEMENT_INVALID:` for invalid input/unsafe number result.

`calculateAdditionalIncludedCreditGrant`: both args safe non-negative integers; if target<alreadyGranted throw `ARCH011_ENTITLEMENT_INCONSISTENT:TARGET_BELOW_GRANTED`; else return subtraction. No clamp and no downgrade/clawback helper.

## Exact tests to append in `src/billing.test.ts`
Add named tests for: 0/1/4 plan topology, Free->Scale upgrade, Scale->Starter downgrade, SAME, each error code, input-order invariance, half-cycle 100/300=>200, additional 100, usage-not-input (compile/API assertion), repeated-upgrade complete-timeline rounding, gap/overlap/reversed rejection, unsafe integer rejection, target<granted rejection, constants 60s/30m.

## Validation
```text
npm test
npm run typecheck
npm run build
npm run validate:billing-entrypoint
npm pack --dry-run --json
git diff --check
```

## Stop conditions
STOP if any accepted ARCH-010 export must be renamed/removed or if the new API cannot live under `@modainteract/moda-interact-shared/billing`.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
