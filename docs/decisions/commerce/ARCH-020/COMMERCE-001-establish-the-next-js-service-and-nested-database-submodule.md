---
id: ARCH-020-COMMERCE-001
architecture_id: ARCH-020
title: Establish the Next.js service and nested database submodule
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 50
executor: codex
claimed_at: 2026-09-20T19:42:47Z
attempt: 3
depends_on: []
enables:
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-005
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-015
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-002
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-COMMERCE-029
created: 2026-09-20
updated: 2026-09-20
---

# Establish the Next.js service and nested database submodule

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Provide a reproducible Next.js application foundation in the new Commerce repository.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

**Readiness:** repository provisioning was verified on 2026-09-20. The private `https://github.com/kodjobaah/moda-interact-commerce.git` repository is registered as the workspace submodule at main commit `01c550c3e3f55dd23a4ecc9514c846bb88cf2067`. The architect promotes this task to Ready with no attempt claimed. See the completed provisioning checkpoint in the implementation handoff. Next.js and the nested database submodule remain this task’s deliverables.

## Scope

New repository app shell, package/toolchain config, .gitmodules database pin, Prisma generation, health/readiness and local development documentation.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Duplicate-action protection

Every state-changing or costly UI action in this task must prevent duplicate
activation, including mouse double-click, double-tap, Enter/Space repetition and
form-submit plus button-click combinations. Acquire a synchronous submission
guard before awaiting work (a render-delayed disabled state alone is insufficient),
and route all activation paths through the same submit handler. Disable the
trigger and conflicting controls immediately, show a meaningful pending label,
and expose accessible busy/status feedback. Do not lock unrelated navigation.

Keep the guard until the operation has definitively completed, failed or been
cancelled. A client timeout is an unknown outcome: reconcile the original
operation before allowing a retry, rather than silently creating a second one.
On a known failure, restore controls and preserve input for an intentional retry.
Ignore stale completions so an earlier request cannot reset a newer request's
pending state. Debounce alone is not sufficient for mutations or paid previews.
Server authorisation and duplicate protection are required independently of the
browser controls; inspect direct duplicate requests as well as UI behaviour.

## Work Items

- [x] After the handoff setup checkpoint registers the remote submodule and owner, scaffold the Node-runtime Next.js App Router application without business features.
- [x] Add database/ as a Git submodule of https://github.com/kodjobaah/moda-interact-database.git pinned to an integrated revision; never copy the schema.
- [x] Provide explicit dev/build/start/typecheck/lint/test and prisma:generate commands; recursively initialise database before client generation in clean builds.
- [x] Establish server-only connection handling and separate liveness/readiness routes with no secret disclosure; do not run migrations on application startup.
- [x] Choose and record a tested MCP SDK/Next.js adapter/client compatibility set with a bounded local round trip; no production endpoint or authentication bypass.

- [x] Provide a reusable pending-action/form pattern for the Studio shell so later screens can use a synchronous guard, native disabled controls and accessible busy/error states. No application-wide network lock.

## Interfaces / Contracts

Proposed private /api/mcp; actual SDK/protocol versions documented here and consumed by BACKGROUND-001.

### Implementation guidance

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C5, C9, C10**. These are required acceptance inputs, not optional examples.

Deliver Next App Router Node service, nested database pin, scripts dev/build/start/typecheck/lint/test/prisma:generate, docs/runtime-compatibility.md and a local MCP protocol fixture. Lock exact tested server/client/adapter versions and record Node/Next/React versions. Fixture route must be test-only and absent from the production route tree. Provide /health/live and /health/ready exactly as C10.

### Required evidence

Fresh recursive clone fixture validates generated Prisma and production build/start/health. Compatibility fixture covers initialize, resource read, prompt retrieval and tools/call for the C5 stateless profile. UI shell test only needs its pending-action example; no paid preview test before preview exists.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies


None.

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-005
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-015
- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-002
- ARCH-020-SYSTEM-TEST-001
- ARCH-020-COMMERCE-029

## Acceptance Criteria

- [x] A fresh recursive clone and canonical execution worktree can generate Prisma and build the service using the database pin.
- [x] No browser bundle contains server credentials; health routes disclose no credentials or tenant records.
- [x] Actual build/start/port/health contracts are documented for Gateway; no Vercel hosting assumption is introduced.

- [x] A local example/test of the shared UI pattern dispatches once under same-tick double activation and permits an intentional retry after a known failure.

## Validation

- [x] Run the new declared typecheck/lint/build and focused local health/adapter smoke checks.
- [x] Check git submodule status --recursive and clean-clone/build instructions; record nested database SHA and git diff --check.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

