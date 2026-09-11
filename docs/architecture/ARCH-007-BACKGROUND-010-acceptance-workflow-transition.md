# ARCH-007 BACKGROUND-010 acceptance and workflow transition

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 architecture/implementation history. Do **not** use ARCH-007 merchant subscription, recovery-capacity, Free-allowance, automatic-overage, top-up, refund or lifecycle semantics as the current product contract. For current rules use [`ARCH-010`](ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../product/pricing-and-billing-model.md), and the [`supersession map`](ARCH-010-supersession-map.md). Non-superseded ARCH-007 message/provider safety primitives and historical completion evidence remain valid.

`ARCH-007-BACKGROUND-010` Attempt 4 is architect-accepted Complete.

Immediate dependency promotion:

```text
ARCH-007-BACKGROUND-011 -> Ready
```

`ARCH-007-SYSTEM-TEST-005` remains Pending/manual-gated until B011 is Complete.

## Git workflow transition

The developer explicitly deferred the new mirrored feature-branch workflow until
both of these tasks were accepted:

```text
ARCH-007-ADMIN-001
ARCH-007-BACKGROUND-010
```

Both are now Complete.

Therefore the **next newly claimed task** should use the mirrored feature-branch
workflow defined by the v2 workflow overlay:

```text
parent workspace:
  task/<TASK_ID>

implementation repository:
  task/<TASK_ID>
```

The agent MUST commit/push both task branches during the normal task lifecycle but must not merge either branch
into main or push/update main.

Do not retrofit feature-branch history onto ADMIN-001 or BACKGROUND-010.

A full workspace architecture/state reconciliation can be performed after the
developer applies the ADMIN-001 and BACKGROUND-010 acceptance overlays plus the
feature-branch workflow overlay.
