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
status: review
priority: 74
executor: copilot
claimed_at: 2026-09-27T15:20:54Z
attempt: 1
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

Explore route/workspace integration, New and existing Tool Request editors, transient authoring-session storage, Admin Explorer/schema browser/argument controls, and focused session/handoff/workspace tests.

### Work Completed

- Replaced the Explore surface with the pinned Shopify Admin GraphQL schema browser and query-authoring flow.
- Added bounded, versioned `sessionStorage` sessions keyed by opaque IDs; restored exact Request editor buffers and Explorer tab, visual selection, and raw literal text across remounts.
- Implemented New Tool and existing Admin draft Request -> Explore -> Use in tool -> Request round trips. Use in tool merges only Admin execution query fields after canonical validation; Cancel discards transient Explorer state without changing the originating definition.
- Preserved representable manual query selections and left valid nonrepresentable manual documents unchanged until a visual edit. Added missing/corrupt-session, cleanup, isolation, no-durable-write, and refresh coverage.

### Validation Results

- Focused round-trip/session/workspace/Admin query-builder suite: 6 files, 65 tests passed.
- Admin GraphQL compiler and no-provider-I/O suites: 2 files, 17 tests passed.
- Admin Explorer refresh test and focused lint passed after adding selection, tab, and raw literal restoration assertions.
- ESLint passed across all changed source and test files.
- Full Commerce `tsc --noEmit` remains blocked by pre-existing diagnostics in preview route imports, `lib/discovery/compiler.ts`, `scripts/validate-shopify-admin-local.ts`, `src/commerce/integration/studio/services.ts`, and the existing Admin query-builder GraphQL `TypeNode` conversion. Filtered diagnostics for C064-touched files are clean.
- `git diff --check` passed.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

The full Commerce TypeScript check is not clean due to the unrelated baseline diagnostics listed above; no C064-touched file reports a TypeScript diagnostic.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
