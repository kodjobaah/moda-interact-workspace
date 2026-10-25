---
id: ARCH-047-BACKGROUND-006
architecture_id: ARCH-047
title: Integrate offer decisions and prepared templates into automated recovery
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-BACKGROUND-001
  - ARCH-047-BACKGROUND-004
enables:
  - ARCH-047-BACKGROUND-007
created: 2026-10-24
updated: 2026-10-24
---

# Integrate offer decisions and prepared templates into automated recovery

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Wire the offer resolver and reusable template preparer into initial and scheduled follow-up sends while preserving one authoritative final outbound admission path.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Modify only relevant automated recovery call sites (`checkout-recovery/recovery-initiation.service.ts`, `checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, narrowly required outbound admission/final fence adapters) to delegate to BG004 and BG001 modules.
- Implement **one narrow shared final-send template assignment/registration recheck adapter** at the established final admission point for both automated and later human sequence-two consumers. Do not create a parallel send pipeline.
- Keep all recovery state, scheduling, reachability, billing and provider-delivery orchestration owned by their existing services; new code is orchestration glue and injection ports.

## Out of Scope

- Do not reimplement the offer resolver, selector, AST compiler, Meta registration management, translation, wrapper rendering or human in-window send.
- Do not reopen completed ARCH-045/046 consent/STOP tasks, bypass purchased-credit reservations or implement unrelated retry/scheduling refactors.

## Requirements

**R1 — Eligible action ordering.** Retain current checkout/recovery and consent/STOP/reachability guards. Only after an initial/sequence-two message is eligible and needed, resolve one verified offer using BG004; then request BG001 preparation with `INITIAL` or `FOLLOW_UP`, verified offer outcome, intended shop/WABA/language/recipient and checkout evidence. No LLM call on irrelevant inbound checkout events.

**R2 — Selected template.** Use prepared approved/published Moda-authored assignment and per-language frozen Meta parameter bindings; default to a No Offer template only on a validated `NO_OFFER` decision, never on an unavailable/ineligible sender slot. Do not perform provider template-metadata GET on normal sends. Preserve the initial shop-default and subsequent conversation-language semantics unless explicitly changed in task scope.

**R3 — Final recheck.** Reverify the exact shop/variant/registration, local approved/enabled status, current provider revocation/drift state, sender WABA and recipient association as late as existing final permit/transaction permits. No external Meta/Redis operation inside a SQL transaction; no stale prepared payload can bypass changed publication/STOP/consent state.

**R4 — Recovery invariants.** Preserve sequence-one idempotency, one permitted sequence-two follow-up, order-completion/checkout-change suppression, last inbound response ordering, consent and authoritative STOP, independent moderation, entitlement and credit reservation/settlement/compensation. Failed preparation/admission yields a controlled no-send result without wrongly consuming credits.

**R5 — Shared adapter ownership.** BG006 owns the narrow final template eligibility adapter/fence changes; BG007 **calls the same adapter** and must not implement a second copy. Existing Meta provider send mechanics remain unchanged except passing prepared body/button/header parameters.

## Work Items

- [ ] Modify only relevant automated recovery call sites (`checkout-recovery/recovery-initiation.service.ts`, `checkout-recovery/recovery-outreach-follow-up-processor.service.ts`, narrowly required outbound admission/final fence adapters) to delegate to BG004 and BG001 modules.
- [ ] Implement **one narrow shared final-send template assignment/registration recheck adapter** at the established final admission point for both automated and later human sequence-two consumers. Do not create a parallel send pipeline.
- [ ] Keep all recovery state, scheduling, reachability, billing and provider-delivery orchestration owned by their existing services; new code is orchestration glue and injection ports.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes** BG004 `RecoveryOfferDecision`, BG001 `PreparedRecoveryTemplate` with immutable assignment identity, existing recovery/credit/final-send ports. This task owns only integration and the shared late-check adapter. Do not make a new Shared package contract for Background-local interfaces.

**Key paths to inspect:** `recovery-initiation.service.ts`, `recovery-outreach-follow-up-processor.service.ts`, `outbound-whatsapp-admission/outbound-message-delivery.service.ts`, `recovery-conversation/outbound-send-fence.service.ts`. Resolve actual call graph before modifying.

## Dependencies

- `ARCH-047-BACKGROUND-001`
- `ARCH-047-BACKGROUND-004`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

- `ARCH-047-BACKGROUND-007`


## Acceptance Criteria

- [ ] Initial NONE/FIXED/AI and sequence-two follow-up select expected six-purpose variants and preserve correct language; mapping of body and dynamic URL/button parameters tested with provider mock.
- [ ] Provider category preflight no longer called; no normal-send Meta metadata GET; missing/revoked/drifted/disabled/ambiguous assignment fails closed.
- [ ] Simulate consent/STOP/recipient/assignment change between preparation and final permit; no send/no permanent credit consumed.
- [ ] Tests for order completion, duplicate initial and sequence-two jobs, response before follow-up and max-two outreach limit.
- [ ] Re-run existing recovery-initiation/follow-up/fence/credit compensation tests, PostgreSQL admission race where available, build and `git diff --check`.
- [ ] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [ ] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [ ] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [ ] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [ ] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep `RecoveryInitiationService` and follow-up processor thin: call the owned modules and preserve their result IDs. Test narrow adapter through injection. Do not delete legacy selector until all callers have migrated; any legacy compatibility cleanup must be bounded and verified.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-006`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Not Started — task definition only; no implementation was executed or validated in this artifact.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run; implementation validation remains outstanding.

### Deviations

None recorded.

### Assumptions

The DB001 Attempt 7 model names and fields are authoritative design inputs, not proof of an accepted/applied production migration. Reinspect current implementation on claim.

### Unresolved Issues

The parent ARCH-047 architecture and `BACKGROUND-001` still require final reconciliation with the Admin-owned AST/compilation and no-new-Shared-template-package decision before work begins.

### Architectural Concerns

No additional cross-repository issues identified at definition time; return any new gap to the architect.

## Architect Review

### Review Status

Pending — implementation not submitted.

### Review Notes

Not reviewed.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

To be assessed against the reconciled ARCH-047 parent architecture and current repository code.

### Follow-up

Architect to reconcile the parent task graph and obsolete Admin/Shared references before promoting these tasks to Ready.
