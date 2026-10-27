---
id: ARCH-050-API-001
architecture_id: ARCH-050
title: Expose and persist Woo notification opt-in through hosted recovery-policy API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-WOOCOMMERCE-001
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-27
---

# Expose and persist Woo notification opt-in through hosted recovery-policy API

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Extend the existing authenticated hosted Woo merchant recovery-policy API with revision-checked notification preference reads/writes.

## Context

`src/merchant/recovery-policy/contract.ts`, `service.ts` and `routes.ts` have strict exact-field DTO validation, revision snapshots and installed Woo shop authorization; no new endpoint is required.

## Scope

**Modify in `moda-interact-api/`:**

- `src/merchant/recovery-policy/contract.ts` — exact HTTP v2 types, strict request parser and response validator.
- `src/merchant/recovery-policy/service.ts` — read projection, equality/revision check and transactional setting write.
- `src/merchant/recovery-policy/routes.ts` — retain existing GET/PUT path, auth, request bounds, no-store headers and error mapping; only update response validation to v2 through the contract.
- `tests/unit/merchant/recovery-policy/` — request and response strictness, revision, default values; `tests/integration/merchant/recovery-policy/` plus existing disposable Postgres harness.

Do not modify Woo plugin PHP/JS validators or Shopify settings code here (they have separate tasks). No new endpoint is required.

## Out of Scope

- Shopify loader, Woo plugin UI, other settings, generic Support read or provider processing.

## Requirements

- Keep `GET|PUT /v1/merchant/recovery-policy`; schemaVersion changes from **1 to 2** for its successful GET/PUT payload. Preserve existing `merchant`, `effective`, `source`, `overrideActive`, `offerSelectionAvailable`, `revision` shapes (their `RecoveryPolicyValues` remain exactly the original four properties).
- Add a **top-level** `notifyOnInitialRecoveryOutreach: boolean` to response v2 and a new required Boolean to the strict PUT request (alongside existing `expectedRevision`, `recoveryDelayMinutes`, `followUpEnabled`, `followUpDelayMinutes`). Do not put it in `effective`, as it is not an admin-overridable recovery policy value.
- `parseRecoveryPolicyUpdate` rejects absent or extra keys, non-Boolean values or Boolean-like strings; keep existing delay bounds and 2048-byte body limit. Update `isRecoveryPolicyResponse()` exact key validation to v2.
- `projection(...)` reads `settings?.notifyOnInitialRecoveryOutreach ?? false` separately from `ShopRecoveryPolicyOverride`. `matches(settings, update)` includes this Boolean so a preference-only write cannot be silently skipped.
- Keep `assertCurrentShop()` row lock and `recovery_policy_conflict` revision behaviour; in current no-op path the Boolean must match too. Write the preference in the same ShopSettings transaction as existing delay/follow-up fields.
- Keep Woo identity, onboarding and discount selection untouched; coordinate deployment with strict WordPress PHP/JS validators in WOOCOMMERCE-001.
- `src/merchant/recovery-policy/routes.ts` already receives `logger: StructuredLogger` from the **canonical** `@modainteract/moda-interact-shared/logging` setup. Reuse that injected logger; do not instantiate another generic logger or add `console.*`. Preserve its existing `merchant.recovery_policy.*` event names, status codes and no-store responses.
- Every newly caught unexpected persistence/validation-integrity exception must produce `logger.error("merchant.recovery_policy.access.failed", {operation, reason:"internal", error})` with safe context before the **existing** sanitized HTTP 500 mapping. Keep expected malformed request/auth failures as their defined 400/401/403 paths; stale revision 409 remains a handled `warn`, not an internal-error event. Do not log request bodies, installation credential, form payload or raw HTTP response. No catch may return a false 200/default-OFF on DB exception. Shared log-sink failure must not change API response/status.

## Work Items

- [x] Update v2 DTO/parser/response validator with top-level Boolean and strict field set.
- [x] Update projection, no-op comparison, and revision-protected persistence for this field; typecheck passes with the accepted database schema.
- [x] Add and run unit/Postgres tests for default OFF, ON/OFF, preference-only save, stale revisions, admin override, unauthorised installation and malformed payloads.
- [x] Extend existing route/logger-spy tests for unexpected save failure: structured error event (with safe `error`), correct 500/no-store, and no fake successful preference result; conflicts remain 409 and warn only.

## Interfaces / Contracts

