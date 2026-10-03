---
id: ARCH-027-API-006
architecture_id: ARCH-027
title: Expose Shopify-parity WooCommerce purchase history and refund actions
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-027-BACKGROUND-005
enables:
  - ARCH-027-WOOCOMMERCE-003
created: 2026-10-03
updated: 2026-10-03
---

# Expose Shopify-parity WooCommerce purchase history and refund actions

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Expose the hosted Woo API required to reproduce the existing Shopify **Manage purchased credits** experience:

```text
purchase history
status filters
pagination
single/batch refund request
refund hold state
pre-provider reactivation
completed refund history
```

Implement exactly:

```text
GET  /v1/billing/recovery-credit-purchases
POST /v1/billing/recovery-credit-refunds
POST /v1/billing/recovery-credit-refunds/reactivate
```

The Woo API must preserve the existing Moda purchase-lot/refund business semantics while removing Shopify-only provider-context rules.

The merchant-visible behavior remains Shopify-parity:

```text
ACTIVE
WITHDRAWN
COMPLETED
REFUNDED
ALL

select one or many eligible purchases
request refund
see held/current/reserved/available values
reactivate only before provider action begins
see completed refund history
```

Provider mechanics differ:

- Shopify refund eligibility depends on the current meter/provider context because settlement is a correction against the current Shopify usage meter;
- Woo one-time charges are independent provider contracts, so an old Woo purchase remains refundable after plan/cycle changes when it still has unused/unreserved credits and valid purchase-provider evidence.

This task creates the **local Woo refund hold only**.

It MUST NOT:

- call Woo;
- approve a vendor-dashboard refund;
- wait for provider settlement;
- complete a `RecoveryCreditRefund`;
- create Shopify correction UsageEvents;
- mutate subscription/plan/period state;
- calculate the later proportional provider amount;
- expose Woo contract/transaction identifiers to the WordPress browser.

BACKGROUND-005 owns hold preparation/provider settlement after the local request is committed.

## Context

The current Shopify implementation in the supplied `moda-interact-workspace(20261003-123430).zip` provides the reference UX and business behavior through:

```text
app/routes/app/billing/recovery-credit-purchases/route.tsx
app/components/dashboard/RecoveryCreditPurchaseManager.jsx
app/services/billing/recovery-credit-purchase-management.service.ts
```

The existing Shopify experience uses:

```text
filters:
    ACTIVE
    WITHDRAWN
    COMPLETED
    REFUNDED
    ALL

page sizes:
    5
    10
    20

default page size:
    5

batch refund maximum:
    20 purchases
```

and supports merchant reactivation only while:

```text
purchase.status = WITHDRAWN
refund.status = REQUESTED
no provider action/reference/confirmation exists
```

ARCH-027 intentionally reuses that merchant model.

### Accepted Woo refund backend

BACKGROUND-005 now owns Woo-specific asynchronous behavior:

```text
REQUESTED local refund
    -> wait for reservations
    -> freeze final credit/provider amount
    -> PROVIDER_ACTION_REQUIRED
    -> Woo vendor-dashboard action
    -> refunded webhook
    -> COMPLETED or NEEDS_ATTENTION
```

The API producer contract expected by BACKGROUND-005 is therefore already fixed.

### Important Woo eligibility difference

Do **not** port Shopify's:

```text
current provider plan
current billing period
current live usage-event handle
```

refund eligibility checks into Woo.

A Woo one-time charge belongs to the purchase lot itself, not to the current recurring contract/meter.

For Woo the normal monetary refund eligibility proof is the purchase's own durable acquisition evidence.

## Scope

Modify only `moda-interact-api` implementation/tests/OpenAPI code required for:

1. paginated Woo purchase-history projection;
2. single/batch local refund-hold creation;
3. refund-request idempotency;
4. strictly pre-provider refund reactivation.

Expected implementation areas conceptually:

```text
src/billing/
  recovery-credit-purchases/
    purchase-history-route.ts
    purchase-history.service.ts
    refund-request-route.ts
    refund-request.service.ts
    refund-reactivation-route.ts
    refund-reactivation.service.ts

openapi/
  woocommerce-purchase-history-v1.yaml
```

Exact filenames may differ where API-001 through API-005 establish clearer route/service organization.

Reuse:

- ARCH-026 `WooInstallationAuthenticator`;
- accepted API error/JSON conventions;
- accepted `Idempotency-Key` parser from API-003/API-004;
- canonical Prisma client/transaction helpers;
- Shared structured logging.

Update the nested `database/` gitlink to the newest compatible architect-accepted ARCH-027 database main commit, including nullable Woo refund billing-period provenance, then regenerate Prisma.

## Out of Scope

- Woo billing hub/plan/top-up presentation already owned by API-002.
- Creating a one-time charge already owned by API-004.
- Background refund preparation/settlement owned by BACKGROUND-005.
- Woo provider API calls/credentials.
- Vendor-dashboard refund approval/rejection.
- Automated partial provider refund initiation.
- Refund completion from provider webhook.
- Admin unmatched/NEEDS_ATTENTION recovery.
- WordPress/Woo React UI.
- Shopify application/service changes.
- Prisma schema/migration edits other than advancing the accepted nested database gitlink.
- Updating `docs/architecture/_index.md`.

## Requirements

### R1 — Reuse Woo installation authentication exclusively

All three endpoints require the accepted ARCH-026 Woo installation principal:

```text
X-Moda-Installation-Id
Authorization: Bearer <installation credential>
```

Authoritative tenant:

```text
principal.shopId
```

Require:

```text
Shop.id = principal.shopId
Shop.platform = WOOCOMMERCE
Shop.shopifyShopId = NULL
Shop.status = ACTIVE
```

Do not accept:

```text
shopId
site URL/domain
Woo provider contract ID
Shopify shop ID
```

from the caller.

Purchase-history/refund management remains available when the current Subscription is `FROZEN`; refund management is purchase-lot state and must not disappear merely because recurring billing needs attention.

### R2 — Exact history endpoint

Implement:

```text
GET /v1/billing/recovery-credit-purchases
```

Accepted query parameters:

```text
filter
page
pageSize
```

Reject unknown query parameters.

`filter` is exactly one of:

```text
ACTIVE
WITHDRAWN
COMPLETED
REFUNDED
ALL
```

Default:

```text
ACTIVE
```

`page` is a positive integer, default `1`.

`pageSize` is exactly one of:

```text
5
10
20
```

Default:

```text
5
```

### R3 — History is Shop-scoped and Woo-purchase scoped

Return only:

```text
RecoveryCreditPurchase.shopId = principal.shopId
RecoveryCreditPurchase.provider = WOOCOMMERCE
```

Status filtering:

```text
ACTIVE     -> status = ACTIVE
WITHDRAWN  -> status = WITHDRAWN
COMPLETED  -> status = COMPLETED
REFUNDED   -> status = REFUNDED
ALL        -> no purchase-status filter
```

For `ALL`, a `REQUESTED` purchase linked to a Woo `ONE_TIME_CHARGE` operation in:

```text
INITIATING
AWAITING_CONFIRMATION
OUTCOME_UNKNOWN
CONFIRMED
```

may be shown as awaiting/processing confirmation.

A `REQUESTED` purchase whose linked acquisition operation is only:

```text
FAILED
```

is an audit/failed-checkout artifact and MUST NOT appear in merchant purchase history.

### R4 — Exact ordering and page clamp

Order:

```text
createdAt DESC,
id DESC
```

Return:

```text
schemaVersion = 1
page
pageSize
total
purchases
```

If the requested page exceeds the current last page, return the last page.

For zero results:

```text
page = 1
total = 0
purchases = []
```

### R5 — History item contract

Each item returns exactly the merchant-safe fields needed by the Shopify-parity manager:

