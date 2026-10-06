---
id: ARCH-027-BACKGROUND-001
architecture_id: ARCH-027
title: Make Woo recovery accounting and frozen fallback provider-safe
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
enables:
  - ARCH-027-BACKGROUND-002
created: 2026-10-03
updated: 2026-10-06
---

# Make Woo recovery accounting and frozen fallback provider-safe

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Make the existing Background recovery-accounting path safe for Woo before recurring Woo lifecycle activation is implemented.

This task owns three related prerequisites:

1. **paid included allowance semantics**
   ```text
   effectiveAllowance =
       currentAllowanceQuantity ?? grantedQuantity

   available =
       max(
           effectiveAllowance
           - committedQuantity
           - reservedQuantity
           - forfeitedQuantity,
           0
       )
   ```

2. **provider-correct UsageEvent attribution for every recovery capacity source**
   ```text
   SHOPIFY Shop     -> UsageEvent.provider = SHOPIFY
   WOOCOMMERCE Shop -> UsageEvent.provider = WOOCOMMERCE
   ```

3. **Woo payment-pause FROZEN fallback**
   ```text
   paid included allowance -> unavailable for new recovery
   active promotional credits -> existing eligibility
   purchased top-up credits -> usable
   lifetime Free credits -> usable
   ```

   Verified Woo cancellation is not a FROZEN state: BACKGROUND-002 keeps the prepaid paid Subscription ACTIVE with `cancelAtPeriodEnd=true`; normal paid capacity policy continues until prepaid entitlement actually ends, after which the Subscription returns to Free.

The task does not consume Woo billing receipts or change Subscription lifecycle state.

It prepares the existing recovery engine so BACKGROUND-002 can safely mark a Woo subscription paid/FROZEN without either creating Shopify reporting work for Woo, globally blocking credits the merchant already owns, or granting paid included recovery after the provider period is no longer current.

## Context

The current Background implementation is still Shopify-shaped in several ways that matter to ARCH-027:

1. `EffectiveBillingPolicyResolver` treats every `FROZEN` subscription as a hard error before fallback capacity can be considered.
2. `ShopExecutionEligibilityService` and `PendingRecoveryCandidateService` treat FROZEN as a Shop-wide execution denial.
3. `RecoveryBillingService` hard-blocks `EXPIRED_RECONCILING` paid periods before promotional/purchased/lifetime-Free fallback is attempted.
4. `PaidIncludedRecoveryReservationService.commit()` creates Shopify-reportable provider evidence.
5. The Free, promotional and purchased recovery commit services create `UsageEvent` rows with `shopifyReportState=NOT_APPLICABLE` but currently rely on the Prisma provider default, which would incorrectly label Woo recovery consumption as `SHOPIFY`.
6. Paid included availability currently reads `grantedQuantity` rather than the new mutable current allowance.

Woo provider behavior now fixed by architecture is different:

```text
paused
    -> recurring paid entitlement frozen
    -> provider may retry renewal

renewed
    -> successful financial evidence / provider coverage reconciliation
    -> does not itself reset Moda included allowance

canceled
    -> prepaid paid entitlement remains ACTIVE until the signed provider end

prepaid term end
    -> current Subscription returns to Free
```

While Woo is FROZEN because the provider recurring contract is paused/payment-recovering, already-owned non-recurring capacity remains usable. A verified scheduled cancellation remains paid/ACTIVE until the prepaid term actually ends. BACKGROUND-006 owns later exact-30-day allowance boundaries and the durable cancellation-end safety net.

The task relies on durable:

```text
Shop.platform = SHOPIFY | WOOCOMMERCE
```

as the bounded ARCH-027 v1 dispatch evidence.

This remains a minimal provider-aware adaptation of the existing recovery domain, not a generic billing-provider framework.

## Scope

Modify only `moda-interact-background` production/tests needed for:

- effective paid allowance/current allowance;
- provider-aware recovery UsageEvent attribution;
- provider-aware FROZEN execution gating;
- fallback recovery source selection while Woo paid included entitlement is unavailable;
- deterministic exhaustion identity.

Expected directly relevant production areas include:

```text
src/services/effective-billing-policy.service.ts
src/services/shop-execution-eligibility.service.ts
src/services/pending-recovery-candidate.service.ts
src/services/recovery-billing.service.ts
src/services/paid-included-recovery-reservation.service.ts
src/services/free-recovery-reservation.service.ts
src/services/promotional-recovery-reservation.service.ts
src/services/purchased-recovery-reservation.service.ts
src/services/outbound-whatsapp-admission.service.ts
```

