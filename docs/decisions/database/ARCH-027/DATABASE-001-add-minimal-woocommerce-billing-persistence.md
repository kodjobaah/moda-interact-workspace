---
id: ARCH-027-DATABASE-001
architecture_id: ARCH-027
title: Add minimal WooCommerce billing persistence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-002
enables:
  - ARCH-027-SHOPIFY-001
  - ARCH-027-API-001
  - ARCH-027-API-002
  - ARCH-027-API-003
  - ARCH-027-API-004
  - ARCH-027-BACKGROUND-001
  - ARCH-027-BACKGROUND-002
  - ARCH-027-BACKGROUND-003
  - ARCH-027-ADMIN-002
created: 2026-10-03
updated: 2026-10-03
---

# Add minimal WooCommerce billing persistence

## Architecture

Architecture ID:

`ARCH-027`

Architecture document:

`docs/architecture/ARCH-027-woocommerce-marketplace-billing-adapter.md`

Coordinator:

`moda_architect`

## Objective

Extend the existing Moda billing persistence model with the **minimum durable WooCommerce billing workflow and provider-evidence state** required for Marketplace SaaS subscriptions, plan switches, one-time recovery-credit charges, signed webhook deduplication, current-period allowance changes and provider-specific purchase/refund evidence.

The task MUST preserve the existing Moda commercial catalogue and operational billing domain:

```text
MerchantPricingPlan
MerchantPricingUsageEvent
MerchantPricingUsageTier
        |
        | existing catalogue
        v
provider adapter / verified provider evidence
        |
        v
BillingPlan
Subscription
BillingPeriod
BillingPeriodEntitlementCounter
RecoveryCreditPurchase / RecoveryCreditRefund
```

This task does **not** create a Woo pricing catalogue and does **not** replace `BillingPlan`, `Subscription`, `BillingPeriod`, `UsageEvent` or `UsageReservation`.

The required persistent delta is:

```text
CREATE
    woocommerce.WooCommerceBillingOperation
    woocommerce.WooCommerceBillingWebhookReceipt

MODIFY MINIMALLY
    billing.BillingPeriodEntitlementCounter
    billing.Subscription
    billing.RecoveryCreditPurchase
    billing.RecoveryCreditRefund

DO NOT REPLACE / DUPLICATE
    billing.MerchantPricingPlan
    billing.MerchantPricingUsageEvent
    billing.MerchantPricingUsageTier
    billing.BillingPlan
    billing.BillingPeriod
    billing.UsageEvent
    billing.UsageReservation
    woocommerce.WooCommerceInstallation
```

## Context

The accepted ARCH-027 direction is a minimal adapter around the current Shopify-shaped billing implementation, not a generic billing rewrite.

Current-source facts from the `moda-interact-workspace(20261003-123430).zip` baseline:

1. `MerchantPricingPlan` is the recurring commercial catalogue and already stores:
   - `shopifyPlanHandle`;
   - recurring amount/currency/billing period;
   - included recovery allowance;
   - plan features;
   - Shopify recovery usage-event handle.

2. `MerchantPricingUsageEvent` / `MerchantPricingUsageTier` already store top-up catalogue economics. For ARCH-027 Woo v1, one merchant selection is one predefined bundle: the API may expose only a directly priced `MerchantPricingUsageEvent` with `pricingMode = FIXED` and non-null `fixedUnitAmountMinor`. `creditsGrantedPerUnit` is the credits granted by that bundle and `fixedUnitAmountMinor` / `currency` are the authoritative retail price. `GRADUATED` / `VOLUME` schedules remain existing catalogue/Admin capabilities but are not evaluated by the Woo adapter. Re-buying a bundle is a new purchase operation/lot rather than a quantity on one charge.

3. `BillingPlan` is the operational plan snapshot currently materialised by the Shopify path. It remains physically independent from `MerchantPricingPlan` and is currently keyed by the catalogue's `shopifyPlanHandle`. ARCH-027 does not change that database model. Woo resolves a trusted `MerchantPricingPlan.id`; downstream software reuses the same catalogue row and the same operational `BillingPlan` materialisation semantics.

4. `Subscription.shopId` is unique, so the existing Moda domain permits **at most one `Subscription` row per `Shop`**. `Subscription.providerSubscriptionId` exists but is not indexed.

5. `BillingPeriodEntitlementCounter` currently contains:
   - `grantedQuantity`;
   - `committedQuantity`;
   - `reservedQuantity`;
   - `forfeitedQuantity`;
   - `version`;
   and the database enforces:
   `committed + reserved + forfeited <= granted`.

6. `RecoveryCreditPurchase` is already the durable purchased-credit lot but currently requires Shopify-specific acquisition evidence:
   - `shopifyPlanHandleSnapshot`;
   - `shopifyEventHandleSnapshot`;
   - `providerSubscriptionIdSnapshot`;
   - provider usage-before/after snapshots;
   - mandatory `usageEventId`.

7. `RecoveryCreditRefund` already owns generic refund quantity/economic lifecycle plus Shopify correction evidence. Its generic provider-result fields already exist:
   - `providerReference`;
   - `providerActionKind`;
   - `providerAmount`;
   - `providerCurrency`;
   - `providerConfirmedAt`.

8. `UsageEvent.provider` already exists and can represent `WOOCOMMERCE`; this task MUST NOT redesign `UsageEvent`.

9. ARCH-026 establishes:
   - `commerce.Shop.platform`;
   - `commerce.Shop.onboardingCompleted`;
   - the `woocommerce` PostgreSQL schema;
   - `woocommerce.WooCommerceInstallation`.
   `WooCommerceInstallation` remains the plugin installation/authentication identity only. Billing state MUST NOT be moved into it.

10. ARCH-026-DATABASE-002 is the serialization gate for this repository. ARCH-027-DATABASE-001 remains `pending` until ARCH-026-DATABASE-002 is architect-accepted `complete`, preventing concurrent schema/migration work against `commerce.Shop` / the same Prisma schema.

### Provider mapping invariant

This database task must support, but must not itself implement, the two provider mappings:

```text
Shopify
verified plan_handle
    -> MerchantPricingPlan.shopifyPlanHandle
    -> existing/materialised BillingPlan

WooCommerce
verified Woo operation/provider contract
    -> WooCommerceBillingOperation.merchantPricingPlanId
    -> MerchantPricingPlan.id
    -> existing/materialised BillingPlan
```

There MUST NOT be separate Shopify and Woo `BillingPlan` rows for the same Moda catalogue plan merely because two providers can activate it.

### Subscription cardinality and Woo contract identity invariant

The current schema already enforces:

```text
Shop 1 -> 0..1 Subscription

Subscription.shopId is UNIQUE
```

ARCH-027 MUST preserve that invariant. WooCommerce does **not** introduce a second Moda subscription model.

`WooCommerceBillingOperation` is historical provider-workflow evidence scoped to a `Shop`; it MUST NOT contain a `subscriptionId` foreign key or Prisma relation to `Subscription`. For subscription-affecting operations, follow-on application/background code resolves the Shop's single current Moda subscription through the existing unique `Subscription.shopId` relationship.

`providerContractId` is a **WooCommerce.com-owned external billing-contract UUID/reference**. It is not:

```text
commerce.Shop.id
woocommerce.WooCommerceInstallation.id
a merchant/customer identity
MerchantPricingPlan.id
Subscription.id
```

Its meaning is operation-specific:

```text
SUBSCRIPTION_CREATE
    providerContractId = the Woo recurring subscription contract UUID once Woo returns it

PLAN_SWITCH
    providerContractId = the existing Woo recurring subscription contract being changed

CANCEL
    providerContractId = the existing Woo recurring subscription contract being cancelled

ONE_TIME_CHARGE
    providerContractId = the Woo one-time charge contract UUID once Woo returns it
```

After verified recurring-subscription activation/reconciliation, the current Woo recurring contract UUID may be projected to:

```text
Subscription.providerSubscriptionId
```

A one-time-charge contract UUID MUST NOT become `Subscription.providerSubscriptionId`; it belongs to the Woo operation and the corresponding `RecoveryCreditPurchase` provider evidence.

Historical operation rows may therefore contain multiple Woo contract IDs for the same Shop, and multiple operations may refer to the same recurring Woo contract. Neither case implies multiple Moda `Subscription` rows.

### Money representation invariant

`WooCommerceBillingOperation.quotedAmountMinor` is an integer **minor-unit** snapshot of the exact amount Moda sent to Woo.

Existing purchase/refund provider amount fields are `Decimal` provider-evidence fields and MUST retain their current representation and semantics.

This task MUST NOT invent an implicit integer/Decimal conversion rule in the database. The API/Background tasks must perform explicit conversion at the provider boundary.

## Scope

Modify only `moda-interact-database` plus the assigned parent task report.

Expected primary implementation files:

```text
moda-interact-database/prisma/schema.prisma
moda-interact-database/prisma/migrations/<timestamp>_arch027_woocommerce_billing_persistence/migration.sql
moda-interact-database/scripts/validate-arch027-woocommerce-billing-schema.mjs
moda-interact-database/scripts/validate-arch027-woocommerce-billing-migration.mjs
moda-interact-database/scripts/test-arch027-woocommerce-billing-postgres.mjs
moda-interact-database/package.json
moda-interact-database/docs/generated/prisma-erd.puml
```

The migration directory timestamp MUST sort after the accepted ARCH-026-DATABASE-002 migration. Create exactly one ARCH-027 database migration for this task; do not rewrite historical migrations.

### A. Woo billing operation enums

Add exactly these provider-specific enums in PostgreSQL schema `woocommerce`:

```prisma
enum WooCommerceBillingOperationKind {
  SUBSCRIPTION_CREATE
  PLAN_SWITCH
  ONE_TIME_CHARGE
  CANCEL

  @@schema("woocommerce")
}

enum WooCommerceBillingOperationState {
  INITIATING
  AWAITING_CONFIRMATION
  CONFIRMED
  OUTCOME_UNKNOWN
  FAILED

  @@schema("woocommerce")
}
```

No generic cross-provider operation enum/table is introduced by this task.

### B. `WooCommerceBillingOperation`

Add this logical model in schema `woocommerce`:

```prisma
model WooCommerceBillingOperation {
  id     String @id @default(cuid()) @db.Text
  shopId String @db.Text
  shop   Shop   @relation(fields: [shopId], references: [id], onDelete: Cascade, onUpdate: Restrict)

  kind  WooCommerceBillingOperationKind
  state WooCommerceBillingOperationState @default(INITIATING)

  requestKey         String @db.VarChar(255)
  requestFingerprint Bytes

  merchantPricingPlanId String? @db.Text
  merchantPricingPlan   MerchantPricingPlan? @relation(
    fields: [merchantPricingPlanId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )

  merchantPricingUsageEventId String? @db.Text
  merchantPricingUsageEvent   MerchantPricingUsageEvent? @relation(
    fields: [merchantPricingUsageEventId],
    references: [id],
    onDelete: Restrict,
    onUpdate: Restrict
  )

  quotedAmountMinor   Int?
  quotedCurrency      String? @db.Char(3)
  quotedBillingPeriod MerchantPricingBillingPeriod?

  recoveryCreditPurchaseId String? @unique @db.Text
  recoveryCreditPurchase   RecoveryCreditPurchase? @relation(
    "WooCommerceBillingOperationRecoveryCreditPurchase",
    fields: [recoveryCreditPurchaseId],
    references: [id],
    onDelete: SetNull,
    onUpdate: Restrict
  )

  providerContractId String? @db.VarChar(255)
  confirmationUrl    String? @db.VarChar(2048)
  lastErrorCode      String? @db.VarChar(128)

  createdAt DateTime @default(now()) @db.Timestamptz(3)
  updatedAt DateTime @default(now()) @updatedAt @db.Timestamptz(3)

  @@unique([shopId, requestKey])
  @@index([shopId, state, createdAt])
  @@index([providerContractId, createdAt])
  @@index([merchantPricingPlanId])
  @@index([merchantPricingUsageEventId])
  @@schema("woocommerce")
}
```

Prisma formatting/relation-field layout may differ, but field names, nullability, referenced entities, delete/update semantics, uniqueness and indexes are architectural requirements.

Add the required inverse Prisma relations to `Shop`, `MerchantPricingPlan`, `MerchantPricingUsageEvent` and `RecoveryCreditPurchase`. These inverse fields are Prisma relation metadata only; they MUST NOT redesign those models.

Do **not** add a `Subscription` inverse relation for Woo billing operations. The operation is tenant-scoped by `shopId`; the Shop's current subscription remains resolved through the existing unique `Subscription.shopId` relationship.

#### Operation command identity

`requestKey` is the Moda command retry identity. It is unique **per Shop**, not globally.

`requestFingerprint` is exactly 32 bytes containing a SHA-256 digest over the canonical operation intent. The API task owns canonicalization and same-key/same-fingerprint validation.

The database MUST enforce:

```text
UNIQUE(shopId, requestKey)

octet_length(requestFingerprint) = 32

btrim(requestKey) <> ''
```

Do **not** make `requestFingerprint` unique. Two legitimate, separately requested top-ups may have identical plan/event/price intent and must be allowed when they have different request keys.

#### Operation kind shape

Add a deterministic PostgreSQL check enforcing exactly these intent shapes:

```text
SUBSCRIPTION_CREATE
    merchantPricingPlanId          IS NOT NULL
    merchantPricingUsageEventId    IS NULL
    quotedAmountMinor              IS NOT NULL AND > 0
    quotedCurrency                 IS NOT NULL
    quotedBillingPeriod            IS NOT NULL
    recoveryCreditPurchaseId       IS NULL
    providerContractId             MAY be NULL until Woo returns the new recurring contract UUID

PLAN_SWITCH
    merchantPricingPlanId          IS NOT NULL
    merchantPricingUsageEventId    IS NULL
    quotedAmountMinor              IS NOT NULL AND > 0
    quotedCurrency                 IS NOT NULL
    quotedBillingPeriod            IS NOT NULL
    recoveryCreditPurchaseId       IS NULL
    providerContractId             IS NOT NULL

ONE_TIME_CHARGE
    merchantPricingPlanId          IS NULL
    merchantPricingUsageEventId    IS NOT NULL
    quotedAmountMinor              IS NOT NULL AND > 0
    quotedCurrency                 IS NOT NULL
    quotedBillingPeriod            IS NULL
    recoveryCreditPurchaseId       IS NOT NULL
    providerContractId             MAY be NULL until Woo returns the new charge contract UUID

CANCEL
    merchantPricingPlanId          IS NULL
    merchantPricingUsageEventId    IS NULL
    quotedAmountMinor              IS NULL
    quotedCurrency                 IS NULL
    quotedBillingPeriod            IS NULL
    recoveryCreditPurchaseId       IS NULL
    providerContractId             IS NOT NULL
```

The Free-plan activation path is local Moda state and MUST NOT manufacture a zero-value `SUBSCRIPTION_CREATE` Woo operation.

A Woo Shop on the Moda Free plan MAY still buy recovery-credit top-ups through `ONE_TIME_CHARGE`. A recurring Woo subscription contract is **not** a prerequisite for a Woo one-time charge. In particular:

```text
Moda Subscription
    plan = Free BillingPlan
    providerSubscriptionId = NULL

        +

WooCommerceBillingOperation
    kind = ONE_TIME_CHARGE
    merchantPricingUsageEventId = <Free-plan top-up event>
    recoveryCreditPurchaseId = <requested purchase lot>
    providerContractId = NULL until Woo creates the charge contract
```

is a valid architecture state. The later Woo charge contract UUID belongs to the `ONE_TIME_CHARGE` operation / purchase evidence and MUST NOT be copied into `Subscription.providerSubscriptionId`.

The database does not decide whether a usage event is offered by the Shop's current Free or Paid plan. The follow-on Woo API command MUST validate that the selected `MerchantPricingUsageEvent` belongs to the Shop's current Moda plan and is a Woo-v1-eligible predefined bundle: `pricingMode = FIXED`, non-null positive `fixedUnitAmountMinor`, and an accepted provider currency. The operation snapshots that stored bundle price directly. This database task MUST NOT add a recurring-contract requirement that would prevent that valid Free-plan top-up flow.

#### Operation quote constraints

When `quotedCurrency` is non-null it must be exactly three uppercase ASCII letters.

The database MUST NOT hard-code `USD`. Woo v1's USD-only restriction belongs to the Woo adapter; the durable operation stores the currency actually quoted.

If non-null, these strings must be non-blank:

```text
providerContractId
confirmationUrl
lastErrorCode
```

`CONFIRMED` requires a non-null, non-blank `providerContractId`.

`PLAN_SWITCH` and `CANCEL` require a non-null `providerContractId` from insertion because they act on the Shop's already-known recurring Woo contract.

`SUBSCRIPTION_CREATE` and `ONE_TIME_CHARGE` may begin with `providerContractId = NULL`; when Woo returns the newly created recurring/charge contract UUID, the field may transition exactly once from `NULL` to that non-blank value.

`OUTCOME_UNKNOWN` explicitly permits `providerContractId = NULL` because a provider POST may have succeeded while its response was lost.

The database MUST NOT interpret `providerContractId` as a Moda merchant, installation or subscription-row identifier.

#### Immutable operation intent

Add a deterministic update guard in schema `woocommerce`:

```text
function:
    woocommerce.arch027_woocommerce_billing_operation_guard()

trigger:
    arch027_woocommerce_billing_operation_guard
```

