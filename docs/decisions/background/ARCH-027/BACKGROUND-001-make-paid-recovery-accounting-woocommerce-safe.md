---
id: ARCH-027-BACKGROUND-001
architecture_id: ARCH-027
title: Make paid included recovery accounting WooCommerce-safe
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-DATABASE-001
enables: []
created: 2026-10-03
updated: 2026-10-03
---

# Make paid included recovery accounting WooCommerce-safe

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Make the existing paid included-recovery accounting path safe for a future **ACTIVE Woo paid subscription** before any Woo subscription webhook task is allowed to activate one.

This task has one bounded outcome:

> The existing Background recovery-admission / reservation / commit path honors `BillingPeriodEntitlementCounter.currentAllowanceQuantity` as the mutable current spend ceiling and records Woo paid included usage **locally** without creating Shopify App Event reporting work.

The accepted provider-neutral capacity contract is:

```text
effectiveAllowance =
    currentAllowanceQuantity
    ?? grantedQuantity

available =
    max(
        effectiveAllowance
        - committedQuantity
        - reservedQuantity
        - forfeitedQuantity,
        0
    )
```

`grantedQuantity` remains the non-decreasing current-period historical/high-water grant used by existing database close/audit invariants.

A Woo downgrade may therefore legitimately produce:

```text
currentAllowanceQuantity = 5
committedQuantity        = 6

available = 0
```

without clawing back committed usage or invalidating the counter.

For paid included usage:

```text
SHOPIFY Shop
    -> existing Shopify usage-event reporting behavior unchanged

WOOCOMMERCE Shop
    -> UsageEvent.provider = WOOCOMMERCE
    -> shopifyReportState = NOT_APPLICABLE
    -> no shopifyEventHandle
    -> no shopifyIdempotencyKey
    -> no Shopify App Event/reporting work
```

This task does **not** consume Woo billing webhook receipts and does not activate a Woo paid subscription. It is a prerequisite for that later lifecycle task so verified Woo activation cannot expose a merchant to the current Shopify-only included-usage path.

## Context

The `moda-interact-workspace(20261003-123430).zip` source baseline contains the accepted ARCH-025 Background billing refactor. Relevant production responsibilities are already separated across:

```text
src/services/effective-billing-policy.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/recovery-billing.service.ts
src/services/current-billing-period-projection.service.ts
src/services/billing-subscription-reconciliation/*
```

The current inspected implementation is still Shopify-shaped in three ways that become unsafe once ARCH-027 begins projecting Woo paid subscriptions:

1. `EffectiveBillingPolicyResolver` requires every paid operational plan to have a Shopify usage-event handle.
2. `PaidIncludedRecoveryReservationService.commit()` always creates a Shopify-reportable `UsageEvent`:
   - `shopifyReportState = PENDING`;
   - Shopify event handle required;
   - Shopify idempotency key created.
3. Paid included availability is calculated from `grantedQuantity`; the new mutable `currentAllowanceQuantity` is not yet consumed by Background admission/reservation logic.

Without correcting those facts first, a verified Woo paid subscription could:

```text
either
    fail paid billing-policy validation because it has no usable Shopify provider meter semantics

or
    create Shopify App Event reporting work for Woo consumption

and
    ignore a Woo plan-switch allowance decrease/increase
```

ARCH-027-DATABASE-001 deliberately leaves this runtime correction to Background. It defines:

```text
currentAllowanceQuantity Int?
```

with:

```text
existing Shopify rows -> NULL
```

and preserves the database high-water constraint:

```text
committedQuantity
+ reservedQuantity
+ forfeitedQuantity
<= grantedQuantity
```

The task also relies on ARCH-026's accepted:

```text
Shop.platform = SHOPIFY | WOOCOMMERCE
```

For ARCH-027 v1 the platform is the provider-dispatch evidence for included-usage reporting:

```text
SHOPIFY Shop
    -> existing Shopify App Event path

WOOCOMMERCE Shop
    -> local Moda usage accounting only
```

This is a bounded v1 dispatch decision; it does not introduce a generic billing-provider framework.

## Scope

Modify only `moda-interact-background` production/tests required for paid included capacity admission and paid included consumption evidence.

Expected primary production areas:

```text
src/services/effective-billing-policy.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/recovery-billing.service.ts
```

Additional directly related type/test helpers may be changed when required.

