---
id: ARCH-038-COMMERCE-002
architecture_id: ARCH-038
title: Execute immutable Studio test execution policies
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-COMMERCE-001
enables:
  - ARCH-038-COMMERCE-003
created: 2026-10-13
updated: 2026-10-17
---
# Execute immutable Studio test execution policies

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_commerce`
- Repository: `moda-interact-commerce`

## Objective

Resolve the selected Studio policy source at Test Conversation creation and execute all its turns using a fixed, validated budget with consistent logging and bounded run lifecycle.

## Context

Recent Preview debugging exposed separate logged versus actual output-token values and a 120-second Redis reservation lifetime. COMMERCE-001 adds saved PREVIEW, read-only effective LIVE and temporary CUSTOM policy selection; execution must remain consistent across these paths and follow-up turns.

## Scope

- At **Start Conversation**, validate the authorised selected Shop and selected source: (a) saved PREVIEW Shop-over-Platform, (b) explicit read-only effective LIVE Merchant-over-Price-Plan-over-Platform, or (c) temporary custom budget. Do not permit accidental fallback between LIVE and PREVIEW contexts; fail closed for missing/invalid policy and unknown persisted schema versions.
- For custom source validate `deadlineMs`, `outputTokens`, `modelSteps` and `remoteCalls` as supported positive safe integers and against actual provider, runner, Redis reservation and termination feasibility. Do not persist custom values in `CommerceModelPolicy`, `CommerceAuditEvent` or another permanent configuration store; bounded Preview session state may retain the snapshot for recovery.
- For PREVIEW/LIVE sources, resolve two policy-controlled fields (`deadlineMs`, `outputTokens`) and preserve current test-runner defaults for `modelSteps` and `remoteCalls` (these are **not** DB policy keys under schema version 1).
- Consume the `PreviewExecutionLimits` component inputs only through the typed, authorised Test Conversation creation request; validate server-side and never allow polling controls, subsequent messages or retries to override limits.
- Freeze exact effective `deadlineMs`, `outputTokens`, `modelSteps`, `remoteCalls`, mode, field sources and applicable policy versions in the isolated Test Conversation at creation; each admitted run consumes that frozen snapshot for execution, reservation/timeout control and structured logging. Changed UI inputs, saved policy rows and LIVE plan changes affect only newly created Test Conversations.
- Reconcile configured deadline with Redis reservation lifetime (currently 120 seconds) and cancellation/reconciliation/retry behaviour.
- Maintain existing adaptive status polling as presentation only, with no budget changes on polling.
- Add tests for page rerenders, conversation reuse, run duplication, custom input tampering, selected-Shop authorisation and policy/plan changes during a conversation.

## Out of Scope

- Do not perform LIVE customer workflow execution, LIVE policy writes or changes to the Background resolver; the **explicit read-only Studio simulation** may resolve the LIVE budget for a trusted Shop.
- Do not alter Shared budget constraints or Admin LIVE UI.

## Requirements

- No discrepancy between RUNNER_STARTED and Shared commerce.turn.started budget values.
- Invalid over-reservation deadline gives actionable validation, not a permanently RUNNING run.
- On retry/reconciliation and subsequent turns in the same Test Conversation, reuse the same effective budget snapshot. A new selection requires starting a new conversation.
- Preview policy cannot affect actual Background calls.

## Work Items

- [x] Implement all three policy-source resolvers/validators and conversation-level immutable snapshot wiring, including authorised read-only LIVE inspection and temporary custom budget acceptance.
- [x] Tie timeout/reservation checks to effective deadline and ensure runtime uses the frozen per-conversation budget rather than the obsolete process-wide environment overrides. COMMERCE-003 owns their final declaration/parser/documentation removal.
- [x] Add focused runtime, cross-context isolation, concurrent edit, long-lived conversation, custom no-persistence, error and polling regressions.
- [x] Return and display the authoritative frozen policy after creation and same-ID replay; cover changed server policy and uncertain-start reconciliation.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` (PREVIEW persisted read and explicitly requested LIVE read-only resolution), COMMERCE-001 typed Start Conversation policy selection, existing Shared runner and Redis Preview session/run state. No new database field or Shared runner API.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-COMMERCE-001`

## Enables

- `ARCH-038-COMMERCE-003`

## Acceptance Criteria

- [x] Exact effective values appear in logs and runner input; browser polling inputs cannot affect execution budgets and no configured process environment override supersedes the selected source.
- [x] Run terminal status remains durable under timeout/cancel/retry.
- [x] Changes to saved policy, merchant LIVE plan/policy or custom controls affect **new Test Conversations only**; existing conversation follow-ups, retries and run logs retain their original selected source and four runner limits.
- [x] Custom mode never writes policy or audit rows; explicit LIVE mode reads effective policy only, remains inside Preview execution and never changes live customer turns.
- [x] Invalid or impossible custom limits fail before a conversation starts, with a visible actionable error.
- [x] Successful creation and replay return the stored server policy snapshot, and the UI labels only that snapshot frozen.

## Validation

- [x] Focused Preview service/reservation/runner integration tests for saved PREVIEW, read-only LIVE and custom modes
- [x] Redis-backed regression for long run and policy change
- [x] Relevant typecheck, production build, changed-file lint and git diff checks

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-COMMERCE-002` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. The portable definition was materialised on the canonical parent task branch during developer preparation. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Attempt 3 corrections are implemented and validated; awaiting developer-update self-review. Attempt 1 and Attempt 2 reviews and evidence are preserved. The task must remain in `review`, not `complete`, because `completion_mode` is `developer`.