The guard MUST reject updates that change any operation-intent or quote-snapshot field after insertion:

```text
id
shopId
kind
requestKey
requestFingerprint
merchantPricingPlanId
merchantPricingUsageEventId
quotedAmountMinor
quotedCurrency
quotedBillingPeriod
recoveryCreditPurchaseId
```

The guard MUST permit legitimate workflow/result updates to:

```text
state
confirmationUrl
lastErrorCode
updatedAt
```

`providerContractId` has bounded write-once semantics:

```text
NULL -> non-blank value     allowed exactly once
non-null -> same value      allowed
non-null -> different value rejected
non-null -> NULL            rejected
```

This means `PLAN_SWITCH` and `CANCEL` snapshot their target recurring contract at insertion and cannot later be redirected to another Woo contract. `SUBSCRIPTION_CREATE` and `ONE_TIME_CHARGE` may attach the provider-created contract after the provider response, but that identity is immutable once known.

The guard MUST NOT block deletion. Deleting a `Shop` must still be able to cascade-delete its Woo billing operations.

### C. `WooCommerceBillingWebhookReceipt`

Add this logical model in PostgreSQL schema `woocommerce`:

```prisma
model WooCommerceBillingWebhookReceipt {
  id String @id @default(cuid()) @db.Text

  topic              String  @db.VarChar(128)
  providerContractId String? @db.VarChar(255)

  payloadSha256     Bytes
  normalizedPayload Json @db.JsonB

  receivedAt      DateTime  @default(now()) @db.Timestamptz(3)
  processedAt     DateTime? @db.Timestamptz(3)
  processingError String?   @db.VarChar(2000)

  @@unique([topic, payloadSha256])
  @@index([providerContractId, receivedAt])
  @@index([processedAt, receivedAt])
  @@schema("woocommerce")
}
```

#### Webhook receipt semantics

`payloadSha256` is exactly 32 bytes and represents the SHA-256 digest of the exact raw request body over which the API verified the Woo signature.

`normalizedPayload` is the bounded canonical payload accepted after signature verification. The raw signature, Woo vendor credential and raw Authorization header MUST NOT be stored.

Webhook dedupe is exactly:

```text
UNIQUE(topic, payloadSha256)
```

Do **not** include nullable `providerContractId` in the dedupe key. PostgreSQL nullable uniqueness semantics must not allow duplicate exact deliveries merely because the provider contract identifier is absent.

The database MUST enforce:

```text
btrim(topic) <> ''
octet_length(payloadSha256) = 32

providerContractId IS NULL
OR btrim(providerContractId) <> ''

processedAt IS NULL
OR processingError IS NULL
```

A failed processing attempt may leave:

```text
processedAt = NULL
processingError = <bounded latest error>
```

A successfully processed receipt has:

```text
processedAt IS NOT NULL
processingError IS NULL
```

Background retry/locking semantics are owned by later Background tasks; this database task supplies durable dedupe and processing evidence only.

#### Immutable webhook evidence

Add a deterministic update guard in schema `woocommerce`:

```text
function:
    woocommerce.arch027_woocommerce_billing_webhook_receipt_guard()

trigger:
    arch027_woocommerce_billing_webhook_receipt_guard
```

The guard MUST reject updates that change:

```text
id
topic
providerContractId
payloadSha256
normalizedPayload
receivedAt
```

It MUST permit updates to:

```text
processedAt
processingError
```

It MUST NOT prevent deletion.

### D. `BillingPeriodEntitlementCounter.currentAllowanceQuantity`

Add:

```prisma
currentAllowanceQuantity Int?
```

to `billing.BillingPeriodEntitlementCounter`.

Add a database check:

```text
currentAllowanceQuantity IS NULL
OR currentAllowanceQuantity >= 0
```

Do not backfill existing rows. Existing Shopify rows remain:

```text
currentAllowanceQuantity = NULL
```

The provider-neutral availability contract for follow-on code is:

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

The existing `BillingPeriodEntitlementCounter_capacity` database constraint MUST remain in force:

```text
committedQuantity
+ reservedQuantity
+ forfeitedQuantity
<= grantedQuantity
```

To preserve that invariant while allowing a Woo allowance increase, follow-on writers MUST obey:

```text
when target allowance > grantedQuantity:
    atomically raise grantedQuantity to at least target allowance
    and set currentAllowanceQuantity = target allowance

when target allowance <= grantedQuantity:
    do not lower grantedQuantity
    set currentAllowanceQuantity = target allowance
```

Therefore:

- `grantedQuantity` remains the non-decreasing current-period historical/high-water grant used by existing close/audit invariants;
- `currentAllowanceQuantity` is the mutable current spend ceiling;
- a downgrade may legitimately produce `committed + reserved > currentAllowanceQuantity`;
- the existing capacity constraint remains satisfied because `grantedQuantity` is not reduced;
- follow-on reservation code, not this migration, must gate new reservations against the effective current allowance.

This task MUST NOT alter existing Shopify plan-change runtime behaviour.

### E. `Subscription.providerSubscriptionId` lookup index and Woo recurring-contract projection

Add exactly a non-unique index:

```prisma
@@index([providerSubscriptionId])
```

Do not make `providerSubscriptionId` unique in this task.

Preserve the existing cardinality invariant:

```text
Subscription.shopId UNIQUE
=> at most one Moda Subscription per Shop
```

For Woo recurring billing, `Subscription.providerSubscriptionId` is the **current Woo recurring subscription contract UUID projected after verified provider evidence**. It is not the Shop identity, Woo installation identity or merchant identity.

A plan switch operates on the existing recurring Woo contract and changes the plan projection; it does not create a second Moda `Subscription` row. Cancellation likewise acts on the same current recurring contract.

A Woo one-time-charge contract UUID MUST NOT be projected to `Subscription.providerSubscriptionId`. One-time charge identity belongs to `WooCommerceBillingOperation.providerContractId` and the associated `RecoveryCreditPurchase.providerReference`/provider evidence.

Historical recurring-contract identity is retained by operation/webhook evidence. `Subscription.providerSubscriptionId` represents the current projected external subscription contract only; it is not intended to be an immutable history table.

For a Woo Shop on the Moda Free plan, the Shop still has the normal single Moda `Subscription`, but `Subscription.providerSubscriptionId` MAY be `NULL` because there is no recurring Woo billing contract. That nullable recurring-contract state MUST NOT prevent independent Woo `ONE_TIME_CHARGE` operations or Woo `RecoveryCreditPurchase` rows.

### F. `RecoveryCreditPurchase` provider-neutral acquisition evidence

A Woo merchant on the local Moda Free plan has no `BillingPeriod`, but ARCH-027 explicitly allows that merchant to buy predefined top-up bundles. Therefore make the existing acquisition-period relation nullable:

```prisma
billingPeriodId String?
billingPeriod   BillingPeriod? @relation(
  "RecoveryCreditPurchaseBillingPeriod",
  fields: [billingPeriodId],
  references: [id],
  onDelete: Restrict
)
```

Retain the existing billing-period index; nullable values are valid Woo acquisition context.

Provider-conditional period semantics are:

```text
provider = SHOPIFY
    billingPeriodId MUST be non-null

provider = WOOCOMMERCE
    billingPeriodId MAY be null
```

The database cannot determine whether a Woo purchase was made while the Shop was Free or Paid. The follow-on API command owns the stronger runtime rule:

```text
Woo Free purchase
    -> billingPeriodId = NULL

Woo paid purchase
    -> billingPeriodId = current OPEN Subscription.billingPeriodId
```

Existing Shopify rows remain non-null through migration; do not backfill or manufacture a BillingPeriod for Woo Free.

Add:

```prisma
provider          String  @default("SHOPIFY") @db.VarChar(32)
providerReference String? @db.VarChar(512)
```

Make these existing fields nullable:

```prisma
shopifyPlanHandleSnapshot               String?
shopifyEventHandleSnapshot              String?
providerSubscriptionIdSnapshot          String?
providerUsageQuantityBeforeSnapshot     Decimal?
providerUsageCostBeforeSnapshot         Decimal?
providerUsageCostCurrencyBeforeSnapshot String? @db.VarChar(3)

usageEventId String? @unique
usageEvent   UsageEvent?
```

The existing provider-after fields remain nullable as they already are.

Do not remove:

```text
providerPurchaseAmount
providerPurchaseCurrency
providerValuationConfirmedAt
providerPriceSnapshot
```

They remain the generic purchase valuation/evidence fields used by both providers.

Add/retain the one-to-one inverse relation to `WooCommerceBillingOperation` required by `recoveryCreditPurchaseId`.

#### Purchase provider discriminator

The database MUST accept exactly:

```text
SHOPIFY
WOOCOMMERCE
```

for `RecoveryCreditPurchase.provider`.

