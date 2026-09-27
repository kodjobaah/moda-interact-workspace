---
id: ARCH-021-COMMERCE-056
architecture_id: ARCH-021
title: Validate and clarify Agent contract authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 71
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-039
  - ARCH-021-COMMERCE-043
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Validate and clarify Agent contract authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make the existing Agent contract tab a self-contained, non-mutating validation checkpoint for the Tool fields exposed to the CommerceAgent: definition version, agent description, agent input schema and agent response template. Validation must reuse the canonical Tool-definition/publication rules, retain temporarily invalid authoring text locally with field-specific diagnostics, and perform no Tool persistence or provider I/O.

## Context

Manual validation of the completed local-only Tool authoring flow found that the Agent contract tab already has the correct structural boundary:

```text
src/studio/tools/authoring/agent-contract-tab.tsx
```

It is already composed by the new-Tool and persisted-DRAFT editors, so this task does **not** extract another component or redesign the tab structure.

The tab currently exposes:

```text
Definition SemVer
Description
Input JSON Schema
Response template
```

but its local feedback is largely limited to JSON parse failure. The canonical Commerce contracts already define stronger rules for semantic versioning, description bounds, the supported bounded input-schema subset, forbidden authority/credential inputs, response-template syntax/tokens and response-template compatibility with the processed result contract. Authors should discover those problems in the Agent contract tab rather than only at Review/Create/Publish.

The authoring lifecycle established by COMMERCE-039 remains authoritative:

```text
raw local form state
    -> may temporarily be incomplete/invalid

canonical local Tool candidate
    -> schema-valid authoring state

final Create / later persisted-DRAFT Save
    -> only durable boundary
```

Validation itself is never a persistence operation.

## Scope

Primary files are expected to include:

```text
src/commerce/tool-authoring/                       # named Agent-contract validation boundary/helper
src/commerce/tool-definition/contracts.ts          # consume/extract existing canonical helpers only when needed
src/commerce/tool-definition/publication.ts        # reuse/extract template-compatibility logic only when needed

src/studio/tools/authoring/agent-contract-tab.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx
src/studio/tools/*server-actions*.ts               # bounded non-mutating validation action if required

app/styles.css                                     # only small validation/help presentation if needed

tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx                   # where the shared Agent tab is exercised
tests/shopify-admin-tools-ui.test.tsx              # parity where the shared Agent tab is used
tests/*agent-contract*                             # focused tests may be added
```

Use the repository's existing authoring action/result conventions. Exact filenames may follow current ownership and module conventions.

## Out of Scope

- Extracting the Agent contract form into another React component; `AgentContractTab` already owns that boundary.
- Request-tab, Response-tab, Test-tab or Review-tab redesign.
- COMMERCE-053 Automatic response generation.
- COMMERCE-054/055 live Test execution or Test UI.
- Provider DNS/network calls, credential resolution/decryption or live execution.
- Persisting a new Tool, ToolRevision, audit event, validation receipt or publication proof.
- Saving a persisted DRAFT merely because validation succeeded.
- Phase 2 tab gating, locked tabs or mandatory Next/Previous progression.
- Changing the Tool descriptor or another cross-service contract.
- Database/Prisma schema changes.
- Weakening final Create/Save/Publish server validation.

## Requirements

### R1 — preserve the existing component boundary

`AgentContractTab` remains the bounded presentation component for this authoring surface.

Do not duplicate its fields back into `NewToolEditor` or `ToolEditor`, and do not create another architecture task/component merely to split the four-field form further.

Parent editors may own orchestration/state and pass validation callbacks/results into the existing tab.

### R2 — add a named Agent-contract validation boundary

Add/reuse one non-mutating, server-authoritative validation boundary for the current Agent contract. It must validate the Agent-facing contract without requiring the complete Request/Test/Review flow to be valid.

The validation input should contain only the current Agent-contract values plus the minimum current result-contract context required to validate response-template paths, conceptually:

```text
definitionVersion
description
inputSchema
responseTemplate
current processed-result/output contract context
```

Do not make Agent-contract validation perform Request construction, connection lookup, provider observation, live execution or Tool persistence.

Reuse/extract canonical validation logic from the existing Commerce Tool-definition/publication contracts rather than maintaining a second set of SemVer, input-schema or response-template rules.

### R3 — validate the complete Agent-facing contract

At minimum validate and report deterministic issues for:

