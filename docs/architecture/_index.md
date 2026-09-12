# Architecture index

> **State synchronization:** ARCH-001..007 rows retain the 2026-09-08 rollup; ARCH-008..010 rows below are synchronized 2026-09-12. Current task state is generated in
> [`WORKSPACE-CURRENT-TASK-STATE.md`](WORKSPACE-CURRENT-TASK-STATE.md).
> Individual task YAML remains authoritative. Historical review/amendment documents
> preserve the state that existed when they were written and should not be used as
> the current execution frontier.

| Architecture | Current task state | Primary architecture |
|---|---|---|
| ARCH-001 | complete 9, ready 1 | [Shopify checkout recovery webhook processing](ARCH-001-shopify-checkout-recovery-webhook-processing.md) |
| ARCH-002 | complete 61, pending 3, ready 2, superseded 5 | [Render production gateway and infrastructure](ARCH-002-render-production-gateway-infrastructure.md) |
| ARCH-003 | blocked 1, complete 23, pending 1, review 1, superseded 1 | [Admin operational UI](ARCH-003-admin-operational-ui.md) |
| ARCH-004 | complete 6, ready 1 | [Cart activity recovery rescheduling](ARCH-004-cart-activity-recovery-rescheduling.md) |
| ARCH-005 | complete 17, pending 2, ready 1, superseded 2 | [Global internationalisation and WhatsApp markets](ARCH-005-global-internationalisation-whatsapp-markets.md) |
| ARCH-006 | complete 21, pending 3, review 3, superseded 2 | [Merchant communications and support inbox](ARCH-006-merchant-communications-support-inbox.md) |
| ARCH-007 | complete 21, pending 13, ready 5 | [Shopify billing, usage and WhatsApp cost control](ARCH-007-shopify-billing-usage-cost-control.md) |
| ARCH-008 | complete 7, ready 1, superseded 1 | [Shopify App Pricing conformance](ARCH-008-shopify-app-pricing-conformance.md) |
| ARCH-009 | complete 5, pending 2, ready 2 | [Merchant billing lifecycle, cancellations and refunds](ARCH-009-merchant-billing-lifecycle-cancellations-refunds.md) |
| ARCH-010 | complete 30, pending 39, ready 5, superseded 7 | [Merchant lifecycle state transitions and behavioural access](ARCH-010-merchant-lifecycle-state-transitions.md) · [First-production baseline](ARCH-010-first-production-baseline.md) |

## Current execution highlights

- `ARCH-010`: first-production baseline consolidation is current. Ready frontier: `ADMIN-007`, `ADMIN-010`, `BACKGROUND-011`, `BACKGROUND-015`, `SHOPIFY-023`. `BACKGROUND-001` is Complete at accepted Attempt 6; `SHOPIFY-002` is Complete at accepted Attempt 8; `DATABASE-012` plus the five consolidation-only task IDs are Superseded.
- `ARCH-010` system-test tasks remain terminal/manual-gated and never block implementation startup.
- For architectures other than ARCH-010, use [`WORKSPACE-CURRENT-TASK-STATE.md`](WORKSPACE-CURRENT-TASK-STATE.md) plus individual task YAML rather than relying on an old highlight bullet.

## Historical architecture material

Files named `*-review-*`, `*-amendment.md`, overview documents, and old overlay/patch artifacts may intentionally preserve earlier decisions or task frontiers. Use the current-state rollup and task YAML for execution eligibility.
