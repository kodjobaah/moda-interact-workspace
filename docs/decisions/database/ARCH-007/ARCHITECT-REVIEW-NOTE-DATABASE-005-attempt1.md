# ARCH-007 DATABASE-005 Attempt 1 review note

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

Attempt 1 received **Changes Requested** for one database CHECK-semantics defect.

The migration currently uses:

```sql
NOT "recoveryCreditPackEnabled"
OR "recoveryCreditsPerPack" > 0
```

which permits `recoveryCreditPackEnabled = true` with `recoveryCreditsPerPack = NULL` because PostgreSQL CHECK constraints accept an UNKNOWN/NULL result.

The authoritative Attempt 2 correction contract is the latest `## Architect Review` in:

```text
docs/decisions/database/ARCH-007/DATABASE-005-repeatable-recovery-credit-packs.md
```

Correct the unapplied migration in place so enabled packs explicitly require a non-null, positive `recoveryCreditsPerPack`, and strengthen the deterministic validator to assert that NULL-safe shape.

Do not redesign the recovery-credit schema or start DATABASE-006/SHARED-005.
