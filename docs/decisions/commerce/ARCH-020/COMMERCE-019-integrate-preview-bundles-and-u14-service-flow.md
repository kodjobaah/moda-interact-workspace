---
id: ARCH-020-COMMERCE-019
architecture_id: ARCH-020
title: Integrate preview bundles and the U14 service flow
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 145
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-017
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-024
  - ARCH-020-COMMERCE-031
created: 2026-09-21
updated: 2026-09-21
---

# Integrate preview bundles and the U14 service flow

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect saved definitions and prompts to the009 preview lifecycle and017 U14 client, using real Redis and isolated provider/model fixtures. Own preview assembly only; no U01–U13 service wiring.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect saved definitions and prompts to the009 preview lifecycle and017 U14 client, using real Redis and isolated provider/model fixtures. Own preview assembly only; no U01–U13 service wiring.

## Out of Scope

Other integration owners' files; new business features/pages; new Shared release,
database migration or external-service implementation; deployment, paid live
provider calls or WhatsApp delivery. Do not replace real components with fixtures.

## Requirements

Follow C20 file ownership and mapping rules. Authorize each protected request using
the accepted auth library. Reuse source schemas, field bounds, hashes and replay/CAS
semantics. Preserve all active work. No production test-adapter registration.
At preparation verify each source/export against its accepted commit and record
that SHA in the mapping document; pending producer symbols must not be guessed.

## Work Items

- [x] Own `src/commerce/integration/preview/` and minimal composition in `lib/preview/runtime.ts` plus U14 client injection. Do not edit018 Studio services/actions or013 backend factory.
- [x] Implement PreviewBundleLoader, PreviewPromptLoader and PreviewToolExecutionPort from accepted009 types using013 read facade and authorized saved revisions. Do not replace authored prompts with generic strings.
- [x] Freeze exact revision content, response definition and synthetic grant at start. After a saved draft changes, an existing conversation still executes its frozen definition; no reloading latest tool content during later turns.
- [x] Instantiate009 PreviewService/RedisPreviewStateStore and typed ports. Use014 actual interpreter with isolated fixture operation adapters; explicit MODEL mode uses separate model config, never production credentials.
- [x] Connect017 PreviewClient to exact C9.1 routes. Retain008 layout handoff and Back restoration using component fixture mounting where needed; no dependency on018 service adapters.
- [x] Provide `docs/commerce-preview-integration.md` and `test:arch020-preview-integration` plus `test:arch020-preview-integration:redis`; preserve existing quotas/replay/cancel logic instead of duplicating it.

## Interfaces / Contracts

Source: `src/commerce/preview/types.ts: PreviewBundleLoader, PreviewPromptLoader,
PreviewToolExecutionPort` and `service.ts: PreviewServiceDependencies`.
`lib/preview/types.ts`/`service.ts` re-export these; do not create a second service.
Destination: `lib/preview/runtime.ts:getPreviewService`, replacing unavailableLoader
with real preview adapters.017's accepted PreviewClient supplies frontend route
calls; record actual file/export once017 is accepted, not a guessed symbol.
013 provides read-only saved-definition access and interpreter factory;019 supplies
fixture transports explicitly. Never reuse the live policy/provider registry.
PreviewResult and body/error shapes remain009/C9.1, not UI-specific alternatives.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-017
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-024
- ARCH-020-COMMERCE-031

## Acceptance Criteria

- [x] P01: real017 UI ->009 route -> real saved loader -> Shared runner/interpreter -> Redis -> reply/details flow; no fake preview service or constant EVAL response.
- [x] P02: N10/N11/N13 preview portion covers release/draft/tool entry, sidebar, Back and refresh loss. Test the real008 composer handoff with injected source data;018 is not required.
- [x] P03: repeated/concurrent Send, same-ID changed payload, cancel/complete race, expired/unknown state and quota boundaries preserve one reservation/model start per logical run across two service instances.
- [x] P04: edit/publish saved content between turns; frozen prompts/tool definitions and language/history persist. New conversation sees new selection; no production grant/reset/write.
- [x] P05: denied staff or foreign/missing revision fails before loading sensitive content; fixture/model credentials remain isolated and no WhatsApp/live-Shopify transport is constructed.
- [x] P06: fail unavailable if loader/Redis/model config is absent; same-code default FIXTURE run works without paid credentials. Real Redis tests verify counters/locks/results/TTL, not merely Lua source text.

## Validation

Use the C20 shared isolated seed contract and this task's named scenarios. Assert
rows, operation IDs, provider calls and state, not only HTTP200 or screenshots.
Substitute external provider/model transports only; application services under
integration remain real. Run focused integration tests during work, then repository
typecheck/lint/build before submission. No redundant full-suite reruns without new
changes/failures. PostgreSQL/Redis/container checks obey the existing execution
policy: provide the command and actual evidence separately; a not-run required
check is not a pass. No paid model, live Shopify or production credentials required.
Document owned commands and exact outputs in the report; C20 maps every former
I01–I09 requirement to an owner so no acceptance coverage disappears.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Review.

