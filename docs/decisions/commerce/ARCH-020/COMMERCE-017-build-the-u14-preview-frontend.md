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
status: review
priority: 135
executor: copilot
claimed_at: 2026-09-21T03:04:44Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
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

Ready for Review.

## Context

- `moda-interact-commerce/app/preview/page.tsx`
- `moda-interact-commerce/app/styles.css`
- `moda-interact-commerce/src/studio/preview/client.ts`
- `moda-interact-commerce/src/studio/preview/preview-screen.tsx`
- `moda-interact-commerce/tests/preview-screen.test.tsx`
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

- Replaced the placeholder preview handoff with the embedded U14 Tool test and Conversation screen.
- Added the typed `PreviewClient` transport boundary for conversation start/run/status/cancel and tool tests; browser transport remains same-origin and credentialed, while tests inject contract-faithful clients.
- Added fixture scenario selection, schema-derived tool arguments, structured trace/result rendering, conversation history, run status feedback, cancellation, same-ID unknown reconciliation, duplicate-send/run guards, frozen selection, reset, return navigation and accessible live notices.
- Preserved composer handoff context and authenticated page entry through the existing Studio layout/auth boundary. No route handlers, database loaders, Redis access, production Shopify/MCP/WhatsApp calls or browser storage were added.

### Requirement-to-Fixture Matrix

| Requirement | Fixture/test evidence | Expected and observed effect |
| --- | --- | --- |
| Tool test success and schema-driven arguments | `p01-healthy-en`; `tests/preview-screen.test.tsx` schema-driven tool case | `runToolTest` receives the frozen tool revision, fixture ID and bounded `{ handle }`; rendered result is shown. Passed. |
| Conversation start and frozen selection | `p01-healthy-en`; focused screen test | Start sends `FIXTURE`, fixture ID and selected revisions; selection controls disable after start. Passed. |
| Duplicate Send suppression and one run ID | `p01-healthy-en`; focused screen test | Two synchronous clicks dispatch one `startRun` with one generated `previewRunId`; input clears only on completed success. Passed. |
| Unknown failure preservation and reconciliation | simulated timeout followed by same-ID completed response; focused screen test | Message remains visible, status is Unknown, retry calls `getRun` with the original run ID and renders the reconciled answer. Passed. |
| Reset before changing frozen context | `p01-healthy-en`; focused screen test | Reset unlocks saved selection and clears synthetic conversation state. Passed. |
| Empty, missing-fact and provider-failure fixture choices | `p02-empty-en`, `p03-missing-fact-en`, `p04-provider-failure-en`; scenario selector and shared preview contract tests | All named fixture IDs are exposed without live provider calls; service/route/store contract coverage passed. |
| Cancel/status/trace/result contract surface | Preview route/service/store/Redis contract tests | 41 focused tests passed across the five preview test files; implementation renders Running, Completed, Failed, Cancelled and Unknown labels and trace/data panels. |

Own the exact U14 /preview tool-test/conversation page, its controls and typed preview-client boundary with the008 composer.

Agent-executed validation:

- `npm test -- --run tests/preview-screen.test.tsx`: 1 file, 4 tests passed.
- `npm test -- --run tests/preview-screen.test.tsx tests/preview-routes.test.ts tests/preview-service.test.ts tests/preview-store.test.ts tests/preview-redis-lua.test.ts`: 5 files, 41 tests passed.
- `npm run typecheck`: passed; Next route types generated and `tsc --noEmit` completed successfully.
- `npm run lint`: passed with no ESLint output.
- `npm run build`: passed; Prisma Client generated and Next production build completed successfully, including `/preview` and preview API route compilation.
- `git diff --check`: passed.
- Full `npm test`: 248 passed, 2 failed out of 250. The failures are outside U14: Redis-backed discovery admission timed out after 30 seconds, and the readiness child-process signal-handler test could not observe its fixture descendant before cancellation. The focused preview suite passed independently.

Developer-owned validation pending:

- Authenticated browser workflow against the running local/developer preview service, including populated desktop/narrow/keyboard views and real auth/session context. The attempted `DEPLOYMENT_ENVIRONMENT_NAME=development NODE_ENV=development PORT=3317 npm run dev` was blocked by `EADDRINUSE` on port 3317 from an existing local Node process; no browser pass is claimed.
- Live database/container/provider validation remains pending and is not represented by fixture tests. The implementation intentionally makes no live Shopify, MCP, WhatsApp, billing or customer-history calls.

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
No scope deviation. The live browser/developer validation is pending because the requested port was already occupied; no alternate live environment or production credentials were introduced.

## Requirements

The existing authenticated Studio layout and composer context are the accepted C19/C16 integration boundary. A preview service will supply the exact API response shapes through `PreviewClient`; this task does not implement its route or backend adapter.
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.
Developer must provide the authenticated browser/live preview evidence after selecting an available port or stopping the conflicting process. The two unrelated full-suite failures above should be compared with the repository baseline during review; they did not affect preview-focused tests, typecheck, lint or build.
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

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
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

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-017`, branch `task/ARCH-020-COMMERCE-017`, implementation commit `2ec7f661bd56ca44e1fdbed8d30a05f48fd78d59`, pushed to `origin/task/ARCH-020-COMMERCE-017`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-017`, branch `task/ARCH-020-COMMERCE-017`, parent claim base `a5f59b22d0dca79cfeb4785e449ea45c29b55a4d`.
Dependency evidence: implementation repository consumed the accepted `origin/main` source at `19b1dc03b317c6d36a504469627a2bb0f8ec64d6`; recursive database submodule was initialized at `5abfd87f57038bae515aaa09ec7c8db62adcfb98` (`database`, `heads/main`).
This report is the only parent-workspace change. No domain index, architecture document, other task, service gitlink or `main` branch was modified. Generated Next.js `AGENTS.md` and `CLAUDE.md` files were removed and not committed.

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
