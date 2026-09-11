# ARCH-007 BACKGROUND-004 Attempt 3 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 3 received **Changes Requested** for one remaining bounded tenant-isolation edge.

The implementation correctly fixes terminal-agent bypass, deterministic terminal content, ambiguous returned ownership pairs, standalone expiry/race behavior and per-conversation cap regressions.

The remaining issue is that both exact-phone routing lookups still use `take: 10`, which does not prove no conflicting 11th tenant exists.

The authoritative Attempt 4 correction contract is the latest `## Architect Review` in:

```text
docs/decisions/background/ARCH-007/BACKGROUND-004-common-whatsapp-outbound-admission.md
```

Use an overflow-sentinel bound (equivalent to `take: 11`) and fail closed whenever the sentinel row exists. Do not redesign the routing or implement BACKGROUND-010.