```ts
type MerchantRecoveryPolicyResponseV2 = {
  schemaVersion: 2;
  revision: string;
  merchant: RecoveryPolicyValues;   // original 4 fields unchanged
  effective: RecoveryPolicyValues;  // original 4 fields unchanged
  source: "MERCHANT" | "ADMIN_OVERRIDE";
  overrideActive: boolean;
  offerSelectionAvailable: false;
  notifyOnInitialRecoveryOutreach: boolean; // NEW top-level field
};
type RecoveryPolicyUpdateV2 = {
  expectedRevision: string;
  recoveryDelayMinutes: number;
  followUpEnabled: boolean;
  followUpDelayMinutes: number | null;
  notifyOnInitialRecoveryOutreach: boolean; // NEW required fifth field
};
```

Existing `GET|PUT /v1/merchant/recovery-policy` accepts only exact fields; no change to separate recovery summary or Support endpoints.
- Logging boundary: use route-injected `StructuredLogger`; keep stable `merchant.recovery_policy.access`/`.access.failed` events, distinguish known 409 conflict from unexpected 500 and include safe operation/category. No new cross-repository logging contract.

## Dependencies

- `ARCH-050-DATABASE-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-WOOCOMMERCE-001` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [x] Unconfigured shop reads OFF in v2 response; ON/OFF survives save and reload, verified by unit and PostgreSQL coverage.
- [x] Notification-only update persists and advances settings revision, while unchanged update remains no-op, verified by unit and PostgreSQL coverage.
- [x] Stale revisions, malformed/extra keys, unsupported shops and revoked installations fail closed.
- [x] Admin override never changes merchant opt-in; existing delay/follow-up/offer data survives.
- [x] Hosted API records a bounded structured failure for unhandled server exceptions and returns the pre-existing error status without exposing the exception or silently defaulting a failed read to OFF.

## Validation

- [x] Prisma Client generated successfully from the updated database schema; `tsc --noEmit -p tsconfig.json --pretty false` passed.
- [x] Focused recovery-policy unit tests passed: 25 tests, including strict DTO validation, default OFF, preference-only updates, revision behavior, admin override, authorization, malformed payloads and Shared logger failure handling.
- [x] Targeted ESLint passed for all changed TypeScript files; `git diff --check` passed.
- [x] Disposable PostgreSQL harness `node scripts/test-arch041-cross-domain-postgres.mjs` passed. It applied all 64 migrations including `20261026235000_arch050_initial_recovery_support_notification` and passed the recovery-policy GET/PUT persistence test plus the included webhook receipt test.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

API is the **HTTP contract owner**; WordPress PHP/JS validators will mirror the v2 DTO in WOOCOMMERCE-001 without a new Node Shared dependency. Keep `merchant/effective` recovery-policy shape unchanged; the notification toggle is independent of admin overrides.

## Completion Report

### Status

Accepted by architect at Attempt 1; task completed automatically. The accepted ARCH-050 database schema is available in the API task worktree, and focused validation passes against it.

### Files Changed

- `src/merchant/recovery-policy/contract.ts`
- `src/merchant/recovery-policy/service.ts`
- `src/merchant/recovery-policy/routes.ts`
- `openapi/woocommerce-merchant-recovery-policy-v1.yaml`
- `tests/unit/merchant/recovery-policy/contract.test.ts`
- `tests/unit/merchant/recovery-policy/service.test.ts`
- `tests/unit/merchant/recovery-policy/routes.test.ts`
- `tests/unit/merchant/recovery-policy/openapi-contract.test.ts`
- `tests/integration/merchant/recovery-policy/service.postgres.test.ts`
- `database` submodule gitlink, advanced to accepted commit `2f702f52372d648abc5f080f02f722046d0e9271`

### Work Completed

Implemented the recovery-policy v2 DTO/parser/validator and OpenAPI contract with top-level `notifyOnInitialRecoveryOutreach`. Added independent ShopSettings projection, no-op comparison and revision-checked persistence. Unexpected read/write failures log the original exception with safe operation context through the injected Shared `StructuredLogger`; logger sink failures remain isolated from HTTP response semantics. Updated the API database submodule pointer to the accepted ARCH-050 database implementation and validated the generated Prisma model and real PostgreSQL persistence path.

### Validation Results

