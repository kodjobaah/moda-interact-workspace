# Architecture index

> **State synchronization:** ARCH-001..007 rows retain the 2026-09-08 rollup; ARCH-008..009 retain the 2026-09-12 rollup; ARCH-010 is synchronized 2026-09-13. Current task state is generated in
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
| ARCH-010 | complete 40, pending 34, ready 4, superseded 8 | [Merchant lifecycle state transitions and behavioural access](ARCH-010-merchant-lifecycle-state-transitions.md) · [First-production baseline](ARCH-010-first-production-baseline.md) |
| ARCH-011 | pending 9, ready 3 | [Pro-rated same-cycle subscription upgrades](ARCH-011-pro-rated-same-cycle-subscription-upgrades.md) |
| ARCH-012 | pending 7, ready 3 | [Moda-managed WhatsApp communications](ARCH-012-moda-managed-whatsapp-communications.md) |
| ARCH-013 | complete 2 | [Merchant application routing, navigation and lifecycle coherence](ARCH-013-merchant-application-routing-navigation.md) |

## Current execution highlights

- `ARCH-010`: first-production baseline consolidation is current. Ready frontier: `BACKGROUND-008`, `BACKGROUND-009`, `ADMIN-004`, `ADMIN-008`. `DATABASE-014` and `ADMIN-010` are architect-accepted Complete; superseded tasks remain history only.
- `ARCH-010` system-test tasks remain terminal/manual-gated and never block implementation startup.
- For architectures other than ARCH-010, use [`WORKSPACE-CURRENT-TASK-STATE.md`](WORKSPACE-CURRENT-TASK-STATE.md) plus individual task YAML rather than relying on an old highlight bullet.

- `ARCH-012`: agreed Moda-managed WhatsApp communications. Ready frontier: `SHARED-001`, `DATABASE-001`, `BACKGROUND-003`. Exact task YAML and `ARCH-012-implementation-handoff.md` are authoritative.

- `ARCH-013`: implemented. `SHOPIFY-001` is Complete / Attempt 2 Accepted and `SHOPIFY-002` is Complete / Attempt 1 Accepted. ARCH-013 has no Ready task; the routing-coherence gate before later billing-v1.1 work is satisfied.

## Historical architecture material

Files named `*-review-*`, `*-amendment.md`, overview documents, and old overlay/patch artifacts may intentionally preserve earlier decisions or task frontiers. Use the current-state rollup and task YAML for execution eligibility.

## ARCH-019 — merchant recovery experience (2026-09-20)

Current frontier: all ARCH-019 implementation tasks are architect-accepted/Complete: DATABASE-001 and SHOPIFY-001/003/006 at Attempt 1, SHOPIFY-002 at Attempt 3, SHOPIFY-004/005 at Attempt 2. SHOPIFY-006 accepted `39054cec`. SYSTEM-TEST-001 Ready at Attempt 0, explicitly developer-invoked after manual validation; not started. Architecture remains In Progress pending terminal integrated validation and final architect acceptance. Accepted dependency records are reconciled into SYSTEM-TEST-001; readiness does not authorize execution, deployment or unmerged dependency consumption.

[Architecture](ARCH-019-merchant-recovery-experience.md) · [Implementation handoff](ARCH-019-implementation-handoff.md)

## ARCH-020 — CommerceAgent Studio and MCP capabilities (2026-09-20)

COMMERCE-001 is architect-accepted Complete at Attempt 3 (`d7c1c65`). The descendant-process cleanup correction passed focused functional validation; prior real Docker PostgreSQL/Redis readiness evidence is retained. COMMERCE-002 is architect-accepted Complete at Attempt 2 (`fb3362e`): development HTTP mutations and revoked-session recovery are corrected. Live Google OAuth remains developer-owned deployment validation. Downstream source consumption awaits developer integration or explicit accepted-commit approval; no task is promoted or launched. COMMERCE-001 remains accepted and integrated. Other task rows retain this branch snapshot; canonical task worktrees remain authoritative.

