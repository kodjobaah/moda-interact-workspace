---
id: ARCH-047-BACKGROUND-008
architecture_id: ARCH-047
title: Integrate prepared wrappers into AI conversation responses
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 40
executor: developer
claimed_at: 2026-10-26T07:16:16Z
attempt: 1
depends_on:
  - ARCH-047-BACKGROUND-005
enables: []
created: 2026-10-24
updated: 2026-10-26
---

# Integrate prepared wrappers into AI conversation responses

## Architecture

Architecture ID: `ARCH-047`.

Architecture document: `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`.

Coordinator: `moda_architect`.

This task definition was supplied as a portable architect handoff and materialized on 2026-10-26 in the canonical parent task worktree on `task/ARCH-047-BACKGROUND-008`. Materialization does not imply implementation or a claim. No new ARCH-047 Shared package is assumed. The parent architecture and `BACKGROUND-001` require reconciliation to the final Admin-owned AST/compilation and DB-backed keyed-segment translation decisions before dependent work is promoted.

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

**R6 — Remove superseded AI composition paths.** Once BG005 is integrated, remove any obsolete direct raw-response-to-provider branch that bypasses the prepared wrapper and full-message moderation. Preserve the intentionally unwrapped result when no published wrapper applies: it must still pass through the same moderation and admission path, not a second legacy send path. Remove no-longer-used adapters/mocks only after a reference audit; do not delete AI ownership/order or provider-window safeguards.

## Work Items

- [x] Integrate BG005 into the existing `ConversationTurnProcessor`/CommerceAgent outbound turn after an AI response is generated but before persisted moderated outbound message and provider delivery.
- [x] Keep the existing AI conversation ordering, ownership checks, generation budgets, abuse/moderation gates and outbound WhatsApp admission unchanged except for inserting the prepared wrapper step.
- [x] Add narrow tests and dependency-injected facade call rather than duplicating wrapper rendering, checkout reads or AST logic.
- [x] Build focused unit/integration fixtures for the specified inputs, outputs and negative/failure cases.
- [ ] Complete repository-declared validation and record actual changed paths, task isolation, branch commits and test evidence in the Completion Report. Code, test and commit evidence is recorded below; the original launcher start-of-attempt packet and recursive submodule-preparation evidence remain unverified.

## Interfaces / Contracts

**Consumes** BG005 prepared wrapper renderer and existing `ConversationTurnProcessor`, `runCommerceAgent`, `AiTurnOwnershipService`, `moderationTurnGate` and outbound WhatsApp admission. No Admin AST or Meta JSON. The outbound message identity passed to BG005 must be stable across retries.

## Dependencies

- `ARCH-047-BACKGROUND-005`


**Important:** Tasks are not Ready merely because their files exist. Confirm each dependency has `status: complete` (not only Passing tests / Accepted review) before claiming. DB001 is developer-owned and may remain in progress pending explicit completion. Dependencies outside this task must be resolved by their owners; do not implement across repositories.

## Enables

None in this nine-task Background set.

## Acceptance Criteria

- [x] AI answer unchanged when wrapper disabled; enabled SHARED/AI wrapper adds correct shop and current valid checkout context.
- [x] Full rendered text is moderated, including forbidden content introduced by wrapper; provider must not receive blocked content. Integration uses a real PostgreSQL projection and an injected moderation/delivery seam, not live Meta delivery.
- [ ] Human takeover before/during/after model generation, service window closure, STOP/consent, credit and ordering regressions. Focused takeover and stale-turn cases passed, but the supplied logs do not independently enumerate all previously existing service-window, STOP/consent and credit regression cases.
- [x] Retry/double-wrap protection and one provider send; read-only commerce tool assertion. Unit tests and source inspection confirm a single wrapper insertion before the existing sender; no Commerce tool mutation was added.
- [x] Focused conversation-turn, moderation and WhatsApp worker tests; integration/build/`git diff --check`. See Validation Results for the latest rerun and earlier broader-suite reports.
- [x] No source/template authoring, shopper checkout mutation, Meta edit-existing-template call, externally authored Meta template adoption, or bypass of existing WhatsApp final-send safeguards is introduced.
- [x] Task implementation is modular, separately testable, and stays within `moda-interact-background/`; externally owned gaps are reported, not silently implemented.