```text
Definition version
- valid semantic version syntax/bounds required by the canonical Tool contract

Agent description
- required/non-empty
- canonical maximum length

Agent input schema
- valid JSON object
- accepted bounded InputSchema subset
- supported nested/array/scalar forms only
- canonical property/count/size bounds
- authority/credential inputs remain forbidden

Agent response template
- valid JSON object
- canonical text/items template shape
- bounded fixed/text fields
- valid {{result.*}} / {{item.*}} tokens
- no unknown/non-scalar referenced result paths
- itemsPath resolves to a valid list/item result when using an items template
- compatibility with the current processed-result/output contract
```

Diagnostics must use deterministic paths suitable for field-local UI presentation, for example:

```text
/definitionVersion
/description
/inputSchema/...
/responseTemplate/...
```

Do not expose raw internal exceptions as the normal author-facing message.

### R4 — preserve raw local authoring state

The tab must distinguish authoring memory from durable persistence.

Temporarily invalid user input MUST remain visible in local form state so it can be corrected, including:

```text
malformed Input schema JSON
malformed Response template JSON
unsupported Input schema content
invalid response-template tokens/paths
invalid Definition version
```

Do not snap the field back to the last valid value merely because the canonical parser rejects the current text.

Only parseable/canonical values may be promoted into the canonical local Tool candidate as appropriate. Neither raw form state nor the canonical local candidate is durably persisted for a new Tool until the existing final Create boundary.

For an existing persisted DRAFT, running Agent-contract validation MUST NOT save the DRAFT.

### R5 — show validation in the Agent contract tab

Provide one clear action such as:

```text
Validate agent contract
```

and show its success/errors in this tab.

Where practical, display issues next to the affected control/JSON editor rather than only as one undifferentiated message at the bottom.

A successful validation state must become stale immediately when any of these change:

```text
definitionVersion
description
inputSchema
responseTemplate
processed-result/output contract used for template compatibility
```

Validation success from an older candidate must never remain visually current after those inputs change.

### R6 — clarify terminology and help text

Use user-facing labels that explain the agent-facing purpose rather than implementation terminology alone. Prefer wording equivalent to:

```text
Definition version
Agent description
Agent input schema
Agent response template
```

Add concise help text explaining:

- Definition version is the semantic version of this Tool definition (for example `1.0.0`).
- Agent description explains the Tool to the CommerceAgent/model.
- Agent input schema defines the arguments the agent is allowed to provide when invoking the Tool.
- Agent response template formats the processed Tool result into the agent-facing Tool response.

Keep technical JSON editors available; this task does not introduce a separate visual schema/template designer.

### R7 — new-Tool and persisted-DRAFT parity

Where the existing shared `AgentContractTab` is used, validation behaviour must be consistent for:

```text
new local Tool authoring
persisted DRAFT authoring
```

For new Tools, validation operates entirely on the non-durable local candidate.

For persisted DRAFTs, validation checks the current unsaved editor candidate and does not require saving first.

Validation does not itself satisfy any live-Test requirement or publication-proof requirement.

### R8 — preserve free tab navigation

Agent-contract errors are visible in Agent contract, but this task MUST NOT disable Request, Response, Test or Review solely because Agent-contract validation has failed or has not yet run.

Phase 2 gating remains outside this task.

## Work Items

- [x] Add/reuse one named non-mutating Agent-contract validator using canonical Tool-definition/publication rules.
- [x] Validate Definition version and Agent description with deterministic field paths.
- [x] Validate Agent input schema including canonical bounds and authority/credential restrictions.
- [x] Validate Agent response-template syntax/tokens and compatibility with the current processed-result/output contract.
- [x] Add bounded Server Action/service wiring without provider I/O or persistence.
- [x] Retain malformed/invalid local Agent-contract text while showing actionable field-local diagnostics.
- [x] Add `Validate agent contract` UI/status and stale-success invalidation.
- [x] Clarify Agent-contract labels/help text without redesigning the tab.
- [x] Preserve new-Tool and persisted-DRAFT parity through the existing `AgentContractTab` component.
- [x] Add focused regression tests for validation, local-state retention, staleness and zero-persistence behaviour.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-016
canonical Commerce Tool-definition, input-schema and response-template contracts

ARCH-021-COMMERCE-039
non-durable new-Tool authoring until final Create

