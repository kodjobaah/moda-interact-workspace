# Architecture index

> **State synchronized 2026-09-08.** Current task state is generated in
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

## Current execution highlights

- `ARCH-001`: the two task files that had drifted back to Review (`SHOPIFY-001`, `BACKGROUND-001`) are restored to their documented Round-2 Accepted/Complete state; `GATEWAY-001` is Ready.
- `ARCH-005`: `SHOPIFY-004` is Ready now that its ARCH-007 overlap dependency is Complete.
- `ARCH-007`: Shared `0.8.0` is current/published; `SHOPIFY-003` is Ready for Attempt 2 after a narrow dependency-baseline correction request; `ADMIN-001`, `BACKGROUND-005`, `BACKGROUND-009`, and `BACKGROUND-010` are Ready; `BACKGROUND-011` remains Pending behind BACKGROUND-010.
- System-test tasks remain terminal/manual-gated across architectures.

## Historical architecture material

Files named `*-review-*`, `*-amendment.md`, overview documents, and old overlay/patch artifacts may intentionally preserve earlier decisions or task frontiers. Use the current-state rollup and task YAML for execution eligibility.
