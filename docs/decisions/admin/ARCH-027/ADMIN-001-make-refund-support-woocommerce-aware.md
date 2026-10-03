---
id: ARCH-027-ADMIN-001
architecture_id: ARCH-027
title: Make recovery-credit refund support WooCommerce-aware
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-027-ADMIN-002
created: 2026-10-04
updated: 2026-10-04
---

# Make recovery-credit refund support WooCommerce-aware

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Adapt the **existing** Platform Admin recovery-credit refund queue to understand Woo provider semantics safely.

This task does not create a new Woo support console.

It extends the existing:

```text
Billing
  -> Refund requests
```

surface so operators can correctly distinguish and inspect:

```text
Shopify automatic correction refunds
Shopify manual-provider fallback refunds
Woo PROVIDER_ACTION_REQUIRED refunds
Woo NEEDS_ATTENTION refunds
Woo completed webhook-confirmed refunds
Woo refunded webhook receipts that cannot yet be matched to a local refund hold
```

The most important safety rule is:

> The existing Admin manual provider-evidence settlement action is Shopify-only. A Woo `PROVIDER_ACTION_REQUIRED` refund must never be manually completed through that generic form.

Woo refund settlement is owned by:

```text
BACKGROUND-005
    signed refunded webhook
    -> exact provider transaction/refund evidence
    -> COMPLETED or NEEDS_ATTENTION
```

Admin is a support/audit surface for that workflow.

This task also adds a **read-only Woo refund receipt attention queue** for exceptional provider evidence such as:

```text
WOO_REFUND_REQUEST_NOT_FOUND
WOO_REFUND_PROVIDER_AMOUNT_NOT_READY
WOO_REFUND_PROVIDER_TRANSACTION_NOT_FOUND
WOO_REFUND_PROVIDER_EVIDENCE_CONFLICT
WOO_REFUND_LOCAL_STATE_CONFLICT
```

It deliberately does **not** invent or complete a local refund row from an unmatched provider refund.

The explicit mutation/recovery policy for exceptional external refunds belongs to the follow-on `ARCH-027-ADMIN-002` task.

## Context

The supplied source baseline already contains a mature refund support surface:

```text
src/app/(protected)/billing/page.tsx
src/components/admin/recovery-credit-refunds.tsx
src/lib/admin/recovery-credit-refunds.ts
src/lib/admin/recovery-credit-refund-settlement.ts
src/app/actions/recovery-credit-refunds.ts
```

Current behavior is Shopify-shaped.

### Source finding 1 — manual settlement would be unsafe for Woo as-is

Current `SettlementActions` renders the provider-evidence form whenever:

```text
status = PROVIDER_ACTION_REQUIRED
automaticCorrectionUsageEventId = null
```

and the settlement service accepts the same shape.

There is currently no billing-provider discriminator in that UI/action guard.

After ARCH-027, a normal Woo refund prepared by BACKGROUND-005 has exactly:

```text
provider = WOOCOMMERCE
status = PROVIDER_ACTION_REQUIRED
automaticCorrectionUsageEventId = null
```

Therefore, without this task, the existing Admin form would incorrectly allow a SUPER_ADMIN to manually record provider evidence and complete a Woo refund before the signed Woo `refunded` webhook is reconciled.

ADMIN-001 must close that path before Woo refunds are operational.

### Source finding 2 — existing Admin types assume Shopify refund provenance is non-null

Current Admin projection types assume fields such as:

```text
billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
purchase.billingPeriod
purchase.shopifyPlanHandleSnapshot
purchase.shopifyEventHandleSnapshot
```

are always present.

ARCH-027 intentionally permits Woo Free top-up/refund provenance to be null.

The Admin read model must become provider-aware rather than fabricating Shopify context.

### Source finding 3 — completed Woo refunds are not "manual fallback"

The current UI classifies completed refunds with:

```text
automaticCorrectionUsageEventId = null
providerActionKind = REFUND | CREDIT
```

as manually completed.

BACKGROUND-005 completes Woo refunds from signed webhook evidence with:

```text
provider = WOOCOMMERCE
providerActionKind = REFUND
providerConfirmedByPlatformAdminId = null
```

That is **automated provider evidence**, not a manual Admin settlement.

The UI must represent it correctly.

### Source finding 4 — unmatched provider refunds need operator visibility before recovery mutation