Update the Background repository's nested `database/` gitlink to the newest compatible architect-accepted `moda-interact-database` main commit containing `ARCH-027-DATABASE-001`, then regenerate Prisma through the repository's declared workflow.

### Explicitly retained boundaries

This task MUST NOT modify Woo subscription/provider lifecycle reconciliation.

It MUST NOT:

- claim `WooCommerceBillingWebhookReceipt`;
- materialize a paid `BillingPlan`;
- activate/switch/freeze/cancel a `Subscription`;
- open/roll/close a Woo `BillingPeriod`;
- write `currentAllowanceQuantity` as part of a plan change;
- reconcile a Woo top-up purchase;
- report Woo included usage externally;
- add a queue/event contract;
- add a generic billing-provider abstraction.

Those are later bounded tasks.

## Out of Scope

- API webhook ingress.
- PostgreSQL receipt claiming.
- Woo recurring subscription lifecycle reconciliation.
- Woo paid `BillingPlan` materialisation.
- Woo billing-period creation/renewal.
- Woo plan-switch writer logic.
- Woo top-up activation/refund reconciliation.
- Shopify plan-change redesign.
- Shopify App Event publisher redesign.
- Woo API calls or credentials.
- Woo WordPress/UI changes.
- Admin changes.
- Gateway/infrastructure changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — `currentAllowanceQuantity` is the current spend ceiling

Every Background calculation that determines whether **new paid included recovery capacity** may be reserved MUST use:

```text
effectiveAllowance =
    currentAllowanceQuantity
    ?? grantedQuantity
```

New-reservation availability is exactly:

```text
max(
    effectiveAllowance
    - committedQuantity
    - reservedQuantity
    - forfeitedQuantity,
    0
)
```

Do not use `grantedQuantity` alone when `currentAllowanceQuantity` is non-null.

### R2 — Preserve the high-water grant invariant

The runtime validator must continue to require all counter quantities to be finite non-negative safe integers.

The existing database/audit invariant remains:

```text
committedQuantity
+ reservedQuantity
+ forfeitedQuantity
<= grantedQuantity
```

If `currentAllowanceQuantity` is non-null, additionally require:

```text
currentAllowanceQuantity is a non-negative safe integer
currentAllowanceQuantity <= grantedQuantity
```

Do **not** require:

```text
committedQuantity + reservedQuantity <= currentAllowanceQuantity
```

because a Woo downgrade may legitimately lower the current spend ceiling below already-consumed/reserved usage.

### R3 — Existing reservations survive a downgrade

A plan-switch allowance decrease affects **new reservation admission only**.

An included reservation already in:

```text
RESERVED
```

before the allowance decrease may still:

```text
COMMIT
or
RELEASE
```

through the existing transition rules.

Do not claw back, auto-release or reject commit solely because:

```text
committed + reserved > currentAllowanceQuantity
```

after a downgrade.

### R4 — Upgrade capacity becomes available without resetting usage

For a fixture representing a later Woo upgrade writer:

```text
grantedQuantity            = 10
currentAllowanceQuantity   = 10
committedQuantity          = 5
reservedQuantity           = 0
forfeitedQuantity          = 0
```

the paid reservation service must expose:

```text
available = 5
```

without resetting committed/reserved quantities or creating a new period.

This task does not perform the writer transition; it proves the consumer semantics required by the later lifecycle task.

### R5 — Shopify null override preserves exact existing behavior

For existing Shopify counters:

```text
currentAllowanceQuantity = NULL
```

the effective allowance is exactly:

```text
grantedQuantity
```

Existing Shopify reservation/exhaustion behavior must remain unchanged.

### R6 — Effective billing policy exposes both audit and current allowance

Extend the paid included counter projection used inside Background so it retains:

```text
grantedQuantity
currentAllowanceQuantity
effectiveAllowanceQuantity
committedQuantity
reservedQuantity
forfeitedQuantity
```

where:

```text
effectiveAllowanceQuantity =
    currentAllowanceQuantity ?? grantedQuantity
```

Do not overwrite or relabel `grantedQuantity`; callers that need the historical/high-water grant must continue to see it.

### R7 — Paid plan provider validation is platform-aware

`EffectiveBillingPolicyResolver` must load the authoritative `Shop.platform`.

For:

```text
Shop.platform = SHOPIFY
```

preserve the existing paid-plan requirement that a Shopify normal-usage event handle is configured.

For:

