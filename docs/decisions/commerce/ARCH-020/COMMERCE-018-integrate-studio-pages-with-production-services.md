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
status: review
priority: 140
executor: null
claimed_at: null
attempt: 5
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-011
  - ARCH-020-COMMERCE-033
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
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

- [x] Own `src/commerce/integration/studio/` and minimal wiring in `src/studio/server-services.ts` plus Studio command Server Actions/client service transport. Do not change backend.ts, MCP route or preview runtime.
- [x] Implement every008 StudioServices method against real013 publication/read services and011 discovery; recheck auth per request/action, Origin on mutations and role before replay.
- [x] Apply the C20 field/error translation table, including source revision names, exact release members and pointer CAS. Rehydrate actual returned IDs into Studio view models; never synthesize IDs by splitting strings. The real-adapter proof remains pending infrastructure.
- [x] Keep existing008 components, routes and draft state. Wire functional commands, preserve unknown-operation identity and role-aware controls; no page redesign or backend business-rule reimplementation.
- [x] Create server-authorized merchant inspection/read models using013 current feature/grant-candidate resolver; never create a production conversation grant for U13.
- [x] Provide `docs/commerce-studio-integration.md` and `test:arch020-studio-integration`. The C20 real-adapter command is also defined as `test:arch020-studio-integration:c20`; complete real-service execution remains developer-gated on disposable targets.

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

Attempt 5 implementation submitted for Architect Review.

### Files Changed

- `docs/commerce-studio-integration.md`
- `tests/studio-integration-c20.test.ts`
- `package.json`

### Work Completed

Consumed the accepted COMMERCE-033 `seedC20IntegrationFixture` helper directly from the real-adapter test. The test keeps the production backend, Prisma storage, lifecycle, inspection and Studio adapter real, substituting only discovery and query transports, and covers origin rejection, role authorization, replay/CAS, configured-environment activation/rollback, discovery outage, positive/excluded eligibility and read-only U13 behavior. Updated the mapping document with accepted producer revisions for COMMERCE-002, COMMERCE-008, COMMERCE-011 and COMMERCE-013, and added the documented `test:arch020-studio-integration:c20` script. No fixture service, MCP route, preview runtime, Shared package, or database schema was changed.

### Validation Results

Agent-executed:

- `npm run test:arch020-studio-integration` — passed, 1 file and 9 tests.
- `npx eslint tests/studio-integration-c20.test.ts` — passed.
- `git diff --check` — passed.
- `npm run lint` — blocked by one pre-existing error in `src/studio/connections/connections-ui.tsx` (`react-hooks/set-state-in-effect`) and eight warnings; no C20-test error.
- `npm run typecheck` — route type generation passed, then blocked on three unrelated baseline errors: two narrowing errors in `src/commerce/integration/backend/executors.ts` and one readonly-schema typing error in `tests/code-response-processor.test.ts`.
- `git diff --check` — passed.

C20 execution evidence:

- `npm run c20-fixture:reset` — not run; disposable C20 targets were not provisioned.
- `npm run test:arch020-studio-integration:c20` — resolved the new script and blocked before tests; exact error: `C20_FIXTURE_UNSAFE_DATABASE_TARGET: disposable C20 targets are required`.

PostgreSQL/Redis real-adapter evidence is therefore not claimed. No live provider, production credential, or non-task-owned infrastructure was used.

### Deviations

The required disposable PostgreSQL/Redis environment variables were unavailable, so the reset and real-adapter test were not treated as passes. This attempt adds the missing named C20 script and reconciles the existing evidence/mapping; no out-of-scope source was changed.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Architect/developer action is required to provide disposable C20 PostgreSQL/Redis targets and rerun the real-adapter path. Repository lint remains blocked by the unrelated connections UI error; typecheck did not complete in the available validation window.

### Architectural Concerns

The accepted COMMERCE-033 helper is present and consumed directly, and the named C20 script now exists. The remaining blocker is disposable infrastructure availability, not a substitute fixture or competing backend implementation.

### Git / VCS

Attempt-5 implementation and parent report commits/pushes are recorded after this report update. No parent service gitlink or main integration was performed.

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


### Attempt 2 Review — Changes Requested — 2026-09-21

**Current decision: Changes Requested; Ready, Attempt 2 retained; executor/claimed_at
null.** Reviewed the submitted implementation commit `4fb9f91` and parent report
commit `07d1ac14` from the exact supplied snapshot. The archive does not contain Git
metadata, so remote-head equality is recorded as submitted evidence rather than
independently asserted here. No next attempt is claimed, no downstream task is
promoted, and no main/gitlink integration is performed.

