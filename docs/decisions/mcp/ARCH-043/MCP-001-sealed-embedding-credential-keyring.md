---
id: ARCH-043-MCP-001
architecture_id: ARCH-043
title: Consume sealed Commerce keyring for MCP embedding credentials
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-043-DATABASE-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: 2026-10-17
---

# Consume sealed Commerce keyring for MCP embedding credentials

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_mcp` / `moda-interact-mcp`. The task is materialized in the canonical parent task worktree; execution ownership is with the developer.

## Developer Ownership Amendment

On 2026-10-17, `/moda_developer_create ARCH-043-MCP-001` was invoked to take over this ready task. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_mcp`, repository ownership, scope, dependency, requirements, and acceptance criteria are unchanged. The canonical developer launcher records the execution attempt separately.

## Objective

Consume sealed Commerce keyring for MCP embedding credentials.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Replace env-backed Commerce keyring reads in MCP embedding-runtime with sealed commerce.connectionKeys.
- Preserve published Shared decryption AAD and embedding-provider credentials compatibility.
- Test missing/wrong-environment/unsealable secret fails closed and never logs secret bytes.

## Out of Scope

- No embedding model/provider policy changes or new credential models.

## Requirements

- Existing encrypted MCP embedding credentials decrypt unchanged; missing/invalid secret denies operation.

## Work Items

- [x] Replace env-backed Commerce keyring reads in MCP embedding-runtime with sealed commerce.connectionKeys.
- [x] Preserve published Shared decryption AAD and embedding-provider credentials compatibility.
- [x] Test missing/wrong-environment/unsealable secret fails closed and never logs secret bytes.
- [x] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Existing encryption/decryption: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039). ARCH-043 sealed JSON and frozen canonical AAD bytes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`; Admin writes and authorised service readers independently implement/verify this documented format without new Shared publication.
- Owner retains environment and service authorisation, fresh per-operation reads, failure semantics and logging; no configuration cache. Never place unseal/root keys in PostgreSQL.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Existing encrypted MCP embedding credentials decrypt unchanged; missing/invalid secret denies operation.

## Validation

- [x] MCP credential and embedding unit tests (13/13); integration test source typechecked. Disposable PostgreSQL execution was unavailable because Docker is not installed in this environment.
- [x] Typecheck, integration typecheck, production build and changed-file lint
- [x] `git diff --check` for committed and uncommitted changes

## Stop Condition

Finish scoped implementation and required validation, update Completion Report, mark task Review, and return to moda_architect. STOP; do not execute follow-on tasks or update `_index.md`.

## Implementation Notes

Reuse Shared/ARCH-039 approved primitives and shared logging; preserve domain auth/tenant boundaries. Physical isolation/synchronisation evidence from task launcher required for acceptance.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and was explicitly completed after architect acceptance. Attempt 1 was claimed at 2026-10-17T15:47:24Z. Attempt 0 review history is preserved below.

### Files Changed

Implementation commit `6287e0b1a177e09382819f9b5303b9c7a7c0645c` on `task/ARCH-043-MCP-001` changes:

- `src/execution/merchant-knowledge/embedding-runtime.ts`
- `src/execution/merchant-knowledge/sealed-commerce-keyring.ts`
- `tests/unit/execution/merchant-knowledge/embedding-runtime.test.ts`
- `tests/integration/embedding-runtime.integration.test.ts`

The implementation branch is aligned with `origin/task/ARCH-043-MCP-001`. No MCP source or test files remain uncommitted; the database gitlink state is recorded under Unresolved Issues.

### Work Completed

Replaced the MCP embedding resolver's environment-backed Commerce keyring with a fresh environment-scoped read of the sealed `commerce.connectionKeys` row. The reader validates the closed envelope and purpose payload, uses the frozen ARCH-043 AAD and deployment-only unseal material, then decrypts existing embedding credentials with their unchanged Shared AAD. Missing, invalid, revoked or undecryptable configuration fails closed without exposing secret or provider/database error details. Tests cover legacy credential compatibility, fresh reads, environment isolation, tampering, rotation/removal, and redaction.

### Validation Results

Passed: focused unit tests (`embedding-runtime.test.ts` and `credential-keyring.test.ts`, 13/13); `npm run typecheck`; `npm run typecheck:integration`; `npm run build`; changed-file ESLint; committed and working-tree `git diff --check`.

Not run: `npm run test:integration:docker` could not start because the shell has no `docker` executable (`spawnSync docker ENOENT`). The runner failed before container creation; no PostgreSQL integration pass is claimed.

### Deviations

No scope deviation. The disposable PostgreSQL test was not executable in this environment; its test source compiles successfully and must not be represented as runtime-validated.

### Assumptions

The canonical resolver returned parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-MCP-001` and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-MCP-001`, both on `task/ARCH-043-MCP-001`. Git worktree registration confirms the implementation path is dedicated to this task; the shared/default MCP checkout was not used. The implementation branch contains `origin/main` and is aligned with its task-branch upstream. Before this review edit, the parent task worktree was clean and included mainline merge `3d71aec0`; it was 26 commits ahead of its remote task branch.

### Unresolved Issues

The implementation worktree has a local database submodule checkout at `aa3fd024db3a1484f72f8033b87f56ad27f4640d` (`origin/main`), while the MCP task branch records gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`. Git therefore reports `database` as modified. The pointer was not staged or changed: it is outside this MCP task's source scope, and repository policy reserves parent gitlink updates for post-integration. Disposable PostgreSQL runtime validation remains outstanding because Docker is unavailable.

