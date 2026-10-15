---
id: ARCH-032-MCP-019
architecture_id: ARCH-032
title: Restore the Commerce capabilities MCP resource and published manifest projection
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 8
executor: developer
claimed_at: 2026-10-15T13:30:28+01:00
attempt: 1
depends_on: []
enables: []
created: 2026-10-15
updated: 2026-10-15
---

# ARCH-032-MCP-019 — Restore the Commerce capabilities manifest resource

## Architecture

Architecture ID: `ARCH-032`.

Architecture document: `docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md`.

Coordinator: `moda_architect`.

This is a targeted integration-defect correction against the supplied 2026-10-15
workspace snapshot. It does not reopen ARCH-032's deferred Studio preview,
Gateway cutover or unrelated execution-policy tasks.

## Objective

Make the standalone private MCP service advertise and serve the existing
`commerce://capabilities` resource as a **complete, schema-valid CommerceManifest**
projected from the shop's current published release and its eligible capabilities,
without changing tool invocation behaviour or importing conversation-grant ownership
into MCP.

## Context

The real Messaging -> Background -> MCP system-test path reaches
`whatsapp.turn.agent_started` and then fails at `mcp.manifest/read_manifest` with
`MCP_MANIFEST_READ_FAILED`. Background calls `client.readResource({ uri:
"commerce://capabilities" })`; MCP's `validateApplicationShape` already accepts
this request. However `src/mcp/registration.ts` currently advertises only
`tools: {}` and registers only `tools/list` and `tools/call`. There is no resources
capability or resource handler.

Furthermore `McpShopSnapshot` only contains `shopId`, `environment`, `releaseId`
and an executable capability list, whereas the published Shared
`CommerceManifestSchema` also requires the immutable release contract, selected
capability ordering, frozen feature behaviour prompts and a consistent grant
projection. Registering a handler that serialises `McpShopSnapshot` would merely
replace the protocol error with a schema error.

The current Prisma model already stores `CommerceRelease.runnerCompatibility`,
`contractVersion`, `responseContract`, `responseContractHash` and frozen
`CommerceReleaseFeature.behaviourPrompt`; use these persisted values, not defaults,
fixtures, mutable authoring settings or synthetic data.

## Scope

- `moda-interact-mcp` only: MCP capability and resource registration; the shop
  capability reader's persisted-release projection; manifest construction and
  validation; directly related MCP unit and disposable-PostgreSQL tests.
- Maintain the existing authenticated-private-ingress assumptions and shop
  context resolution, release-pointer selection, RepeatableRead read transaction,
  entitlement/preference/platform gating and supported-executor filtering.
- Preserve `tools/list`/`tools/call` behaviours and advertised capability identity
  while adding resource discovery/read support.

## Out of Scope

- Changes to `moda-interact-system-test`, aimock, Background, Messaging, Commerce,
  Shopify, WooCommerce, API, Gateway, Shared or Database repositories.
- Prisma schema changes or migrations; a second manifest schema or hard-coded
  substitute for the published release.
- Changes to conversation grants, Background's runner, selected-model settings,
  LLM calls, WhatsApp output, private ingress or endpoint cutover.
- The pre-existing tool-name/identity compatibility question between Background
  descriptor names and MCP capability-key `tools/list` entries. Do not silently
  change either interface to address it under this resource-only correction.
- Any `docs/decisions/**/_index.md` or unrelated architecture-document changes.

## Requirements

1. MCP `initialize` advertises both `tools: {}` and `resources: {}`. Retain the
   mandatory tools capability even for a shop with zero eligible tools.
2. `resources/list` returns exactly the bounded published resource descriptor
   for `commerce://capabilities` (`mimeType: application/json`); it does not
   reveal other shops' resources or unpublished/draft data.