```text
Shop.platform = WOOCOMMERCE
```

do **not** reject an otherwise valid paid plan merely because Background will not submit included usage to Shopify.

The resolver must still require:

- active Shop;
- active mapped plan;
- current OPEN paid BillingPeriod;
- valid included counter;
- all existing feature/pause/operational requirements.

Do not weaken those checks.

### R8 — Paid reservation commit dispatches reporting by Shop platform

When a paid included reservation commits, create exactly one local `UsageEvent` with the existing common identity:

```text
metric         = RECOVERY_CONVERSATION
quantity       = committed quantity
idempotencyKey = existing Moda recovery idempotency key
sourceType     = PAID_RECOVERY_CONVERSATION
sourceId       = source key
billingPeriodId = current BillingPeriod
```

Then apply provider-edge reporting evidence as follows.

#### Shopify

Preserve exactly the existing behavior:

```text
provider               = SHOPIFY
shopifyReportState     = PENDING
shopifyEventHandle     = current paid Shopify usage-event handle
shopifyIdempotencyKey  = createShopifyUsageIdempotencyKey(...)
```

The existing Shopify usage publisher remains responsible for external reporting.

#### WooCommerce

Write:

```text
provider               = WOOCOMMERCE
shopifyReportState     = NOT_APPLICABLE
shopifyEventHandle     = NULL
shopifyIdempotencyKey  = NULL
```

No Shopify event handle lookup is required.

No external provider usage API call is made.

### R9 — Woo local usage must not enter Shopify publication scans

The committed Woo `UsageEvent` must be invisible to existing Shopify usage publication selection because:

```text
shopifyReportState = NOT_APPLICABLE
```

Do not modify the Shopify publisher merely to filter Woo rows if its existing state predicate already excludes `NOT_APPLICABLE`.

Add a regression assertion that a Woo included-usage event cannot be selected as Shopify PENDING/RETRYABLE work.

### R10 — Shop platform is not client/provider payload input

The reporting branch derives only from durable:

```text
commerce.Shop.platform
```

loaded under the existing authenticated/business Shop context.

Do not derive provider reporting from:

- a request payload;
- `observedShopifyPlanHandle`;
- presence/absence of a Shopify handle;
- `providerSubscriptionId` string format;
- Woo webhook JSON.

### R11 — FROZEN continues to block new paid usage

Existing `SubscriptionProjectionStatus.FROZEN` behavior remains unchanged:

```text
EffectiveBillingPolicyError("SUBSCRIPTION_FROZEN")
```

A future Woo `paused` receipt will set FROZEN in the later lifecycle task; once that occurs, this task's policy/reservation path must already deny new recoveries exactly as it does for the current frozen subscription state.

### R12 — Recovery-capacity exhaustion identity includes the current allowance

Where `recovery-billing.service.ts` creates deterministic billing/exhaustion lifecycle identity from the included counter, include the effective/current allowance so a Woo plan switch that changes available capacity produces a distinct current billing-state fingerprint.

The fingerprint must distinguish, for example:

```text
granted=10 currentAllowance=10 committed=6 reserved=0
```

from:

```text
granted=10 currentAllowance=5 committed=6 reserved=0
```

while preserving deterministic output for Shopify rows where the override is null.

Do not change the externally documented support-message schema/version solely for formatting; change only the internal lifecycle input required to avoid stale exhaustion/support state.

### R13 — No fake Shopify evidence for Woo

No Woo included-recovery path may create:

```text
shopifyEventHandle
shopifyIdempotencyKey
ShopifyReportState.PENDING
ShopifyReportState.RETRYABLE
```

or invoke a Shopify provider reporting helper.

The operational `BillingPlan` may still physically contain current legacy Shopify mapping fields because ARCH-027 deliberately does not redesign `BillingPlan`. Those fields are not evidence that Woo usage must be reported to Shopify.

### R14 — No Woo-specific duplicate reservation service

Extend the existing `PaidIncludedRecoveryReservationService`.

Do not create:

```text
WooPaidIncludedRecoveryReservationService
WooEffectiveBillingPolicyResolver
```

or another independent paid capacity ledger.

Woo and Shopify share the same Moda included counter/reservation state. Only provider reporting evidence differs at commit.

### R15 — Structured logging remains shared

If new logs are required, use:

```text
@modainteract/moda-interact-shared/logging
```

Do not create a local generic logger.

