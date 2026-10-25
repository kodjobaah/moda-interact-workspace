---
id: ARCH-047-BACKGROUND-005
architecture_id: ARCH-047
title: Implement prepared AI and human conversation wrapper renderer
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-BACKGROUND-008
  - ARCH-047-BACKGROUND-009
created: 2026-10-24
updated: 2026-10-25
---

# Implement prepared AI and human conversation wrapper renderer

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This is a **portable task definition** prepared from the 24 October 2026 workspace snapshot and consolidated DB001 Attempt 7 contract. It is not a repository implementation, task claim or evidence of a created worktree/branch. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

## Objective

Render Admin-prepared checkout-context wrapper content around an existing AI/human response, without parsing the authoring AST or sending messages.

## Context

ARCH-047 permits only immutable, Moda Admin-authored template definitions. Admin validates and compiles the AST and persists already-prepared transport/runtime data. Background handles independently testable execution modules and **never re-parses the Admin authoring AST**. The DB001 schema provides translation runs/items/batches, compiled Meta registrations, publication targets and wrapper pointers. Messaging delivers Meta template status observations through the existing BullMQ path; Background persists/assesses them. Existing outbound admission remains authoritative.

## Scope

- Implement `src/services/conversation-wrappers/` with a wrapper lookup/read-only context adapter and pure **prepared-runtime** renderer, plus a small public facade and injected dependencies.
- Resolve current `WhatsAppConversationWrapperActiveSlot` (`SHARED`, optional `AI` or `HUMAN` override), matching approved definition/locale and conversation language from DB001. Use `WhatsAppTemplateLocale.localeAst` only to read the **Admin-compiled prepared wrapper projection** stored there, not to parse/compile its authoring AST.
- Resolve verified shop/customer/checkout fields from the existing conversation/recovery context without crossing tenant boundaries. Insert the already-authored response text in the one required response slot; return composed text plus provenance/version and typed refusal when unavailable.

## Out of Scope

- No AI answer generation, human message editing, product/cart mutation, AST authoring/compiling/translation, Meta template submission, moderation decisions, provider sending, billing, follow-up admission or Shopify/Woo UI code.
- Do not introduce a second global renderer library or a new database column/table just to duplicate the prepared wrapper already owned by Admin.

## Requirements

**R1 — Prepared-render input.** Admin owns the editable AST and emits a versioned, immutable **runtime wrapper projection** into a documented portion of each ready `WhatsAppTemplateLocale.localeAst` JSONB value. That projection has ordered literal/variable fragments for header/footer, a single response slot, and explicit conditional fragments; it is **not** the AST. Background only interprets these prepared fragments. If Admin has not persisted such a projection, refuse rendering and surface the missing contract rather than reverse-engineering the AST.

**R2 — Selection.** AI uses an active AI override if present else SHARED, Human uses HUMAN override if present else SHARED; absence of an approved matching language follows the documented shop/conversation language fallback or returns an explicit unavailable outcome. Verify the chosen definition is eligible as a wrapper **in application code**, not through database CHECKs.

**R3 — Context and fallbacks.** Resolve `shop.name`, `customer.firstName`, checkout URL/summary from the current verified conversation-scoped checkout. Missing or stale checkout information causes explicitly optional conditional fragments to be omitted, not invented. Never use a URL belonging to a different customer/shop. Allow a safe no-wrapper result when configured by application policy; no blank checkout placeholders.

**R4 — Exactly once and safe content.** Use prepared version/content digest and message identity to prevent double-wrapping on retries. Preserve the original AI/human response exactly (only deterministic wrapping/escaping allowed). Bound complete output length/variable values for WhatsApp; return a typed failure before moderation/send if oversized/invalid. Wrappers do not confer service-window or consent eligibility.

**R5 — Module boundary.** Return a rendered message/provenance; no moderation/send inside renderer. Caller integrations must moderate the **whole rendered message** and preserve final admission fences. Logging contains IDs/lengths/status only, not customer messages or checkout URLs.

## Work Items

- [ ] Implement `src/services/conversation-wrappers/` with a wrapper lookup/read-only context adapter and pure **prepared-runtime** renderer, plus a small public facade and injected dependencies.
- [ ] Resolve current `WhatsAppConversationWrapperActiveSlot` (`SHARED`, optional `AI` or `HUMAN` override), matching approved definition/locale and conversation language from DB001. Use `WhatsAppTemplateLocale.localeAst` only to read the **Admin-compiled prepared wrapper projection** stored there, not to parse/compile its authoring AST.
- [ ] Resolve verified shop/customer/checkout fields from the existing conversation/recovery context without crossing tenant boundaries. Insert the already-authored response text in the one required response slot; return composed text plus provenance/version and typed refusal when unavailable.
- [ ] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

## Interfaces / Contracts

**Consumes** `WhatsAppConversationWrapperActiveSlot`, `WhatsAppTemplateDefinition` and ready `WhatsAppTemplateLocale` rows, plus pre-existing `Conversation`/`CheckoutRecovery` read models. **Admin owns** the prepared wrapper projection format; it must be documented and fixture-tested at the seam. No Meta Graph API, Shared AST/renderer package or additional DB migration required.

**Background-local port:** `renderConversationResponse({conversationId, source:'AI'|'HUMAN', messageIdentity, responseBody, languageTag}): Promise<{kind:'rendered',body,wrapperDefinitionId,localeId}|{kind:'unavailable'|'rejected',reason}>`. It is a pure preparation step, not a send.

## Dependencies

- `ARCH-047-DATABASE-001`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

- `ARCH-047-BACKGROUND-008`
- `ARCH-047-BACKGROUND-009`


## Acceptance Criteria

- [ ] SHARED/AI/HUMAN precedence, activation CAS change, language fallback and unpublished/wrong-kind/wrong-shop negative cases.
- [ ] Prepared header + `response.body` + footer with optional valid checkout URL; missing/expired checkout omits conditional section; no invented/cross-tenant URL.
- [ ] Exact-once replay, already-wrapped input, malformed prepared projection, duplicate/missing response slot and total message size boundary.
- [ ] Demonstrate no provider calls, AI calls, moderation writes or checkout mutations; verify preserved original response and bounded logs.
- [ ] PostgreSQL integration with active slot and locale fixtures, focused unit/build/typecheck and `git diff --check`. Full AI/human send tests belong to BG008/009.
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

Keep rendering separate from active-wrapper repository reads and conversation context reads. The renderer should not import Admin source or modify Shop/Checkout tables. A compiled wrapper projection is a **runtime data interface**, not a second AST. If the database stores only an authoring AST with no prepared projection, stop and request an Admin data-contract correction.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-005`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.

**Architectural concern:** Shop/checkout read paths may currently be null for non-recovery conversations; never fabricate association. A missing verified checkout is a typed outcome, not permission to mutate another repository.

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

Shop/checkout read paths may currently be null for non-recovery conversations; never fabricate association. A missing verified checkout is a typed outcome, not permission to mutate another repository.

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
