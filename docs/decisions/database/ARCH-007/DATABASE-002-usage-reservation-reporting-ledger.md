---
id: ARCH-007-DATABASE-002
architecture_id: ARCH-007
title: Add concurrency-safe usage reservation, counters and Shopify reporting ledger
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-DATABASE-001
enables: 
  - ARCH-007-DATABASE-003
  - ARCH-007-BACKGROUND-006
created: 2026-09-07
updated: 2026-09-07
---

# ARCH-007-DATABASE-002: Add concurrency-safe usage reservation, counters and Shopify reporting ledger

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Add the typed durable state required for Free lifetime capacity reservation, committed usage, paid Shopify App Event outbox delivery and compensating corrections.

## Context

ARCH-007 separates admission from external provider send and Shopify publication. The current UsageEvent row is not enough to prevent two workers from both consuming the final Free credit or to classify App Event retries/permanent failures.

## Scope

Modify canonical Prisma schema/generated artifacts for ShopEntitlementCounter, UsageReservation and the final typed UsageEvent reporting state. Extend Shop/BillingPeriod relations/indexes as needed. Create the normal Prisma migration for this schema slice; no production data-preservation/backfill compatibility is required.

## Out of Scope

- Plan/subscription catalog semantics (DATABASE-001).
- Admin policy/audit models (DATABASE-003).
- Runtime reservation/publisher services.
- Raw SQL locks or database triggers.

## Requirements

- Create a typed counter key containing at least `FREE_RECOVERY_LIFETIME` and a ShopEntitlementCounter unique by `(shopId, counter)` with `committedQuantity`, `reservedQuantity`, integer `version`, timestamps and indexes for shop lookup.
- Create UsageReservation with unique deterministic `sourceKey`, shop/counter, positive integer quantity, typed status `RESERVED|COMMITTED|RELEASED|AMBIGUOUS`, optional expiry and optional unique committed UsageEvent relation.
- Create typed UsageMetric containing at least `RECOVERY_CONVERSATION`, `OUTBOUND_AUTOMATED_MESSAGE`, `DELIVERED_WHATSAPP_MESSAGE`.
- UsageEvent `quantity` remains Decimal/non-zero at service layer so positive and negative compensating values are representable.
- UsageEvent has unique Moda `idempotencyKey`, optional `correctionOfUsageEventId` self-relation, source type/id and exact `occurredAt`.
- Add typed Shopify report state `NOT_APPLICABLE|PENDING|IN_FLIGHT|RETRYABLE|REPORTED|NEEDS_ATTENTION` plus snapshotted `shopifyEventHandle`, unique optional `shopifyIdempotencyKey`, attempt count, next/last attempt times, reportedAt, bounded provider response/error fields.
- Indexes must support bounded due publisher selection by report state + nextReportAt/occurredAt and shop-period reconciliation. Avoid unindexed full-table scheduler scans.
- Do not create a generic monetary cost model or Meta rate table in this task.
- Create the normal Prisma migration through Prisma tooling. Do not add application/runtime raw SQL or production-style backfill/compatibility machinery.

## Work Items

- [x] Implement typed enums/models/relations/indexes.
- [x] Create/apply the normal Prisma migration for this schema slice using the repository workflow.
- [x] Regenerate Prisma client and ERD artifacts after migration generation/application.
- [x] Validate self-relation/correction uniqueness and report-state due-query indexes.
- [x] Check for schema tests; none are declared in `package.json`.

- If this schema slice invalidates repository seed/fixture code, update that seed/fixture in the same task and validate the normal development reset path.

### Attempt 2 correction work items — architect review