## Completion Report

### Attempt 3 — Ready for Review (2026-09-20)

Addressed the current Attempt 2 Changes Requested finding on process-group teardown. Implementation **d7c1c65bf382de1538d77ac4dbe65c1d7fcd1276** is committed and pushed to `task/ARCH-020-COMMERCE-001`. Task status is **review**; architect acceptance is pending. The prior reports and the entire Architect Review/authorization are preserved as recorded history.

#### Correction checklist

- [x] **Source correction:** `scripts/readiness-docker.mjs` keeps one idempotent teardown promise after timeout/AbortSignal cancellation. It sends SIGTERM, retains the two-second SIGKILL escalation independently of the leader's `close`, and awaits escalation before settling the command. A scheduler turn after SIGKILL permits signal delivery before resource cleanup proceeds. Missing spawn PIDs cannot target a process group. Command output redaction/failure codes, main SIGINT/SIGTERM codes and ownership-verified Docker cleanup remain intact.
- [x] **Behavioral regressions:** `tests/readiness-docker.test.ts` adds separate timeout and AbortSignal cases. A real Node parent spawns an ignored-stdio descendant; the descendant installs a no-op SIGTERM handler before reporting readiness, and the parent exits with code 17 on SIGTERM. Both cases verify cancellation rejection, preserved code 17, leader exit, and descendant/process-group absence within the bounded deadline. `finally` kills only those synthetic processes and removes its temporary directory if assertions fail. Existing single-process timeout and Docker ownership/cleanup tests remain.
- [x] **Validation and publication:** focused regressions, full tests, typecheck, lint and whitespace checks passed. Published both mirrored task branches for architect review; no main merge or dependent-task execution.

#### Requirement-to-fixture results

| Requirement | Expected effects / command | Result |
|---|---|---|
| Timeout and AbortSignal after early leader exit | Synthetic local child processes only; `npm test -- tests/readiness-docker.test.ts` | **10 passed**, including both new descendant regressions and existing cleanup tests |
| Foundation and cleanup regression coverage | Local mocks/loopback/subprocesses; `npm test` | **29 passed, five suites** |
| Declared command-runner cancellation type | `npm run typecheck` | **Passed** after adding the explicit existing AbortSignal option declaration |
| Lint / whitespace | `npm run lint`; `git diff --check` and staged check | **Passed** |
| Schema ownership | Nested `database` status and unchanged pin | **Clean**, no database edit/pin change |

Validation used workspace-bootstrap Node 24.19.0/npm 11.17.0 in the prepared implementation worktree. During implementation the new typed call exposed that JavaScript inference omitted the runner's existing `signal` option; an explicit JSDoc signature corrected it, and typecheck/lint then passed. No unresolved correction validation remains.

Per the current architect review, the earlier successful real Docker readiness/build/clean-clone evidence is retained. This correction changes process teardown only; it does not change provisioning, readiness queries, runtime routes or dependencies. No Docker/build rerun or live/provider operation was required or performed. The previously reviewed Prisma/deepmerge-ts limitation retains its recorded disposition; no clean-audit claim is made. SIGKILL/host failure still cannot execute application cleanup, as already documented.

#### Prepared launcher and VCS evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-001`.
- Both worktrees reused for this task; both branches `task/ARCH-020-COMMERCE-001`. No shared/default checkout switched or mutated, no other task worktree reused.
- Packet: both remote task fast-forwards `not-needed`; both origin/main incorporations `already-current`; no dependencies, dependency gate passed.
- Prepared parent head `9414923a01c00b681a90bd96f2b29e546735896c`; implementation start `8c8b8250954aec9d6f011130bf05f620c35dff04`.
- Recursive submodule sync/update passed, status ready; `database` initialized at **9c6a4d8402a01840e2ea8dc18e89171f00564d29**. No repeated startup preparation.
- Attempt 3 claimed by codex at `2026-09-20T19:42:47Z`; launcher durably committed/pushed claim **99b6ec2f7d8429c1ed606e75f539cc814354a10a**.
- Implementation correction commit above is pushed. The parent report revision is the commit containing this report, published on the mirrored branch. Parent edits are limited to this task file; Architect Review and execution authorization preserved byte-for-byte.
- No gitlink, architecture, index, other task, main merge/push, deployment, downstream promotion or self-acceptance.

### Attempt 2 — Ready for Review (2026-09-20)