Existing rows MUST migrate deterministically to:

```text
provider = SHOPIFY
```

No Woo purchase row is seeded by the migration.

#### Shopify purchase evidence

For `provider = SHOPIFY`, preserve the current acquisition contract:

```text
shopifyPlanHandleSnapshot               non-null and non-blank
shopifyEventHandleSnapshot              non-null and non-blank
providerSubscriptionIdSnapshot          non-null and non-blank
providerUsageQuantityBeforeSnapshot     non-null
providerUsageCostBeforeSnapshot         non-null
providerUsageCostCurrencyBeforeSnapshot non-null
usageEventId                            non-null
```

For every non-`REQUESTED` Shopify purchase, preserve the accepted valuation proof:

```text
providerUsageQuantityAfterSnapshot      non-null
providerUsageQuantityAfterSnapshot      > providerUsageQuantityBeforeSnapshot

providerUsageCostAfterSnapshot          non-null
providerUsageCostCurrencyAfterSnapshot  non-null

providerPurchaseAmount                  non-null and >= 0
providerPurchaseCurrency                non-null
providerValuationConfirmedAt            non-null
providerPriceSnapshot                   non-null

before/after/purchase currencies equal

providerUsageCostAfterSnapshot >= providerUsageCostBeforeSnapshot

providerPurchaseAmount =
    providerUsageCostAfterSnapshot
    - providerUsageCostBeforeSnapshot
```

The zero monetary delta already supported for valid Shopify development/provider-meter behavior MUST remain valid.

#### Woo purchase evidence

For `provider = WOOCOMMERCE`, Shopify meter-acquisition evidence MUST NOT be fabricated:

```text
shopifyPlanHandleSnapshot               IS NULL
shopifyEventHandleSnapshot              IS NULL
providerUsageQuantityBeforeSnapshot     IS NULL
providerUsageCostBeforeSnapshot         IS NULL
providerUsageCostCurrencyBeforeSnapshot IS NULL
providerUsageQuantityAfterSnapshot      IS NULL
providerUsageCostAfterSnapshot          IS NULL
providerUsageCostCurrencyAfterSnapshot  IS NULL
usageEventId                            IS NULL
```

`providerSubscriptionIdSnapshot` MAY be null because a Woo one-time charge does not require a recurring Woo contract. This explicitly includes a Woo Shop whose single Moda `Subscription` is the Free plan and has `providerSubscriptionId = NULL`.

For every non-`REQUESTED` Woo purchase require:

```text
providerReference            non-null and non-blank
providerPurchaseAmount       non-null and > 0
providerPurchaseCurrency     non-null, three uppercase ASCII letters
providerValuationConfirmedAt non-null
providerPriceSnapshot        non-null
```

`providerReference` is the Woo charge/contract provider reference for the purchase.

The migration MUST replace the current Shopify-only `RecoveryCreditPurchase_confirmed_valuation_complete` predicate with provider-conditional semantics that preserve current Shopify behavior exactly and permit the Woo evidence shape above.

The existing purchase-lot invariants remain unchanged:

```text
creditsGranted > 0

0 <= currentAmount <= creditsGranted
0 <= reservedAmount <= currentAmount

REQUESTED:
    currentAmount = 0
    reservedAmount = 0

ACTIVE:
    currentAmount > 0

WITHDRAWN:
    currentAmount > 0

COMPLETED / REFUNDED:
    currentAmount = 0
    reservedAmount = 0
```

### G. `RecoveryCreditRefund` provider-neutral settlement evidence

Add:

```prisma
provider String @default("SHOPIFY") @db.VarChar(32)
```

Make these existing Shopify-context snapshots nullable:

```prisma
billingPeriodIdSnapshot        String?
providerSubscriptionIdSnapshot String?
planHandleSnapshot             String?
eventHandleSnapshot            String?
```

`billingPeriodIdSnapshot` must become nullable because an accepted Woo Free purchase has no `BillingPeriod` but may still enter the generic refund lifecycle.

Do not create a new Woo refund table.

Continue to reuse the existing generic provider result fields:

```text
providerReference
providerActionKind
providerAmount
providerCurrency
providerConfirmedByPlatformAdminId
providerConfirmedAt
```

#### Refund provider discriminator

The database MUST accept exactly:

```text
SHOPIFY
WOOCOMMERCE
```

for `RecoveryCreditRefund.provider`.

Existing refund rows MUST migrate deterministically to:

```text
provider = SHOPIFY
```

The implementing code/migration must prove every existing refund's `provider` matches the referenced existing purchase's defaulted provider.

#### Shopify refund evidence

For `provider = SHOPIFY`, preserve current snapshot requirements:

```text
billingPeriodIdSnapshot        non-null and non-blank
providerSubscriptionIdSnapshot non-null and non-blank
planHandleSnapshot             non-null and non-blank
eventHandleSnapshot            non-null and non-blank
```

The existing partner-development snapshot and automatic negative/fractional App Event correction behavior remain valid.

#### Woo refund evidence

For `provider = WOOCOMMERCE`:

```text
billingPeriodIdSnapshot        MAY be null
providerSubscriptionIdSnapshot MAY be null
planHandleSnapshot             IS NULL
eventHandleSnapshot            IS NULL

shopifyPartnerDevelopmentSnapshot = false

automaticCorrectionUsageEventId              IS NULL
providerUsageQuantityBeforeCorrection        IS NULL
providerUsageCostBeforeCorrection            IS NULL
expectedProviderUsageQuantityAfterCorrection IS NULL
expectedProviderUsageCostAfterCorrection     IS NULL
```

A Woo refund MUST NOT fabricate a Shopify correction `UsageEvent`.

For a Woo refund with:

```text
status = COMPLETED
```

require verified provider settlement evidence:

```text
providerReference   non-null and non-blank
providerAmount      non-null and >= 0
providerCurrency    non-null, three uppercase ASCII letters
providerConfirmedAt non-null
```

`providerConfirmedByPlatformAdminId` MAY remain null when confirmation came from verified automated Woo provider evidence rather than a platform admin.

The existing generic refund quantity/economic invariants remain unchanged, including:

```text
availableAmountAtRequestSnapshot =
    currentAmountAtRequestSnapshot
    - reservedAmountAtRequestSnapshot

availableAmountAtRequestSnapshot > 0

finalCreditQuantity <= currentAmountAtRequestSnapshot

expectedProviderAmount >= 0 when present
```

The existing ARCH-015 automatic-correction evidence-group check MUST be updated only as required to make that evidence path Shopify-only while preserving its current Shopify semantics.

### H. No schema redesign outside the listed delta

The physical migration MUST NOT:

- add `WooCommerceBillingOffer`;
- add `MerchantPricingProviderOffer`;
- add a generic `BillingOperation` table;
- add a generic provider-webhook table;
- add a new entitlement-period table;
- modify `MerchantPricingPlan` commercial price fields;
- modify `MerchantPricingUsageEvent` / `MerchantPricingUsageTier` commercial price fields;
- move or remove `shopifyPlanHandle`;
- replace or duplicate `BillingPlan`;
- make `BillingPlan` provider-specific;
- modify `BillingPeriod` structure;
- modify `UsageEvent` structure;
- modify `UsageReservation` structure;
- modify `WooCommerceInstallation` with billing fields;
- introduce Woo vendor credentials, API keys, secrets or webhook signing secrets into PostgreSQL.

## Out of Scope

- Woo Marketplace HTTP client.
- Woo vendor credential configuration.
- Woo `/subscriptions`, switch, cancel or `/charges` calls.
- HMAC verification implementation.
- API routes or HTTP contracts.
- WordPress/PHP plugin changes.
- Woo Admin React changes.
- Billing catalogue read models.
- Pricing calculation implementation.
- Extracting or introducing a runtime FIXED/GRADUATED/VOLUME evaluator for Woo; Woo v1 reads the stored price of a predefined FIXED bundle.
- `MerchantPricingPlan` -> `BillingPlan` materialisation implementation.
- Changing Shopify's `BillingPlanResolutionService`.
- Changing Shopify hosted-pricing callbacks.
- Provider lifecycle reconciliation.
- Background receipt polling/queueing/locking.
- Allowance reservation runtime changes.
- Woo Free activation runtime behavior.
- Woo renewal/cancellation runtime behavior.
- Woo top-up activation runtime behavior.
- Woo refund initiation.
- Woo arbitrary partial-refund capability.
- Woo sandbox validation.
- Admin support UI.
- Gateway/Render changes.
- Adding billing data to `WooCommerceInstallation`.
- A broad generic `BillingProvider` abstraction.
- Replacing ARCH-011 Shopify same-cycle plan-change semantics.
- Removing Shopify compatibility fields.
- Any repository other than `moda-interact-database` plus the assigned parent task report.

## Requirements

### R1 — One Moda pricing catalogue remains authoritative

