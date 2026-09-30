---
id: ARCH-021-COMMERCE-064
architecture_id: ARCH-021
title: Rebuild Explore Shopify for Admin GraphQL authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 74
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-039
  - ARCH-021-COMMERCE-061
enables:
  - ARCH-021-COMMERCE-065
  - ARCH-021-COMMERCE-069
created: 2026-09-27
updated: 2026-09-27
---

# Rebuild Explore Shopify for Admin GraphQL authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the current Storefront-oriented Explore Shopify product surface with a Shopify Admin `2026-07` explorer/query builder and implement the complete Request -> Explore -> Use in tool -> Request authoring handoff for both unsaved new Tools and existing Tool drafts using `StudioComposerContext` plus versioned `sessionStorage` authoring sessions.

## Context

The current Explore screen consumes Storefront discovery and requires `composer.tool` to contain an already-persisted `toolId`/`toolRevisionId`. That prevents the new local-only Tool creation flow from using Explore before a Tool exists.

The agreed design is:

```text
Request tab
  -> persist browser-session ToolAuthoringSession
  -> Explore Shopify (Admin API)
  -> build/validate Admin GraphQL
  -> Use in tool updates that same authoring session
  -> return to originating Request tab
```

This specific round trip is part of the Explore feature. General tab traversal/gating remains deferred.

## Scope

Expected implementation areas include:

```text
components/studio-composer-context.tsx
components/studio-workspace.tsx
src/studio/discovery/                         # Admin React surfaces
src/studio/tools/new-tool-editor.tsx
src/studio/tools/tool-editor.tsx              # existing draft handoff where applicable
app/explore/page.tsx / related route plumbing only as needed
app/styles.css

tests/studio-workspace.test.tsx
tests/tool-authoring-screen.test.tsx
tests/shopify-admin-tools-ui.test.tsx
new focused authoring-session/Explore tests
```

## Out of Scope

- General Request/Response/Test/Agent/Review tab traversal rules.
- Tab gating or automatic Next/Previous flow.
- Shopify Response/result-schema UI; COMMERCE-065 owns it.
- ToolResultContract or Result Template UI.
- Database persistence of unfinished new Tool drafts.
- `localStorage` persistence.
- Storefront code deletion; COMMERCE-069 owns cleanup after migration.
- Provider execution.

## Requirements

### R1 — Explore Shopify means Admin API

The product surface must browse/build only against the pinned Shopify Admin `2026-07` query schema supplied by COMMERCE-061.

Use user-facing wording equivalent to:

```text
Explore Shopify
Shopify Admin API · 2026-07
```

Do not offer Storefront as an alternate mode in this flow.

### R2 — manual GraphQL remains authoritative

Explore is an authoring convenience for `SHOPIFY_ADMIN_GRAPHQL.execution.document`.

A user may continue to type/edit GraphQL manually in the Request tab before or after using Explore. Do not persist a `generatedByExplore` flag or separate query entity required by runtime.

### R3 — versioned browser-session authoring identity

Extend the existing Studio composer model with a transient `authoringSessionId` that can represent:

```text
new unsaved Tool        -> no toolId/toolRevisionId yet
existing Tool draft     -> durable IDs may also be present
```

Persist the temporary authoring session in `sessionStorage` under a namespaced/versioned key. The stored payload must be bounded and contain only browser-visible authoring state.

Do not store credentials, access tokens, connection secrets or provider authorization values.

### R4 — preserve the whole originating Tool draft

Before navigating to Explore, store the exact current Tool authoring draft plus its return location.

`Use in tool` may merge only the Admin query-authoring fields produced by COMMERCE-061, conceptually:

```text
apiVersion
schemaHash
document
operationName
variables
```

It must not replace unrelated authoring state such as:

```text
name
description
inputSchema
resultPath/resultSchema
responseTemplate
other tab-local draft state
```

### R5 — exact session return

`Use in tool` must update the same `authoringSessionId` that opened Explore and navigate to that session's validated `returnTo` location.

Two concurrent authoring sessions must not write into one another.

Do not use one global `tool-draft` storage key.

### R6 — Cancel does not commit Explore changes