Implemented the architect-authorized Docker fixture and supplied the previously
missing real PostgreSQL/Redis readiness evidence. Implementation
`8c8b8250954aec9d6f011130bf05f620c35dff04` is committed and pushed on
`task/ARCH-020-COMMERCE-001`. Task status is **review**; no architect acceptance
decision has been made by this agent. The Attempt 1 report and architect review
below are retained as historical evidence; their pending local-readiness handoff
is superseded by this successful authorized execution.

#### Authorization checklist and changed files

- Repeatable single command: `package.json` declares `npm run test:readiness-docker`;
  `scripts/readiness-docker.mjs` provisions dependencies, waits for final PostgreSQL
  TCP readiness/Redis PONG, applies the existing schema, builds, then runs the probe.
- Isolation: unique invocation names/labels, own network, loopback ephemeral ports,
  generated synthetic credentials, tmpfs storage and no persistent volumes.
  Rejects remote Docker contexts and dotenv files; no shared service credentials
  are inherited. No canonical schema/migration change or application startup migration.
- Bounded failure handling: per-command deadlines, bounded/redacted child output,
  process-group termination with a two-second kill grace, owned-resource cleanup
  on success/failure/SIGINT/SIGTERM and preservation of validation failure exit codes.
  Cleanup checks ownership labels, includes stopped containers, and reports failure.
- Evidence: `scripts/readiness-local-smoke.mjs` now prints status and elapsed time;
  `tests/readiness-docker.test.ts` covers isolated target construction, partial
  setup cleanup, cancellation, ownership mismatch, remote-context rejection,
  failure-code preservation, redaction and forced termination.
- `README.md` and `docs/runtime-compatibility.md` document the command, prerequisites,
  resource boundaries, cleanup and the lower-level read-only validator.

#### Requirement-to-fixture results

| Requirement / fixture | Expected effects | Actual command / result |
| --- | --- | --- |
| Existing foundation plus new lifecycle tests | Local mock/loopback/subprocess checks only | `npm test`: **27 passed, five suites** |
| Types and lint | Local generated types/cache only | `npm run typecheck`, `npm run lint`: **passed** |
| Disposable local infrastructure | Pull two official images; create only own network and two tmpfs containers | `npm run test:readiness-docker`: **passed, exit 0** |
| Pinned schema | Apply recorded Prisma schema only to the new empty local fixture database | Docker command's `prisma db push --schema database/prisma/schema.prisma --skip-generate`: **passed** |
| Production build | Generate pinned client/build locally; no app startup migrations | Docker command's `npm run build`: **passed** |
| Real healthy connectivity | Read-only SQL/schema check and Redis PING through production Next process | **HTTP 200 ready, 226.4 ms** |
| Unavailable Redis | Probe unreachable loopback endpoint; no shared service stopped | **HTTP 503 not_ready, 136.7 ms** |
| Unavailable PostgreSQL | Probe unreachable loopback endpoint; no shared service stopped | **HTTP 503 not_ready, 98.2 ms** |
| Invalid verification keys | Fresh app process with synthetic invalid key configuration | **HTTP 503 not_ready, 58.3 ms** |
| Cleanup | Remove own containers/network only; no persistent volumes | **passed**; independent label-filtered container/network inventory returned no resources |
| Git/schema ownership | No whitespace errors or nested database modifications | `git diff --check`, nested `git status --short`: **passed/clean** |

Full fixture ran once successfully on local Docker Engine **29.5.2**, Node
**24.19.0**, npm **11.17.0**, with implementation source subsequently committed
unchanged as `8c8b8250954aec9d6f011130bf05f620c35dff04` (the fixture printed its
pre-commit base `3ae6c7f12f2f0f6467c93ca49012967f26d16b44`). Database pin:
`9c6a4d8402a01840e2ea8dc18e89171f00564d29`.

Exact command: `npm run test:readiness-docker` from the canonical implementation
worktree, after the workspace Node bootstrap. No credentials supplied by the user
or loaded from deployment configuration. Run ID:
`commerce-readiness-c2d65f87-1cf7-4d4e-b0aa-6e9f94ac6f55`.

Resolved official image versions/digests:

- `postgres:16.4-alpine` → `postgres@sha256:5660c2cbfea50c7a9127d17dc4e48543eedd3d7a41a595a2dfa572471e37e64c`.
- `redis:7.4.0-alpine` → `redis@sha256:c35af3bbcef51a62c8bae5a9a563c6f1b60d7ebaea4cb5a3ccbcc157580ae098`.

During development, one ownership-test mock incorrectly intercepted Docker context
inspection and TypeScript exposed test/helper annotation issues; corrected before
successful validation. Initial Node bootstrap from the implementation sibling
could not resolve the primary workspace; sourcing the existing bootstrap from the
canonical primary workspace resolved this without host/toolchain changes.

