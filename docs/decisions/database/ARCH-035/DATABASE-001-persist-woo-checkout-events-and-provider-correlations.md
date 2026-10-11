---
id: ARCH-035-DATABASE-001
architecture_id: ARCH-035
title: Persist Woo activity receipts and checkout/order correlation
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 67
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-SHARED-001
enables:
  - ARCH-035-API-008
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-DATABASE-001: Persist Woo activity receipts and checkout/order correlation

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Add only the durable Woo activity receipt and provider-correlation records needed for idempotent checkout/order ingestion and recovery lifecycle safety.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Exact code and migration boundary:** change only `moda-interact-database/prisma/schema.prisma`; add
`prisma/migrations/20261011193000_arch035_woo_activity_receipts/migration.sql`; add
`scripts/validate-arch035-woo-activity.mjs` and its SQL/Postgres fixture. Existing Prisma names listed below are
confirmed in the snapshot. This migration is additive and creates no `CheckoutRecovery`, `Customer`, `Subscription`,
`UsageEvent` or Shopify replacement tables.

**Create precisely three enums, in PostgreSQL schema `woocommerce`:**

```prisma
// value sets are closed: never add arbitrary strings in the first implementation
WooCommerceActivityKind = CHECKOUT_UPSERT | ORDER_PLACED | ORDER_PAID | ORDER_CANCELLED
WooCommerceActivityProcessingState = PENDING | PROCESSING | APPLIED | IGNORED | FAILED
WooCommerceOrderTerminalState = PLACED | PAID | CANCELLED
```

**Create `model WooCommerceActivityReceipt` in `@@schema("woocommerce")`:** `id String @id @default(cuid())
@db.Text`; `shopId String @db.Text` FK to `Shop` with cascade delete/restrict update; `installationId String
@db.Text` with **composite FK `(installationId, shopId)` → `WooCommerceInstallation(id, shopId)`**, using its
existing composite unique; `eventId String @db.Uuid`; `contractVersion String @db.VarChar(32)`; `kind
WooCommerceActivityKind`; `checkoutKey String @db.VarChar(128)`; `revision Int`; `cartKey String? @db.VarChar(128)`;
`orderId String? @db.VarChar(20)`; `occurredAt DateTime @db.Timestamptz(3)`; `receivedAt DateTime @default(now())
@db.Timestamptz(3)`; `payloadSha256 String @db.Char(64)`; `snapshot Json? @db.JsonB` (only the typed Shared-v1
snapshot); `processingState WooCommerceActivityProcessingState @default(PENDING)`; `attemptCount Int @default(0)`;
`nextAttemptAt DateTime? @db.Timestamptz(3)`; `claimedUntil DateTime? @db.Timestamptz(3)`; `processedAt DateTime?
@db.Timestamptz(3)`; `lastErrorCode String? @db.VarChar(64)`. Add `@@unique([shopId,eventId])`,
`@@unique([id,shopId])`, and indexes on `(processingState,nextAttemptAt,receivedAt)`,
`(shopId,checkoutKey,occurredAt)`, `(shopId,orderId)`. Add the corresponding inverse Shop and WooCommerceInstallation
relation fields. Never store raw HTTP payloads, address/customer email, API credentials, order customer metadata or
network headers.

**Create `model WooCommerceCheckoutLineage` in `@@schema("woocommerce")`:** `id String @id @default(cuid())
@db.Text`, `shopId String @db.Text` and required Shop FK; `checkoutKey String @db.VarChar(128)`; `cartKey String?
@db.VarChar(128)`; `lastRevision Int @default(0)`; `lastAppliedRevision Int @default(0)`; `lastActivityAt DateTime? @db.Timestamptz(3)`; `terminalOrderId
String? @db.VarChar(20)`; `terminalState WooCommerceOrderTerminalState?`; `terminalOccurredAt DateTime?
@db.Timestamptz(3)`; `checkoutRecoveryId String? @unique`; `createdAt DateTime @default(now()) @db.Timestamptz(3)`
and `updatedAt DateTime @default(now()) @updatedAt @db.Timestamptz(3)`. Enforce `@@unique([shopId,checkoutKey])`,
`@@unique([shopId,terminalOrderId])`, and `@@index([shopId,lastActivityAt])`. Add `@@unique([id,shopId])` to the
existing `CheckoutRecovery` model, then a composite `(checkoutRecoveryId,shopId) -> CheckoutRecovery(id,shopId)` FK
on lineage, with `onDelete: Restrict, onUpdate: Restrict` (delete lineage explicitly before its recovery if ever
required; never nullable-match the composite shopId). Add inverse Shop/CheckoutRecovery relations.

**Column checklist (must match Prisma field spelling exactly):**