- Passed: Prisma Client generation and `tsc --noEmit -p tsconfig.json --pretty false`.
- Passed: focused recovery-policy unit suite (25 tests).
- Passed: targeted ESLint and `git diff --check`.
- Passed: disposable PostgreSQL migration harness; all 64 migrations applied, including the ARCH-050 migration, and both included integration tests passed.
- Passed: implementation task branch pushed at `ba2541ef869836c20953ae236dd401cde104dbd1`, containing API implementation commit `dd12c25` and database pointer update commit `ba2541e`.

### Deviations

Updated the existing OpenAPI description/schema to document the schemaVersion 2 request and response payload. No other task scope was changed.

### Assumptions

The accepted ARCH-050-DATABASE-001 commit is `2f702f52372d648abc5f080f02f722046d0e9271`, as recorded in the database task report.

### Unresolved Issues

None known for this task. Architect review and acceptance remain outstanding.

### Architectural Concerns

None identified. The API remains the HTTP contract owner; the preference is top-level and independent from admin-overridable recovery policy values.

### Task Branch / Worktree Evidence

Parent branch/worktree: `task/ARCH-050-API-001`, `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-API-001`. Implementation branch/worktree: `task/ARCH-050-API-001`, `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-API-001`. The implementation worktree is isolated and points its `database` submodule at accepted commit `2f702f52372d648abc5f080f02f722046d0e9271`. Implementation branch tip `ba2541ef869836c20953ae236dd401cde104dbd1` is pushed to `origin/task/ARCH-050-API-001`. Neither task branch is merged to `main`.

## Architect Review — Attempt 1 — Accepted — 27 October 2026

### Review Status

Accepted.

### Review Notes

The API upgrades the existing authenticated GET/PUT contract to schema version 2 with a strict top-level `notifyOnInitialRecoveryOutreach` Boolean. The merchant/effective policy shape remains unchanged, the parser requires the exact five PUT fields, and the response validator rejects missing or extra fields. The service projects the setting independently from admin overrides, includes it in idempotency comparison and persists preference-only changes under the existing revision check and transaction. The existing Woo identity/onboarding checks, installation locking, conflict behavior, and no-store route response remain intact.

Unexpected service failures and invalid service response integrity are logged through the injected Shared logger with safe operation context and the original `Error`, then retain the sanitized 500 response. Expected malformed requests and handled conflict/integrity cases preserve their established status mappings; logger-sink failures cannot alter the response. OpenAPI documents the v2 payload. Changes stay within the hosted API contract, service, route, documentation, and focused tests.

### Reviewed Files

- `moda-interact-api/src/merchant/recovery-policy/contract.ts`
- `moda-interact-api/src/merchant/recovery-policy/service.ts`
- `moda-interact-api/src/merchant/recovery-policy/routes.ts`
- `moda-interact-api/openapi/woocommerce-merchant-recovery-policy-v1.yaml`
- Recovery-policy unit/PostgreSQL tests and Attempt 1 Completion Report.
- Implementation/database submodule branch and publication evidence.

### Validation Reviewed

- Prisma Client generation and `tsc --noEmit -p tsconfig.json --pretty false` passed, per the task report.
- Focused recovery-policy unit tests: 25 passed, including strict DTO validation, default OFF, preference-only updates, revision behavior, admin override, authorization, malformed payloads, and Shared logger failure handling.
- Disposable PostgreSQL migration harness passed, applying all 64 migrations including the ARCH-050 migration and passing both included integration tests.
- Targeted ESLint and `git diff --check` passed.
- Implementation branch `task/ARCH-050-API-001` is clean and published at `ba2541ef869836c20953ae236dd401cde104dbd1`; its database submodule is at accepted commit `2f702f52372d648abc5f080f02f722046d0e9271`. Neither task branch was merged to `main`.

### Architecture Conformance

Conforms to ARCH-050: the API remains the HTTP contract owner, and the preference is top-level and independent of admin-overridable policy values. No WooCommerce plugin, Shopify, Background, or database source changes were introduced; the database gitlink points to the separately accepted schema implementation.

### Dependency Frontier

This task uses `completion_mode: automatic`; architect acceptance completes Attempt 1. `ARCH-050-WOOCOMMERCE-001` depends on this task and is otherwise eligible, so its canonical task status advances from `pending` to `ready` at Attempt 0. `ARCH-050-SYSTEM-TEST-002` remains pending because its WooCommerce and other declared implementation prerequisites are incomplete; system testing remains terminal and does not gate implementation.

### Lifecycle

`status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. Neither task branch was merged to `main`.