No remaining required real local-readiness evidence gap. The previously reviewed
Prisma/deepmerge-ts audit limitation remains unchanged. SIGKILL/host failure cannot
run cleanup; documentation identifies the run ID for manual scoped inspection.
No deployed/provider validation, browser rerun or redundant clean-clone run was
needed for this script-only addition; prior foundation evidence remains recorded.

#### Prepared launcher / publication evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-001`;
  implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-001`.
- Both branches: `task/ARCH-020-COMMERCE-001`; both canonical worktrees reused.
- Both remote task fast-forwards `not-needed`; both origin/main incorporation
  `already-current`; dependency gate passed (no dependencies).
- Prepared parent HEAD `767b526f04a81f1edf3b0a46173e75bd7fa0a214`; implementation
  HEAD `3ae6c7f12f2f0f6467c93ca49012967f26d16b44`.
- Recursive submodule sync/update passed, status ready, database at
  `9c6a4d8402a01840e2ea8dc18e89171f00564d29`; no repeated startup preparation.
- Attempt 2 claimed by codex at `2026-09-20T19:19:18Z`; durable claim committed and
  pushed by launcher as `cb2abb9968a94ced5c9b75bc9f1ee18d8c163e52`.
- Implementation commit above pushed to Commerce origin/task/ARCH-020-COMMERCE-001.
  This report's containing commit is the parent report revision and is published
  on the mirrored parent branch. Only this task file is staged in parent.
- No shared/default checkout switched or mutated, other task worktree reused,
  parent gitlink staged, architecture/index edited, main merge/push, deployment,
  downstream launch or self-acceptance.

### Attempt 1 report (historical)

### Status

Attempt 1: Ready for Review. Implementation and bounded local checks are complete. Real PostgreSQL/Redis healthy-readiness evidence remains developer-owned and pending before acceptance. No architect acceptance decision has been made by this agent.

### Files Changed

Implementation commit `3ae6c7f12f2f0f6467c93ca49012967f26d16b44`:

- App Router layout/static setup page, responsive CSS, exact `/health/live` and `/health/ready` Node routes.
- `.nvmrc`, exact dependency package/lockfile, Next/TypeScript/ESLint/Vitest configuration and declared scripts.
- Canonical nested `database/` gitlink and `.gitmodules`, no copied or edited schema.
- Server-only configuration/Prisma/Redis/readiness modules.
- Reusable `PendingActionForm` and synthetic behavioral tests.
- Test-only MCP Next Request/Response adapter fixture and actual SDK client loopback test.
- Production-process health smoke, fresh recursive clone validator, developer local-dependency validator, `.env.example`, README and `docs/runtime-compatibility.md`.

### Work Completed

The foundation runs Next.js 16.3.5 / React 19.3.0 on workspace Node 24.19.0. The pinned Prisma 6.19.3 client is generated from the canonical database submodule. Clean builds initialize recorded submodule pins before generation; no startup/build migrations are introduced.

Liveness performs no external check. Readiness validates required configuration, one/two unique RSA public verification keys, database SELECT 1 and integrated foundation identity/shop columns, and Redis PING. It has a 1.8-second response deadline, bounded pool/connect/query work, no retries for Redis and no exception/credential details in the returned response. Missing published releases are not a readiness dependency. Future schema consumers must extend foundation checks when their tables exist.

The static setup page exposes no business data or business action. Staff authentication and live MCP remain their owning tasks. The compatibility fixture lives outside the production app route tree, uses synthetic credentials/data and a fresh stateless SDK server for each request. The actual pinned SDK client successfully performs initialize/initialized notification, resource list/read, prompt list/get and tool list/call using NextRequest/Response over loopback HTTP with JSON responses and no session ID/SSE dependency. This is a protocol/adapter fixture, not a production service-authority implementation or a Shared manifest implementation.

The reusable form acquires its guard before awaiting, immediately disables the conflicting fieldset, provides accessible pending feedback, keeps input after known failures and holds unknown outcomes until reconciliation of the same operation ID. Unmounted/stale completion is ignored. There is no global navigation lock. Server replay/authentication remains an independent requirement for future business-action owners; this task creates no server mutation endpoint.

### Validation Results

All commands below ran in the canonical implementation worktree with Node 24.19.0 unless stated otherwise.

| Requirement / fixture | Expected side effects | Command / evidence | Actual result |
| --- | --- | --- | --- |
| Canonical schema client | Generated local client only; no migration/query | `npm run prisma:generate` | PASS; Prisma 6.19.3, database pin below |
| MCP C5 stateless profile | Synthetic loopback HTTP only, no provider calls | `npm test`, `tests/mcp-compatibility.test.ts` | PASS; initialize protocol 2025-11-25, resources/prompts/tools, JSON/no session, GET/DELETE 405, Origin/batch/credential rejection |
| Readiness/configuration | Mock dependency checks, synthetic RSA keys | `npm test`, `tests/health.test.ts` | PASS; success/failure/redaction/config rejection and 1.8-second abort behavior |
| Pinned SQL adapter | Mock transaction plus actual pinned schema inspection | `npm test`, `tests/database-contract.test.ts` | PASS; exact SELECTs, existing schema/columns, transaction limits and no release/migration reads |
| UI duplicate action | Synthetic local promise only | `npm test`, `tests/pending-action-form.test.tsx` | PASS; same-tick duplicate submit/button/keyboard paths, accessible busy feedback, retry after known failure, unknown reconciliation and stale completion |
| All focused tests | Local only | `npm test` | **19 passed, four suites** |
| Types/lint | Local generated types/cache only | `npm run typecheck`; `npm run lint` | **PASS**, no diagnostics |
| Production build | Local client and Next build output only | `NEXT_TELEMETRY_DISABLED=1 npm run build` | **PASS**; root, not-found and two health routes only |
| Production process | Own temporary loopback process, no shared config | `npm run test:health` | **PASS**; live 200, missing-dependency ready 503, root 200, MCP GET/POST/DELETE 404 |
| Fresh recursive clone | Own temporary checkout/npm installation, cleaned afterward | `npm run test:clean-clone` at `3ae6c7f12f2f0f6467c93ca49012967f26d16b44` | **PASS**; npm ci, recorded database pin, Prisma generation, production build/start/health |
| Responsive shell | Local browser only | In-app browser at 1024px and 320px | **PASS**, no mobile horizontal overflow; viewport and task tab cleaned up |
| Client boundary | Read-only built bundle scan | `rg -l 'PrismaClient|COMMERCE_ASSERTION_PUBLIC_KEYS|AUTH_GOOGLE_SECRET|DATABASE_URL' .next/static` | No matches; server modules additionally use server-only |
| Git/submodule | Read-only checks | `git diff --check`; `git submodule status --recursive` | **PASS**, exact database pin, no nested edits |
| Real healthy readiness | Read-only SELECT/PING to disposable local services, own app processes | `npm run test:readiness-local` with explicit local fixture URLs | **PENDING developer execution**; unit-injected success does not establish real PostgreSQL/Redis connectivity |

Developer validation required after provisioning disposable local PostgreSQL with the pinned schema and local Redis:

```sh
npm run build
COMMERCE_TEST_DATABASE_URL='postgresql://fixture:fixture@127.0.0.1:5432/commerce_fixture' \
COMMERCE_TEST_REDIS_URL='redis://127.0.0.1:6379' npm run test:readiness-local
```

Replace placeholders with disposable local credentials. The validator rejects remote hosts, uses synthetic keys/OAuth placeholders, starts/stops only its own Next processes, and never migrates or mutates records. Expected: healthy 200 ready; unreachable database, unreachable Redis and invalid keys 503 not_ready, each within two seconds. Infrastructure preparation and its real-dependency evidence are developer-owned under the validation policies; no shared/deployed credentials were inspected or used. Required evidence remains pending before acceptance.

### Deviations

No business scope expansion. The MCP fixture uses the SDK's Web Standard transport directly with NextRequest/Response, avoiding an unnecessary third-party adapter; the pinned SDK client verifies compatibility. No production MCP route/auth bypass exists.

### Assumptions

Database main revision `9c6a4d8402a01840e2ea8dc18e89171f00564d29` is the integrated foundation schema. ARCH-020-DATABASE-001 and subsequent service tasks own the future commerce tables and consumption. No dependency acceptance was inferred from a task snapshot.

### Unresolved Issues

- Developer real PostgreSQL/Redis readiness evidence above is pending; it is not represented as passed.
- `npm audit` reports three high findings in the build-time Prisma 6.19.3 → @prisma/config → deepmerge-ts chain, GHSA-ggr8-5vv4-36mx (recursive-object stack exhaustion). Only trusted checked-in Prisma configuration is consumed. No untested major override/force downgrade was applied. This toolchain limitation is documented for architect review; production request handlers do not merge user-controlled Prisma configuration.

### Architectural Concerns

No new cross-repository implementation requirement. Background must consume the recorded MCP compatibility set while independently implementing the C5 assertion/grant contract. Gateway receives exact build/start/port/private health contracts in runtime-compatibility.md. Later mutation owners must supply durable server replay and status reconciliation independently of the reusable browser guard.

### Git / VCS

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-001`; branch `task/ARCH-020-COMMERCE-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-001`; same task branch.
- Prepared launcher reused parent, created implementation, passed dependency gate (no dependencies), and completed fetch/prune/synchronization. Both remote task fast-forwards were not needed and origin/main was already incorporated. Initial parent HEAD `3d00af0fda3ded8305d178d900ee21a48c00619e`; implementation HEAD `01c550c3e3f55dd23a4ecc9514c846bb88cf2067`.
- Initial recursive sync/update passed with no submodules. This task added the authorized nested `database/` from `https://github.com/kodjobaah/moda-interact-database.git` at integrated pin `9c6a4d8402a01840e2ea8dc18e89171f00564d29`; fresh recursive clone and final status verify it. No update --remote or nested schema edit.
- Attempt 1 claimed by codex at `2026-09-20T18:30:42Z`; durable parent claim `ad47a97692321dccad7fbe2f54ef893e8ffed917` committed/pushed by launcher.
- Implementation committed/pushed: `3ae6c7f12f2f0f6467c93ca49012967f26d16b44` to the provisioned private moda-interact-commerce origin/task/ARCH-020-COMMERCE-001.
- This task report is committed/pushed on the mirrored parent branch; the containing Git commit is the report revision. Only this task document is staged in parent.
- Shared/default checkouts were not switched or mutated for implementation; no other task worktree reused. No parent service gitlink, architecture, index, main merge/push, deployment or enabled-task execution.

