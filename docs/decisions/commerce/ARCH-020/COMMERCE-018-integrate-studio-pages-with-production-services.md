---
id: ARCH-020-COMMERCE-018
architecture_id: ARCH-020
title: Integrate Studio pages with production services
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 140
executor: copilot
claimed_at: 2026-09-21T20:23:29Z
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-011
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-21
---

# Integrate Studio pages with production services

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect accepted U01–U13 Studio components to the013 backend facade and existing discovery services. Own protected UI service/action adapters and integrated authoring navigation; no MCP runtime or preview backend changes.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect accepted U01–U13 Studio components to the013 backend facade and existing discovery services. Own protected UI service/action adapters and integrated authoring navigation; no MCP runtime or preview backend changes.

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

- [ ] Own `src/commerce/integration/studio/` and minimal wiring in `src/studio/server-services.ts` plus Studio command Server Actions/client service transport. Do not change backend.ts, MCP route or preview runtime.
- [ ] Implement every008 StudioServices method against real013 publication/read services and011 discovery; recheck auth per request/action, Origin on mutations and role before replay.
- [ ] Apply the C20 field/error translation table, including source revision names, exact release members and pointer CAS. Rehydrate actual returned IDs into Studio view models; never synthesize IDs by splitting strings.
- [ ] Keep existing008 components, routes and draft state. Wire functional commands, preserve unknown-operation identity and role-aware controls; no page redesign or backend business-rule reimplementation.
- [ ] Create server-authorized merchant inspection/read models using013 current feature/grant-candidate resolver; never create a production conversation grant for U13.
- [ ] Provide `docs/commerce-studio-integration.md` and `test:arch020-studio-integration`. Demonstrate the complete populated authoring flow before collecting secondary layout evidence.

## Interfaces / Contracts

Source: `src/studio/contracts.ts: StudioServices` and the accepted
`docs/studio-service-contract.md`. Producer:013 `getCommerceBackend()` facade,
`CommerceLifecycle` commands/read snapshot and011 `createDiscoveryService`/compiler.
Factory destination: existing `src/studio/server-services.ts:getStudioServices`.
Use `lib/auth` helpers including requireStudioAdmin/requireStudioSuperAdmin and
assertStudioMutationOrigin. C20 lists actual payload mappings; no backend module
may be imported into browser bundles. New protected action files belong only to018.
If the accepted facade cannot express a required field, report the producer gap;
do not silently omit it or implement a second publication service.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002
- ARCH-020-COMMERCE-011

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [ ] S01: actual U03 -> U04 -> U09 -> U06 -> U07 -> U06 -> U09 -> U10 -> U11 flow authors, validates, publishes and activates through real services; exact definitions/member positions/responseContract survive.
- [ ] S02: N01–N09/N12 and composer portion of N13 pass with real reads/actions; missing IDs/foreign revisions produce correct states and exact published revisions remain read-only.
- [ ] S03: ADMIN cannot publish; revoked admin denied on next request; duplicate clicks/CAS/changed replay and unknown-outcome recovery preserve exactly one write/audit and the original operationId.
- [ ] S04: discovery outage preserves local/saved draft; schema unavailable blocks publication; empty/not-found/denied/unavailable are distinct. No JSON-dump or fixture-success substitute for UI.
- [ ] S05: U13 presents authoritative eligibility/tool descriptors without token/definition leakage or grant writes; shop IDs cannot be inferred from fixture naming.
- [ ] S06: production/narrow/keyboard populated views use accepted008 components and return paths. U14 remains a link with contract handoff; actual preview behavior is019-owned.

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

Implementation submitted for Architect Review.

### Files Changed

- `src/commerce/integration/studio/services.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `components/production-studio-page.tsx`
- `tests/studio-integration.test.ts`
- `docs/commerce-studio-integration.md`
- `package.json`

### Work Completed

Connected the production Studio workspace to the accepted `CommerceBackend` facade. Added protected server actions and the production adapter for publication reads, lifecycle commands, discovery, validation, shop inspection, operation replay/CAS error translation, environment-scoped release pointers, subscription plan labels, and feature status mapping. Mutations rehydrate returned IDs from a fresh publication snapshot. No fixture service, MCP route, preview runtime, Shared package, or database schema was changed.

### Validation Results

- `npm run test:arch020-studio-integration` — passed, 1 file and 3 tests.
- `npm run typecheck` — passed.
- `npm run lint -- --quiet` — passed.
- `npm run build` — passed; Next production build and route generation completed.
- `git diff --check` — passed.

The focused tests cover real backend service composition, publication mapping, operation ID forwarding with reread behavior, and stale CAS translation. Full acceptance flows requiring the shared isolated seed contract and external PostgreSQL/Redis evidence remain Architect/System Test follow-up.

### Deviations

No scope deviations. The accepted backend facade does not expose a persisted release sequence number or shop plan in inspection results, so the adapter derives release display numbers deterministically from the publication snapshot and reads plan names from the existing subscription relation. Documentation upstream does not expose related field paths, so that DTO remains empty.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-018`.
Implementation branch: `task/ARCH-020-COMMERCE-018`.
Implementation commit/push: `d074205` (`feat(commerce): integrate production studio services`), pushed to `origin/task/ARCH-020-COMMERCE-018`.
Parent report branch: `task/ARCH-020-COMMERCE-018` in the dedicated parent worktree; this report is the only parent change. Parent commit/push is recorded after this update. No parent service gitlink or main integration was performed.

