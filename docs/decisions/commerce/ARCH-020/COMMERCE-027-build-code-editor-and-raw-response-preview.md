---
id: ARCH-020-COMMERCE-027
architecture_id: ARCH-020
title: Build code editor and raw-response preview
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: copilot
claimed_at: 2026-09-22T01:01:12Z
attempt: 1
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-017
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Build code editor and raw-response preview

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Frontend only: src/studio/code-response/** exports CodeResponsePanel and RawResponseSamplePanel for023 slots. Implement exact C21 section6 controls and XN04 against injected ports. No host-page/sidebar changes, engine or live fetch.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Frontend only: src/studio/code-response/** exports CodeResponsePanel and RawResponseSamplePanel for023 slots. Implement exact C21 section6 controls and XN04 against injected ports. No host-page/sidebar changes, engine or live fetch.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [ ] Provide locally bundled editor, source/version docs, format-aware raw sample and processed JSON/template panels. HTML/XML stay escaped text; no innerHTML/eval or external editor CDN.
- [ ] Implement typed compile/test/cancel/read ports from section2.3, content-hash stale checks, save-before-run, duplicate guards, error retention and unknown-run reconciliation.
- [ ] Show schema diagnostics with JSON Pointer, expected type and bounded safe message; no provider source/secret echoed in generic error. Existing successful result is stale after edits.
- [ ] Include illustrative plain-text, JSON, HTML, XML and simple CSV extraction examples; explain no DOM/imports/full parser libraries. Published code read-only; source diff on new draft.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-017

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [ ] X12/XN04: Text ->Code->sample->compile->save->run->schema failure->correct->save/run->return/publish handoff; same flow works for JSON.
- [ ] No browser execution or active HTML, role/pending/cooldown/abort states accessible on keyboard/narrow layout; late results cannot validate changed code.
- [ ] Both panels build/test independently of023/026 using agreed fixtures;024 owns actual host installation and engine calls.

## Validation

Provide `test:arch020-code-editor` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Review-ready, Attempt 1 implementation submitted to `moda_architect`.

### Files Changed

- `moda-interact-commerce/src/studio/code-response/contracts.ts`
- `moda-interact-commerce/src/studio/code-response/code-response-panel.tsx`
- `moda-interact-commerce/src/studio/code-response/raw-response-sample-panel.tsx`
- `moda-interact-commerce/src/studio/code-response/index.ts`
- `moda-interact-commerce/tests/code-editor.test.tsx`
- `moda-interact-commerce/package.json`

### Work Completed

Added independently mountable `CodeResponsePanel` and
`RawResponseSamplePanel` with typed injected ports. The code panel provides
locally bundled source editing with line numbers, runtime/API guidance, five
bounded examples, validation diagnostics, save-before-run, duplicate guards,
cancel and unknown-run reconciliation, stale-result invalidation, draft restore,
read-only published mode and publish handoff. The raw-response panel captures
bounded status/content type/JSON-or-text/body input and displays processed JSON
and rendered text without HTML injection or browser execution. HTML/XML/CSV
examples remain escaped text and the UI explains that parsing is string-only.

The ports preserve the C21 content hash, preview run identity and sample fixture
contract; the panels do not perform network calls, evaluate source, or expose
credentials. Host route installation and real sandbox calls remain owned by
COMMERCE-024.

### Validation Results

- `npm run test:arch020-code-editor`: passed, 1 file and 4 tests.
- `npx eslint src/studio/code-response tests/code-editor.test.tsx`: passed.
- `npm run lint`: passed.
- `git diff --check`: passed.
- `npm run typecheck`: not clean because of existing unrelated errors in
  `src/commerce/integration/backend/executors.ts` and
  `tests/code-response-processor.test.ts`; no COMMERCE-027 source or test
  diagnostics were reported.
- `npm run build`: application compilation and QuickJS packaging/smoke passed,
  then Next type checking failed on the same 3 unrelated baseline errors.
- No live provider, sandbox, database, or assembled host-flow validation was
  claimed; those checks belong to COMMERCE-024/SYSTEM-TEST-002.

### Deviations

The panels use the accepted C21/Shared `0.14.2` contract shapes locally and
receive server-owned behavior through injected ports. The launcher dependency
gate passed for SHARED-002, COMMERCE-008 and COMMERCE-017; their physical
accepted SHAs were not included in the launcher packet and were not guessed.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No known implementation blocker. COMMERCE-024 must install the exported panels
into U06/U14 and connect accepted compile/sample services before assembled-flow
acceptance.

### Architectural Concerns

No contract contradiction found. The repository-wide typecheck/build baseline
remains separately blocked by the 3 errors listed above.

### Git / VCS

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-027`
  parent branch: `task/ARCH-020-COMMERCE-027`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-027`
  implementation branch: `task/ARCH-020-COMMERCE-027`
  shared workspace checkout switched/mutated: no
  another task worktree reused: no

Start synchronization from launcher: parent and implementation branches were
already current; no remote fast-forward or main incorporation was needed.
Recursive implementation submodules: sync passed, update/init passed,
database at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.
Implementation commits: `221c913`, `771c1ff`, pushed to the task branch.
Parent report claim commit: `fa865434fa888bf7bb33c241bc04dabd2158c042`;
this report update is the next mirrored parent commit.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