ARCH-021-COMMERCE-043
current processed-result/result-schema contract used by Visual Response authoring
```

Reuse the canonical publication/template compatibility semantics in:

```text
src/commerce/tool-definition/publication.ts
```

where applicable. Do not duplicate template path interpretation in Studio UI code.

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-039
- ARCH-021-COMMERCE-043

## Enables

None.

## Acceptance Criteria

- [x] `AgentContractTab` remains the single bounded React component for the Agent-contract form.
- [x] The tab offers a clear `Validate agent contract` action.
- [x] Validation does not require Request/Test/Review completion and performs no provider/network/credential work.
- [x] Definition version and description failures are shown at deterministic Agent-contract paths.
- [x] Input-schema validation uses the canonical bounded input-schema contract and rejects forbidden authority/credential inputs.
- [x] Response-template validation uses the canonical template contract and validates paths against the current processed-result/output contract.
- [x] Malformed/temporarily invalid JSON/text remains visible locally for correction instead of silently reverting.
- [x] New-Tool Agent-contract validation writes no Tool, ToolRevision, audit, receipt or publication-proof state.
- [x] Persisted-DRAFT Agent-contract validation does not save the DRAFT.
- [x] Validation success is invalidated by any relevant Agent-contract/result-contract edit.
- [x] Labels/help text clearly explain Definition version, Agent description, Agent input schema and Agent response template.
- [x] New local Tool and persisted-DRAFT flows use the same Agent-contract validation semantics where the shared tab is used.
- [x] Other tabs remain freely navigable; no Phase 2 gating is introduced.
- [x] Final Create/Save/Publish validation remains authoritative and is not weakened or bypassed.

## Validation

- [x] focused Agent-contract domain/Server Action tests
- [x] focused `AgentContractTab` / new-Tool authoring UI tests
- [x] persisted-DRAFT Agent-contract UI regression tests
- [x] input-schema authority/credential rejection tests
- [x] response-template result-path compatibility tests
- [x] explicit proof that validation performs no provider I/O and no durable Tool/ToolRevision/audit writes
- [x] relevant common Tool-authoring regression packet declared by the repository
- [x] targeted TypeScript diagnostics or repository typecheck with baseline reconciliation
- [x] targeted ESLint for changed files
- [x] `git diff --check`

## Stop Condition

After Agent-contract validation, local-state retention, terminology/help text and required regressions are complete, set this task to `review`, complete the Completion Report and STOP. Do not begin Review-tab redesign, Test implementation, publication-proof work or Phase 2 tab gating.

## Implementation Notes

The current form is already extracted into `src/studio/tools/authoring/agent-contract-tab.tsx`; preserve that component boundary.

Prefer extracting/reusing canonical Agent-contract validation helpers from Tool-definition/publication code over validating a complete Tool merely to obtain Agent-contract errors. The purpose of this task is to let the tab validate its own concerns independently.

For External HTTP, remember that agent response templates see the Commerce Tool output contract (including the existing `values` wrapper used by execution/publication semantics), not the raw provider response.

Do not treat successful Agent-contract validation as a live-Test receipt or publication authorization.

## Completion Report

### Status
Ready for Architect Review

### Files Changed
- `src/commerce/tool-authoring/agent-contract-validation.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/studio/tools/agent-contract-validation-server-actions.ts`
- `src/studio/tools/authoring/agent-contract-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/agent-contract-validation.test.ts`
- `tests/agent-contract-validation-server-actions.test.ts`
- `tests/external-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed
- Added a pure, named Agent-contract validator reusing canonical SemVer, description, bounded input-schema, forbidden-authority-input and response-template schemas. Publication and Agent validation now share output-path compatibility rules and the External HTTP `values` wrapper.
- Added an ADMIN-authorized Server Action that validates only Agent fields plus the current output contract. It does not access the Commerce backend, provider, credentials, Request builders, or persistence services.
- Kept `AgentContractTab` as the single form component, added Agent-facing labels/help and field-local diagnostics, and retained raw JSON text. Validation state is keyed to the complete current Agent/output candidate and stays mounted across tab navigation.
- Wired New Tool Shopify Admin and External HTTP candidates and persisted External HTTP DRAFT candidates through the same action. External output uses the canonical `values` wrapper; Admin uses its direct result schema.
- Added domain, action, New Tool and persisted-DRAFT tests for malformed JSON, forbidden inputs, template paths/list compatibility, local-state retention, stale success, output-context parity and no-write/no-provider behavior.

