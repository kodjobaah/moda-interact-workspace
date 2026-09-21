---
id: ARCH-020-COMMERCE-017
architecture_id: ARCH-020
title: Build the U14 preview frontend
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 135
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-21
updated: 2026-09-21
---

# Build the U14 preview frontend

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own the exact U14 /preview tool-test/conversation page, its controls and typed preview-client boundary with the008 composer.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own the exact U14 /preview tool-test/conversation page, its controls and typed preview-client boundary with the008 composer.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [ ] Implement the complete embedded U14 screen and approved prototype hierarchy. Use C9.1 routes as defined; no alternate preview backend or duplicated budget logic.
- [ ] Implement the C19 PreviewClient interface with C9.1 exact request/result shapes, injected HTTP transport and contract fixtures. Do not load database bundles or implement backend adapters.
- [ ] Implement tool-test/conversation selection, schema-driven arguments, trace/reply/structured-details panels, errors and quotas; changing frozen selection requires Reset.
- [ ] Implement synchronous duplicate guards across mouse/keyboard, same-ID unknown reconciliation, cancel status, return context and C16 authenticated tab-local composer restoration.
- [ ] Run populated browser workflows against contract-faithful preview service fixtures and assert request IDs/payloads/counts. Component acceptance is independent of009;013 owns real service pairing.

## Interfaces / Contracts

Own U14 page entry and `src/studio/preview/` only. Reuse008 authenticated layout provider. No route handlers, Redis, database loaders or production backend composition.013 owns real PreviewBundleLoader and endpoint wiring. C9.1/C16/C19 remain binding.

### U14: tool tests and conversation traversal (COMMERCE-017)

Landing has **Tool test** and **Conversation** modes. Source context preselects
saved draft/revision/release; direct navigation requires explicit selection.

Tool test: choose saved tool revision, synthetic scenario (success, empty, missing
fact, provider failure), enter schema-driven input, Run -> same page with mapped
variables/arguments, structured facts, rendered text and validation/failure codes.
No live Shopify request. Editing test input invalidates visible success until
rerun. Return to tool links to U06; code/schema edits occur there.

Conversation: choose saved behaviour revisions or release, synthetic feature flags
and fixture basket. **Start conversation** freezes synthetic prompt/tool grant;
then show chat with message input, Send, Cancel run, Reset conversation, trace and
remaining limits. Default Fixture mode is deterministic. Explicit Model mode uses
separate preview credentials and C9 quotas; controls explain unavailable config
or exhausted budget. No production model credentials/customer transcripts.

Send creates one previewRunId before dispatch, disables duplicate sends, preserves
input on known failure and shows Running/Completed/Failed/Cancelled/Unknown.
Trace lists discovered tools, chosen tool/input, structured output and final answer.
Cancel requests cancellation of that same run and waits for confirmed status;
unknown state is reconciled before another run. C9 max20 turns,32k history,24h
retention and model budgets apply. Reset confirms abandoning synthetic state and
creates a new preview conversation; never replaces a live grant. Changing selected
release/tools/flags requires reset confirmation; an ongoing preview does not gain
new tools. Back returns the originating page, or U03 when entered from sidebar.

## Dependencies

- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.

## Enables

- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] U01: N10/N11 from every specified source and sidebar, populated tool test and multi-turn conversation, match exact routes/results; errors preserve inputs.
- [ ] U02: N13 draft response -> preview -> Back restores definition/members/reason/hash; refresh/sign-out loss shows required notice; no browser storage or URL payload.
- [ ] U03: repeated Send/Run/Cancel and uncertain status preserve one run/model-budget reservation; quota/owner/expired-state failures show correct accessible feedback.
- [ ] U04: C16 response/language fixtures, ungranted tools and changed release demonstrate immutable preview state and bounded referral.
- [ ] U05: desktop/narrow/keyboard views show actual populated workflows; auth guards remain active; UI fixtures cannot call live Shopify/MCP or WhatsApp; real loader evidence belongs to013.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-017. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.

## Architect readiness reconciliation — 2026-09-21

Ready, Attempt 0, executor/claimed_at null. COMMERCE-008 is architect-accepted
Complete at Attempt 6 (`8ba5e42`); COMMERCE-002 and SHARED-001 are already accepted
Complete. All explicit prerequisites are satisfied. Use C19 contract fixtures for
frontend component work;009 acceptance is not an added prerequisite, and013 owns
the real service pairing. No implementation attempt is claimed or launched by
this promotion. Normal preparation and accepted-source integration rules apply.