No Woo-specific recurring/top-up pricing table is created.

`MerchantPricingPlan` remains the recurring commercial source.

`MerchantPricingUsageEvent` remains the Woo predefined-bundle source. For Woo v1, the API consumes only a directly priced `FIXED` event and snapshots its stored `fixedUnitAmountMinor` / `currency`; it does not recalculate `GRADUATED` / `VOLUME` schedules. `MerchantPricingUsageTier` remains an existing catalogue/Admin capability and receives no ARCH-027 schema change.

### R2 — Woo workflow uncertainty is durable

A Woo create/switch/charge/cancel attempt has one durable `WooCommerceBillingOperation` persisted before any provider POST.

`OUTCOME_UNKNOWN` is representable without pretending the provider operation failed or can be blindly retried.

### R3 — Operation retries have a durable command identity

`(shopId, requestKey)` is unique.

The same request key cannot be persisted twice.

Equal fingerprints with different request keys remain legal.

### R4 — Operation commercial intent is immutable

Catalogue references and exact stored-price quote snapshots cannot be rewritten after insertion.

Later catalogue edits cannot change historical provider intent.

### R5 — Webhook exact-delivery dedupe does not depend on nullable contract identity

`(topic, payloadSha256)` uniquely identifies an exact accepted Woo delivery.

A null `providerContractId` does not weaken dedupe.

### R6 — Webhook evidence is immutable after durable acceptance

Topic, provider contract identity, raw-payload digest, normalized snapshot and receipt timestamp cannot be rewritten.

Only processing result fields may change.

### R7 — Current allowance is distinct from high-water grant

`currentAllowanceQuantity` is nullable and non-negative.

Existing rows remain null.

A plan downgrade may set the current allowance below committed/reserved usage without invalidating historical state.

The existing high-water capacity constraint remains valid through non-decreasing `grantedQuantity`.

### R8 — Woo contract lookup is indexed without imposing false uniqueness

`Subscription.providerSubscriptionId` has a non-unique index.

### R9 — Woo billing operations preserve the one-Subscription-per-Shop domain

`Subscription.shopId` remains unique.

`WooCommerceBillingOperation` has no `subscriptionId` column or direct `Subscription` relation. Subscription-affecting operations are scoped by `shopId`; follow-on runtime code resolves the Shop's single current Subscription through the existing unique relation.

`providerContractId` is WooCommerce.com external contract identity. For recurring operations it identifies the current recurring Woo contract; for one-time charges it identifies the charge contract. A one-time-charge contract must never be treated as `Subscription.providerSubscriptionId`.

The operation guard allows a provider contract identity to be attached once when a create response returns it, then forbids replacement or clearing.

### R10 — Free Moda subscriptions may buy Woo top-ups without a recurring Woo contract

A Woo Shop may have its single current Moda `Subscription` on the Free `BillingPlan` with `Subscription.providerSubscriptionId = NULL`.

That state remains eligible for independent Woo `ONE_TIME_CHARGE` operations when the selected `MerchantPricingUsageEvent` belongs to the current Free plan and is a directly priced Woo-v1-eligible predefined bundle. One operation purchases one bundle; buying the same bundle again creates a new operation and a new `RecoveryCreditPurchase` lot.

The database MUST NOT require a recurring Woo contract, non-null `Subscription.providerSubscriptionId`, or synthetic zero-value `SUBSCRIPTION_CREATE` operation before a Woo one-time charge can be persisted.

If Woo later returns a one-time-charge contract UUID, that UUID remains charge/purchase evidence and MUST NOT become the Free Subscription's `providerSubscriptionId`.

### R11 — Existing Shopify purchase rows remain valid without data loss

Every existing `RecoveryCreditPurchase` becomes `provider = SHOPIFY`.

Existing required Shopify acquisition/valuation evidence remains preserved and required for Shopify rows.

No current zero-value Shopify valuation case is broken.

### R12 — Woo purchases require Woo evidence, not fake Shopify meter evidence

A Woo purchase can exist with no purchase-acquisition `UsageEvent` and no Shopify meter snapshots.

Once it leaves `REQUESTED`, it requires Woo provider reference and validated monetary/price evidence.

### R13 — Existing Shopify refund rows remain valid without data loss

Every existing `RecoveryCreditRefund` becomes `provider = SHOPIFY`.

Existing Shopify snapshot and automatic-correction semantics remain valid.

### R14 — Woo refunds reuse the generic refund ledger

A Woo refund is an existing `RecoveryCreditRefund` with `provider = WOOCOMMERCE`.

It does not create a Woo-specific refund ownership table.

A completed Woo refund must have verified provider settlement evidence.

### R15 — Woo refund rows cannot masquerade as Shopify correction flows

Woo refund rows must have no Shopify plan/event snapshots, no partner-development flag and no automatic Shopify correction usage evidence.

### R16 — `WooCommerceInstallation` remains installation/authentication state only

No billing-plan, subscription, provider-contract, price or charge fields are added to `WooCommerceInstallation`.

### R17 — No Woo billing rows are seeded

The migration creates schema capability only.

No Woo billing operation, receipt, purchase, refund, subscription or billing-period fixture/production row is inserted.

### R18 — Existing core billing models are preserved

No physical schema replacement/duplication occurs for:

```text
MerchantPricingPlan
MerchantPricingUsageEvent
MerchantPricingUsageTier
BillingPlan
BillingPeriod
UsageEvent
UsageReservation
```

except the explicitly authorised inverse Prisma relation metadata and `Subscription.providerSubscriptionId` index.

## Work Items

- [ ] Re-read the accepted ARCH-026-DATABASE-002 task and verify it is `complete` before claiming this task.
- [ ] Verify the launcher-prepared parent and database worktrees are dedicated to `ARCH-027-DATABASE-001` and synchronized from current `origin/main`.
- [ ] Inspect the current `moda-interact-database/package.json` before choosing validation commands.
- [ ] Register no new PostgreSQL schema; consume the accepted ARCH-026 `woocommerce` schema.
- [ ] Add `WooCommerceBillingOperationKind`.
- [ ] Add `WooCommerceBillingOperationState`.
- [ ] Add `WooCommerceBillingOperation` with the exact command identity, catalogue references, quote snapshots, provider result fields, relations, uniqueness and indexes defined above, with **no `subscriptionId` column or direct `Subscription` relation**.
- [ ] Add deterministic operation shape/currency/digest/non-blank/confirmed-evidence constraints, including required recurring `providerContractId` for `PLAN_SWITCH` / `CANCEL`.
- [ ] Add provider-contract write-once enforcement: allow only `NULL -> non-blank` attachment for create/charge, then reject change/clear.
- [ ] Prove the existing `Subscription.shopId` unique constraint remains unchanged and no second Woo subscription relation/model is introduced.
- [ ] Prove the schema permits a Woo Shop's single Moda Free `Subscription` to have `providerSubscriptionId = NULL` while independently persisting a valid Woo `ONE_TIME_CHARGE` and Woo `RecoveryCreditPurchase`; do not add or require a synthetic zero-value `SUBSCRIPTION_CREATE`.
- [ ] Prove `WooCommerceBillingOperation` has no quantity field: one `ONE_TIME_CHARGE` references one predefined `MerchantPricingUsageEvent` bundle and snapshots one stored bundle price.
- [ ] Add `arch027_woocommerce_billing_operation_guard()` and its trigger.
- [ ] Add `WooCommerceBillingWebhookReceipt`.
- [ ] Add exact-delivery dedupe on `(topic, payloadSha256)`.
- [ ] Add receipt digest/non-blank/processing-state constraints.
- [ ] Add `arch027_woocommerce_billing_webhook_receipt_guard()` and its trigger.
- [ ] Add nullable `BillingPeriodEntitlementCounter.currentAllowanceQuantity`.
- [ ] Add its non-negative constraint without backfilling existing rows.
- [ ] Preserve `BillingPeriodEntitlementCounter_capacity` unchanged.
- [ ] Add the non-unique `Subscription.providerSubscriptionId` index.
- [ ] Make `RecoveryCreditPurchase.billingPeriodId` / `billingPeriod` nullable so Woo Free top-ups do not require a fabricated BillingPeriod, while provider-conditional constraints continue to require a billing period for Shopify purchases.
- [ ] Add `RecoveryCreditPurchase.provider` and `providerReference`.
- [ ] Make the explicitly listed Shopify purchase-acquisition fields and `usageEventId` nullable.
- [ ] Make the `UsageEvent` relation optional without changing the `UsageEvent` table.
- [ ] Replace purchase evidence/valuation checks with the exact provider-conditional semantics above.
- [ ] Prove current Shopify zero-value provider valuation remains valid.
- [ ] Add `RecoveryCreditRefund.provider`.
- [ ] Make `RecoveryCreditRefund.billingPeriodIdSnapshot` nullable for Woo Free refund provenance while retaining non-null Shopify refund requirements.
- [ ] Make the explicitly listed Shopify refund-context fields nullable.
- [ ] Make ARCH-015 automatic correction evidence Shopify-only without changing valid Shopify behavior.
- [ ] Add Woo completed-refund provider-evidence validation.
- [ ] Create exactly one migration ending `_arch027_woocommerce_billing_persistence` and ensure it sorts after the accepted ARCH-026-DATABASE-002 migration.
- [ ] Add static schema validation for all exact model/enum/index/constraint/guard requirements.
- [ ] Add static migration validation proving the migration contains no forbidden pricing/provider-offer/entitlement redesign.
- [ ] Add disposable PostgreSQL fresh migration rehearsal.
- [ ] Add disposable PostgreSQL upgrade rehearsal from the immediately preceding accepted migration history.
- [ ] Seed representative pre-ARCH-027 Shopify subscription/counter/purchase/refund data into the upgrade rehearsal and prove it survives exactly as Shopify data.
- [ ] Add PostgreSQL positive/negative cases for operation kind shapes, provider-contract requirements/write-once semantics and immutable snapshots.
- [ ] Add PostgreSQL positive/negative cases for webhook dedupe, hash length and immutable evidence.
- [ ] Add PostgreSQL positive/negative cases for nullable/current allowance behavior.
- [ ] Add PostgreSQL positive/negative cases for Shopify and Woo purchase evidence.
- [ ] Add PostgreSQL positive/negative cases for Shopify and Woo refund evidence.
- [ ] Prove no Woo billing rows are seeded.
- [ ] Prove `WooCommerceInstallation` shape is not changed by this task.
- [ ] Prove `MerchantPricingPlan`, `MerchantPricingUsageEvent`, `MerchantPricingUsageTier`, `BillingPlan`, `BillingPeriod`, `UsageEvent` and `UsageReservation` have no unauthorised physical schema changes.
- [ ] Add focused package scripts for ARCH-027 schema, migration and PostgreSQL validation.
- [ ] Regenerate the Prisma ERD through the repository's canonical generator.
- [ ] Run `git diff --check`.
- [ ] Record exact validation and physical worktree evidence in the Completion Report.

