---
id: ARCH-038-COMMERCE-001
architecture_id: ARCH-038
title: Configure persisted and temporary Studio test execution policies
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-COMMERCE-002
  - ARCH-038-SYSTEM-TEST-002
created: 2026-10-13
updated: 2026-10-16
---
# Configure persisted and temporary Studio test execution policies

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_commerce`
- Repository: `moda-interact-commerce`

## Objective

Provide authorised Studio Preview policy editing plus a Test Conversations selector for saved PREVIEW, read-only LIVE simulation or temporary custom execution budgets.

## Context

Current Test Conversations polling settings are browser-only and separate from execution budgets. Persisted Preview Platform/Shop deadline/output settings move to `CommerceModelPolicy` rows filtered by `context=PREVIEW`; ad hoc debugging additionally needs temporary per-conversation overrides that must never change LIVE or persisted PREVIEW rows.

## Scope

- Extend Commerce Studio Agent Configuration/Test Conversations with a clearly labelled **Test-only Preview Execution Policy** section for Platform and selected Shop; use a reusable Commerce-local schema-driven editor/allowlisted version-1 descriptors, not raw JSON or an import of Admin UI source.
- Add authorised server actions/API reading/updating only `context=PREVIEW` policy rows, validating `budgetSchemaVersion=1`, sparse JSON budget keys, audit reason and edit-version fencing.
- Show `deadlineMs` with unit and readable seconds equivalent and `outputTokens` as per-model-invocation tokens, with descriptions and independent per-field source. Preview Platform fields are required; selected-Shop test fields have **Override / Inherit** controls, and cleared keys fall back to PREVIEW Platform without copying defaults.
- Display a read-only effective Preview budget and per-field provenance, and a context/scope/shop/environment-filtered paginated **Policy History** (actor, timestamp, reason, before/after) from CommerceAuditEvent.
- Add a **Test Conversations execution policy** selector with modes **Saved Studio Preview** (default), **Effective LIVE policy (read-only simulation)** and **Custom test policy**. Display selected Shop, effective values, field-level source and a prominent **Test only** label. Only explicit LIVE simulation may read LIVE policy rows; it must not mutate them, switch the customer runtime, or silently fall back between contexts.
- In Custom mode, make `deadlineMs` and `outputTokens` directly editable with units and validation, plus optional advanced, clearly labelled `modelSteps` and `remoteCalls` for that test. These advanced properties are ephemeral runner inputs, **not** new `CommerceModelPolicy.budget` schema-version-1 keys. Provide Reset to Studio defaults; editing a control must not write a policy or audit row.
- Freeze policy source and custom draft when **Start Conversation** is submitted; subsequent changes to controls must apply to a newly started conversation only. COMMERCE-001 owns the UI/read boundary; COMMERCE-002 owns server-authoritative creation validation and immutable conversation/run snapshot execution.
- Preserve polling controls as an independent browser-only configuration. Polling fields must not leak into execution policy snapshots or run-admission payloads; explicitly authorised policy-source/custom inputs may be added only to the **Start Conversation** contract after server validation.

## Out of Scope

- No LIVE Admin Platform/Plan/Merchant edits, no Background or Shared changes.
- No merchant-facing capability to change execution budgets.

## Requirements

- Studio SUPER_ADMIN/authorised platform operator is required for policy mutation and for temporary custom/LIVE-simulation selection, with server-side checks; merchant-facing surfaces receive none of these controls.
- Preview model authorisation and selected Shop tenant scope remain enforced.
- Values displayed are for testing only and never modify live customer budgets. LIVE simulation resolves the trusted selected Shop's current plan/merchant/platform values for **read-only test snapshot** use, not a PREVIEW-policy fallback. Unresolvable LIVE policy must be explicit, not replaced silently. Future persisted JSON keys require approved versioned descriptors; do not auto-expose unknown keys.
- Existing dev env vars are documented as migration/bootstrap defaults, not a permanent hidden extra precedence. The editor must provide inline validation and clear disabled-in-flight Save state, require a reason, and surface stale edit-version conflicts with reload recovery.

## Work Items

- [x] Add scoped Preview policy read/mutation surface and strictly authorised read-only effective LIVE policy inspection for the selected Shop.
- [x] Build a reusable Commerce-local versioned Preview budget editor, descriptions, Platform-required and Shop-Override/Inherit views, and effective source/provenance summary.
- [x] Add scoped paginated Preview policy-history read/UI using existing audit rows.
- [x] Add a policy-source selector, custom budget and advanced-runner controls, reset/defaults, descriptions and explicit validation. Confirm custom edits do not mutate stored policy rows and later UI changes cannot alter a started conversation.
- [x] Add auditing, validation, CAS/conflict reload, in-flight disable, audit-history isolation, schema allowlist, independent-field inheritance and LIVE read-only permission tests.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` for persisted `context=PREVIEW` Platform/Shop settings; reads effective `context=LIVE` values only when explicitly selected for read-only Studio simulation. COMMERCE-001 defines a typed, authorised Test Conversation source/custom-input handoff consumed by COMMERCE-002 at conversation creation; run-admission and polling payloads remain separate. No DB changes for temporary custom fields.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-COMMERCE-002`
- `ARCH-038-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] A test-Shop override changes only the selected Shop Preview scope.
- [x] Each budget key can be cleared independently by omission; no explicit JSON null or empty override row.
- [x] Live policy remains unchanged and unauthorised writes are rejected.
- [x] Platform fields are mandatory, Shop fields inherit independently, field labels/units/help and effective sources are visible; raw JSON is not the UI.
- [x] Policy History shows only authorised Preview entries; concurrent edits and invalid values have actionable recovery without partial writes.
- [x] Studio can select saved Preview, effective read-only LIVE, or an unsaved custom test budget; custom values include `deadlineMs`, `outputTokens` and optional advanced `modelSteps`/`remoteCalls`, with per-field validation and Reset.
- [x] Custom input changes never write a policy/audit row, affect no merchant LIVE execution and cannot alter an already started Test Conversation. No separate polling field appears in policy or run payloads.