Attempt 2 correctly preserves the production facade and closes A1-R1, A1-R2, A1-R3
and A1-R5 at source level: Server Action mutations execute the canonical Origin check
before service construction, capability publication sends the strict lifecycle
payload, documentation search/document paths round-trip without `/docs/docs`, and
response examples are validated against the submitted contract while retaining the
content hash. The U13 no-active-release state and descriptor de-duplication are also
present. The following original C20/A1 requirements remain incomplete.

#### A2-R1 — release command rereads are still environment-agnostic

`services.ts` correctly calls `models(state, env())` for shell/list/get release reads,
but the shared `release(state,id)` helper still calls `models(state)` without the
configured environment. `createRelease`, `activateRelease`, `rollbackRelease` and
U13's active-release mapping all use that helper. Their returned `ReleaseSummary` can
therefore carry `activePointerVersion: 0` and can classify a release ACTIVE because a
different environment points to it. This is the same A1-R4 contract: command rereads
must use the same configured-environment semantics as list/get reads.

Correction contract:

- make every release summary used by Studio command rereads and U13 resolve through
  the configured environment; do not fall back to all pointers;
- after create, return the current environment pointer editVersion; after activate or
  rollback, reread the updated pointer and return its new editVersion/status;
- preserve PUBLISHED/ACTIVE/SUPERSEDED semantics from the configured environment only;
- add the exact non-zero-pointer create -> activate -> previous-release -> rollback
  regression requested in A1-R4, including a second environment pointer so cross-env
  activity cannot make a release ACTIVE.

#### A2-R2 — U13 still synthesizes feature identity for non-feature capabilities

The eligibility mapper currently uses `capability?.featureId ?? value.capabilityId`.
For BASE/RECOVERY_POLICY members (or a missing publication capability), that invents a
feature ID from the capability ID. A1-R6 required *feature-bound* candidate
capabilities to use their actual publication feature identity and prohibited inferred
identity.

Correction contract:

- include positive/negative feature eligibility rows only where the authoritative
  publication capability has a real non-null `featureId`;
- never substitute `capabilityId`, key text or parsed identifiers into `featureId`;
- keep BASE/RECOVERY_POLICY candidates available to descriptor construction where
  appropriate without misrepresenting them as feature eligibility rows;
- retain exact exclusion reasons and descriptor de-duplication by tool revision;
- add a focused fixture containing BASE plus FEATURE candidates and an excluded FEATURE
  capability, asserting only the real feature IDs appear and U13 remains read-only.

#### A2-R3 — task-owned C20 production-integration evidence is still missing

The named `tests/studio-integration.test.ts` suite injects a mocked
`CommerceBackend`, mocks `requireStudioAdmin`, and mocks the database client. Those
regressions are useful adapter tests, but C20 and this task's Validation require the
application services under integration to remain real, with only external
provider/model transports substituted. The Completion Report explicitly defers the
full acceptance flows to Architect/System Test; S01-S06 and C20 do not permit this
task's own integration evidence to be transferred to terminal system validation.

Correction contract:

- retain the eight focused adapter regressions; they need not be broadened arbitrarily;
- add/run the bounded C20 real-adapter integration path for this task using the
  accepted production publication/discovery/inspection composition and isolated test
  data; substitute only external provider/model transports;
- prove the task-owned success/rejection paths needed by S01/S03/S04/S05, including
  same-origin versus missing/mismatched-origin mutation with zero command invocation,
  SUPER_ADMIN/ADMIN authorization, one-write replay/CAS behavior, authoring through
  activation/rollback, discovery outage draft preservation and U13 read-only behavior;
- record actual PostgreSQL/Redis/container evidence only for infrastructure genuinely
  exercised by that path. A required check that is not run is not a pass;
- if the accepted COMMERCE-013 source lacks the C20 shared isolated seed/helper needed
  by 018, report that exact producer/export gap to `moda_architect` rather than
  inventing a competing backend helper or marking the real-adapter requirement passed.

#### A2-R4 — C20 producer mapping document is still incomplete

`docs/commerce-studio-integration.md` contains useful narrative mappings but does not
record the required accepted producer SHAs or the C20 table of source file/export,
input/output mapping, destination adapter, bounded error mapping and test ID. A1
explicitly required this reconciliation.

Correction contract: update that existing document from the actual accepted dependency
source consumed by the prepared worktree. Record exact accepted revisions for
COMMERCE-002/008/011/013 and map the concrete exports used by 018. Do not guess a SHA
or copy stale conversational values; use the prepared source/task records.

No UI redesign, new Shared/database contract, live Shopify call, paid model call or
COMMERCE-019 work is requested. Preserve the passing typecheck/lint/build and the
source corrections already made. Before the next Review submission, reconcile the
implementing-agent-owned Work Items/Acceptance Criteria/Validation checkboxes and
Completion Report to the evidence actually executed; do not mark deferred S01-S06
requirements complete.