### Validation Results
- Launcher preparation passed for Attempt 1: all three declared dependencies passed; dedicated mirrored task worktrees and the pinned Commerce submodule were established. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-056`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-056`.
- Passed: `./node_modules/.bin/vitest run tests/agent-contract-validation.test.ts tests/agent-contract-validation-server-actions.test.ts tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx` (4 files, 92 tests).
- Passed: targeted ESLint for all 11 changed source/test files; `git diff --check`; Pylance diagnostics on changed files (none).
- Passed focused shared publication checks: Agent-contract and `external-publication` tests (18 tests).
- Attempt 2 prepared and claimed by the launcher: all three dependencies passed; attempt 2 claim commit `cbf17e6a6780eff943a9720b76e13b358aec93c8` was committed and pushed. The launcher reports both task worktrees reused, no other task worktree reused, and no canonical/shared checkout switched or mutated for task work.
- Attempt 2 physical worktree isolation: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-056` on `task/ARCH-021-COMMERCE-056`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-056` on `task/ARCH-021-COMMERCE-056`; shared workspace checkout switched/mutated: no; shared implementation checkout switched/mutated: no; another task worktree reused: no.
- Attempt 2 start-of-attempt synchronization from the launcher packet: parent remote task branch fast-forwarded `not-needed`; parent `origin/main` incorporated `already-current`; implementation remote task branch fast-forwarded `not-needed`; implementation `origin/main` incorporated `already-current`.
- Recursive implementation submodules were ready; `database` was initialized at pinned commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`. No database submodule gitlink was staged.
- After C055 `origin/main` presented two test-fixture merge conflicts, both were resolved by retaining the C056 Agent-validation mock/reset and C055 live-Test mock/reset. The required post-merge C056 focused packet passed: `./node_modules/.bin/vitest run tests/agent-contract-validation.test.ts tests/agent-contract-validation-server-actions.test.ts tests/tool-authoring-screen.test.tsx tests/external-tools-ui.test.tsx` (4 files, 99 tests). Targeted ESLint for the two resolved test files and `git diff --check` passed.
- Common packet `pnpm run test:arch021-tool-authoring-common`: 85/86 passed. Existing `commerce-lifecycle.test.ts` fixture uses an empty External result schema and receives `INVALID_DEFINITION` before its expected `LIVE_TEST_REQUIRED` gate.
- `pnpm run typecheck`: failed with 12 existing diagnostics in six unrelated files (`app/api/studio/code-response/validate/route.ts`, `lib/discovery/compiler.ts`, `scripts/validate-shopify-admin-local.ts`, `src/commerce/integration/studio/services.ts`, `tests/agent-configuration-effective.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`). No diagnostics were reported for changed files.
- Additional `shopify-admin-tools-ui.test.tsx`: 13/15 passed; two existing assertions expect `Valid Admin GraphQL query.` from the persisted Admin editor, which does not render that status and does not use `AgentContractTab`. New Tool Shopify Admin Agent validation is covered and passes in `tool-authoring-screen.test.tsx`.
- Implementation repository `moda-interact-commerce`: C056 implementation commit `b7cbd97` is pushed to `origin/task/ARCH-021-COMMERCE-056`; Attempt 2 current-main integration commit `266bd94` is also pushed to that branch. The task branch was not merged to implementation `main`.
- Parent workspace task file `docs/decisions/commerce/ARCH-021/COMMERCE-056-validate-agent-contract-authoring.md`: initial completion-report commit `bbfa8ef7` and Attempt 2 claim commit `cbf17e6a` are pushed on `origin/task/ARCH-021-COMMERCE-056`; this A1-R1 report correction is being submitted on the same branch. The parent task branch was not merged to workspace `main`.

### Deviations
None. Final Create/Save/Publish validation and lifecycle boundaries remain unchanged.

### Assumptions
- External HTTP response-template paths are evaluated against the processed Commerce output, including its `values` wrapper. Shopify Admin paths use the current authored result schema directly.
- The existing persisted-DRAFT surface using the shared Agent tab is External HTTP; the standalone persisted Shopify Admin editor remains outside that component boundary.

### Unresolved Issues
- The common packet and full repository typecheck retain the unrelated baseline failures listed above. The persisted Admin UI packet also retains two assertions for a status that this non-Agent surface does not render.
- None related to A1-R1; the Attempt 2 report correction records the launcher-provided isolation/synchronization values and the rerun validation evidence.

### Architectural Concerns
None

## Architect Review

### Review Status
Changes Requested

### Review Notes

Attempt 1 implementation is otherwise architecturally conformant and does not require implementation-source churn.

The named Agent-contract validator is non-mutating and validates only the Agent-facing definition fields plus the current processed-result/output contract. SemVer, bounded input-schema, forbidden authority/credential inputs and response-template schema/path semantics are reused from the canonical Tool-definition/publication boundary; publication and in-tab validation share `responseTemplateCompatibilityIssues(...)`. External HTTP uses the same canonical `values` output wrapper as publication. The ADMIN-authorized Server Action does not resolve Commerce backend/provider/credential state or perform persistence.

`AgentContractTab` remains the single bounded form component. Raw malformed JSON remains in local authoring buffers, validation success is keyed to the complete current Agent/output candidate and therefore becomes stale on relevant edits, persisted-DRAFT validation operates on the unsaved candidate without Save, and no Phase 2 navigation gating is introduced.

The submitted focused validation evidence is acceptable for the task-owned implementation: 92/92 focused tests passed, targeted ESLint and `git diff --check` passed, focused publication checks passed, and changed-file diagnostics are reported clean. The common 85/86 lifecycle fixture mismatch and repository-wide typecheck diagnostics are documented outside the C056 changed files.

#### A1-R1 — reconcile mandatory VCS/worktree evidence in the Completion Report

The Completion Report does not yet contain the complete durable evidence required by `docs/agent-worktree-isolation-policy.md` and `docs/agent-vcs-ownership-policy.md`.

It currently states generally that launcher preparation established dedicated worktrees and the pinned Commerce submodule, but the report must record the concrete physical-isolation and start-of-attempt synchronization fields, together with both published branch/commit records.

For Attempt 2, recover the existing launcher/preparation packet and record the actual values; do not invent them:

```text
Physical worktree isolation:
  canonical workspace root: <launcher-resolved path>
  parent worktree: <launcher-resolved path>
  parent branch: task/ARCH-021-COMMERCE-056
  implementation worktree: <launcher-resolved path>
  implementation branch: task/ARCH-021-COMMERCE-056
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation repository:
  repository: moda-interact-commerce
  commit: b7cbd97
  remote branch: origin/task/ARCH-021-COMMERCE-056
  pushed: yes