```text
id
status
createdAt
activatedAt

creditsGranted
currentAmount
reservedAmount
availableAmount
heldForRefundAmount

refundEligible
refundUnavailableReason

planName
bundleLabel

originalProviderPurchase {
    amount
    currency
} | null

latestRefund | null
completedRefund | null

reactivationAvailable
providerActionStarted
```

Where:

```text
availableAmount =
    status == ACTIVE
      ? max(currentAmount - reservedAmount, 0)
      : 0

heldForRefundAmount =
    status == WITHDRAWN
      ? max(currentAmount - reservedAmount, 0)
      : 0
```

Do not return:

```text
providerReference
provider contract ID
provider transaction ID
providerPriceSnapshot
Woo confirmation URL
requestKey/fingerprint
Shopify plan/event handles
billingPeriodId
```

### R6 — Display-only plan and bundle labels

`planName` comes from the purchase's durable `plan` relation/name.

For Woo, `bundleLabel` may be resolved for display through the linked one-time-charge operation:

```text
purchase.id
    -> WooCommerceBillingOperation.recoveryCreditPurchaseId
    -> merchantPricingUsageEventId
    -> current MerchantPricingUsageEvent.adminLabel
```

This label is display-only.

If the catalogue event no longer exists or the label is blank:

```text
bundleLabel = null
```

Do not fail history retrieval.

The authoritative historical values remain:

```text
creditsGranted
provider purchase amount/currency
purchase/refund lifecycle
```

not the mutable display label.

### R7 — Merchant-safe refund summaries

Expose refund summaries only as:

```text
status
reason
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
createdAt
completedAt
```

`latestRefund` is the most recently created refund row for the purchase.

`completedRefund` is the most recently created `COMPLETED` refund row.

Do not expose internal admin IDs, source support-message IDs, provider references or automatic correction UsageEvent IDs.

### R8 — Woo refund eligibility is purchase-local

An ACTIVE Woo purchase is normal merchant-refund eligible only when all are true:

```text
status = ACTIVE

availableAmount =
    currentAmount - reservedAmount
    >= 1

providerReference non-blank
providerPurchaseAmount > 0
providerPurchaseCurrency = USD
providerValuationConfirmedAt non-null
providerPriceSnapshot non-null

no live refund exists in:
    REQUESTED
    PROVIDER_ACTION_REQUIRED
    NEEDS_ATTENTION
```

Refund eligibility MUST NOT require:

```text
current Subscription provider contract
current plan
current BillingPeriod
current Woo contract still active
current Shopify event handle
```

Historical Woo purchase lots therefore remain refundable after plan/cycle changes when their own evidence is valid.

### R9 — Refund unavailable reason

For an ACTIVE purchase return:

```text
refundEligible = true
refundUnavailableReason = null
```

when R8 passes.

Otherwise:

```text
refundEligible = false
```

with one of:

```text
NO_AVAILABLE_CREDITS
PROVIDER_EVIDENCE_UNAVAILABLE
REFUND_IN_PROGRESS
```

For non-ACTIVE purchase states:

```text
refundEligible = false
refundUnavailableReason = null
```

because the status itself explains the lifecycle.

### R10 — Reactivation presentation contract

Set:

```text
reactivationAvailable = true
```

only when:

```text
purchase.status = WITHDRAWN
latest live refund.status = REQUESTED

refund.providerReference IS NULL
refund.providerActionKind IS NULL
refund.providerConfirmedAt IS NULL

refund.finalCreditQuantity IS NULL
refund.expectedProviderAmount IS NULL
refund.expectedProviderCurrency IS NULL
```

Set:

```text
providerActionStarted = true
```

for a WITHDRAWN purchase whose latest live refund is:

```text
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

or otherwise has provider action/evidence fields populated.

This preserves the Shopify UX distinction:

```text
REQUESTED pre-provider -> Reactivate available
provider action begun  -> Reactivation blocked
```

### R11 — Exact batch refund endpoint

Implement:

```text
POST /v1/billing/recovery-credit-refunds
```

Required header:

```text
Idempotency-Key
```

Reuse API-003/API-004's exact accepted grammar.

Request JSON is exactly:

```json
{
  "purchaseIds": ["...", "..."]
}
```

Reject unknown fields.

Requirements:

```text
1..20 input entries
non-blank strings
deduplicate purchase IDs preserving first occurrence order
```

Do not accept:

```text
quantity
refundQuantity
amount
currency
shopId
billingPeriodId
providerReference
```

from the caller.

### R12 — Batch idempotency is per purchase

One batch request processes each unique purchase independently.

Do **not** wrap the entire batch in one database transaction.

For each purchase derive the database refund request key exactly as:

```text
canonicalIntent =
    "arch027-woo-refund-v1\n"
    + shopId + "\n"
    + Idempotency-Key + "\n"
    + purchaseId + "\n"

requestKey =
    "woo-refund-v1:"
    + lower-case hex SHA-256(canonicalIntent)
```

This fits the existing `requestKey VARCHAR(255)` contract.

The same batch/header replay is idempotent for every selected purchase.

A later request with a new idempotency key may create a new refund only after any prior refund is terminal and the purchase is again eligible.

Changing the purchase list while reusing the same header does not rewrite existing refund rows; newly included purchase IDs derive distinct keys and are evaluated independently.

### R13 — Refund batch response preserves independent outcomes

Return exactly:

```json
{
  "schemaVersion": 1,
  "outcomes": [
    {
      "purchaseId": "...",
      "code": "REQUESTED",
      "currentAmount": 10,
      "reservedAmount": 2,
      "availableAmount": 8
    }
  ]
}
```

Outcomes are in deduplicated request order.

Allowed codes:

```text
REQUESTED
REFUND_NOT_AVAILABLE
NOT_ACTIVE
ALREADY_WITHDRAWN
ALREADY_REFUNDED
COMPLETED
NOT_FOUND
REFUND_STATE_CONFLICT
```

One purchase failure MUST NOT roll back another purchase's successful refund hold.

### R14 — Fresh state is authoritative for every selected purchase

Each purchase uses a separate Serializable transaction with bounded retry.

Load the purchase by:

```text
id
shopId = principal.shopId
provider = WOOCOMMERCE
```

Cross-Shop/other-provider purchase returns:

```text
NOT_FOUND
```

Do not expose its existence.

Reload live refunds inside the same transaction.

Never trust history data previously rendered to the browser.

### R15 — Existing live refund is idempotent

If a live refund exists:

```text
REQUESTED
    -> REQUESTED

PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
    -> ALREADY_WITHDRAWN
```

and return the authoritative current:

```text
currentAmount
reservedAmount
availableAmount
```

Do not create another live refund.

### R16 — Purchase status outcomes

If no live refund exists:

```text
purchase.status = REFUNDED
    -> ALREADY_REFUNDED

purchase.status = COMPLETED
    -> COMPLETED

purchase.status != ACTIVE
    -> NOT_ACTIVE
```

Only ACTIVE may create a new hold.

### R17 — Refund admission uses current local purchase state only

For ACTIVE:

```text
availableAmount =
    max(currentAmount - reservedAmount, 0)
