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
status: review
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-002
  - ARCH-020-SYSTEM-TEST-001
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
- ARCH-020-COMMERCE-002
- ARCH-020-SYSTEM-TEST-001

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
