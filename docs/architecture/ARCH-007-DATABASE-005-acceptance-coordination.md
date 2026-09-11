> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 architecture/implementation history. Do **not** use ARCH-007 merchant subscription, recovery-capacity, Free-allowance, automatic-overage, top-up, refund or lifecycle semantics as the current product contract. For current rules use [`ARCH-010`](ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../product/pricing-and-billing-model.md), and the [`supersession map`](ARCH-010-supersession-map.md). Non-superseded ARCH-007 message/provider safety primitives and historical completion evidence remain valid.

## Current synchronization

This coordination note is historical. Subsequent accepted state is now:

```text
DATABASE-005 Complete
DATABASE-006 Complete
SHARED-005 Complete
SHARED-006 Complete / published 0.8.0
BACKGROUND-010 Ready
```

Use the canonical ARCH-007 document and implementation handoff for the current frontier.

# ARCH-007 DATABASE-005 acceptance coordination

`ARCH-007-DATABASE-005` Attempt 2 is architect-accepted Complete on 2026-09-08.

Immediate promotions:

```text
DATABASE-006 -> Ready
SHARED-005   -> Ready
```

`SHARED-006` remains Pending until SHARED-005 is architect-accepted Complete.

Do not tell consumers to use `@modainteract/moda-interact-shared@0.8.0` until SHARED-006 is completed, architect-accepted and published.

The DATABASE-005 migration remains unapplied; deployment is developer-controlled.