The Commerce repository and nested database are provisioned; live MCP remains private and staff UI routing remains Gateway-owned. This task review does not complete ARCH-020.

[Architecture](ARCH-020-commerce-agent-studio-mcp-capabilities.md) ·
[Implementation handoff](ARCH-020-implementation-handoff.md)

## Shopify merchant preferences acceptance — 2026-09-20

SHOPIFY-001 is architect-accepted Complete at Attempt 1 (`4693bba`, report
`c5016d73`). Merchant eligibility, explicit idempotent saves and guarded form
behavior conform; architect reran 18 passing focused checks and reviewed six
passing PostgreSQL tests plus build/browser evidence. Existing repository-wide
typecheck/lint limitations remain documented. SYSTEM-TEST-001 remains Pending
until all its implementation dependencies are accepted, then explicitly
user-invoked; no task is launched. Developer integration remains separate.

Historical pre-acceptance snapshot: 19 tasks, 4 Complete, 1 Ready, 14 Pending; superseded for BACKGROUND-001 by the Attempt 3 acceptance below.
Other canonical task worktrees remain authoritative for concurrent progress;
this review does not overwrite their state. Prior readiness records are historical.

## BACKGROUND-001 Attempt 3 architect acceptance — 2026-09-20

ARCH-020-BACKGROUND-001 is **Accepted / Complete, Attempt 3**, implementation
`4e42056`, report `7a3cf35d`. R1/R2 are resolved: persisted inbound ordering
replaces completion-time comparisons, and finishing an earlier reply does not
discard valid pending audio. Architect independently reran **133 passing tests**
and reviewed the submitted passing build and local real-SDK compatibility evidence.
The existing configurable OpenAI adapter and A1/A2 amendments are accepted.
Live audio-quality and PostgreSQL concurrency checks remain explicitly not run;
no deployed integration or acoustic-quality result is asserted.

This is the current decision and supersedes earlier BACKGROUND-001 Ready/Review
and Changes Requested notes. Other task states remain unchanged. BACKGROUND-002,
GATEWAY-001, COMMERCE-012 and SYSTEM-TEST-001 retain remaining dependency gates;
no dependent task is promoted or launched. Developer integration remains separate,
and ARCH-020 is not complete. See the task's latest Architect Review for limits.

## COMMERCE-011 Attempt 3 — Changes Requested — 2026-09-21

COMMERCE-011 is **Ready, Attempt 3 retained**, claim cleared, not accepted.
Reviewed implementation `c616560` and report `78325853`. Prior four compiler
reproductions pass and R4's rolling-history/readiness/error-handling defects are
corrected in source. Three additional invalid GraphQL definitions still return
valid:true (unquoted String value, duplicate argument, conflicting alias).
R1 remains incomplete; R3 still returns a search excerpt as a document and retains
failed startup promises without owned shutdown. See the latest task Architect
Review. Verified artifact is retained; no new live validation requirement, claim,
dependent promotion, implementation edit or main integration. Other task states
and C17 ownership remain unchanged.

## COMMERCE-011 Attempt 4 — document-provider resolution — 2026-09-21

COMMERCE-011 is **Ready, Attempt 4 retained**, claim cleared, not yet accepted.
Reviewed `f363ac4` / report `05311f5b`; eight independent compiler checks pass.
The pinned MCP document-fetch gap is valid and is resolved architecturally by
**C15.1**: retain MCP search, add a bounded credential-free server adapter for
exact official shopify.dev/docs document retrieval. The in-Studio API/workflow is
preserved. Always-unavailable document retrieval is not task completion.
Implement the amendment on the same task branch, then resubmit. Prior review
history accidentally removed by the report has been restored. The reported full
suite remains95/96; the unrelated timing failure is not asserted resolved.
No new claim, downstream promotion, implementation edit or main integration.
