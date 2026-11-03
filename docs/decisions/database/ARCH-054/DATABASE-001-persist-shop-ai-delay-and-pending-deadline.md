---
id: ARCH-054-DATABASE-001
architecture_id: ARCH-054
title: Persist shop AI delay and versioned per-turn eligibility deadline
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
  - ARCH-054-BACKGROUND-001
  - ARCH-054-API-001
  - ARCH-054-API-002
  - ARCH-054-SHOPIFY-001
  - ARCH-054-SHOPIFY-002
created: 2026-10-31
updated: 2026-10-31
---


# ARCH-054-DATABASE-001: Persist shop AI delay and versioned per-turn eligibility deadline


## Architecture

Architecture: `ARCH-054`

Document: `docs/architecture/ARCH-054-merchant-configurable-ai-response-delay.md`

Coordinator: `moda_architect`. Attempt 2 was accepted by Architect review; the task is complete.


## Objective

Introduce durable merchant-configured AI delay and a three-field frozen pending-turn deadline, with DB-side integrity and scan index.


## Context

ARCH-054 adds a **merchant-selectable integer 0–30 minute AI reply delay** to the existing ARCH-040 recovery-conversation processor and handover controls, leaving merchant-authored HUMAN replies without configured delay. See the parent architecture and current snapshot for specific boundaries.


## Scope

Modify `moda-interact-database/prisma/schema.prisma` ONLY for the existing `ShopSettings` and `Conversation` models. Create `prisma/migrations/20261031170000_arch054_merchant_ai_response_delay/migration.sql` in the owning database repository. Add schema/migration tests in the existing database test convention.


## Out of Scope

No unrelated architecture changes, new standalone chat service, per-user timer jobs, invented provider error explanations, or updates to `docs/decisions/**/_index.md`. No implementation outside the assigned repository.


## Requirements

- Add exactly `ShopSettings.aiResponseDelayMinutes Int @default(0)` (0 through 30 inclusive).
- Add exactly `Conversation.pendingAiNotBeforeAt DateTime? @db.Timestamptz(3)`, `pendingAiControlRevision Int?`, `pendingAiDelayMinutes Int?`; create `@@index([pendingAiNotBeforeAt, id])` for bounded due scanning.
- SQL adds named CHECK `ShopSettings_aiResponseDelayMinutes_range` requiring 0 <= value <= 30; and `Conversation_pendingAiTriple_consistency` requiring all three nullable fields simultaneously null or simultaneously non-null; populated pair must have a non-null `pendingTurnStartedAt`, nonnegative revision and delay 0–30; `pendingAiNotBeforeAt >= pendingTurnStartedAt`.
- Do not modify `recoveryDelayMinutes`, `BackgroundRuntimeConfig.conversationQuietWindowMs`, `conversationMaxSettleWindowMs`, Meta message models, human command models or other migrations. Keep existing `CheckoutRecovery` and `Conversation` uniqueness/keys.
- A non-NULL pending deadline is an eligibility bound, not proof that a message was sent. Record actual send state only in existing outbound provider records.


## Work Items

- [x] Add the four Prisma fields in existing models and generate the declared migration.
- [x] Add PostgreSQL CHECKs and btree due index with exact names above.
- [x] Test fresh migration, Prisma validation and client generation, DB constraints for -1/31/0.5, mixed-null snapshot, misordered timestamps and valid 0/30.


## Interfaces / Contracts

Database owner only; no public API DTO here. Pending-AI triple is internal, not a new shared queue payload or standalone timer table. Snapshot unit is integer minutes; deadline uses `timestamptz(3)` UTC instant.


## Dependencies

None


## Enables

- ARCH-054-BACKGROUND-001
- ARCH-054-API-001
- ARCH-054-API-002
- ARCH-054-SHOPIFY-001
- ARCH-054-SHOPIFY-002


## Acceptance Criteria

- [x] Existing shop rows default to zero; fields are null on idle conversations.
- [x] Valid triple writes and nulling all three succeeds; invalid partial triple, out-of-range and negative revisions fail at DB.
- [x] Existing shop/recovery/conversation constraints remain valid; migration can run in disposable pg17 and Prisma generated client has declared names.


## Validation

- [x] `npm run validate`; `npm run prisma:generate`; apply migration to a disposable PostgreSQL; execute targeted constraint regression tests; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Use existing migration conventions; exact timestamp path is reserved for ARCH-054. No backfill requiring live provider or historical events; preproduction rollout includes explicit pending-turn drain before enabling nonzero delay.


## Completion Report

### Status

