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
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 1
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

Coordinator: `moda_architect`. Task materialised on the parent task branch; implementation Attempt 1 is complete and submitted for review.


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

Attempt 1 review requested a timezone-independent deadline comparison; Attempt 2 is ready to address it.

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

### Validation Results

- `npm run validate` — passed.
- `npm run prisma:generate` — passed with Prisma 6.19.3.
- `npm run test:arch054-ai-response-delay-schema` — passed.
- `npm run test:arch054-ai-response-delay-migration` — passed.
- `npm run test:arch054-ai-response-delay:postgres:fresh` — passed against PostgreSQL 17 after applying all 68 migrations through this task.
- `npm run test:arch054-ai-response-delay:postgres:upgrade` — passed; existing shop recovery delay and conversation start time remained unchanged, new fields received their intended defaults.
- Database regressions cover valid 0 and 30 minute values, rejection of -1/31 and fractional integer text, negative revisions, partial snapshots, missing turn start, earlier deadlines, complete snapshot clearing, and due-index presence.
- `git diff --check` — passed.

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

Review intake for Attempt 1: make the deadline check timezone-independent. The comparison between `pendingAiNotBeforeAt` (`timestamptz`) and `pendingTurnStartedAt` (`timestamp without time zone`) must interpret the stored turn-start timestamp as UTC explicitly. Attempt 1 remains unchanged; correction is assigned to Attempt 2.

### Worktree and Git Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-054-DATABASE-001`, branch `task/ARCH-054-DATABASE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-054-DATABASE-001`, branch `task/ARCH-054-DATABASE-001`.
- Parent start-of-attempt sync: remote task branch fast-forward not needed; `origin/main` already current. Pre-claim head `7beffeb118e07f3da5f061288ba1fb7e025bb1de`; claim commit `2f738cd98630fd3b549cd3d82bccbeff3c49b087`.
- Implementation start-of-attempt sync: remote task branch fast-forward not needed; `origin/main` already current. Pre-implementation head `b87e460e86de2044477f8c96b5c1c42e722de8f0`; implementation commit `42e23aebcc1ebacd817aa54b4ef3a0572afc6fa4` (`feat(database): persist merchant AI response delay`).
- Recursive implementation submodules: sync passed; init/update passed; no entries were recorded.
- Shared workspace and shared database source checkouts were not switched or modified for implementation. No other task worktree was reused. Disposable PostgreSQL containers were removed by the regression runner.

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
