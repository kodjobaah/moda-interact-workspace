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
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-008-BACKGROUND-002
enables:
  - ARCH-009-SHARED-001
created: 2026-09-09
updated: 2026-09-10
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
Ready for Review

### Files Changed
- `prisma/schema.prisma`
- `prisma/migrations/20260910030000_add_billing_lifecycle_operations/migration.sql`
- `scripts/validate-billing-lifecycle-schema.mjs`
- `scripts/validate-recovery-credit-pack-schema.mjs`
- `package.json`
- `docs/generated/prisma-erd.puml`

### Work Completed
- Attempt 1 added the exact ARCH-009 durable schema, migration, relation arrays, validator, package script, and ERD.
- Attempt 2 strengthened `scripts/validate-billing-lifecycle-schema.mjs` with exact ordered enum membership assertions for all five new enums.
- Attempt 2 added exact migration SQL assertions for the three appended enum values and five newly-created enum value lists.

### Validation Results
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma 6.19.3.
- `npm run test:recovery-credit-packs`: passed.
- `npm run test:billing-lifecycle`: passed with exact enum and migration assertions.
- `npm run erd:puml`: passed; generated output was unchanged in Attempt 2.
- `git diff --check`: passed.

### Deviations
Attempt 2 was validator-only as requested. No schema, migration, or ERD changes were needed.

### Assumptions
The tracked database repository remains the authoritative owner of the Prisma schema and migration history; no live/shared database deployment was performed.

### Unresolved Issues
None

### Architectural Concerns
None

### Git / VCS

Task branch: `task/ARCH-009-DATABASE-001`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-009-DATABASE-001`
  parent branch: `task/ARCH-009-DATABASE-001`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-009-DATABASE-001`
  implementation branch: `task/ARCH-009-DATABASE-001`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: already-current
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: already-current
  implementation origin/main incorporated: already-current

Implementation repository:
  repository: `moda-interact-database`
  commit: `6e91680`
  remote branch: `origin/task/ARCH-009-DATABASE-001`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/database/ARCH-009/DATABASE-001-billing-lifecycle-operations.md`
  commit: `4c5f794`
  remote branch: `origin/task/ARCH-009-DATABASE-001`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 closes the sole Attempt 1 Changes Requested item and preserves the already-conformant ARCH-009 database design.

Verified correction:

- `scripts/validate-billing-lifecycle-schema.mjs` now parses the five new Prisma enums and asserts exact ordered membership with `assert.deepEqual`;
- the validator now asserts the full SQL `CREATE TYPE ... AS ENUM (...)` definitions for all five new lifecycle enums;
- migration validation also asserts:
  - `RecoveryCreditPurchaseStatus` appends `REFUNDED`;
  - `BillingAuditAction` appends `SUBSCRIPTION_CANCELLATION`;
  - `BillingAuditAction` appends `RECOVERY_CREDIT_REFUND`;
- the existing default/model/unique/index assertions remain in place.

Attempt 2 is correctly validator-only. Published commit `6e91680` changes only:

```text
scripts/validate-billing-lifecycle-schema.mjs
```

No change was made to `prisma/schema.prisma`, the lifecycle migration, ERD, package contract, or recovery-credit persistence model.

The architect directly reran from the supplied review archive:

```text
node scripts/validate-billing-lifecycle-schema.mjs
-> Billing lifecycle schema assertions passed.

node scripts/validate-recovery-credit-pack-schema.mjs
-> Recovery credit pack schema assertions passed.
```

The supplied archive does not contain `node_modules`, so Prisma validate/generate and ERD generation were not independently rerun in the architect container.

Agent-reported Attempt 2 validation:

- `npm run prisma:validate`: passed;
- `npm run prisma:generate`: passed with Prisma 6.19.3;
- `npm run test:recovery-credit-packs`: passed;
- `npm run test:billing-lifecycle`: passed;
- `npm run erd:puml`: passed with unchanged generated output;
- `git diff --check`: passed.

Published Git verification:

- implementation task branch tip: `6e916806649ab0cbf705656746f0aba02f67dc72`;
- Attempt 2 directly follows Attempt 1 `98bf7e1648c10a5fb5993f1daa4ea425ab1c7057`;
- database task branch is two commits ahead of `main`, zero behind;
- cumulative implementation changes remain limited to the six declared DATABASE-001 files;
- parent task branch tip: `c39a00027ada4d27208f33563b191e1ad89634ea`;
- dedicated parent/implementation worktree and start-of-attempt synchronization evidence is present and conformant;
- no implementation/workspace `main` branch or shared/live database was modified.

### Architecture Conformance

Accepted.

The durable ARCH-009 cancellation/refund lifecycle persistence contract is now complete and adequately regression-protected.

### Follow-up

`ARCH-009-SHARED-001` is now Ready because its sole authoritative dependency, `ARCH-009-DATABASE-001`, is Complete.

Proceed with `moda_shared` on the exact Shared 0.9.0 contract. Do not start downstream SHOPIFY/BACKGROUND/ADMIN tasks until SHARED-001 is architect-accepted Complete.
