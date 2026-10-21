---
id: ARCH-043-ADMIN-004
architecture_id: ARCH-043
title: Use database Shopify Partner credentials in Admin subscription reads
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 55
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-043-ADMIN-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-21'
---

# Use database Shopify Partner credentials in Admin subscription reads

## Architecture

- `ARCH-043`: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Current source evidence and boundary: controlling 17 October environment-variable reconciliation in that parent architecture.
- Logical owner: `moda_admin` (`moda-interact-admin`).
- Materialised on canonical parent and implementation worktrees for `task/ARCH-043-ADMIN-004`; developer execution is claimed for Attempt 1.

## Objective

Replace the current Admin Shopify Partner subscription inspection environment reads with the approved purpose-scoped `shopify.partner` configuration. Do not change the Admin login system.

## Context

The canonical ARCH-043 inventory defines this as a newly scoped consumer task; do not revive identically numbered superseded proposal files or their retired dependencies. The generic database models and ARCH-039 published cryptography remain unchanged.

## Scope

- Read the validated partner tuple `{accessToken,organizationId,appId,apiVersion?}` from PostgreSQL for each Partner API operation, using the existing Admin service and ARCH-039 unseal mechanism.
- Resolve the entire Partner tuple exclusively from the sealed `shopify.partner` record. Do not read legacy Partner token, organisation, app ID or API-version environment variables, including when the database row is absent.
- Keep request authentication, SUPER_ADMIN authorisation, error redaction and Partner API response handling unchanged.

## Out of Scope

- No new Prisma model, root cryptography, Shared package, gateway or cross-repository implementation.
- No `_index.md` changes, unrelated refactors or changes to other services' credential sources. Do not remove unrelated deployment secrets.

## Requirements

- Use the environment-scoped `PlatformConfiguration` sealed envelope with immutable AAD bytes and published ARCH-039 Node-only decryption.
- Missing, disabled, corrupt, undecryptable or unavailable `shopify.partner` data fails closed. No Partner credential alias compatibility, transition mode or environment fallback is permitted.
- Read once per relevant bounded operation; do not add a per-event hot-path query, a global indefinite cache or a network operation inside a transaction.
- Secrets never leave the trusted server or enter logs, audits, errors or browser output.
- Respect existing service ownership, launcher task-isolation, developer review and task-state claims.

## Work Items

- [x] Read the validated partner tuple `{accessToken,organizationId,appId,apiVersion?}` from PostgreSQL for each Partner API operation, using the existing Admin service and ARCH-039 unseal mechanism.
- [x] Remove legacy Partner environment alias readers and transition flags; require a complete sealed database tuple for every Partner API operation.
- [x] Keep request authentication, SUPER_ADMIN authorisation, error redaction and Partner API response handling unchanged.
- [x] Add positive and negative unit/integration tests; record actual validation and isolated-worktree evidence.

## Interfaces / Contracts

- Configuration keys and decrypted field names: `docs/architecture/ARCH-043-database-managed-platform-configuration.md` (17 October reconciliation).
- Writer and sealed key lifecycle: `ARCH-043-ADMIN-002`; schema: `ARCH-043-DATABASE-001`.
- Shared cryptography: `@modainteract/moda-interact-shared/security/credentials/node` (existing published exports).

## Dependencies