3. `resources/read` for that exact URI returns one textual entry containing:

   ```json
   {
     "contents": [{
       "uri": "commerce://capabilities",
       "mimeType": "application/json",
       "text": "<JSON-encoded CommerceManifest>"
     }]
   }
   ```

   The angle-bracket placeholder above is documentation only; `text` must be a
   JSON string of a real manifest and must pass the published Shared schema.
   Unknown/malformed URIs fail closed with safe protocol errors.
4. The manifest includes the persisted `contractVersion`, `releaseId`,
   `runnerCompatibility`, `responseContract` and `responseContractHash`; the
   currently **eligible, published and executable** capabilities with exact pinned
   `toolDescriptor`, `capabilityId`, `key`, `featureId` and strictly increasing
   original release `position`; frozen `featureBehaviours` for those represented
   features in first-occurrence order; matching `selectedCapabilityKeys`; and
   deterministic `grantedTools` corresponding to the selected capability set.
5. For multiple selected capabilities pointing at the same published tool,
   retain both capability entries and produce the single consistent granted-tool
   identity with sorted capability keys. Reuse Shared commerce helpers and
   schemas (including `CommerceManifestSchema`) instead of reimplementing
   their canonicalisation or contract rules.
6. A shop with zero **eligible** capabilities and a valid published release
   returns a valid empty-capability manifest and `tools: []`; no release pointer,
   incompatible release, malformed descriptor, inconsistent feature snapshot,
   bad response contract/hash, cross-shop context or invalid projection fails
   closed. Do not invent a release or grant to make tests pass.
7. The resource is derived from the same request-scoped shop/release snapshot
   used for tools discovery, with no tenant leakage. Respect current MCP bounds,
   cancellation, private/no-store transport behaviour and sanitized logging;
   do not place credentials or raw Prisma errors in resource output.
8. Do not access `Conversation`, `CommerceConversationGrant`, processing leases
   or trusted prompt/conversation data to project the manifest. Background
   remains responsible for persisting and enforcing conversation grants.

## Work Items

- [ ] Add MCP resource capability, `resources/list` and `resources/read`
      registration in `src/mcp/registration.ts`, preserving current tool handlers.
- [ ] Extend the existing reader/records/ports as needed to carry the published
      release metadata and its frozen feature snapshots in the same bounded
      `RepeatableRead` projection (`src/capabilities/` and `src/mcp/`).
- [ ] Build and validate one `CommerceManifest` using published Shared commerce
      exports; reject inconsistent or oversized projections with stable safe
      MCP reason codes.
- [ ] Confirm eligible capability ordering, tool deduplication, release pointer,
      empty-shop and revocation behaviour without reading conversations/grants.
- [ ] Add protocol tests using the MCP SDK client (initialize, resources/list,
      resources/read, malformed URI) and ensure `tools/list`/`tools/call`
      regression tests still pass, including shared-tool capabilities.
- [ ] Add/extend disposable migrated PostgreSQL integration coverage for pinned
      release metadata, frozen feature behaviour, response hash, eligibility and
      empty-capability shops. Correct test fixtures where they contradict the
      published Shared schema; never weaken production validation to fit fixtures.

## Interfaces / Contracts

- MCP protocol: `initialize`, `resources/list`, `resources/read` for URI
  `commerce://capabilities`; existing `tools/list` and `tools/call` are preserved.
- Contract owner: `moda-interact-shared`; consume the **published**
  `@modainteract/moda-interact-shared/commerce` exports including
  `CommerceManifestSchema` and existing contract/deduplication utilities.
- Producer: `moda-interact-mcp`; existing consumer:
  `moda-interact-background/src/commerce/mcp-client.ts`.
- Persistent source: the environment's current `CommerceReleasePointer`, its
  `CommerceRelease`, `CommerceReleaseCapability`, `CommerceReleaseFeature`,
  published tool revisions, shop state, plan features and shop preferences.
- No new inter-service payload version, queue event or database table.

## Dependencies

None as a *new task gate*: this correction targets the MCP runtime and published
Shared contract already present in the 2026-10-15 snapshot. Existing ARCH-032
historical task-status metadata is not silently treated as accepted; do not
change those tasks or unblock deferred Studio/Gateway work in this patch.

