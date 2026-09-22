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
status: complete
priority: 140
executor: null
claimed_at: null
attempt: 8
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-002
  - ARCH-020-COMMERCE-011
  - ARCH-020-COMMERCE-035
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
- [x] Apply the C20 field/error translation table, including source revision names, exact release members and pointer CAS. Rehydrate actual returned IDs into Studio view models; never synthesize IDs by splitting strings. The real-adapter proof passed against the approved disposable PostgreSQL/Redis targets in Attempt 8.
- [x] Keep existing008 components, routes and draft state. Wire functional commands, preserve unknown-operation identity and role-aware controls; no page redesign or backend business-rule reimplementation.
- [x] Create server-authorized merchant inspection/read models using013 current feature/grant-candidate resolver; never create a production conversation grant for U13.
- [x] Provide `docs/commerce-studio-integration.md` and `test:arch020-studio-integration`. The C20 real-adapter command is also defined as `test:arch020-studio-integration:c20`; the real-service proof passed against approved disposable targets in Attempt 8.

## Interfaces / Contracts

Source: `src/studio/contracts.ts: StudioServices` and the accepted
`docs/studio-service-contract.md`. Producer:013 `getCommerceBackend()` facade,
`CommerceLifecycle` commands/read snapshot and011 `createDiscoveryService`/compiler.
Factory destination: existing `src/studio/server-services.ts:getStudioServices`.
Use `lib/auth` helpers including requireStudioAdmin/requireStudioSuperAdmin and
assertStudioMutationOrigin. C20 lists actual payload mappings; no backend module
may be imported into browser bundles.

C20 test-only fixture producer: `ARCH-020-COMMERCE-035`, accepted Complete at
Attempt 4, export `src/commerce/integration/backend/c20-test-fixture.ts:
seedC20IntegrationFixture`. `ARCH-020-COMMERCE-033` is the preview OpenAI/Groq
model-provider task and is not the fixture dependency for this Studio integration
task. New protected action files belong only to018.
If the accepted facade cannot express a required field, report the producer gap;
do not silently omit it or implement a second publication service.

## Dependencies

- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-002
- ARCH-020-COMMERCE-011
- ARCH-020-COMMERCE-035

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [x] S01: actual U03 -> U04 -> U09 -> U06 -> U07 -> U06 -> U09 -> U10 -> U11 flow authors, validates, publishes and activates through real services; exact definitions/member positions/responseContract survive.
- [x] S02: N01–N09/N12 and composer portion of N13 pass with real reads/actions; missing IDs/foreign revisions produce correct states and exact published revisions remain read-only.
- [x] S03: ADMIN cannot publish; revoked admin denied on next request; duplicate clicks/CAS/changed replay and unknown-outcome recovery preserve exactly one write/audit and the original operationId.
- [x] S04: discovery outage preserves local/saved draft; schema unavailable blocks publication; empty/not-found/denied/unavailable are distinct. No JSON-dump or fixture-success substitute for UI.
- [x] S05: U13 presents authoritative eligibility/tool descriptors without token/definition leakage or grant writes; shop IDs cannot be inferred from fixture naming.
- [x] S06: production/narrow/keyboard populated views use accepted008 components and return paths. U14 remains a link with contract handoff; actual preview behavior is019-owned.

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

Attempt 8 implementation submitted for Architect Review.

### Files Changed

- `docs/commerce-studio-integration.md`
- `tests/studio-integration-c20.test.ts`
- `package.json`
- `src/commerce/integration/studio/services.ts`

### Work Completed

Consumed the accepted COMMERCE-035 `seedC20IntegrationFixture` helper directly from the real-adapter test. Added the required fifth C20 scenario covering real Studio tool/capability validation, draft creation, publication, response validation, exact-position release creation, activation, rollback and one-audit-per-operation assertions. Fixed two Studio adapter payload mappings so absent optional source revision IDs are omitted before lifecycle operation hashing. No fixture service, MCP route, preview runtime, Shared package, or database schema was changed.

### Validation Results

Agent-executed:

- `npm run test:arch020-studio-integration` — passed, 1 file and 9 tests.
- `npm run c20-fixture:reset` — passed against the approved disposable PostgreSQL/Redis targets.
- `npm run test:arch020-studio-integration:c20` — passed, 1 file and 5 tests.
- `npx eslint tests/studio-integration-c20.test.ts src/commerce/integration/studio/services.ts` — passed with one pre-existing unused `ShopSummary` warning.
- `git diff --check` — passed.
- `npm run lint` — blocked by the known unrelated `src/studio/connections/connections-ui.tsx` `react-hooks/set-state-in-effect` error and existing warnings; no task-owned error.
- `npm run typecheck` — route type generation passed, then retained the known unrelated errors in connections typing, backend executor narrowing, CodeMirror dependencies, and code-response test schema typing.
- `npm run build` — retained the known repository baseline failure; no task-owned diagnostic was implicated.

No live provider, production credential, or non-task-owned infrastructure was used.

### Deviations