- `ARCH-043-ADMIN-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Valid partner lookup and revision refresh
- [x] No Partner environment credential fallback; missing/revoked/invalid/wrong-environment data rejects
- [x] No secrets in logs/browser, typecheck and focused Partner API tests
- [x] No cross-environment secret leakage, duplicate provider credentials or stale revision reuse.
- [x] All prerequisite tasks were Complete before the implementation claim.

## Validation

- [x] Task-focused unit and integration tests using existing repository commands.
- [x] Typecheck, applicable lint/build, `git diff --check`.
- [x] Recorded launcher-resolved parent/implementation task worktree isolation and sync.

## Stop Condition

After required work and validation, record the Completion Report and developer self-review. Completion authority is `developer`; do not start enabled tasks as part of this task.

## Developer Takeover and Claim

The developer invoked `/moda_developer_create ARCH-043-ADMIN-004` to take over this ready agent-owned task. The logical owner remains `moda_admin`; this amendment changes execution and completion authority only.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Attempt claimed: 1 at `2026-10-21T12:02:42Z`
- Dependency gate: `ARCH-043-ADMIN-002` was resolved through the canonical launcher as `complete` before claim.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-ADMIN-004`, branch `task/ARCH-043-ADMIN-004`, clean at `d8a49efb2c7c310ae63ca07355797d4b126ca64a` (`origin/main`).
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-ADMIN-004`, branch `task/ARCH-043-ADMIN-004`, clean at `884c56aabb49f0edc22db313fb9c50ce8681cac8` (`origin/main`).
- Synchronization: both repositories were fetched; no existing task branch or stale worktree registration was present, so canonical worktrees were created from current `origin/main`.

## Implementation Notes

The implementation replaced the prior environment-based `partnerConfig()` reader in `shopify-subscription-contract.ts` with a per-operation read of the environment-scoped sealed `shopify.partner` configuration. The complete tuple is validated and unsealed through the existing Admin configuration service and ARCH-039 mechanism; absent, disabled, invalid, wrong-environment, undecryptable or unavailable data fails closed. The Partner GraphQL request and subscription response validation remain on their existing path.

## Completion Report

### Status

Complete — developer Attempt 1 was accepted and explicitly completed on 2026-10-21. Attempt remains 1; `executor` and `claimed_at` are null.

### Files Changed

- `src/lib/admin/shopify-partner-configuration.ts`: added the trusted server-side environment-scoped `shopify.partner` database reader, ARCH-039 unsealing, and payload validation.
- `src/lib/admin/shopify-partner-credentials.ts`: added per-operation tuple resolution, API-version defaulting, environment/revision validation, and fail-closed errors without a cross-request cache.
- `src/lib/admin/shopify-subscription-contract.ts`: replaced environment aliases with the sealed configuration reader while retaining the Partner API request and response handling.
- `.env.example`: documented that Partner credentials are configured through sealed Admin platform configuration, without adding credential variables.
- `tests/unit/arch043-shopify-partner-credentials.test.ts`, `tests/integration/arch043-shopify-partner-sealed.test.ts`, and `tests/unit/arch043-shopify-partner-wiring.test.mjs`: added positive, negative, rotation, sealing/AAD, redaction, and no-fallback coverage.

### Work Completed

- Partner subscription inspection now loads the complete validated tuple from the `PlatformConfiguration` row keyed by deployment environment and `shopify.partner` for each operation.
- Removed all Partner token, organization, app ID, and API-version environment fallback from the production reader; missing or invalid database configuration fails closed.
- Preserved the existing authentication/authorization and Partner API request/response flow; no secrets are returned in errors from the new resolver.
- No Prisma schema, Shared package, gateway, other service credential source, or unrelated deployment secret was changed. No material assigned-agent assistance was used.

### Validation Results

- Focused Partner credential, sealed-envelope, and wiring tests: 13 passed, 0 failed.
- `npm run build`: passed, including Prisma generation and Next.js TypeScript/build stages. Build emitted existing optional BullMQ dependency warnings for `@valkey/valkey-glide` and a dynamic dependency expression; compilation and build completed successfully.
- `npm run lint`: exit 0, 0 errors; one warning remains in the untouched `database/eslint.config.mjs`.
- `git diff --check origin/main...HEAD`: passed for the implementation branch. Implementation worktree was clean at `38e49c366d1c249b98d73712aff3260f2219c504`, equal to `origin/task/ARCH-043-ADMIN-004`.
- Canonical launcher resolved the parent worktree as `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-043-ADMIN-004` and the implementation worktree as `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-043-ADMIN-004`; both use `task/ARCH-043-ADMIN-004`. Prerequisite `ARCH-043-ADMIN-002` resolved as `complete` before the Attempt 1 claim.

### Deviations

- Enabled-task dependency-frontier recalculation is blocked because the canonical launcher reports duplicate definitions for both `ARCH-043-GATEWAY-001` and `ARCH-043-SYSTEM-TEST-001`. Their separate records have materially different scopes/dependencies. They were not modified or promoted based on a guessed canonical definition; architect reconciliation is required.

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Developer Self-Review — Accepted — Attempt 1 (2026-10-21)

**Disposition: Accepted.** The implementation satisfies the approved database-only Partner credential scope, uses the existing sealed configuration and ARCH-039 unseal path, fails closed for missing or invalid configuration, and has no legacy Partner environment fallback. The Partner request and response-handling path remains unchanged. Focused tests, build, lint, implementation-branch publication, and task-worktree isolation were reviewed as recorded above. Work Items, Acceptance Criteria, and Validation checklists are complete. The non-blocking build/lint warnings are in existing unrelated dependency/configuration surfaces.

**Completion authority:** `completion_mode: developer`. The developer explicitly requested `/moda_developer_update ARCH-043-ADMIN-004 complete`; the accepted Attempt 1 is unchanged. The implementation branch is committed and pushed. The parent task record is being committed and pushed on `task/ARCH-043-ADMIN-004`. No task branch is merged to `main`.

## Developer Completion Decision — 2026-10-21

The developer explicitly requested `/moda_developer_update ARCH-043-ADMIN-004 complete` after the durable Accepted Attempt 1 review. All required Work Items and Acceptance Criteria are complete; implementation commit `38e49c366d1c249b98d73712aff3260f2219c504` is committed and pushed. Task status is `complete`; Attempt 1 is unchanged, with `executor: null` and `claimed_at: null`. Dependency-frontier reconciliation remains blocked by duplicate Gateway/System-Test task IDs and is recorded under Deviations; those records are left unchanged pending architect reconciliation. No task branch is merged to `main`.

## Architect Review

### Review Status

Pending

### Review Notes

Not reviewed.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not evaluated.

### Follow-up

None