## Architect Review

### Current review — Attempt 3, Accepted (2026-09-20)

**Accepted.** Reviewed implementation `d7c1c65bf382de1538d77ac4dbe65c1d7fcd1276`
and report `a257985d44f5464a71c2ff3ecc1f79557e9ec84e`, both verified at their
published task-branch heads. With `completion_mode: automatic`, COMMERCE-001 is
**Complete at Attempt 3**. This decision supersedes the historical reviews below.

The functional cleanup defect is resolved. `commandRunner` now retains an
idempotent process-group teardown promise independently of the leader's close,
keeps the two-second SIGKILL escalation, and awaits it before returning control.
The correction preserves original command failure codes and the fixture's scoped
Docker cleanup. No provisioning, schema, dependency or application behavior changed.

Architect executed `npm test -- tests/readiness-docker.test.ts`: **10 passed**,
including real ignored-stdio descendants surviving SIGTERM until bounded forced
termination under both timeout and AbortSignal. The supplied full suite has
**29 passing tests**; typecheck and lint passed. Committed whitespace checks pass.
Review is focused on the required functionality and reproduced defect; no broader
test-coverage or additional infrastructure run is required for acceptance.

The successful real Docker evidence from Attempt 2 is retained: healthy readiness
200 (226.4 ms), unavailable Redis 503 (136.7 ms), unavailable PostgreSQL 503
(98.2 ms), invalid keys 503 (58.3 ms), production build success and owned-resource
cleanup. The unchanged database pin is `9c6a4d8402a01840e2ea8dc18e89171f00564d29`.
Earlier foundation/build/clean-clone/MCP compatibility evidence remains applicable.
No redundant Docker, build or clean-clone run was performed by this review.

