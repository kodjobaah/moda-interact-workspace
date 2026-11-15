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
status: review
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

- [x] Follow the parent R15 evidence privacy amendment: routingDecision contains only message IDs, clause offsets/hashes and structural evidence, no exact clause plaintext. Preserve exact wording through pending inputJson then atomic existing ConversationMessage association.
- [x] Freeze input/candidate/config/parent scope; permit only explicit destructive terminal value→NULL scrub and real FK SET NULL cleanup, never rebind or payload resurrection. Terminal scrub removes ephemeral customer/candidate/prompt payloads without deleting authentic owned Conversation history.

- [x] Add nullable routingDecision JSONB separately from configurationSnapshot, with structural schema-version/object validation and write-once decision evidence. Preserve the parent R15 original/current inbound, confirmed prompt, candidate fingerprint, exact clause/moderation, policy/template and owner/control bindings. Application owns role/evidence business validation; SQL guards prevent replacement of frozen evidence and terminal-resolution rebinding.

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Enforce immutable recipient/sender identity and assignment-per-Conversation; protect original request candidate snapshots and terminal resolutions.
- [x] Preserve current ordered-delivery sender/status evidence; use database baseline 2e14f866 with all 80 predecessor migrations through 20261113111320_arch075_meta_app_operation_state; sender target 20261113120000_whatsapp_sender_pool remains available.
- [x] Preserve prepared attempt 1 metadata; resume only in its canonical prepared implementation worktree.

## Work Items

- [x] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [x] Implement only this task's scope and requirements.
- [x] Complete the focused checks below and record exact commands and evidence.
- [x] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

None

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [x] Frozen routingDecision cannot be replaced during retry or terminal replay; invalid structural shape is rejected without imposing model confidence business policy in SQL or Shared.

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Enforce immutable recipient/sender identity and assignment-per-Conversation; protect original request candidate snapshots and terminal resolutions.
- [x] Preserve current ordered-delivery sender/status evidence; use database baseline 2e14f866 with all 80 predecessor migrations through 20261113111320_arch075_meta_app_operation_state; sender target 20261113120000_whatsapp_sender_pool remains available.
- [x] Preserve prepared attempt 1 metadata; resume only in its canonical prepared implementation worktree.

## Validation

- [x] Verify exact clause survives association/retry through authentic message IDs and offsets/hash; routingDecision contains no customer plaintext. Test frozen payload replacement rejection, terminal destructive scrub, FK cleanup and resurrection/rebinding rejection.

- [x] Disposable PostgreSQL checks cover NULL initial decision, one valid freeze, attempted replacement, wrong schema shape, terminal replay and preservation of configurationSnapshot as a distinct record.

- [x] Prisma validate/generate and scoped ERD render against actual declared commands.
- [x] Fresh and full-history upgrade replay preserve existing rows, ordered delivery parts, Meta operation state and old-writer nullable fields.
- [x] Real PostgreSQL constraint, immutability, duplicate inbound, concurrent recipient allocation/release and deletion cases.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Replace obsolete fixed SQL counts with exact reviewed five-table objects. Generate final SQL from the user-authorized field contract; do not copy historical five-table SQL.

## Completion Report

### Status

Ready for Review — prepared attempt 1 resumed without re-claiming or incrementing. This agent performed no hosted migration, service activation, system-test execution or main merge. The coordinator subsequently merged the accepted implementation source as recorded below.

### Files Changed

Implementation repository only:

- `prisma/schema.prisma`: five sender/routing models, inverse relations, two nullable root dispatch sender fields; unchanged one-Conversation-per-checkout uniqueness.
- `prisma/migrations/20261113120000_whatsapp_sender_pool/migration.sql`: additive tables, 9 FKs, 14 CHECKs, 16 explicit indexes, 8 functions and 11 triggers. Parent/assignment/resolution FKs use reviewed deferred deletion semantics.
- `scripts/test-arch076-sender-pool-postgres.mjs` and package script: invocation-owned PostgreSQL authoring/deployment, preservation, ownership, freeze, concurrency, resolution and deletion validation.
- `docs/architecture/arch076-sender-pool.md`, scoped `docs/generated/arch076-sender-pool.puml/.png`, and scoped additions to `docs/generated/prisma-erd.puml`.

