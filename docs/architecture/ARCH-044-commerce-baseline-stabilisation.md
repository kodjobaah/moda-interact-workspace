---
id: ARCH-044
title: Commerce baseline stabilisation
status: agreed
coordinator: moda_architect
created: '2026-10-18'
updated: '2026-10-18'
---

# ARCH-044: Commerce baseline stabilisation

## Status

Agreed for **eight portable task definitions**. These files have not been materialised in the developer's Git worktrees/branches, and no implementation has been executed or accepted by this architectural definition. All implementation belongs to `moda_commerce` in `moda-interact-commerce`.

## Problem

Unchanged Commerce baseline testing on 2026-10-18 confirms extensive real validation debt. Treating failures as "pre-existing" is useful for attribution but does not repair them. The developer has approved a focused repair initiative rather than broadening `ARCH-043-COMMERCE-002` with unrelated Studio/Code Runtime changes.

**Evidence sources**: supplied unchanged baseline `baseline-vitest.log` and ARCH-043 Commerce run `typescript(20261018-183033)`; log names identify the evidence provided in the architect conversation, not committed repo paths. Record exact baseline Git commit and task-branch Git commit during execution because their SHAs were not supplied with the logs.

| Metric | Unchanged Commerce baseline | ARCH-043 task worktree |
|---|---:|---:|
| Test files total | 188 | 193 |
| Test files passed | 169 | 173 |
| Test files failed | 15 | 16 |
| Test files skipped | 4 | 4 |
| Test assertions passed | 1,400 | 1,414 |
| Test assertions failed | 38 | 39 |
| Test assertions skipped | 11 | 11 |
| Suites failing before tests run | 6 | 6 |
| ESLint | 2 errors, 15 warnings | 2 errors, 15 warnings |

All **38** baseline failing assertion identities also occur in the ARCH-043 run. The task run had one additional Code Runtime proof failure, `tests/code-runtime-proof.test.ts` (supervisor termination after built-in starts), with `started === false` at a 400-ms deadline. That difference is not yet classified as a product regression; isolated and concurrent reproduction is required.

The baseline `npm run code-runtime:smoke` passed while the ARCH-043 worktree previously failed `packaged v2 compile did not preserve compile-only behavior` in `scripts/code-runtime-packaged-smoke.mjs:68`. The engine artifact SHA-256 matched (prefix `d4c9375f`), while `helpers-v2.js` SHA-256 differed (baseline `83fe8b71`, task `070d8bd1`). **This is a diagnostic difference, not proof of a specific root cause.**

The unchanged repository declares `engines.node: 24.19.0`; an operator environment reported Node `24.21.0`. Installed tooling and dependency versions must be recorded before changing runtime logic. Previous mixed `npm ci` and `pnpm exec` caused `ERR_PNPM_IGNORED_BUILDS`; the successful full baseline comparison used npm commands.

## Goals

1. Return Commerce to a reproducible, fully understood build, lint and comprehensive test state with **zero unexplained failures**.
2. Fix genuine defects, correct obsolete tests, and provide safe disposable integration testing; never weaken security/consistency semantics merely for green results.
3. Preserve standalone MCP extraction: Shopify Admin live Test in Commerce is currently deferred and tests must not reactivate embedded MCP tooling.
4. Keep the work in eight independently reviewable Commerce tasks; accept each on its own evidence and integrate without destabilising ARCH-043 database-backed configuration.

## Non-Goals

- Reimplementing standalone MCP live Shopify Test, new Commerce products, or alternative credential/configuration systems.
- Disabling failing test files, deleting assertions, suppressing global lint rules, or increasing timeouts without measured justification.
- Migrating Prisma schema/adding migrations in Commerce, changing Shared contracts without separate ownership review, deploying Gateway changes or touching other repositories.
- Treating `ARCH-043-COMMERCE-002` as a hidden dependency of this initiative or silently marking it Complete.

## Current Architecture

Commerce uses Next.js, Auth.js, TypeScript/Vitest, Prisma/PostgreSQL, Redis where needed, QuickJS-WASI for bounded Code Runtime and a modular Studio Tool authoring UI. Test runner `npm test -- --maxWorkers=4` delegates to `vitest run --maxWorkers=4` after schema sync. Commerce package scripts include `code-runtime:package`, `code-runtime:smoke`, `test:arch020-backend-integration:postgres` and `test:arch043-platform-configuration:disposable`; `prisma:generate` synchronises the `database` submodule before client generation. Specific assumptions must be verified against the task worktree's package manifest at execution time.