Physical worktree isolation, prepared Attempt 3 claim, synchronization/submodule
records and mirrored publication agree with the report. No blocking functional
finding remains. The previously reviewed Prisma/deepmerge-ts audit limitation is
unchanged and nonblocking under its recorded trusted-build-configuration scope.

Integration and dependency disposition: the developer still owns implementation
PR #1 and parent report PR #166 merges and the final parent gitlink update.
Implementation main remains the scaffold revision `01c550c3`; this acceptance does
not merge or authorize implicit consumption of unmerged source. COMMERCE-002's
sole task dependency is now satisfied, but it remains Pending until developer
integration or explicit accepted-commit consumption is established. Background
and terminal system-test dependencies are not yet all satisfied; no downstream
task is launched or promoted by this review. ARCH-020 remains unfinished.


### Historical review — Attempt 2, Changes Requested (2026-09-20)

Reviewed published implementation `8c8b8250954aec9d6f011130bf05f620c35dff04`
and report `f799eeb1b83bf259899438782d48a0bf7b240ad1`. **Changes Requested**:
one reproducible process-cleanup defect remains. Task returns to `ready`,
executor/claimed_at cleared, Attempt 2 retained. No Attempt 3 is claimed and no
dependant is promoted. This is the authoritative correction contract; the
Attempt 1 review below is historical.