### Architectural Concerns

No implementation-scope concern identified. Do not stage the database gitlink as part of this task; reconcile it only at the repository integration boundary.

## Developer Self-Review

### Review Status

Accepted for Attempt 1 based on the passing focused tests, typechecks, production build, lint and diff checks. The disposable PostgreSQL integration suite could not run because Docker is unavailable, so no database runtime pass is claimed. Status is `review`; explicit developer completion remains pending.

### Reviewed Files

The four implementation paths listed under Files Changed, including the diff from `origin/main` to `6287e0b1a177e09382819f9b5303b9c7a7c0645c`.

### Validation Reviewed

Focused unit tests (13/13), `npm run typecheck`, `npm run typecheck:integration`, `npm run build`, changed-file ESLint and both committed/uncommitted `git diff --check` passed. `npm run test:integration:docker` was blocked before startup with `spawnSync docker ENOENT`.

### Architecture Conformance

Conforms to the MCP-owned scope: only the embedding runtime and its tests changed. No embedding policy, database schema, migration, tenant boundary or follow-on task was changed. Existing encrypted credential AAD remains unchanged; the sealed configuration uses the frozen ARCH-043 AAD.

### Follow-up

The developer explicitly completed this accepted attempt. No task branch was merged into `main`. The disposable PostgreSQL run remains unavailable in this environment; the local database gitlink divergence remains uncommitted and outside this task's implementation changes.

## Developer Completion Decision

On 2026-10-17, the developer invoked `/moda_developer_update ARCH-043-MCP-001 complete` after architect acceptance. Attempt 1 remains the accepted attempt; status is `complete`, `executor` and `claimed_at` are cleared, and no implementation branch was merged into `main`.

### Dependency Frontier

The enabled IDs `ARCH-043-GATEWAY-001` and `ARCH-043-SYSTEM-TEST-001` were checked after this completion. The canonical launcher refuses route resolution for both IDs because the workspace contains duplicate task definitions for each ID. No downstream task was promoted or edited. Resolve the duplicate task definitions before the architecture frontier can be reconciled; the system-test task remains subject to its normal manual gate.

## Architect Review

### Review Status

Accepted — architect acceptance was explicitly supplied with the developer completion request.

### Review Notes

The bounded MCP implementation meets the accepted task scope and preserves existing embedding credential compatibility. Focused unit tests, typechecks, production build, changed-file lint and diff checks passed. The disposable PostgreSQL integration test was not run because Docker was unavailable; this limitation was considered in the acceptance. The database submodule checkout differs from the implementation branch's recorded gitlink; the pointer remains unstaged and is not part of this task's implementation commit.

### Reviewed Files

The four implementation paths listed under Files Changed, in implementation commit `6287e0b1a177e09382819f9b5303b9c7a7c0645c`.

### Validation Reviewed

Focused unit tests (13/13), `npm run typecheck`, `npm run typecheck:integration`, `npm run build`, changed-file ESLint and `git diff --check` passed. `npm run test:integration:docker` was blocked before container startup because `docker` was unavailable.

### Architecture Conformance

Accepted for the MCP-owned scope. Existing encrypted credential AAD and provider credential behavior are preserved; the sealed configuration reader uses the documented ARCH-043 AAD and fails closed without exposing secret material.

### Follow-up

Resolve duplicate ARCH-043 Gateway and system-test task IDs before dependency-frontier promotion. Reconcile the database gitlink only at the repository integration boundary; do not stage it as part of this task.
