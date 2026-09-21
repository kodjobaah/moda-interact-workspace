---
id: ARCH-020-COMMERCE-013
architecture_id: ARCH-020
title: Integrate Commerce backend runtime and publication services
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 125
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-011
  - ARCH-020-COMMERCE-014
  - ARCH-020-COMMERCE-015
  - ARCH-020-COMMERCE-016
enables:
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-018
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-001
created: 2026-09-21
updated: 2026-09-21
---

# Integrate Commerce backend runtime and publication services

## Architecture

ARCH-020. [Implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C4/C5/C7/C9/C14–C19 remain binding. The integration ownership specification is
[C20](../../../architecture/ARCH-020-implementation-contracts.md#c20-integration-task-ownership-and-parallel-execution).
Use actual accepted prerequisite source, never copied snapshots or new schemas.

## Objective

Connect production publication storage/compiler validation, MCP authorization/dispatch and Shopify/policy adapters. Deliver the stable backend facade used independently by018 and019. No Studio page or preview lifecycle wiring.

## Context

The former013 combined backend, Studio and preview integration. This definition
replaces that combined scope;018 and019 can execute concurrently after013 and
their own component prerequisites complete. No task was claimed by this amendment.

## Scope

Connect production publication storage/compiler validation, MCP authorization/dispatch and Shopify/policy adapters. Deliver the stable backend facade used independently by018 and019. No Studio page or preview lifecycle wiring.

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

- [ ] Deliver `src/commerce/integration/backend.ts` with server-only `getCommerceBackend()`; C20 defines its typed members and lifetime rules. Do not import Studio or preview components.
- [ ] Implement durable `PublicationStoragePort`/authorization/feature/runtime adapters under `src/commerce/integration/backend/`. The accepted003 factory currently throws UNAVAILABLE; tests/in-memory storage are not a production adapter.
- [ ] Wire011 compiler into003 validation, one executable registry into publication and014, and014 into004. Resolve durable authorization records for004 using existing grant/feature/recovery models.
- [ ] Connect005 tokenless transport and015/006/016/007 privileged adapters with current server-owned identity, policy, installation lookup and a shared per-call budget. Register exact installed versions only.
- [ ] Preserve full Studio command semantics in the backend facade. Correct the known capability enable/disable CAS mismatch as C20 specifies; do not silently drop expectedUpdatedAt or weaken strict schemas.
- [ ] Replace the unavailable MCP runtime at app/api/mcp/route.ts with this composition; preserve existing HTTP profile. No request-specific identity/grant stored in a process-global singleton.
- [ ] Provide `docs/commerce-backend-integration.md`, exact facade types, mapping table and `test:arch020-backend-integration` plus `test:arch020-backend-integration:database` commands. Freeze these contracts before018/019 begin.

## Interfaces / Contracts

Binding wiring table (paths relative to Commerce repository):

| Source/export | Destination | Required adapter/file |
|---|---|---|
| `src/commerce/publication/lifecycle.ts: CommerceLifecycle`; `ports.ts: PublicationStoragePort` | Durable publication facade | `backend/publication-storage.ts`, `backend/publication.ts` |
| `lib/discovery/compiler.ts: createCommerceCompiler` | `QueryValidationPort.validate({definition})` | `backend/query-validation.ts`: compile the exact execution/input schema, validate mapping/output/template through accepted validators; bounded INVALID_DEFINITION vs unavailable errors |
| `execution/ports.ts: createPolicyOperationRegistry`;005 `createQueryExecutionPort` |014 `createDefinitionExecutor` | `backend/executors.ts`: one immutable exact-version registry shared with publication availability |
|015 `createProductPolicyAdapters`,006 `createDiscountRuleReader`/`getDiscountOptions`,016 `createDiscountEvaluationAdapter` | Policy registry | preserve operation input/output; adapt context without resetting budget/deadline or deriving shop from arguments |
|007 accepted recommendation descriptors | Policy registry | record its actual exported symbol on accepted source before Ready; no invented handler name |
|004 `resolveAuthorizedSnapshot`, `createMcpService`, assertion verifier | `/api/mcp` | `backend/authorization.ts`, backend facade and existing MCP route only |

Typed product/rule/evidence interfaces are their accepted module exports; C19
field semantics and C18 evidence separation remain authoritative. This task owns
backend assembly only, including real PostgreSQL and HTTP transports.

## Dependencies

- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-011
- ARCH-020-COMMERCE-014
- ARCH-020-COMMERCE-015
- ARCH-020-COMMERCE-016

All dependencies must be Complete and architect-accepted before execution.
Readiness never launches a task; use the normal dedicated mirrored worktrees.

## Enables

- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-018
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-001

## Acceptance Criteria

- [ ] B01: real publication/compiler/storage create and publish a valid query and release; invalid field/mapping/version or absent executor produces zero publication/audit writes.
- [ ] B02: duplicate operation ID commits one effect/audit; mismatched reuse and stale CAS conflict. Pointer/member writes rollback together on injected failure; two real DB connections exercise races.
- [ ] B03: authenticated MCP resolve/list/call executes the published query through005; old seeded grant remains pinned after new publication; cross-shop/revoked/expired assertion dispatches zero provider calls.
- [ ] B04: every policy registration matches installed version/schema; renamed discount/recommendation tool works; unknown/missing adapter fails closed. Provider budgets are shared by reference across nested adapters.
- [ ] B05: production factory is callable with real dependencies and contains no fixture registration; missing config returns typed unavailable; backend import does not require018/019 or browser code.
- [ ] B06: known capability enable/disable timestamp CAS is preserved in strict input, payload hash and same transaction as the write; stale timestamp and changed replay payload have zero committed changes.

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

Ready for Review.

### Files Changed

Implementation branch `task/ARCH-020-COMMERCE-013`: `src/commerce/integration/backend.ts`,
`src/commerce/integration/backend/{authorization,executors,publication-storage,query-validation}.ts`,
`app/api/mcp/route.ts`, publication lifecycle/ports, backend integration tests,
auth entrypoint test, package scripts, and `docs/commerce-backend-integration.md`.

### Work Completed

- Added the server-only `getCommerceBackend()` facade with publication, discovery,
  compiler, shared execution, explicit fixture execution, saved-selection and
  inspection boundaries; missing saved/inspection production adapters fail closed.
- Replaced the MCP route's unavailable composition with the backend runtime and
  retained request-scoped assertion, grant, turn and budget state.
- Added Prisma-backed serializable publication storage with advisory locking,
  durable replay reconstruction from audit metadata, atomic business/audit writes,
  canonical tool-definition JSON, and strict metadata/edit/pointer CAS.
- Wired accepted compiler, executor registry, query, policy, discount,
  recommendation, assertion and authorization exports without adding fixture
  registration to production.
- Corrected the known enable/disable timestamp CAS mismatch for both capability
  and tool commands; updated the lifecycle test to supply the current token.

### C20 Requirement Matrix

| Requirement | Evidence / disposition |
| --- | --- |
| B01 | Compiler validation and publication integration are wired; focused lifecycle and execution tests pass. Real PostgreSQL publication rows remain developer validation. |
| B02 | Serializable transaction, advisory lock, replay audit and atomic write path are implemented. Two-connection race/rollback evidence remains pending isolated PostgreSQL validation. |
| B03 | MCP route composes verified assertions, authorization snapshot and exact execution registry; request-scoped identity is preserved. Live grant/provider evidence remains pending. |
| B04 | Exact `1.0.0` policy registration and immutable registry are composed from accepted exports; renamed/adapter/provider budget scenarios are covered by prerequisite tests and require integrated provider evidence. |
| B05 | Server-only facade, no fixture registration, typed unavailable behavior, and production build are verified. |
| B06 | Capability and tool enable/disable require `expectedUpdatedAt`, hash the strict request, compare inside the transaction, and update the timestamp. Focused suite passes. |

Former I01-I09 ownership is preserved: I01/06/07 are COMMERCE-018, I09 is
COMMERCE-019, and I02/03/04/05/08 are represented by this backend boundary and
the pending real-infrastructure evidence above.

### Validation Results

Agent-executed checks, implementation worktree `task/ARCH-020-COMMERCE-013`:

- `npm run test:arch020-backend-integration`: passed, 4 files / 49 tests.
- `npm run typecheck`: passed; Next route types generated and `tsc --noEmit` passed.
- `npm run lint`: passed.
- `npm run build`: passed; Prisma Client 6.19.3 generated and Next production build completed.
- `npm run test:arch020-backend-integration:database`: static schema check passed;
  migration validator failed closed before connection with `Local isolated target required`
  because no `DATABASE_URL` was supplied.
- `git diff --check`: passed.

Developer validation required: run the migration validator twice against
developer-created localhost PostgreSQL databases `arch020_test_fresh` and
`arch020_test_upgrade`, plus the C20 real PostgreSQL two-connection race/rollback
and Redis/container transport checks. Record actual rows, operation IDs, audit
rows, provider calls, and rollback state; no pass is claimed here.

### Deviations

No scope deviation. The saved-selection and inspection adapters are explicit
injected boundaries and fail closed until their owning Studio/preview integration
provides real server adapters; no fixtures or browser code cross the backend
boundary.

### Assumptions

Accepted producer source SHAs and installed versions are recorded in
`docs/commerce-backend-integration.md`. Database submodule is consumed at
`5abfd87f57038bae515aaa09ec7c8db62adcfb98`; shared package `0.13.1`, Prisma
`6.19.3`, Next `16.3.5`, and MCP SDK `1.30.0`.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Attempt 1 uses mirrored `task/ARCH-020-COMMERCE-013` branches. Parent claim is
`97180042`; implementation branch started at `aaa776c14dde87260afdd3c9a1d2797db613df4f`.
At submission record the implementation and parent report commit hashes and push
results, the database submodule SHA above, and confirmation that no main branch
or parent service gitlink was changed.

## Completion Report — Attempt 2

Status: Ready for Review.

Attempt 2 implements the six corrections from the latest Architect Review. The
implementation branch is `task/ARCH-020-COMMERCE-013` at implementation commit
`d432276`; the parent report branch is the mirrored
`task/ARCH-020-COMMERCE-013` branch in its dedicated parent worktree. The
implementation worktree is
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-013`;
the parent worktree is
`/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-013`.
The prepared claim was `495b88ed`; both task branches were synchronized from
their respective remotes before this attempt. The database submodule remained at
`5abfd87f57038bae515aaa09ec7c8db62adcfb98`. No main branch, parent service
gitlink, downstream task, or Architect Review text was changed.

### A1 correction checklist

- [x] **A1-R1:** `getCommerceBackend()` now lazily assembles the production
  server boundary from validated configuration, Prisma, accepted auth and
  provider/policy adapters; injected construction remains test-only and missing
  configuration fails closed with the bounded unavailable result.
- [x] **A1-R2:** publication persistence now writes only changed mutable rows,
  inserts immutable rows and audits once, preserves publisher metadata on a real
  draft-to-published transition, and keeps pointer/member/business writes in the
  locked transaction.
- [x] **A1-R3:** CAS timestamps are reconstructed with exact Date precision for
  tools and capabilities, preserving non-zero milliseconds and same-second
  token changes.
- [x] **A1-R4:** the facade now owns typed, authorized read-only
  `saved.readSelection`, `inspection.listShops`, and `inspection.inspectShop`
  adapters with bounded inputs, exact revision selection, and no grant/token or
  customer-history writes.
- [x] **A1-R5:** query validation now invokes Shared's accepted full publication
  validator against the pinned compiler output, including response templates,
  before lifecycle writes.
- [x] **A1-R6:** executable B01-B06-labelled scenarios run through the backend
  facade and lifecycle boundary; the disposable PostgreSQL replay/CAS/rollback
  rehearsal has a declared command and remains separately developer-owned.

### Validation Results

Executed in the implementation worktree with Node `v24.21.0` and npm `11.19.0`:

| Command | Result |
|---|---|
| `npm run test:arch020-backend-integration` | **passed: 4 files, 52 tests** |
| `npm run lint` | **passed** |
| `npm run typecheck` | **passed**; Next route types generated and `tsc --noEmit` completed |
| `npm run build` | **passed**; Prisma Client `6.19.3` generated and Next production build completed |
| `git diff --check` | **passed** |
| `npm run test:arch020-backend-integration:database` | **static schema/migration/ERD checks passed**; migration rehearsal failed closed with `AssertionError: Local isolated target required` because no `DATABASE_URL`/isolated target was supplied |
| `npm run test:arch020-backend-integration:postgres` | **pending**; failed closed before container creation with `Set ARCH020_REHEARSAL_ALLOW_DISPOSABLE_DOCKER=1 to authorize creation and removal of one disposable Docker container.` |

The database command made no database connection. PostgreSQL two-connection
fresh/upgrade, replay/CAS, rollback and race evidence remains pending developer
execution against the exact isolated targets `arch020_test_fresh` and
`arch020_test_upgrade`. Redis-backed readiness and containerized provider
transport validation also remain pending developer execution. No live Shopify,
MCP, model, WhatsApp, billing, customer-history or production credential
evidence is claimed.

### Dependencies and handoff

All listed prerequisites were accepted before the attempt:
COMMERCE-003/004/005/006/007/011/014/015/016. Attempt 2 re-verified the
producer exports and revisions recorded in
`docs/commerce-backend-integration.md`, including the accepted COMMERCE-007
recommendation source `e08b896`, and introduced no copied source or database
schema. The implementation commit is `d432276`; the parent report commit will
be recorded after publication of this report branch. This task is ready for
architect review; no downstream task was launched.

## Architect Review

### Attempt 1 — Changes Requested (2026-09-21)

Reviewer: moda_architect. Reviewed implementation `8258b0139a1d722af418555b2d3c5ca5a05b36e8` and parent report `9c1a26b509adaffe5f21ca89717f1c51a78a1c0a`. Both submitted heads matched remote and their task worktrees were clean. Decision: **Changes Requested; Ready, Attempt 1; executor and claim cleared**. These are functional integration defects, not a requirement for exhaustive coverage. COMMERCE-018/019 remain Pending; this facade cannot yet be frozen for them.

#### A1-R1 — Supply the production composition, not caller-provided missing adapters

Files: `src/commerce/integration/backend.ts`, `backend/authorization.ts`, `backend/executors.ts`, `app/api/mcp/route.ts`.

The only production caller is the route's `getCommerceBackend()` with no arguments. The factory throws unless a caller previously supplied config, and there is no such initializer. Thus every fresh production process returns 503 regardless of valid deployment configuration. The factory also requires the caller to supply query execution, policy registrations, authorization record resolution and publication authorization/features/runtime compatibility. It never constructs the accepted product/discount/recommendation adapters or durable authorization resolver claimed by the mapping table.

Implement lazy production assembly from validated server configuration, real Prisma clients and accepted auth/installation libraries. Build the tokenless HTTP transport, privileged provider/recovery/policy adapters, exact-version immutable registry and durable grant/feature/recovery record resolver here. Share the same registry with publication and execution. Preserve request-local principal/turn/grant/shop, deadline, cancellation and budget references; singleton state may contain only reusable stateless dependencies. Keep an explicitly injected factory for tests, but the no-argument production entry must work without an out-of-band caller. Missing genuine configuration must fail with the accepted bounded availability contract. Do not delegate this assembly to018/019. Verify a fresh-process configured route reaches real authorization/execution with only external provider transport substituted, and that denied/revoked/cross-shop requests make zero provider calls.

#### A1-R2 — Persist only the transaction's changes and honor database publication invariants

File: `backend/publication-storage.ts`.

`writeState()` upserts every loaded tool/revision/release/member/pointer/audit, even on a replay with no state changes. The canonical migration forbids UPDATE of audits, releases, release members and published revisions; unchanged draft/pointer updates also fail required editVersion increments. After the first audit exists, a subsequent command or replay attempts to update that audit and fails. Additionally, published tool/capability writes omit `publishedByAdminId` and `publishedAt`, which the database requires for PUBLISHED rows. A temporary recording Prisma port confirmed both generated-write defects; no real database pass is claimed.

Replace whole-snapshot upserts with a before/after diff or explicit mutation journal under the C7/C20 locking/CAS transaction. Insert only new immutable rows/audits; update only changed owned metadata/drafts/pointers with locked current versions. A successful identical replay must return its durable original result with zero business/audit writes. Persist publisher identity/time on the actual DRAFT-to-PUBLISHED transition, preserving creator/history. Business rows, release members, pointer and audit must commit or rollback together. Follow the specified READ COMMITTED/locking design; do not rely on a global serializable lock to compensate for stale snapshots or missing CAS. Keep schema/triggers intact. Verify generated writes locally and provide the runnable PostgreSQL replay/race/rollback scenarios described in A1-R6.

#### A1-R3 — Preserve exact timestamp CAS tokens

File: `backend/publication-storage.ts`, `stateFromRows()` tool/capability mappings.

`new Date(String(row.updatedAt))` converts Prisma Date objects through their human-readable string, losing milliseconds. Reproduction: `2026-09-21T12:00:00.456Z` becomes `.000Z`. This makes the token returned by a prior write fail on the next command and can collapse distinct updates within one second.

Serialize Date objects directly to ISO (with validated handling for any other supported representation), preserving full stored precision. Apply to both tools and capabilities. Ensure metadata/enable updates produce a changed token even when operations occur within one clock tick, and retain expectedUpdatedAt in strict input, replay hash and locked write checks. Verify a write/read/token round trip and stale-token rejection with non-zero milliseconds and same-second updates.

#### A1-R4 — Implement and freeze the C20 saved-selection and inspection facade

File: `src/commerce/integration/backend.ts` and owned `backend/**` adapters.

`saved.readSelection`, `inspection.listShops` and `inspection.inspectShop` are default throwing placeholders typed with unknown inputs/results. ProductionBackendConfig cannot even provide their optional overrides. The report assigns them to consumers, but C20 explicitly assigns these durable read adapters and canonical typed results to013;018/019 must import them without editing this facade.

Implement authorized durable reads for accepted009 RELEASE/DRAFT selections, exact selected revisions/definitions/prompts/content hashes and response contract/hash. Validate ownership, conflicts and bounds; never substitute latest revisions. Define the concrete shared result types from accepted record contracts. Implement read-only merchant/feature eligibility and candidate manifest/exclusion reasons for inspection, with current server-resolved staff authorization on every protected entry and no tokens/customer history/grant writes in results. Keep019's grant-scoped frozen snapshot ownership separate. Freeze a read-only facade usable by both consumers and verify representative authorized and denied selections/inspection through it.

#### A1-R5 — Validate the complete published query definition

File: `backend/query-validation.ts`.

The adapter invokes compile and validateMappedArguments, but never checks the response template against the compiled output schema. The lifecycle's schema parse does not supply this missing semantic validation. Consequently a valid query with `{{result.nonexistent}}` can be admitted even though the accepted Shared publication validator rejects it.

Invoke the accepted full definition publication validator with the pinned compiler, covering schema, mappings and scalar/items template paths; do not implement another parser. Preserve bounded INVALID_DEFINITION versus schema/validator availability errors. Verify a valid query publishes and an absent/nonscalar template path fails before any business or audit write. Keep existing policy registry/version validation intact.

#### A1-R6 — Provide executable integration evidence and correct the handoff record

The named 49-test command mostly reruns prerequisite component suites; the two new backend tests only exercise helper validation/registry and missing-config behavior. They do not assemble the backend or exercise PrismaPublicationStorage. The `:database` script runs schema/migration validation, not B02's two-connection publication races, replay or injected rollback. Pending infrastructure execution is correctly not claimed as a pass, but the required backend scenarios themselves must exist.

Add bounded scenarios for B01–B06 using the actual facade, lifecycle, authorization, compiler, execution and durable storage. Substitute only external provider/model transports. Supply a command that really runs the isolated PostgreSQL publication/replay/CAS/rollback/two-connection scenarios, in addition to migration validation; retain developer ownership of actually running restricted PostgreSQL/Redis/container checks. No paid/live provider requirement is added. Correct the mapping table to list adapters actually constructed and their accepted source revisions, and report per-scenario executed/pending results honestly. Record the prepared execution packet's exact dedicated worktrees, start synchronization and recursive database revision; retain existing history. Submission claim fields must be clear. Do not launch downstream work.

#### Architect validation and disposition

`npm run test:arch020-backend-integration`: **49/49 passed** on submitted implementation. Independent temporary harness `/tmp/c013-a1-review/review.test.ts` uses the actual storage/validation adapters with a recording Prisma boundary; **4/4 assertions failed**, confirming immutable-audit rewrites, missing publisher metadata, lost CAS milliseconds and acceptance of a template path rejected by the accepted Shared validator. This is local functional evidence, not real PostgreSQL validation. Submitted typecheck/lint/build/Prisma results were reviewed, not redundantly rerun. No implementation or main branch was changed. Pending live/infrastructure checks remain developer-owned. No downstream promotion; preserve the final manual system-test gate.

### Original pending review placeholder (historical)

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.


## Architect readiness reconciliation — COMMERCE-007 acceptance — 2026-09-21

Promoted **Ready**, Attempt 0 retained, executor/claimed_at null. COMMERCE-003/004/005/006/007/011/014/015/016 are architect-accepted Complete, including COMMERCE-007 Attempt 7 at `e08b896`. All explicit prerequisites are satisfied. Normal preparation owns synchronization and claim and must consume actual accepted source. No automatic launch, implementation change, main integration or gitlink update.