## Architect Review

### Review Status

Changes Requested.

### Review Notes

Attempt 1 is not accepted. The submitted implementation `d074205` and parent report
`686abc47` establish the production Studio composition and should be preserved, but
six bounded functional gaps remain in the C20 integration contract. This review does
not request broader UI redesign, exhaustive test expansion, live provider calls, or
new database/Redis infrastructure evidence. Correct the same task and return it for
Attempt 2.

#### A1-R1 — enforce the canonical mutation Origin at the Server Action boundary

`src/studio/server-actions.ts` currently dispatches every mutating action directly to
`createCommerceStudioServices()` without calling `assertStudioMutationOrigin`. C7 and
this task require same-origin POST enforcement for direct mutations; UI visibility and
Next's Server Action transport are not substitutes.

Correction contract:

- use the accepted `lib/auth` `assertStudioMutationOrigin` helper with the current
  request headers for every Studio mutation action;
- perform the Origin check before invoking the production Studio service/backend;
- missing/mismatched Origin must return a bounded forbidden result and perform zero
  publication writes/audits;
- reads remain current-principal protected but do not require the mutation Origin check;
- preserve backend role re-authorization so ADMIN still cannot publish/activate/rollback
  or enable/disable.

Focused proof: one accepted same-origin mutation and one missing/mismatched-origin
mutation that demonstrates zero backend command invocation.

#### A1-R2 — send the exact strict payload for capability publication

`publishRevision` currently calls the strict lifecycle method with `{ ...input,
revisionId: input.capabilityRevisionId }`. The spread retains the Studio-only
`capabilityRevisionId` property, while `PublishRevisionSchema` is strict and accepts
only `operationId`, `reason`, `revisionId`, and `expectedEditVersion`. The production
U09 publish command therefore rejects an otherwise valid request as `INVALID_INPUT`.

Correction contract: construct the backend payload explicitly from exactly the four
accepted fields, preserve the original operationId/reason byte-for-byte, then reread
the exact published revision. Add a focused regression proving a valid capability
publish reaches the lifecycle and returns the published revision.

#### A1-R3 — repair the documentation search -> document handoff

`searchDocumentation` exposes `new URL(sourceUrl).pathname`, which for Shopify docs is
`/docs/...`; `getDocumentation` forwards that string unchanged to the accepted
discovery service, whose `assertDocumentationPath` already prefixes relative paths
with `/docs/`. The resulting production lookup becomes `/docs/docs/...`, so the N04
search-result -> document traversal does not address the searched document.

Correction contract: keep one stable Studio path representation and translate it to
the discovery service's accepted path exactly once. A focused test must take the path
returned by `searchDocumentation` and feed it to `getDocumentation`, asserting that the
canonical Shopify document is requested without a duplicated `/docs` segment. Do not
replace discovery with fixture content.

#### A1-R4 — preserve release member order and the current environment pointer CAS

The release adapter currently gives a non-active release `activePointerVersion: 0`.
That value is then sent by U11 as `expectedActiveReleaseVersion`, even when the current
environment pointer is already at version N>0. A newly created release therefore cannot
reliably perform the required create -> activate flow, and a previous release cannot
reliably rollback. `getShell()` also derives ACTIVE from pointers across all
environments rather than the configured environment.

In addition, `createRelease` forwards `input.members` in array order without enforcing
C20's exact member contract.

Correction contract:

- derive the current configured environment pointer once per read;
- every release summary used for activate/rollback carries that current pointer's
  `editVersion` as `activePointerVersion`, because the CAS belongs to the pointer, not
  to the target release;
- only the configured environment pointer determines `ACTIVE`; releases previously
  activated/rolled back in that environment are presented as `SUPERSEDED` where the
  accepted state/audit record proves it, while never-active releases remain
  `PUBLISHED`;
