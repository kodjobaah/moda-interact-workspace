# ARCH-007 Background Tasks

Architecture: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

Assigned Agent: `moda_background`

Coordinator: `moda_architect`

| Task | Description | Status | Dependencies |
|---|---|---|---|
| BACKGROUND-001 | Implement typed effective entitlement and billing safety policy resolution | Complete | SHARED-002, DATABASE-003 |
| BACKGROUND-002 | Implement concurrency-safe Free recovery reservation, commit and release | Complete | BACKGROUND-001 |
| BACKGROUND-003 | Integrate Free/paid recovery admission, usage commitment and merchant billing notifications | Complete | BACKGROUND-002, SHOPIFY-001 |
| BACKGROUND-004 | Route every Moda-originated WhatsApp send through one durable safety-admission boundary | Complete | BACKGROUND-003, DATABASE-004 |
| BACKGROUND-005 | Apply normalized Meta provider status to durable message and usage accounting | Complete | BACKGROUND-004, MESSAGING-001, SHARED-004 |
| BACKGROUND-006 | Implement Shopify App Events 2026-07 adapter and expiring token cache | Complete | SHARED-002, DATABASE-002 |
| BACKGROUND-007 | Publish paid UsageEvents idempotently with retries and compensating corrections | Complete | BACKGROUND-003, BACKGROUND-006 |
| BACKGROUND-008 | Add independent billing worker for publication, subscription sync, reconciliation and uninstall drain | Complete | BACKGROUND-005, BACKGROUND-007, BACKGROUND-009, SHOPIFY-001 |
| BACKGROUND-009 | Activate billed recovery packs and consume purchased credits before overage | Complete | DATABASE-005, SHARED-006, BACKGROUND-007 |
| BACKGROUND-010 | Coalesce fragmented inbound WhatsApp messages into one CommerceAgent turn | Complete | DATABASE-006, BACKGROUND-004 |
| BACKGROUND-011 | Add inbound WhatsApp abuse admission before routing and CommerceAgent work | Complete | BACKGROUND-010 |
> **State synchronization — 2026-09-08:** The task table above is regenerated from the individual task YAML frontmatter. Those task files remain authoritative. Historical narrative below may describe earlier frontiers.
The individual task YAML metadata is authoritative.

Current frontier:
- BACKGROUND-004 Attempt 4 is architect-accepted Complete.
- BACKGROUND-005 Attempt 2 is architect-accepted Complete.
- BACKGROUND-007 Attempt 3 is architect-accepted Complete.
- BACKGROUND-009 Attempt 3 is architect-accepted Complete.
- BACKGROUND-008 Attempt 3 received Changes Requested; substantive runtime behavior is accepted and the same task is Ready for a final telemetry/test-hardening Attempt 4.
- BACKGROUND-010 Attempt 4 is architect-accepted Complete.
- BACKGROUND-011 Attempt 3 is architect-accepted Complete. Raw sender/global abuse admission and settled-turn sender/conversation/shop/global admission are operational safety, not merchant billing. SYSTEM-TEST-005 remains pending/manual-gated.