- [x] A source-level check confirms there is one AI outbound composition/admission path (with a no-wrapper case), no hidden second raw-response send path, and no duplicate legacy wrapper helpers. Old mocks expecting bypass behaviour have been updated.

## Validation

- [x] Run the focused new tests and relevant existing regression suites identified above; record outcomes. The latest terminal capture includes the 54-test conversation-turn suite; earlier task validation reported 131 passing unit tests and 6 passing PostgreSQL integration tests. The exact earlier command output is not in the newest recording.
- [x] Run the repository-declared build/typecheck (`npm run build`) and focused ESLint; both completed without reported errors on 2026-10-26.
- [ ] `git diff --check`, inspect changed-file scope and capture task-isolated start-of-attempt and mirrored-branch evidence. Diff/changed-file/branch evidence is present; the launcher preparation/synchronisation and recursive submodule packet is not reproduced in the supplied capture.
- [x] PostgreSQL integration: six tests passed in the earlier local validation; the new integration suite exercises real database state and an injected moderation/delivery seam. The latest capture reran the corrected unit test, not the database suite.

## Stop Condition

After finishing Work Items, Acceptance Criteria and Validation, fill the Completion Report, change task status to `review`, return both the implementation and parent task-branch evidence to `moda_architect`, and **STOP**. Do not start any enabled/adjacent task or update `docs/decisions/**/_index.md`.

## Implementation Notes

Make one minimal insertion in the authoritative outbound AI reply path; don't wrap generated prompt/tool messages or conversation history, only the final customer-visible message. Use the existing shared moderation API boundary unchanged.

Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md` and the deterministic `/moda-task` launcher packet. Use launcher-resolved dedicated parent and implementation worktrees, both on `task/ARCH-047-BACKGROUND-008`; synchronise from canonical roots, not a prior task worktree. Preserve exact source semantics and existing test expectations; use the published `@modainteract/moda-interact-shared/logging` for generic structured logs, not a second logger. Prefer small coordinator/repository/pure-helper files over 300+ line catch-all services.



## Completion Report

### Status

Ready for Review — Attempt 1, developer execution. Implementation commit `db627fe` was pushed to `origin/task/ARCH-047-BACKGROUND-008` on 2026-10-26. This is a submission for review, **not** architect acceptance or explicit developer completion.

### Files Changed

Implementation repository: `moda-interact-background/` (11 files; 625 insertions, 4 deletions in commit `db627fe`):

- `src/services/conversation-turn-processor.service.ts`
- `src/services/conversation-wrappers/compose-ai-outbound.ts` (new)
- `src/workers/whatsapp.worker.ts`
- `tests/integration/conversation-ai-wrapper.integration.test.ts` (new)
- `tests/integration/conversation-turn-scheduling.integration.test.ts`
- `tests/integration/fixtures/arch040-ai-turn.fixture.ts`
- `tests/unit/services/conversation-turn-processor.service.test.ts`
- `tests/unit/services/conversation-turn-processor/ai-wrapper.cases.ts` (new)
- `tests/unit/services/conversation-turn-processor/facade-abuse-admission.cases.ts`
- `tests/unit/services/conversation-wrappers/compose-ai-outbound.test.ts` (new)
- `tests/unit/services/outbound-whatsapp-admission/outbound-message-delivery.service.test.ts`

No database schema, Admin, Meta template authoring, Shared contract or `_index.md` change is included.

### Work Completed

- Added a narrow BG005 composition adapter that consumes the original AI response with the reserved message ID and requires `source: "AI"`; verifies message provenance and exact no-wrapper passthrough.
- Injected the published `ConversationWrapperService` into the WhatsApp conversation-turn processor using `onMissingSlot: "passthrough"`. Invalid/unavailable published wrappers fail closed, with no raw-text fallback.
- Kept a single `sendPreparedText` path for both wrapped and deliberately unwrapped text, preserving existing full-message moderation, final-send admission, recipient/window, billing and delivery ownership.
- Rechecked turn ownership and inbound version after the asynchronous BG005 read, suppressing obsolete AI results and HUMAN takeover races.
- Reused outbound reservation identity for replay; did not add Commerce mutators, alternative provider sends or duplicate wrapper parsing.
- Logged unexpected processing and cleanup errors through the shared structured logger and propagated the errors; a two-line follow-up fixed `AggregateError.cause` while retaining both error objects in `errors`.
- Added unit and PostgreSQL-backed integration coverage for wrapper selection, concurrent claims, no-wrapper passthrough, moderation of wrapper-inserted forbidden text, stale-turn/HUMAN suppression, replay and exception handling.

### Validation Results

- `git apply --check --whitespace=error-all` and `git apply --whitespace=error-all` for the Attempt 1 ESLint correction: no errors reported in the 2026-10-26 terminal capture.
- `npm run build`: **PASS**; Prisma Client generated and TypeScript compiled without errors.
- `npx vitest run tests/unit/services/conversation-turn-processor.service.test.ts`: **PASS — 54/54** in the latest terminal capture.
- `npx eslint src/services/conversation-turn-processor.service.ts tests/unit/services/conversation-turn-processor/ai-wrapper.cases.ts`: **PASS**, no lint errors reported after the correction.
- `git diff --check`: **PASS**, no whitespace errors reported.
- Broader focused validation from the preceding task report: **131 unit tests passed and 6 PostgreSQL integration tests passed**. Those results were reported before the two-line lint correction; the latest capture independently reran build, 54 affected unit tests and lint, but not the integration suite.
- Source review against the submitted snapshot: BG005 is invoked after model completion, the same prepared-send path receives the final text in either case, and no separate direct AI-result-to-provider send branch was identified.
- Git evidence: implementation task branch `task/ARCH-047-BACKGROUND-008`, commit **`db627fe`** (`feat(arch-047-background)`), successful GitHub push with upstream tracking established. The log shows the dedicated implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-BACKGROUND-008`, and the snapshot names the separate parent task worktree.
- The original launcher-resolved start-of-attempt synchronization packet and recursive implementation-submodule materialization evidence are **not present in the supplied terminal recording**. The presence of worktrees or a successful push does not substitute for that evidence.

