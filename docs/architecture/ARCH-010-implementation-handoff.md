# ARCH-010 Implementation Handoff / Frontier

Date: 2026-09-11  
Architecture status: **Agreed / implementation-ready**

## Read before implementation

Use this order for merchant billing/lifecycle work:

1. [`../product/pricing-and-billing-model.md`](../product/pricing-and-billing-model.md) — concise current product model;
2. [`ARCH-010-merchant-lifecycle-state-transitions.md`](ARCH-010-merchant-lifecycle-state-transitions.md) — canonical cross-service architecture;
3. [`ARCH-010-supersession-map.md`](ARCH-010-supersession-map.md) — explicit historical old→new mapping;
4. the exact `ARCH-010-*` task — bounded implementation/status contract.

ARCH-007 dependencies may be read for implemented primitives, code history and review evidence, but their superseded automatic-overage, Free-allowance-adjustment, old capacity-order, top-up/refund or lifecycle rules must not override ARCH-010.

## Execution rules

1. Individual task YAML/frontmatter is authoritative for status and `depends_on`.
2. A task is claimable only when `status: ready` and every explicit dependency is Complete.
3. `enables` is a reverse-index convenience and does not create an additional dependency gate.
4. Respect one-task/one-repository worktree isolation and mirrored task branches.
5. Implementation agents do not merge to `main`; developer/user owns final integration.
6. System-test tasks are terminal/manual-gated. Never auto-start them and never make implementation depend on them.
7. When a task hits a documented Stop condition, return to `moda_architect`; do not invent missing architecture.

## Current Ready frontier

There are 14 dependency-ready implementation tasks at consolidation time.

### Database

```text
ARCH-010-DATABASE-001  durable subscription reconciliation schedule
ARCH-010-DATABASE-005  durable capacity-blocked recovery state
ARCH-010-DATABASE-006  shop-lifetime Free grant/platform policy
ARCH-010-DATABASE-007  purchased-credit lot/refund accounting
ARCH-010-DATABASE-008  FROZEN/provider lifecycle evidence
ARCH-010-DATABASE-009  promotional-credit ledger
```

Recommended Database critical-path order when repository work is serialized:

```text
DATABASE-001
  -> DATABASE-002 / DATABASE-003 become eligible
DATABASE-006
DATABASE-002
DATABASE-004
DATABASE-003
DATABASE-007
DATABASE-008
DATABASE-009
DATABASE-005
```

`DATABASE-005/007/008/009` are independent at the current graph level; the order above prioritizes the central activation/period path rather than declaring new dependencies.

### Shared

```text
ARCH-010-SHARED-001  reconciliation queue contract
ARCH-010-SHARED-005  refund system-message contract
```

Recommended chains:

```text
SHARED-001 -> SHARED-002
          \-> SHARED-003 -> SHARED-004

SHARED-005 -> SHARED-006
```

Publication tasks run only after the corresponding implementation task is architect-accepted.

### Background

```text
ARCH-010-BACKGROUND-004  inactive-shop recovery gate
ARCH-010-BACKGROUND-005  inactive-shop WhatsApp/conversation gate
ARCH-010-BACKGROUND-015  Partner subscription lifecycle snapshot
```

These can be implemented before the central billing-period chain becomes eligible, subject to repository concurrency policy.

### Shopify merchant app

```text
ARCH-010-SHOPIFY-001  fresh install/onboarding
ARCH-010-SHOPIFY-013  authoritative Shopify subscription read model
```

### Gateway

```text
ARCH-010-GATEWAY-001  wire Redis to billing workers
```

### Admin

No Admin task is currently Ready. ADMIN-001/004 become eligible after DATABASE-006/009 respectively.

## Dependency layers

The following layers are a **graph view**, not permission to run same-repository tasks concurrently. Repository/worktree/concurrency rules still apply.

### Layer 0 — current Ready frontier

```text
BACKGROUND-004, BACKGROUND-005, BACKGROUND-015
DATABASE-001, DATABASE-005, DATABASE-006, DATABASE-007, DATABASE-008, DATABASE-009
GATEWAY-001
SHARED-001, SHARED-005
SHOPIFY-001, SHOPIFY-013
```