| Model | Required columns | Nullable columns | Exact DB constraints / indexes |
|---|---|---|---|
| `WooCommerceActivityReceipt` | `id`, `shopId`, `installationId`, `eventId`, `contractVersion`, `kind`, `checkoutKey`, `revision`, `occurredAt`, `receivedAt`, `payloadSha256`, `processingState`, `attemptCount` | `cartKey`, `orderId`, `snapshot`, `nextAttemptAt`, `claimedUntil`, `processedAt`, `lastErrorCode` | Unique `(shopId,eventId)` and `(id,shopId)`; FK Shop; composite FK installation/Shop; due-work `(processingState,nextAttemptAt,receivedAt)`; lineage/event and Shop/order indexes |
| `WooCommerceCheckoutLineage` | `id`, `shopId`, `checkoutKey`, `lastRevision`, `lastAppliedRevision`, `createdAt`, `updatedAt` | `cartKey`, `lastActivityAt`, `terminalOrderId`, `terminalState`, `terminalOccurredAt`, `checkoutRecoveryId` | Unique `(shopId,checkoutKey)`, `(shopId,terminalOrderId)`, `checkoutRecoveryId`; composite FK `(checkoutRecoveryId,shopId)`; index `(shopId,lastActivityAt)` |
| Existing `CheckoutRecovery` | **No new columns** | **No new columns** | Add only composite unique `(id,shopId)` to support same-Shop correlation FK; preserve `@@unique([shopId,checkoutToken,generation])` |

**Schema reverse relations:** `Shop.activityReceipts`, `Shop.wooCheckoutLineages`,
`WooCommerceInstallation.activityReceipts` and `CheckoutRecovery.wooCheckoutLineage` (one optional). Use these exact
names so API-008/Background-001 can compile against the generated Prisma client.

**Migration SQL beyond Prisma-generated DDL:** check `revision >= 1`, `attemptCount >= 0`, `lastRevision >= 0`, `lastAppliedRevision >= 0`, `lastAppliedRevision <= lastRevision`,
`contractVersion = 'woo.activity.v1'`, valid SHA-256 hex, `orderId IS NULL` and `snapshot IS NOT NULL` for `CHECKOUT_UPSERT`, and `orderId IS NOT NULL` and `snapshot IS NULL` for ORDER_*; cap `snapshot` storage at 16,384 bytes and reject non-object JSON. Add a targeted `BEFORE UPDATE` trigger on
ActivityReceipt preventing any change to immutable identity, kind, checkout correlation, occurredAt, digest and
snapshot fields; only processing/claim/retry fields may change. Add a `BEFORE UPDATE` lineage trigger that forbids
decreasing `lastRevision` or `lastAppliedRevision`, clearing a terminal state, changing an existing paid terminal to another state, or making
a processed late checkout remove a terminal order; allow `PLACED -> CANCELLED/PAID` and `CANCELLED -> PAID`. Match
the exact checkoutKey/source correlation, never phone/email. Triggers must be limited to newly introduced Woo tables
and checked in Prisma migrate deploy.

**Atomic consumer contract:** API-008 writes receipt and updates `lastRevision` (accepted high-water, NOT applied high-water) on lineage under Shop+lineage lock in the same
transaction, returning a previously stored receipt for identical `(shopId,eventId,payloadSha256)`; if hash differs
return 409. It records terminal ORDER_* tombstones before 202 acknowledgement. Background-001/002 claim only
`PENDING`/due `FAILED` rows under `FOR UPDATE SKIP LOCKED`, process idempotently, and can replay failed work even if
Redis hints are lost. Background-001 updates `lastAppliedRevision` only after applying a checkout snapshot. The lineage terminal marker survives deletion of old APPLIED receipts: prune APPLIED/IGNORED receipt rows older than 30 days in bounded batches, retain PENDING/PROCESSING, and retain failed/dead-letter receipts for operator recovery for at least 90 days; never prune terminal lineage while its Shop exists. No deletion may manufacture a new recovery.

**Proofs (mandatory):** fresh database migration, upgrade from actual prior schema, `migrate deploy` twice (no-op
second run), `prisma validate`, `prisma generate`; zero Shop and mixed Shopify/Woo fixtures; same/different Shop
eventId collisions; wrong-Shop installation/composite Recovery FK; racing duplicate orders; order-before-checkout and
checkout-after-paid; trigger rejection for mutated receipt and terminal rollback; concurrent claim `SKIP LOCKED`;
bounded snapshot/retention; SQL `EXPLAIN` for nextAttemptAt and lineage queries; `git diff --check`. Do not modify
prior migrations or backfill Shopify rows.

## High-level scope (non-authoritative summary)

- Represent immutable event receipt, shop/platform ownership, dedupe key, checkout/cart/order correlation and causal processing checkpoints using appropriately constrained indexes.
- Preserve existing CheckoutRecovery unique(shopId, checkoutToken, generation) and Shopify rows; no cross-Shop correlation by email/phone alone.
- Model a later authoritative order event so late cart updates cannot reopen a paid recovery; plan for replay/at-least-once delivery and cleanup retention.
- No insecure generic PII dump, new duplicate subscription/customer tables or migration of existing production history.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-database`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-SHARED-001` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-API-008`

## Acceptance Criteria

- [ ] Fresh/upgrade/re-run migration and Prisma validation.
- [ ] Concurrent receipt/order-correlation uniqueness and cross-Shop FK tests.
- [ ] Shopify checkout/recovery regression and rollback/retry evidence.
- [ ] Scope stays within `moda-interact-database` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect on implementation submission.