### Deviations

No out-of-scope implementation changes identified. Full end-to-end Meta delivery, STOP/consent and billing admission were not newly implemented in BG008; those remain the existing outbound service's responsibility.

### Assumptions

- `ARCH-047-BACKGROUND-005` was `complete` at claim time per the canonical task record in the supplied snapshot.
- Existing `sendPreparedText` continues to enforce the authoritative whole-message moderation and final delivery rules; the BG008 integration tests deliberately inject the send/moderation seam rather than contact Meta.
- The developer claimed Attempt 1 at `2026-10-26T07:16:16Z`; applying the ESLint correction inside that claim did not constitute a new launcher attempt.

### Unresolved Issues

- Task-isolation/start-of-attempt packet and recursive submodule/synchronisation evidence remain unverified and must be provided or explicitly recorded as workflow non-conformance during review.
- The reviewer should confirm the full service-window, STOP/consent, credits and existing delivery regression evidence required by the composite Acceptance Criterion above, since the latest terminal capture does not enumerate all those cases.

### Architectural Concerns

No new cross-repository contract or schema change was introduced. Any required changes to other repository boundaries remain with their owning agents.

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
- Materialization: The portable architect definition was materialized in the canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-BACKGROUND-008` on `task/ARCH-047-BACKGROUND-008`. No external implementation worktree or commit is asserted.
- Change: The developer explicitly invoked `/moda_developer_create ARCH-047-BACKGROUND-008` for this Ready agent-owned task. Execution ownership transfers to the developer and completion mode is set to developer review.
- Preserved: `assigned_agent: moda_background`, coordinator, repository, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-BACKGROUND-005` routes as `complete` in its canonical task record.
- State before claim: `ready`, Attempt 0, `executor: null`, `claimed_at: null`. The canonical developer preparation workflow will synchronize the task worktrees and claim Attempt 1. No implementation or merge to `main` is performed by this ownership amendment.