### Attempt 3 Preparation

- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-002`, branch `task/ARCH-038-COMMERCE-002`, clean before claim; parent task branch was synchronized to its remote.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-002`, branch `task/ARCH-038-COMMERCE-002`, clean at `048df599c1fbc671b383445190e495c4e178f27e`, matching `origin/task/ARCH-038-COMMERCE-002` and containing current `origin/main` `957bc9ac4b8f6c2cf3849cff75926758292d7ee6`.
- Implementation `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Explicit dependencies `ARCH-038-DATABASE-001` and `ARCH-038-COMMERCE-001` remain complete. No shared/default checkout or other task worktree is used.

### Attempt 2 Preparation

- Canonical parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-002`, branch `task/ARCH-038-COMMERCE-002`, clean at `43bea0d3d084059cf97397fbe50b4ec15e149ba0`, matching `origin/task/ARCH-038-COMMERCE-002`; current `origin/main` `34626f4dc284a01dfa54cd67b330f8153d12a7d4` is an ancestor.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-002`, branch `task/ARCH-038-COMMERCE-002`, clean at `048df599c1fbc671b383445190e495c4e178f27e`, matching `origin/task/ARCH-038-COMMERCE-002`; current `origin/main` `957bc9ac4b8f6c2cf3849cff75926758292d7ee6` is an ancestor.
- Implementation `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Explicit dependencies `ARCH-038-DATABASE-001` and `ARCH-038-COMMERCE-001` are both complete. The previously observed uncommitted `development.log` change was no longer present when this attempt was prepared; neither worktree had user changes overwritten.

### Files Changed

12 implementation and test files in `moda-interact-commerce` for the Attempt 3 corrections. Implementation commit `0db7a70` is pushed to `origin/task/ARCH-038-COMMERCE-002`.

### Work Completed

- `PreviewService.startConversation()` returns the policy from the persisted conversation snapshot for both existing same-ID replay and the `claimConversation()` result. The latter also covers a concurrent claim replay and avoids returning a locally re-resolved policy that differs from the stored winner.
- The no-store creation route returns that server policy. The Studio client validates the exact response structure, allowed source/provenance values, four bounded positive limits and policy-version fields; a malformed response remains an uncertain start.
- The screen no longer calls its browser-side selection frozen. It only labels the policy frozen after a successful creation/replay response and displays the authoritative four limits, source provenance and policy versions.
- Added service, route, client, component and screen regressions for policy changes between browser selection and admission, original-policy retention on same-ID replay, invalid responses, and uncertain-start reconciliation with the original request ID. Existing request filtering and access-control behavior remain intact.

### Validation Results