## Validation

- [x] Focused Studio configuration actions and UI tests (including all three modes, reset, no-write custom path, LIVE read-only authorisation and run-input isolation)
- [x] Relevant typecheck/lint/build scripts (changed-file lint is clean; package-wide lint has the pre-existing untouched-file errors recorded below)
- [x] git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-COMMERCE-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This task definition was materialised and claimed for Attempt 1 on 2026-10-16. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

In Review — Attempt 1 claimed by the developer at 2026-10-16T11:49:10Z. Developer completion mode is retained; explicit developer completion remains pending.

### Files Changed

Implementation commit `80cdad5d10251d3bc7e671557d7cf8b820e5f4b9` is the current published task-branch tip. Changed files:

- `app/preview/page.tsx`
- `app/styles.css`
- `development.log` (local runtime capture from the original implementation commit)
- `src/commerce/execution-policy/policy-service.ts`
- `src/studio/agent-configuration/agent-configuration-screen.tsx`
- `src/studio/execution-policy/contracts.ts`
- `src/studio/execution-policy/policy-editor.tsx`
- `src/studio/execution-policy/server-actions.ts`
- `src/studio/test-conversations/contracts.ts`
- `src/studio/test-conversations/conversation-panel.tsx`
- `src/studio/test-conversations/conversation-settings.tsx`
- `src/studio/test-conversations/preview-execution-limits.tsx`
- `src/studio/test-conversations/test-conversation-drawer.tsx`
- `src/studio/test-conversations/test-conversations-screen.tsx`
- `tests/arch038-preview-execution-limits.test.tsx`
- `tests/arch038-preview-policy-actions.test.ts`
- `tests/arch038-preview-policy-contracts.test.ts`
- `tests/arch038-preview-policy-editor.test.tsx`
- `tests/arch038-preview-policy-service.test.ts`
- `tests/preview-page.test.tsx`
- `tests/test-conversations-client.test.ts`
- `tests/test-conversations-component-boundaries.test.ts`
- `tests/test-conversations-screen.test.tsx`

### Work Completed