The current persisted Shopify Admin Tool Test tab explicitly says `Live Shopify Admin tests are deferred until standalone MCP integration is restored.` Yet many older tests assert a `Run Test` control and C082 live execution; this is **documented expectation drift**, not authorisation to reintroduce live execution.

## Baseline failure inventory

The 38 failed assertions group as follows. The source log has full Vitest error detail; task files contain the exact case names and expected corrective checks.

| Owning task | Area | Baseline failed assertions |
|---|---|---:|
| `ARCH-044-COMMERCE-003` | Persisted Shopify Admin Tool authoring (includes Policy Operation paths) | 19 |
| `ARCH-044-COMMERCE-004` | New Tool authoring UI | 7 |
| `ARCH-044-COMMERCE-005` | Studio Workspace authoring UI | 6 |
| `ARCH-044-COMMERCE-002` | Discovery admission 60/61 timeout | 1 |
| `ARCH-044-COMMERCE-004` | WooCommerce provider-local component boundary | 1 |
| `ARCH-044-COMMERCE-006` | Agent template error-code expectation | 1 |
| `ARCH-044-COMMERCE-006` | MCP extraction dependency assertion | 1 |
| `ARCH-044-COMMERCE-007` | Retained Agent configuration model/prompt CAS | 1 |
| `ARCH-044-COMMERCE-007` | Publication PostgreSQL transaction expiry | 1 |
| **Total** | | **38** |

Six additional suite import/setup failures (not included in the 38 assertion count) are owned by COMMERCE-002: `agent-configuration-model-postgres`, `agent-configuration-prompts-postgres`, `c20-integration-fixture`, `preview-openrouter-postgres`, `studio-integration-c20` and `tool-editor-dispatch` (all under `tests/`). The first five require disposable database/Redis configuration, while the sixth lacks `ResponseTemplateSchema` in a test mock.

### Every baseline failing assertion (exact test identity)

