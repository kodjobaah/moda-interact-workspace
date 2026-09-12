# ARCH-010 Final Consolidation / Architect Review

Date: 2026-09-12
Coordinator: `moda_architect`

## Overall decision

**ARCH-010 remains Agreed / In Progress and is now explicitly the Moda Interact first-production billing/lifecycle baseline. It is not yet Implemented.**

The 2026-09-12 review changes the rollout/migration boundary, not the core product intent:

```text
no production billing data exists
        ↓
PRE-PRODUCTION / BREAKING ROLLOUT
        ↓
ship one clean ARCH-010 first-production model
        ↓
future architectures migrate forward from that baseline
```

The binding baseline amendment is [`ARCH-010-first-production-baseline.md`](ARCH-010-first-production-baseline.md).

## Accepted task history decision

Completed task files remain immutable accepted implementation/review evidence.

This review verified that all **23 Complete ARCH-010 task files** from the supplied workspace remain byte-for-byte unchanged by the consolidation work. `ARCH-010-SHOPIFY-002` also remains unchanged in `review` at Attempt 8.

Where accepted/in-flight implementation targeted an intermediate development schema, the architecture now uses new dependent correction tasks or amended still-open tasks. It does not rewrite history.

## Database consolidation decision

The earlier idea of multiple cleanup migrations is rejected.

Instead:

- DATABASE-001..011 remain Complete historical development tasks;
- DATABASE-012 is Superseded before implementation;
- DATABASE-013 creates one final Prisma schema and one empty-database first-production migration;
- valid upgrade-economics requirements from DATABASE-012 are folded into DATABASE-013;
- future ARCH-011+ changes use normal forward migrations from accepted DATABASE-013.

This keeps development design history in task/review documents without making every intermediate development schema part of the production migration chain.

## First-production removals

The final baseline intentionally contains no runtime compatibility for:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment / FREE_ALLOWANCE_ADJUSTED
FREE_RECOVERY_LIFETIME alias
ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)
MIGRATION_RECONCILED
SubscriptionCancellationRequest / local cancellation state machine
appSubscriptionCancel execution path
RecoveryCreditPurchaseStatus.REFUNDED
negative/fractional App Event refund settlement/correction state
campaign-less/direct PromotionalCreditGrant compatibility
BILLING_FREE_ALLOWANCE_EXHAUSTED historical-row compatibility
```

Canonical lifetime entitlement:

```text
LIFETIME_FREE_RECOVERY_CREDITS
```

## Final capacity order

```text
Paid
  selected usable campaign promotion
  -> current-period included
  -> purchased FIFO lot
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION

Free
  selected usable campaign promotion
  -> purchased FIFO lot
  -> lifetime Free
  -> BLOCK NEW RECOVERY ADMISSION
```

The exact selected `PromotionalCreditGrant` lot is promotional capacity authority. There is no aggregate promotional entitlement counter.

## Refund model

Purchased-credit partial refunds remain first-release functionality, but the development automatic correction mechanism is removed.

Canonical rule:

```text
purchase remains ACTIVE
refund request/approval holds exact unused quantity
SUPER_ADMIN performs Shopify Partner Dashboard REFUND or CREDIT
provider evidence is recorded
local lot/aggregate refunded quantity is finalised exactly once
```

There is no purchase `REFUNDED` terminal state for a partial refund and no negative App Event correction processor.

## Cancellation model

Shopify App Pricing remains cancellation authority.

Moda observes and reconciles provider state. The first-production model contains no local cancellation request/approval/execution state machine and no `appSubscriptionCancel` path.

BACKGROUND-012 now owns both provider reconciliation and removal of any remaining development local cancellation executor code in the Background repository.

## Promotional model

First production supports campaign-linked merchant opt-in promotions only:

```text
PromotionCampaign
  -> MerchantPromotionSelection
  -> exact PromotionalCreditGrant(campaignId, shopId)
  -> UsageReservation.promotionalCreditGrantId
```

`PromotionalCreditGrant.campaignId` is required. Campaign-less direct grants are not migrated into production.

## Shared package consolidation

The already-published ARCH-010 development package `@modainteract/moda-interact-shared@0.10.0` contains contracts accumulated through accepted Shared tasks.

Because first production removes obsolete pre-production billing compatibility exports, two new tasks are required:

- SHARED-007 removes the local-cancellation contracts and the Free-only `BILLING_FREE_ALLOWANCE_EXHAUSTED` source/declaration contract without deprecation aliases;
- SHARED-008 publishes the resulting clean contract as `0.11.0`.

No duplicate publication of SHARED-001/003/005 is required.

## Consumer conformance tasks

Two new bounded consumer tasks prevent accepted implementation history from being rewritten:

- ADMIN-010 — remove Admin compatibility reads/types and compile only against DATABASE-013/SHARED-008;
- SHOPIFY-023 — remove Shopify billing compatibility reads/raw SQL/types and make lifetime-Free projection plan-independent.

Still-open Background/Shopify/Admin tasks were amended directly where their implementation has not yet been accepted.

## Task graph audit

Current counts from individual task YAML:

```text
all ARCH-010 task files: 79
complete:                 23
review:                    1
ready:                     4
pending:                  49
superseded:                2
```

Domain totals:

```text
Shopify       23
Background    19
Database      13
Admin         10
Shared         8
System Test    5
Gateway        1
```

Current Ready frontier:

```text
ARCH-010-DATABASE-013
ARCH-010-SHARED-007
ARCH-010-ADMIN-007
ARCH-010-BACKGROUND-015
```

Current Review:

```text
ARCH-010-SHOPIFY-002  Attempt 8
```

Graph validation:

```text
missing internal ARCH-010 dependency references: 0
internal dependency cycles:                        0
non-system-test task -> system-test dependency:    0
```

Historical `enables:` fields in immutable Complete/Review task files are not rewritten when new correction work is added. They are therefore historical reverse snapshots rather than a globally regenerated graph. Current `depends_on:` remains the execution eligibility authority; the open-task indexes/handoff provide the current reverse planning view.

## System-test boundary

Five system-test tasks remain terminal/manual-gated. They are not prerequisites for normal implementation work and must not auto-start when dependencies complete.

The developer may perform manual integrated verification after implementation before explicitly invoking the system-test suite.

## Infrastructure / observability assessment

This first-production baseline consolidation does not introduce a new infrastructure topology or new observability mechanism. Existing ARCH-010 Gateway work remains valid. No new Gateway task is required solely for schema rebaselining.

Runtime correction tasks must preserve existing logging/telemetry conventions; they must not create duplicate observability merely as part of compatibility cleanup.

## Architect conclusion

ARCH-010 now has a clean migration/runtime boundary:

```text
accepted development history is retained
        +
production compatibility is not fabricated before production
        +
one canonical database/Shared baseline is established
        +
open consumers converge on that baseline
```

This is the architecture to implement before first production.