```

Require:

```text
availableAmount >= 1
```

and R8 provider purchase evidence.

If not:

```text
REFUND_NOT_AVAILABLE
```

Do not query Woo.

Do not require current subscription/provider context.

### R18 — Exact Woo refund row created by the API

For an admitted purchase, create:

```text
RecoveryCreditRefund
    shopId = principal.shopId
    purchaseId = purchase.id
    provider = WOOCOMMERCE
    source = MERCHANT_UI

    sourceMessageId = NULL
    requestedByShopifyUserId = NULL

    purchaseCreditsGrantedSnapshot = purchase.creditsGranted
    currentAmountAtRequestSnapshot = purchase.currentAmount
    reservedAmountAtRequestSnapshot = purchase.reservedAmount
    availableAmountAtRequestSnapshot = availableAmount

    billingPeriodIdSnapshot = purchase.billingPeriodId
    providerSubscriptionIdSnapshot =
        purchase.providerSubscriptionIdSnapshot

    planHandleSnapshot = NULL
    eventHandleSnapshot = NULL
    shopifyPartnerDevelopmentSnapshot = false

    purchaseProviderAmountSnapshot =
        purchase.providerPurchaseAmount
    purchaseProviderCurrencySnapshot =
        purchase.providerPurchaseCurrency

    finalCreditQuantity = NULL
    expectedProviderAmount = NULL
    expectedProviderCurrency = NULL

    automaticCorrectionUsageEventId = NULL
    providerReference = NULL
    providerActionKind = NULL
    providerAmount = NULL
    providerCurrency = NULL
    providerConfirmedByPlatformAdminId = NULL
    providerConfirmedAt = NULL

    status = REQUESTED
    requestKey = R12 key
    reason = NULL
    holdAppliedAt = now
```

For a Woo Free purchase:

```text
billingPeriodIdSnapshot = NULL
providerSubscriptionIdSnapshot = NULL
```

is valid.

### R19 — Apply the refund hold atomically

In the same Serializable transaction:

```text
purchase:
    ACTIVE -> WITHDRAWN
    version += 1

ShopEntitlementCounter(PURCHASED_RECOVERY_CREDITS):
    refundingQuantity += availableAmount
    version += 1
```

Preserve purchase:

```text
currentAmount
reservedAmount
creditsGranted
provider evidence
```

exactly.

The aggregate counter must exist and satisfy its normal invariants.

A missing/inconsistent aggregate produces:

```text
REFUND_STATE_CONFLICT
```

and creates no partial refund hold.

### R20 — Uniqueness races resolve to authoritative state

Handle both:

```text
RecoveryCreditRefund.requestKey unique
one-live-refund-per-purchase unique constraint
```

deterministically.

On `P2002`/equivalent:

1. first reload exact `requestKey` under authenticated Shop/purchase scope;
2. if absent, reload the purchase + current live refund under:
   ```text
   purchase.id = requested purchase
   purchase.shopId = principal.shopId
   ```
3. if a live refund now exists, return its authoritative outcome;
4. only rethrow if neither exact idempotency state nor authoritative live refund explains the conflict.

Never query/return cross-Shop refund state.

### R21 — No provider call or asynchronous publication from refund request

Successful request ends after the local database hold commits.

Do not:

```text
call Woo
call Background HTTP
publish BullMQ/Redis
create Shopify correction UsageEvent
```

The existing leased Background worker discovers:

```text
provider = WOOCOMMERCE
status = REQUESTED
```

and BACKGROUND-005 prepares it asynchronously.

### R22 — Exact reactivation endpoint

Implement:

```text
POST /v1/billing/recovery-credit-refunds/reactivate
```

Request JSON exactly:

```json
{
  "purchaseId": "..."
}
```

Reject unknown fields.

No amount/quantity/provider fields are accepted.

### R23 — Reactivation is strictly pre-provider-action

Using a Serializable transaction, require:

```text
purchase.shopId = principal.shopId
purchase.provider = WOOCOMMERCE
purchase.status = WITHDRAWN

latest live refund exists
refund.provider = WOOCOMMERCE
refund.status = REQUESTED

refund.providerReference IS NULL
refund.providerActionKind IS NULL
refund.providerConfirmedAt IS NULL

refund.finalCreditQuantity IS NULL
refund.expectedProviderAmount IS NULL
refund.expectedProviderCurrency IS NULL
```

Otherwise return:

```text
REACTIVATION_NOT_AVAILABLE
```

Do not reactivate:

```text
PROVIDER_ACTION_REQUIRED
NEEDS_ATTENTION
```

refunds.

### R24 — Reactivation with credits remaining

If:

```text
purchase.currentAmount > 0
```

calculate:

```text
heldAvailable =
    max(
      purchase.currentAmount - purchase.reservedAmount,
      0
    )