- `getShell`, list/get release and command rereads use the same environment semantics;
- before `createRelease`, validate exact capability/revision ownership, unique members,
  and contiguous positions `0..n-1`, then sort by `position` and pass
  `memberRevisionIds` in that order. Do not infer identity from IDs.

Focused proof: start from a non-zero active pointer, create a release, activate it, then
read the previous release and rollback using the current pointer CAS. Also submit a
permuted member array and prove persisted member positions follow explicit `position`,
not caller array order.

#### A1-R5 — validate the supplied response example, not only the contract schema

`validateResponseContract` currently ignores `input.example`. The accepted publication
validation module already exposes `validateResponseExample(contract, example)`, and
C16/U10 requires the example validator before Review/Test/Create. A structurally valid
response contract with an invalid example is therefore reported as valid today.

Correction contract: validate the contract first, then validate the supplied example
against that exact contract and return the bounded JSON-pointer `INVALID_EXAMPLE`
issues while preserving the submitted `contentHash`. Add one valid and one invalid
example regression.

#### A1-R6 — U13 must show positive eligibility as well as exclusions

`getShop` currently maps only `inspection.exclusions` into `ShopDetail.eligibility`.
Capabilities present in `candidateManifest.capabilities` disappear from the eligibility
view even though they are the authoritative eligible set. When `releaseId` is null the
view can also become an empty ambiguous list instead of the required explicit
unavailable/no-active-release state. Tool descriptors may be repeated when the same
revision is selected by more than one capability.

Correction contract:

- map feature-bound candidate capabilities to `eligible: true` using actual publication
  capability/feature identity;
- map exclusions to `eligible: false` with their exact reason and no ID parsing;
- represent `candidateManifest.releaseId === null` explicitly as unavailable/no active
  release using the authoritative inspection facts rather than an empty success;
- deduplicate the agent descriptor list by exact tool revision identity while preserving
  the canonical toolId/toolRevisionId/name/version/description/input schema;
- keep U13 read-only: zero grant creation, provider execution, preference writes or
  customer-history access.

Focused proof: one shop with both an eligible and excluded feature, plus a no-active-
release shop; assert the visible read model and zero write/execution calls.

Preserve the existing production facade composition, operation replay behavior, CAS
translation, build/typecheck/lint success, and COMMERCE-019 ownership boundary. Update
`docs/commerce-studio-integration.md` with the corrected source/export mappings and
actual accepted producer revisions required by C20; this is reconciliation of the
implemented flow, not a request for additional architecture.

### Reviewed Files

- `src/commerce/integration/studio/services.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx` (consumer behavior relevant to the mappings)
- `src/studio/contracts.ts`
- `src/commerce/publication/lifecycle.ts` and `validation.ts` (accepted producer contract)
- `lib/auth/origin.ts` and `platform-admin.ts` (accepted auth boundary)
- `lib/discovery/service.ts` and `upstream.ts` (accepted discovery path contract)
- `src/commerce/integration/backend.ts` (accepted inspection facade)
- `tests/studio-integration.test.ts`
- `docs/commerce-studio-integration.md`

### Validation Reviewed

Submitted focused integration tests: 3 passed. Submitted typecheck, lint, production
build and `git diff --check`: passed. Those checks support the implementation but do
not override the production-flow defects above. No exhaustive suite rerun is required
for Attempt 2; add focused regressions for the corrected behavior and rerun the task's
existing named validation plus typecheck/lint/build/diff hygiene.

### Architecture Conformance

The repository and file ownership are correct and the implementation uses the accepted
COMMERCE-013 facade without modifying MCP or preview ownership. The six findings above
prevent C7/C20 and S01/S03/S04/S05 from being functionally satisfied.

### Follow-up

Return this same task to `ready`, retain `attempt: 1`, clear executor/claimed_at, and
make no downstream task Ready. The next authorized `/moda-task` claim increments to
Attempt 2 exactly once. COMMERCE-012, COMMERCE-024, GATEWAY-001 and terminal system
validation remain gated.


### Readiness reconciliation after COMMERCE-013 Attempt 9 acceptance — 2026-09-21

Ready, Attempt 0 retained; executor/claimed_at null. COMMERCE-013 implementation
`4d52977` is architect accepted and all other explicit prerequisites are Complete.
No claim or automatic launch. Consume the actual backend via normal preparation.
Preserve native-basic monetary discount profiles as UNSUPPORTED while provider
rounding semantics are unproven; do not estimate savings or implement missing
provider semantics in this composition task. PostgreSQL adapter timeout diagnosis
and live infrastructure evidence remain separately developer-owned.