Explore may maintain temporary working selection/binding state. Leaving/cancelling Explore without `Use in tool` must leave the originating Tool authoring session unchanged.

### R7 — session hydration survives route remount and refresh

The authoring session must be restorable from `sessionStorage` when Context/route components remount during the same browser session.

If the stored version is unknown/corrupt or the requested session ID is missing, fail safely with an actionable authoring message rather than applying another session's state.

### R8 — lifecycle cleanup

Successful final Tool creation and explicit authoring discard/cancel must clear the corresponding session entry.

Do not clear a different active session.

### R9 — representable manual queries can seed Explore

When COMMERCE-061 can represent the current manual Admin document, initialize the visual selection/bindings from it.

When it cannot, explain that the query remains valid/manual but is not representable in Explore. Do not rewrite or discard it.

### R10 — validation remains canonical

`Validate`/`Use in tool` must use the Admin compiler path from COMMERCE-061/018. Visual selection alone is not proof of validity.

## Work Items

- [x] Extend Studio composer authoring state with `authoringSessionId` and optional durable Tool IDs.
- [x] Add versioned `sessionStorage` persistence/hydration/cleanup for Tool authoring sessions.
- [x] Replace Explore schema/browser/query builder with Admin equivalents from COMMERCE-061.
- [x] Support current-manual-query seeding when representable.
- [x] Add `Use in tool` merge semantics that update only Admin query fields.
- [x] Return to the exact originating Request authoring location.
- [x] Preserve unrelated Tool draft fields across the round trip.
- [x] Add cancel/corrupt-session/multiple-session/refresh tests.

## Interfaces / Contracts

Consumes the Commerce-internal Admin discovery/query-authoring contract from COMMERCE-061.

Introduces one browser-only, versioned authoring-session shape owned by Commerce Studio. It is not a database or cross-service contract.

## Dependencies

- `ARCH-021-COMMERCE-039`
- `ARCH-021-COMMERCE-061`

## Enables

- `ARCH-021-COMMERCE-065`
- `ARCH-021-COMMERCE-069`

## Acceptance Criteria

- [x] New unsaved Shopify Tool -> Explore -> Use in tool returns to the same draft.
- [x] Existing Tool draft -> Explore -> Use in tool returns to the same draft.
- [x] The round trip survives a route remount/refresh in the same browser session.
- [x] Other draft fields are unchanged by `Use in tool`.
- [x] Cancel leaves the originating draft unchanged.
- [x] Two authoring sessions cannot cross-write.
- [x] Manual GraphQL is still editable after returning from Explore.
- [x] Representable manual GraphQL seeds Explore; unsupported visual forms are preserved rather than rewritten.
- [x] No Tool/ToolRevision is created merely by opening or using Explore.
- [x] No credentials are stored in `sessionStorage`.
- [x] General tab gating/traversal is unchanged.

## Validation

- [x] focused Studio composer/session-storage tests
- [x] Explore Shopify Admin UI tests
- [x] new-Tool round-trip tests
- [x] persisted-draft round-trip tests
- [x] targeted lint
- [x] changed-file TypeScript diagnostics
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, return the Completion Report to `moda_architect` and STOP. Do not begin COMMERCE-065 or COMMERCE-069.

## Implementation Notes

Use `sessionStorage`, not `localStorage`, for temporary durability. Context remains the reactive in-app interface; browser session storage is the remount/refresh recovery layer.

The implementation may split storage serialization into a focused module rather than embedding storage calls throughout React components.

## Completion Report

### Status

Review

### Files Changed

Implementation repository: `moda-interact-commerce`.

- `components/studio-composer-context.tsx`
- `src/commerce/tool-authoring/admin-validation.ts`
- `src/studio/discovery/admin-explorer.tsx`
- `src/studio/tools/admin-validation-server-actions.ts`
- `src/studio/tools/new-tool-editor.tsx`
- `src/studio/tools/shopify-admin-editor.tsx`
- `src/studio/tools/tool-authoring-screen.tsx`
- `src/studio/tools/tool-editor.tsx`
- `tests/admin-explorer.test.tsx`
- `tests/shopify-admin-authoring-validation.test.ts`
- `tests/shopify-admin-tools-ui.test.tsx`
- `tests/tool-authoring-screen.test.tsx`