### Layer 1

```text
ADMIN-001, ADMIN-004
BACKGROUND-011
DATABASE-002, DATABASE-003
SHARED-002, SHARED-003, SHARED-006
SHOPIFY-018
```

### Layer 2

```text
ADMIN-002, ADMIN-005
BACKGROUND-002, BACKGROUND-014
DATABASE-004
SHARED-004
```

### Layer 3

```text
ADMIN-003
BACKGROUND-001, BACKGROUND-019
SHOPIFY-002
```

### Layer 4

```text
BACKGROUND-008, BACKGROUND-009
```

### Layer 5

```text
BACKGROUND-007
```

### Layer 6

```text
BACKGROUND-003
```

### Layer 7

```text
BACKGROUND-006, BACKGROUND-010
SHOPIFY-003
```

### Layer 8

```text
BACKGROUND-012, BACKGROUND-016
SHOPIFY-004, SHOPIFY-006, SHOPIFY-015
```

### Layer 9

```text
BACKGROUND-013, BACKGROUND-018
SHOPIFY-007, SHOPIFY-009, SHOPIFY-011
```

### Layer 10

```text
BACKGROUND-017
SHOPIFY-014
```

### Layer 11

```text
SHOPIFY-010
```

### Layer 12

```text
SHOPIFY-012
```

### Layer 13 — final merchant presentation endpoints

```text
SHOPIFY-008, SHOPIFY-016, SHOPIFY-017, SHOPIFY-019, SHOPIFY-020
```

### Layer 14 — manual terminal system tests

```text
SYSTEM-TEST-001
SYSTEM-TEST-002
SYSTEM-TEST-003
```

These become dependency-ready only after their own implementation prerequisites are Complete, but the developer still chooses when to invoke them.

### Layer 15 — final architecture acceptance

```text
SYSTEM-TEST-004
```

## Critical integration boundaries

### Database before runtime consumers

Schema/migration tasks must be integrated and their generated/client propagation completed before a runtime task that reads their new fields is deployed.

### Shared implementation before publication before consumers

Do not make consumers depend on an unpublished local Shared contract. SHARED-002/004/006 are explicit publication gates.

### PostgreSQL before BullMQ correctness

All delayed reconciliation/resume behaviour must remain reconstructable from PostgreSQL. A Redis/BullMQ success is never the only durable transition record.

### Provider call outside DB transaction

Tasks that query Shopify and then mutate local state preserve the architecture rule: provider/network I/O outside the DB transaction; row lock/re-read/stale guard inside the transaction before mutation.

### No partial authority handoff

Do not let merchant UI become subscription authority, Admin become merchant-facing, or local BillingPlan price/rank become Shopify commercial truth while implementing individual tasks.

## Recommended developer manual checkpoints

Before invoking expensive system tests, manually verify the integrated milestones in this order:

1. fresh install -> Free and fresh install -> Paid;
2. final recovery source priority and ordinary capacity exhaustion;
3. Free/Paid top-up purchase and provider confirmation;
4. billing-cycle rollover and pending plan change;
5. uninstall/reinstall;
6. cancellation and freeze/unfreeze execution gates;
7. partial refund hold/finalization on a safe non-production provider charge;
8. single-shop and targeted promotional grants.

These are developer checkpoints, not synthetic task dependencies.

## Production/rollout safety

ARCH-010 tasks are designed to be additive/fail-closed where possible, but merchant-facing behaviour should not be intentionally considered production-complete until the required cross-repository dependencies are integrated.

In particular:

- schema before consumer runtime;
- Shared release before consumer import;
- Background execution gates before relying on lifecycle UI states;
- provider read/reconciliation before enabling corresponding merchant action;
- no production claim of ARCH-010 completion before terminal system-test acceptance.

## Final system-test gate

```text
SYSTEM-TEST-001  core subscription/capacity lifecycle
SYSTEM-TEST-002  lifecycle execution gates
SYSTEM-TEST-003  refunds/promotions
        \           |           /
         -> SYSTEM-TEST-004 final acceptance
```

ARCH-010 status remains **Agreed**, not **Implemented**, until this terminal validation chain is complete and architect-accepted.
