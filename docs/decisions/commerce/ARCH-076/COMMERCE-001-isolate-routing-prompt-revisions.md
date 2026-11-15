---
id: ARCH-076-COMMERCE-001
architecture_id: ARCH-076
title: Exclude routing-only prompt revisions from normal Commerce configuration
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-11-15T13:59:51Z
attempt: 1
depends_on: []
enables: [ARCH-076-BACKGROUND-004, ARCH-076-SYSTEM-TEST-001]
created: 2026-11-15
updated: 2026-11-15
---

# Isolate routing-only prompt revisions

## Architecture

ARCH-076; [parent architecture](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Prevent normal Commerce Studio configuration from reading, seeding or activating routing-only prompt revisions.

## Context

ADMIN003 publishes immutable PLATFORM revisions in the existing prompt lineage, tagged `sourceContext.purpose = RECOVERY_ROUTING` and schemaVersion 1, without changing the normal agent pointer. Existing Commerce `prompt-service.ts#setPointer` checks PUBLISHED/exact scope but not purpose, so Studio can otherwise activate such a revision. Admin's normal-agent guard does not protect this separate repository. This bounded correction is required before live routing prompt activation; ADMIN003's own source acceptance is independent.

## Scope

Commerce-owned prompt configuration services/read models, normal draft seed/read selection and applicable Studio selectors/server actions. Start at `src/commerce/agent-configuration/prompt-service.ts`, effective configuration and prompt revision reads. Inspect actual current repository tests/package commands before implementation.

## Out of Scope

Admin implementation, new prompt lineage/table/schema, Shared changes/publication, model configuration refactor, routing execution, provider calls, live settings and deferred SYSTEM-TEST execution.

## Requirements

- [ ] Application-owned purpose guard rejects a revision tagged RECOVERY_ROUTING from every ordinary normal Commerce activation path, even when PUBLISHED, exact PLATFORM scope and explicitly supplied by ID.
- [ ] Normal revision listings, effective read models and draft seeds exclude routing-only revisions. Do not simply remove sourceContext from projections and lose evidence. An already-invalid active pointer fails closed with a bounded actionable error; never silently choose another active prompt or repair configuration by writing during a read.
- [ ] A normal draft created without an active pointer uses the latest eligible normal revision, not a newer routing revision. Preserve existing scope/shop, PUBLISHED/DRAFT, edit-version/CAS, immutable content hash, role and audit behavior.
- [ ] Normal revision numbering shares the existing lineage with routing publication. Allocate against actual latest revision under existing concurrency controls, so excluding routing revisions from candidates does not reuse their revision numbers.
- [ ] Same protection applies to explicit platform/shop activation entry points as appropriate; wrong owner/scope remains rejected. Ordinary untagged revisions retain current behavior. Treat purpose as application policy, not a new Shared business enum.
- [ ] No new schema or Shared release. No normal pointer/model/prompt editVersion changes caused merely by reading, listing or rejecting routing revisions.

## Work Items

- [ ] Inspect all normal Studio prompt activation/read/seed entry points in the current accepted main.
- [ ] Implement the bounded application-owned purpose exclusion consistently.
- [ ] Add focused tests for explicit activation, no-active seed, effective read and shared-lineage revision allocation.
- [ ] Run declared focused validation and complete the report in canonical launcher-prepared worktrees.

## Interfaces / Contracts

Existing CommerceAgentPromptRevision.sourceContext JSON carries purpose RECOVERY_ROUTING; published prompt schema and existing normal agent pointers are unchanged. Admin owns routing publication and recovery.routingAgent pointer. Commerce owns ordinary Studio activation/reads. Background revalidates routing prompt references at use. The purpose discriminator does not authorize tenant access or substitute for exact scope validation.

## Dependencies

None. The tag contract is defined here and in the accepted parent architecture; fixtures can seed tagged rows without waiting for Admin deployment. ADMIN003 acceptance is not blocked by this task, but live routing activation and BG004 acceptance require it Complete.

## Enables

ARCH-076-BACKGROUND-004 and final deferred integrated routing validation.

## Acceptance Criteria

- [ ] Tagged PLATFORM PUBLISHED revision cannot become an ordinary active Commerce prompt via explicit Studio API/action.
- [ ] Newest tagged revision is absent from normal candidate/seed paths; normal revision numbers remain collision-free.
- [ ] Tagged current pointer produces a visible refusal without fallback or mutation; normal exact-owner CAS behavior remains intact.
- [ ] Focused tests, required checks and mirrored worktree evidence are recorded; no live calls or unrelated source changes.

## Validation

- [ ] Unit/service tests cover tagged and untagged revisions, missing/malformed context, exact scope, unauthorized owner, draft/published state and stale CAS.
- [ ] Disposable PostgreSQL service tests prove rejected tagged activation leaves normal pointer/editVersion/audit unchanged; normal fallback seed skips newest tagged revision while allocating beyond actual latest; existing invalid active pointer read is refusal and read-only; concurrent ordinary/routing-like revision inserts preserve uniqueness/CAS behavior.
- [ ] Existing relevant prompt/effective configuration tests, declared typecheck/lint and production build appropriate to changed code.
- [ ] Git diff check; no schema/Shared/live configuration changes. Inspect package.json and existing harnesses rather than inventing scripts. These task-local checks do not execute SYSTEM-TEST.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return Completion Report and STOP. Do not activate routing or begin another task.

## Implementation Notes

Reuse the existing authorization, prompt storage, CAS and audit mechanisms. A small repository-local purpose predicate is application policy; do not import Admin source or duplicate generic parsing/cryptography. If an inaccessible current module or existing schema prevents the guard, return the concrete gap to architect instead of widening ownership.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run; definition only.

### Deviations

None

### Assumptions

Routing publication keeps its existing purpose marker stable.

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Definition only; implementation has not been claimed.

### Reviewed Files

Read-only existing Commerce prompt-service.ts and Admin routing prompt publication contract.

### Validation Reviewed

Task route resolution and definition diff check only.

### Architecture Conformance

Bounded Commerce-owned isolation gap; no schema, Shared or runtime deployment addition.

### Follow-up

Complete before BG004 acceptance or live routing activation. ADMIN003 remains independently acceptable. SYSTEM-TEST stays deferred.
