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

**In Progress — Attempt 1, blocked on an architectural decision.** The developer's existing claim at `2026-10-26T07:24:51Z` remains recorded in task YAML. This report is an escalation for the architect, **not** a completed implementation, formal review submission, or new attempt. The developer/architect workflow must authorise any later transition to `blocked` or `ready`; this documentation patch does not change the claim.

### Files Changed

Preparation-only source present in the supplied BG009 implementation worktree:

- `moda-interact-background/src/services/recovery-conversation/human-wrapper-preparation.service.ts` (new).
- `moda-interact-background/tests/unit/services/recovery-conversation/human-wrapper-preparation.test.ts` (new; execution not evidenced).

This handoff patch changes only `docs/decisions/background/ARCH-047/BACKGROUND-009-integrate-human-conversation-wrappers.md`. The uploaded archive does not establish whether the implementation files have been committed or pushed.

### Work Completed

- Added a preparation-only seam over BG005's `renderConversationResponse(source: 'HUMAN')`, using the accepted command ID as stable rendering identity and the original merchant text as input.
- The preparer distinguishes rendered, explicitly unconfigured passthrough, refusal, and non-applicable post-window commands. It does **not** grant moderation approval or provider-send permission.
- Added unit-test source for identity and exact merchant text, passthrough/refusal behaviour, exclusion of the post-window command kind, and shared-logger exception propagation. The tests have **not** been shown to execute in the supplied terminal log.
- Deliberately **did not** connect prepared text to `HumanCommandDispatcherService`, the moderation assessment service, `OutboundSendFenceService`, or the WhatsApp provider. These would currently disagree on the authoritative content.

### Validation Results

The uploaded `typescript(20261026-072937)` terminal recording shows:

- `npm run prisma:generate` — completed successfully (Prisma Client 6.19.3 generated).
- `git apply --check --whitespace=error-all` for the preparation patch — no error reported.
- `git apply --whitespace=error-all` — no error reported.
- `git diff --check` — no error reported.
- The archive was created by the task-worktree compressor using separate reported parent and implementation paths. This is **not** a substitute for launcher-resolved start-of-attempt synchronisation/branch evidence.

**Not evidenced or claimed passed:** focused Vitest, build/typecheck after the preparation patch, ESLint, PostgreSQL integration, moderation/final-send/provider equality, or an implementation commit/push. All corresponding task Validation and Acceptance Criteria remain unchecked.

### Deviations

**Intentional preparation-only implementation.** The task's in-window dispatcher/moderation/final-send integration remains incomplete, because the currently installed durable command and moderation constraints do not permit the prepared wrapped body to become the canonical moderated and sent content. No insecure workaround or parallel raw-text send path was introduced.

### Assumptions

- The provided 26 October worktree snapshot is the inspected development baseline; schema and migration files in this archive do not by themselves prove deployment state.
- `ARCH-047-BACKGROUND-005` is recorded `complete` in the uploaded task definitions.
- The existing ARCH-040 tenant/control/window/STOP/final-send/moderation guards remain mandatory; BG007 retains the separately owned post-window Meta-template path.

### Unresolved Issues

**Blocking decision: durable prepared HUMAN_TEXT content.** The immutable raw accepted command, canonical moderation identity, final-admission message construction, and provider send must be reconciled before BG009 can meet R1/R2/R3/R6.

- The architect must decide the durable representation and consistency boundary; direct mutation of accepted `MerchantConversationSendCommand.textBody`, an unmoderated append, or in-memory/Redis-only prepared content is not acceptable.
- A database-owned schema/migration and SQL moderation guard change (or an architect-approved equivalent durable design) is required before Background may safely wire the prepared text into the existing dispatcher and admission transaction. Assign a real task ID and update dependencies only through architecture coordination.
- BG007 also changes `human-command-dispatcher.service.ts`. Reconcile its final branch before BG009 acceptance; do not modify BG007's post-window flow within this task.
- Following the decision and prerequisite implementation, run the required unit, database integration, compensation/retry, and full-message/payload equality validations; capture branch/worktree/synchronisation evidence before formal review.

### Architectural Concerns

**Evidence in the supplied repository:**

1. `database/prisma/migrations/20261017214500_arch040_remove_outreach_sequence_policy/migration.sql` enforces immutable accepted-command identity/payload, including `textBody`, through `whatsapp.arch040_command_guard()`.
2. `src/services/conversation-moderation/moderation-assessment.service.ts` resolves a HUMAN_TEXT command's canonical moderation content from `command.textBody`, and rejects a supplied `effectiveText` that differs (`moderation_content_identity_mismatch`).
3. `database/prisma/migrations/20261018092000_arch040_moderation_template_content_digest/migration.sql` enforces the HUMAN_COMMAND/TEXT moderation digest against the same command text in `whatsapp.arch040_moderation_subject_guard()`.
4. `src/services/recovery-conversation/outbound-send-fence.service.ts` constructs the admitted HUMAN_TEXT `ConversationMessage` from `command.textBody`; `src/services/recovery-conversation/human-command-dispatcher.service.ts` also sends `command.textBody` to WhatsApp. A prepared wrapper currently has no durable, authoritative pre-moderation handoff to either step.

**Architect decision requested:** Choose and document an architecture-owned contract (for example, an immutable, set-once prepared body plus provenance/digest on the command, **or an equivalent durable one-to-one prepared-message record**) satisfying all of the following:

- Preserve the original accepted merchant text, request payload identity, idempotency key, tenant/conversation/command relationship and audit history unchanged.
- Atomically freeze the complete customer-visible body and selected wrapper provenance under a valid command claim **before** moderation; retry/restart/replay must reuse that frozen body rather than re-render under a changed assignment.
- Make the frozen full body the canonical HUMAN_TEXT moderation subject, including database digest validation and existing ALLOW/BLOCK/REVIEW_REQUIRED, model/policy-version and fail-closed requirements. Do not reclassify HUMAN text as AGENT/AUTOMATION to bypass the guard.
- Bind final admission to the exact moderated digest, current tenant/HUMAN control/24-hour window/STOP/consent and wrapper-publication policy, then persist `ConversationMessage.content` from that same frozen body. The provider-send payload must equal the durably admitted message. Decide explicitly what happens when the wrapper assignment changes after freezing but before admission (suppress/reprepare under a safe revision contract, never silently change admitted text).
- Preserve one-way provider permits, existing UNKNOWN/compensation/idempotency handling, and the separate BG007 post-window template/billing behaviour.
- Require PostgreSQL integration coverage for uniqueness, concurrent leases, restart/replay, mid-flight control or wrapper changes, wrapper-only moderation denial, stale moderation, and exact moderated/persisted/provider-text equality. Preserve structured error reporting through `@modainteract/moda-interact-shared/logging` without swallowing unexpected failures.

**Ownership and sequencing decision requested:** `moda_architect` to approve a `moda_database` prerequisite and any necessary cross-repository contracts, update the ARCH-047 execution graph/task dependencies, and then return BG009 to its existing developer execution path for the bounded Background wiring/tests. If the architect selects a different design, explicitly revise BG009's acceptance criteria and track the remaining full-content moderation/final-send obligation. Until that decision, **do not treat the preparation-only patch as BG009 acceptance evidence**.

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