## Interfaces / Contracts

This task creates database contracts only. It does not create an HTTP or queue contract.

### Woo operation persistence contract

Owner:

`ARCH-027-DATABASE-001`

Durable model:

`woocommerce.WooCommerceBillingOperation`

Consumers:

```text
moda-interact-api
    creates/updates provider-edge operations

moda-interact-background
    reads verified operations while projecting provider outcomes

moda-interact-admin
    may later read operation evidence for support/audit views
```

The database does not perform Woo price calculation or provider calls.

### One Subscription per Shop / Woo provider contract mapping

Existing Moda cardinality:

```text
Shop 1 -> 0..1 Subscription
Subscription.shopId UNIQUE
```

`WooCommerceBillingOperation` is **not** a child subscription identity. It is a Shop-scoped provider workflow/history row.

For subscription-affecting Woo operations:

```text
WooCommerceBillingOperation.shopId
        -> Subscription WHERE Subscription.shopId = shopId
```

Provider identity mapping:

```text
Woo recurring contract UUID
        -> WooCommerceBillingOperation.providerContractId
        -> after verified projection, Subscription.providerSubscriptionId

Woo one-time charge contract UUID
        -> WooCommerceBillingOperation.providerContractId
        -> RecoveryCreditPurchase.providerReference / provider evidence
        -> NEVER Subscription.providerSubscriptionId
```

The contract UUID is external WooCommerce.com billing evidence; it is not a Moda tenant, merchant, installation or internal subscription-row identifier.

### Woo Free subscription / one-time top-up contract

A Woo Shop on Free remains represented by the normal single Moda subscription:

```text
Shop
    -> Subscription
        plan = Free BillingPlan
        providerSubscriptionId = NULL
```

That state does not require a recurring Woo contract and does not block one-time credit purchases:

```text
Free Moda Subscription
        +
MerchantPricingUsageEvent belonging to the current Free plan
        -> WooCommerceBillingOperation(kind = ONE_TIME_CHARGE)
        -> Woo charge contract UUID when returned
        -> RecoveryCreditPurchase provider evidence
```

The follow-on API owns current-plan membership and Woo-v1 bundle eligibility validation. It must require a directly priced `FIXED` event and read the authoritative stored `fixedUnitAmountMinor` / `currency`; it must not run tier arithmetic for Woo. The database owns only the durable operation/purchase shapes and MUST NOT introduce a recurring-contract prerequisite. A Woo one-time-charge contract UUID MUST remain operation/purchase evidence and MUST NOT populate `Subscription.providerSubscriptionId`.

For that Free flow, `RecoveryCreditPurchase.billingPeriodId = NULL` is valid and intentional. A Woo Free top-up MUST NOT create a synthetic `BillingPeriod` merely to satisfy purchase acquisition persistence. Shopify purchases continue to require their current billing period.

### Woo webhook receipt contract

Owner:

`ARCH-027-DATABASE-001`

Durable model:

`woocommerce.WooCommerceBillingWebhookReceipt`

Producer:

`moda-interact-api`

Consumer:

`moda-interact-background`

Durable acceptance identity:

```text
topic
+
SHA-256(exact signed raw body)
```

Runtime payload validation/normalisation is owned by the later Shared/API contract tasks.

### Current allowance contract

Owner:

`ARCH-027-DATABASE-001`

Field:

`billing.BillingPeriodEntitlementCounter.currentAllowanceQuantity`

Consumer contract:

```text
effectiveAllowance =
    currentAllowanceQuantity
    ?? grantedQuantity
```

Writers raising the allowance above `grantedQuantity` must raise the high-water grant atomically.

Writers lowering the allowance must not lower the historical/high-water grant.

### Purchase provider contract

Owner:

`ARCH-027-DATABASE-001`

Values:

```text
SHOPIFY
WOOCOMMERCE
```

`RecoveryCreditPurchase` remains the provider-neutral durable credit lot.

### Refund provider contract

Owner:

`ARCH-027-DATABASE-001`

Values:

```text
SHOPIFY
WOOCOMMERCE
```

`RecoveryCreditRefund` remains the provider-neutral durable refund lifecycle.

## Dependencies

- `ARCH-026-DATABASE-002`

`ARCH-026-DATABASE-002` already depends on `ARCH-026-DATABASE-001`, so this single dependency guarantees:

- `commerce.Shop` has the accepted provider-neutral foundation;
- PostgreSQL schema `woocommerce` exists and is registered with Prisma;
- `WooCommerceInstallation` exists;
- ARCH-026 database migrations have a deterministic serial order;
- no ARCH-026/ARCH-027 database task is concurrently modifying the same Prisma schema/migration frontier.

This is an execution/serialization dependency as well as an architectural prerequisite.

## Enables

- `ARCH-027-SHOPIFY-001`
- `ARCH-027-API-001`
- `ARCH-027-API-002`
- `ARCH-027-API-003`
- `ARCH-027-API-004`
- `ARCH-027-BACKGROUND-001`
- `ARCH-027-BACKGROUND-002`
- `ARCH-027-BACKGROUND-003`
- `ARCH-027-ADMIN-002`

These tasks are not executable merely because this file lists them under `Enables`. Each must still exist, have all of its own dependencies `complete`, and be explicitly made `ready` by `moda_architect`.

## Acceptance Criteria

