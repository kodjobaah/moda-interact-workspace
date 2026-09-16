# ARCH-015 database tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-DATABASE-001](DATABASE-001-fractional-provider-usage-snapshots.md) | complete | Change provider quantity-before/after purchase evidence from Int to Decimal for fractional App Event corrections. |
| [ARCH-015-DATABASE-002](DATABASE-002-typed-refund-correction-evidence.md) | ready | Add typed automatic-refund provider baseline/expected-after evidence and an explicit one-to-one correction UsageEvent link on RecoveryCreditRefund. |

## Current architect review state

`ARCH-015-DATABASE-001` Attempt 1 is **Accepted — Complete**. The bounded Decimal evidence-type migration is complete.

`ARCH-015-DATABASE-002` is **Ready**. It corrects the pre-implementation ARCH-015 refund design after code/schema audit proved that `UsageEvent` has no `metadata` field and that settlement-critical correction evidence belongs on `RecoveryCreditRefund`, not in an untyped JSON payload.

`ARCH-015-DATABASE-002` does not add a model/status/queue/catalogue. It adds only four typed Decimal correction-evidence fields plus one unique FK from `RecoveryCreditRefund` to the automatic correction `UsageEvent`, with grouped integrity constraints.
