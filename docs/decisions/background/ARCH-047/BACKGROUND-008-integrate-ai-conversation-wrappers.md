---
id: ARCH-047-BACKGROUND-008
architecture_id: ARCH-047
title: Integrate prepared wrappers into AI conversation responses
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
  - ARCH-047-BACKGROUND-005
enables: []
created: 2026-10-24
updated: 2026-10-24
---

# Integrate prepared wrappers into AI conversation responses

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Apply BG005 to AI-authored responses before final full-message moderation and delivery while preserving turn ownership and customer-service-window limits.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Integrate BG005 into the existing `ConversationTurnProcessor`/CommerceAgent outbound turn after an AI response is generated but before persisted moderated outbound message and provider delivery.
- Keep the existing AI conversation ordering, ownership checks, generation budgets, abuse/moderation gates and outbound WhatsApp admission unchanged except for inserting the prepared wrapper step.
- Add narrow tests and dependency-injected facade call rather than duplicating wrapper rendering, checkout reads or AST logic.

## Out of Scope

- No rewriting AI answers into canned responses, no new AI turn purpose, no Meta template-based reply outside the window, no cart/checkout/coupon mutation, no general CommerceAgent refactor.
- No template authoring, translation, wrapper publication, new Shared package or editing of merchant human command path.

## Requirements

**R1 — Source and context.** Take the AI-generated response string as-is, together with actual conversation/shop/customer/checkout identity and resolved conversation language. Request BG005 `source:'AI'` rendering using stable outbound message/turn identity. If checkout context is missing, use the module's safe omission/refusal policy; never invent a URL.

**R2 — Authority ordering.** Preserve current AI-versus-HUMAN control before running the model, after await and immediately before sending. Human takeover or obsolete turn suppresses the wrapped result. No extra model turn merely to render a wrapper.

**R3 — Moderation and admission.** The **complete rendered message**, not only the AI response fragment, passes outbound independent moderation before final admission. Apply existing provider window, opt-out/STOP, recipient, entitlements and message cost limits. Do not send a free-form wrapped reply outside the allowed service window.

**R4 — Replay and persistence.** Correlate the composed content, moderation decision, durable outbound message and provider request; retries cannot append a second wrapper or send duplicated replies. Preserve audit history of original generated response where existing contracts require it, without exposing private payloads in logs.

**R5 — Read-only CommerceAgent.** The integration cannot add products, change quantities, apply codes or alter the basket. Its only new effect is deterministic message composition.

## Work Items

- [ ] Integrate BG005 into the existing `ConversationTurnProcessor`/CommerceAgent outbound turn after an AI response is generated but before persisted moderated outbound message and provider delivery.
- [ ] Keep the existing AI conversation ordering, ownership checks, generation budgets, abuse/moderation gates and outbound WhatsApp admission unchanged except for inserting the prepared wrapper step.
- [ ] Add narrow tests and dependency-injected facade call rather than duplicating wrapper rendering, checkout reads or AST logic.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes** BG005 prepared wrapper renderer and existing `ConversationTurnProcessor`, `runCommerceAgent`, `AiTurnOwnershipService`, `moderationTurnGate` and outbound WhatsApp admission. No Admin AST or Meta JSON. The outbound message identity passed to BG005 must be stable across retries.

## Dependencies

- `ARCH-047-BACKGROUND-005`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] AI answer unchanged when wrapper disabled; enabled SHARED/AI wrapper adds correct shop and current valid checkout context.
- [ ] Full rendered text is moderated, including forbidden content introduced by wrapper; provider must not receive blocked content.
- [ ] Human takeover before/during/after model generation, service window closure, STOP/consent, credit and ordering regressions.
- [ ] Retry/double-wrap protection and one provider send; read-only commerce tool assertion.
- [ ] Focused conversation-turn, moderation and WhatsApp worker tests; integration/build/`git diff --check`.
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

Make one minimal insertion in the authoritative outbound AI reply path; don't wrap generated prompt/tool messages or conversation history, only the final customer-visible message. Use the existing shared moderation API boundary unchanged.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-008`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



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