Parent workspace:
  task file: docs/decisions/commerce/ARCH-021/COMMERCE-056-validate-agent-contract-authoring.md
  commit: bbfa8ef7
  remote branch: origin/task/ARCH-021-COMMERCE-056
  pushed: yes
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no
```

Retain the recursive/pinned `database` submodule evidence from the launcher packet.

This is a workflow-evidence/report correction only. No implementation source or test change is required unless validation rerun from the canonical task worktrees exposes a task-owned regression.

### Reviewed Files

- `src/commerce/tool-authoring/agent-contract-validation.ts`
- `src/commerce/tool-definition/contracts.ts`
- `src/commerce/tool-definition/publication.ts`
- `src/studio/tools/agent-contract-validation-server-actions.ts`
- `src/studio/tools/authoring/agent-contract-tab.tsx`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/agent-contract-validation.test.ts`
- `tests/agent-contract-validation-server-actions.test.ts`
- `tests/tool-authoring-screen.test.tsx`
- `tests/external-tools-ui.test.tsx`
- `docs/agent-worktree-isolation-policy.md`
- `docs/agent-vcs-ownership-policy.md`
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Focused Agent-contract/UI packet: 92/92 passed.
- Focused shared publication checks: 18/18 passed.
- Targeted ESLint: passed.
- Changed-file diagnostics: no C056-owned diagnostics reported.
- `git diff --check`: passed.
- Common Tool-authoring packet: 85/86 with the documented unrelated lifecycle fixture mismatch.
- Repository `pnpm run typecheck`: 12 documented diagnostics in six files outside the C056 changed-file set.
- Additional Shopify Admin UI packet: 13/15 with two documented pre-existing assertions on the separate persisted Admin surface.

### Architecture Conformance

Conforms at the implementation level.

C056 preserves the existing Agent-contract component boundary, introduces one named non-mutating validation boundary, reuses canonical Tool-definition/publication semantics, retains invalid local authoring text, validates the current processed-result contract, performs no provider I/O or durable writes, preserves new-Tool/persisted-DRAFT parity where the shared tab is used, and introduces no navigation gating.

Acceptance is withheld only because the durable Completion Report is missing the mandatory full VCS/worktree synchronization evidence.

### Follow-up

Return the same task through `/moda-task` for Attempt 2. Reconcile the Completion Report with the existing launcher/preparation evidence, rerun only the task-required validation necessary to substantiate that canonical-worktree record, return the task to `review`, clear the active claim, and STOP. No implementation-source change is required unless that validation reveals a C056-owned regression.
