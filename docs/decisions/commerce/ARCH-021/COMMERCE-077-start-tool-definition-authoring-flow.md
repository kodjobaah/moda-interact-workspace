---
id: ARCH-021-COMMERCE-077
architecture_id: ARCH-021
title: Start Tool creation with a first-class Tool Definition step
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 72
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-039
  - ARCH-021-COMMERCE-064
enables:
  - ARCH-021-COMMERCE-078
created: 2026-09-28
updated: 2026-09-28
---

# Start Tool creation with a first-class Tool Definition step

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the inline New Tool form on the Tool library with a single **Create Tool** launcher and introduce a browser-local Tool Definition authoring step that can exist before a schema-valid `CommerceToolDraftDefinition` exists.

## Context

The current `ToolLibrary` renders the Tool list and a second `New tool` form. That form owns MCP name/display name/description/provider selection, eagerly loads Shopify Admin metadata and immediately constructs a draft definition before `NewToolEditor` can open. `ToolAuthoringScreen.LocalSession` therefore requires a complete `CommerceToolDraftDefinition`, and `NewToolEditor` starts on Request.

The agreed product flow instead starts authoring only after the operator presses **Create Tool** and makes **Tool Definition** the first authoring surface. No Tool/ToolRevision may be created by entering or editing this step; the existing COMMERCE-039 final-write invariant remains authoritative.

## Scope

Primary implementation areas:

```text
src/studio/tools/tool-library.tsx
src/studio/tools/tool-authoring-screen.tsx
src/studio/tools/new-tool-editor.tsx
src/studio/tools/authoring/tool-authoring-tabs.tsx
src/studio/tools/authoring/tool-definition-tab.tsx       # new
src/studio/tools/new-tool-authoring-state.ts              # new pure local-state helper, or exact equivalent
```

Focused regressions belong primarily in:

```text
tests/tool-authoring-screen.test.tsx
tests/external-tools-ui.test.tsx
tests/shopify-admin-tools-ui.test.tsx
```

No database, Shared, Gateway, Background or deployment file is in scope.

## Out of Scope

- Reordering Result Template/Test/Review beyond inserting Tool Definition first; COMMERCE-078 owns the final six-step composition.
- Agent Contract removal; COMMERCE-078 owns that change.
- External or Shopify live-Test execution.
- Persisted-DRAFT parity; COMMERCE-079 owns it.
- Publication proof or publication-gate changes.
- Database/schema changes.
- Creating a durable Tool when **Create Tool** on the library is pressed.

## Requirements

### R1 — the Tool library is a launcher, not an authoring form

`ToolLibrary` must no longer render or own these inputs/state:

```text
Immutable MCP name
Display name
Description
Tool purpose/provider
Shopify Admin metadata
provider draft builders
```

The Tool page must expose one button labelled exactly:

```text
Create Tool
```

Pressing it starts a local authoring session and shows `NewToolEditor`; it must perform **zero** Server Action mutation, Tool write, ToolRevision write, audit write or operation-receipt write.

### R2 — local state must represent an incomplete Tool Definition

Introduce one explicit local state model equivalent to:

```ts
type NewToolKind = "SHOPIFY_ADMIN_GRAPHQL" | "EXTERNAL_HTTP";

type NewToolDefinitionState = {
  name: string;
  displayName: string;
  description: string;
  definitionVersion: string;
  kind: NewToolKind | null;
};

type NewToolAuthoringState = {
  tool: NewToolDefinitionState;
  proposedDefinition: CommerceToolDraftDefinition | null;
};
```

The exact type name may differ, but these semantics may not: a new session starts with blank `name`, `displayName`, `description`, `definitionVersion: "1.0.0"`, `kind: null`, and no provider definition. Do **not** weaken `CommerceToolDraftDefinitionSchema` merely to represent blank UI state.

### R3 — Tool Definition is the first tab and owns identity/provider choice

Add `tool-definition` as the first authoring tab. Its visible controls are exactly:

```text
Immutable MCP name
Display name
Description
Definition version
Tool type
```

Tool type initially has an unselected placeholder and these values only:

```text
SHOPIFY_ADMIN_GRAPHQL -> Shopify Admin GraphQL
EXTERNAL_HTTP         -> External HTTP/API
```

Validation must use the existing canonical limits:

```text
MCP name: ToolNameSchema
Display name: trim, 1..255 characters
Description: 0..4000 characters for create-command compatibility;
             Review/Save remains disabled while blank because definition.description requires non-empty
Definition version: SemverSchema
```

The one Tool Definition `description` is authoritative for both the create command's Tool metadata description and `proposedDefinition.description`. Do not keep a second editable "Agent description" for a new Tool.

### R4 — provider selection initializes only local provider defaults

When `kind` becomes `SHOPIFY_ADMIN_GRAPHQL`, load Admin authoring metadata at that time (not when `/tools` first renders) and initialize the same local defaults the current Tool-library builder uses:

