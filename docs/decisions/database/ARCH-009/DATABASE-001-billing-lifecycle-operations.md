---
id: ARCH-009-DATABASE-001
architecture_id: ARCH-009
title: Persist cancellation and recovery-credit refund lifecycle operations
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-008-BACKGROUND-002
enables:
  - ARCH-009-SHARED-001
created: 2026-09-09
updated: 2026-09-09
---

# ARCH-009-DATABASE-001: Billing lifecycle persistence

## Objective

Add exact durable state for:

- human-approved subscription cancellation;
- full-pack refund;
- refund-capacity hold;
- provider confirmation;
- replay/concurrency-safe processing;
- audit.

## Required baseline

Confirm schema contains:

```text
Subscription
BillingPeriod
UsageEvent
RecoveryCreditPurchase
ShopEntitlementCounter
MerchantSupportMessage
PlatformAdmin
BillingAuditEvent
```

Expected RecoveryCreditPurchaseStatus:

```text
PENDING_BILLING
ACTIVE
NEEDS_ATTENTION
CANCELLED
```

If baseline differs, STOP and report exact drift.

## Exact Prisma enums

Add exactly:

```prisma
enum BillingLifecycleRequestSource {
  MERCHANT_UI
  MERCHANT_SUPPORT
  ADMIN

  @@schema("billing")
}

enum SubscriptionCancellationMode {
  END_OF_CYCLE
  IMMEDIATE_NO_PRORATION
  IMMEDIATE_PRORATED
  IMMEDIATE_SKIP_FINAL_USAGE

  @@schema("billing")
}

enum SubscriptionCancellationStatus {
  REQUESTED
  APPROVED
  PROCESSING
  RETRYABLE
  PROVIDER_ACCEPTED
  COMPLETED
  REJECTED
  WITHDRAWN
  NEEDS_ATTENTION

  @@schema("billing")
}

enum RecoveryCreditRefundSettlementMode {
  CURRENT_CYCLE_APP_EVENT_CORRECTION
  PARTNER_DASHBOARD_REFUND

  @@schema("billing")
}

enum RecoveryCreditRefundStatus {
  REQUESTED
  APPROVED
  PROCESSING
  PROVIDER_PENDING
  PROVIDER_ACTION_REQUIRED
  PROVIDER_CONFIRMED
  COMPLETED
  REJECTED
  WITHDRAWN
  NEEDS_ATTENTION

  @@schema("billing")
}
```

Extend RecoveryCreditPurchaseStatus with exactly:

```text
REFUNDED
```

Preserve all existing BillingAuditAction values and append:

```text
SUBSCRIPTION_CANCELLATION
RECOVERY_CREDIT_REFUND
```

## Exact counter change

Add to ShopEntitlementCounter:

```prisma
refundingQuantity Int @default(0)
```

## Exact model — SubscriptionCancellationRequest

```prisma
model SubscriptionCancellationRequest {
  id String @id @default(cuid())

  shopId String
  shop   Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)

  source BillingLifecycleRequestSource

  sourceMessageId String?
  sourceMessage MerchantSupportMessage? @relation(
    "SubscriptionCancellationSourceMessage",
    fields: [sourceMessageId],
    references: [id],
    onDelete: SetNull
  )

  requestedByShopifyUserId String?

  providerSubscriptionIdSnapshot String
  planHandleSnapshot String
  currentPeriodEndSnapshot DateTime?

  mode SubscriptionCancellationMode @default(END_OF_CYCLE)
  status SubscriptionCancellationStatus @default(REQUESTED)

  requestKey String @unique @db.VarChar(255)
  reason String? @db.VarChar(1000)

  approvedByPlatformAdminId String?
  approvedByPlatformAdmin PlatformAdmin? @relation(
    "ApprovedSubscriptionCancellations",
    fields: [approvedByPlatformAdminId],
    references: [id],
    onDelete: SetNull
  )
  approvedAt DateTime?

  version Int @default(0)
  attemptCount Int @default(0)
  nextAttemptAt DateTime?
  lastAttemptAt DateTime?
  processingStartedAt DateTime?

  providerAcceptedAt DateTime?
  providerErrorCode String? @db.VarChar(128)
  providerResponseSummary String? @db.VarChar(2000)

  completedAt DateTime?

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([shopId, status, createdAt])
  @@index([status, nextAttemptAt, createdAt])
  @@index([sourceMessageId])
  @@index([approvedByPlatformAdminId, createdAt])
  @@schema("billing")
}
```

