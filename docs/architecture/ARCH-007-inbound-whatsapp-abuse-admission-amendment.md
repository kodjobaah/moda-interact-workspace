# ARCH-007 amendment — inbound WhatsApp abuse admission

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 architecture/implementation history. Do **not** use ARCH-007 merchant subscription, recovery-capacity, Free-allowance, automatic-overage, top-up, refund or lifecycle semantics as the current product contract. For current rules use [`ARCH-010`](ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../product/pricing-and-billing-model.md), and the [`supersession map`](ARCH-010-supersession-map.md). Non-superseded ARCH-007 message/provider safety primitives and historical completion evidence remain valid.

Created 2026-09-08 by `moda_architect`.

The single public Moda WhatsApp number introduces an application-layer abuse surface that is separate from tenant ambiguity and outbound-message caps.

Canonical implementation task:

```text
ARCH-007-BACKGROUND-011
docs/decisions/background/ARCH-007/BACKGROUND-011-inbound-whatsapp-abuse-admission.md
```

Dependency:

```text
DATABASE-006 + BACKGROUND-004 Complete
  -> BACKGROUND-010 coalescing
  -> BACKGROUND-011 abuse admission
  -> SYSTEM-TEST-005 terminal/manual-gated validation
```

The task uses two stages:

1. raw sender/global abuse admission before tenant/database routing;
2. settled-turn sender/conversation/shop/global abuse admission after BACKGROUND-010 coalescing and before outbound reservation/CommerceAgent.

This is operational safety state in Redis. It does not introduce a merchant-billable inbound-message or agent-turn metric.

The canonical ARCH-007 architecture, Background index and SYSTEM-TEST-005 task are updated by the same overlay.