### Reviewed Files — Attempt 2

- `src/commerce/integration/studio/services.ts`
- `src/studio/server-actions.ts`
- `src/studio/server-services.ts`
- `components/production-studio-page.tsx`
- `components/studio-workspace.tsx`
- `src/studio/contracts.ts`
- `src/commerce/integration/backend.ts`
- `lib/auth/origin.ts` / `lib/auth/errors.ts`
- `tests/studio-integration.test.ts`
- `tests/backend-integration.test.ts` / `tests/backend-postgres-rehearsal.test.ts`
- `docs/commerce-studio-integration.md`
- C20 in `docs/architecture/ARCH-020-implementation-contracts.md`

### Validation Reviewed — Attempt 2

Submitted evidence: 8 focused Studio integration tests passed; typecheck, quiet lint,
production build and `git diff --check` passed. The source review confirms the four
Attempt-1 corrections listed above, but the current tests do not exercise the
environment-aware mutation reread, non-feature U13 identity case, Server Action
Origin side effects, or the required real-application-service C20 path. No exhaustive
full-suite rerun is requested.

### Architecture Conformance — Attempt 2

Repository/file ownership and the COMMERCE-013 facade boundary remain correct; no MCP
or preview ownership drift was found. A2-R1/A2-R2 prevent A1-R4/A1-R6 and S01/S05
from being complete, while A2-R3/A2-R4 leave the explicit C20 integration-evidence
and mapping contract incomplete.

### Follow-up — Attempt 2

Return this same task to its configured `/moda-task` correction path. Preserve
`attempt: 2`; the next authorized claim increments once to Attempt 3.
COMMERCE-012, COMMERCE-024, GATEWAY-001 and terminal system validation remain gated.
Do not start or promote a dependent task from this review.


### Attempt 3 Review — Blocked with producer correction materialised — 2026-09-21

**Current decision: Blocked; Attempt 3 retained; executor/claimed_at null.** Reviewed
submitted implementation `3de9940` and parent report `225ed421` from the exact supplied
snapshot. The archive has no Git metadata, so those heads are recorded as submitted
evidence rather than independently asserted.

Attempt 3 closes A2-R1 and A2-R2: release mutation rereads now resolve through the
configured environment and preserve the actual pointer CAS version/status across
activate/rollback; U13 no longer substitutes capability IDs for absent feature IDs.
The focused cross-environment and BASE+FEATURE regressions are present. Submitted
9 focused tests, typecheck, lint, build and `git diff --check` are retained as passing.

A2-R3 cannot be completed inside COMMERCE-018 because C20 assigns the missing
real-integration seed/reset boundary to the backend producer. The accepted
COMMERCE-013 source exposes `getCommerceBackend()`, `createCommerceBackend()`,
`createFixtureExecution(...)` and `resetCommerceBackendForTests()`, but not the C20
isolated persistent seed/reset helper required by both 018 and 019. COMMERCE-018
correctly reported that gap instead of inventing another publication backend or local
fixture graph.

The architect therefore materialises **ARCH-020-COMMERCE-033** in this review:
`docs/decisions/commerce/ARCH-020/COMMERCE-033-provide-c20-isolated-integration-fixture.md`.
It is Ready, Attempt 0, claims null, depends only on accepted COMMERCE-013, and owns
one deterministic test-only fixture boundary. Its task file is the complete execution
contract; no agent is expected to infer fixture contents, reset behavior, target safety,
file scope, exports or validation from this review prose.

COMMERCE-018 now explicitly depends on COMMERCE-033 and remains Blocked until 033 is
architect-accepted Complete. Do not reopen or modify accepted COMMERCE-013 for this
correction.

One 018-owned item remains after unblocking: the C20 producer mapping must record the
accepted producer heads, not historical pre-acceptance revisions. At minimum reconcile:

- COMMERCE-008 accepted head: `8ba5e423112771defe533438ea99965357271526`;
- COMMERCE-011 accepted head: `11764125825a119b5dd7aa8c8adf88c0341f75f8`;
- COMMERCE-013 accepted head: `4d529773fde26599027aef2d76fbd70bc974b352`.

After COMMERCE-033 is Complete, `moda_architect` may transition this task
`blocked -> ready` without changing `attempt: 3`. The next authorised `/moda-task`
claim becomes Attempt 4. Attempt 4 must consume the 033 helper directly, run the C20
real PostgreSQL/Redis integration path for S01/S03/S04/S05, correct the producer
mapping, rerun the existing named repository checks, return to Review and stop.

No UI redesign, new schema, Shared contract, live provider call or COMMERCE-019
implementation is authorised by this review.