No new generic HTTP/queue metrics are required by this task.

Allowed bounded semantic fields may include:

```text
shopId
shopPlatform
billingPeriodId
usageEventId
effectiveAllowance
reservation outcome
```

Do not log customer payloads or provider credentials.

## Work Items

- [ ] Update the nested database gitlink to the accepted ARCH-027-DATABASE-001 main commit and regenerate Prisma.
- [ ] Inspect the accepted generated Prisma field names/types before editing runtime code.
- [ ] Add `currentAllowanceQuantity` / effective allowance semantics to the Background paid included policy projection.
- [ ] Update paid included counter validation to preserve the high-water grant invariant while allowing a downgrade below committed/reserved usage.
- [ ] Update paid included new-reservation availability to use the effective current allowance and floor at zero.
- [ ] Prove existing reserved usage can still commit/release after a downgrade below already-used capacity.
- [ ] Make paid plan Shopify-meter validation conditional on durable `Shop.platform`.
- [ ] Preserve Shopify paid usage-event creation exactly.
- [ ] Create Woo paid included `UsageEvent` rows as local `provider=WOOCOMMERCE`, `shopifyReportState=NOT_APPLICABLE` evidence.
- [ ] Ensure Woo paid commit performs no Shopify event-handle/idempotency helper call.
- [ ] Add a regression test proving Woo local usage is excluded from Shopify publication selection.
- [ ] Include current/effective allowance in deterministic recovery-billing exhaustion identity.
- [ ] Preserve all existing Free lifetime, promotional and purchased-credit priority semantics.
- [ ] Add focused Shopify regression and Woo provider-local accounting tests.

## Interfaces / Contracts

### Database contract

Owner:

`ARCH-027-DATABASE-001`

Consumed fields:

```text
commerce.Shop.platform

billing.BillingPeriodEntitlementCounter.currentAllowanceQuantity

billing.UsageEvent.provider
billing.UsageEvent.shopifyReportState
billing.UsageEvent.shopifyEventHandle
billing.UsageEvent.shopifyIdempotencyKey
```

No new Shared runtime contract is created.

### Effective paid allowance contract

```text
effectiveAllowance =
    currentAllowanceQuantity
    ?? grantedQuantity
```

New reservation admission:

```text
available =
    max(
        effectiveAllowance
        - committedQuantity
        - reservedQuantity
        - forfeitedQuantity,
        0
    )
```

Historical/audit capacity constraint:

```text
committedQuantity
+ reservedQuantity
+ forfeitedQuantity
<= grantedQuantity
```

### Included usage provider evidence

Shopify:

```text
UsageEvent.provider = SHOPIFY
shopifyReportState = PENDING
```

WooCommerce:

```text
UsageEvent.provider = WOOCOMMERCE
shopifyReportState = NOT_APPLICABLE
```

Both represent the same Moda business metric:

```text
UsageMetric.RECOVERY_CONVERSATION
```

## Dependencies

- `ARCH-027-DATABASE-001`

DATABASE-001 must be architect-accepted Complete and the Background nested database gitlink must point to the accepted database main commit before implementation.

This task does not depend on API-005 because it is the **capacity-safety prerequisite** for later Woo paid subscription activation and may execute in parallel with API provider-edge work once the database contract is accepted.

## Enables

None yet.

When the next task is materialized, `ARCH-027-BACKGROUND-002` is expected to depend on both:

```text
ARCH-027-BACKGROUND-001
ARCH-027-API-005
```

before it is allowed to project a Woo paid subscription from durable webhook receipts.

## Acceptance Criteria