Parent write: this task file only. No parent submodule gitlink staged.

### Work Completed

- Implemented immutable verified sender identity, recipient/sender thread generations, shop routes and lifetime recovery Conversation assignments. Assignment creation locks Conversation then CheckoutRecovery, while deferred reverse-owner checks prevent concurrent parent edits from invalidating ownership.
- Preserved separate bound-shop and admitted-prompt scope. A neutral prompt remains neutral after shop binding; physical shop deletion scrubs pending private input without rebinding historical scope.
- Added structural schema-versioned, write-once routing decisions and explicit immutable resolution witnesses. A frozen Q1 CLARIFY is preserved while a later child authorizes resolution; direct usable classifications may self-resolve, but CLARIFY cannot. Explicit prompt lookup supports original → shop prompt holder → basket selection, with no newest/reverse/recursive inference.
- Protected raw input/candidate/moderation/configuration snapshots from replacement, permitted destructive terminal cleanup, excluded plaintext clause fields from decision evidence, preserved exact prompt receipts, and prevented terminal owner/resolver rebinding.
- Preserved existing ordered physical delivery/status proofs and nullable old-writer message inserts. No credit/allowance fields, counter resets, fake funding or additional Conversation were added.

### Validation Results

Final tested implementation commit: `87fbe59edfc6aa80607f2dfdc409e9f1e5ed3dda`; tree `ec1a255c3501e239d9173671d5ced7a43f8b4089`.

- `npm run lint` — PASS, exit 0.
- `npm run test:arch076-sender-pool:postgres` — PASS, exit 0, **226 assertions**, actual Prisma migrate dev `--create-only --skip-generate` against disposable local PostgreSQL, then migrate deploy on fresh and seeded upgrade databases. All 80 predecessors replayed; 81 migrations through this target, re-deploy no-op.
- Upgrade fingerprints preserved Shop, CheckoutRecovery, Conversation, CustomerPhone/consent, UsageEvent, UsageReservation, ConversationMessage, ConversationDeliveryPart, ConversationDeliveryStatusReceipt and MetaTemplateAppOperationState rows.
- Positive and negative SQL cases covered frozen decisions, original/current identities, private-clause exclusion, neutral prompt scope, cross-thread/shop/parent/assignment rejection, parent/resolver cohort retention, physical owner deletion, immutable generation/assignment/dispatch proofs, concurrent owner mutation versus assignment insert, serialized recipient allocation, sibling release/admission, duplicate/restarted admission, SELECT_ONLY, SELECT_AND_QUESTION, independent NEW_QUESTION, distinct competing selection children, CLARIFY self-resolution rejection, and two-stage shop/basket prompts with forged root/thread/scope/receipt rejection.
- `npm run validate` — PASS, exit 0.
- `npm run prisma:generate` — PASS, Prisma Client 6.19.3, exit 0.
- `npm run erd:puml` — PASS; retained only task-scoped new entities/relations and new message columns in the tracked aggregate ERD to avoid unrelated snapshot churn. `plantuml -tpng docs/generated/arch076-sender-pool.puml` — PASS; rendered PNG visually inspected.
- `git diff --check` — PASS; final implementation worktree clean.

Final invocation-owned PostgreSQL container `moda-arch076-sender-73bc8629-2bde-49be-88e7-30fbd1ad1930` and its volumes/temporary migration files were removed by the runner. Earlier interrupted containers were removed; no unrelated container or hosted DB was targeted.

Resolved iteration failures: non-login shell initially lacked Docker; login shell plus canonical Node bootstrap resolved it. Workspace ENOSPC/containerd I/O failure interrupted one run; root coordinated disk/Docker recovery before the final successful replay. An expanded-fixture helper ordering ReferenceError and lint `no-unsafe-finally` were corrected and rerun. Cleanup now preserves the primary failure. `npm ci --ignore-scripts` reported 8 dependency audit findings; dependency versions/lockfile were not changed by this task.

