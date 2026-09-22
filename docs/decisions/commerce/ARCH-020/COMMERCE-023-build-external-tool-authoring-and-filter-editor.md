---
id: ARCH-020-COMMERCE-023
architecture_id: ARCH-020
title: Build external tool authoring and response-filter editor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 155
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-017
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-21
---

# Build external tool authoring and response-filter editor

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Frontend only: src/studio/external-http/**, U06 external execution/response-processing steps and U14 synthetic fixture controls. Own mode selector and typed code-panel slot, not027 code editor. No U15/U16/sidebar, provider HTTP, credential or shared-factory edits.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Frontend only: src/studio/external-http/**, U06 external execution/response-processing steps and U14 synthetic fixture controls. Own mode selector and typed code-panel slot, not027 code editor. No U15/U16/sidebar, provider HTTP, credential or shared-factory edits.

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

- [ ] Implement exact U06 connection/revision/GET/query/schema controls and Process response visual editor + Advanced configuration for the same section2.1 schema.
- [ ] Display supplied connection documentation in Studio; source/processed sample side by side, counts and field errors. Use injected processor port fixtures; never execute source in browser;027 supplies code panel. Do not infer a trusted schema from a sample.
- [ ] Implement U06->U16 return-context contract, saved revision U14 test/return, stale validation invalidation and source hash checks. No secret fields; no live call/decryption in Fixture or Model preview.
- [ ] Preserve existing publication/release flow and exact tool binding/version selection. Demonstrate owned XN02 sections through injected connection/processor/service ports.

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

- [x] X06: full authoring of C21 sample and list-filter example, including field rename/filter/sort/limit, produces exact stored execution JSON.
- [x] No lost edits on save/discard/return, duplicate Test/Publish guarded, modified response invalidates old validation; keyboard/narrow controls usable.
- [x] U14 external tests show processed fixtures and existing reply template with zero network calls; no U15 backend dependency for component acceptance.

## Validation

Provide `test:arch020-external-tools-ui` in the owning repository and document its exact scope.
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

Implemented in isolated worktree; pending architect review.

### Files Changed

`moda-interact-commerce/components/studio-workspace.tsx`,
`moda-interact-commerce/src/studio/external-http/editor.tsx`,
`moda-interact-commerce/src/studio/external-http/ports.ts`,
`moda-interact-commerce/src/studio/external-http/processor.ts`,
`moda-interact-commerce/tests/external-tools-ui.test.tsx`, and
`moda-interact-commerce/package.json`.

### Work Completed

Added the U06 external read-only editor for exact connection revision, fixed GET
path, scalar query mappings, response format/media types, visual OBJECT/LIST
processing, field rename/projection, filter, sort, limit, Advanced processing
JSON, response shape JSON, supplied documentation, and synthetic source/processed
sample panels. The editor uses an injected typed fixture port and never performs
live requests or browser code execution; JavaScript is represented as the typed
027-owned slot. Existing ToolEditor save/CAS, dirty navigation, and publication
flow remain in control. Added fixture processing coverage for X06/U14 with zero
`fetch` calls.

### Validation Results

`npm run test:arch020-external-tools-ui` passed 4 tests; neighboring
`npx vitest run tests/studio-workspace.test.tsx` passed 18 tests. Changed-file
diagnostics are clean and `git diff --check` passed. The external-tools files
are lint-clean. Full `npm run lint` remains blocked by a pre-existing
`react-hooks/set-state-in-effect` error in `src/studio/connections/connections-ui.tsx`
plus baseline warnings outside this task. Full typecheck/build were not run;
existing repository typecheck has unrelated database/publication diagnostics.

### Deviations

Definition authored on main under the user's existing instruction.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No implementation reported. Explicit dependencies gate execution.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Dedicated worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-023`.
Branch: `task/ARCH-020-COMMERCE-023`. Commit and push are being prepared; no
merge, service gitlink update, or downstream launch performed.

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