- `npm run test:arch020-preview-integration`: passed, 46 tests.
- `npm run test:arch020-preview-integration:redis`: passed, 10 tests.
- Focused Preview service/route/client/screen tests: passed, 73 tests. The final strict response-validator client/screen/component run passed, 36 tests.
- `npm run typecheck`: passed after updating a stale component-test fixture to the authoritative response contract.
- Final `npm run build`: passed through schema/manual/runtime packaging and smoke checks, Prisma generation, Next production compilation, type generation and route output. Two existing Nunjucks dynamic-dependency warnings remain. One intermediate packaged-runtime smoke invocation failed nondeterministically; the standalone smoke rerun and final complete build both passed.
- Changed TypeScript-file ESLint: zero errors, four warnings in existing test code (`preview-integration.test.ts`, `preview-service.test.ts`, and `studio-tool-clients.test.ts`).
- `git diff --check origin/main...HEAD` and working-tree `git diff --check`: passed.
- Final structured full suite: 39 failed, 1,382 passed, 7 skipped. Failures compared with `ARCH025-COMMERCE-TEST-001`:
  - **11 stable baseline test identities**: `admin-explorer.test.tsx` — “builds and validates a representable selection before merging query fields into an existing draft”; `agent-configuration-retained-read.test.ts` — “tracks model and prompt CAS versions on one retained row across clear operations”; `agent-contract-validation.test.ts` — “rejects unknown scalar paths and non-list items paths”; `backend-postgres-rehearsal.test.ts` — “publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure”; `discovery-limits.test.ts` — “allows 60 sequential requests and rejects the 61st in the rolling window”; and all six documented `studio-workspace.test.tsx` failures (unexpected action failure class, reusable tool navigation, incremental invalid JSON, mounted detail reset, newer edits during earlier save, stale CAS input retention). The discovery test continues to time out at 30 seconds, matching the documented identity.
  - **28 non-baseline test identities**: `commerce-mcp-extraction-boundary.test.ts` (expects the MCP SDK dependency to be absent); 19 `shopify-admin-tools-ui.test.tsx` cases (Admin GraphQL authoring/save, current-test gate, stale/live test handling, no-shop/session gates, CAS/save/publication/policy behavior, editable mappings and result-schema behavior); `tool-authoring-request-component-boundaries.test.ts` (WooCommerce authoring boundary expects `<WooCommerceRestTest />`); and seven `tool-authoring-screen.test.tsx` cases (new-tool review/test flow, local definition preservation, exact creation identities, lost-create reconciliation and cancellation). These failures reproduced in an isolated rerun of the affected unchanged test files (29 failures including the baseline discovery timeout, 59 passes); all six inspected failure files match `origin/main` and none is changed by this task. The Shopify/Admin cases predominantly fail because tests expect the “Run Test” control or older target-shop/validation behavior that the current UI does not expose.
  Exact identities from the final JSON report:
  ```text
  commerce-mcp-extraction-boundary.test.ts :: ARCH-032-COMMERCE-005 complete MCP extraction boundary does not ship an embedded MCP route or server, and keeps only a private thin live client
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI offers Admin GraphQL and saves the exact validated definition
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI requires a current Shopify Test for Save and shows the exact server-rendered result without writes
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI stales a successful Shopify Test when arguments change without persisting the transient edit
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI does not call C082 when no Studio shop is selected
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI disables Shopify Test when the selected shop has no offline session
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI marks a failed C082 stage FAILED and never exposes a passed rendered result
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI prevents an old run from resurfacing after shop and arguments both cycle A-to-B-to-A
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI saves once with the current CAS token and refreshes from the canonical revision
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI keeps a Shopify CAS conflict visible without refreshing or overwriting local edits
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI persists editable JSON string and numeric literal mappings
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI recomputes aggregate validity when a literal mapping switches to an input mapping
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI keeps another invalid literal mapping invalid while fixing one literal
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI ignores invalid literal state for variables removed from the current document
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI derives and displays a read-only result shape without saving a persisted draft
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI does not accept an old Shopify Review validation after candidate A-to-B-to-A
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI saves the compiler-produced schema while preserving the persisted response template
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI keeps Admin publication disabled for ADMIN and surfaces the typed live-test gate for SUPER_ADMIN
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI saves, publishes through the canonical action, and reopens the exact Policy binding read-only
  shopify-admin-tools-ui.test.tsx :: Shopify Admin tool authoring UI preserves Policy local edits on CAS conflict and unknown mutation outcome without retrying
  tool-authoring-request-component-boundaries.test.ts :: new Tool authoring component boundaries keeps WooCommerce Response authoring provider-local while reusing the shared Result Template stage
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation does not unlock the first Review step after a failed Test
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation does not unlock the first Review step after a stale Test
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation preserves edited local definition values through tab switches
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation validates and creates the exact current Admin candidate without intermediate persistence
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation uses exact returned identities after confirmed creation
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation reconciles a lost final create without replaying the mutation
  tool-authoring-screen.test.tsx :: ToolAuthoringScreen new-tool local creation cancels from Review without writing and returns to Tools
  ```
  - **Five of six baseline collection failures recurred**: `agent-configuration-model-postgres.test.ts`, `agent-configuration-prompts-postgres.test.ts`, `c20-integration-fixture.test.ts`, `preview-openrouter-postgres.test.ts`, and `studio-integration-c20.test.ts`, blocked by absent disposable database/fixture configuration. The baseline `local-external-mcp-diagnostic.test.ts` collection failure did not recur. One **non-baseline collection failure** remains in `tool-editor-dispatch.test.tsx`: its unchanged mock omits the `ResponseTemplateSchema` export.
  - A preceding full run reported 38 rather than 39 failed tests; the final run’s additional failure is the exact stable-baseline Admin Explorer identity above. No failure in the Attempt 3 Preview/service/client/UI files appeared in the full-suite inventory. No unrelated production or test files were changed to chase these failures.