- [ ] `WooCommerceBillingOperationKind` exists in `woocommerce` with exactly `SUBSCRIPTION_CREATE`, `PLAN_SWITCH`, `ONE_TIME_CHARGE`, `CANCEL`.
- [ ] `WooCommerceBillingOperationState` exists in `woocommerce` with exactly `INITIATING`, `AWAITING_CONFIRMATION`, `CONFIRMED`, `OUTCOME_UNKNOWN`, `FAILED`.
- [ ] `WooCommerceBillingOperation` exists in `woocommerce`, not `billing` or `commerce`.
- [ ] `WooCommerceBillingOperation` has no `subscriptionId` column, FK or Prisma relation to `Subscription`.
- [ ] Existing `Subscription.shopId` uniqueness remains unchanged, preserving at most one Moda Subscription per Shop.
- [ ] `(shopId, requestKey)` is unique.
- [ ] `requestFingerprint` must be exactly 32 bytes.
- [ ] Identical request fingerprints with different request keys are accepted.
- [ ] Operation kind shape constraints accept all four valid shapes and reject cross-kind field mixtures.
- [ ] `WooCommerceBillingOperation` has no `requestedQuantity` column; one `ONE_TIME_CHARGE` represents one predefined bundle purchase.
- [ ] `quotedCurrency`, when present, is three uppercase ASCII letters.
- [ ] The database does not require `quotedCurrency = USD`.
- [ ] `CONFIRMED` operation rows require a provider contract reference.
- [ ] `PLAN_SWITCH` and `CANCEL` require the existing recurring Woo `providerContractId` at insertion.
- [ ] `SUBSCRIPTION_CREATE` and `ONE_TIME_CHARGE` may start with null `providerContractId` and attach the provider-created contract exactly once.
- [ ] Once non-null, an operation `providerContractId` cannot be changed or cleared.
- [ ] `OUTCOME_UNKNOWN` permits a null provider contract reference.
- [ ] Operation intent/quote fields are immutable after insert.
- [ ] Operation result/workflow fields remain updateable.
- [ ] Shop deletion can cascade-delete Woo operations.
- [ ] `WooCommerceBillingWebhookReceipt` exists in `woocommerce`.
- [ ] Receipt dedupe is exactly `(topic, payloadSha256)` and does not rely on nullable `providerContractId`.
- [ ] Receipt payload SHA-256 must be exactly 32 bytes.
- [ ] Duplicate exact topic/payload receipt insertion is rejected even when `providerContractId` is null.
- [ ] Distinct payload hashes for the same topic remain insertable.
- [ ] Receipt evidence fields are immutable after insert.
- [ ] `processedAt` / `processingError` remain updateable under the required consistency rule.
- [ ] `BillingPeriodEntitlementCounter.currentAllowanceQuantity` exists as nullable `Int`.
- [ ] Existing rows upgrade with `currentAllowanceQuantity = NULL`.
- [ ] Negative current allowance is rejected.
- [ ] Existing `BillingPeriodEntitlementCounter_capacity` remains present and unchanged.
- [ ] `Subscription.providerSubscriptionId` has a non-unique index.
- [ ] The task contract explicitly maps verified Woo recurring contract UUIDs to the Shop's single current `Subscription.providerSubscriptionId` and excludes one-time-charge contract UUIDs from that field.
- [ ] A Woo Shop may have its single Moda Subscription on Free with `Subscription.providerSubscriptionId = NULL`.
- [ ] That Free/no-recurring-contract state can coexist with a valid `ONE_TIME_CHARGE` operation and Woo `RecoveryCreditPurchase`.
- [ ] The database task contract states that Woo v1 one-time charges use the selected event's stored `FIXED` bundle price and do not require runtime `GRADUATED` / `VOLUME` evaluation.
- [ ] The database does not require a recurring Woo contract or non-null `Subscription.providerSubscriptionId` before a one-time charge can be persisted.
- [ ] A zero-value `SUBSCRIPTION_CREATE` operation is rejected by the operation-shape constraints and is not required to represent Woo Free activation.
- [ ] A Woo one-time-charge contract UUID remains operation/purchase evidence and cannot become the Free Subscription's `providerSubscriptionId`.
- [ ] `RecoveryCreditPurchase.billingPeriodId` / relation are nullable after ARCH-027.
- [ ] Existing Shopify purchase rows remain non-null for `billingPeriodId` after upgrade.
- [ ] Provider-conditional purchase constraints reject a `SHOPIFY` purchase with null `billingPeriodId`.
- [ ] A `WOOCOMMERCE` purchase may persist with null `billingPeriodId`, enabling the accepted Free-plan top-up flow without a fabricated period.
- [ ] `RecoveryCreditPurchase.provider` exists, defaults existing/new unspecified rows to `SHOPIFY`, and accepts only `SHOPIFY` / `WOOCOMMERCE`.
- [ ] `RecoveryCreditPurchase.providerReference` exists and is nullable.
- [ ] Existing Shopify purchase rows preserve all original evidence and remain valid after upgrade.
- [ ] Shopify purchase acquisition still requires its Shopify snapshots and `usageEventId`.
- [ ] Current Shopify non-requested valuation semantics, including valid zero monetary delta, remain accepted.
- [ ] Woo purchase rows require no Shopify plan/event/usage-meter snapshots and no purchase-acquisition `UsageEvent`.
- [ ] A non-requested Woo purchase requires provider reference, positive provider amount, provider currency, provider valuation confirmation and provider price snapshot.
- [ ] Existing purchase lot amount/lifecycle constraints remain intact.
- [ ] `RecoveryCreditRefund.provider` exists, defaults existing/new unspecified rows to `SHOPIFY`, and accepts only `SHOPIFY` / `WOOCOMMERCE`.
- [ ] Existing Shopify refund rows preserve current snapshot and correction semantics.
- [ ] Existing Shopify refund rows remain non-null for `billingPeriodIdSnapshot` after upgrade.
- [ ] Provider-conditional refund constraints reject a `SHOPIFY` refund with null `billingPeriodIdSnapshot`.
- [ ] A `WOOCOMMERCE` refund may persist with null `billingPeriodIdSnapshot`, enabling refund of a Free-plan Woo top-up without a fabricated BillingPeriod.
- [ ] Woo refund rows cannot contain Shopify plan/event snapshots, partner-development evidence or automatic Shopify correction usage evidence.
- [ ] A completed Woo refund requires provider reference/amount/currency/confirmation evidence.
- [ ] No `WooCommerceBillingOffer` exists.
- [ ] No `MerchantPricingProviderOffer` exists.
- [ ] No generic `BillingOperation` or generic provider-webhook table is introduced.
- [ ] No new entitlement-period model is introduced.
- [ ] No billing fields are added to `WooCommerceInstallation`.
- [ ] `MerchantPricingPlan`, `MerchantPricingUsageEvent`, `MerchantPricingUsageTier`, `BillingPlan`, `BillingPeriod`, `UsageEvent` and `UsageReservation` have no unauthorised physical schema changes.
- [ ] The migration seeds no Woo billing business rows.
- [ ] Fresh migration rehearsal passes from the complete accepted migration history.
- [ ] Upgrade rehearsal passes from the immediately preceding accepted migration history with representative Shopify data.
- [ ] Prisma validation and client generation pass.
- [ ] Generated ERD reflects the accepted ARCH-027 delta.
- [ ] `git diff --check` passes.
- [ ] Dedicated parent/implementation worktree, synchronization, branch and push evidence are recorded in the Completion Report.

## Validation

Inspect the repository's current `package.json` first. Use the actual scripts that exist after the task adds the focused ARCH-027 scripts.

Required checks:

- [ ] clean dependency installation from the repository lockfile;
- [ ] `npm run format` followed by a clean diff for `prisma/schema.prisma`;
- [ ] `npm run validate`;
- [ ] `npm run prisma:generate`;
- [ ] `npm run test:arch027-woocommerce-billing-schema`;
- [ ] `npm run test:arch027-woocommerce-billing-migration`;
- [ ] `npm run test:arch027-woocommerce-billing:postgres -- --mode fresh`;
- [ ] `npm run test:arch027-woocommerce-billing:postgres -- --mode upgrade`;
- [ ] `npm run erd:puml`;
- [ ] focused catalog assertions for all ARCH-027 tables, enums, indexes, checks, FKs, functions and triggers;
- [ ] focused positive/negative PostgreSQL operation-shape tests, including recurring-contract requirements for switch/cancel and rejection of zero-value `SUBSCRIPTION_CREATE`;
- [ ] static/schema proof that `WooCommerceBillingOperation` contains no `requestedQuantity` field and the one-charge/one-bundle shape is enforced by the task contract;
- [ ] focused PostgreSQL positive proof that a Woo Shop with one Free Moda `Subscription` and `providerSubscriptionId = NULL` can persist a requested Woo purchase plus `ONE_TIME_CHARGE`, attach the returned charge contract UUID, and retain `Subscription.providerSubscriptionId = NULL`;
- [ ] focused positive/negative PostgreSQL provider-contract write-once tests;
- [ ] focused positive/negative PostgreSQL operation immutability tests;
- [ ] focused positive/negative PostgreSQL webhook dedupe/immutability tests;
- [ ] focused current-allowance tests;
- [ ] focused purchase-period nullability tests proving Shopify requires a BillingPeriod while Woo may omit it;
- [ ] focused Woo Free purchase test with `billingPeriodId = NULL`;
- [ ] focused Woo paid purchase test with a non-null current BillingPeriod snapshot;
- [ ] focused Shopify-purchase regression tests;
- [ ] focused Woo-purchase evidence tests;
- [ ] focused Shopify-refund regression tests;
- [ ] focused Woo-refund evidence tests;
- [ ] upgrade proof that existing Shopify purchase/refund/provider evidence is unchanged except deterministic `provider = SHOPIFY` and authorised nullability changes;
- [ ] static proof that no forbidden Woo/provider-offer/generic-billing/entitlement model was introduced;
- [ ] static proof that `WooCommerceInstallation` gained no billing fields;
- [ ] static proof that `WooCommerceBillingOperation` has no `subscriptionId` column/FK/relation and `Subscription.shopId` uniqueness remains present;
- [ ] `git diff --check`;
- [ ] repository-agent changed-file/worktree checks.