requestKey:

```text
subscription-cancel:<shopId>:<providerSubscriptionIdSnapshot>
```

## Exact model — RecoveryCreditRefund

```prisma
model RecoveryCreditRefund {
  id String @id @default(cuid())

  shopId String
  shop Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)

  purchaseId String @unique
  purchase RecoveryCreditPurchase @relation(
    fields: [purchaseId],
    references: [id],
    onDelete: Restrict
  )

  source BillingLifecycleRequestSource

  sourceMessageId String?
  sourceMessage MerchantSupportMessage? @relation(
    "RecoveryCreditRefundSourceMessage",
    fields: [sourceMessageId],
    references: [id],
    onDelete: SetNull
  )

  requestedByShopifyUserId String?

  originalUsageEventIdSnapshot String
  billingPeriodIdSnapshot String?
  planHandleSnapshot String
  eventHandleSnapshot String
  creditsSnapshot Int

  settlementMode RecoveryCreditRefundSettlementMode?
  status RecoveryCreditRefundStatus @default(REQUESTED)

  requestKey String @unique @db.VarChar(255)
  reason String? @db.VarChar(1000)

  approvedByPlatformAdminId String?
  approvedByPlatformAdmin PlatformAdmin? @relation(
    "ApprovedRecoveryCreditRefunds",
    fields: [approvedByPlatformAdminId],
    references: [id],
    onDelete: SetNull
  )
  approvedAt DateTime?

  holdAppliedAt DateTime?

  correctionUsageEventId String? @unique
  correctionUsageEvent UsageEvent? @relation(
    "RecoveryCreditRefundCorrectionEvent",
    fields: [correctionUsageEventId],
    references: [id],
    onDelete: Restrict
  )

  providerReference String? @db.VarChar(512)

  providerConfirmedByPlatformAdminId String?
  providerConfirmedByPlatformAdmin PlatformAdmin? @relation(
    "ConfirmedRecoveryCreditRefunds",
    fields: [providerConfirmedByPlatformAdminId],
    references: [id],
    onDelete: SetNull
  )
  providerConfirmedAt DateTime?

  version Int @default(0)
  attemptCount Int @default(0)
  nextAttemptAt DateTime?
  lastAttemptAt DateTime?
  processingStartedAt DateTime?

  providerErrorCode String? @db.VarChar(128)
  providerResponseSummary String? @db.VarChar(2000)

  completedAt DateTime?

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([shopId, status, createdAt])
  @@index([status, nextAttemptAt, createdAt])
  @@index([sourceMessageId])
  @@index([approvedByPlatformAdminId, createdAt])
  @@index([providerConfirmedByPlatformAdminId, createdAt])
  @@schema("billing")
}
```

requestKey:

```text
recovery-credit-refund:<purchaseId>
```

One refund lifecycle row per purchase.

## Relation arrays

Add only required Prisma relation arrays to:

```text
Shop
MerchantSupportMessage
PlatformAdmin
RecoveryCreditPurchase
UsageEvent
```

Use explicit relation names from the models above.

## Migration

Create one migration:

```text
add_billing_lifecycle_operations
```

Do not modify historical migrations.

Do not deploy to shared/prod from task agent.

## Validation script

Create:

```text
scripts/validate-billing-lifecycle-schema.mjs
```

Assert:

- exact new enums;
- REFUNDED;
- new audit values;
- refundingQuantity default;
- both models;
- required unique/index fields;
- purchaseId unique;
- correctionUsageEventId unique;
- both requestKey unique.

Add package script:

```json
"test:billing-lifecycle": "node scripts/validate-billing-lifecycle-schema.mjs"
```

## Validation

Run:

```bash
npm run prisma:validate
npm run prisma:generate
npm run test:recovery-credit-packs
npm run test:billing-lifecycle
npm run erd:puml
git diff --check
```

## Out of scope

No app logic/provider/UI/partial refund/price field.

## Stop

Complete report -> review -> push mirrored task branches -> architect -> STOP.

## Completion Report

### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
None
### Deviations
None
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review

### Review Status
Pending
### Review Notes
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending
### Follow-up
None
