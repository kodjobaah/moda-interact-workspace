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
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-10-31T19:14:54Z
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

Coordinator: `moda_architect`. Task **defined but not materialised**; no local Git/worktree/branch activity is claimed.


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

- [ ] Add the four Prisma fields in existing models and generate the declared migration.
- [ ] Add PostgreSQL CHECKs and btree due index with exact names above.
- [ ] Test fresh migration, Prisma validation and client generation, DB constraints for -1/31/0.5, mixed-null snapshot, misordered timestamps and valid 0/30.


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

- [ ] Existing shop rows default to zero; fields are null on idle conversations.
- [ ] Valid triple writes and nulling all three succeeds; invalid partial triple, out-of-range and negative revisions fail at DB.
- [ ] Existing shop/recovery/conversation constraints remain valid; migration can run in disposable pg17 and Prisma generated client has declared names.


## Validation

- [ ] `npm run validate`; `npm run prisma:generate`; apply migration to a disposable PostgreSQL; execute targeted constraint regression tests; `git diff --check`.


## Stop Condition

After all required Work Items, Acceptance Criteria and Validation are complete, update Completion Report, set status to `review`, return control to `moda_architect` and **STOP**. Do not implement dependent tasks. Publication tasks do not rerun accepted implementation validation.


## Implementation Notes

Use existing migration conventions; exact timestamp path is reserved for ARCH-054. No backfill requiring live provider or historical events; preproduction rollout includes explicit pending-turn drain before enabling nonzero delay.


## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not Run

### Deviation / Assumptions / Unresolved Issues / Architectural Concerns

None

### Worktree and Git Evidence

Not materialised; implementing agent must record launcher-prepared dedicated parent/implementation worktree paths, start-of-attempt sync, branch SHAs, submodule pins and cleanup.


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