| # | Test identity | Repair task |
|---:|---|---|
| 01 | `tests/agent-configuration-retained-read.test.ts > retained agent configuration reads > tracks model and prompt CAS versions on one retained row across clear operations` | `ARCH-044-COMMERCE-007` |
| 02 | `tests/agent-contract-validation.test.ts > deprecated validateAgentContract compatibility adapter > rejects unknown scalar paths and non-list items paths` | `ARCH-044-COMMERCE-006` |
| 03 | `tests/backend-postgres-rehearsal.test.ts > ARCH-020 Commerce-013 PostgreSQL adapter rehearsal > publishes once, replays durably, rejects stale CAS, races across connections, and rolls back injected failure` | `ARCH-044-COMMERCE-007` |
| 04 | `tests/commerce-mcp-extraction-boundary.test.ts > ARCH-032-COMMERCE-005 complete MCP extraction boundary > does not ship an embedded MCP route or server, and keeps only a private thin live client` | `ARCH-044-COMMERCE-006` |
| 05 | `tests/discovery-limits.test.ts > discovery admission > allows 60 sequential requests and rejects the 61st in the rolling window` | `ARCH-044-COMMERCE-002` |
| 06 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > offers Admin GraphQL and saves the exact validated definition` | `ARCH-044-COMMERCE-003` |
| 07 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > requires a current Shopify Test for Save and shows the exact server-rendered result without writes` | `ARCH-044-COMMERCE-003` |
| 08 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > stales a successful Shopify Test when arguments change without persisting the transient edit` | `ARCH-044-COMMERCE-003` |
| 09 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > does not call C082 when no Studio shop is selected` | `ARCH-044-COMMERCE-003` |
| 10 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > disables Shopify Test when the selected shop has no offline session` | `ARCH-044-COMMERCE-003` |
| 11 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > marks a failed C082 stage FAILED and never exposes a passed rendered result` | `ARCH-044-COMMERCE-003` |
| 12 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > prevents an old run from resurfacing after shop and arguments both cycle A-to-B-to-A` | `ARCH-044-COMMERCE-003` |
| 13 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > saves once with the current CAS token and refreshes from the canonical revision` | `ARCH-044-COMMERCE-003` |
| 14 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > keeps a Shopify CAS conflict visible without refreshing or overwriting local edits` | `ARCH-044-COMMERCE-003` |
| 15 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > persists editable JSON string and numeric literal mappings` | `ARCH-044-COMMERCE-003` |
| 16 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > recomputes aggregate validity when a literal mapping switches to an input mapping` | `ARCH-044-COMMERCE-003` |
| 17 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > keeps another invalid literal mapping invalid while fixing one literal` | `ARCH-044-COMMERCE-003` |
| 18 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > ignores invalid literal state for variables removed from the current document` | `ARCH-044-COMMERCE-003` |
| 19 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > derives and displays a read-only result shape without saving a persisted draft` | `ARCH-044-COMMERCE-003` |
| 20 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > does not accept an old Shopify Review validation after candidate A-to-B-to-A` | `ARCH-044-COMMERCE-003` |
| 21 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > saves the compiler-produced schema while preserving the persisted response template` | `ARCH-044-COMMERCE-003` |
| 22 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > keeps Admin publication disabled for ADMIN and surfaces the typed live-test gate for SUPER_ADMIN` | `ARCH-044-COMMERCE-003` |
| 23 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > saves, publishes through the canonical action, and reopens the exact Policy binding read-only` | `ARCH-044-COMMERCE-003` |
| 24 | `tests/shopify-admin-tools-ui.test.tsx > Shopify Admin tool authoring UI > preserves Policy local edits on CAS conflict and unknown mutation outcome without retrying` | `ARCH-044-COMMERCE-003` |
| 25 | `tests/studio-workspace.test.tsx > Studio connected browser workflows > exposes the failure class when a named Studio action rejects unexpectedly` | `ARCH-044-COMMERCE-005` |
| 26 | `tests/studio-workspace.test.tsx > Studio connected browser workflows > authors a reusable tool without publishing and navigates to its returned ID` | `ARCH-044-COMMERCE-005` |
| 27 | `tests/studio-workspace.test.tsx > Studio connected browser workflows > retains incremental invalid JSON and saves only the complete canonical tool definition` | `ARCH-044-COMMERCE-005` |
| 28 | `tests/studio-workspace.test.tsx > Studio connected browser workflows > resets editor state when a mounted detail changes to another record` | `ARCH-044-COMMERCE-005` |
| 29 | `tests/studio-workspace.test.tsx > Studio connected browser workflows > keeps newer edits dirty when an earlier save completes` | `ARCH-044-COMMERCE-005` |
| 30 | `tests/studio-workspace.test.tsx > Studio connected browser workflows > retains editor input after stale CAS` | `ARCH-044-COMMERCE-005` |
| 31 | `tests/tool-authoring-request-component-boundaries.test.ts > new Tool authoring component boundaries > keeps WooCommerce Response authoring provider-local while reusing the shared Result Template stage` | `ARCH-044-COMMERCE-004` |
| 32 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > does not unlock the first Review step after a failed Test` | `ARCH-044-COMMERCE-004` |
| 33 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > does not unlock the first Review step after a stale Test` | `ARCH-044-COMMERCE-004` |
| 34 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > preserves edited local definition values through tab switches` | `ARCH-044-COMMERCE-004` |
| 35 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > validates and creates the exact current Admin candidate without intermediate persistence` | `ARCH-044-COMMERCE-004` |
| 36 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > uses exact returned identities after confirmed creation` | `ARCH-044-COMMERCE-004` |
| 37 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > reconciles a lost final create without replaying the mutation` | `ARCH-044-COMMERCE-004` |
| 38 | `tests/tool-authoring-screen.test.tsx > ToolAuthoringScreen new-tool local creation > cancels from Review without writing and returns to Tools` | `ARCH-044-COMMERCE-004` |

## Proposed Architecture

Create **eight** independently reviewable repository-owned tasks with one canonical parent initiative. Repair work proceeds from measured evidence: classify whether a failing assertion represents a genuine defect, a stale expectation or an unavailable safe fixture; then apply the smallest behavior- and architecture-conformant correction.