BACKGROUND-005 intentionally leaves a Woo `refunded` receipt unprocessed when no local Moda refund hold exists:

```text
processingError = WOO_REFUND_REQUEST_NOT_FOUND
processedAt = null
```

That is safer than fabricating a refund after provider money has already moved, but it means Platform Admin needs a bounded triage view.

ADMIN-001 surfaces that evidence read-only.

## Scope

Modify only `moda-interact-admin` production/tests required for:

1. provider-aware refund queue/list/detail projection;
2. provider filter/presentation;
3. Woo refund workflow guidance;
4. Shopify-only protection of the existing manual settlement mutation;
5. Woo webhook-confirmed completed-refund presentation;
6. read-only Woo refund receipt-attention queue and detail.

Expected implementation areas:

```text
src/lib/admin/
  types.ts
  recovery-credit-refunds.ts
  recovery-credit-refund-settlement.ts
  woo-refund-receipt-attention.ts

src/components/admin/
  recovery-credit-refunds.tsx
  woo-refund-receipt-attention.tsx

src/app/(protected)/billing/page.tsx
src/app/actions/recovery-credit-refunds.ts

src/i18n/catalogue or accepted admin translation files
tests/
```

Exact filenames must follow the accepted Admin structure.

Update the nested `database/` gitlink to the newest compatible architect-accepted ARCH-027 database main commit and regenerate Prisma before source changes.

## Out of Scope

- Creating a new pricing editor.
- Changing MerchantPricingPlan/UsageEvent economics.
- Woo refund provider initiation.
- Woo credentials.
- Calling Woo APIs.
- Manually completing a normal Woo PROVIDER_ACTION_REQUIRED refund.
- Creating a RecoveryCreditRefund for an unmatched provider receipt.
- Adjusting purchase/counter quantities for unmatched/mismatched Woo refunds.
- Resolving NEEDS_ATTENTION automatically.
- Merchant-facing refund UI.
- Background refund reconciliation.
- Database schema/migration edits other than advancing the accepted database gitlink.
- Gateway/system-test work.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Reuse the existing Billing refund tab

Do not create another Admin page/navigation destination.

Extend the existing:

```text
/billing?view=refunds
```

surface.

The existing refund queue and detail drawer remain the primary support workflow.

Add Woo-specific evidence progressively inside that surface.

### R2 — Refund projection includes provider

Add to the Admin refund item/detail projection:

```text
provider
```

with accepted values:

```text
SHOPIFY
WOOCOMMERCE
```

Also select purchase provider/evidence fields required to explain the refund safely.

Queue rows display a bounded provider label:

```text
Shopify
Woo Marketplace
```

Do not infer provider from nullable Shopify fields.

### R3 — Add a provider filter

Add an optional refund queue filter:

```text
refundProvider
```

with exactly:

```text
ALL
SHOPIFY
WOOCOMMERCE
```

Default:

```text
ALL
```

Filtering is database-side:

```text
RecoveryCreditRefund.provider
```

and composes with the existing queue-status filter.

Preserve current:

```text
refundStatus
refundPage
```

query behavior.

Changing provider/status resets `refundPage`.

### R4 — Make Woo-nullable provenance actually nullable in Admin types

Update Admin projection/types so accepted Woo nulls are represented exactly:

```text
billingPeriodIdSnapshot: string | null
providerSubscriptionIdSnapshot: string | null
planHandleSnapshot: string | null
eventHandleSnapshot: string | null
```

and where the accepted purchase schema is nullable:

```text
purchase.billingPeriod: ... | null
purchase.shopifyPlanHandleSnapshot: string | null
purchase.shopifyEventHandleSnapshot: string | null
purchase.providerSubscriptionIdSnapshot: string | null
```

Do not insert placeholder Shopify values merely to satisfy TypeScript.

### R5 — Provider-specific settlement route classification

Classify each refund into one of these presentation routes.

#### Shopify automatic correction

```text
provider = SHOPIFY
automaticCorrectionUsageEventId != null
```

Preserve current automatic evidence UI.

#### Shopify manual fallback

```text
provider = SHOPIFY
status = PROVIDER_ACTION_REQUIRED
automaticCorrectionUsageEventId = null
```

Preserve the existing explicit SUPER_ADMIN provider-evidence form.

#### Woo provider-dashboard action required