Exact files may differ after inspection.

Update the nested database gitlink to accepted `ARCH-027-DATABASE-001` and regenerate Prisma.

### Explicitly retained boundaries

This task MUST NOT:

- process Woo billing webhook receipts;
- create/switch/freeze/cancel a Subscription;
- open/renew/close a Woo BillingPeriod;
- buy a new top-up while FROZEN;
- reconcile a Woo top-up/refund;
- call Woo;
- add a new queue/provider framework.

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

### R1 — Current allowance is the paid included spend ceiling

Every new paid-included reservation uses:

```text
effectiveAllowance =
    currentAllowanceQuantity ?? grantedQuantity

available =
    max(
        effectiveAllowance
        - committedQuantity
        - reservedQuantity
        - forfeitedQuantity,
        0
    )
```

### R2 — Preserve the high-water grant invariant

Continue to require:

```text
committedQuantity + reservedQuantity + forfeitedQuantity <= grantedQuantity
```

When non-null:

```text
0 <= currentAllowanceQuantity <= grantedQuantity
```

Do not require committed/reserved usage to fit under a later lower current allowance.

### R3 — Existing paid reservations survive an allowance downgrade

A lower current allowance gates **new** paid included reservations. Existing RESERVED included capacity may still COMMIT or RELEASE.

### R4 — Upgrade exposes new capacity without usage reset

Raising current allowance makes the difference available without resetting committed/reserved/forfeited or changing BillingPeriod identity.

### R5 — Shopify null override is unchanged

For Shopify, `currentAllowanceQuantity = NULL` remains valid and effective allowance is `grantedQuantity`.

### R6 — Effective policy exposes platform/status/current allowance

The effective recovery policy must carry enough durable state to distinguish `Shop.platform`, `Subscription.status`, paid period phase and granted/current allowance.

### R7 — Shopify FROZEN remains a hard execution block

For Shopify FROZEN preserve existing `SUBSCRIPTION_FROZEN` execution denial.

### R8 — Woo payment-pause FROZEN is not a Shop-wide recovery block

For Woo payment-pause FROZEN, execution gating must allow the recovery/conversation path to reach billing-capacity selection. `EffectiveBillingPolicyResolver` returns a bounded Woo FROZEN policy instead of throwing the generic frozen error.

### R9 — Woo payment-pause FROZEN capacity order

For Woo payment-pause FROZEN, new recovery admission tries only:

```text
active promotional
-> purchased
-> lifetime Free
-> capacity exhausted
```

It MUST NOT reserve from paid `INCLUDED_RECOVERY_CREDITS`.

### R10 — Expired Woo provider period also falls back

When a Woo paid current provider period is no longer active/current while lifecycle evidence converges, do not grant paid included capacity and do not globally block before fallback sources are tried.

Shopify expired-period behavior remains unchanged.

### R11 — Revalidation preserves valid fallback admissions across freeze races

Promotional/purchased/lifetime-Free admissions may remain valid if Woo freezes before provider send. A paid-included admission encountering Woo FROZEN/expired period must be released and re-admitted through fallback sources.

### R12 — Pending candidate scheduling is platform-aware

Remove/replace direct platform-agnostic FROZEN discard paths that would discard Woo candidates before fallback capacity can be evaluated. Shopify behavior remains unchanged.

### R13 — Every recovery UsageEvent has explicit provider attribution

For paid included, promotional, purchased and lifetime-Free recovery commits:

```text
Shopify -> provider=SHOPIFY
Woo     -> provider=WOOCOMMERCE
```

Do not rely on the database default.

### R14 — Paid included external reporting remains provider-specific

Shopify paid included remains PENDING/reportable with Shopify event/idempotency evidence. Woo paid included is `NOT_APPLICABLE` with null Shopify reporting fields.

### R15 — Non-reportable recovery sources stay non-reportable

Free/promotional/purchased recovery remains `shopifyReportState=NOT_APPLICABLE` on both platforms; only the explicit provider discriminator differs.

### R16 — Exhaustion identity includes current allowance

Include effective/current allowance in deterministic paid-capacity exhaustion/support identity.

### R17 — No duplicate Woo capacity ledger

Reuse existing counters/reservation services.

### R18 — Structured logging remains shared

Use the Shared structured logger and bounded identifiers only.