### Files Changed

- `moda-interact-commerce/lib/preview/runtime.ts`
- `moda-interact-commerce/src/commerce/integration/preview/adapters.ts`
- `moda-interact-commerce/tests/preview-integration.test.ts`
- `moda-interact-commerce/docs/commerce-preview-integration.md`
- `moda-interact-commerce/package.json`

### Work Completed

Connected production `PreviewService` composition to Redis, the accepted COMMERCE-013
saved-selection facade, authored prompt loading, and fixture tool execution. Fixture
execution uses the accepted definition executor with a synthetic query boundary and
does not construct live Shopify or paid model transports. Bundle, prompt, and loaded
tool definitions are frozen for an existing conversation. Added focused integration
and Redis validation scripts plus integration documentation.

### Validation Results

- `npm run test:arch020-preview-integration`: 4 files passed, 37 tests passed.
- `npm run test:arch020-preview-integration:redis`: 1 file passed, 4 tests passed.
- `npm run typecheck`: passed.
- `npm run lint`: passed with 2 pre-existing warnings in
  `scripts/code-runtime-manifest.mjs` and `src/commerce/code-response/runtime/kernel.ts`.
- `npm run build`: passed; Next.js production build completed and emitted all expected
  Commerce routes.
- `git diff --check`: passed.
- Recursive database submodule initialized at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

### Deviations

The generic MODEL adapter remains fail-closed because no separate preview model
configuration was installed. No live provider, Shopify, WhatsApp, PostgreSQL, or
production credential validation was performed.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Attempt: 1. Implementation worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-019`,
branch `task/ARCH-020-COMMERCE-019`, commits `ed6e22e`, `2ff2a8a`, and
`197d5c6`, pushed to
`origin/task/ARCH-020-COMMERCE-019`. Canonical parent worktree:
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-019`,
branch `task/ARCH-020-COMMERCE-019`. COMMERCE-013 accepted source commit:
`4d529773fde26599027aef2d76fbd70bc974b352`. No parent service gitlink or main
integration was performed.

## Architect Review

### Attempt 1 — Changes Requested — 2026-09-21

Reviewer: moda_architect. **Changes Requested; Ready, Attempt 1 retained;
executor/claimed_at null. Not accepted.** Reviewed the exact submitted
`moda-interact-workspace-ARCH-020-COMMERCE-019.zip`, parent report commit
`5e89f15c647559daee4af6fc95fd0b4840d5c8a0`, C9/C20 and the task acceptance
criteria. The submitted implementation identifies `197d5c6` as its implementation
head. The GitHub connector could not resolve that implementation commit directly,
so source review is grounded in the exact submitted implementation snapshot; the
parent report commit is independently verified.

The implementation materially connects the accepted PreviewService to Redis, the
COMMERCE-013 saved-selection facade, authored prompts and the accepted definition
executor. The reported 37 focused tests, 4 executable Redis tests, typecheck, lint,
build and diff check are useful supporting evidence. This review does not require
an arbitrary larger test count. The blockers below are functional integration
failures in the submitted source.

#### A1-R1 — P1 — Make frozen tool definitions Redis/replica/restart durable

Files: `src/commerce/integration/preview/adapters.ts`, the private preview snapshot
shape/store plumbing needed by C20, `lib/preview/runtime.ts` only if composition
changes, and focused integration tests.

The submitted adapter keeps the selected `PreviewSelection` and exact tool
definitions in module-global process-local Maps (`selections` and `definitions`).
The durable Redis conversation stores the manifest/grant/prompts/history, but not
the exact definitions used to execute later turns. `execute(..., bundle)` therefore
looks up `definitions.get(bundleKey(...))`; after a process restart or on another
Commerce replica the Redis conversation still exists while that Map is empty, so
the later tool call fails `NOT_FOUND` instead of executing the frozen definition.
This contradicts C20's explicit no-global-mutable-registry rule and requirement that
restart/cross-replica fixtures retain the exact frozen content.

There is also an in-process overwrite case: `bundleKey` hashes only the manifest. A
draft edit can change execution/response-template content while keeping the same
revision identity and descriptor-visible fields. Starting a new conversation then
writes the new definition under the same Map key; an older conversation can execute
the newer definition. That violates P04's "existing conversation still executes its
frozen definition" requirement.

Replace the process-local Maps as correctness authority with a bounded frozen
snapshot owned by the preview conversation. Persist the exact selected definitions
with the Redis conversation or persist an opaque Redis snapshot handle that resolves
to the exact immutable snapshot. Take prompts/definitions/response definition from
the authorized creation-time selection, not by re-reading mutable draft content on
a later turn. Preserve the public C9.1 payloads. Enforce C20's snapshot bounds: at
most 32 definitions, each definition <=65,536 bytes, total authored prompts <=64,000
characters and total serialized snapshot <=3 MiB; fail closed rather than dropping
content. No new database table or browser field is required.