The PostgreSQL rehearsal MUST use disposable databases only.

Because the migration history includes pgvector, use the architecture-approved PostgreSQL runtime capable of replaying the full history, such as:

```text
pgvector/pgvector:pg17
```

The focused PostgreSQL script must accept explicit database URLs and MUST NOT discover or mutate arbitrary local/development/staging/production databases.

Use:

```text
ARCH027_FRESH_DATABASE_URL
ARCH027_UPGRADE_DATABASE_URL
```

and explicit:

```text
--mode fresh
--mode upgrade
```

If Docker/PostgreSQL is unavailable, record the exact validation blocker. Do not silently weaken or mark the required database proof as passed.

### Required upgrade rehearsal seed matrix

Before applying the ARCH-027 migration to the upgrade database, seed at minimum:

1. one representative Shopify `Subscription` with non-null `providerSubscriptionId`;
2. one open paid `BillingPeriod`;
3. one included-credit counter satisfying the existing capacity invariant;
4. one `REQUESTED` Shopify `RecoveryCreditPurchase`;
5. one provider-confirmed non-requested Shopify purchase with positive monetary delta;
6. one provider-confirmed non-requested Shopify purchase with valid zero monetary delta;
7. one Shopify `RecoveryCreditRefund` without automatic correction evidence;
8. one Shopify refund with complete ARCH-015 automatic correction evidence.

After migration prove:

```text
all purchase.provider = SHOPIFY
all refund.provider   = SHOPIFY

all original Shopify snapshots/evidence are byte/value equivalent

all original usageEventId values remain attached

currentAllowanceQuantity IS NULL for pre-existing counters

the existing Subscription.providerSubscriptionId value is unchanged

Subscription.shopId uniqueness remains present and unchanged

all rows satisfy the new provider-conditional constraints
```

### Required post-migration negative matrix

PostgreSQL tests must prove rejection of at least:

- invalid operation fingerprint length;
- blank operation request key;
- duplicate `(shopId, requestKey)`;
- subscription operation with a usage-event catalogue id;
- one-time charge with no purchase id;
- zero-value `SUBSCRIPTION_CREATE`;
- one-time charge with a recurring billing period snapshot;
- cancel operation carrying quote/catalogue fields;
- confirmed operation with no provider contract id;
- plan switch with no provider contract id;
- cancel with no provider contract id;
- replacement of a non-null operation provider contract id with a different value;
- clearing a non-null operation provider contract id;
- mutation of immutable operation quote/intent fields;
- receipt with invalid SHA-256 length;
- duplicate exact `(topic, payloadSha256)` with null contract id;
- mutation of accepted receipt evidence;
- negative `currentAllowanceQuantity`;
- invalid purchase provider value;
- Woo purchase with Shopify meter snapshot fields;
- Woo purchase with non-null purchase-acquisition `usageEventId`;
- non-requested Woo purchase without provider reference/valuation evidence;
- Shopify purchase missing required Shopify acquisition evidence;
- invalid refund provider value;
- Woo refund containing Shopify plan/event snapshots;
- Woo refund containing automatic Shopify correction evidence;
- completed Woo refund without provider settlement evidence.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set task status to review
        ->
commit/push implementation task branch
        ->
commit/push parent task-report branch
        ->
return to moda_architect
        ->
STOP
```

Do not begin Shared, API, Shopify, Background, Admin, Gateway or WooCommerce consumer work.

Do not begin an enabled task.

## Implementation Notes

### 1. Minimal-change architecture is mandatory

Earlier discussion considered a larger provider-neutral redesign with provider-offer tables and provider-specific evidence tables.

That is **not** this task.

ARCH-027 v1 deliberately keeps:

```text
one MerchantPricingPlan catalogue
one MerchantPricingUsageEvent/Tier catalogue
one BillingPlan operational model
one Subscription projection
one BillingPeriod model
one RecoveryCreditPurchase lot model
one RecoveryCreditRefund lifecycle
```

Provider differences are represented only where required for Woo workflow durability and conditional evidence.

### 2. Woo contract identity does not create another Moda Subscription

WooCommerce.com creates external contract UUIDs for recurring subscriptions and one-time charges. Those identifiers are provider evidence, not Moda tenant identities.

Keep the existing Moda cardinality:

```text
Shop 1 -> 0..1 Subscription
```

Do not add `subscriptionId` to `WooCommerceBillingOperation`. Subscription-affecting operations resolve the Shop's single Subscription using `shopId`.

For a recurring contract, verified provider reconciliation may set/update the current `Subscription.providerSubscriptionId`. A plan switch continues to act on that same recurring contract; it changes the plan projection, not the number of Subscription rows.

For a one-time charge, the Woo contract UUID belongs to the operation/purchase evidence and must never be copied into `Subscription.providerSubscriptionId`.

A Woo Free Shop therefore has a normal Moda `Subscription` with no recurring Woo contract and may still accumulate independent Woo one-time-charge contract references through top-up purchases. Those charge contracts do not change the one-Subscription-per-Shop invariant and do not turn the Free Subscription into a provider-backed recurring subscription.

Historical operations/receipts are where old or repeated provider contract references remain visible.

### 3. Do not infer billing provider from `WooCommerceInstallation`

`WooCommerceInstallation` authenticates the merchant-controlled plugin.

It is not the Woo financial contract and must not become the owner of:

```text
current plan
subscription status
provider contract id
charge id
billing amount
refund
```

### 4. Do not make catalogue deletion silently rewrite history

`WooCommerceBillingOperation` catalogue references use `ON DELETE RESTRICT`.

Historical operations snapshot the quote, but the referenced catalogue row must not disappear underneath accepted historical provider intent. Catalogue entries should be deactivated rather than deleted while referenced.

### 5. Do not make the Woo provider limitation a global currency rule

Woo v1 currently accepts USD through the Marketplace SaaS Billing API.

That restriction belongs to the API adapter.

The database only requires syntactically valid three-letter uppercase quoted/provider currencies.

### 6. Do not use webhook raw body as durable business payload

The exact raw body is used transiently by API signature verification.

Persist only:

```text
SHA-256(raw body)
+
bounded normalized payload
```

No Woo secret, signature or Authorization value belongs in these tables.

### 7. Do not weaken Shopify proof to make Woo fit

Where a current Shopify row has required meter/provider evidence, keep that requirement for `provider = SHOPIFY`.

Woo gets a different valid evidence branch.

Do not solve Woo support by making all provider evidence unconditionally optional.

### 8. `UsageEvent` remains unchanged

Woo consumption events may later use:

```text
provider = "WOOCOMMERCE"
shopifyReportState = NOT_APPLICABLE
```

but that is a runtime concern. This database task does not modify `UsageEvent`.

### 9. `grantedQuantity` and `currentAllowanceQuantity` have different jobs

Do not reinterpret `grantedQuantity` as the mutable current allowance.

The new nullable field is specifically required so a downgrade can reduce current availability without rewriting historical/current-period usage.

Keep the existing capacity invariant and high-water grant semantics intact.

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

- ARCH-026-DATABASE-002 will be architect-accepted and merged before this task executes.
- The accepted ARCH-026 database work creates/registers PostgreSQL schema `woocommerce`.
- Woo v1 uses the existing Moda `MerchantPricingPlan` / `MerchantPricingUsageEvent` catalogue rather than provider-specific pricing tables.
- Woo Free activation does not require a Woo recurring billing operation, and a Free Shop may still purchase configured recovery-credit top-ups through independent Woo one-time charges.
- Existing `Subscription.shopId @unique` remains the authoritative one-Subscription-per-Shop invariant.
- Woo recurring and one-time charge contract IDs are WooCommerce.com external contract identifiers, not merchant/Moda identities.
- Woo one-time recovery-credit purchases continue to use the existing `RecoveryCreditPurchase` lot and existing required `BillingPeriod` association.
- Woo purchase acquisition does not create a fake Shopify purchase `UsageEvent`.
- Existing `RecoveryCreditRefund` provider result fields are sufficient for Woo settlement evidence.
- Exact Woo API/refund capabilities that require Marketplace sandbox access remain external validation gates and are not schema blockers.

### Unresolved Issues

None within this database task.

Woo sandbox behavior remains a later provider-integration/system-validation concern.

### Architectural Concerns

None.

Any implementation discovery that would require:

- a second pricing catalogue;
- a provider-offer table;
- a new entitlement-period model;
- changing `BillingPlan` identity;
- moving billing state into `WooCommerceInstallation`;
- changing Shopify purchase/refund business semantics rather than conditional provider evidence;
- adding another durable billing mechanism outside this task;

must be returned to `moda_architect` rather than implemented opportunistically.

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