#### Blocking finding — P2: preserve process-group teardown after leader exit

`scripts/readiness-docker.mjs:29–32` calls `finish()` when the direct child emits
`close`; `finish()` clears the pending `force` timer. On timeout/abort, that timer
is the only scheduled SIGKILL for the detached process group. A parent that exits
on SIGTERM can therefore cancel escalation while its descendant is still alive.
This is relevant to the actual fixture: `readiness-local-smoke.mjs` starts Next
with ignored stdio, so closing the immediate script does not wait for Next or
prove that the process group is gone. The runner can report cleanup and return
while leaving a fixture application process running.

A bounded synthetic reproduction imported the committed `commandRunner`, used a
1000 ms timeout, and launched a Node parent that spawned an ignored-stdio child
with a no-op SIGTERM handler. The runner rejected with `cancelled/timed out`;
2500 ms later `process.kill(descendantPid, 0)` still succeeded. The reviewer then
SIGKILLed only that synthetic descendant. No Docker service or shared process was
used for the reproduction.

Required source/test corrections on the same task branches:

1. Retain and await bounded process-group teardown after timeout or AbortSignal
   cancellation even when the group leader closes before the two-second grace
   period. Do not treat leader exit as proof of descendant termination. Preserve
   command failure and SIGINT/SIGTERM exit-code behavior and owned-resource cleanup.
2. Add behavioral regressions for both timeout and AbortSignal with an
   ignored-stdio descendant that ignores SIGTERM while its parent exits. Assert
   the descendant/process group is no longer running within the bounded teardown
   deadline; ensure the test itself cleans up if the assertion fails. Keep the
   existing single-process timeout and Docker ownership/cleanup tests.
3. Run the focused regression, `npm test`, `npm run typecheck`, `npm run lint` and
   `git diff --check`; report outcomes and publish both mirrored branches. Existing
   happy-path Docker readiness evidence below remains valid; no repeat of the
   entire Docker/build fixture is required solely for this correction unless
   relevant provisioning/readiness behavior changes or new failures justify it.

#### Conformance and evidence retained

The prior real PostgreSQL/Redis evidence gap is closed. The supplied authorized
run built production and returned healthy 200 in 226.4 ms, unavailable Redis 503
in 136.7 ms, unavailable PostgreSQL 503 in 98.2 ms, and invalid keys 503 in 58.3 ms;
all satisfy C10's two-second deadline. Exit 0, image digests, database pin,
invocation identity and successful Docker cleanup were recorded. This review did
not redundantly rerun the full Docker fixture/build/clean clone.

The fixture otherwise preserves the scoped boundary: official versioned images,
unique labelled resources, loopback ephemeral ports, synthetic credentials,
tmpfs storage, selected local Docker context, isolated child environments, dotenv
refusal and ownership-verified container/network removal. Existing canonical
schema is applied only to the fresh disposable database; no schema ownership or
application-start migration change. Runtime endpoints and business behavior are
unchanged. The documented Prisma/deepmerge-ts limitation retains its prior review
disposition; no clean-audit claim is made.

Architect reran `npm test`: **27 passed, five suites**. Those tests cover a single
SIGTERM-resistant direct child, but not the confirmed descendant case. Supplied
typecheck/lint/build evidence is passing. Published remote heads, prepared claim,
dedicated mirrored worktrees and pinned submodule evidence agree with the report.
No implementation edits or main integration were made during this review.

### Historical Attempt 1 review

### Review Status

**Acceptance withheld — pending required developer validation, Attempt 1, 2026-09-20, moda_architect.** Task remains `review`; no new implementation attempt, Complete transition or downstream promotion.

Reviewed implementation `3ae6c7f12f2f0f6467c93ca49012967f26d16b44` and report `1ff2eafc3372332ec4c77f80ae0030e8254fd199`; both published remote heads verified. No blocking code defect found in the inspected foundation. This is not acceptance: real PostgreSQL/Redis readiness evidence is still required by the task and C10/C12.

### Review Notes / Architecture Conformance

The Node App Router foundation, exact dependency pins, nested canonical database gitlink, generation/build/start contracts and server-only connection/configuration boundaries conform to the scoped task. Liveness is independent of dependencies. Readiness has generic responses, bounded work/deadline, required configuration/key checks and no release-publication or startup-migration dependency. The stateless MCP compatibility fixture uses the pinned SDK client and Next Request/Response objects outside the production route tree; it is not production authorization. The pending form synchronously guards dispatch, retains unknown operations for reconciliation and ignores stale completion; future business endpoints still require independent server replay/authentication.

