---
id: ARCH-011-DATABASE-002
architecture_id: ARCH-011
title: Enforce canonical active plan topology at database commit
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-001
enables:
- ARCH-011-ADMIN-001
- ARCH-011-SHOPIFY-001
created: 2026-09-14
updated: 2026-09-14
---

# ARCH-011-DATABASE-002: Enforce canonical active plan topology at database commit

## Objective
Make PostgreSQL the final authority that active BillingPlans plus active BillingUpgradeEconomicsEdges form exactly one linear adjacent chain. No transition/segment schema changes in this task.

## Authorized implementation surface
```text
prisma/migrations/20260914020000_arch011_canonical_plan_topology/migration.sql
scripts/validate-arch011-plan-topology.mjs   # new
```
Do not edit `prisma/schema.prisma` unless Prisma requires relation/index metadata already authorised by DATABASE-001; no new business fields.

## Exact database mechanism
Create schema-qualified function exactly named:

```text
billing.validate_active_billing_plan_topology()
```

The function inspects final transaction state and raises SQLSTATE `P0001` with message prefix `MODA_BILLING_TOPOLOGY_INVALID:` when invalid.

Rules:

```text
N=0 active plans => zero active edges referencing an active plan
N=1 => zero active edges
N>1 => exactly N-1 active edges
active edge endpoints must both be active plans
no self edge
one and only one active plan has indegree 0
one and only one active plan has outdegree 0
all other active plans have indegree 1 and outdegree 1
recursive traversal from lowest visits exactly N distinct plans
no cycle, branch or disconnected active plan
```

Create DEFERRABLE INITIALLY DEFERRED CONSTRAINT TRIGGERs on:

```text
billing."BillingPlan" AFTER INSERT OR UPDATE OF "active" OR DELETE
billing."BillingUpgradeEconomicsEdge" AFTER INSERT OR UPDATE OF "active","lowerPlanId","higherPlanId" OR DELETE
```

Both call the same validator. Invoke the validator once at end of migration so invalid pre-existing state aborts migration.

## Required validator script
`validate-arch011-plan-topology.mjs` must fail unless the exact function name, error prefix, deferred constraint triggers and migration self-validation call are present.

## Acceptance Criteria
- [ ] Valid Free->Starter->Growth->Scale commits.
- [ ] Direct merchant skipping requires no additional edge.
- [ ] Branch, cycle, disconnected plan, self-edge, inactive endpoint and wrong edge count fail at transaction commit.
- [ ] Atomic replacement of multiple edges inside one transaction succeeds when final state is valid.
- [ ] No partial topology write commits when final state is invalid.

## Validation
```text
npm run prisma:validate
npm run prisma:generate
npm run test:first-production-baseline
node scripts/validate-arch011-plan-topology.mjs
git diff --check
```

## Out of scope
Admin UI/actions, Shared validator, transition schema, entitlement logic.

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
