---
id: ARCH-047-BACKGROUND-005
architecture_id: ARCH-047
title: Implement prepared AI and human conversation wrapper renderer
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 30
executor: developer
claimed_at: 2026-10-26T06:14:27Z
attempt: 2
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-BACKGROUND-008
  - ARCH-047-BACKGROUND-009
created: 2026-10-24
updated: 2026-10-26
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

- [x] Implement `src/services/conversation-wrappers/` with a wrapper lookup/read-only context adapter and pure **prepared-runtime** renderer, plus a small public facade and injected dependencies.
- [x] Resolve current `WhatsAppConversationWrapperActiveSlot` (`SHARED`, optional `AI` or `HUMAN` override), matching approved definition/locale and conversation language from DB001. Use `WhatsAppTemplateLocale.localeAst` only to read the **Admin-compiled prepared wrapper projection** stored there, not to parse/compile its authoring AST.
- [x] Resolve verified shop/customer/checkout fields from the existing conversation/recovery context without crossing tenant boundaries. Insert the already-authored response text in the one required response slot; return composed text plus provenance/version and typed refusal when unavailable.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [x] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report.

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

- [x] SHARED/AI/HUMAN precedence, activation CAS change, language fallback and unpublished/wrong-kind/wrong-shop negative cases.
- [x] Prepared header + `response.body` + footer with optional valid checkout URL; missing/expired checkout omits conditional section; no invented/cross-tenant URL.
- [x] Exact-once replay, already-wrapped input, malformed prepared projection, duplicate/missing response slot and total message size boundary.
- [x] Demonstrate no provider calls, AI calls, moderation writes or checkout mutations; verify preserved original response and bounded logs.
- [x] PostgreSQL integration with active slot and locale fixtures, focused unit/build/typecheck and `git diff --check`. Full AI/human send tests belong to BG008/009.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

## Validation

- [x] Run the focused new tests and relevant existing regression suites identified above; record exact executable commands and outcomes.
- [x] Run the repository-declared build/typecheck (for this snapshot: `npm run build`) and focused ESLint where applicable; do not assume every repository has identical scripts.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence.
- [x] When integration depends on a real PostgreSQL/BullMQ service, run the repository's declared integration harness or record the missing environment explicitly; do not claim an unrun test passed.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Keep rendering separate from active-wrapper repository reads and conversation context reads. The renderer should not import Admin source or modify Shop/Checkout tables. A compiled wrapper projection is a **runtime data interface**, not a second AST. If the database stores only an authoring AST with no prepared projection, stop and request an Admin data-contract correction.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-005`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.

**Architectural concern:** Shop/checkout read paths may currently be null for non-recovery conversations; never fabricate association. A missing verified checkout is a typed outcome, not permission to mutate another repository.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-26T06:14:27Z. Attempt 1 review history is preserved below.

### Files Changed

Implementation repository `moda-interact-background` — 10 new files, as recorded by commit `c25295a`:

- `src/services/conversation-wrappers/contracts.ts`
- `src/services/conversation-wrappers/index.ts`
- `src/services/conversation-wrappers/projection.ts`
- `src/services/conversation-wrappers/render.ts`
- `src/services/conversation-wrappers/repository.ts`
- `src/services/conversation-wrappers/selection.ts`
- `src/services/conversation-wrappers/service.ts`
- `tests/unit/services/conversation-wrappers/projection-and-render.test.ts`
- `tests/unit/services/conversation-wrappers/service.test.ts`
- `tests/integration/conversation-wrapper-rendering.integration.test.ts`

No database schema, merchant/Admin application, Meta provider, sending, billing, moderation, or `docs/decisions/**/_index.md` files were changed by BG005. This task-definition update is a separate parent-worktree documentation change.

### Work Completed

- Implemented a modular, read-only wrapper repository, prepared projection validator, pure renderer, slot/language selector and injectable service facade using the Admin-persisted `localeAst.prepared` data; the authoring AST is not reparsed.
- Resolved SHARED versus AI/HUMAN active-slot precedence, definition/locale eligibility, language fallbacks, versioned activation, prepared content digest, typed unavailability/rejection and a bounded output length.
- Verified conversation/recovery/shop/customer relationships before using checkout context. Missing, cancelled or stale checkout information omits optional checkout content; stored checkout URLs are restricted to a matching merchant host.
- Preserved original AI/human response text within the envelope, supplied deterministic application provenance/replay handling, and refused malformed/double-wrapped input.
- Left AI/human calling integrations, moderation of the complete rendered message, final admission/STOP guards, and provider sending to BG008/BG009.
- Logged operational outcomes through `@modainteract/moda-interact-shared/logging`; unexpected repository/service exceptions are logged with bounded identifiers and rethrown, without logging the response or checkout URL.
- Fixed the three `no-control-regex` ESLint findings in the renderer and repository without changing the intended control-character policy.

### Validation Results

All commands below were recorded from the dedicated Background implementation worktree; the run evidence is in `typescript(20261026-035450)`, `typescript(20261026-044857)`, and `typescript(20261026-050429)` as supplied for this review handoff.

