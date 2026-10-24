---
id: ARCH-047-BACKGROUND-007
architecture_id: ARCH-047
title: Integrate merchant post-window recovery follow-up templates
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-BACKGROUND-001
  - ARCH-047-BACKGROUND-004
  - ARCH-047-BACKGROUND-006
enables: []
created: 2026-10-24
updated: 2026-10-24
---

# Integrate merchant post-window recovery follow-up templates

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Reuse the approved follow-up template preparer and BG006 final fence in the merchant post-window sequence-two path, without changing ordinary human replies.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Update only the **post-24-hour** Meta template branch of `recovery-conversation/human-command-dispatcher.service.ts` and its narrow command-evaluation/selection adapters to use BG001 prepared follow-up and BG004 verified offer decision where required.
- Reuse BG006's late DB template-admission check and established human recovery claim, reserve/send/compensate pipeline. Keep merchant authentication/authorization in the existing API/Shopify/Woo boundaries; Background rechecks tenant/recipient/recovery claims.

## Out of Scope

- No free-text in-window AI/human wrapper work (BG008/009), no Meta authoring/editing/importing, no new merchant inbox/roles or parallel credit provider.
- Do not change the permitted one-follow-up-after-window policy, send timing semantics or existing human command retries just to accommodate templates.

## Requirements

**R1 — Correct branch.** If the rolling 24-hour customer-service window is open, preserve existing permitted ordinary human free-text handling (subsequently wrapped by BG009). If closed, only the existing eligible **sequence-two** recovery follow-up may use a Meta-approved Follow-up template; never send a free-text wrapper outside the window.

**R2 — Trusted preparation.** Resolve an approved Follow-up purpose/offer using BG004/BG001 with the **same shop/WABA/recipient/conversation checkout** and language as the stored merchant command. A merchant-selected template identifier must be re-resolved against current permitted assignments, not trusted as arbitrary Meta name or injected parameter list.

**R3 — Idempotency and audit.** One sequence-two claim per recovery, no duplicate sends from retries/double-clicks, do not consume another conversation/credit on refusal; persist provider and moderation evidence through existing mechanisms. Preserve authorised merchant identity, source and command audit.

**R4 — Final gate.** Use the **same BG006** late template recheck/final admission adapter; respect STOP, consent, moderation, entitlement, credit compensation and terminal recovery/order checks. Do not add another final fence or metadata GET.

**R5 — Failure.** No matching Follow-up template, stale consent, unavailable offer, revoked Meta registration or closed policy is a typed no-send/error communicated through existing human-command result, never fallback to unauthorised Meta template or free text.

## Work Items

- [ ] Update only the **post-24-hour** Meta template branch of `recovery-conversation/human-command-dispatcher.service.ts` and its narrow command-evaluation/selection adapters to use BG001 prepared follow-up and BG004 verified offer decision where required.
- [ ] Reuse BG006's late DB template-admission check and established human recovery claim, reserve/send/compensate pipeline. Keep merchant authentication/authorization in the existing API/Shopify/Woo boundaries; Background rechecks tenant/recipient/recovery claims.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes** BG001 preparation, BG004 offer decision, BG006 template fence adapter and existing `HumanCommandDispatcherService`/`MerchantSendCommandService`. No new cross-repo template transport and no changes to the command payload unless specifically required by an independently accepted merchant API task.

## Dependencies

- `ARCH-047-BACKGROUND-001`
- `ARCH-047-BACKGROUND-004`
- `ARCH-047-BACKGROUND-006`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] In-window typed human text remains unchanged by this task; post-window uses only one eligible Follow-up Meta template with correct language/offer bindings.
- [ ] Wrong-shop/WABA/wrong-variant, merchant template override, stale published slot and revoked Meta registration are refused.
- [ ] Rapid duplicate commands, provider timeout, STOP after preparation, credits consumed/refunded and retry safety.
- [ ] Existing ARCH-040 human command, follow-up claim and final admission tests pass, plus focused integration/build/`git diff --check`.
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

Keep changes local to the existing merchant command path and integration points. Any Shopify/Woo merchant UI filtering of available Follow-up templates belongs to its owning frontend task, not Background.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-007`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



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
