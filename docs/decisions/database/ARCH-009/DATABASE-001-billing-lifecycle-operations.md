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
status: review
priority: 10
executor: copilot
claimed_at: 2026-09-10T03:44:25Z
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
  commit: `PENDING` (final Attempt 2 report commit)
  remote branch: `origin/task/ARCH-009-DATABASE-001`
  pushed: pending
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 is architecturally sound at the schema and migration level, but the task's required validation contract is not fully implemented.

The new schema currently conforms to the task:

- the five ARCH-009 enums contain exactly the specified values;
- `RecoveryCreditPurchaseStatus` appends `REFUNDED`;
- `BillingAuditAction` preserves the existing values and appends `SUBSCRIPTION_CANCELLATION` and `RECOVERY_CREDIT_REFUND`;
- `ShopEntitlementCounter.refundingQuantity Int @default(0)` is present;
- `SubscriptionCancellationRequest` matches the specified persistence model;
- `RecoveryCreditRefund` matches the specified persistence model;
- the required Shop / MerchantSupportMessage / PlatformAdmin / RecoveryCreditPurchase / UsageEvent back-relations are present;
- `purchaseId`, `correctionUsageEventId`, and both `requestKey` fields have the required uniqueness;
- the required lifecycle indexes are present;
- the single `add_billing_lifecycle_operations` migration creates the required enum/table/index/foreign-key state and does not modify historical migration files;
- the generated ERD contains the new lifecycle entities, enums, refund hold counter and relationships;
- the only existing validator adjustment is whitespace-tolerance for Prisma formatting and does not change the recovery-credit contract;
- no price field, partial-refund persistence, app/provider logic, UI, or shared-database deployment was introduced.

### Required Correction — exact enum validation

The task explicitly requires `scripts/validate-billing-lifecycle-schema.mjs` to assert:

```text
exact new enums
```

The current validator uses `includesAll(...)` for each new enum. This proves that the required values exist, but it does not prove exact membership.

For example, this invalid schema would currently pass:

```prisma
enum SubscriptionCancellationMode {
  END_OF_CYCLE
  IMMEDIATE_NO_PRORATION
  IMMEDIATE_PRORATED
  IMMEDIATE_SKIP_FINAL_USAGE
  UNAUTHORISED_EXTRA_MODE
}
```

That is incompatible with ARCH-009's deterministic cancellation contract.

Attempt 2 must:

1. replace inclusion-only validation for the five new enums with exact ordered membership assertions;
2. parse/normalize enum values and use an equality assertion (for example `assert.deepEqual`) against these exact arrays:

```text
BillingLifecycleRequestSource
[
  MERCHANT_UI,
  MERCHANT_SUPPORT,
  ADMIN
]

SubscriptionCancellationMode
[
  END_OF_CYCLE,
  IMMEDIATE_NO_PRORATION,
  IMMEDIATE_PRORATED,
  IMMEDIATE_SKIP_FINAL_USAGE
]

SubscriptionCancellationStatus
[
  REQUESTED,
  APPROVED,
  PROCESSING,
  RETRYABLE,
  PROVIDER_ACCEPTED,
  COMPLETED,
  REJECTED,
  WITHDRAWN,
  NEEDS_ATTENTION
]

RecoveryCreditRefundSettlementMode
[
  CURRENT_CYCLE_APP_EVENT_CORRECTION,
  PARTNER_DASHBOARD_REFUND
]

RecoveryCreditRefundStatus
[
  REQUESTED,
  APPROVED,
  PROCESSING,
  PROVIDER_PENDING,
  PROVIDER_ACTION_REQUIRED,
  PROVIDER_CONFIRMED,
  COMPLETED,
  REJECTED,
  WITHDRAWN,
  NEEDS_ATTENTION
]
```

3. strengthen migration-side validation so the migration is also proven to contain:
   - `RecoveryCreditPurchaseStatus ADD VALUE 'REFUNDED'`;
   - `BillingAuditAction ADD VALUE 'SUBSCRIPTION_CANCELLATION'`;
   - `BillingAuditAction ADD VALUE 'RECOVERY_CREDIT_REFUND'`;
   - the exact SQL value lists for the five newly-created enums;
4. retain the existing uniqueness/index/default/model assertions;
5. do not change `prisma/schema.prisma` or the migration unless the strengthened validator exposes an actual discrepancy;
6. do not add new lifecycle states or persistence fields.

This is deliberately a validator-only correction unless exact validation discovers genuine source drift.

### Validation Reviewed

The architect directly reran from the supplied archive:

```text
node scripts/validate-billing-lifecycle-schema.mjs
-> Billing lifecycle schema assertions passed.

node scripts/validate-recovery-credit-pack-schema.mjs
-> Recovery credit pack schema assertions passed.
```

The archive does not contain `node_modules`, so Prisma validate/generate and ERD regeneration were not independently rerun in the architect container.

Agent-reported validation:

- `npm run prisma:validate`: passed;
- `npm run prisma:generate`: passed;
- `npm run test:recovery-credit-packs`: passed;
- `npm run test:billing-lifecycle`: passed;
- `npm run erd:puml`: passed;
- `git diff --check`: passed.

### Published Git Verification

- database task branch tip: `98bf7e1648c10a5fb5993f1daa4ea425ab1c7057`;
- database branch is one commit ahead of `main`, zero behind;
- changed implementation files are limited to the six declared database/schema/migration/validator/ERD/package files;
- parent task branch tip: `dca3542dfa158dc895e62feae15e58ee5965df4e`;
- worktree and start-of-attempt synchronization evidence is present and conforms to the workflow.

### Architecture Conformance

Changes required only in validation coverage.

### Follow-up

Attempt 2 must stay on the SAME `ARCH-009-DATABASE-001` task and mirrored `task/ARCH-009-DATABASE-001` branches.

After the validator correction:

1. rerun `npm run prisma:validate`;
2. rerun `npm run prisma:generate`;
3. rerun `npm run test:recovery-credit-packs`;
4. rerun `npm run test:billing-lifecycle`;
5. rerun `npm run erd:puml`;
6. rerun `git diff --check`;
7. update the Completion Report with the Attempt 2 implementation commit and validation results;
8. return the same task to `review`;
9. STOP.

`ARCH-009-SHARED-001` remains Pending until DATABASE-001 is architect-accepted Complete.