- [x] Correct `prisma/seed.mjs` so one seeded recovery creates **exactly one** `RECOVERY_CONVERSATION` UsageEvent. Do not map both the legacy checkout-recovery and conversation seed rows to the same recovery-conversation metric.
- [x] Make Shopify reporting semantics in the seed architecture-correct: only paid `RECOVERY_CONVERSATION` rows are `PENDING`/`REPORTED`; internal `OUTBOUND_AUTOMATED_MESSAGE` and `DELIVERED_WHATSAPP_MESSAGE` rows are `NOT_APPLICABLE`. Any seeded paid reportable recovery row must snapshot the plan's `shopifyUsageEventHandle` and a stable unique `shopifyIdempotencyKey`; do not leave a reportable row missing either field.
- [x] Keep the message seed representative: the two outbound demo messages may each produce `OUTBOUND_AUTOMATED_MESSAGE`, and the message whose persisted status is `DELIVERED` may additionally produce one `DELIVERED_WHATSAPP_MESSAGE`. Use distinct deterministic Moda `idempotencyKey` values for each semantic UsageEvent.
- [x] Make the seed rerunnable against the same migrated development database. Its demo-shop cleanup must remove/reset ARCH-007 `UsageReservation` and `ShopEntitlementCounter` state in FK-safe order before rebuilding demo usage. Validate by running the seed **twice** against the same fresh migrated disposable PostgreSQL database and proving both runs succeed with stable expected counts.
- [x] Add `@@index([shopifyReportState, lastReportAttemptAt])` (or the Prisma-equivalent index with the same query semantics) so BACKGROUND-008 can perform a bounded stale-`IN_FLIGHT` recovery scan without scanning all report rows for a state.
- [x] Add `@@index([correctionOfUsageEventId])` so ADMIN-004/background correction net-bound/link lookups do not require a full UsageEvent scan. Do **not** make `correctionOfUsageEventId` unique; multiple bounded partial corrections remain a runtime possibility and ADMIN-004 owns net-bound enforcement.
- [x] Regenerate/amend the normal DATABASE-002 Prisma migration through the repository workflow, regenerate Prisma client + ERD artifacts, and validate the exact PostgreSQL indexes from the catalog. No production backfill/compatibility work is required.

## Interfaces / Contracts

Required identities:

```text
ShopEntitlementCounter UNIQUE(shopId, counter)
UsageReservation.sourceKey UNIQUE
UsageEvent.idempotencyKey UNIQUE
UsageEvent.shopifyIdempotencyKey UNIQUE when non-null
UsageReservation.committedUsageEventId UNIQUE when non-null
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-DATABASE-003
- ARCH-007-BACKGROUND-006

## Acceptance Criteria

- [x] Schema supports CAS/version counter updates without raw SQL.
- [x] One reservation identity cannot be duplicated.
- [x] One committed recovery usage identity cannot be duplicated.
- [x] Paid UsageEvent can be durably pending/retryable/reported/needs-attention independently of business processing.
- [x] Negative compensating UsageEvents can link to originals without mutating originals.
- [x] Due publisher and reconciliation queries have supporting indexes.
- [x] Prisma validation/generation passes with the normal Prisma migration artifact present.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-DATABASE-002` branch and the mirrored parent-workspace `task/ARCH-007-DATABASE-002` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20260907180000_add_usage_reservation_reporting_ledger/migration.sql`
- `prisma/seed.mjs`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`

### Work Completed

- Added typed entitlement counter and reservation status/identity models with CAS-ready versioned counters, expiry, committed-event uniqueness, shop relations, and bounded lifecycle indexes.
- Replaced UsageEvent metric strings with typed metrics and added append-only correction linkage.
- Added typed Shopify reporting lifecycle, snapshotted event/idempotency fields, bounded provider error/response summaries, retry timestamps/counts, and due publisher indexes.
- Added and applied the normal DATABASE-002 Prisma migration after DATABASE-001, updated seed metrics/report states, and regenerated Prisma/ERD artifacts.
- Corrected seed semantics so each recovery creates exactly one recovery event, internal message metrics are `NOT_APPLICABLE`, paid recovery events snapshot the Shopify handle/idempotency key, and demo reservation/counter state is cleared in FK-safe order.
- Added bounded stale-`IN_FLIGHT` and correction-link indexes to `UsageEvent` and amended the normal migration.

### Validation Results

- `npm run format` — passed.
- `npm run validate` — passed.
- `npm run prisma:generate` — passed; Prisma Client v6.19.3 generated.
- `npm run erd` — passed; PlantUML and PNG regenerated.
- `node --check prisma/seed.mjs` — passed.
- `npx prisma migrate deploy` against local `moda_interact_shadow` — passed; DATABASE-002 applied after the complete prior migration chain.
- `node prisma/seed.mjs` against the migrated shadow database — passed; 3 plans and 80 usage events seeded.
- Fresh local disposable database migration chain — passed; all 22 migrations applied.
- `node prisma/seed.mjs` twice against the same fresh migrated disposable database — passed; both runs produced stable counts: 20 `RECOVERY_CONVERSATION`, 40 `OUTBOUND_AUTOMATED_MESSAGE`, and 20 `DELIVERED_WHATSAPP_MESSAGE` events.
- PostgreSQL catalog query — passed; verified counter/reservation uniqueness and Shopify report due indexes.
- PostgreSQL catalog query — passed; verified `UsageEvent_shopifyReportState_lastReportAttemptAt_idx` and `UsageEvent_correctionOfUsageEventId_idx` in addition to the existing identity/due-work indexes.
- `git diff --check` — passed after normalizing generated PlantUML trailing whitespace.
- Repository `package.json` declares no test, typecheck, lint, or build scripts.

