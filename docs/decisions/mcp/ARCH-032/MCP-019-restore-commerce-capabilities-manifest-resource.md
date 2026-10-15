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
status: complete
priority: 8
executor: null
claimed_at: null
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

- [x] Add MCP resource capability, `resources/list` and `resources/read`
      registration in `src/mcp/registration.ts`, preserving current tool handlers.
- [x] Extend the existing reader/records/ports as needed to carry the published
      release metadata and its frozen feature snapshots in the same bounded
      `RepeatableRead` projection (`src/capabilities/` and `src/mcp/`).
- [x] Build and validate one `CommerceManifest` using published Shared commerce
      exports; reject inconsistent or oversized projections with stable safe
      MCP reason codes.
- [x] Confirm eligible capability ordering, tool deduplication, release pointer,
      empty-shop and revocation behaviour without reading conversations/grants.
- [x] Add protocol tests using the MCP SDK client (initialize, resources/list,
      resources/read, malformed URI) and ensure `tools/list`/`tools/call`
      regression tests still pass, including shared-tool capabilities.
- [x] Add/extend disposable migrated PostgreSQL integration coverage for pinned
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

- [x] `initialize` declares `tools` and `resources` even for an empty shop.
- [x] `resources/list` contains the exact `commerce://capabilities` resource.
- [x] `resources/read` returns one `application/json` textual resource whose
      parsed body passes the published `CommerceManifestSchema`.
- [x] The manifest has every required release, feature, capability, selection,
      granted-tools and response-contract field from the actual persisted state.
- [x] Published pinned revisions, same-tool multi-capability provenance,
      release ordering and frozen feature behaviour are preserved.
- [x] Zero eligible capabilities produce a valid empty manifest and empty tool
      catalogue; missing/invalid release and snapshot data fail closed.
- [x] Unsupported/revoked or other-shop capabilities never appear in the
      manifest; current shop authorisation and executor gating remain intact.
- [x] Existing `tools/list` and `tools/call` behaviour remains unchanged, and
      argument validation, provider isolation and execution limits still pass.
- [x] No migration, unrelated application change or `_index.md` edit occurs.

## Validation

- [x] Use the launcher-resolved dedicated parent and MCP implementation task
      worktrees; record preparation/synchronisation evidence in Completion Report.
- [x] `git diff --check` for the implementation and parent task reports.
- [x] Focused MCP protocol/resource and capability/reader unit tests, including
      SDK client-driven initialize/list/read and empty-capability cases.
- [x] Migrated disposable PostgreSQL integration exercising the complete
      release projection and release pointer, preferably using the repository's
      existing Docker test harness.
- [x] `npm run typecheck`, `npm run lint`, `npm test`, `npm run build` in MCP.
- [x] `npm run typecheck:integration` and `npm run test:integration:docker`
      when Docker is available; if blocked, report precisely and leave the
      required validation unchecked.
- [x] Confirm no changes outside the assigned MCP repository and parent task
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

Complete — Attempt 1 accepted and explicitly completed by the developer.

### Files Changed

Implementation changes are confined to the 16 files in the MCP repository diff
against `origin/main`: manifest projection and registration in `src/capabilities/`
and `src/mcp/`, plus related fixtures and unit/integration tests. No migration,
`_index.md`, or other repository was changed. The parent-workspace change is this
task file only.

### Work Completed

Restored the private `commerce://capabilities` resource and schema-valid manifest
projection from the persisted published release, retaining the existing tool
handlers and shop-scoped authorization. Added SDK protocol and disposable
PostgreSQL coverage for pinned release data, feature snapshots, eligibility,
revocation, shared-tool provenance and the empty-capability case. The existing
Shopify executor test fixture used `definition.name` after spreading a broadly
typed record; corrected that fixture to read its already-persisted name once.

Implementation branch `task/ARCH-032-MCP-019` is published through `bd618bb`
(`test(mcp): fix Shopify executor fixture typing`), following implementation
commit `ea590ec`.

