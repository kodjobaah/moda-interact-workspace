# ARCH-007 amendment — inbound WhatsApp abuse admission

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