```text
provider = WOOCOMMERCE
status = PROVIDER_ACTION_REQUIRED
```

Render Woo-specific guidance, not the generic manual evidence form.

#### Woo provider attention

```text
provider = WOOCOMMERCE
status = NEEDS_ATTENTION
```

Render expected vs observed provider evidence and the bounded reason.

#### Woo webhook-confirmed completion

```text
provider = WOOCOMMERCE
status = COMPLETED
providerConfirmedByPlatformAdminId = null
providerActionKind = REFUND
```

Render as:

```text
Woo webhook confirmed
```

not "manual completion."

### R6 — Woo PROVIDER_ACTION_REQUIRED guidance is explicit

For a Woo refund in:

```text
PROVIDER_ACTION_REQUIRED
```

display:

```text
final refundable credits
expected provider amount/currency
purchase provider amount/currency
hold/request timestamps
```

and merchant/operator guidance equivalent to:

> Moda has frozen the refund amount. Complete/approve the corresponding SaaS refund in Woo's vendor dashboard under SaaS Apps → Pending Refunds. Moda will complete the local refund only after the signed refunded webhook is reconciled.

Do not claim the Admin console itself can approve the Woo refund.

Do not include a guessed external vendor-dashboard URL.

### R7 — Normal Woo refunds must not render the generic manual settlement form

`SettlementActions` / equivalent must require:

```text
refund.provider = SHOPIFY
```

in addition to the existing manual-fallback predicates.

For:

```text
provider = WOOCOMMERCE
```

there is no:

```text
providerReference input
providerAmount input
providerCurrency input
manual "Record provider evidence" submit
```

for normal settlement.

### R8 — Server-side manual settlement is Shopify-only too

UI hiding is insufficient.

`recordRecoveryCreditProviderEvidence()` must fail closed unless:

```text
refund.provider = SHOPIFY
```

while preserving every existing authorization rule:

```text
requirePlatformAdminMutation()
role = SUPER_ADMIN
explicit confirmed checkbox
PROVIDER_ACTION_REQUIRED
automaticCorrectionUsageEventId = null
```

A crafted Server Action request with a Woo refund ID must not complete or mutate the Woo refund.

Use a bounded error such as:

```text
Manual provider settlement is Shopify-only.
```

Do not mutate the refund/purchase/counter.

### R9 — Shopify regression is exact

Existing Shopify support semantics remain unchanged:

- automatic correction evidence remains visible;
- manual fallback remains SUPER_ADMIN-only;
- provider amount mismatch still moves to NEEDS_ATTENTION according to existing logic;
- completion audit/system message behavior remains unchanged;
- App Event links/evidence remain Shopify-only.

Do not make Shopify fields nullable in presentation where the database contract still requires them for Shopify; only the cross-provider TypeScript shape becomes nullable.

### R10 — Woo completed refund presentation

For webhook-completed Woo refunds, display:

```text
providerReference
providerActionKind
providerAmount/providerCurrency
providerConfirmedAt
finalCreditQuantity
expectedProviderAmount/expectedProviderCurrency
completedAt
```

with provider-aware labels.

Because this is an internal support console, the bounded provider reference may be shown.

Do not show the complete raw Woo webhook payload.

### R11 — Woo NEEDS_ATTENTION presentation

For a Woo refund with:

```text
status = NEEDS_ATTENTION
```

display at minimum:

```text
reason
finalCreditQuantity
expectedProviderAmount / expectedProviderCurrency
providerAmount / providerCurrency
providerReference
providerConfirmedAt
purchase current/reserved amounts
```

Known reason:

```text
WOO_PROVIDER_REFUND_AMOUNT_MISMATCH
```

gets explicit operator copy:

> Woo reports a refund amount different from Moda's frozen expected amount. Credits remain held. Do not manually complete this refund until the discrepancy is resolved.

Unknown Woo reason is shown as a bounded code plus generic support warning.

No local quantity/counter mutation is offered in ADMIN-001.

### R12 — Provider-specific provenance section

For Woo:

- label `planHandleSnapshot` / `eventHandleSnapshot` as not applicable when null;
- do not render headings implying they are Woo identifiers;
- `billingPeriodIdSnapshot = null` is valid for Free-plan top-up refunds;
- `providerSubscriptionIdSnapshot = null` is valid;
- purchase `billingPeriod = null` is valid.

Show useful Woo acquisition evidence:

```text
purchase provider amount/currency
provider valuation confirmed at
bounded provider price snapshot
purchase provider reference when available
```

The existing 2,000-character bounded JSON snapshot display may be retained for Platform Admin if it contains no secret/customer data, but the UI must label it as provider acquisition evidence rather than Shopify price evidence.

### R13 — Add a Woo refund receipt-attention read model

Add a bounded Admin read model for unprocessed Woo charge refund receipts.

Select only:

```text
topic = saas_billing_contract.refunded
processedAt = null
normalizedPayload has top-level `charge`
processingError starts with "WOO_REFUND_"
```

Page size:

```text
20
```

Maximum selectable page size:

```text
50
```

Order:

```text
receivedAt DESC,
id DESC
```

This view is Platform Admin read-only.

### R14 — Receipt attention projection is bounded and safe

Project only:

```text
receiptId
receivedAt
providerContractId
processingError

providerTransactionId | null
providerTransactionAmount | null
providerAmountRefunded | null

matchedOperationId | null
matchedPurchaseId | null
matchedPurchaseStatus | null
matchedPurchaseCurrentAmount | null
matchedPurchaseReservedAmount | null
matchedRefundId | null
matchedRefundStatus | null
```

Do not expose:

```text
full normalizedPayload
transaction URL
customer/payment data
webhook signature
Woo credentials
```

The provider transaction/refund amount may be parsed server-side from the signed durable provider snapshot for support display only.

### R15 — Receipt correlation is read-only and deterministic

For an attention receipt:

```text
providerContractId
    -> ONE_TIME_CHARGE WooCommerceBillingOperation
    -> recoveryCreditPurchaseId
    -> latest RecoveryCreditRefund
```

Do not mutate any correlated record.

If correlation is ambiguous:

```text
matchedOperationId = null
```

and show a bounded:

```text
Ambiguous local charge correlation
```

support message.

Do not guess a purchase from amount or Shop/domain.

### R16 — Surface unmatched provider refund prominently

For:

```text
processingError = WOO_REFUND_REQUEST_NOT_FOUND
```

render an explicit warning equivalent to:

> Woo reports provider money refunded for this charge, but Moda has no corresponding local RecoveryCreditRefund hold. Do not create or complete a refund manually from this screen. Escalate for exceptional recovery.

Show:

```text
provider contract
provider refund amount evidence
matched purchase when uniquely available
```

but no mutation action.

This is the intentional safety state from BACKGROUND-005.

### R17 — Other Woo refund processing errors have bounded operator copy

Map known errors such as:

```text
WOO_REFUND_PROVIDER_AMOUNT_NOT_READY
WOO_REFUND_PROVIDER_TRANSACTION_NOT_FOUND
WOO_REFUND_PROVIDER_TRANSACTION_AMBIGUOUS
WOO_REFUND_HOLD_NOT_READY
WOO_REFUND_LOCAL_STATE_CONFLICT
WOO_REFUND_PROVIDER_EVIDENCE_CONFLICT
```

to concise support descriptions.

Do not render raw exception/database text.

The literal bounded processingError code may also be displayed because this is an internal Platform Admin support surface.

### R18 — Receipt attention lives inside Refund requests

Add a progressive disclosure section within:

```text
Billing -> Refund requests
```

such as:

```text
Woo provider receipt attention
```

with count/table/detail.

Do not create another top-level Admin navigation item.

A refund row/detail remains the primary support entity when one exists.

### R19 — No mutation from the receipt attention queue

ADMIN-001 MUST NOT offer:

```text
Create local refund
Complete refund
Adjust credit quantity
Adjust counter
Mark receipt processed
Retry provider refund
```

from unmatched/attention receipt evidence.

`ARCH-027-ADMIN-002` will own any explicit exceptional recovery mutation after its exact safe invariants are separately reviewed.

### R20 — Platform Admin authorization remains unchanged

Reads use the existing:

```text
requirePlatformAdminRead()
```

boundary.

Existing Shopify manual settlement remains:

```text
SUPER_ADMIN
```

only.

No Woo-specific role bypass is introduced.

### R21 — Structured audit and secrets

ADMIN-001 adds no new financial mutation, so it requires no new mutation audit event.

Existing manual Shopify settlement audit remains unchanged.

Never log:

```text
raw Woo payload
Woo credentials
webhook signature
payment/customer data
```

