# ARCH-014 Implementation Handoff

Date: 2026-09-15
Coordinator: `moda_architect`
Architecture: `ARCH-014-admin-managed-merchant-pricing-catalogue.md`

## Binding execution rule for GPT-5.6 Luna

Every task is deliberately explicit. The exact task file is the implementation contract. Do not infer another data model, route, locale policy, catalogue-order rule, pricing algorithm or save workflow.

For every task:

1. use the launcher-prepared isolated parent + implementation worktrees;
2. record physical worktree/synchronization evidence in the Completion Report;
3. edit only the authorized repository/surface;
4. run the exact focused validations plus repository-declared validation in the task;
5. do not silently widen scope to solve unrelated baseline problems;
6. if a named prerequisite capability differs materially from the inspected snapshot/task assumption, STOP and return exact evidence to `moda_architect`;
7. when implementation is complete, set task to `review`, clear the claim, return to `moda_architect`, and STOP.

## Architecture invariants agents must not reinterpret

```text
Shopify remains subscription/billing authority.
ARCH-014 MerchantPricing catalogue is self-contained.
ARCH-014 database migration is additive-only.
No existing table/model block/enum literal is schema-modified by DATABASE-001.
No BillingPlan/BillingEconomicsSnapshot/BillingUpgradeEconomicsEdge row is needed to
  create, validate, order, activate, deactivate or render ARCH-014 catalogue plans.
No ARCH-014 Shared package task exists.
Canonical 20 locales are explicitly fixed by architecture.
No supported locale gets an English plan-description fallback.
Plan order comes only from MerchantPricingPlan.cataloguePosition.
No ordering by price/name/allowance/creation time/operational topology.
0..5 Shopify pricing usage events per catalogue plan.
1..6 tiers for GRADUATED/VOLUME.
Pasted/uploaded translation JSON uses one parser.
Every persisted plan has all 20 descriptions; no incomplete DB draft exists.
No hard-coded merchant commercial plan matrix remains after SHOPIFY-001.
Every lower->higher projected portfolio pair must PASS before economics-affecting save/activation.
Existing operational billing runtime is untouched.
```

## Task graph

```text
ARCH-014-DATABASE-001   additive self-contained MerchantPricing* persistence/integrity
ARCH-014-ADMIN-001      pure multi-meter full-portfolio economics engine

DATABASE-001 + ADMIN-001
    -> ARCH-014-ADMIN-002
       MerchantPricing plans view/builder + explicit catalogue ordering
       + translations + atomic save/activation

DATABASE-001
    -> ARCH-014-SHOPIFY-001
       active catalogue reader + onboarding rendering + hard-code removal

ADMIN-002 + SHOPIFY-001
    -> ARCH-014-SYSTEM-TEST-001
       terminal/manual integrated acceptance
```

There are intentionally **no** `ARCH-014-SHARED-*`, `ARCH-014-DATABASE-002` or `ARCH-014-SHOPIFY-002` tasks, and `ARCH-014-ADMIN-002` has no ARCH-011 topology dependency.

## Materialisation state

These definitions were authored against the supplied 2026-09-15 workspace snapshot and are **defined but not materialised**. No branch, worktree, claim, commit or push is asserted by this overlay. Normal `/moda-task` launcher preparation remains authoritative at execution time.