### Deviations

The existing development database was not reset or modified; migration validation used the isolated local shadow database. The normal migration artifact was generated from the DATABASE-001-applied shadow schema and excludes unrelated historical index-renaming drift.

### Assumptions

Nullable PostgreSQL unique indexes provide uniqueness for optional Shopify idempotency and committed-event identities while allowing unreported events/reservations to remain null.

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted.

### Findings

- Attempt 2 resolves all four Changes Requested from the Attempt 1 architect review.
- The seed now creates exactly one `RECOVERY_CONVERSATION` UsageEvent per seeded recovery. The two outbound demo messages create distinct `OUTBOUND_AUTOMATED_MESSAGE` events, and the delivered outbound message additionally creates one `DELIVERED_WHATSAPP_MESSAGE` event.
- Internal message metrics are `NOT_APPLICABLE` for Shopify reporting. Paid `RECOVERY_CONVERSATION` rows snapshot the mapped plan's `shopifyUsageEventHandle` plus a stable unique `shopifyIdempotencyKey`; completed demo recoveries are represented as `REPORTED` and remaining reportable recoveries as `PENDING`.
- Development seed cleanup now deletes `UsageReservation` before `ShopEntitlementCounter` and clears `UsageEvent` in FK-safe order. The agent validated two consecutive seed runs against the same freshly migrated disposable database with stable counts: 20 recovery-conversation, 40 outbound-automated-message and 20 delivered-WhatsApp-message UsageEvents.
- `UsageEvent` now has both bounded downstream indexes requested by review: `(shopifyReportState, lastReportAttemptAt)` for stale `IN_FLIGHT` recovery and `correctionOfUsageEventId` for correction-link/net-bound lookup. The existing due-work index `(shopifyReportState, nextReportAt, occurredAt)` and shop-period reconciliation indexes remain present.
- The final schema preserves the typed `ShopEntitlementCounter`, `UsageReservation`, `UsageMetric`, `ShopifyReportState` and append-only correction model required by ARCH-007. The reservation service task remains responsible for shop-scoped CAS transitions, positive reservation quantities and lifecycle validation; no runtime raw SQL was introduced by this database task.
- The normal `20260907180000_add_usage_reservation_reporting_ledger` Prisma migration contains the accepted enums/tables/relations/indexes and was validated as part of a fresh 22-migration chain.
- Independent architect source inspection found no new `$queryRaw`, `$executeRaw` or `Prisma.sql` billing runtime path. `node --check prisma/seed.mjs` also passed during review. An attempted independent package install for Prisma validation exceeded the review environment timeout, so Prisma format/validate/generate and fresh-database execution are accepted from the agent's recorded validation evidence plus source/migration inspection.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260907180000_add_usage_reservation_reporting_ledger/migration.sql`
- `moda-interact-database/prisma/seed.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `moda-interact-database/package.json`
- `docs/decisions/database/ARCH-007/DATABASE-002-usage-reservation-reporting-ledger.md`
- ARCH-007 recovery admission, App Event publisher, correction and data-model contracts

### Validation Reviewed

Agent-reported Attempt 2 validation:

- Prisma format/validate/generate — passed.
- normal Prisma migration artifact present and fresh 22-migration deployment — passed.
- seed execution twice against the same fresh migrated disposable PostgreSQL database — passed with stable expected counts.
- PostgreSQL catalog verification for the new stale-report and correction-link indexes — passed.
- seed syntax diagnostics — passed.
- `git diff --check` — passed.

Independent architect inspection additionally verified the exact schema/index definitions, corrected seed semantics/cleanup, migration DDL and absence of new runtime raw-SQL APIs. `node --check prisma/seed.mjs` passed. The review environment could not complete a fresh `npm ci` within its timeout, so it did not duplicate the agent's successful Prisma executable validation.

### Architecture Conformance

Conformant. DATABASE-002 now provides the typed, idempotent and bounded durable ledger/reservation foundation required by the dependent Background/Admin tasks without implementing their runtime behaviour.

### Decision

`ARCH-007-DATABASE-002` is architect-accepted and Complete.

`ARCH-007-DATABASE-003` is now unblocked and Ready for its first claim. It remains unclaimed with `attempt: 0`; the claiming `moda_database` agent increments it to Attempt 1.

### Follow-up

Proceed only with `ARCH-007-DATABASE-003`. Do not start Shared/Background/Admin tasks until their explicit dependencies are architect-accepted Complete.
