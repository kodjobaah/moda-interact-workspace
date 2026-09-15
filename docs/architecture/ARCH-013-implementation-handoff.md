# ARCH-013 Implementation Handoff — coherent merchant routing before billing v1.1

Date: 2026-09-15
Coordinator: `moda_architect`
Architecture: [`ARCH-013-merchant-application-routing-navigation.md`](ARCH-013-merchant-application-routing-navigation.md)

## Binding execution order

ARCH-013-SHOPIFY-001 is the only implementation task currently defined for ARCH-013.

```text
ARCH-013-SHOPIFY-001
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

## Materialisation note

This definition was produced from the supplied 2026-09-15 workspace snapshot. It is a **portable canonical definition** and is `defined but not materialised` in the developer's canonical Git workspace until the normal `/moda-task ARCH-013-SHOPIFY-001` preparation/materialisation path creates/reuses the authoritative task branch/worktree.