### Deviations

The repository-wide suite remains non-green. Non-baseline failures reproduce in unchanged files and were isolated; the extra collection failure is an unchanged mock-contract issue. These are recorded for architect triage rather than changed outside this task. The initial Attempt 1 report’s 69-failure aggregate is superseded by the identity-based comparison above.

### Assumptions

None.

### Unresolved Issues

Attempt 1 CR-1 through CR-3 are addressed in Attempt 3. The 45-line `development.log` deletion remains inherited from implementation commit `048df599`; its origin/purpose is unknown from the task record and no deletion or restoration was made in Attempt 3. Reviewer/developer ownership confirmation is requested before changing it. The repository-wide non-baseline failures and extra collection failure remain unrelated triage items as classified above.

### Architectural Concerns

None identified in this implementation review.

### Git / VCS

Task branch: `task/ARCH-038-COMMERCE-002`

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-002`
  parent branch: `task/ARCH-038-COMMERCE-002`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-002`
  implementation branch: `task/ARCH-038-COMMERCE-002`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes
  parent `origin/main` incorporated: yes, merge commit `499d047c1c16c5f263f4c030cf85985077aa7c2c`
  implementation remote task branch fast-forwarded: not needed
  implementation `origin/main` incorporated: already current at implementation commit

Implementation repository:
  repository: `moda-interact-commerce`
  commit: `0db7a7078f3b46192729e1a0463261478fb8a073`
  remote branch: `origin/task/ARCH-038-COMMERCE-002`
  pushed: yes

Parent workspace:
  task file: `docs/decisions/commerce/ARCH-038/COMMERCE-002-snapshot-studio-preview-execution-budgets.md`
  report commit: `ac34c3ed` (initial review record; Attempt 3 report is the current task-branch update)
  remote branch: `origin/task/ARCH-038-COMMERCE-002`
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no

## Architect Review

### Review Status

**Changes Requested — Attempt 1 (2026-10-17).** The task returns to `ready` for the next developer claim. Preserve `attempt: 1`, the submitted Completion Report, and the cleared executor/claim. This is **not** an architect acceptance or developer completion decision.

### Review Notes

The core mechanism is implemented: Preview and explicitly requested LIVE policy reads are server-resolved, CUSTOM_TEST is transient, a frozen policy is stored in the isolated Redis conversation snapshot, the Shared runner consumes those same four limits, and Studio caps the deadline at 90 seconds relative to the current 120-second reservation. Focused validation is encouraging but does not close the following findings.