- `npm run build` — PASS. Prisma client generation and TypeScript compilation completed without reported errors (post-correction run, 2026-10-26).
- `npx vitest run tests/unit/services/conversation-wrappers` — PASS: 2 test files, 14 tests, after the ESLint correction.
- `npx eslint src/services/conversation-wrappers tests/unit/services/conversation-wrappers tests/integration/conversation-wrapper-rendering.integration.test.ts` — PASS: no reported errors after the correction. The preceding run had three `no-control-regex` errors, which were corrected and rechecked.
- `npm run test:integration -- tests/integration/conversation-wrapper-rendering.integration.test.ts` — PASS: 1 file, 2 actual PostgreSQL integration tests on 2026-10-26 at 05:02. Covered versioned active-slot changes, verified checkout recovery context, replay provenance, stale/cancelled/missing checkout omission, and cross-shop/customer mismatch refusals. A preceding test run failed at disposable PostgreSQL startup (`P1001`), then the rerun passed; this was a setup failure before test execution, not a failing application assertion.
- `git diff --check` — passed during this review for the implementation delta and parent task report delta.
- Review reruns on 2026-10-26: `npx vitest run tests/unit/services/conversation-wrappers` — 2 files, 14 tests passed; focused `npx eslint ...` — no reported errors; `npm run build` — passed (Prisma generation and TypeScript compilation); `npm run test:integration -- tests/integration/conversation-wrapper-rendering.integration.test.ts` — 1 file, 2 PostgreSQL integration tests passed.
- `git commit -m "feat(arch-047-background-005)"` — PASS: implementation commit `c25295a`, 10 files, 969 insertions.
- `git push -u origin task/ARCH-047-BACKGROUND-005` — PASS: published `task/ARCH-047-BACKGROUND-005` to the Background origin (reported by Git in the terminal log).

**Physical worktree / start-of-attempt evidence:**

- Parent task worktree reported by the developer archive helper: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-005`.
- Background implementation worktree reported by test output and archive helper: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-005`.
- Implementation branch and pushed commit verified above. Parent task branch publication is **not** verified by the supplied log; this documentation patch must be committed/pushed separately on `task/ARCH-047-BACKGROUND-005` in the parent worktree.
- The original `/moda_developer_create` launcher packet, canonical root identity, parent/implementation remote fast-forward and `origin/main` incorporation decisions, and recursive implementation submodule-preparation output are **not present** in the Attempt 1 transcript. Do not represent these checks as passed. Attempt 2's canonical packet must be recorded as Attempt 2 evidence only; it cannot prove Attempt 1 preparation.
- Independent current comparison during review: implementation `task/ARCH-047-BACKGROUND-005` is 9 commits behind and 1 ahead of `origin/main`; parent task branch is 31 behind and 4 ahead. Neither branch has current `origin/main` as an ancestor. The implementation delta is limited to the ten wrapper files listed above and the parent delta is this task record. No merge was performed during review.
- The local untracked `typescript` terminal capture was not staged in the implementation commit.

### Deviations

No production runtime scope expansion was identified. An incremental correction replaced control-character regexes to satisfy focused ESLint. The original integration retry initially failed to connect to its temporary PostgreSQL service and succeeded on the subsequent run.

### Assumptions

This record uses the supplied combined archive and validation terminal captures as implementation evidence; it is not an independent verification of Git remotes, launcher preparation, or runtime execution from this review environment. Versioned Admin-prepared wrapper projection remains the upstream runtime contract.

### Unresolved Issues

- Historical launcher start-of-attempt synchronization and recursive submodule-preparation evidence remains unverified. Provide the original prepared execution packet if available. If it is unavailable, the reviewer must determine the policy-compliant worktree remediation/validation needed rather than fabricate historical records.
- Parent task Completion Report updates for this review must be committed and pushed on the dedicated parent task branch.

### Architectural Concerns

- Non-recovery conversations may lack a verifiable checkout; the renderer intentionally omits optional checkout fragments rather than fabricate associations.
- Merchant-host validation deliberately omits otherwise valid hosted checkout URLs with a different host until a trusted ownership contract exists. This is a safe limitation to consider in BG008/BG009 integration.
- BG008/BG009 must preserve wrapper application provenance and moderate the complete rendered message before the established final-send gates; BG005 does not itself send or moderate.

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

- Date: 2026-10-26
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, task scope, acceptance criteria, validation requirements and current Ready eligibility.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.

## Developer Self-Review - Changes Requested

- Review date: 2026-10-26; reviewed attempt: 1.
- Current focused validation passed: wrapper unit tests 14/14, focused ESLint with no reported errors, `npm run build`, and the focused PostgreSQL integration test 2/2. `git diff --check` passed. These checks do not resolve the branch synchronization or historical launcher evidence gaps.
- Required correction: keep the implementation changes scoped to the ten task files, then use the canonical developer launcher for Attempt 2 to synchronize both dedicated task branches with their task remotes and current `origin/main`. Inspect and resolve any merge conflicts or behavior changes introduced by that synchronization. Rerun the focused unit, lint, build, and PostgreSQL integration checks against the synchronized implementation. Update the Completion Report with the exact preparation packet, parent/implementation branch revisions, and validation outcomes.
- Historical evidence: Attempt 1's launcher packet is unavailable. Do not rerun preparation to manufacture Attempt 1 evidence or label a later packet as proof of that attempt. Record the limitation truthfully; any explicit acceptance of this historical gap must be separately authorized and precisely scoped.
- No implementation-source defect was established by the current focused checks. The task remains unaccepted until synchronized-branch revalidation and the report correction are complete.
- Lifecycle transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1`. The next canonical developer claim increments the attempt exactly once.