The real C20 run required complete ephemeral service configuration in addition to the disposable target variables; the run was then reset and passed. The final authored release is correctly reported as `SUPERSEDED` after rollback under the existing publication-state model.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Repository lint, typecheck and build remain blocked by unrelated baseline diagnostics documented above.

### Architectural Concerns

The accepted COMMERCE-033 helper is present and consumed directly, and the named C20 script now exists. The remaining blocker is disposable infrastructure availability, not a substitute fixture or competing backend implementation.

### Git / VCS

Attempt-5 implementation and parent report commits/pushes are recorded after this report update. No parent service gitlink or main integration was performed.

## Attempt 6 Completion Report

### Status

Attempt 6 implementation revalidated and submitted for Architect Review.

### Scope and Evidence

The implementation worktree was prepared and claimed for Attempt 6 with claim
`00a92812b9b887c247a1ecbb780046391d2a8a63`, dependency gate passed, and accepted
COMMERCE-033 fixture support present. The current implementation head was
`d96d74192da3175c9bce8d1e1497e2026ba3dfc6`; no new source edit was required in
this attempt because the A2-R1/A2-R2 corrections are present and the existing
focused regressions cover configured-environment pointer rereads, explicit member
ordering, feature-only eligibility identity, excluded features, and no-active-
release handling. The mapping document records the accepted producer revisions
and the C20 source/export, input/output, destination adapter, bounded errors, and
test coverage.

### Validation Results

Agent-executed:

- `npm run test:arch020-studio-integration` — passed, 1 file and 9 tests.
- `npm run lint` — blocked by the pre-existing `react-hooks/set-state-in-effect`
  error in `src/studio/connections/connections-ui.tsx`; eight warnings were also
  reported, including the existing unused `ShopSummary` warning in the adapter.
- `npm run typecheck` — blocked by 15 existing errors in connection lifecycle,
  backend executor narrowing, CodeMirror dependencies/types, and the response
  processor test; no Studio integration adapter error was reported.
- `npm run build` — code-runtime packaging, smoke test, Prisma generation, and
  Next.js production compilation passed; the command then failed in its
  TypeScript phase on the same unrelated baseline errors, so the build is not
  claimed as a pass.
- `git diff --check` — no whitespace errors.

C20 execution evidence:

- `npm run c20-fixture:reset` — not run because disposable C20 PostgreSQL/Redis
  targets were not provisioned.
- `npm run test:arch020-studio-integration:c20` — blocked before tests with the
  exact error `C20_FIXTURE_UNSAFE_DATABASE_TARGET: disposable C20 targets are
  required`; no C20 tests are claimed as passed.

No live provider, production credential, non-task-owned infrastructure, fixture
service, MCP route, preview runtime, Shared package, or database schema was
changed.

### Deviations and Unresolved Validation

Disposable C20 infrastructure remains developer-gated and must be provisioned
before the real Prisma/storage/lifecycle/inspection/Studio-adapter proof can run.
Repository lint, typecheck, and build remain blocked by unrelated baseline issues
described above. These are recorded as validation blockers rather than treated as
passes.

### Git / VCS

No implementation commit was needed in Attempt 6 because the claimed branch was
clean after revalidation. This parent report is the only Attempt 6 change and is
submitted at Architect Review; no enabled task was started.

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

## Architect Review — Attempt 6 autonomous C20 validation unblock — 2026-09-22

### Review Status

Changes Requested — validation-only resumption.

`ARCH-020-COMMERCE-018` is returned to **Ready**, Attempt 6 retained, with
`executor: null` and `claimed_at: null`. The next authorised `/moda-task` claim
becomes Attempt 7.

No Studio source correction is currently requested. The submitted Attempt 6 source
already contains the previously requested production-adapter corrections and the
named real-adapter test. The remaining acceptance gate is execution of that C20 path
against disposable PostgreSQL and Redis.

The exact submitted parent handoff is
`860107f5ea76e2cc480421c830ac0d43f88d022a`; the remote parent task branch matched
that commit at review time. The submitted implementation head is
`d96d74192da3175c9bce8d1e1497e2026ba3dfc6`. The Commerce implementation remote is
not readable through the current review connector, so source review is grounded in
the exact submitted archive.

### Dependency reconciliation

Historical COMMERCE-018 review text referred to the C20 fixture correction as
`ARCH-020-COMMERCE-033`. That identifier is now canonically the accepted OpenAI/Groq
preview-model transport.

The accepted C20 isolated fixture producer is:

```text
ARCH-020-COMMERCE-035
Provide the C20 isolated integration fixture boundary
status: complete
accepted: Attempt 4
implementation: 9a0120b
export: seedC20IntegrationFixture
```

This review therefore replaces COMMERCE-018's stale fixture dependency on
COMMERCE-033 with COMMERCE-035. The source already imports the canonical
`src/commerce/integration/backend/c20-test-fixture.ts` helper produced by
COMMERCE-035; do not copy or reimplement that fixture.

### Explicit validation-policy override for Attempt 7

For **ARCH-020-COMMERCE-018 Attempt 7 only**, `moda_architect` explicitly authorises
the repository agent to create, use and destroy its own local Docker PostgreSQL and
Redis containers for the required C20 real-adapter validation.

