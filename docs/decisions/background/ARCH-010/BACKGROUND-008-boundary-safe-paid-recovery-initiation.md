---
id: ARCH-010-BACKGROUND-008
architecture_id: ARCH-010
title: Make paid recovery initiation safe across the billing-cycle boundary
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 46
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-010-BACKGROUND-002
- ARCH-010-SHARED-008
- ARCH-010-BACKGROUND-019
enables:
- ARCH-010-BACKGROUND-007
created: 2026-09-11
updated: '2026-09-13'
---

# ARCH-010-BACKGROUND-008: Make paid recovery initiation safe across the billing-cycle boundary

## Objective

Prevent a normal paid Shopify-metered recovery from being admitted in one BillingPeriod and actually initiated after that period is closing/expired. Add a five-minute paid-period drain guard, pre-provider revalidation, period-specific included-reservation identity, and a bounded WhatsApp send timeout shorter than the drain window.

This task does not close/open BillingPeriods; BACKGROUND-007 owns rollover.

## Inspect before editing

```text
src/services/effective-billing-policy.service.ts
src/services/recovery-billing.service.ts
src/services/checkout-recovery.service.ts
src/services/paid-included-recovery-reservation.service.ts   # name may differ after BACKGROUND-002
src/services/purchased-recovery-reservation.service.ts
src/services/outbound-whatsapp-admission.service.ts
src/services/whatsapp.service.ts
src/providers/shopify-app-events.provider.ts
src/services/shopify-usage-event-publisher.service.ts
tests/unit/services/effective-billing-policy.service.test.ts
tests/unit/services/recovery-billing.service.test.ts
tests/unit/services/outbound-whatsapp-admission.service.test.ts
tests/unit/services/whatsapp.service.test.ts
package.json
```

Read the implemented BACKGROUND-002 result first. Do not create a second paid included reservation implementation.

## Required Shared constant

Import from the accepted published Shared billing package:

```text
APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS
```

The canonical value is 300000 ms (5 minutes). Do not redeclare a different app-local constant.

## Derived paid period phases

For a mapped ACTIVE paid subscription with exact current BillingPeriod:

```text
ACTIVE:
  now < periodEnd - APP_PRICING_BILLING_PERIOD_DRAIN_WINDOW_MS

DRAINING:
  periodEnd - window <= now < periodEnd

EXPIRED_RECONCILING:
  now >= periodEnd while Subscription still points at that period
```

Do not persist a new SubscriptionProjectionStatus for these phases.

Expose enough typed policy information for RecoveryBillingService to distinguish ACTIVE vs DRAINING. Once the period is expired, subscription-dependent business admission must fail closed with a specific local reason equivalent to:

```text
BILLING_PERIOD_RECONCILIATION_REQUIRED
```

Do not map an expired period to NO_CONTRACT or SYNC_ERROR.

## Paid admission behaviour

### ACTIVE

Keep the final ARCH-010 ordering after BACKGROUND-019:

```text
selected promotional -> period included -> purchased lifetime -> shop-lifetime Free -> recovery blocked
```

### DRAINING

Do not start a new recovery that would create the normal paid recovery-meter App Event in the closing period.

Required routing:

```text
try selected usable promotional campaign
  -> available: allow promotional-funded recovery
  -> unavailable: try purchased lifetime credit
       -> available: allow purchased-credit recovery
       -> unavailable: try shop-lifetime Free credit
            -> available: allow lifetime-Free-funded recovery
            -> unavailable: block with billing-period-closing reason
```

Do not consume included capacity and do not create any overage path during DRAINING. A usable selected promotion is checked first; promotional-, purchased- and lifetime-Free-funded recoveries create no normal paid recovery App Event and may continue in canonical fallback order.

### EXPIRED_RECONCILING

Block all new recovery initiation until the subscription/billing-period reconciliation worker verifies the successor state. If a purchased-credit reservation was created before the expiry but no provider action has started, release it.

## Period-specific included reservation source identity

Amend the BACKGROUND-002 period-included sourceKey so it contains the BillingPeriod identity.

Conceptual form:

```text
paid-included:<billingPeriodId>:<canonical recovery identity>
```

Use the repository's existing deterministic/bounded key conventions; do not leak customer data.

This is required so a recovery whose old-period admission is safely released can later be re-admitted under a different BillingPeriod without colliding with the globally unique `UsageReservation.sourceKey`.

Purchased lifetime source identity remains period-independent.

## Revalidate immediately before provider business action

The current checkout recovery flow admits billing before conversation creation and calls Meta later. That creates a race with `periodEnd`.

Add one explicit billing revalidation hook immediately before `outboundWhatsAppAdmissionService.sendTemplate(...)` (or the exact provider-initiation boundary after integrated refactoring).

Required contract conceptually:

```ts
revalidateBeforeProvider({ admission, recoveryId })
  -> admitted with same/replacement admission
  -> BLOCK NEW RECOVERY ADMISSION
```