- [ ] Paid included policy exposes `grantedQuantity`, nullable `currentAllowanceQuantity` and deterministic `effectiveAllowanceQuantity`.
- [ ] Null `currentAllowanceQuantity` preserves exact Shopify availability semantics.
- [ ] New reservation admission uses `currentAllowanceQuantity ?? grantedQuantity`.
- [ ] Availability floors at zero after a downgrade below already committed/reserved usage.
- [ ] Counter validation still enforces `committed + reserved + forfeited <= granted`.
- [ ] Counter validation does not require committed/reserved usage to fit under the lower current allowance.
- [ ] A pre-existing RESERVED reservation can commit after a downgrade below current usage.
- [ ] A released pre-existing reservation is not re-reserved when the new current allowance has no room.
- [ ] An allowance increase fixture exposes the additional capacity without resetting committed/reserved usage.
- [ ] Effective policy requires the existing Shopify usage-event handle for SHOPIFY paid Shops.
- [ ] Effective policy does not require a Shopify usage-event handle merely to support WOOCOMMERCE local included accounting.
- [ ] Shopify paid commit still writes provider `SHOPIFY`, `PENDING`, Shopify event handle and Shopify idempotency key.
- [ ] Woo paid commit writes provider `WOOCOMMERCE`, `NOT_APPLICABLE`, null Shopify event handle and null Shopify idempotency key.
- [ ] Woo paid commit invokes no Shopify provider/reporting helper.
- [ ] Woo included UsageEvents cannot be selected by the existing Shopify usage publisher.
- [ ] FROZEN subscription policy continues to reject new recoveries.
- [ ] Recovery billing exhaustion identity changes when the effective current allowance changes.
- [ ] Free lifetime, promotional and purchased-credit reservation semantics are unchanged.
- [ ] No Woo receipt, Subscription lifecycle, BillingPeriod rollover or plan-switch writer is implemented.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the current `moda-interact-background/package.json` and task requirements before choosing exact commands.

The supplied source baseline currently declares:

```text
npm test
npm run test:unit
npm run test:integration
npm run build
npm run prisma:validate
npm run prisma:generate
```

Use the actual accepted repository state rather than assuming these remain identical.

Required validation categories:

- [ ] Prisma generation from accepted ARCH-027-DATABASE-001;
- [ ] Prisma validation;
- [ ] repository typecheck/build through the declared production build;
- [ ] targeted lint/changed-file diagnostics required by repository instructions;
- [ ] focused `EffectiveBillingPolicyResolver` current-allowance tests;
- [ ] Shopify null-override regression test;
- [ ] Woo lower-current-allowance availability-floor test;
- [ ] existing-reservation commit-after-downgrade test;
- [ ] released-reservation no-room-after-downgrade test;
- [ ] allowance-increase availability test;
- [ ] malformed negative/non-safe current-allowance rejection tests;
- [ ] invalid `currentAllowanceQuantity > grantedQuantity` fail-closed test;
- [ ] Shopify paid normal-usage-meter requirement regression test;
- [ ] Woo paid policy test that does not require Shopify reporting semantics;
- [ ] Shopify paid commit UsageEvent exact-evidence regression test;
- [ ] Woo paid commit UsageEvent exact local-evidence test;
- [ ] Woo commit negative assertion for Shopify event-handle/idempotency helper usage;
- [ ] existing Shopify usage-publisher selection test proving `NOT_APPLICABLE` Woo rows are excluded;
- [ ] FROZEN paid subscription rejection regression test;
- [ ] deterministic recovery-billing exhaustion identity test including current allowance;
- [ ] focused Free/promotional/purchased priority regression where touched;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization, nested database gitlink and pushed task-branch evidence in the Completion Report.

No Woo provider sandbox/network call is required for this task.

## Stop Condition

After all defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
    -> set task status to review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo webhook receipt reconciliation or any enabled/follow-on work.

## Implementation Notes

This task exists because the **current source would be unsafe to activate for Woo paid merchants as-is**.

Keep the implementation small:

```text
same BillingPeriod counter
same UsageReservation
same UsageEvent business metric

only:
    current allowance admission semantics
    +
    provider-aware external-reporting evidence
```

Do not use this task to redesign the billing domain.

The later Woo lifecycle task is responsible for atomically updating a counter on plan switch:

```text
if targetAllowance > grantedQuantity:
    grantedQuantity = targetAllowance

currentAllowanceQuantity = targetAllowance
version += 1
```

This task only consumes that state correctly.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

- ARCH-027-DATABASE-001 is accepted before implementation.
- ARCH-027 v1 paid Woo billing runs only for `Shop.platform = WOOCOMMERCE`.
- Woo paid included recoveries are locally accounted in Moda and are not reported to Woo as usage events.
- Existing Shopify usage publisher already selects only reportable Shopify states and therefore naturally excludes `NOT_APPLICABLE`.

### Unresolved Issues

None within this bounded capacity/accounting task.

### Architectural Concerns

A future architecture that allows a WooCommerce-platform Shop to use a non-Woo billing provider will require an explicit billing-provider discriminator rather than using `Shop.platform` as the v1 provider-reporting dispatch. ARCH-027 intentionally does not add that broader abstraction.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