The agent MUST NOT wait for developer-supplied
`COMMERCE_TEST_DATABASE_URL` / `COMMERCE_TEST_REDIS_URL` when a usable local Docker
engine exists.

This authorisation is limited to:

- local Docker through a Unix-socket Docker context;
- exactly two task-owned disposable containers;
- loopback-only dynamically allocated host ports;
- no persistent Docker volumes;
- no shared/deployed PostgreSQL or Redis;
- no Render, managed database, managed Redis, production or normal developer
  database;
- no `FLUSHALL` / `FLUSHDB`;
- cleanup only of resources whose run label exactly matches this invocation.

Do not inspect `.env` files, deployment secrets or developer configuration to find
infrastructure.

### Exact disposable target contract

Use the already accepted local C20 image versions:

```text
PostgreSQL: postgres:16.4-alpine
Redis:      redis:7.4.0-alpine
```

Use exactly:

```text
database name:     arch020_c20_commerce018_a7
Redis namespace:   arch020:c20:commerce018-a7
Postgres user:     fixture
Postgres password: fixture-only
environment:       test
label key:         moda.arch020.c20.run
```

The password is synthetic local fixture data, not a platform secret.

No fixed host port is permitted. Docker must allocate loopback ports dynamically.

### Exact provisioning and validation procedure

Run this from the dedicated COMMERCE-018 implementation worktree:

```bash
set -euo pipefail

command -v docker >/dev/null 2>&1 || {
  echo "C20_LOCAL_DOCKER_UNAVAILABLE: docker command not found" >&2
  exit 1
}

DOCKER_ENDPOINT="$(
  docker context inspect --format '{{.Endpoints.docker.Host}}' 2>/dev/null
)"

case "$DOCKER_ENDPOINT" in
  unix://*) ;;
  *)
    echo "C20_LOCAL_DOCKER_UNAVAILABLE: local Unix-socket Docker context required" >&2
    exit 1
    ;;
esac

docker version --format '{{.Server.Version}}' >/dev/null

RUN_ID="arch020-c20-commerce018-a7-$$"
LABEL_KEY="moda.arch020.c20.run"
PG_CONTAINER="${RUN_ID}-postgres"
REDIS_CONTAINER="${RUN_ID}-redis"

DB_NAME="arch020_c20_commerce018_a7"
PG_USER="fixture"
PG_PASSWORD="fixture-only"
REDIS_NAMESPACE="arch020:c20:commerce018-a7"

cleanup_c20_targets() {
  for container in "$PG_CONTAINER" "$REDIS_CONTAINER"; do
    if docker container inspect "$container" >/dev/null 2>&1; then
      owner="$(
        docker container inspect \
          --format '{{index .Config.Labels "moda.arch020.c20.run"}}' \
          "$container"
      )"
      if [ "$owner" = "$RUN_ID" ]; then
        docker rm -f -v "$container" >/dev/null
      else
        echo "C20 cleanup ownership mismatch for $container" >&2
        return 1
      fi
    fi
  done
}

trap cleanup_c20_targets EXIT INT TERM

docker pull postgres:16.4-alpine >/dev/null
docker pull redis:7.4.0-alpine >/dev/null

docker run -d \
  --name "$PG_CONTAINER" \
  --label "${LABEL_KEY}=${RUN_ID}" \
  --publish 127.0.0.1::5432 \
  --tmpfs /var/lib/postgresql/data \
  --env "POSTGRES_USER=${PG_USER}" \
  --env "POSTGRES_PASSWORD=${PG_PASSWORD}" \
  --env "POSTGRES_DB=${DB_NAME}" \
  postgres:16.4-alpine >/dev/null

docker run -d \
  --name "$REDIS_CONTAINER" \
  --label "${LABEL_KEY}=${RUN_ID}" \
  --publish 127.0.0.1::6379 \
  --tmpfs /data \
  redis:7.4.0-alpine \
  redis-server --save "" --appendonly no >/dev/null

pg_ready=0
for _ in $(seq 1 100); do
  if docker exec "$PG_CONTAINER" \
      pg_isready -h 127.0.0.1 -U "$PG_USER" -d "$DB_NAME" >/dev/null 2>&1; then
    pg_ready=1
    break
  fi
  sleep 0.2
done
[ "$pg_ready" -eq 1 ] || {
  echo "C20_LOCAL_POSTGRES_UNAVAILABLE: disposable PostgreSQL did not become ready" >&2
  exit 1
}

redis_ready=0
for _ in $(seq 1 100); do
  if [ "$(docker exec "$REDIS_CONTAINER" redis-cli ping 2>/dev/null || true)" = "PONG" ]; then
    redis_ready=1
    break
  fi
  sleep 0.2
done
[ "$redis_ready" -eq 1 ] || {
  echo "C20_LOCAL_REDIS_UNAVAILABLE: disposable Redis did not become ready" >&2
  exit 1
}

PG_BIND="$(docker port "$PG_CONTAINER" 5432/tcp)"
REDIS_BIND="$(docker port "$REDIS_CONTAINER" 6379/tcp)"

case "$PG_BIND" in
  127.0.0.1:*) ;;
  *) echo "C20_LOCAL_POSTGRES_UNSAFE_BIND: expected loopback binding" >&2; exit 1 ;;
esac

case "$REDIS_BIND" in
  127.0.0.1:*) ;;
  *) echo "C20_LOCAL_REDIS_UNSAFE_BIND: expected loopback binding" >&2; exit 1 ;;
esac

PG_PORT="${PG_BIND##*:}"
REDIS_PORT="${REDIS_BIND##*:}"

export COMMERCE_TEST_DATABASE_URL="postgresql://${PG_USER}:${PG_PASSWORD}@127.0.0.1:${PG_PORT}/${DB_NAME}"
export DATABASE_URL="$COMMERCE_TEST_DATABASE_URL"
export COMMERCE_TEST_REDIS_URL="redis://127.0.0.1:${REDIS_PORT}"
export COMMERCE_C20_REDIS_NAMESPACE="$REDIS_NAMESPACE"
export DEPLOYMENT_ENVIRONMENT_NAME="test"

# Do not echo the full URLs or fixture password.
echo "C20 Studio targets ready: database=${DB_NAME} namespace=${REDIS_NAMESPACE}"

npm run c20-fixture:reset
npm run test:arch020-studio-integration:c20
npm run test:arch020-studio-integration

npm run lint
npm run typecheck
npm run build
git diff --check
```

