# ARCH-007 outbound-safety coordination note — reconciled historical pointer

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

The standalone-conversation/outbound-safety correction described by this note is now part of the canonical ARCH-007 architecture and durable task files.

Current sources of truth:

- `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`
- `docs/architecture/ARCH-007-implementation-handoff.md`
- `docs/decisions/database/ARCH-007/DATABASE-004-standalone-whatsapp-conversation-scope.md`
- `docs/decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md`

DATABASE-004 is architect-accepted Complete. BACKGROUND-004 is currently **In Progress — Attempt 2** under its existing Changes Requested contract. Do not use the old blocker state from this historical note.