Implemented environment-scoped PREVIEW policy reads and audited writes, explicit read-only LIVE inspection, Shop-scoped sparse overrides, effective-source/history views, and the reusable Preview policy editor. Added the `PreviewExecutionLimits` component beside browser polling controls, wired a typed frozen policy selection into Start Conversation, and kept policy inputs out of run-admission/polling calls. LIVE-simulation and Custom starts remain blocked until COMMERCE-002 supplies server-authoritative admission. The focused suites cover authorization, policy contracts/service/actions/editor, all selector modes, reset/validation, frozen UI state, and polling/run-input separation.

### Validation Results

Validation results:

- Focused Studio policy and Test Conversations tests: 9 files, 54 passed, 0 failed. Command: `./node_modules/.bin/vitest run tests/arch038-preview-execution-limits.test.tsx tests/arch038-preview-policy-actions.test.ts tests/arch038-preview-policy-contracts.test.ts tests/arch038-preview-policy-editor.test.tsx tests/arch038-preview-policy-service.test.ts tests/preview-page.test.tsx tests/test-conversations-client.test.ts tests/test-conversations-component-boundaries.test.ts tests/test-conversations-screen.test.tsx`.
- `npm run typecheck` — passed.
- Changed-file ESLint across all task source and test files — passed. The initial-load effect in `policy-editor.tsx` was deferred to a microtask in commit `80cdad5` to resolve the task-local lint error.
- `npm run lint` — fails on two errors in unchanged `src/studio/prompt-editor/markdown-prompt-editor.tsx` (render-time ref writes at lines 26–27); 15 warnings are also reported in untouched files. The task-owned files lint clean.
- `npm run build` — passed; webpack reported non-fatal Nunjucks dynamic-dependency warnings.
- `git diff --check` — passed.

Physical worktree isolation and synchronization:

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-COMMERCE-001`, branch `task/ARCH-038-COMMERCE-001`; clean and up to date with its remote task branch.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-COMMERCE-001`, branch `task/ARCH-038-COMMERCE-001`; clean and pushed at `80cdad5d10251d3bc7e671557d7cf8b820e5f4b9`.
- At attempt preparation, both task worktrees were launcher-prepared, clean and synchronized; the implementation `database` submodule was initialized at gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.
- The shared workspace and shared Commerce reference checkout were not switched or used for implementation; no other task worktree was reused.
- At reconciliation, the implementation branch was three commits ahead and four commits behind `origin/main`; the mainline-only commits are later Commerce/ARCH-030 work. No mainline merge was performed during this review.

### Deviations

The original implementation diff includes `development.log`, a local runtime capture committed with the feature work. It was left unchanged during reconciliation. Package-wide lint remains blocked by the two untouched errors listed under Validation Results.

### Assumptions

The LIVE-simulation and Custom policy choices are presentation/handoff only in this task; the component blocks starting those modes until COMMERCE-002 implements server-authoritative admission and immutable execution snapshots.

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None

## Developer Self-Review

### Review Status

Passed — Attempt 1 satisfies this task's bounded Preview policy read/edit and Test Conversations UI handoff scope. Focused tests, typecheck, changed-file lint, build and diff checks pass. The package-wide lint failure is limited to two unchanged files and is disclosed above. `completion_mode: developer` is retained; explicit developer completion remains pending.

### Reviewed Files

All task implementation files in the published diff from `origin/main` to `80cdad5d10251d3bc7e671557d7cf8b820e5f4b9`, including the new policy service/actions/editor, Test Conversations controls, tests, and the committed runtime log.

### Validation Reviewed

See the exact focused test command, pass counts, typecheck, changed-file lint, package-wide lint result, production build and diff check in the Completion Report.

### Architecture Conformance

The implementation keeps PREVIEW mutation scoped to PREVIEW rows, exposes LIVE values only through explicit privileged read-only inspection, keeps custom policy inputs ephemeral, and separates execution-policy inputs from polling/run-admission calls. Server-authoritative LIVE/Custom conversation admission remains assigned to COMMERCE-002.

### Follow-up

Return to `moda_architect` for review. Do not begin COMMERCE-002 or another enabled task from this reconciliation. The developer may explicitly complete this task after the accepted review.
