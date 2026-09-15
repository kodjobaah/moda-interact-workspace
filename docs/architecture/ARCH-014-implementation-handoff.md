# ARCH-014 Implementation Handoff

Date: 2026-09-15
Coordinator: `moda_architect`
Architecture: `ARCH-014-admin-managed-merchant-pricing-catalogue.md`

## Current accepted baseline

Already Complete before this delta:

```text
ARCH-014-DATABASE-001
ARCH-014-ADMIN-001
ARCH-014-ADMIN-002
ARCH-014-ADMIN-003
ARCH-014-ADMIN-004
ARCH-014-SHOPIFY-001
ARCH-014-DATABASE-002
ARCH-014-SHOPIFY-002
```

Do not reopen those tasks for the new work.

## Binding execution rule for GPT-5.6 Luna

Each remaining task is deliberately explicit. The exact task file is the implementation contract. Do not infer another schema, translation format, card-content model, route, placement rule or save workflow.

For every task:

1. use launcher-prepared isolated parent + implementation worktrees;
2. record physical isolation/start synchronization evidence in the Completion Report;
3. edit only the authorized repository/surface;
4. use actual repository-declared scripts;
5. do not silently widen scope to unrelated baseline cleanup;
6. stop on any stated stop condition rather than improvising another architecture;
7. return completed implementation to `moda_architect` in `review` and STOP.

## New binding architecture invariants

```text
Highlights are merchant presentation content, not Shopify usage events.
DATABASE-002 creates only new highlight tables/validation; it does not ALTER any existing table.
Every persisted highlight has exact 20 locale title+description translations.
Plan name remains non-localized in ARCH-014 v1.
Translation package schemaVersion is 2 after ADMIN-004.
Translation v2 covers plan description + exact current highlight contentKey set for every locale.
Highlight contentKey is stable UUID; reorder changes position only.
Reorder-only edit does not invalidate translations.
Changed/new/removed English highlight content requires a new completed translation package.
Admin placement is shown in normal language; raw BEFORE/AFTER ids are hidden.
Create compares the current DB catalogue order to the builder's captured order snapshot before placement/write.
Final Admin Create/Save exists only on Translations & review step.
Portfolio FAIL/UNVERIFIED cannot reach final review.
One reusable MerchantPricingCatalogue renders onboarding and completed NO_CONTRACT pricing.
NO_CONTRACT + zero active plans => pricing unavailable and no plan-selection/manage-capacity pricing CTA.
Primary pricing cards render DB/localized highlights; raw FIXED/VOLUME/GRADUATED tier mechanics are not primary card content.
Shopify remains subscription authority.
Operational BillingPlan/topology remains outside ARCH-014 catalogue behavior.
```

## Remaining task graph

```text
ARCH-014-DATABASE-002                       COMPLETE
ARCH-014-ADMIN-004                          COMPLETE
ARCH-014-SHOPIFY-002                        COMPLETE
        |
        v
ARCH-014-ADMIN-005                          COMPLETE
        |
        v
ARCH-014-SYSTEM-TEST-001                    READY (DEVELOPER-GATED)
```

DATABASE-002, ADMIN-004, ADMIN-005 and SHOPIFY-002 are architect-accepted/integrated. No automatic implementation task remains. SYSTEM-TEST-001 is **Ready** but terminal/developer-gated and must be invoked explicitly by the developer.

## Materialisation state

This delta defines tasks against the supplied 2026-09-15 current snapshot in which ADMIN-003 is Complete. Applying the overlay materialises documentation only; it does not claim implementation worktrees/branches. Normal `/moda-task` launcher preparation remains authoritative.

## Non-blocking tooling note

DATABASE-002 is accepted on the implemented runtime/database contract. Broader SQL-spelling mutation coverage in `validate-arch014-plan-highlights.mjs` is optional tooling hardening and does not gate ADMIN-004, SHOPIFY-002 or SYSTEM-TEST-001.