The `EXIT` trap owns cleanup. Do not manually remove any container whose
`moda.arch020.c20.run` label does not equal this invocation's `RUN_ID`.

### Required C20 evidence

The real-adapter command must exercise the actual accepted application components:
Prisma storage, publication lifecycle, inspection and the COMMERCE-018 Studio
adapter, consuming COMMERCE-035's `seedC20IntegrationFixture`.

Only external discovery/query transports may remain controlled test doubles.

Record the observed results for the task-owned C20 scenarios, including:

- missing/mismatched Origin rejects before mutation;
- ADMIN remains unable to publish;
- replay/CAS preserves one business write/audit for one operation ID;
- configured-environment activation and rollback use the current pointer CAS;
- discovery outage returns bounded unavailable while publication/draft state remains
  intact;
- U13 exposes real positive/excluded feature eligibility and remains read-only;
- the task consumes the exact COMMERCE-035 fixture graph rather than a local copy.

The existing focused 9-test suite remains useful adapter evidence but does not replace
the real C20 path.

### Required execution evidence

Record in the Attempt 7 Completion Report:

- Docker context endpoint class (`unix://...`; do not record unrelated environment
  values);
- Docker server version;
- `postgres:16.4-alpine` and `redis:7.4.0-alpine` image RepoDigests;
- run-scoped container names;
- database name and Redis namespace, but not the full URLs/password;
- PostgreSQL and Redis health success;
- `npm run c20-fixture:reset` result;
- `npm run test:arch020-studio-integration:c20` exact result/scenario count;
- `npm run test:arch020-studio-integration` exact result;
- cleanup success for both labelled containers.

### Known repository baseline handling

Attempt 6 recorded repository-wide failures outside the Studio integration change:

- lint: the existing `src/studio/connections/connections-ui.tsx`
  `react-hooks/set-state-in-effect` diagnostic plus existing warnings;
- typecheck/build: existing connection-lifecycle, backend-executor, CodeMirror and
  response-processor diagnostics.

Attempt 7 must rerun the commands because the task requires them. If the failures are
materially identical to the already recorded baseline and no COMMERCE-018-owned file
is implicated, record them accurately and **continue to `review` once both the C20
reset/proof and focused Studio suite pass**.

Do not return COMMERCE-018 to `blocked` merely because those unchanged unrelated
diagnostics remain.

### Failure handling

Return to `blocked` only if:

1. Docker command/server is unavailable;
2. the selected Docker context is not local `unix://`;
3. an approved task-owned PostgreSQL/Redis container cannot start or become healthy;
4. cleanup ownership cannot be proven;
5. the real C20 path exposes a genuine COMMERCE-018-owned defect that cannot be
   corrected within this task; or
6. the real C20 path demonstrates a regression in the already accepted
   COMMERCE-035 fixture producer. In that case do not modify COMMERCE-035 from this
   task; record the exact producer reproduction for `moda_architect`.

If the real path exposes a bounded COMMERCE-018 adapter defect, fix only that defect,
rerun the affected proof and report it.

**Do not ask the developer for PostgreSQL/Redis URLs as the next step.**

### Stop condition

When the C20 reset/proof and focused Studio suite pass:

1. reconcile S01-S06 and Work Items truthfully from the combined evidence;
2. update the Completion Report with the real-client evidence;
3. set `status: review`;
4. set `executor: null`;
5. set `claimed_at: null`;
6. push both mirrored task branches;
7. return control to `moda_architect`;
8. **STOP**.

Do not begin COMMERCE-012, COMMERCE-024, GATEWAY-001 or any system-test task.

## Attempt 7 Completion Report

### Status

Attempt 7 C20 validation completed and submitted for Architect Review. The bounded
real-adapter proof and focused Studio suite pass. Full S01-S06 assembled-flow
acceptance remains architect/system-test gated and is not claimed here.