Here the blocked result is the capacity/billing-boundary outcome for the not-yet-started recovery; it is not a global merchant execution state.

Algorithm:

1. Free lifetime admission: preserve existing semantics, but current Shop availability still applies.
2. Purchased admission:
   - if current subscription/business execution is still valid, keep it;
   - if current paid period is expired and successor truth is not installed, release before provider and block.
3. Paid included:
   - re-resolve current billing policy;
   - if same period remains ACTIVE, continue;
   - if period changed, DRAINING or EXPIRED, release any old included reservation before provider;
   - call normal `admit()` once to reclassify against current state;
   - accept the replacement only if it is currently valid;
   - never loop repeatedly.
4. If re-admission returns blocked, do not call WhatsApp/Commerce provider work.

The revalidation must occur after any potentially slow local preparation but before the irreversible external provider action.

## WhatsApp send timeout

The current `WhatsAppService` uses bare `fetch()` with no bounded timeout. That permits a provider call started before the drain window to remain in-flight across the cycle boundary.

Add a bounded timeout to Meta message/template requests.

Canonical requirement for this task:

```text
WHATSAPP_SEND_TIMEOUT_MS = 30_000
```

The timeout is Background-local; do not add another Shared package constant.

Use the workspace-supported standard abort mechanism (for example `AbortSignal.timeout`) rather than adding an unrelated timeout package.

A timeout is an **ambiguous** provider outcome, not a definitive rejection. Preserve existing ambiguity semantics; do not release/charge as if Meta definitely rejected the request.

The 30-second timeout must remain strictly less than the five-minute drain window.

## RecoveryBillingService blocked reasons

Extend typed local blocked reasons so tests/callers can distinguish at minimum:

```text
billing-period-closing
billing-period-reconciliation
```

These are local workflow outcomes. Do not expose raw internal error strings to customers.

Checkout recovery should treat them as terminal no-send/no-new-work for that attempt, using existing recovery scheduling/retry semantics rather than throwing an unbounded worker error.

## No synchronous Shopify App Events call in the recovery hot path

Do not solve the boundary by reporting the Shopify billing App Event synchronously before WhatsApp. Preserve asynchronous usage publication.

The drain window plus pre-provider revalidation plus bounded provider call duration are the boundary-safety mechanism.

## Required tests

At minimum prove:

1. ACTIVE paid period still permits included reservation;
2. DRAINING paid period does not reserve included capacity;
3. DRAINING with purchased credit admits purchased recovery;
4. DRAINING without promotional capacity falls through to purchased credit, then lifetime Free when available, and blocks only when all fallback sources are unavailable;
5. EXPIRED period blocks normal recovery initiation;
6. included reservation source key differs across BillingPeriods for the same recovery;
7. duplicate admission inside the same BillingPeriod remains idempotent;
8. pre-provider revalidation with unchanged ACTIVE period preserves admission;
9. pre-provider revalidation after rollover releases old included reservation and may re-admit under new period;
10. pre-provider revalidation entering DRAINING releases old included reservation and falls back to promotional, then purchased FIFO, then lifetime Free; it blocks only when all fallback sources are unavailable;
11. pre-provider revalidation entering EXPIRED releases pre-provider reservation and performs no WhatsApp call;
12. purchased reservation is released if the period expires before provider action and no valid successor entitlement exists;
13. WhatsApp template send passes a 30-second abort timeout;
14. WhatsApp text send passes the same timeout;
15. timeout is treated as ambiguous, not definitive provider rejection;
16. no normal paid recovery UsageEvent is created when boundary revalidation blocks;
17. Free and purchased baseline tests remain passing;
18. no Shopify App Events network call is moved into the recovery hot path.

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:unit
npm run build
git diff --check
```

Run relevant existing integration tests through `npm run test:integration` when their declared infrastructure is available.

## Non-goals

Do not implement:

- BillingPeriod close/open;
- BullMQ boundary scheduling;
- usage-event drain/flush;
- merchant UI;
- top-up purchase UI/server guard;
- upgrade/downgrade/cancellation;
- a Messaging-ingress tenant lookup redesign;
- Admin changes.

## Stop conditions

STOP and return to `moda_architect` if:

- BACKGROUND-002 did not create an explicit period-included reservation that can be released before provider work;
- the recovery flow has no safe pre-provider hook after integrated changes;
- Meta provider calls cannot be bounded below the drain window without changing a cross-repository contract;
- adding period-specific source identity would break an accepted externally-visible idempotency contract.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.


## Final promotional fallback during drain/revalidation

After BACKGROUND-019, DRAINING/pre-provider fallback order is:

```text
promotional -> purchased FIFO -> lifetime Free
```

Paid included is unavailable for new reservation while DRAINING. A usable selected promotion is non-App-Event capacity and may continue under an otherwise executable subscription, exactly like purchased/lifetime Free capacity. Revalidation must never skip promotional and jump directly to purchased.
