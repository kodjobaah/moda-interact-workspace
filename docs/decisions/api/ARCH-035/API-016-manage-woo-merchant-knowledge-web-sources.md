---
id: ARCH-035-API-016
architecture_id: ARCH-035
title: Manage Woo Merchant Knowledge web sources and ordering
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 44
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-015]
enables: [ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-API-016 — Manage Woo Merchant Knowledge web sources and ordering

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.


## Objective

Provide authenticated, durable web-page source CRUD, refresh and ordering using the existing Merchant Knowledge lifecycle.

## Context

Shopify’s `merchant-knowledge.server.ts` handles HTTPS URL source creation/edit/refresh/delete/reorder with Shop locks, plan/type limits and source revisions. API-015 owns the canonical read/allowed-source projection.

## Scope

- Implement bounded POST source, PATCH/DELETE source/{id}, POST source/{id}/refresh and PUT order endpoints; publish strict OpenAPI input/output and errors.
- Reuse canonical Shop-scoped source/revision models, active subscription/source-type eligibility and limits, HTTPS/SSRF-safe URL policy and accepted language tags from Shared.
- Enforce atomic Shop lock/ordered positions, generation increments and durable revision creation; preserve durable `PENDING` revisions for Background reconciliation; any optional immediate queue hint must be non-blocking, after commit and architecture-approved.
- Retain configured sources when feature toggle is off; do not queue ingestion while off. Protect against duplicate actions, stale IDs and unexpected provider types.
- Add focused conflict, concurrency, SSRF-protection, entitlement and history tests; preserve Shopify data.

## Out of Scope

- Uploaded file lifecycle or R2 signing (API-017).
- Woo interface/feature-preference commands, new DB schema or another repository’s queue processing.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [x] Implement bounded POST source, PATCH/DELETE source/{id}, POST source/{id}/refresh and PUT order endpoints; publish strict OpenAPI input/output and errors.
- [x] Reuse canonical Shop-scoped source/revision models, active subscription/source-type eligibility and limits, HTTPS/SSRF-safe URL policy and accepted language tags from Shared.
- [x] Enforce atomic Shop lock/ordered positions, generation increments and durable revision creation; preserve durable `PENDING` revisions for Background reconciliation; any optional immediate queue hint must be non-blocking, after commit and architecture-approved.
- [x] Retain configured sources when feature toggle is off; do not queue ingestion while off. Protect against duplicate actions, stale IDs and unexpected provider types.
- [x] Add focused conflict, concurrency, SSRF-protection, entitlement and history tests; preserve Shopify data.
- [x] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- POST `/v1/merchant/merchant-knowledge/sources`; PATCH/DELETE `/v1/merchant/merchant-knowledge/sources/{id}`; POST `.../{id}/refresh`; PUT `/v1/merchant/merchant-knowledge/order`.
- Use API-015 projection for post-action refresh; immutable Shop authorization from principal.

## Dependencies

- `ARCH-035-API-015` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [x] Create/edit URL yields correct revision/generation and source state; metadata-only edit avoids spurious revisions.
- [x] Foreign Shop, malformed/restricted URL, exceeded source count, disabled plan/type and stale source reject with no partial writes.
- [x] Delete/reorder leaves contiguous deterministic positions; duplicate/retried requests cannot create unintended duplicate durable work; feature-off retains editable configuration.
- [x] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [x] Focused unit and disposable PostgreSQL concurrency/transaction tests; durable-pending/reconciliation and dedup tests.
- [x] Typecheck, lint, build and `git diff --check`.
- [x] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled API-structure handoff (2026-10-16 22:56 snapshot)

- Implement the commands under `src/merchant/merchant-knowledge/` using feature-owned routes, bounded input parsers and small source lifecycle services. Register through `src/composition/merchant.ts`, authenticate through `src/auth/woo-installation/`, and reuse `src/http/` conventions. Use the read projection from API-015; do not change the Woo installation connection router or Shopify source files.
- The current API `package.json` has **no BullMQ dependency or knowledge queue producer**. The existing Background `MerchantKnowledgeReconciliationService` scans durable `PENDING` source revisions and publishes the canonical Shared queue contract. Therefore the required correctness outcome is **transactionally durable revision state plus eventual reconciliation**, not a newly invented synchronous Redis/BullMQ dependency in the API. A best-effort producer is optional only if architecture-approved, non-blocking and backed by the durable reconciler; no Redis/network call inside a Prisma transaction. Tests must demonstrate work remains discoverable when direct queue publication is absent or fails.
- Treat HTTPS/SSRF safety as two separate boundaries: API validates/canonicalises submitted URLs using approved shared rules; existing Background fetch protection remains the authority for outbound DNS/IP/redirect enforcement. Preserve atomic shop lock, order/position integrity, version/generation fencing and idempotency for repeated writes.
- Locate unit and PostgreSQL tests at `tests/unit/merchant/merchant-knowledge/` and `tests/integration/merchant/merchant-knowledge/`. Register new integration validation in `package.json`; author the versioned command contracts in `openapi/merchant-knowledge-v1.yaml` alongside API-015's read contract.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-API-016`, explicitly taking over this ready agent-executed task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 will be claimed by `developer` after canonical parent and implementation worktree synchronization.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and was explicitly completed by the developer after the instruction “Architect Review Accepted”.

### Files Changed

In `moda-interact-api` (10 files): `openapi/merchant-knowledge-v1.yaml`; `scripts/test-arch035-merchant-knowledge-postgres.mjs`; `src/composition/merchant.ts`; `src/merchant/merchant-knowledge/commands.contract.ts`; `src/merchant/merchant-knowledge/commands.routes.ts`; `src/merchant/merchant-knowledge/commands.service.ts`; `src/merchant/merchant-knowledge/read.service.ts`; `tests/integration/merchant/merchant-knowledge/commands.postgres.test.ts`; `tests/unit/composition/real-route-registration.test.ts`; `tests/unit/merchant/merchant-knowledge/commands.test.ts`.

### Work Completed

- Added authenticated create, patch, delete, refresh and reorder commands with bounded strict request parsing, safe responses, OpenAPI contracts, and the API-015 canonical read projection.
- Implemented Shop/install-scoped transactional locking, entitlement/source-type/source-limit enforcement, generation fencing, durable revisions, idempotent create/refresh handling, and deterministic position compaction. No Redis/BullMQ producer or network call was added to API transactions.
- Added unit and migration-backed PostgreSQL coverage for URL input rejection, authentication, concurrency/deduplication, metadata-only and URL-change updates, durable pending revisions, source limits, entitlement, tenant isolation, stale generations, refresh, deletion and ordering.
- Confirmed existing Background reconciliation scans ordered `PENDING` revisions, skips stale/dormant work, and uses deterministic job IDs. Its disposable PostgreSQL recovery test passed through queue publication loss and subsequent recovery, demonstrating that committed API revisions remain discoverable without direct API queue publication.

### Validation Results

All commands passed:

- `npx tsx --test tests/unit/merchant/merchant-knowledge/commands.test.ts` — 3/3 passed.
- `npm run test:arch035-merchant-knowledge:postgres` — 2/2 passed using disposable PostgreSQL and applied migrations.
- `npm test` — 447/447 passed.
- `npm run test:integration` — all six registered harnesses passed, 35 tests total.
- `npm run typecheck` — Prisma client generation and TypeScript check passed.
- `npm run lint` — passed with zero warnings.
- `npm run build` — Prisma client generation and production TypeScript build passed.
- `git diff --check origin/main...HEAD` — passed.
- From `moda-interact-background`: `PATH="$PWD/node_modules/.bin:$PATH" node scripts/test-integration.mjs tests/integration/merchant-knowledge-reconciliation.integration.test.ts` — 1/1 disposable PostgreSQL recovery test passed. The initial invocation without the local `.bin` path failed before test startup (`spawn prisma ENOENT`); the corrected invocation passed.

### Branch and Worktree Evidence

- API implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-016`, branch `task/ARCH-035-API-016`, implementation commit `24bc6403f7aa81c086d06fe9a931d0373dbb796e`; HEAD equals `origin/task/ARCH-035-API-016`, worktree clean, one commit ahead of `origin/main` at `95ef371cc2154687ac54aec990f7478cd9aa151f`.
- Canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-016`, branch `task/ARCH-035-API-016`, baseline HEAD/remote before this report update `a2ee1cf9d64c7cdcc83e2f9776246f26e4aa2513`.
- Recursive implementation submodule status was clean at database `139765042baad3901682cfe9c54a3d6bba73e75c` (`heads/main`). API diff contains no `_index.md` or unrelated domain changes. The primary shared workspace's unrelated dirty files/submodules were left untouched.

### Deviations

The Background reconciliation recovery check is an existing cross-repository integration test and was run from `moda-interact-background`; no changes were made to that repository. The test runner required the Background repository's local `node_modules/.bin` in `PATH` for Prisma.

### Assumptions

The API-015 dependency was already complete and architect accepted. Its canonical projection and the existing Background reconciliation contract remain authoritative; this task adds no competing queue or ingestion contract.

### Unresolved Issues

None identified in the implemented scope or validation. Architect review remains pending.

### Developer Self-Review

**Passed — 2026-10-17.** Scope, acceptance criteria and required validation are evidenced above. No API-016 implementation changes remain requested. This passing review was followed by the explicit developer completion decision recorded below.

### Developer Completion Decision

**Complete — 2026-10-17.** The developer explicitly invoked `/moda_developer_update ARCH-035-API-016 complete` with “Architect Review Accepted”. The passing Attempt 1 review, completed acceptance criteria and validation evidence were verified before transition. Attempt remains 1; `executor` and `claimed_at` are null. Implementation and parent task branches remain separate and neither was merged to `main`.

### Downstream Dependency Frontier

`ARCH-035-WOOCOMMERCE-014` remains `pending`: its explicit dependencies include `ARCH-035-API-017`, which the canonical launcher currently reports as `in_progress`. Completing API-016 alone does not make WOO-014 ready. No downstream task or architecture index was changed.

## Architect Review

### Review Status

Accepted — developer-as-architect acceptance recorded on 2026-10-17 in response to the explicit “Architect Review Accepted” instruction. No separate `moda_architect` agent review was run.

### Review Notes

Implementation and validation evidence is recorded in the Completion Report. The developer explicitly accepted the review and completed the task.

### Reviewed Files

The ten API implementation files listed in the Completion Report, the API-016 task definition, and the existing Background reconciliation implementation/test consulted as cross-repository contract evidence. No task index files changed.

### Validation Reviewed

All validation listed in the Completion Report passed, including the API and Background disposable PostgreSQL recovery suites.

### Architecture Conformance

Accepted. The implementation uses API-015's canonical projection, writes durable Shop-scoped revisions for existing Background reconciliation, and introduces no cross-repository implementation changes.

### Follow-up

`ARCH-035-WOOCOMMERCE-014` remains pending until its remaining explicit dependencies, including API-017, are complete.
