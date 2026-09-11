# ARCH-007 DATABASE-006 acceptance and migration-drift coordination

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 architecture/implementation history. Do **not** use ARCH-007 merchant subscription, recovery-capacity, Free-allowance, automatic-overage, top-up, refund or lifecycle semantics as the current product contract. For current rules use [`ARCH-010`](ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../product/pricing-and-billing-model.md), and the [`supersession map`](ARCH-010-supersession-map.md). Non-superseded ARCH-007 message/provider safety primitives and historical completion evidence remain valid.

`ARCH-007-DATABASE-006` Attempt 1 is architect-accepted Complete on 2026-09-08.

Immediate task promotion:

```text
ARCH-007-BACKGROUND-010 -> Ready
```

because DATABASE-006 and BACKGROUND-004 are Complete.

`ARCH-007-BACKGROUND-011` remains Pending behind BACKGROUND-010.

## Environment migration drift

During DATABASE-006 implementation, `prisma migrate dev` against the inherited remote database detected that the already-applied DATABASE-005 migration differs from the architect-accepted local DATABASE-005 migration and requested a reset.

No reset was performed.

This does not block DATABASE-006 source/migration acceptance, but the affected remote database must be reconciled before later migrations are deployed there.

For a disposable test database, rebuilding it from the accepted migration history is the preferred clean route.

For a non-disposable database, do not reset blindly. Compare the actually applied DATABASE-005 schema/constraint with the accepted local migration and reconcile it explicitly before applying DATABASE-006 or later migrations.

DATABASE-006's migration itself remains unapplied and is strictly additive.

The full-workspace synchronization has now updated the canonical ARCH-007 parent document to show DATABASE-006 Complete and BACKGROUND-010 Ready.
