---
id: ARCH-076-DATABASE-001
architecture_id: ARCH-076
title: Persist explicit sender ownership and routing evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-15T11:46:23Z
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-001, ARCH-076-ADMIN-001]
created: 2026-11-13
updated: 2026-11-15
---

# Persist explicit sender ownership and routing evidence

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Persist sender ownership and unresolved originals with five durable records.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Prisma, one forward sender migration, constraints/indexes, scoped ERD and disposable PostgreSQL tests; see exact fields in parent architecture.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Follow the parent R15 evidence privacy amendment: routingDecision contains only message IDs, clause offsets/hashes and structural evidence, no exact clause plaintext. Preserve exact wording through pending inputJson then atomic existing ConversationMessage association.
- [ ] Freeze input/candidate/config/parent scope; permit only explicit destructive terminal value→NULL scrub and real FK SET NULL cleanup, never rebind or payload resurrection. Terminal scrub removes ephemeral customer/candidate/prompt payloads without deleting authentic owned Conversation history.

- [ ] Add nullable routingDecision JSONB separately from configurationSnapshot, with structural schema-version/object validation and write-once decision evidence. Preserve the parent R15 original/current inbound, confirmed prompt, candidate fingerprint, exact clause/moderation, policy/template and owner/control bindings. Application owns role/evidence business validation; SQL guards prevent replacement of frozen evidence and terminal-resolution rebinding.

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Enforce immutable recipient/sender identity and assignment-per-Conversation; protect original request candidate snapshots and terminal resolutions.
- [ ] Preserve current ordered-delivery sender/status evidence; use database baseline 2e14f866 with all 80 predecessor migrations through 20261113111320_arch075_meta_app_operation_state; sender target 20261113120000_whatsapp_sender_pool remains available.
- [ ] Preserve prepared attempt 1 metadata; resume only in its canonical prepared implementation worktree.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

None

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Frozen routingDecision cannot be replaced during retry or terminal replay; invalid structural shape is rejected without imposing model confidence business policy in SQL or Shared.

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Enforce immutable recipient/sender identity and assignment-per-Conversation; protect original request candidate snapshots and terminal resolutions.
- [ ] Preserve current ordered-delivery sender/status evidence; use database baseline 2e14f866 with all 80 predecessor migrations through 20261113111320_arch075_meta_app_operation_state; sender target 20261113120000_whatsapp_sender_pool remains available.
- [ ] Preserve prepared attempt 1 metadata; resume only in its canonical prepared implementation worktree.

## Validation

- [ ] Verify exact clause survives association/retry through authentic message IDs and offsets/hash; routingDecision contains no customer plaintext. Test frozen payload replacement rejection, terminal destructive scrub, FK cleanup and resurrection/rebinding rejection.

- [ ] Disposable PostgreSQL checks cover NULL initial decision, one valid freeze, attempted replacement, wrong schema shape, terminal replay and preservation of configurationSnapshot as a distinct record.

- [ ] Prisma validate/generate and scoped ERD render against actual declared commands.
- [ ] Fresh and full-history upgrade replay preserve existing rows, ordered delivery parts, Meta operation state and old-writer nullable fields.
- [ ] Real PostgreSQL constraint, immutability, duplicate inbound, concurrent recipient allocation/release and deletion cases.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Replace obsolete fixed SQL counts with exact reviewed five-table objects. Generate final SQL from the user-authorized field contract; do not copy historical five-table SQL.

## Completion Report

### Status

Not Started.

### Files Changed

Pending implementation.

### Work Completed

Pending implementation. Record launcher-resolved parent and implementation worktrees, mirrored branch names, start sync and final SHAs, consumer submodule pin where applicable, and cleanup.

### Validation Results

Pending. Record exact commands, exit status, container IDs, cleanup, failures and warnings. Report baseline issues separately from this change.

### Deviations

None recorded.

### Assumptions

None recorded.

### Unresolved Issues

None recorded.

### Architectural Concerns

None recorded.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.

## Current-main definition review — 15 November 2026

Architect read-only compatibility review against Database `2e14f866` found no conflicting Prisma anchor, table, foreign-key target or prescribed SQL name. The predecessor has 80 migration SQL files ending at `20261113111320_arch075_meta_app_operation_state`; the prescribed unused `20261113120000_whatsapp_sender_pool` target is the 81st through that migration. Upgrade fixtures replay all 80 predecessors and preserve the existing `ConversationDeliveryPart`, `ConversationDeliveryStatusReceipt` and Meta operation-state tables/rows in addition to the ordinary seeded ownership, consent, billing and message rows. Expected source counts are 138 Prisma models and 108 tracked PUML entities before this task.

The SQL contract remains five new tables, eight foreign keys, thirteen CHECKs, nine explicit indexes (six partial) and one identity trigger/function. Required fresh/upgrade/concurrency validation belongs to the Database implementation attempt; this read-only definition review is not evidence those tests passed.

DATABASE-001 is independently Ready: it supplies sender-pool storage only. The same-Conversation renewed-credit amendment belongs to separate DATABASE-002 and BACKGROUND-005 definitions and does not authorize adding allowance fields or billing policy here. No downstream task is promoted by this definition review. No implementation worktree, claim, schema migration or live mutation has been performed by the architect.


### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

Prepared claim evidence: parent task claim commit `5c0bc8cbe`, attempt 1, executor codex, claimed_at 2026-11-15T11:46:23Z. Dedicated implementation worktree remains untouched at Database main 2e14f866. The earlier user-review pause is lifted; resume this exact prepared attempt without erasing its claim or incrementing a new attempt.

Restored exact storage contract: use parent Explicit sender storage field table, FK/delete actions and indexes for all five entities; preserve R15 routingDecision separate from configurationSnapshot and immutable candidate/original/prompt scope. Prior SQL block/counts in historical review are not current migration instructions. No new claim; prepared attempt1 resumes under the user authorization.

Parent relationship correction: parentProviderMessageId FK NO ACTION DEFERRABLE INITIALLY DEFERRED; allow NULL→ID once after classification (row must exist before model I/O), then no clear/rebind. Retention deletes eligible parent/dependent cohorts or full thread cascade; selected Conversation associates only atomically with frozen routingDecision. Validate deferred parent deletion protection, bind-once concurrency and cohort deletion. This supersedes generic parent FK SET NULL cleanup wording.