The initiative needs **no new Gateway, Shared or Database implementation task** on inspected evidence. If investigation proves that a schema change, new Shared primitive, standalone MCP implementation or deployment topology change is necessary, stop that boundary and return to `moda_architect` for a separate owning task rather than making cross-repository edits inside Commerce.

## Request / Test Flow

```text
existing Commerce repo / exact pinned dependencies
  -> run fast unit/UI suites and static contracts
  -> provision disposable, isolated PostgreSQL + Redis fixtures
  -> run real integration suites, including failure recovery and cleanup
  -> run Code Runtime package + security smoke
  -> run full lint, typecheck and production build
  -> compare every failure identity with baseline
  -> mark task review only when its specific requirements pass
  -> architect accepts and developer integrates implementation task branch
  -> run full integrated Commerce validation after all eight tasks
```

## Repository Responsibilities

- `moda_commerce` owns all eight implementation tasks in `moda-interact-commerce` and its repository-local test scripts, fixtures, tests and runtime code as explicitly scoped.
- `moda_architect` owns this architecture, task definitions, reviewing accepted evidence, dependency promotions and eventual coordination documents.
- `moda_database`, `moda_shared`, `moda_mcp` and `moda_gateway` remain separate owners for any future discovered cross-boundary corrections; inspection alone does not authorise changes to those repositories.

## Data Model

No schema migration is planned. COMMERCE-007 must validate existing retained Agent model/prompt CAS fields, publication `CommerceAuditEvent` transactional behavior, exact replay and rollback using the canonical Prisma schema. Redis in COMMERCE-002 is a disposable test dependency, not a new source of truth.

## Contracts

No new cross-repository wire contract is planned. Preserve existing Tool/ToolRevision, agent template validation errors, Auth.js session behavior, Shopify/Admin schema artifact, standalone MCP extraction, Redis admission `RATE_LIMITED`, Code Runtime v1/v2 request/response and `CommerceAuditEvent` invariants. If a shared contract is found incompatible, return it to the architect for shared-first design rather than adding a local incompatible duplicate.

## Consistency and Transactions

COMMERCE-007 owns tests/corrections of model and prompt edit-version CAS, audit transaction atomicity, idempotency, out-of-order/stale update denial, two-client races and rollback after injected faults. Test harnesses must use disposable isolated resources; a transaction timeout is never an acceptable partial commit.

## Ordering

Tasks 001, 002, 003, 004, 005, 006 and 008 are definition-level Ready because no required ARCH-044 implementation dependency blocks their investigation. COMMERCE-007 was Pending until COMMERCE-002 was architect-accepted Complete so its integration evidence uses the agreed disposable fixture; that dependency is now satisfied and COMMERCE-007 is Ready. Tasks may proceed in separate canonical task worktrees, and repository/parent merges remain developer-owned. Avoid unnecessary cross-task sequencing beyond that dependency.

## Failure Handling

- Missing Docker, Redis or PostgreSQL must produce an explicit unresolved validation reason, not a green fake pass.
- Code Runtime compilation, deadline, cancellation and untrusted guest sandboxing must remain fail-closed.
- Tests based on retired live Shopify Admin execution must assert the current deferred state; no silent reactivation.
- Failures unrelated to the assigned task must be documented with exact test identity and routed to the proper task instead of hidden in an "accepted baseline" blanket exception.
- No production customer data or provider secrets should appear in baseline logs or fixture output.

## Scalability

This is baseline correctness work rather than a throughput expansion. Preserve bounded worker concurrency and message/runtime limits, deterministic Redis admission under at least 60+1 calls, and finite test/runtime timeouts. Load/benchmark estimates are not assumed measured. COMMERCE-001 and COMMERCE-002 must separate actual run latency from queue/scheduling delays before modifying deadlines.

## Security

Do not weaken auth, tenant isolation, CAS, provider credential confidentiality, guest sandboxing, immutable helper namespace, or administrative live-publish permissions to make tests pass. Use the published Shared logger for new structured runtime logging and log bounded semantic reasons, never raw secrets, database URLs, or provider error objects. All fixtures must validate the disposable target and avoid deleting persistent data.

## Observability