### Files Changed

- `tests/studio-integration-c20.test.ts`

The test now supplies a synthetic valid assertion key for real backend construction,
uses the accepted `LifecycleError('FORBIDDEN', ...)` authorization contract, keeps
ADMIN publication denial separate from SUPER_ADMIN replay/CAS coverage, asserts the
audit operation row identity, and restores the intentionally toggled capability
before the later read-only U13 eligibility proof. No production adapter, backend,
MCP route, preview runtime, Shared package, database schema, or COMMERCE-035 fixture
source was changed.

### Validation Results

Agent-executed:

- `npm run c20-fixture:reset` — passed against the disposable target.
- `npm run test:arch020-studio-integration:c20` — passed, 1 file and 4 tests.
- `npm run test:arch020-studio-integration` — passed, 1 file and 9 tests.
- `npx eslint tests/studio-integration-c20.test.ts` — passed.
- `git diff --check` — passed.

The real C20 scenarios proved same-origin/mismatched-origin rejection before
mutation, ADMIN publication denial, one-write replay/CAS, configured-environment
activation/rollback, discovery outage handling with preserved state, positive and
excluded U13 eligibility, descriptor reads, and zero U13 writes/execution. The test
consumed `seedC20IntegrationFixture` from COMMERCE-035 directly.

### Disposable C20 Evidence

- Docker context: local `unix://` endpoint; server `29.5.2`.
- PostgreSQL image: `postgres:16.4-alpine`, RepoDigest
  `postgres@sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c`.
- Redis image: `redis:7.4.0-alpine`, RepoDigest
  `redis@sha256:c35af3bbcef51a62c8bae5a9a563c6f1b60d7ebaea4cb5a3ccbcc157580ae098`.
- Run containers: `arch020-c20-commerce018-a7-final-postgres` and
  `arch020-c20-commerce018-a7-final-redis`.
- Database: `arch020_c20_commerce018_a7`.
- Redis namespace: `arch020:c20:commerce018-a7`.
- PostgreSQL health: passed; Redis health: passed.
- Cleanup: passed for both containers after ownership verification.

Repository-wide checks were rerun as required. `npm run lint` remains blocked by
the existing Connections UI `react-hooks/set-state-in-effect` error and warnings;
`npm run typecheck` and `npm run build` remain blocked by the previously recorded
connection-lifecycle, backend-executor, CodeMirror, and response-processor baseline
diagnostics. The Studio integration files and changed C20 test introduced no
reported diagnostics.

### Deviations

No scope deviation. Disposable infrastructure used only the explicitly authorised
local Docker Unix context, two loopback-only tmpfs containers, synthetic fixture
credentials, and no persistent volumes or deployed services.

### Git / VCS

Implementation changes are on `task/ARCH-020-COMMERCE-018` in the dedicated
implementation worktree. This parent report is on the mirrored parent task branch;
both branches are to be committed and pushed for Architect Review. No enabled task,
main merge, service gitlink update, or deployment was performed.

## Architect Review — Attempt 7 — 2026-09-22

### Review Status

Changes Requested

### Review Notes

Attempt 7 successfully closes the validation-only infrastructure gate from the prior
Architect Review:

```text
npm run c20-fixture:reset
  PASS

npm run test:arch020-studio-integration:c20
  PASS — 1 file / 4 tests

npm run test:arch020-studio-integration
  PASS — 1 file / 9 tests

changed-test ESLint
  PASS

git diff --check
  PASS

disposable PostgreSQL/Redis
  health PASS
  cleanup PASS
```

The submitted Docker evidence is sufficient and is accepted. Do not repeat the
Docker/provisioning work merely to manufacture more infrastructure evidence unless
the Attempt-8 source change requires the C20 suite to be rerun, as specified below.

The production Studio adapter corrections from the previous attempts remain accepted
in substance. No new production-source defect was found during this review.

One task-owned functional acceptance gap remains: **S01 / C20 I01 full authoring
traversal is still not exercised against the real production services.**

The current real C20 suite starts from COMMERCE-035's already-published tool,
capabilities and releases. Its "authors through configured-environment activation and
rollback" test only rolls back to the pre-seeded inactive release and reactivates the
pre-seeded active release. It does not call:

```text
createTool
createToolDraft
publishToolRevision
createCapability
createDraft
publishRevision
createRelease
```

through `createCommerceStudioServices(...)`.

C20 explicitly assigns former I01 `full authoring traversal` to COMMERCE-018 S01.
The task's own S01 requires an actual author/validate/publish/release/activate flow
through real services. The Completion Report correctly says full S01-S06 assembled
acceptance is not claimed; therefore the task cannot yet move to Complete.

This is not a request for exhaustive testing or another UI redesign. Attempt 8 is a
single bounded real-adapter traversal.

### A7-R1 — add one real S01 authoring traversal

Primary file:

```text
tests/studio-integration-c20.test.ts
```

Do not change production source unless this exact real traversal exposes a genuine
COMMERCE-018-owned adapter defect.

Keep the existing four C20 tests. Add one fifth test with exactly this title:

```text
authors validates publishes releases activates and rolls back through real Studio services
```

