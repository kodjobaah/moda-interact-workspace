# ARCH-010 Shopify Tasks

Architecture:

`docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`

First-production baseline:

`docs/architecture/ARCH-010-first-production-baseline.md`

Assigned Agent:

`moda_app`

Coordinator:

`moda_architect`

> Synchronized 2026-09-12 from individual task YAML. Individual task files are authoritative. Complete/Review task files are immutable accepted/in-flight evidence; their historical `enables:` fields are not rewritten when later correction tasks are added.

Current counts: `complete` 2, `pending` 19, `review` 1, `superseded` 1

| Task | Description | Status | Dependencies |
|---|---|---|---|
| `SHOPIFY-001` | Establish fresh-install no-plan state and onboarding-only merchant access | Complete | ARCH-007-SHOPIFY-001, ARCH-007-SHOPIFY-002 |
| `SHOPIFY-002` | Activate Free plan with durable asynchronous Shopify verification | **Review** | ARCH-010-DATABASE-006, ARCH-010-SHOPIFY-001, ARCH-010-DATABASE-001, ARCH-010-DATABASE-004, ARCH-010-SHARED-002, ARCH-007-SHOPIFY-001, ARCH-007-SHOPIFY-002 |
| `SHOPIFY-003` | Activate first verified paid plan with exact billing period | Pending | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-002, ARCH-010-BACKGROUND-002, ARCH-010-BACKGROUND-003, ARCH-008-SHOPIFY-001, ARCH-010-SHOPIFY-023 |
| `SHOPIFY-004` | Present current paid-period entitlement to merchants | Pending | ARCH-010-SHOPIFY-003, ARCH-010-DATABASE-013 |
| `SHOPIFY-005` | Make uninstall an execution gate without resetting billing state | Superseded | ARCH-010-BACKGROUND-004, ARCH-010-BACKGROUND-005 |
| `SHOPIFY-006` | Gate reinstall until Background restores Shopify subscription truth | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-006 |
| `SHOPIFY-007` | Present App Pricing billing-cycle transition and guard late-cycle top-up purchase | Pending | ARCH-010-BACKGROUND-007, ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-SHOPIFY-003, ARCH-010-SHOPIFY-004 |
| `SHOPIFY-008` | Present recovery-capacity exhaustion on merchant dashboard and history | Pending | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-BACKGROUND-009, ARCH-010-SHARED-008 |
| `SHOPIFY-009` | Add local merchant recovery-capacity projection | Pending | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-004, ARCH-010-SHOPIFY-023 |
| `SHOPIFY-010` | Productionise recovery top-up purchase panel component | Pending | ARCH-010-SHOPIFY-014 |
| `SHOPIFY-011` | Productionise Shopify-hosted plan management panel component | Pending | ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-015 |
| `SHOPIFY-012` | Integrate real billing options route and purchase hub | Pending | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-010, ARCH-010-SHOPIFY-011, ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-018, ARCH-010-SHOPIFY-014, ARCH-010-SHOPIFY-015, ARCH-010-SHOPIFY-007, ARCH-008-SHOPIFY-001 |
| `SHOPIFY-013` | Expose authoritative Shopify commercial subscription read model | Complete | ARCH-008-SHOPIFY-001 |
| `SHOPIFY-014` | Expose real recovery top-up purchase lifecycle for billing options | Pending | ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-007, ARCH-007-SHOPIFY-004, ARCH-010-SHOPIFY-018 |
| `SHOPIFY-015` | Handle Shopify-hosted upgrade and downgrade return without premature entitlement change | Pending | ARCH-010-SHOPIFY-013, ARCH-010-SHARED-008, ARCH-010-BACKGROUND-010, ARCH-010-SHOPIFY-018 |
| `SHOPIFY-016` | Present Shopify cancellation state without local cancellation authority | Pending | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-013, ARCH-010-BACKGROUND-012, ARCH-010-BACKGROUND-013 |
| `SHOPIFY-017` | Present unused purchased-credit refundability and support CTA | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-SHOPIFY-012 |
| `SHOPIFY-018` | Expose Shopify-authoritative subscription lifecycle state including freeze and unfreeze | Pending | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-013, ARCH-010-SHOPIFY-023 |
| `SHOPIFY-019` | Present frozen Shopify subscription state and disable business billing actions | Pending | ARCH-010-BACKGROUND-017, ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-018 |
| `SHOPIFY-020` | Present selected promotion and promo-first recovery capacity | Pending | ARCH-010-SHOPIFY-009, ARCH-010-SHOPIFY-012, ARCH-010-SHOPIFY-021 |
| `SHOPIFY-021` | Show eligible running promotion offers and let a merchant select one | Pending | ARCH-010-DATABASE-013, ARCH-010-SHOPIFY-018, ARCH-010-ADMIN-004 |
| `SHOPIFY-022` | Show merchant promotion selection and usage history | Pending | ARCH-010-SHOPIFY-021, ARCH-010-DATABASE-013 |
| `SHOPIFY-023` | Conform Shopify billing runtime to the clean first-production baseline | Pending | ARCH-010-DATABASE-013, ARCH-010-SHARED-008, ARCH-010-SHOPIFY-002 |

## Execution note

`depends_on` in the individual task file is the execution eligibility authority.