**CR-1 — Show the actually admitted, server-frozen policy, not the browser's potentially stale policy.** In `test-conversations-screen.tsx`, `beginStart()` sets `frozenPolicy` to `frozenTestExecutionPolicy(...)` from the browser's current dashboard. In contrast, `PreviewService.startConversation()` resolves persisted PREVIEW/LIVE policy again on the server. The creation route currently returns only a conversation ID. An administrator can edit the policy between page render/inspection and Start, causing the UI to label different values and provenance as **Effective test budget (frozen)** than the values used by the Shared runner. Return or retrieve the authoritative, safely projected stored policy on successful creation and same-ID replay/reconciliation, and display those resolved limits/sources. Do not trust browser-supplied persisted policy values or change admission precedence. Add a focused regression proving a policy edit between initial browser selection and server creation does not misreport the frozen result; include the uncertain-start/same-ID replay case. Preserve access control over LIVE/CUSTOM snapshots.

**CR-2 — Reconcile the 69 failing full-suite tests against the pre-task baseline.** The Completion Report provides a count and one example but no failing identities or comparable baseline execution. `docs/development-baseline.md` records `ARCH025-COMMERCE-TEST-001`, with a **specific stable failure set** (not a blanket exemption for a historic aggregate count). Record the 69 current failing identities/reasons and compare with the baseline and/or a matched run on the implementation pre-task revision using the same Node/dependencies/environment. Investigate each new, worsened or changed failure; fix a demonstrated task regression within this task. If no task regression is found, record reproducible equivalence evidence and do not change unrelated code merely to obtain a green suite. The untouched prompt-editor lint errors can be treated separately only with an evidenced baseline/no-regression classification.

**CR-3 — Complete the required validation and preparation evidence.** The task checks `Relevant typecheck/build and git diff --check`, but the Completion Report does not record an `npm run build` outcome. Run the declared build after corrections (or explicitly record the real blocker and leave the item unchecked), focused Preview and Redis tests, typecheck, changed-file lint and `git diff --check`. Add the launcher-resolved start-of-attempt preparation/submodule hydration evidence to the Completion Report; do not create a new implementation commit solely to reproduce launcher discovery evidence. The supplied archive has no Git metadata, so published commit/branch identities are currently report evidence rather than independently authenticated Git history.

### Reviewed Files

- `src/commerce/preview/service.ts`, `types.ts`, `run-budgets.ts`, Redis store and Preview runtime composition.
- `src/commerce/execution-policy/policy-service.ts` and `src/studio/execution-policy/contracts.ts`.
- `src/studio/test-conversations/{client,contracts,preview-execution-limits,test-conversations-screen}.ts*` and the Preview creation HTTP route.
- Preview, Redis, Test Conversations UI/client and policy regression tests; the submitted Completion Report; `docs/development-baseline.md`.

### Validation Reviewed

- Reported passing: 45 focused Preview tests, 10 Redis regressions, 32 policy/UI tests, `npm run typecheck`, and changed-file ESLint (no errors; four warnings).
- Reported failing: package-wide 69 tests and two untouched prompt-editor ESLint errors. Their equivalence to a current pre-task baseline is not yet demonstrated.
- Source comparison: the submitted 25 Commerce patch files match the 2026-10-16 20:43 snapshot after applying the supplied Attempt 1, 2 and 3 patches in order; this is file-content evidence, not a replacement for Git commit verification.
- Full build and independent runtime execution were not established from this portable archive.

### Architecture Conformance

**Partial, pending corrections.** The immutable server-side execution and Redis snapshot boundaries align with ARCH-038, but the displayed frozen selection can diverge from the executed server snapshot. The broader regression status and required build evidence remain unresolved. No database, Shared runner, Background, Gateway or `_index.md` change is authorised by this review.

### Follow-up

Reclaim **ARCH-038-COMMERCE-002** as the next developer execution attempt, address CR-1 through CR-3, update the Completion Report and return this same task to `review`. Do not start COMMERCE-003 or SYSTEM-TEST-002. Preserve all historical Attempt 1 evidence and the developer completion boundary.

### Prior submission state (preserved)

The archived pre-review placeholder from the original submission was:

> ## Architect Review
>
> ### Review Status
>
> Pending architect review
>
> ### Review Notes
>
> Review the broader package test/lint failures against the pre-task baseline; task-scoped Preview, Redis and UI validations pass.
>
> ### Reviewed Files
>
> Preview service, run-budget/types, Redis state store, execution-policy service, runtime wiring, Studio Test Conversations client/UI and focused tests.
>
> ### Validation Reviewed
>
> Focused Preview integration (45/45), Redis regression (10/10), execution-policy UI/contracts (32/32), typecheck and changed-file ESLint pass. Package-wide suite/lint have unrelated failures noted in the Completion Report.
>
> ### Architecture Conformance
>
> Pending architect review
>
> ### Follow-up
>
> None

## Developer Self-Review - Changes Requested (Attempt 2)

### Review Status

Changes Requested. The Attempt 2 implementation branch contains no source or test correction for the Attempt 1 findings. Its only delta from the Attempt 1 implementation commit `9d71d488611ea286326c8bccb041d3d0ce6010ad` is deletion of 45 lines from `development.log` in commit `048df599c1fbc671b383445190e495c4e178f27e`.

### Required Corrections

1. **CR-1 — Display the server-frozen policy.** Return or retrieve a safely projected authoritative stored policy after successful conversation creation and same-ID replay/reconciliation. Update the Studio client/UI to display those server-resolved values and sources, not the browser's pre-start policy snapshot. Add regressions for policy changes between browser inspection and server admission and for uncertain-start/same-ID replay; preserve LIVE/CUSTOM authorization boundaries.
2. **CR-2 — Reconcile the full-suite failures.** Run the required full `npm test`, record every failing test identity and reason, and compare them with the exact stable identities and six collection failures documented by `ARCH025-COMMERCE-TEST-001` or a matched run at the pre-task implementation revision using the same Node, dependency tree and environment. Investigate every new, changed or worsened failure and fix any demonstrated task regression; do not treat the historical 69-failure aggregate as a blanket exemption.
3. **CR-3 — Complete and record validation.** Run the focused Preview service/reservation/runner tests, Redis regression, `npm run typecheck`, package `npm run build`, changed-file lint, and `git diff --check` after corrections. Record actual results, including any failure as unverified/incomplete. Retain the canonical launcher/worktree and submodule evidence already recorded, and document the purpose/ownership of the `development.log` deletion rather than silently reverting it.

### Validation Reviewed

No validation commands were run for Attempt 2 during this review. The focused Preview (45), Redis (10), UI/policy (32), and typecheck results in the Completion Report are historical Attempt 1 evidence. Attempt 1 did not establish a package build result; its full-suite report recorded 69 failures without an identity-by-identity comparison to the documented baseline.

### Attempt and Claim State

Attempt 2 is preserved as the reviewed cycle. The task returns to `ready` with `executor: null` and `claimed_at: null`; the next `/moda_developer_create ARCH-038-COMMERCE-002` claim increments to Attempt 3. No implementation files were changed during this review.

## Developer Self-Review - Accepted (Attempt 3)

### Review Status

Accepted for authorised review. The task is `review`, `executor: null`, `claimed_at: null`, `attempt: 3`. This is not developer completion; `completion_mode: developer` remains in force.

### Review Notes

- CR-1 is addressed: creation, same-ID replay and concurrent claim replay return the persisted snapshot policy; the route/client/UI transport and display it as server-frozen only after a validated response.
- CR-2 is addressed: the final 39 failed tests and six collection failures are inventoried against the exact baseline. Eleven failing test identities and five collection failures match the documented baseline. Twenty-eight non-baseline failures reproduce in isolated unchanged files, and the one non-baseline collection failure is an unchanged mock missing `ResponseTemplateSchema`. No task-owned Preview/client/UI failure was observed.
- CR-3 is addressed: focused Preview, Redis, UI/client, typecheck, final build, changed-file lint and both diff checks are recorded above. The only build warning is existing Nunjucks dynamic dependency warnings; the transient runtime smoke failure did not reproduce and the final build passed.
- The inherited 45-line `development.log` deletion remains untouched. Its purpose/owner is unknown from available task history and has been surfaced for developer/reviewer confirmation.

### Validation Reviewed

See Attempt 3 Validation Results above. The final full suite is non-green, but task-specific checks and production build pass; all non-baseline failures were independently reproduced and shown to be outside the changed files.

### Follow-up

Authorised review may accept this attempt or request another correction cycle. Do not merge to `main`, complete the task, or start COMMERCE-003/SYSTEM-TEST-002 from this review transition.