Bounded internal identifiers/error codes are allowed.

## Work Items

- [ ] Update the Admin nested database gitlink to accepted ARCH-027 database main and regenerate Prisma.
- [ ] Add refund `provider` to Admin list/detail projections.
- [ ] Make Woo-valid provenance fields nullable in Admin types/UI.
- [ ] Add exact ALL/SHOPIFY/WOOCOMMERCE refund provider filter.
- [ ] Make queue/detail settlement-route classification provider-aware.
- [ ] Preserve Shopify automatic correction UI.
- [ ] Preserve Shopify manual fallback UI/action.
- [ ] Hide generic manual settlement controls for every Woo refund.
- [ ] Add server-side `provider=SHOPIFY` guard to manual provider-evidence mutation.
- [ ] Add Woo PROVIDER_ACTION_REQUIRED vendor-dashboard guidance.
- [ ] Add Woo NEEDS_ATTENTION expected-vs-actual provider evidence presentation.
- [ ] Present webhook-confirmed Woo COMPLETED refunds distinctly from manual completion.
- [ ] Add provider-aware nullable provenance rendering.
- [ ] Add bounded read-only Woo refund receipt-attention query/projection.
- [ ] Add receipt-attention section inside the existing Refund requests surface.
- [ ] Add explicit unmatched-provider-refund warning with no mutation.
- [ ] Add bounded operator copy for known WOO_REFUND processing errors.
- [ ] Add focused authorization/provider/regression/security tests.

## Interfaces / Contracts

### Refund business state

Owners:

```text
ARCH-027-API-006
ARCH-027-BACKGROUND-005
```

Consumed:

```text
RecoveryCreditRefund.provider
RecoveryCreditRefund.status
finalCreditQuantity
expectedProviderAmount/currency
providerReference
providerActionKind
providerAmount/currency
providerConfirmedAt
providerConfirmedByPlatformAdminId
reason
```

### Woo provider receipt attention

Owner:

`ARCH-027-DATABASE-001`

Producer/processor:

```text
API-005 -> durable receipt
BACKGROUND-005 -> processingError / processedAt
```

ADMIN-001 reads:

```text
WooCommerceBillingWebhookReceipt
topic = refunded
processedAt = null
processingError LIKE 'WOO_REFUND_%'
```

### Existing manual settlement mutation

Owner:

`moda_admin`

After ADMIN-001 it is explicitly:

```text
SHOPIFY only
SUPER_ADMIN only
```

It is not a Woo settlement mechanism.

## Dependencies

- `ARCH-027-BACKGROUND-005`

BACKGROUND-005 must be architect-accepted Complete before ADMIN-001 becomes Ready so:

- Woo PROVIDER_ACTION_REQUIRED semantics are fixed;
- Woo webhook-confirmed COMPLETED semantics are fixed;
- NEEDS_ATTENTION amount-mismatch evidence is fixed;
- unmatched provider refund processing-error codes are stable.

Through BACKGROUND-005 this task also depends on accepted ARCH-027 database provider/refund/receipt fields.

## Enables

- `ARCH-027-ADMIN-002`

ADMIN-002 owns only the deterministic exceptional mutations proven safe after ADMIN-001:

```text
existing Woo NEEDS_ATTENTION provider over-refund
    -> explicitly accept over-refund
    -> remove the already-frozen full credit quantity

unmatched WOO_REFUND_REQUEST_NOT_FOUND
    -> only when one purchase/transaction is proven
    -> purchase is ACTIVE/unreserved
    -> provider refunded at least the amount required for all currently unused credits
    -> create one audited ADMIN recovery refund
```

Provider under-refund, ambiguous provider identity, active reservations and other non-deterministic cases remain non-mutating support exceptions.

## Acceptance Criteria

