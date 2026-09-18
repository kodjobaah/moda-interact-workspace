# ARCH-011 Implementation Handoff — deterministic Luna revision

Date: 2026-09-14
Coordinator: `moda_architect`

## Binding product rules
- Native Shopify App Pricing only; no legacy Billing API migration.
- Same-cycle proration applies only to UPGRADE.
- Every DOWNGRADE remains effective at the next provider billing-cycle boundary; no current-cycle clawback/proration.
- Shopify provider-current plan is authority; Moda requested target is historical intent only.
- Callback is an accelerator, never entitlement authority.
- DATABASE-013 is the immutable database baseline.

## Luna rule
The task file gives exact files, symbols, decisions, tests and stop conditions. Do not invent alternate architecture, helper names, schedulers, ranks, billing formulas, timestamps, target-specific Shopify links or downgrade proration. If an exact authorised file/symbol is absent or a prerequisite baseline capability is missing, STOP and return evidence to `moda_architect`.

## Task graph
```text
DATABASE-001 -> DATABASE-002 -> ADMIN-001 -> ADMIN-002 ------+
      |              |                                      |
      |              +-> SHOPIFY-001 -> SHOPIFY-002 --------+
      |                                                       |
ARCH-012-SHARED-001 (`0.12.0`) -> SHARED-001 -> SHARED-002 (`0.13.0`)
                                              |
                                              +-> BACKGROUND-002 -> BACKGROUND-003-+-> SYSTEM-TEST-001
                                                                  ^                  |
BACKGROUND-001 ---------------------------------------------------+                  +------------------+
```

Ready frontier: `ARCH-011-DATABASE-001`, `ARCH-011-SHARED-001`, `ARCH-011-BACKGROUND-001`. `ARCH-011-SHARED-001` now explicitly preserves the accepted ARCH-012 Shared `0.12.0` baseline; `ARCH-011-SHARED-002` remains Pending until SHARED-001 is architect-accepted Complete.

## Repository sequencing
Tasks in the same repository are deliberately serialised by dependencies. Do not start the next same-repository task until the predecessor is architect-accepted Complete.