Attempt 2 complete and accepted by Architect review.

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20261031170000_arch054_merchant_ai_response_delay/migration.sql`
- `scripts/validate-arch054-ai-response-delay-schema.mjs`
- `scripts/validate-arch054-ai-response-delay-migration.mjs`
- `scripts/test-arch054-ai-response-delay-postgres.mjs`
- `package.json` (focused validation commands)

### Work Completed

- Added `ShopSettings.aiResponseDelayMinutes` with default zero; retained the existing `recoveryDelayMinutes` field and default.
- Added the nullable pending-AI deadline, control revision and frozen delay to `Conversation`; added the due-scan index.
- Added named PostgreSQL checks for the shop delay range and all-or-none pending snapshot, including start timestamp, revision, delay range and deadline ordering.
- Added focused Prisma schema/migration checks and PostgreSQL fresh/upgrade regression runs.
- Updated the pending-AI deadline check to interpret `pendingTurnStartedAt` as UTC with `AT TIME ZONE 'UTC'`, making the comparison independent of the session timezone.

### Validation Results

Attempt 1 and Attempt 2 validation:

- `npm run validate` — passed.
- `npm run prisma:generate` — passed with Prisma 6.19.3.
- `npm run test:arch054-ai-response-delay-schema` — passed.
- `npm run test:arch054-ai-response-delay-migration` — passed; verifies explicit UTC conversion in the deadline constraint.
- `npm run test:arch054-ai-response-delay:postgres:fresh` — passed against PostgreSQL 17 after applying all 68 migrations through this task.
- `npm run test:arch054-ai-response-delay:postgres:upgrade` — passed; existing shop recovery delay and conversation start time remained unchanged, new fields received their intended defaults.
- PostgreSQL regression inserts a valid UTC deadline after its UTC turn start under `America/Los_Angeles`, and rejects a deadline before turn start in that same non-UTC session timezone; existing range, snapshot, revision, and 0/30 boundary checks also pass.
- `git diff --check` — passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

Attempt 1 P2 addressed in Attempt 2: the CHECK now compares `pendingAiNotBeforeAt` with `pendingTurnStartedAt AT TIME ZONE 'UTC'`. The PostgreSQL regression verifies valid and invalid comparisons under `America/Los_Angeles`.

### Worktree and Git Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-DATABASE-001`, branch `task/ARCH-054-DATABASE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-DATABASE-001`, branch `task/ARCH-054-DATABASE-001`.
- Attempt 2 parent start-of-attempt sync: remote task branch fast-forward not needed; `origin/main` already current. Pre-claim head `7f0ab8785840f190a9d9540b9fae4f11b987c987`; claim commit `92ec8e1bbbefd41adc680b8cab4887264777d1a3`.
- Attempt 2 implementation start-of-attempt sync: remote task branch fast-forward not needed; `origin/main` already current. Pre-implementation head `42e23aebcc1ebacd817aa54b4ef3a0572afc6fa4`; correction commit `7002f867f035742771889afcf4ae5874570c53f6` (`fix(database): compare pending deadline in UTC`).
- Recursive implementation submodules: sync passed; init/update passed; no entries were recorded.
- Shared workspace and shared database source checkouts were not switched or modified for implementation. No other task worktree was reused. Disposable PostgreSQL containers were removed by the regression runner.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 resolves the timezone-dependent comparison by explicitly interpreting the legacy `pendingTurnStartedAt` value as UTC. The PostgreSQL regression covers acceptance of a later deadline and rejection of an earlier deadline under `America/Los_Angeles`. No further findings.

### Reviewed Files

- `prisma/schema.prisma`
- `prisma/migrations/20261031170000_arch054_merchant_ai_response_delay/migration.sql`
- `scripts/validate-arch054-ai-response-delay-schema.mjs`
- `scripts/validate-arch054-ai-response-delay-migration.mjs`
- `scripts/test-arch054-ai-response-delay-postgres.mjs`
- `package.json`

### Validation Reviewed

The Attempt 2 Completion Report records successful Prisma validation and generation, schema and migration checks, PostgreSQL 17 fresh and upgrade runs, and `git diff --check`. The recorded results were reviewed; the architect did not rerun validation.

### Architecture Conformance

Accepted

### Follow-up

Dependency frontier reconciled. `ARCH-054-BACKGROUND-001`, `ARCH-054-API-002`, `ARCH-054-SHOPIFY-002`, and `ARCH-054-SHARED-002` are Ready. `ARCH-054-API-001` and `ARCH-054-SHOPIFY-001` remain Pending until `ARCH-054-SHARED-002` is Complete.