### Task Preparation and VCS Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Dedicated parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-032-MCP-019`, branch `task/ARCH-032-MCP-019`.
- Dedicated implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-032-MCP-019`, branch `task/ARCH-032-MCP-019`.
- Task definition was materialized in parent commit `9364f493`; the attempt claim was recorded in parent commit `87e638dcb`.
- Implementation was prepared from current `origin/main`; before the final correction its task branch was at published commit `ea590ec`, equal to `origin/task/ARCH-032-MCP-019`.
- The shared workspace and shared implementation checkout were not switched or edited for task work; no other task worktree was reused.
- The parent task worktree contains an unrelated untracked Vim swap file; it was left untouched. Other pre-existing shared-workspace changes were also left untouched.
- Review submission was published in parent commit `904e54e6`; implementation branch remains published through `bd618bb`.

### Validation Results

- `npm run typecheck`: passed after the fixture typing correction.
- `npm run lint`: passed after the fixture typing correction.
- `npm test`: 148 passed, 0 failed, 0 skipped after the correction.
- `npm run build`: passed.
- `npm run typecheck:integration`: passed.
- `npm run test:integration:docker`: passed against disposable migrated PostgreSQL; 16 passed, 0 failed, 1 opt-in live Shopify test skipped. The harness removed its temporary container, volume and network.
- Focused Shopify executor test: 4 passed, 0 failed.
- `git diff --check`: passed for the implementation change and parent task report.
- The cross-service black-box system-test scenario was not run; no system-test success is claimed.

### Deviations

The initial typecheck found two type errors in an existing Shopify test fixture, where `definition.name` was read from a spread object whose inferred type omitted that property. The fixture now reads `name` from the original pinned definition. Typecheck, lint, focused and full unit tests passed after the correction.

### Assumptions

The manifest contract and existing published Shared commerce schema in the supplied
workspace snapshot are authoritative. No schema or dependency changes were needed.

### Unresolved Issues

The separate Background descriptor-name versus MCP capability-key compatibility
question remains out of scope and requires architect-owned integration follow-up.
The black-box system-test scenario remains pending.

### Architectural Concerns

No direct MCP conversation-grant ownership was introduced. Background's name/key
compatibility was not altered as part of manifest projection.

### Dependency Frontier Reconciliation

`ARCH-032-MCP-020` now has its only declared dependency satisfied and is
dependency-eligible. It remains `pending`: this task explicitly specifies no
automatic downstream task promotion, and no sibling task record was changed.
`ARCH-032-COMMERCE-006` and `ARCH-032-BACKGROUND-001` still depend on MCP-020;
COMMERCE-006 also depends on COMMERCE-005. `ARCH-032-SYSTEM-TEST-002` remains
pending and manual-gated, with additional implementation and infrastructure
dependencies outstanding. No downstream task was claimed or completed.

## Architect Review

### Review Status

Accepted

### Review Notes

The developer supplied the disposition `Architect Review Accepted` with the
explicit completion action on 2026-10-15. It applies to the bounded MCP-019
implementation and the recorded validation evidence. This is not a claim that
the cross-service black-box system-test scenario passed; that scenario remains
pending as stated in the Completion Report.

### Reviewed Files

The MCP-019 implementation branch through `bd618bb` and the task Completion
Report on parent branch `task/ARCH-032-MCP-019`.

### Validation Reviewed

`npm run typecheck`, `npm run lint`, `npm test` (148/148), `npm run build`,
`npm run typecheck:integration`, and `npm run test:integration:docker` (16 passed,
one opt-in live Shopify test skipped); focused Shopify executor tests (4/4) and
`git diff --check` are recorded as passed.

### Architecture Conformance

Accepted for the task's bounded scope. The separate Background tool-name/key
compatibility correction remains assigned to its own task; no system-test result
or cross-repository implementation is claimed here.

### Follow-up

Continue through the separately governed MCP-020 and other dependent tasks. Run
the black-box system-test scenario only after its required implementation tasks
are accepted and its manual gate is explicitly opened.

## Developer Completion Decision

### Decision

Complete — explicitly authorized by the developer on 2026-10-15 after supplying
`Architect Review Accepted`.

### Accepted Attempt

Attempt 1; attempt number preserved. The implementation branch is committed and
published through `bd618bb`, and the parent task/report branch is committed and
published through this completion record. Neither branch was merged to `main`.
