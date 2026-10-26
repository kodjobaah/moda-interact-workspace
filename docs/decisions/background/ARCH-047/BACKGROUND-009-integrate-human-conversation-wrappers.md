---
id: ARCH-047-BACKGROUND-009
architecture_id: ARCH-047
title: Integrate prepared wrappers into human conversation replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-26T07:24:51Z
attempt: 1
depends_on:
  - ARCH-047-BACKGROUND-005
enables: []
created: 2026-10-24
updated: 2026-10-26
---

# Integrate prepared wrappers into human conversation replies

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Apply BG005 to merchant-authored in-window text before moderation and sending, preserving the merchant response and checkout context.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Wire BG005 only into the existing **in-window free-text** branch of the merchant human command path (`recovery-conversation/human-command-dispatcher.service.ts`, related command/message record) after authorisation and before final content moderation.
- Preserve exactly the merchant-authored response inside prepared SHARED/HUMAN wrapper and store/send the same complete customer-visible content. Use existing tenant, recovery, human-takeover and provider send code.

## Out of Scope

- No post-window Meta follow-up branch work (BG007), no new Quick Reply/canned response authoring, no UI redesign, no staff roles or per-conversation assignment, no AST compilation, template Meta status work or checkout mutations.
- No relaxed moderation or customer-service-window checks because a template wrapper is internally published.

## Requirements

**R1 — Intent and content.** For a human-authored ordinary response within the valid rolling WhatsApp 24-hour service window, resolve SHARED/HUMAN wrapper through BG005 and insert the submitted merchant text unchanged. Checkout URL and shop name come from read-only verified conversation context; never use a customer-supplied arbitrary URL as the trusted basket URL.

**R2 — Final message consistency.** Moderate the complete rendered text (including header/footer) independently. Persist, audit, bill and deliver exactly the same content that was approved; no moderation of only the raw merchant fragment followed by unmoderated append. Merchant previews in Shopify/Woo should use identical prepared-wrapper semantics under their separate owning tasks; do not create UI from Background.

**R3 — Admission invariants.** Reuse current merchant authentication, tenant scoping, HUMAN control, the 24-hour window, consent/STOP, support moderation, provider compensation/idempotency and billing policy. Existing merchant-authored replies within the window are not subjected to AI-exchange caps. No additional paid follow-up is created by wrapper rendering.

**R4 — Retry/error.** Stable command/message ID prevents applying the wrapper twice. If a wrapper's checkout context, schema projection or length is invalid, return an explicit failure/safe no-wrapper policy rather than sending mismatched or partially rendered content.

**R5 — Separation.** Post-window commands must continue to the Meta recovery-template path (BG007), never use a free-form conversation wrapper in place of an approved template.

**R6 — One human in-window path; no obsolete bypass.** Replace any separate in-window direct raw-text dispatch that would evade BG005 and full-message moderation, while retaining a no-wrapper case through the *same* final admission path. Remove dead local wrapper/formatting helpers and superseded tests after a reference audit, not by deleting the original human-control, service-window or moderation protections. BG007 separately owns the post-window template branch; both tasks touch `human-command-dispatcher.service.ts`, so require explicit final-branch reconciliation before acceptance.

## Work Items

- [ ] Wire BG005 only into the existing **in-window free-text** branch of the merchant human command path (`recovery-conversation/human-command-dispatcher.service.ts`, related command/message record) after authorisation and before final content moderation.
- [ ] Preserve exactly the merchant-authored response inside prepared SHARED/HUMAN wrapper and store/send the same complete customer-visible content. Use existing tenant, recovery, human-takeover and provider send code.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes** BG005 wrapper `renderConversationResponse(source:'HUMAN')`, existing `MerchantSendCommandService`, `HumanCommandDispatcherService` and moderation/admission services. No Shared AST. UI preview endpoints remain owned by Shopify/Woo/API; this task exposes only its established prepared render result to the existing command path.

## Dependencies

- `ARCH-047-BACKGROUND-005`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [ ] Human in-window reply retains verbatim merchant text with deterministic wrapper; HUMAN override/SHARED fallback and valid checkout URL tested.
- [ ] Wrapper-only forbidden content blocked by full-message moderation; durable message/provider payload equality verified.
- [ ] 24-hour expiry prevents unapproved free text; post-window sequence two untouched; STOP, consent, tenant scope and HUMAN ownership preserved.
- [ ] Retry/replay, template activation change and double-wrap refusal; no AI cap applied to eligible merchant text.
- [ ] Existing human command/moderation/compensation tests plus focused integration/build and `git diff --check`.
- [ ] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [ ] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

- [ ] Old human raw-text bypass/duplicated formatting path is absent; unwrapped fallback (if no wrapper is published) uses the same full-message moderation and final-send logic. BG007's post-window processing remains isolated and compatible.

## Validation

- [ ] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [ ] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [ ] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep merchant-facing display parity explicit in handoff to Shopify/Woo tasks, but do not modify those repositories. A preview must never be the security authority at send time: Background re-resolves current wrapper and session eligibility.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-009`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-26T07:24:51Z. Attempt 0 review history is preserved below.

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

## Execution Ownership Amendment

- Date: 2026-10-26.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-BACKGROUND-009` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, task scope, acceptance criteria, validation requirements, dependency gate, Ready eligibility, and attempt 0. The existing Architect Review follow-up and BG007 shared-dispatcher reconciliation requirement remain unchanged. This amendment does not itself claim an implementation attempt.