```

atomically:

```text
refund.status = CANCELLED
refund.reason = MERCHANT_REACTIVATED
refund.version += 1

purchase.status = ACTIVE
purchase.version += 1

counter.refundingQuantity -= heldAvailable
counter.version += 1
```

Preserve current/reserved amounts exactly.

Return:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "code": "REACTIVATED",
  "currentAmount": 7,
  "reservedAmount": 2
}
```

### R25 — Reactivation when no credits remain

If:

```text
purchase.currentAmount = 0
```

do not restore a zero-credit purchase to ACTIVE.

Atomically:

```text
refund.status = CANCELLED
refund.reason = MERCHANT_REACTIVATED
refund.version += 1

purchase.status = COMPLETED
purchase.version += 1
```

Require the held aggregate amount is already zero/consistent.

Return exactly:

```json
{
  "schemaVersion": 1,
  "purchaseId": "...",
  "code": "COMPLETED_NO_CREDITS",
  "currentAmount": 0,
  "reservedAmount": 0
}
```

### R26 — Reactivation HTTP retry is state-idempotent

If a retry finds:

```text
purchase.status = ACTIVE
latest refund.status = CANCELLED
latest refund.reason = MERCHANT_REACTIVATED
```

return the persisted semantic result:

```text
REACTIVATED
```

without another counter mutation.

If:

```text
purchase.status = COMPLETED
latest refund.status = CANCELLED
latest refund.reason = MERCHANT_REACTIVATED
```

return:

```text
COMPLETED_NO_CREDITS
```

Other terminal/cancelled historical refunds do not imply replay success.

### R27 — Refund/Background preparation race has one winner

BACKGROUND-005 moves:

```text
REQUESTED -> PROVIDER_ACTION_REQUIRED
```

with refund version/CAS once reserved credits are zero and provider economics are frozen.

Merchant reactivation competes on the same refund version/status.

Exactly one wins:

```text
reactivation wins
    -> refund CANCELLED / purchase ACTIVE
    -> Background preparation CAS loses

Background preparation wins
    -> PROVIDER_ACTION_REQUIRED
    -> reactivation returns REACTIVATION_NOT_AVAILABLE
```

Do not weaken this race boundary.

### R28 — No direct capacity-resume transport from API

Reactivation may restore spendable purchased capacity.

Do not add Redis/BullMQ merely for this API action.

The next normal recovery admission reads the restored counter, and existing repair paths remain authoritative.

If later source evidence proves immediate async resume is required for UX parity, that must be separately architected rather than silently coupling API to Background here.

### R29 — History read never calls Woo

The purchase-history endpoint is a local durable read model.

It MUST NOT call Woo to determine:

```text
refund eligibility
purchase status
provider transaction state
```

The accepted local provider evidence is authoritative for presentation.

### R30 — OpenAPI contract

Document all three endpoints with:

- Woo installation authentication;
- exact filters/page sizes;
- exact history fields;
- batch maximum 20;
- required `Idempotency-Key` only on refund request;
- independent batch outcomes;
- reactivation semantics;
- no caller-controlled refund quantity/money/provider identity.

## Work Items

- [ ] Add exact paginated Woo purchase-history endpoint.
- [ ] Add ACTIVE/WITHDRAWN/COMPLETED/REFUNDED/ALL filters with exact 5/10/20 page sizes.
- [ ] Exclude failed REQUESTED checkout artifacts from merchant history.
- [ ] Add merchant-safe history item/refund summary projection.
- [ ] Add Woo purchase-local refund eligibility without Shopify current-provider-context checks.
- [ ] Add exact batch refund endpoint with maximum 20 unique purchases.
- [ ] Reuse accepted Idempotency-Key parser and implement exact per-purchase SHA-256 requestKey.
- [ ] Process batch lots independently with one Serializable transaction per purchase.
- [ ] Create exact provider=WOOCOMMERCE refund snapshot/hold expected by BACKGROUND-005.
- [ ] Apply ACTIVE -> WITHDRAWN plus purchased-counter refunding hold atomically.
- [ ] Handle requestKey/live-refund uniqueness races deterministically.
- [ ] Add exact reactivation endpoint.
- [ ] Preserve Shopify-parity REQUESTED-only pre-provider reactivation semantics.
- [ ] Add state-idempotent reactivation replay behavior.
- [ ] Prove Background preparation/reactivation CAS race has one winner.
- [ ] Update OpenAPI and add focused history/refund/reactivation tests.