Use existing framework/Shared logger and test/harness structured diagnostics; no new competing generic logger or duplicate framework HTTP metrics. Log bounded cause classifications, test fixture identity (without connection URLs or secrets), deterministic artifact hashes and operational reasons for failures. Test exporter side effects remain disabled by default. No new deployment/OTLP wiring is indicated by inspected code.

## Infrastructure and Deployment

No Render/Gateway topology change is required. Development fixtures may use disposable Docker Postgres/Redis when available, and existing approved scripts remain the first choice. Deployment rollout classification: **compatibility-preserving maintenance** until a task proves a runtime or format change; do not assume freedom to break production ciphertext, sessions, or Tool definitions.

## Rollout / Migration

1. Materialise the nine documentation files (this architecture plus eight task definitions) on the canonical **parent workspace** following `docs/task-definition-materialization.md`. No implementation worktree or branch is claimed simply by definition.
2. Let each eligible task enter the launcher-controlled task preparation/claim flow. Implement and review its bounded change.
3. Developer integrates accepted implementation branches first, then parent workspace gitlink/documentation changes as the established protocol requires; rebase or resynchronise sibling task branches against integrated `main` to avoid stale patches.
4. Run integrated full Commerce suite with disposable fixtures, `npm run lint`, `npm run typecheck`, `npm run build`, Code Runtime smoke and PostgreSQL migration/rehearsal checks as appropriate.
5. Synchronise `ARCH-043-COMMERCE-002` with accepted integrated Commerce fixes; rerun its focused Auth.js fallback/rotation, Merchant Knowledge on-demand, Shared logging and PostgreSQL tests and finish its separate review. **Do not automatically mark ARCH-043 complete because ARCH-044 was tested.**

No database schema migration is planned. If one becomes necessary it requires a database-owned task and its own rollout classification.

## Decisions / Tasks

| Task | Owner | Status at definition | Depends on | Baseline symptoms |
|---|---|---|---|---|
| ARCH-044-COMMERCE-001 | moda_commerce | Ready | — | Code Runtime packaged v2 compile-only and 400-ms supervisor proof |
| ARCH-044-COMMERCE-002 | moda_commerce | Ready | — | Six zero-test fixture setup failures, Redis admission timeout |
| ARCH-044-COMMERCE-003 | moda_commerce | Ready | — | Shopify Admin Tool authoring 19 failures |
| ARCH-044-COMMERCE-004 | moda_commerce | Ready | — | New Tool 7 failures + Woo provider component-boundary 1 |
| ARCH-044-COMMERCE-005 | moda_commerce | Ready | — | Studio Workspace 6 failures |
| ARCH-044-COMMERCE-006 | moda_commerce | Ready | — | Agent validation error code + MCP extraction boundary (2) |
| ARCH-044-COMMERCE-007 | moda_commerce | Ready | ARCH-044-COMMERCE-002 (complete) | Agent model/prompt CAS + PostgreSQL publication transaction (2) |
| ARCH-044-COMMERCE-008 | moda_commerce | Ready | — | React ref lint 2 errors |

These eight tasks cover **all 38** unchanged-baseline failing assertions, the six suite-setup failures, the two lint errors, and the separately observed Code Runtime smoke/proof discrepancy. No ninth task is requested. Because the scope is a single-repository baseline correction and no new end-to-end inter-service flow is introduced, a separate system-test implementation task is not currently justified; the integrated Commerce validation is a required architectural final gate. Reassess if runtime changes cross service boundaries.

## Open Questions

- Which exact baseline Git commit SHA and dependency/environment identity produced the provided log? The source logs identify the detached baseline path, not an unambiguous revision; record when materialised.
- Does the Code Runtime helper digest difference reflect install/toolchain provenance, packaged artifact nondeterminism or a true product defect?
- Do the six import-failing suites all run safely via existing scripts once combined, or is bounded new harness orchestration needed?
- Does `@modelcontextprotocol/sdk` have a legitimate remaining Commerce runtime use or is it a dependency cleanup?
- Are the two residual PostgreSQL failures production defects, test double drift, timeout pressure or a combination? Do not infer before testing.

## Change History

- 2026-10-18: Developer requested eight detailed baseline-stabilisation tasks after comparing unchanged Commerce and ARCH-043 failure inventories. Initial portable canonical definitions prepared; no `_index.md`, implementation or Git operations.
