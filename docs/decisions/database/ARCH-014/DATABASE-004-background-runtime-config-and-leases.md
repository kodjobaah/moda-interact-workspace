---
id: ARCH-014-DATABASE-004
architecture_id: ARCH-014
title: Add typed background runtime configuration, audit history and distributed leases
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 62
executor: copilot
claimed_at: 2026-09-15T23:53:05Z
attempt: 2
depends_on:
- ARCH-014-DATABASE-003
enables:
- ARCH-014-BACKGROUND-001
- ARCH-014-ADMIN-009
created: 2026-09-16
updated: 2026-09-15
---

# ARCH-014-DATABASE-004

## Objective

Create one additive, typed and concurrency-safe platform configuration foundation for all Admin-tunable background runtime controls.

Do **not** create a billing-only runtime-config table.

## Binding scope

Add only new database objects except for generated ERD/documentation updates.

Do not alter the physical columns/indexes/constraints of any existing table.

The new models live in schema `public`.

## Required enums

```prisma
enum BackgroundRuntimeConfigSection {
  OPERATIONAL
  ADVANCED
  ABUSE_PROTECTION
  WORKER_THROUGHPUT

  @@schema("public")
}

enum BackgroundRuntimeLeaseName {
  BILLING_RECONCILIATION
  RECOVERY_CAPACITY_REPAIR
  TRANSLATION_RECONCILIATION
  QUEUE_CONCURRENCY_RECONCILIATION

  @@schema("public")
}
```

## Required singleton model

Create:

```prisma
model BackgroundRuntimeConfig {
  id      String @id @default("default")
  version Int    @default(0)

  // Operational
  billingReconciliationIntervalSeconds Int @default(60)
  billingReconciliationShopBatchSize   Int @default(50)
  shopifyUsagePublishBatchSize         Int @default(50)

  recoveryRepairIntervalSeconds        Int @default(300)
  recoveryRepairShopBatchSize          Int @default(100)
  recoveryResumeBatchSize              Int @default(25)

  translationReconciliationIntervalSeconds Int @default(300)
  translationBatchMaxRequests              Int @default(100)

  conversationQuietWindowMs            Int @default(3000)
  conversationMaxSettleWindowMs        Int @default(10000)

  // Advanced
  billingFrozenRecheckSeconds          Int @default(3600)
  billingProviderRetrySeconds          Int @default(300)

  shopifyUsageRetryBaseSeconds         Int @default(60)
  shopifyUsageRetryMaxSeconds          Int @default(3600)

  translationReconciliationPageSize    Int @default(100)
  translationClaimTimeoutSeconds       Int @default(900)
  translationSubmitRetrySeconds        Int @default(300)
  translationInitialPollSeconds        Int @default(300)
  translationPollIntervalSeconds       Int @default(300)
  translationResultRetrySeconds        Int @default(300)
  translationSubmitMaxAttempts         Int @default(3)
  translationMaxAutoRetries            Int @default(3)

  // Abuse protection. Window lengths remain fixed in code.
  rawSenderLimitPerMinute                       Int @default(60)
  rawGlobalLimitPerMinute                       Int @default(20000)
  turnSenderLimitPerMinute                      Int @default(12)
  turnSenderLimitPerTenMinutes                  Int @default(60)
  turnConversationLimitPerMinute                Int @default(12)
  turnConversationLimitPerTenMinutes            Int @default(60)
  turnShopLimitPerMinute                        Int @default(600)
  turnGlobalLimitPerMinute                      Int @default(5000)
  discoverySenderLimitPerMinute                 Int @default(4)
  discoverySenderLimitPerTenMinutes             Int @default(12)
  discoveryConversationLimitPerMinute           Int @default(4)
  discoveryConversationLimitPerTenMinutes       Int @default(12)

  // Fleet-wide BullMQ queue concurrency.
  checkoutQueueGlobalConcurrency                Int @default(10)
  orderQueueGlobalConcurrency                   Int @default(5)
  pendingRecoveryQueueGlobalConcurrency         Int @default(10)
  recoveryResumeQueueGlobalConcurrency          Int @default(10)
  whatsappQueueGlobalConcurrency                Int @default(20)
  merchantCommunicationsQueueGlobalConcurrency  Int @default(10)
  billingSubscriptionQueueGlobalConcurrency     Int @default(10)

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  auditEvents BackgroundRuntimeConfigAuditEvent[]

  @@schema("public")
}
```