### Git / VCS

- Mirrored branch: `task/ARCH-076-DATABASE-001` in both repositories.
- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-DATABASE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-DATABASE-001`.
- Shared workspace/shared implementation checkout switched or mutated for implementation: no. Another task worktree reused: no.
- Prepared packet: parent remote task fast-forward not-needed; origin/main incorporated yes; implementation remote task fast-forward not-needed; origin/main already-current at `2e14f8668346dfc135aa12f8d1fbc94e05c12ce7`.
- Recursive submodule sync/update passed in launcher; no nested implementation submodules.
- Original durable claim remains `5c0bc8cbe931abe52716492a9ccb150abcf5fe71`, attempt 1, executor codex, claimed_at 2026-11-15T11:46:23Z. Parent resumed current governance by merging origin/main into this same task branch, most recently `2628b87dfc6e1877bf6eb853bc7c7308366195e8`.
- Source commit/tree above pushed to `origin/task/ARCH-076-DATABASE-001`; source PR [Database #79](https://github.com/kodjobaah/moda-interact-database/pull/79).
- Coordinator merged source PR #79 to actual Database main `a7c204618c6b0ad83952a7b661482cfd03acf899`. A read-only fetch verified its tree `ec1a255c3501e239d9173671d5ced7a43f8b4089` exactly matches the tested source tree; no additional schema/code changes were introduced by integration.
- Parent task/report is submitted on the same mirrored branch/PR #1059; initial review-report publication commit `b9c07371e1d0fe4c93f50f40bb038ec2771ca4ba` is pushed; final source-integration evidence publication SHA is recorded in the coordinator handoff.
- Implementation main merged by this agent: no. Parent main merged by this agent: no. Unmerged implementation gitlink staged: no. Coordinator owns acceptance, final main integration and accepted DB consumer pin.

### Deviations

No runtime scope expansion. Added selective partial indexes for historical scope cleanup and parent/resolver/selected-pointer retention/deletion queries, avoiding full retained-turn scans. The sibling release/admission fixture deliberately retains another live assignment; it is not represented as the actual allocation service's last-member generation-closure race, which belongs to BACKGROUND-001.

### Assumptions

Background owns consent, window, contacted/eligible candidates, moderation, confidence, configuration and provider admission. SQL supplies durable structural identity/ownership/freeze constraints, not model confidence business policy. Allowance renewal remains independent DATABASE-002/BACKGROUND-005 work.

### Unresolved Issues

None blocking this bounded database task. Hosted rollout and architecture-level system tests are not claimed; SYSTEM-TEST-001 remains deferred at the user's request.

### Architectural Concerns

No new concern. Reviewed privacy, parent-retention, immutable resolution witness, ownership concurrency and multi-stage prompt amendments are incorporated.

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

R15 positive resolution lifecycle correction: classifier routingDecision and later original-request resolution are separate. Add nullable resolutionInboundProviderMessageId TEXT self-FK NO ACTION DEFERRABLE INITIALLY DEFERRED (no global UNIQUE). Q1 frozen CLARIFY stays unchanged; confirmed prompt + Q2 frozen exact-parent SELECT_ONLY/SELECT_AND_QUESTION permits Q1's initial selectedConversationId+witness=Q2 bind atomically with original admission and terminal scrub. Direct NEW_QUESTION may use self witness and leaves older pending originals alone. Bound witness is immutable; a preexisting CLARIFY decision must not block valid first resolution. Validate same-thread/route original/prompt/candidate and current owner/control/moderation under lock. Required positive PostgreSQL original→CLARIFY→confirmed prompt→child selection→original admission case, plus simultaneous selections/replay/crash, forged witness, separate new question, exact additional clause and retention-cohort deletion. Do not rewrite classifier decisions or infer resolver by reverse-child lookup.