Set:

```ts
authState.principal = principal(fixture.admins.superAdmin);
```

Use this exact operation/reason prefix:

```text
reason:
  "ARCH-020 COMMERCE-018 S01 real authoring proof"

operation IDs:
  c20-studio-s01:create-tool
  c20-studio-s01:create-tool-draft
  c20-studio-s01:publish-tool
  c20-studio-s01:create-capability
  c20-studio-s01:create-capability-draft
  c20-studio-s01:publish-capability
  c20-studio-s01:create-release
  c20-studio-s01:activate-release
  c20-studio-s01:rollback-release
```

#### 1. Author and validate a new tool

Create this exact tool definition in the test:

```ts
const authoredToolDefinition = {
  name: 'c20_studio_authored_lookup',
  definitionVersion: '1.0.0',
  description: 'C20 Studio authored catalogue lookup.',
  inputSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false,
  },
  execution: {
    kind: 'SHOPIFY_STOREFRONT_QUERY',
    executorVersion: '1.0.0',
    apiVersion: '2026-07',
    schemaHash:
      '54b992d0bc6ceffd030f9d4de69be944159cc9686e1e030d97b8293a5fe059bc',
    document:
      'query C20StudioCatalog { products(first: 1) { nodes { id } } }',
    operationName: 'C20StudioCatalog',
    variables: {},
    resultPath: 'products.nodes',
  },
  responseTemplate: {
    kind: 'text',
    text: '{{result.value}}',
    unavailable: 'C20 Studio catalogue data is unavailable.',
  },
} as const;
```

Call:

```ts
services.validateToolDefinition({
  definition: authoredToolDefinition,
})
```

and require:

```text
kind: ok
value.valid: true
value.errors: []
```

Then call `services.createTool(...)` with:

```text
name:        c20_studio_authored_lookup
displayName: C20 Studio Authored Lookup
description: C20 Studio authored lookup.
```

Use the returned real `toolId`; do not infer or construct an ID.

Call `services.createToolDraft(...)` using the exact returned tool ID and
`authoredToolDefinition`. Require a real DRAFT revision and capture its returned
`id` and `editVersion`.

Call `services.publishToolRevision(...)` with that exact revision ID/editVersion.
Require `status: PUBLISHED`. Use the returned exact `toolId` /
`toolRevisionId` for the capability binding below.

#### 2. Author a FEATURE capability and prove draft retention during discovery outage

Call `services.createCapability(...)` with:

```text
key:         c20_studio_authored_feature
displayName: C20 Studio Authored Feature
description: C20 Studio authored feature.
type:        FEATURE
featureId:   fixture.billing.featureId
```

Use the returned real capability ID.

Call `services.createDraft(...)` with:

```ts
promptTemplate:
  'Use the C20 Studio authored lookup for fixture catalogue facts.',
configuration: {},
contractVersion: 'commerce.v1',
toolBindings: [{
  toolId: <exact created tool ID>,
  toolRevisionId: <exact published tool revision ID>,
}]
```

Capture the returned DRAFT revision exactly.

Before publishing that capability revision, execute the already configured unavailable
discovery path:

```ts
const discovery = await services.searchDocumentation({ query: 'product' });
expect(discovery.kind).toBe('unavailable');
```

Then reread:

```ts
services.getCapability(
  <exact created capability ID>,
  <exact created draft revision ID>,
)
```

and prove the draft still contains exactly the authored:

```text
promptTemplate
configuration
contractVersion
toolBindings
editVersion
```

This is the S04 saved-draft preservation proof. Do not infer preservation merely from
audit counts.

Then call `services.publishRevision(...)` with the exact draft revision ID and current
editVersion and require a PUBLISHED revision.

#### 3. Validate the response contract before release creation

Use exactly:

```ts
const authoredResponseContract = {
  version: 'response.v1',
  instructions: 'Answer only from C20 Studio authoring facts.',
  detailsSchema: {
    type: 'object',
    properties: {},
    additionalProperties: false,
  },
} as const;
```

Call:

```ts
services.validateResponseContract({
  responseContract: authoredResponseContract,
  example: {},
  contentHash: 'c20-studio-s01-response-contract',
})
```

and require:

```text
kind: ok
value.valid: true
value.errors: []
value.contentHash: c20-studio-s01-response-contract
```

#### 4. Create the release with exact member order

Create the release through `services.createRelease(...)` with:

```text
position 0:
  capabilityId:
    fixture.capabilities.base.capabilityId
  capabilityRevisionId:
    fixture.capabilities.base.revisionId

position 1:
  capabilityId:
    <exact newly created FEATURE capability ID>
  capabilityRevisionId:
    <exact newly published FEATURE revision ID>
```

and:

```text
responseContract: authoredResponseContract
```

Require the returned release to preserve:

```text
members[0].position == 0
members[0] == exact fixture BASE capability/revision identity

members[1].position == 1
members[1] == exact newly authored FEATURE capability/revision identity

responseContract == authoredResponseContract
```

No array-index-derived IDs or latest-revision substitution is permitted.

#### 5. Activate the newly authored release and rollback

Before activation read:

```ts
services.getRelease(fixture.releases.active.releaseId)
```

and capture its real `activePointerVersion`.

Activate the newly created release with that exact pointer CAS:

```ts
services.activateRelease({
  operationId: 'c20-studio-s01:activate-release',
  reason,
  releaseId: <exact newly created release ID>,
  expectedActiveReleaseVersion: <captured pointer version>,
})
```

Require:

```text
kind: ok
status: ACTIVE
activePointerVersion == captured + 1
```

Then rollback to:

```text
fixture.releases.active.releaseId
```

using the exact returned `activePointerVersion` from activation. Require:

```text
kind: ok
status: ACTIVE
activePointerVersion == captured + 2
```

Reread the authored release after rollback and require it is no longer ACTIVE under
the configured TEST environment.

#### 6. Prove the lifecycle ledger

After the flow, read:

```ts
const state = await backend.publication.snapshot();
```

For each of the nine S01 operation IDs listed above require:

```text
state.audits.filter(audit => audit.id === operationId).length == 1
```

Also assert the persisted release members/response contract using the returned real
identities; do not use only total table counts.

### A7-R2 — preserve the existing C20 evidence

Attempt 8 must not weaken or delete the four existing real C20 scenarios. After the
new S01 test is added, the real suite expectation becomes:

```text
tests/studio-integration-c20.test.ts
  5 tests passed
```

The existing focused adapter suite remains:

```text
tests/studio-integration.test.ts
  9 tests passed
```

No arbitrary additional test count is required.

### A7-R3 — execution and failure routing

Because the S01 test uses the real Prisma/lifecycle adapter, rerun the exact approved
Attempt-7 disposable Docker procedure from the previous Architect Review. Use the same
image versions, safety guards, dynamic loopback ports, database name, Redis namespace,
ownership label and cleanup rules.

Run:

```bash
npm run c20-fixture:reset
npm run test:arch020-studio-integration:c20
npm run test:arch020-studio-integration
npx eslint tests/studio-integration-c20.test.ts
git diff --check
```

Also rerun the repository-required:

```bash
npm run lint
npm run typecheck
npm run build
```

The already documented unrelated baseline remains non-blocking only when materially
unchanged and no diagnostic points at an Attempt-8-owned file.

If the exact S01 flow exposes:

```text
COMMERCE-018 adapter defect
```

fix only that bounded defect inside COMMERCE-018, rerun the affected proof and report
the change.

If it exposes an accepted COMMERCE-013 or COMMERCE-035 producer defect, do **not**
modify that producer from this task. Return COMMERCE-018 `blocked` with the exact
reproduction for `moda_architect`.

### A7-R4 — durable report/state reconciliation

Before returning Attempt 8:

1. check S01 only when the exact real traversal above passes;
2. reconcile S02-S06 truthfully from the combined accepted component/focused/C20
   evidence; do not claim terminal cross-service/system-test behavior that was not run;
3. update Work Items / Acceptance Criteria / Validation where the evidence supports it;
4. append an Attempt 8 Completion Report containing:
   - implementation commit(s);
   - parent report commit;
   - launcher/worktree synchronization evidence;
   - the 5/5 C20 result;
   - the 9/9 focused Studio result;
   - Docker endpoint class/server version/image digests/container names;
   - database name/Redis namespace without URLs/password;
   - health and cleanup success;
   - lint/typecheck/build/diff results and exact unchanged baseline diagnostics;
5. return:

```yaml
status: review
attempt: 8
executor: null
claimed_at: null
```

6. push both mirrored task branches;
7. STOP.

Do not begin COMMERCE-012, COMMERCE-024, GATEWAY-001 or any system-test task.

### Reviewed Files

- `moda-interact-commerce/tests/studio-integration-c20.test.ts`
- `moda-interact-commerce/tests/studio-integration.test.ts`
- `moda-interact-commerce/src/commerce/integration/studio/services.ts`
- `moda-interact-commerce/src/studio/server-actions.ts`
- `moda-interact-commerce/src/studio/contracts.ts`
- `moda-interact-commerce/src/commerce/integration/backend/c20-test-fixture.ts`
- `docs/architecture/ARCH-020-implementation-contracts.md`
- this task's Attempt-7 Completion Report

### Validation Reviewed

Attempt 7 durable evidence is accepted:

```text
real C20 suite:       4/4 PASS
focused Studio suite: 9/9 PASS
changed-test ESLint:  PASS
git diff --check:     PASS
PostgreSQL health:    PASS
Redis health:         PASS
container cleanup:    PASS
```

Repository-wide lint/typecheck/build remain non-zero only on the already recorded
unrelated baseline according to the Completion Report.

### Architecture Conformance

Partial.

The production adapter and the Attempt-7 validation infrastructure conform. The
remaining gap is evidence for C20's explicitly assigned I01/S01 real authoring
traversal. A task whose report explicitly says full S01 assembled acceptance is not
claimed cannot yet satisfy its own S01 criterion.

### Follow-up

Return this same task to `ready`, retain `attempt: 7`, clear the claim and make no
downstream task Ready.