## Interfaces / Contracts

### Purchase history

```text
GET /v1/billing/recovery-credit-purchases
  ?filter=ACTIVE|WITHDRAWN|COMPLETED|REFUNDED|ALL
  &page=1
  &pageSize=5|10|20
```

### Batch refund request

```text
POST /v1/billing/recovery-credit-refunds
Idempotency-Key: <required>

{
  "purchaseIds": ["purchase-a", "purchase-b"]
}
```

One local refund hold per eligible purchase.

### Reactivation

```text
POST /v1/billing/recovery-credit-refunds/reactivate

{
  "purchaseId": "..."
}
```

Allowed only before BACKGROUND-005/provider action begins.

### Asynchronous consumer

Producer:

`ARCH-027-API-006`

Consumer:

`ARCH-027-BACKGROUND-005`

Durable handoff:

```text
RecoveryCreditRefund
provider = WOOCOMMERCE
status = REQUESTED
```

No queue contract is created.

## Dependencies

- `ARCH-027-BACKGROUND-005`

BACKGROUND-005 must be architect-accepted Complete before API-006 becomes Ready so the exact Woo refund producer/consumer contract is fixed before merchant refund actions can create holds.

Through the dependency chain, API-006 also consumes accepted Woo installation authentication and ARCH-027 database provider-neutral purchase/refund fields.

## Enables

- `ARCH-027-WOOCOMMERCE-003`

WOOCOMMERCE-003 will consume API-006 to reproduce the existing Shopify purchase-history/refund/reactivation merchant experience after the recurring and top-up Billing surfaces are accepted.

## Acceptance Criteria

- [ ] Exactly the three API-006 endpoints are added.
- [ ] Purchase-history responses are explicitly versioned with `schemaVersion=1`.
- [ ] Both reactivation success codes return the same bounded versioned response shape with purchase/current/reserved quantities.
- [ ] All endpoints authorize exclusively through the Woo installation principal.
- [ ] History filters/page sizes/defaults match the current Shopify merchant experience.
- [ ] History is Shop-scoped and provider=WOOCOMMERCE scoped.
- [ ] Failed REQUESTED checkout artifacts are not shown as indefinitely awaiting confirmation.
- [ ] History exposes no Woo provider contract/transaction IDs or Shopify handles.
- [ ] ACTIVE Woo purchase refund eligibility depends on its own unused/unreserved credits and durable provider purchase evidence, not current subscription/plan/period.
- [ ] Historical Woo purchases can remain refund eligible after plan/cycle changes.
- [ ] Batch refund accepts 1..20 unique purchase IDs and no quantity/money/provider inputs.
- [ ] Refund request requires the accepted Idempotency-Key grammar.
- [ ] Per-purchase requestKey follows exact SHA-256 canonical intent.
- [ ] Batch lots commit/fail independently.
- [ ] Same request replay is idempotent.
- [ ] Different-request live-refund uniqueness race returns authoritative current state rather than 500.
- [ ] Eligible request atomically creates one Woo REQUESTED refund, withdraws the purchase and increments refundingQuantity by available amount only.
- [ ] Reserved credits remain outside the initial hold quantity.
- [ ] Free-plan Woo refund snapshot may have null billingPeriod/providerSubscription provenance.
- [ ] No Shopify plan/event handles or correction UsageEvent are written for Woo.
- [ ] Successful refund request makes no Woo/network/Background call.
- [ ] Reactivation is allowed only for strictly pre-provider REQUESTED refund state.
- [ ] PROVIDER_ACTION_REQUIRED/NEEDS_ATTENTION cannot be reactivated.
- [ ] Reactivation restores ACTIVE only when currentAmount > 0 and decrements exactly the currently held amount.
- [ ] Zero-current purchase reactivation completes rather than restoring an empty ACTIVE lot.
- [ ] Reactivation replay is state-idempotent.
- [ ] Reactivation/BACKGROUND-005 preparation race has exactly one CAS winner.
- [ ] OpenAPI documents exact contracts.
- [ ] `docs/architecture/_index.md` is unchanged.