## Enables

No automatic task promotion. On acceptance, the developer may rebuild **only**
the standalone MCP image and rerun the same black-box system-test scenario.
Subsequent integration defects, if any, require independent evidence/review.

## Acceptance Criteria

- [ ] `initialize` declares `tools` and `resources` even for an empty shop.
- [ ] `resources/list` contains the exact `commerce://capabilities` resource.
- [ ] `resources/read` returns one `application/json` textual resource whose
      parsed body passes the published `CommerceManifestSchema`.
- [ ] The manifest has every required release, feature, capability, selection,
      granted-tools and response-contract field from the actual persisted state.
- [ ] Published pinned revisions, same-tool multi-capability provenance,
      release ordering and frozen feature behaviour are preserved.
- [ ] Zero eligible capabilities produce a valid empty manifest and empty tool
      catalogue; missing/invalid release and snapshot data fail closed.
- [ ] Unsupported/revoked or other-shop capabilities never appear in the
      manifest; current shop authorisation and executor gating remain intact.
- [ ] Existing `tools/list` and `tools/call` behaviour remains unchanged, and
      argument validation, provider isolation and execution limits still pass.
- [ ] No migration, unrelated application change or `_index.md` edit occurs.

## Validation

- [ ] Use the launcher-resolved dedicated parent and MCP implementation task
      worktrees; record preparation/synchronisation evidence in Completion Report.
- [ ] `git diff --check` for the implementation and parent task reports.
- [ ] Focused MCP protocol/resource and capability/reader unit tests, including
      SDK client-driven initialize/list/read and empty-capability cases.
- [ ] Migrated disposable PostgreSQL integration exercising the complete
      release projection and release pointer, preferably using the repository's
      existing Docker test harness.
- [ ] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` in MCP.
- [ ] `npm run typecheck:integration` and `npm run test:integration:docker`
      when Docker is available; if blocked, report precisely and leave the
      required validation unchecked.
- [ ] Confirm no changes outside the assigned MCP repository and parent task
      file; do not claim success of the full system test at unit-test completion.

## Stop Condition

When the bounded resource/manifest work and required validation are complete,
record the implementation and evidence, return the task to `review` and STOP.
Do not begin the separate tool-name compatibility correction, system-test changes
or dependent architecture tasks without architect review.

## Implementation Notes

The portable task definition was materialised in the canonical parent task
worktree and published on `task/ARCH-032-MCP-019` in commit `9364f493`.
Developer Attempt 1 is claimed. The canonical MCP implementation worktree is
prepared at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-032-MCP-019`.

Preserve `docs/decisions/**/_index.md` as requested. An observed later failure
from Background's tool descriptor name versus MCP capability-key identity
must be returned to `moda_architect` as a separate integration finding; do not
conflate it with the currently proven missing resource handler.

## Completion Report

### Status

In Progress

### Files Changed

No implementation files changed during task preparation.

### Work Completed

Materialized and published the task definition in the parent task worktree;
created the MCP implementation worktree from current `origin/main`; verified
the task has no dependencies and both worktrees are clean and correctly routed.

### Validation Results

Task-file whitespace check passed. Required implementation tests and build
validation have not been run; implementation has not started.

### Deviations

None

### Assumptions

The uploaded snapshot is the implementation baseline; local repository HEAD,
worktree and dependency version must be reconfirmed before execution.

### Unresolved Issues

Background-to-MCP tool-name compatibility requires follow-up verification after
manifest restoration; not evidence of a completed or accepted correction.

### Architectural Concerns

No direct MCP conversation-grant ownership is permitted. Background's name/key
compatibility must not be silently altered during manifest projection.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed; task definition only.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation review.

### Follow-up

Rerun the same system-test scenario after the standalone MCP image is rebuilt;
classify any later protocol/authorization failure independently.