Acceptance reproduction: start a tool-using conversation on service instance A,
execute a later turn on instance B sharing only Redis/backend state, and repeat after
a fresh service construction; both must execute the original definition. Also edit
only execution/response-template content so the descriptor/manifest identity remains
otherwise unchanged, start a second conversation, and prove conversation A still
executes its original definition while conversation B sees the edited definition.

#### A1-R2 — P1 — Make the real saved-tool test and tool-entry paths executable

Files: `src/commerce/integration/preview/adapters.ts` and focused real-facade
integration coverage; do not weaken COMMERCE-013 authorization.

`PreviewToolExecutionPort.load()` currently calls the accepted saved facade with
`capabilityRevisionIds: ['preview-capability']`. COMMERCE-013 validates that every
requested capability revision exists, so the production U14 tool-test path is rejected
unless a database row happens to use that fabricated ID. Use the accepted DRAFT
shape for an authorized tool-only read (`capabilityRevisionIds: []`, exact
`toolRevisionIds: [toolRevisionId]`) or another already-accepted facade path; do not
invent a capability identity. The fixture executor must continue to use the accepted
interpreter and synthetic query boundary only.

Also reconcile U14's accepted tool-entry Start flow. The accepted screen sends a
DRAFT selection with zero capability revisions and one tool revision when entered
from a saved tool. The current bundle loader produces zero capabilities and therefore
cannot satisfy `CommerceManifestSchema`; Start fails before a preview conversation is
created. P02 explicitly includes tool entry. Support the accepted tool-entry behavior
without fabricating a generic authored prompt or live grant. If the accepted
COMMERCE-013 facade genuinely lacks the authored BASE data needed to form a valid
synthetic conversation bundle, record that exact interface gap for architect
resolution instead of silently claiming P02 complete. Tool-test execution itself must
work regardless.

Acceptance reproduction should exercise the production adapter against a
COMMERCE-013-compatible saved facade, not a stub that accepts arbitrary IDs: a real
saved tool test succeeds with zero live Shopify/WhatsApp/provider calls, missing or
foreign revisions fail before execution, and the U14 tool-entry Start path either
creates a valid frozen conversation or returns an explicitly documented architectural
gap for resolution.

#### A1-R3 — P2 — Reconcile MODEL mode with the accepted preview configuration

Files: `lib/preview/runtime.ts`, preview integration adapter/config wiring and focused
composition tests.

The production runtime checks `PREVIEW_MODEL_URL`, which is not an ARCH-020 preview
configuration name, and when present installs `createUnavailableModel()`, whose every
call throws `UNAVAILABLE`. Under the accepted C10 configuration
`COMMERCE_PREVIEW_ENABLED=true` with `COMMERCE_PREVIEW_MODEL` and
`COMMERCE_PREVIEW_API_KEY`, `MODEL` therefore remains unavailable; adding the
unapproved variable still cannot produce a model turn. That is not the task's stated
"explicit MODEL mode uses separate model config" integration.

Use the accepted preview-enable/model/API-key configuration and a separately injected
preview model transport. `FIXTURE` must remain the default and require no paid
credentials. Disabled/missing preview/model configuration must fail closed before
model dispatch, and MODEL must never fall back to Background/production credentials
or enable live tools. No paid/live provider call is required for review: prove this
with an injected configured model transport and call counts. If no accepted provider
transport contract exists in the current source, report that exact architectural gap
instead of inventing `PREVIEW_MODEL_URL` or claiming MODEL integration complete.

#### Resubmission

Preserve the working Redis quota/replay/cancellation logic, authored prompt loading,
fixture query boundary and accepted Shared runner/interpreter composition. This is not
a request for broader refactoring or exhaustive tests. Add only targeted regressions
that demonstrate the corrected functional paths above, rerun this task's focused
integration/Redis checks plus repository typecheck/lint/build, update the Completion
Report with the actual Attempt 2 preparation/commits, set `status: review`, clear the
claim and stop. No dependent task is promoted or launched until COMMERCE-019 is
architect-accepted Complete.


### Readiness reconciliation after COMMERCE-013 Attempt 9 acceptance — 2026-09-21

Ready, Attempt 0 retained; executor/claimed_at null. COMMERCE-013 implementation
`4d52977` is architect accepted and all other explicit prerequisites are Complete.
No claim or automatic launch. Consume the actual backend via normal preparation.
Preserve native-basic monetary discount profiles as UNSUPPORTED while provider
rounding semantics are unproven; do not estimate savings or implement missing
provider semantics in this composition task. PostgreSQL adapter timeout diagnosis
and live infrastructure evidence remain separately developer-owned.