```text
executorVersion: 1.0.0
apiVersion/schemaHash: server-authoritative Admin authoring metadata
document: query NewTool { shop { name } }
operationName: NewTool
variables: {}
resultPath: shop
resultSchema: object{name:string}
inputSchema: empty object schema
responseTemplate: text {{result.name}}
```

When `kind` becomes `EXTERNAL_HTTP`, initialize the current local defaults:

```text
executorVersion: 1.0.0
connectionRevisionId: first authorized listed revision id, or "" when none exists
method: GET
request: DECLARATIVE /
responseFormat: JSON [application/json]
resultPath: ""
responseProcessing: DIRECT
resultSchema: object{value:string}
inputSchema: empty object schema
responseTemplate: text {{result.values.value}}
```

An absent External connection must not create a Tool and must not silently substitute a fake connection. Request may show the existing unavailable/no-selection state until an authorized revision is selected.

### R5 — changing provider type is an explicit destructive reset

If no provider is selected, selecting one initializes its defaults immediately.

If a provider is already selected and the user chooses the other provider, do not silently reinterpret the existing Request/Response/Template state. Keep the current type until the user explicitly confirms a visible reset action whose text states that Request, Response, Result Template and Test state will be cleared. On confirmation, replace the provider draft with the new provider defaults and clear provider-derived validation/Test state. On cancel, leave all existing state byte-for-byte unchanged.

### R6 — no regression to Explore/session and final persistence boundaries

The Shopify Request -> Explore -> Use in tool -> Request round trip must continue to work once a valid Shopify candidate exists. The existing versioned `sessionStorage` handoff remains the only browser persistence used for that navigation.

The final durable operation remains `createToolWithInitialDraft`; this task must not call it from Tool Definition or the Tool-library launcher.

## Work Items

- [x] Remove the inline New Tool form and all provider-bootstrap state/effects from `ToolLibrary`.
- [x] Add the single `Create Tool` launcher.
- [x] Add the incomplete local new-Tool authoring-state model without weakening durable/draft schemas.
- [x] Add the Tool Definition tab/component and make it the initial tab.
- [x] Move Shopify Admin metadata bootstrap from ToolLibrary into provider selection in the local authoring flow.
- [x] Move External default-draft bootstrap into provider selection in the local authoring flow.
- [x] Make Tool Definition description feed both Tool metadata creation input and definition description.
- [x] Implement explicit provider-switch reset confirmation.
- [x] Preserve Shopify Explore session handoff after Shopify initialization.
- [x] Add zero-write and provider-switch regression coverage.

## Interfaces / Contracts

Consumes:

```text
CommerceToolDraftDefinitionSchema              existing local-draft boundary
ToolNameSchema / SemverSchema                  canonical identity validation
getShopifyAdminAuthoringMetadataAction         server-authoritative Admin identity
createToolWithInitialDraft                     final write boundary; MUST NOT be called by this task's launcher/definition edits
ARCH-021-COMMERCE-039                          local-until-final-create invariant
ARCH-021-COMMERCE-064                          Explore Shopify sessionStorage handoff
```

No new cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-039
- ARCH-021-COMMERCE-064

## Enables

- ARCH-021-COMMERCE-078

## Acceptance Criteria

- [x] `/tools` renders the Tool library plus one `Create Tool` launcher and no inline Tool-definition form.
- [x] Pressing `Create Tool` opens a local authoring session on `Tool Definition` with blank identity fields, SemVer `1.0.0`, and no provider selected.
- [x] Starting/editing Tool Definition performs zero durable writes.
- [x] Tool Definition exposes only the five specified controls and validates them against canonical limits.
- [x] New Tool description has one authoritative editable value used by both Tool metadata creation and definition description.
- [x] Selecting Shopify initializes the current Admin defaults only after authoritative metadata is available.
- [x] Selecting External initializes the current External defaults without inventing a connection.
- [x] Switching provider kind requires explicit destructive-reset confirmation and never silently preserves incompatible provider state.
- [x] Shopify Explore round-trip still restores the same new authoring session after Shopify initialization.
- [x] Final Tool persistence is still absent from this task.

## Validation

- [x] `npx vitest run tests/tool-authoring-screen.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/external-tools-ui.test.tsx`
- [x] focused zero-provider/write assertions proving Tool-library launch and Tool Definition edits do not call mutation actions
- [x] targeted ESLint for changed files
- [x] changed-file TypeScript diagnostics, or repository typecheck with baseline reconciliation
- [x] `git diff --check`

## Stop Condition

After every defined Work Item, Acceptance Criterion and required Validation item is complete, set the task to `review`, complete the Completion Report and STOP. Do not begin an enabled or adjacent task.

## Implementation Notes

Do not make `CommerceToolDraftDefinitionSchema` accept empty names/descriptions/provider placeholders. The browser needs a separate incomplete authoring-state type precisely because the durable/draft schema describes a definition that is far enough along to validate as a Tool draft.