## Validation

Inspect the accepted `moda-interact-api/package.json` and implementation before selecting exact commands.

Required categories:

- [ ] repository typecheck/build;
- [ ] targeted lint/changed-file diagnostics;
- [ ] authenticated Shop-scoped history tests;
- [ ] history `schemaVersion=1` response-shape test;
- [ ] exact `REACTIVATED` / `COMPLETED_NO_CREDITS` response-shape tests;
- [ ] cross-Shop purchase non-disclosure test;
- [ ] provider=SHOPIFY row exclusion test;
- [ ] exact filter/default/page-size tests;
- [ ] page-clamp/zero-result tests;
- [ ] failed REQUESTED acquisition exclusion test;
- [ ] history merchant-safe field/redaction test;
- [ ] Woo historical prior-plan/prior-period purchase remains eligible test;
- [ ] no-current-recurring-contract eligibility test;
- [ ] missing provider evidence -> refund unavailable test;
- [ ] 1..20 batch bound and dedupe-order test;
- [ ] Idempotency-Key grammar tests;
- [ ] exact requestKey SHA-256 vector test;
- [ ] successful refund hold atomic transaction test;
- [ ] reserved-credit available-amount hold test;
- [ ] same-request replay test;
- [ ] different-request one-live-refund P2002/concurrency test;
- [ ] per-purchase batch partial-success test;
- [ ] aggregate missing/conflict rollback test;
- [ ] Free null billing-period/provider-subscription refund snapshot test;
- [ ] no provider/queue/UsageEvent call assertion;
- [ ] reactivation positive test;
- [ ] reactivation provider-action-blocked tests;
- [ ] zero-current reactivation completion test;
- [ ] reactivation replay idempotency test;
- [ ] reactivation/BACKGROUND-preparation CAS race test;
- [ ] no sensitive/provider identity in API response/log test;
- [ ] `git diff --check`;
- [ ] dedicated parent/implementation worktree, synchronization, nested database gitlink and pushed task-branch evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete:

```text
finish Completion Report
    -> status: review
    -> return to moda_architect
    -> STOP
```

Do not begin Woo UI or Admin support implementation.

## Implementation Notes

The goal is **same merchant experience, different provider proof**.

Do not copy the Shopify `isCurrentProviderContext()` requirement into Woo.

Shopify needs current meter context for a correction against a plan-associated usage meter.

Woo has an independent one-time charge contract, so the purchase's own durable provider evidence is sufficient for normal refund eligibility.

Keep provider settlement asynchronous:

```text
API-006:
    local refund hold

BACKGROUND-005:
    wait/freeze/provider settlement reconciliation
```

Do not make the merchant HTTP request wait for Woo provider action.

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

- BACKGROUND-005 is accepted before execution and consumes provider=WOOCOMMERCE REQUESTED refunds.
- Woo merchant purchase-history UI will be implemented later against these APIs.
- Current Woo historical one-time-charge purchases remain provider-refundable independently of current recurring plan context, subject to unused/unreserved local credits and valid provider purchase evidence.

### Unresolved Issues

- None within the local purchase-history/refund API boundary.
- Provider partial-refund capability remains a separate sandbox gate and does not change local hold creation.

### Architectural Concerns

None.

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
