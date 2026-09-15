# ARCH-013 Implementation Handoff — coherent merchant routing before billing v1.1

Date: 2026-09-15
Coordinator: `moda_architect`
Architecture: [`ARCH-013-merchant-application-routing-navigation.md`](ARCH-013-merchant-application-routing-navigation.md)

## Binding execution order

`ARCH-013-SHOPIFY-001` is architect-accepted **Complete** at Attempt 2. `ARCH-013-SHOPIFY-002` is architect-accepted **Complete** at Attempt 1. ARCH-013 has no remaining Ready task.

```text
ARCH-013-SHOPIFY-001  Complete / Attempt 2 Accepted
    -> ARCH-013-SHOPIFY-002
    -> architect review/acceptance
    -> only then define/start implementation work derived from
       Moda_Recovery_Credits_Shopify_App_Pricing_Design_v1.1
```

Do not combine billing v1.1 behaviour with this route refactor.

## Canonical billing URLs after this task

```text
/app/billing/options                    embedded billing/capacity page
/app/billing/select                     standalone Shopify-hosted plan-selection redirect
/app/billing/callback                   standalone plan-selection callback/reconciliation
/app/billing/recovery-credit-purchases  embedded purchased-credit history
```

Removed:

```text
/app/billing
/app/additional
```

## Luna execution rule

`ARCH-013-SHOPIFY-001` is an exact implementation contract.

The `moda_app` agent MUST:

1. use launcher-prepared parent + implementation task worktrees;
2. read the complete task before editing;
3. implement the route/state matrix exactly as written;
4. delete only the stale modules explicitly named by the task;
5. preserve billing/provider/refund business logic outside route/access presentation;
6. update all first-party links/tests so `/app/billing` has zero remaining runtime references;
7. run the exact focused tests plus repository-declared validation in the task;
8. return the task to `review` and STOP.

The agent MUST NOT:

```text
invent another merchant lifecycle state
retain /app/billing as an alias
rename /app/billing/options
turn /app/billing/select into a UI page
move /app/billing/callback under the app layout
make frozen plan selection available
make promotions available during onboarding/NO_CONTRACT/FROZEN
remove read/history access from onboarded NO_CONTRACT/FROZEN
implement billing v1.1
implement ARCH-011 proration
change Prisma schema
change Shared contracts
change Background/Gateway/Messaging
```

If the current code contradicts a named route/file assumption materially, or satisfying the task requires a billing/product decision not specified here, STOP and report the exact evidence to `moda_architect`.

## SHOPIFY-002 correction execution rule

`ARCH-013-SHOPIFY-002` is deliberately narrower than SHOPIFY-001. The `moda_app` agent MUST implement only the task file `docs/decisions/shopify/ARCH-013/SHOPIFY-002-residual-routing-coherence-corrections.md`.

It MUST NOT reopen or rewrite the accepted SHOPIFY-001 route topology, lifecycle matrix, pending-recovery policy, navigation ordering, breadcrumbs, support-message actions, stale-route deletions or callback semantics.

The only production correction is to stop `/app/billing/options` from advertising purchased-credit history when `canAccessMerchantSurface(merchantExperienceState, "BILLING_PURCHASE_HISTORY")` is false. The other correction is the malformed `tests/unit/billing-ui.test.ts` import structure and its associated validation evidence.

After SHOPIFY-002 returns to `review`, STOP. Do not begin billing v1.1 or another ARCH-013 task automatically.

## Current review state

`ARCH-013-SHOPIFY-001` Attempt 2 remains **architect-accepted Complete**. Its accepted implementation is the dependency baseline for SHOPIFY-002.

`ARCH-013-SHOPIFY-002` Attempt 1 is **architect-accepted Complete**. Its correction derives purchase-history presentation from the canonical surface policy, hides the denied onboarding link, preserves direct route authorization, and repairs the billing UI test module without reopening SHOPIFY-001.

ARCH-013 is **Implemented** and has no remaining Ready task. The SHOPIFY-002 sequencing gate on later billing-v1.1 work is satisfied; no later billing task is implicitly started or promoted by this acceptance.