Do not rename fields or use JSON/key-value storage.

## Required audit model

```prisma
model BackgroundRuntimeConfigAuditEvent {
  id String @id @default(cuid())

  configId String
  config   BackgroundRuntimeConfig @relation(fields: [configId], references: [id], onDelete: Restrict)

  section          BackgroundRuntimeConfigSection
  expectedVersion  Int
  resultingVersion Int

  platformAdminId String
  reason          String @db.VarChar(1000)

  beforeValue Json
  afterValue  Json

  createdAt DateTime @default(now())

  @@index([configId, createdAt])
  @@index([platformAdminId, createdAt])
  @@schema("public")
}
```

`platformAdminId` is intentionally stored as the authenticated actor id without adding a relation/back-reference to the existing `PlatformAdmin` model. Do not alter `PlatformAdmin`.

## Required lease model

```prisma
model BackgroundRuntimeLease {
  name BackgroundRuntimeLeaseName @id

  ownerToken String
  generation Int @default(0)

  acquiredAt  DateTime
  heartbeatAt DateTime
  leaseUntil  DateTime
  updatedAt   DateTime @updatedAt

  @@index([leaseUntil])
  @@schema("public")
}
```

No seed lease rows.

## Exact database bounds

The migration MUST add named PostgreSQL CHECK constraints. Prisma-side validation alone is insufficient.

| Field | Min | Max |
|---|---:|---:|
| billingReconciliationIntervalSeconds | 10 | 3600 |
| billingReconciliationShopBatchSize | 1 | 200 |
| shopifyUsagePublishBatchSize | 1 | 200 |
| recoveryRepairIntervalSeconds | 30 | 3600 |
| recoveryRepairShopBatchSize | 1 | 500 |
| recoveryResumeBatchSize | 1 | 100 |
| translationReconciliationIntervalSeconds | 30 | 3600 |
| translationBatchMaxRequests | 1 | 500 |
| conversationQuietWindowMs | 250 | 10000 |
| conversationMaxSettleWindowMs | 1000 | 30000 |
| billingFrozenRecheckSeconds | 300 | 86400 |
| billingProviderRetrySeconds | 30 | 3600 |
| shopifyUsageRetryBaseSeconds | 10 | 3600 |
| shopifyUsageRetryMaxSeconds | 60 | 86400 |
| translationReconciliationPageSize | 1 | 500 |
| translationClaimTimeoutSeconds | 60 | 86400 |
| translationSubmitRetrySeconds | 30 | 86400 |
| translationInitialPollSeconds | 30 | 86400 |
| translationPollIntervalSeconds | 30 | 86400 |
| translationResultRetrySeconds | 30 | 86400 |
| translationSubmitMaxAttempts | 1 | 10 |
| translationMaxAutoRetries | 0 | 10 |
| every `*QueueGlobalConcurrency` field | 1 | 100 |

Abuse limits:

```text
rawSenderLimitPerMinute:                     1..10_000
rawGlobalLimitPerMinute:                     1..1_000_000
turnSenderLimitPerMinute:                    1..10_000
turnSenderLimitPerTenMinutes:                1..100_000
turnConversationLimitPerMinute:              1..10_000
turnConversationLimitPerTenMinutes:          1..100_000
turnShopLimitPerMinute:                      1..100_000
turnGlobalLimitPerMinute:                    1..1_000_000
discoverySenderLimitPerMinute:               1..10_000
discoverySenderLimitPerTenMinutes:           1..100_000
discoveryConversationLimitPerMinute:         1..10_000
discoveryConversationLimitPerTenMinutes:     1..100_000
```

Add cross-field CHECK constraints:

```text
conversationMaxSettleWindowMs >= conversationQuietWindowMs
shopifyUsageRetryMaxSeconds >= shopifyUsageRetryBaseSeconds

rawGlobalLimitPerMinute >= rawSenderLimitPerMinute

turnSenderLimitPerTenMinutes >= turnSenderLimitPerMinute
turnConversationLimitPerTenMinutes >= turnConversationLimitPerMinute
turnGlobalLimitPerMinute >= turnShopLimitPerMinute
turnShopLimitPerMinute >= turnSenderLimitPerMinute

discoverySenderLimitPerTenMinutes >= discoverySenderLimitPerMinute
discoveryConversationLimitPerTenMinutes >= discoveryConversationLimitPerMinute

discoverySenderLimitPerMinute <= turnSenderLimitPerMinute
discoverySenderLimitPerTenMinutes <= turnSenderLimitPerTenMinutes
discoveryConversationLimitPerMinute <= turnConversationLimitPerMinute
discoveryConversationLimitPerTenMinutes <= turnConversationLimitPerTenMinutes
```