The task may factor provider-default builders into pure functions so UI tests can prove exact initialization and destructive-reset behaviour without mounting provider/network code.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

- `src/studio/tools/tool-library.tsx`, `src/studio/tools/tool-authoring-screen.tsx`, and `src/studio/tools/new-tool-editor.tsx`.
- `src/studio/tools/new-tool-authoring-state.ts` and `src/studio/tools/authoring/tool-definition-tab.tsx`, with the shared authoring tabs and Agent Contract presentation updated for new Tools.
- Focused tests in `tests/tool-authoring-screen.test.tsx`, `tests/shopify-admin-tools-ui.test.tsx`, `tests/external-tools-ui.test.tsx`, `tests/new-tool-authoring-state.test.ts`, and `tests/admin-explorer.test.tsx`.

### Work Completed

- Replaced the ToolLibrary identity/provider form with one `Create Tool` launcher and a separate incomplete, browser-local authoring state. Durable/draft schemas remain unchanged.
- Added the first Tool Definition step with canonical name, trimmed display-name, SemVer, and description limits. The single description feeds both Tool metadata and the proposed definition; Review cannot open while it is blank.
- Moved Shopify metadata loading and External defaults into provider selection. Shopify uses the server metadata; External uses the first authorized listed revision or remains unavailable without inventing a connection.
- Added explicit provider-reset confirmation. Cancel retains the active provider state; confirmation remounts provider editors and prevents restored buffers from the previous provider from rehydrating.
- Preserved the versioned Shopify Explore sessionStorage round trip and kept the sole durable create operation at Review via `createToolWithInitialDraft`.
- Added launcher/definition zero-write, defaults, validation, provider-reset, missing-connection, metadata-timing, and Explore regressions.
- Implementation commit `31b1a2a2593be815877b180ae39f3bdec79c5c5e` was pushed to `task/ARCH-021-COMMERCE-077`. Local and remote task refs match; no main branch was changed.

### Validation Results

- Focused command `npx vitest run tests/tool-authoring-screen.test.tsx tests/shopify-admin-tools-ui.test.tsx tests/external-tools-ui.test.tsx tests/new-tool-authoring-state.test.ts tests/admin-explorer.test.tsx` passed: 5 files, 134 tests.
- Targeted ESLint across all changed source and test files passed with no warnings or errors.
- `npm run typecheck` exits 2 with 262 repository-wide TypeScript diagnostics. No diagnostics remain in the C077 implementation or changed test files, including the migrated `tests/admin-explorer.test.tsx` consumer.
- `git diff --check` passed. The implementation worktree was clean after commit; the `database` submodule remained at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- The implementation branch was pushed; `HEAD` and `origin/task/ARCH-021-COMMERCE-077` both resolve to `31b1a2a2593be815877b180ae39f3bdec79c5c5e`.

### Deviations

- The prepared implementation worktree had no installed dependencies, so `npm ci` was run from its existing lockfile. It completed without project-file changes and reported engine/peer/deprecation warnings and 9 high npm audit findings.
- The repository typecheck remains nonzero because of 262 diagnostics outside the changed C077 files; all changed-file diagnostics were resolved.

### Assumptions

- The existing `createToolWithInitialDraft` command remains the authoritative single durable creation boundary; this task changes its local authoring inputs, not its persistence contract.
- Shopify API version and schema hash continue to come from `getShopifyAdminAuthoringMetadataAction`; External revisions are taken only from the authorized catalogue.

### Unresolved Issues

- Repository-wide typecheck still reports 262 TypeScript diagnostics outside C077-changed files. No changed-file diagnostics remain.

### Architectural Concerns

None.

### Physical Worktree Isolation and Synchronization

Recorded from the deterministic launcher preparation packet. The canonical paths and prepared commit values below are launcher evidence; implementation publication was verified after the commit.

```text
Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-077
  parent branch: task/ARCH-021-COMMERCE-077
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-077
  implementation branch: task/ARCH-021-COMMERCE-077
  shared workspace checkout switched/mutated for task work: no
  shared implementation source checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization (launcher packet):
  parent worktree reused: yes
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  parent prepared head: 09449250adcee6274629307c97bae8d602a11b0c
  implementation worktree created: yes
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current
  implementation prepared head: efcc1f6abec0e1c5ce39275c5e15c951c0ca470a
  parent claim commit: f2d402163c2b43bc16075db533fa45c653a0c5fa (pushed)

Recursive implementation submodule:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recursive status: ready
  database commit: 0a8d3b9feade69690b6c1e33aeda051ea588bd45

Published task state:
  implementation commit: 31b1a2a2593be815877b180ae39f3bdec79c5c5e
  implementation remote: origin/task/ARCH-021-COMMERCE-077
  implementation pushed: yes; local and remote task refs match
  parent claim/report branch: task/ARCH-021-COMMERCE-077
  parent claim is pushed; completion report is committed and will be pushed on this branch
  merged to implementation main: no
  merged to workspace main: no
```

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

Pending

### Follow-up

None
