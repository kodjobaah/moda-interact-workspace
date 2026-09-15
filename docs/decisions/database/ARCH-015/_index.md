# ARCH-015 database tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-015-DATABASE-001](DATABASE-001-fractional-provider-usage-snapshots.md) | complete | Change provider quantity-before/after purchase evidence from Int to Decimal for fractional App Event corrections. |

## Current architect review state

`ARCH-015-DATABASE-001` Attempt 1 is **Accepted**. The bounded Decimal evidence-type
migration is complete. No downstream task is promoted by this database acceptance
alone because each enabled task retains additional prerequisites.