Require `version >= 0`.

## Seed rule

The migration MUST insert exactly one default config row:

```text
id = "default"
version = 0
all other values = model defaults above
```

Use `INSERT ... ON CONFLICT ("id") DO NOTHING`.

The Admin application MUST NOT be responsible for creating this singleton.

## Migration naming

Create one ARCH-014 migration after the accepted DATABASE-003 migration. Use the repository's chronological migration naming convention.

The migration must create only the new enums/tables/indexes/check constraints/default row. It must contain no `ALTER TABLE` against pre-existing application tables.

## Validation script

Add:

```text
scripts/validate-arch014-background-runtime-config.mjs
```

It MUST assert:

1. all three models exist;
2. exact field names/defaults exist;
3. exact enum values exist;
4. migration contains all required CHECK constraints;
5. migration seeds `id='default'`;
6. no pre-existing table is altered;
7. all queue concurrency fields are present;
8. `translationResultRetrySeconds` is distinct from `translationPollIntervalSeconds`;
9. lease has owner token + generation + expiry + heartbeat;
10. ERD contains all new models.

## Required commands

```bash
npm run prisma:format
npm run prisma:validate
npm run prisma:generate
node scripts/validate-arch014-background-runtime-config.mjs
npm test --if-present
git diff --check
```

If PostgreSQL is unavailable for migration execution, record that exact environment blocker; schema generation/validation and static migration validation must still pass.

## Stop conditions

STOP and return to architect review rather than improvising if:

- DATABASE-003 is not present;
- implementing this requires altering an existing table;
- Prisma generation requires unrelated schema repair;
- a requested runtime field conflicts with an existing authoritative persisted setting;

## Completion Report

Status: Ready for Review

Implementation commit: `0247a27` (`feat(database): add background runtime config and leases`), pushed to `task/ARCH-014-DATABASE-004` in the `moda-interact-database` repository.

### Acceptance Mapping

- Added the exact `BackgroundRuntimeConfigSection` and `BackgroundRuntimeLeaseName` enums in `public`.
- Added additive `BackgroundRuntimeConfig`, `BackgroundRuntimeConfigAuditEvent`, and `BackgroundRuntimeLease` models with the specified fields, defaults, relations, and indexes. `platformAdminId` remains an actor-id string with no `PlatformAdmin` relation.
- Added migration `20260916000000_arch014_background_runtime_config_and_leases` with 55 named bounds, cross-field, and version CHECK constraints, no `ALTER TABLE`, no lease seed, and one idempotent default config seed using `ON CONFLICT ("id") DO NOTHING`.
- Added `scripts/validate-arch014-background-runtime-config.mjs` covering models, exact defaults/enums, checks, seed, preserved existing schema objects, queue fields, distinct translation retry/poll fields, lease fields, and ERD models.
- Regenerated `docs/generated/prisma-erd.puml` and `docs/generated/erd.png` with all three new models.

### Validation

- `npm run prisma:format`: repository script is absent; exact command reported `Missing script: "prisma:format"`. Equivalent declared `npm run format` passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma 6.19.3.
- `node scripts/validate-arch014-background-runtime-config.mjs`: passed.
- `npm test --if-present`: no test script declared; skipped by npm.
- `git diff --check`: passed.
- `npm run erd:puml` and `npm run erd:png`: passed.
- Local migration deploy was attempted with `DATABASE_URL="postgresql://postgres:postgres@localhost:5432/moda_interact"`; PostgreSQL was reachable, but Prisma returned `P3009` because pre-existing migration `20260915140000_arch015_fractional_provider_usage_snapshots` is already failed. No reset or migration resolution was performed.

### Evidence and Limitations

- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-014-DATABASE-004`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-014-DATABASE-004`.
- Dependency `ARCH-014-DATABASE-003` was present at implementation base `d44b621cdcc3635127b91601be648b61c0eff1e2`.
- The implementation is ready for architect review; the local database blocker is limited to the pre-existing failed migration state.
- the migration cannot enforce the specified bounds.