The next successful `/moda-task ARCH-020-COMMERCE-018` claim creates Attempt 8 exactly
once.

No production source correction is requested before that claim.

## Architect Review — Attempt 8 — 2026-09-22

### Review Status

Accepted.

### Review Notes

**Accepted / Complete, Attempt 8.**

Reviewed by `moda_architect` against the exact submitted Attempt 8 archive and parent
handoff `c99dd98228067e02f612837b810bb8f82a09e332`. The current remote
`task/ARCH-020-COMMERCE-018` parent branch matches that handoff commit. The task
records implementation commit `621b33c`; the Commerce implementation remote is not
readable through the current review connector, so implementation acceptance is
grounded in the exact submitted archive.

Attempt 8 closes the single remaining task-owned gap from the Attempt 7 Architect
Review: C20 I01 / S01 now performs a full real authoring traversal through the
production `StudioServices` adapter and accepted application services.

The fifth real C20 scenario now proves, using real returned identities rather than
constructed IDs:

```text
validate tool definition
-> create tool
-> create tool draft
-> publish tool revision
-> create FEATURE capability
-> create capability draft
-> discovery outage
-> reread and preserve the exact saved draft
-> publish capability revision
-> validate response contract/example
-> create release with explicit member positions
-> activate with current pointer CAS
-> rollback with returned pointer CAS
-> reread authored release as SUPERSEDED
-> verify one audit row for each of the nine operation IDs
```

The production-source correction discovered by that real traversal is bounded and
correct: optional source revision fields are omitted when absent before lifecycle
operation hashing. `createToolDraft(...)` no longer forwards
`sourceToolRevisionId: undefined`, and `createDraft(...)` no longer forwards
`sourceRevisionId: undefined`. This preserves the accepted strict command/hash shape
without changing replay semantics or producer ownership.

Two test-fixture details differ from the literal Attempt 7 recipe but remain
architecturally conformant and do not weaken S01:

- the authored Storefront tool uses a valid LIST/`items` response template against
  `products.nodes` rather than the illustrative text template; the definition passes
  the accepted production compiler/definition validator before persistence;
- response-contract validation uses a complete valid `response.v1` example rather
  than an empty object, exercising the accepted `validateResponseExample(...)`
  boundary instead of bypassing the real final-response shape.

The important acceptance invariant is the real create/validate/publish/release/
activate/rollback traversal through accepted production services, and that invariant
is now satisfied.

Attempt 7's already accepted infrastructure and real-adapter evidence remains valid
and is preserved. Attempt 8 reran the affected proof and reports:

```text
npm run c20-fixture:reset
  PASS

npm run test:arch020-studio-integration:c20
  PASS — 5/5

npm run test:arch020-studio-integration
  PASS — 9/9

focused changed-file ESLint
  PASS (one pre-existing unused ShopSummary warning reported by the task)

git diff --check
  PASS
```

Repository-wide lint/typecheck/build remain non-zero only on the documented unrelated
baseline outside COMMERCE-018. No Attempt-8-owned diagnostic is reported, so those
baseline failures do not block acceptance.

The combined accepted evidence now satisfies this task's S01-S06 boundary. This does
not claim terminal cross-service/system-test execution outside COMMERCE-018 ownership;
those remain owned by the downstream Gateway/System-Test/final-checkpoint tasks.

### Functional Acceptance

- real Studio authoring uses the accepted publication/lifecycle services;
- same-origin mutation enforcement and role reauthorization remain intact;
- ADMIN publication denial and one-write replay/CAS evidence remain intact;
- discovery outage preserves the authored draft before publication;
- exact member ordering and current environment pointer CAS are exercised;
- response-contract example validation is exercised against the accepted validator;
- U13 positive/excluded eligibility remains read-only;
- no copied C20 fixture, production fixture registration, MCP/runtime rewrite,
  database schema change, live provider call or production credential was introduced.

### Validation Reviewed

Submitted Attempt 8 evidence:

```text
real C20 suite:       5/5 PASS
focused Studio suite: 9/9 PASS
changed-file lint:    PASS
git diff --check:     PASS
fixture reset:        PASS
```

The previously accepted disposable PostgreSQL/Redis health, image, loopback,
ownership and cleanup evidence remains part of the durable Attempt 7/8 proof.

### Architecture Conformance

Conformant.

COMMERCE-018 now satisfies the accepted C20 Studio production-integration boundary.
Actual preview behavior remains COMMERCE-019 ownership, external production
composition remains COMMERCE-024 ownership, deployment remains Gateway ownership and
terminal system testing remains System-Test ownership.

### Dependency Frontier

With COMMERCE-018 Complete, every dependency of `ARCH-020-GATEWAY-001` in this exact
snapshot is Complete. `ARCH-020-GATEWAY-001` is therefore promoted from `pending` to
`ready`, claim clear, Attempt 0 retained.

No task is launched automatically.

`ARCH-020-COMMERCE-024`, `ARCH-020-COMMERCE-012` and the system-test tasks retain
other incomplete prerequisites and remain gated.

### Follow-up

None for COMMERCE-018. Do not reopen its accepted production adapter unless a later
consumer produces a concrete regression against this contract.
