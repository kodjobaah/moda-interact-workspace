# ARCH-016 database tasks

| Task | Status | Summary |
|---|---|---|
| [ARCH-016-DATABASE-001](DATABASE-001-recovery-policy-discount-catalogue-outreach-generations.md) | complete | Durable recovery policy, Shopify discount catalogue, outreach attempts, generations and lifetime schema. |

## Current architect review state

`ARCH-016-DATABASE-001` Attempt 2 is **Accepted — Complete**. The durable ARCH-016
recovery-policy, Shopify-discount-catalogue, recovery-generation, outreach-attempt
and recovery-lifetime schema boundary is established. The selected validation
database remains blocked before ARCH-016 by the pre-existing ARCH-015 Prisma P3009;
that deployment-history issue is unchanged and was not modified by this task.

DATABASE-only dependants `ARCH-016-ADMIN-001` and `ARCH-016-BACKGROUND-002` are now
Ready. Shared-dependent siblings remain Pending until `ARCH-016-SHARED-001` is
architect-accepted Complete.
