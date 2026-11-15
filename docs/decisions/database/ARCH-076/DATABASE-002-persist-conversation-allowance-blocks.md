---
id: ARCH-076-DATABASE-002
architecture_id: ARCH-076
title: Persist independent funded conversation allowances
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-11-15T12:59:02Z
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-005]
created: 2026-11-15
updated: 2026-11-15
---

# Persist independent funded conversation allowances

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Persist exact funded-block lineage without resetting conversation history.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

One independent allowance migration, Prisma relations, integrity guards, ERD and disposable PostgreSQL checks; no sender schema dependency.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Implement exact Independent allowance storage fields/constraints in parent architecture.
- [ ] Existing messages with NULL allowanceBlockId remain original block-zero history; no rewriting UsageEvents or mass retagging.
- [ ] Lazy initial block adoption requires proven original funding; unknown historical proof holds for reconciliation, never fabricates funding or charges again.
- [ ] One ACTIVE and one PENDING successor per Conversation; cancelled intents retained and monotonic ordinal never reused.
- [ ] Freeze message block pin at insert and immutable funding identity; independent repair lease survives turn lease expiry.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Independent allowance storage section is authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

None

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Implement exact Independent allowance storage fields/constraints in parent architecture.
- [ ] Existing messages with NULL allowanceBlockId remain original block-zero history; no rewriting UsageEvents or mass retagging.
- [ ] Lazy initial block adoption requires proven original funding; unknown historical proof holds for reconciliation, never fabricates funding or charges again.
- [ ] One ACTIVE and one PENDING successor per Conversation; cancelled intents retained and monotonic ordinal never reused.
- [ ] Freeze message block pin at insert and immutable funding identity; independent repair lease survives turn lease expiry.

## Validation

- [ ] Fresh/full-history upgrade, Prisma validate/generate and scoped ERD.
- [ ] Real PostgreSQL FK/uniqueness/owner trigger/message-pin immutability and ACTIVE+inflight concurrency tests.
- [ ] Preserve all historical messages, UsageEvents/reservations and Conversation.checkoutRecoveryId uniqueness.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

In Progress — initial implementation and PostgreSQL checks passed; final client-path checks and integration with the separately owned sender migration remain pending.

### Files Changed

Implementation commit `20eea0a` on mirrored task branch: `prisma/schema.prisma`, additive `prisma/migrations/20261115130322_conversation_allowance_blocks/migration.sql`, `package.json`, allowance schema validator and disposable PostgreSQL runner, scoped full-ERD PUML additions, and focused `docs/generated/conversation-allowance.puml`/PNG.

### Work Completed

Implemented the 16-field block model, nullable insert-only message pin, same-owner/deferred reservation/predecessor/message FKs, per-conversation ACTIVE/PENDING uniqueness, monotonic retained ordinals, immutable funding/policy identity and independent repair evidence. Parent ownership edits cannot invalidate a funded block. Existing reservation/provider records remain authoritative; no sender dependency, historical reset or hosted mutation.

Prepared packet: canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-DATABASE-002`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-DATABASE-002`; both branches `task/ARCH-076-DATABASE-002`. Parent reused/synchronized through main `41d383094`; source created from main `2e14f866`; recursive source submodules ready (none). Prepared attempt 1 claim `2467fd896` pushed at 2026-11-15T12:59:02Z. No startup re-claim, shared-checkout switch, gitlink or main merge.

### Validation Results

- Node bootstrap selected workspace Node 24.19.0; `npm ci --ignore-scripts` completed (existing audit reports 8 dependency vulnerabilities; no dependency changes).
- `npm run validate`, `npm run prisma:generate`, `npm run lint`, `npm run test:conversation-allowance` passed.
- Prisma `migrate dev --create-only --name conversation_allowance_blocks` authored the migration against an invocation-owned localhost PostgreSQL fixture after all 80 predecessors; task-only SQL retained, unrelated generated naming/default drift excluded.
- `npm run test:conversation-allowance:postgres` passed fresh/full-history upgrade with 111 assertions, including concurrent pending intents/repair CAS, owner mismatch and edits, reservation reuse constraints, immutable pins, retained cancelled lineage, preserved old messages/usage/reservations, deferred owner cascades and old writers. Fixture setup bugs (reservation lacked required counter, Decimal string precision expectation) were corrected before the passing run.
- Scoped PUML generated from Prisma; focused PNG rendered and visually checked. Existing full PNG retained because its default 4096-pixel render clips the large diagram.
- Final expanded generated Prisma Client path checks are running; accepted sender migration will be merged into this task branch and relevant checks rerun before review submission.
- All authoring/test databases are disposable invocation-owned local Docker resources. Authoring container removed; test runner cleans its resources. No SYSTEM-TEST task, hosted database or provider calls.

### Deviations

Prisma models the inverse composite optional reservation relation as a list; the unique creditReservationId index still enforces at most one block per reservation without a redundant composite unique index. Scoped ERD PNG is a dedicated readable artifact rather than a cropped regeneration of the repository-wide PNG.

### Assumptions

The application validates actual funding state, dispatch evidence and lease-token CAS. ACTIVE→CANCELLED remains legal for application-proven definitive late opening failure; SQL does not decide compensation eligibility.

### Unresolved Issues

Final sender-migration integration and expanded PostgreSQL/client validation pending before review.

### Architectural Concerns

None requiring cross-repository schema change. Sender and renewal task streams remain independent.

## Architect Review

### Review Status

Pending

### Review Notes

Definition only; implementation not started.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation review.

### Follow-up

None


### 15 November definition amendment

This is a new independently scoped definition, not implementation evidence. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.