### Work Completed

- Replaced the Explore surface with the pinned Shopify Admin GraphQL schema browser and query-authoring flow.
- Added bounded, versioned `sessionStorage` sessions keyed by opaque IDs; restored exact Request editor buffers and Explorer tab, visual selection, and raw literal text across remounts.
- Implemented New Tool and existing Admin draft Request -> Explore -> Use in tool -> Request round trips. Use in tool merges only Admin execution query fields after canonical validation; Cancel discards transient Explorer state without changing the originating definition.
- Preserved representable manual query selections and left valid nonrepresentable manual documents unchanged until a visual edit. Added missing/corrupt-session, cleanup, isolation, no-durable-write, and refresh coverage.
- Lifted raw Admin literal text into the parent New and existing-draft editors, preserving malformed text and authored whitespace exactly through Explore and route remounts without draft writes.
- Made Explore validation Request-only: it validates the current InputSchema and the Admin query-authoring execution subset through `compileAdminQueryAuthoring`, without parsing or validating Response/result-template buffers.
- Added separate reactive composer identities for unsaved and existing authoring sessions. Durable `tool` and `release` preview handoffs remain unchanged; session identity is set on Explore open/restore and cleared on discard, consume, or successful creation.

### Validation Results

- Focused authoring/session/Explorer/Preview/query-builder regression set: 8 files, 98 tests passed.
- ESLint passed for all 12 changed source and test files.
- Full Commerce `tsc --noEmit` remains blocked by existing diagnostics in preview route imports, `lib/discovery/compiler.ts`, `scripts/validate-shopify-admin-local.ts`, `src/commerce/integration/studio/services.ts`, and the existing Admin query-builder GraphQL `TypeNode` conversion. A filtered check reported no diagnostics in the 12 changed files after the test fixture annotations were corrected.
- Prisma client generation passed through the already-installed CLI: `./node_modules/.bin/prisma generate --schema database/prisma/schema.prisma`. The preceding pnpm invocation was blocked by ignored package build scripts; no build-script approval was granted.
- `git diff --check` passed.

### Attempt 2 Execution Evidence

- Canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-064`, branch `task/ARCH-021-COMMERCE-064`. It started at the launcher-prepared claim commit `e51e7ce60bb7842b8a554a618e7c59341ecf8f0b`; the parent report worktree was clean before this report update.
- Canonical implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-064`, branch `task/ARCH-021-COMMERCE-064`. Launcher synchronization merged current `origin/main`; implementation started clean at `1d3a5234090597a9e09b9a9863ba9f91c6d584db`.
- Recursive implementation submodule `database` was prepared at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`; `git submodule status --recursive` showed it initialized and clean.
- Worktree registration checks found one canonical parent and one canonical implementation worktree for C064; no other task worktree was reused. The shared workspace remained on `main` at `b7f4019b0385e3ef40d1e49d10dec446143a97d0`; it had unrelated dirty/untracked workspace content, which this task left untouched. No implementation edits were made in the shared checkout.
- Launcher Attempt 2 claim `e51e7ce60bb7842b8a554a618e7c59341ecf8f0b` was pushed before implementation work. No startup synchronization or submodule initialization was repeated during this continuation.
- Attempt 2 implementation commit `933ffa8` was pushed to `origin/task/ARCH-021-COMMERCE-064`; this report update is being published on the mirrored parent task branch.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

The full Commerce TypeScript check is not clean due to the unrelated baseline diagnostics listed above; no C064-touched file reports a TypeScript diagnostic.

### Architectural Concerns

None.

### Attempt 3 Execution Evidence

- Reconciled Request `literalText` during `Use in tool`: exact raw JSON text is retained only when its parsed value still equals the same literal mapping; changed/new mappings receive bounded canonical JSON text, while stale/nonliteral entries are removed. Other editor buffers remain unchanged.
- Added actual New Tool Request -> Explore visual literal edit -> Validate -> Use in tool -> Request/remount coverage. It verifies the returned query and variables, valid visible JSON literal text and Request mapping, unchanged unrelated buffers, and no durable Tool create. A companion case verifies exact raw-text preservation for an unchanged mapping and stale-buffer removal.
- Focused validation passed: five suites, 55 tests; ESLint passed for both Attempt 3 files; `git diff --check` passed. Full Commerce `tsc --noEmit` still reports the previously documented repository baseline diagnostics; filtering found no diagnostics in either Attempt 3 file.
- Implementation commit `c0e07c5` (`fix(commerce): reconcile Explore literal request buffers`) was pushed to `task/ARCH-021-COMMERCE-064`.
- Launcher evidence: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-064`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-064`; both task branches are `task/ARCH-021-COMMERCE-064`. The prepared start heads were parent `4253a76e23e75248607d6cbbe6313a5c755939ae` and implementation `45be742f9c001729df5085a0c47bef724aa56633`; claim commit `f54c866441678aa6514cf68e933460efccdea808` was pushed. The recursive `database` submodule was ready at `0a8d3b9feade69690b6c1e33aeda051ea588bd45`. The shared workspace and shared implementation checkout were not modified, and no other task worktree was reused.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 satisfies the remaining Attempt 2 correction contract. `Use in tool` now reconciles the Request literal buffer with the accepted Admin variable mappings deterministically: exact raw JSON text is preserved only when it still parses to the same semantic literal value; new, renamed or changed literal mappings receive bounded canonical JSON text; stale/nonliteral entries are removed; and unrelated editor buffers are not modified.

The focused New Tool regression exercises the actual Request -> Explore -> visual literal edit -> Validate -> Use in tool -> Request path. It proves that a newly generated string literal returns as valid JSON text (`"customer_email:test"`), the accepted query/variable mapping is restored into the Request editor and validates successfully, the browser authoring session contains the reconciled literal buffer, and no final Tool create action is required for the Explore handoff. The companion unchanged-literal regression preserves exact authored whitespace and removes stale literal entries.

The authoritative task handoff is also correct for Attempt 3: `status: review`, `attempt: 3`, `executor: null` and `claimed_at: null`, with dedicated parent/implementation worktree evidence recorded in the Completion Report.

The four Attempt 1 corrections and the accepted Attempt 2 boundaries remain preserved: Request-only Explore validation, distinct transient authoring identity, exact authoring-session isolation/restoration, Cancel semantics, no provider I/O and no durable Tool persistence merely for Explore navigation.

### Reviewed Files

- `docs/decisions/commerce/ARCH-021/COMMERCE-064-rebuild-explore-shopify-admin-authoring.md`
- `src/studio/discovery/admin-explorer.tsx`
- `tests/admin-explorer.test.tsx`
- relevant previously accepted C064 authoring/session files recorded in the Completion Report

### Validation Reviewed

- Inspected the Attempt 3 implementation and focused regressions in `admin-explorer.tsx` and `admin-explorer.test.tsx`.
- Submitted Attempt 3 validation reports 55/55 tests across five suites, targeted ESLint and `git diff --check` passing, with no filtered TypeScript diagnostics in either Attempt 3 file.
- The full Commerce TypeScript check remains red on the previously documented unrelated repository diagnostics and is not treated as a C064 regression.
- No independent test rerun was performed from the supplied review archive.

### Architecture Conformance

Conformant. Explore Shopify is now an Admin `2026-07` authoring surface that round-trips both unsaved New Tool and existing-DRAFT Request state through versioned browser-session authoring identity without introducing unfinished durable Tool state. `Use in tool` updates only the accepted Admin query-authoring fields while keeping Request literal buffers semantically aligned and preserving unrelated draft/editor state. Manual GraphQL remains authoritative, canonical validation remains the validity boundary, and Storefront removal/provider execution remain outside C064.

### Follow-up

COMMERCE-064 is Complete. COMMERCE-062 is already Complete, so COMMERCE-065 becomes Ready. COMMERCE-060 is already Complete, so COMMERCE-069 also becomes Ready. Those two tasks are independent and may be executed separately. COMMERCE-068 remains Pending until COMMERCE-065 is Complete.
