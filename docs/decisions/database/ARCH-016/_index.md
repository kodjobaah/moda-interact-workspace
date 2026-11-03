# ARCH-016 database tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-016-DATABASE-001](DATABASE-001-recovery-policy-discount-catalogue-outreach-generations.md) | complete | Durable recovery policy, Shopify discount catalogue, outreach attempts, generations and lifetime schema. |
| [ARCH-016-DATABASE-002](DATABASE-002-remove-recovery-lifetime-range-check.md) | complete | Attempt 1 accepted: remove the obsolete 1–90-day database check with a forward-only migration; preserve the 21-day default. |

## Current architect review state

`ARCH-016-DATABASE-001` Attempt 2 is **Accepted — Complete**. The durable ARCH-016
recovery-policy, Shopify-discount-catalogue, recovery-generation, outreach-attempt
and recovery-lifetime schema boundary is established. The selected validation
database remains blocked before ARCH-016 by the pre-existing ARCH-015 Prisma P3009;
that deployment-history issue is unchanged and was not modified by this task.

DATABASE-only dependants `ARCH-016-ADMIN-001` and `ARCH-016-BACKGROUND-002` are now
Ready. Shared-dependent siblings remain Pending until `ARCH-016-SHARED-001` is
architect-accepted Complete.

`ARCH-016-DATABASE-002` Attempt 1 is **Accepted — Complete**. Fresh and
upgrade PostgreSQL validation passed for the forward-only removal of the old
lifetime check. `ARCH-016-BACKGROUND-005` is now Ready; dependent
`ARCH-016-ADMIN-003` remains Pending until Background-005 is complete.