- [ ] Existing Billing -> Refund requests surface remains the single Admin refund support destination.
- [ ] Refund queue/detail exposes provider and exact ALL/SHOPIFY/WOOCOMMERCE filter.
- [ ] Woo-nullable billing-period/provider/Shopify provenance no longer causes invalid TypeScript/UI assumptions.
- [ ] Shopify automatic correction presentation is unchanged.
- [ ] Shopify manual PROVIDER_ACTION_REQUIRED settlement remains SUPER_ADMIN-only and unchanged.
- [ ] Woo PROVIDER_ACTION_REQUIRED never renders the generic manual provider-evidence form.
- [ ] Crafted manual settlement action against a Woo refund is rejected server-side with zero refund/purchase/counter mutation.
- [ ] Woo PROVIDER_ACTION_REQUIRED clearly tells operators to use Woo SaaS Pending Refunds/vendor workflow and wait for signed reconciliation.
- [ ] Woo NEEDS_ATTENTION shows final credits, expected provider money and observed provider money/reference without offering speculative completion.
- [ ] `WOO_PROVIDER_REFUND_AMOUNT_MISMATCH` has explicit safe operator copy.
- [ ] Webhook-completed Woo refund is presented as provider/webhook-confirmed, not manual fallback.
- [ ] Woo Free refund with null billingPeriodIdSnapshot/providerSubscriptionIdSnapshot renders normally.
- [ ] Shopify-only handle fields are not mislabeled as Woo identities.
- [ ] A bounded Woo refund receipt-attention queue is present inside Refund requests.
- [ ] Attention queue selects only unprocessed refunded charge receipts with WOO_REFUND processing errors.
- [ ] Attention projection never renders full provider payload/customer/payment data.
- [ ] `WOO_REFUND_REQUEST_NOT_FOUND` is prominently identified as provider money moved with no local refund hold.
- [ ] Unmatched provider refund attention exposes no create/complete/counter mutation action.
- [ ] Ambiguous contract correlation fails closed/read-only.
- [ ] Existing Platform Admin read and SUPER_ADMIN mutation authorization remain intact.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect accepted `moda-interact-admin/package.json` / repository instructions before choosing exact commands.

Required validation categories:

- [ ] Prisma generate/validate against accepted ARCH-027 database gitlink;
- [ ] repository typecheck;
- [ ] targeted lint/changed-file diagnostics;
- [ ] production build;
- [ ] existing Admin billing/refund security suites remain green;
- [ ] provider projection/filter tests;
- [ ] Woo nullable refund provenance projection/detail tests;
- [ ] Shopify automatic correction presentation regression test;
- [ ] Shopify manual fallback form/action regression test;
- [ ] Woo PROVIDER_ACTION_REQUIRED no-manual-form test;
- [ ] crafted Woo manual settlement server-action rejection test;
- [ ] Woo webhook-completed classification test;
- [ ] Woo NEEDS_ATTENTION expected-vs-provider amount presentation test;
- [ ] WOO_PROVIDER_REFUND_AMOUNT_MISMATCH copy test;
- [ ] Woo Free null-period refund detail test;
- [ ] refunded receipt attention query filter/order/page tests;
- [ ] unmatched WOO_REFUND_REQUEST_NOT_FOUND projection test;
- [ ] unique operation/purchase/refund correlation test;
- [ ] ambiguous operation correlation fail-closed test;
- [ ] provider transaction/refunded amount bounded extraction test;
- [ ] no full normalizedPayload/transaction URL/customer data presentation test;
- [ ] no mutation control in receipt-attention UI test;
- [ ] Platform Admin read authorization test;
- [ ] manual settlement remains SUPER_ADMIN-only test;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, start-of-attempt synchronization, nested database gitlink and pushed task-branch evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin exceptional unmatched/NEEDS_ATTENTION mutation recovery, Gateway or system-test work.

## Implementation Notes

This should be a surgical provider-aware extension of the existing Admin refund support surface.

Do not duplicate:

```text
refund queue
refund detail drawer
settlement UI framework
billing navigation
```

for Woo.

The safety boundary is:

```text
normal Woo refund
    -> vendor dashboard action
    -> signed webhook
    -> BACKGROUND-005 completion
    -> Admin observes/supports

exceptional Woo refund
    -> Admin observes evidence
    -> no mutation in ADMIN-001
    -> ADMIN-002 must define any recovery explicitly
```

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

- BACKGROUND-005 is accepted and its WOO_REFUND processingError codes/provider evidence are stable.
- The existing Admin refund support screen remains the desired operator destination.
- Woo normal refunds are provider-confirmed by signed webhook, not by generic Admin manual evidence.

### Unresolved Issues

- Exact safe mutation for unmatched provider refunds is intentionally deferred to ADMIN-002.
- Exact safe operator resolution for provider amount mismatch is intentionally deferred to ADMIN-002.

### Architectural Concerns

None within this read/support-hardening task.

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
