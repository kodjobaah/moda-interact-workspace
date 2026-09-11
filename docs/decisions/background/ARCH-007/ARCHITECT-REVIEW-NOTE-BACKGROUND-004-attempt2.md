# ARCH-007 BACKGROUND-004 Attempt 2 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 2 received **Changes Requested**.

The authoritative correction contract is the latest `## Architect Review` in:

```text
docs/decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md
```

## Nested database checkout observation

The submitted Background archive's nested `database/` checkout contains schema/migration material beyond accepted DATABASE-004, including recovery-credit-pack additions associated with later DATABASE-005 work.

BACKGROUND-004 does not use those later fields, so this did not cause the review decision.

Before developer commit/publication of BACKGROUND-004, ensure the nested database gitlink points to an architect-approved published database commit. Do not make BACKGROUND-004 implicitly depend on unaccepted DATABASE-005 work.

This note does not alter DATABASE-005 state.