## Work Items

- [ ] Update database gitlink and regenerate Prisma.
- [ ] Add current-allowance availability including forfeited quantity.
- [ ] Load durable Shop.platform in effective policy/execution gating.
- [ ] Keep Shopify FROZEN hard-block behavior.
- [ ] Allow Woo FROZEN to reach capacity selection.
- [ ] Skip Woo paid included while FROZEN or provider period is expired/pending lifecycle convergence.
- [ ] Preserve promotional -> purchased -> lifetime-Free fallback.
- [ ] Make pre-provider revalidation release paid included and retain/re-admit fallback capacity correctly.
- [ ] Remove direct platform-agnostic Woo FROZEN candidate discard.
- [ ] Explicitly write UsageEvent.provider for paid/free/promotional/purchased recovery commits.
- [ ] Preserve Shopify paid App Event behavior.
- [ ] Prove Woo NOT_APPLICABLE events cannot enter Shopify publishing.
- [ ] Update deterministic exhaustion identity.
- [ ] Add focused cross-provider regression tests.

## Interfaces / Contracts

### Effective paid allowance

```text
effectiveAllowance = currentAllowanceQuantity ?? grantedQuantity
available = max(effectiveAllowance - committed - reserved - forfeited, 0)
```

### Woo FROZEN / expired-period fallback

```text
paid included -> unavailable
promotion     -> eligible if active
purchased     -> eligible if available
lifetime Free -> eligible if available
```

### Recovery UsageEvent provider evidence

```text
Shopify recovery -> provider=SHOPIFY
Woo recovery     -> provider=WOOCOMMERCE
```

Only Shopify paid included usage is externally reportable.

## Dependencies

- `ARCH-027-DATABASE-001`

DATABASE-001 must be architect-accepted Complete and the Background nested database gitlink must point to the accepted database main commit before implementation.

This task does not depend on API-005 because it is the **capacity-safety prerequisite** for later Woo paid subscription activation and may execute in parallel with API provider-edge work once the database contract is accepted.

## Enables

- `ARCH-027-BACKGROUND-002`

## Acceptance Criteria

- [ ] Paid included availability uses currentAllowance fallback and subtracts committed/reserved/forfeited.
- [ ] Shopify null current allowance preserves existing behavior.
- [ ] Shopify FROZEN still blocks execution.
- [ ] Woo FROZEN reaches capacity selection rather than being discarded globally.
- [ ] Woo FROZEN cannot reserve paid included capacity.
- [ ] Woo FROZEN can use active promotional, purchased and lifetime-Free capacity.
- [ ] Woo expired provider period cannot grant paid included capacity while lifecycle evidence is pending, but fallback capacity remains usable.
- [ ] Paid admission then freeze-before-send releases/re-admits safely.
- [ ] Pending-candidate scheduling is platform-aware.
- [ ] Shopify paid included usage remains provider SHOPIFY + PENDING.
- [ ] Woo paid included usage is provider WOOCOMMERCE + NOT_APPLICABLE.
- [ ] Woo promotional, purchased and lifetime-Free recovery usage explicitly writes provider WOOCOMMERCE.
- [ ] Shopify non-reportable recovery sources explicitly remain provider SHOPIFY.
- [ ] Woo recovery UsageEvents cannot enter Shopify publication scans.
- [ ] No Woo lifecycle writer is implemented in this task.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Required categories include:

- [ ] Prisma generate/validate;
- [ ] build/typecheck/lint;
- [ ] current-allowance + forfeited availability tests;
- [ ] Shopify FROZEN hard-block regression;
- [ ] Woo FROZEN promotional/purchased/lifetime-Free fallback tests;
- [ ] Woo FROZEN no-paid-included test;
- [ ] freeze-before-send revalidation/re-admission test;
- [ ] pending-candidate Woo FROZEN not-discarded test;
- [ ] pending-candidate Shopify FROZEN discarded regression;
- [ ] provider attribution tests for paid/free/promotional/purchased commits on both platforms;
- [ ] Shopify App Event reporting regression;
- [ ] Woo NOT_APPLICABLE publication exclusion test;
- [ ] exhaustion identity test;
- [ ] `git diff --check`;
- [ ] dedicated worktree/submodule/push evidence.

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
- Woo recovery consumption is locally accounted in Moda; paid included, promotional, purchased and lifetime-Free UsageEvents are explicitly provider=WOOCOMMERCE and are not reported through Shopify App Events.
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