**Required evidence gap:** mocked readiness success and a production 503 smoke do not establish healthy real connectivity/schema compatibility. C12 states: “missing evidence prevents acceptance”. Record real healthy 200, unavailable PostgreSQL 503, unavailable Redis 503 and invalid-key 503, each within two seconds, against disposable local services with the recorded schema. The supplied validator is read-only and starts/stops its own application processes; it does not provision or migrate the dependencies.

The reported Prisma/deepmerge-ts audit findings remain a documented toolchain limitation. Inspected request paths do not merge untrusted Prisma configuration; no dependency override or upgrade is required by this review. This disposition does not claim the dependency audit is clean; future changes to configuration inputs/runtime exposure must revisit it.

### Reviewed Files

Package/lockfile and runtime documentation; Next app/routes/config; server configuration, Prisma/Redis connections and readiness; pending form and behavioral tests; test-only MCP adapter/client fixture; health/database tests; production health, clean-clone and local-readiness scripts; nested database pin; task preparation/report evidence.

### Validation Reviewed

- Architect reran `npm test`: **19 passed across four suites**.
- Architect reran `npm run typecheck` and `npm run lint`: **passed**, no diagnostics.
- Architect reran `npm run test:health`: **passed** — production live 200, missing-config readiness 503, root 200 and production MCP GET/POST/DELETE 404.
- Build and fresh-recursive-clone success are supplied implementation evidence; no redundant rebuild/reclone performed. Read-only built-static scan found none of the tested server credential/client markers.
- Recursive database status matches `9c6a4d8402a01840e2ea8dc18e89171f00564d29`; committed whitespace checks pass and implementation worktree remains clean. Dedicated mirrored worktree/synchronization/claim evidence agrees with the report.
- Real PostgreSQL/Redis success/failure validation was not run by this review and remains pending. No shared/deployed service or credential was used.

### Follow-up

From the canonical Commerce implementation worktree, after provisioning disposable local PostgreSQL with the pinned schema and local Redis, run:

```sh
npm run build
COMMERCE_TEST_DATABASE_URL='<disposable-local-postgresql-url>' \
COMMERCE_TEST_REDIS_URL='<disposable-local-redis-url>' npm run test:readiness-local
```

Provide the tested implementation/database SHAs, environment, command with credentials redacted, all four scenario results/timings and exit code. Do not claim Attempt 2 merely to supply evidence; retain Attempt 1 review state unless a validation failure requires implementation correction. The architect can complete acceptance after reviewing that evidence. COMMERCE-002 and other dependants remain gated; terminal system-test execution remains explicitly developer-invoked.

## Architect execution authorization — disposable Docker readiness fixture

The developer explicitly requests that this task provision and run its own local PostgreSQL and Redis in Docker, adding a repeatable setup script. This supersedes the earlier developer-execution-only handoff for this exact validation. Task returns to Ready, unclaimed, retaining Attempt 1 and its review; the normal launcher may claim Attempt 2 for the script and evidence work. This is an authorized scope addition, not a newly discovered defect in the reviewed foundation.

moda_commerce owns the implementation repository script/package command, usage documentation and task report. Add a single documented command that provisions disposable local PostgreSQL and Redis, waits with bounded deadlines, prepares the existing pinned schema only inside its own disposable database, builds/starts the application as needed, and runs `test:readiness-local`. Use pinned official container images, synthetic credentials, unique run-scoped names and loopback-bound ephemeral ports to avoid existing services. Never consume shared/deployed database/Redis credentials, change the canonical schema/migrations, or use global Docker prune/volume deletion.

The developer authorizes pulling those images, creating the isolated containers/network/volumes, applying the existing pinned schema to that disposable database, running the healthy and failure readiness scenarios, and cleaning up only resources created by the invocation. Cleanup must cover success, failure and signals and preserve the validation exit code. If Docker is unavailable, report the concrete environment blocker; do not install or reconfigure Docker without separate authorization. Keep logs bounded and redact connection secrets.

Run the complete local fixture once after implementation; investigate genuine failures and rerun affected checks only after a relevant correction. Record app/database revisions, image versions, exact command, all scenario outcomes/timings, exit code and cleanup evidence. Include healthy 200, unavailable database 503, unavailable Redis 503 and invalid-key 503 within the contract deadline. Preserve the reviewed foundation and prior evidence. Commit/push both mirrored task branches, return to review, and stop for architect acceptance. No production endpoint/deployment, main integration, downstream execution or other repository implementation is authorized.
