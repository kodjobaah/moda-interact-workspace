# ARCH-015 database tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-DATABASE-001](DATABASE-001-fractional-provider-usage-snapshots.md) | complete | Change provider quantity-before/after purchase evidence from Int to Decimal for fractional App Event corrections. |
| [ARCH-015-DATABASE-002](DATABASE-002-typed-refund-correction-evidence.md) | complete | Add typed automatic-refund provider baseline/expected-after evidence and an explicit one-to-one correction UsageEvent link on RecoveryCreditRefund. |

## Current architect review state

`ARCH-015-DATABASE-001` Attempt 1 is **Accepted — Complete**. The bounded Decimal evidence-type migration is complete.

`ARCH-015-DATABASE-002` is **Ready**. It corrects the pre-implementation ARCH-015 refund design after code/schema audit proved that `UsageEvent` has no `metadata` field and that settlement-critical correction evidence belongs on `RecoveryCreditRefund`, not in an untyped JSON payload.

`ARCH-015-DATABASE-002` does not add a model/status/queue/catalogue. It adds only four typed Decimal correction-evidence fields plus one unique FK from `RecoveryCreditRefund` to the automatic correction `UsageEvent`, with grouped integrity constraints.


## DATABASE-002 Attempt 1 acceptance

`ARCH-015-DATABASE-002` Attempt 1 is **Accepted — Complete**.

The typed automatic-refund evidence boundary is now established on
`RecoveryCreditRefund`: four Decimal provider baseline/expected-after fields plus one
unique restrictive FK to the correction `UsageEvent`. Existing refund provenance and
refund-amount fields are reused, `UsageEvent.quantity` remains Decimal, and no generic
`UsageEvent.metadata` settlement record was introduced.

The selected database still has a pre-existing P3009 on the earlier ARCH-015 fractional
provider-usage migration. That database-history issue must be resolved before deployment,
but it is not caused by DATABASE-002 and does not require another implementation attempt.

`ARCH-015-BACKGROUND-003` is promoted to Ready because all of its declared prerequisites
are now architect-accepted Complete.
