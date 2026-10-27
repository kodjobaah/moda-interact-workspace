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
status: blocked
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
- `parseRecoveryPolicyUpdate` must reject absent/extra fields, `
- `parseRecoveryPolicyUpdate` rejects absent or extra keys, non-Boolean values or Boolean-like strings; keep existing delay bounds and 2048-byte body limit. Update `isRecoveryPolicyResponse()` exact key validation to v2.
- `projection(...)` reads `settings?.notifyOnInitialRecoveryOutreach ?? false` separately from `ShopRecoveryPolicyOverride`. `matches(settings, update)` includes this Boolean so a preference-only write cannot be silently skipped.
- Keep `assertCurrentShop()` row lock and `recovery_policy_conflict` revision behaviour; in current no-op path the Boolean must match too. Write the preference in the same ShopSettings transaction as existing delay/follow-up fields.
- Keep Woo identity, onboarding and discount selection untouched; coordinate deployment with strict WordPress PHP/JS validators in WOOCOMMERCE-001.
- `src/merchant/recovery-policy/routes.ts` already receives `logger: StructuredLogger` from the **canonical** `@modainteract/moda-interact-shared/logging` setup. Reuse that injected logger; do not instantiate another generic logger or add `console.*`. Preserve its existing `merchant.recovery_policy.*` event names, status codes and no-store responses.
- Every newly caught unexpected persistence/validation-integrity exception must produce `logger.error("merchant.recovery_policy.access.failed", {operation, reason:"internal", error})` with safe context before the **existing** sanitized HTTP 500 mapping. Keep expected malformed request/auth failures as their defined 400/401/403 paths; stale revision 409 remains a handled `warn`, not an internal-error event. Do not log request bodies, installation credential, form payload or raw HTTP response. No catch may return a false 200/default-OFF on DB exception. Shared log-sink failure must not change API response/status.

## Work Items

- [x] Update v2 DTO/parser/response validator with top-level Boolean and strict field set.
- [x] Update projection, no-op comparison, and revision-protected persistence for this field. Typecheck is currently blocked because the pinned Prisma client lacks the completed database field.
- [x] Add unit/Postgres tests for default OFF, ON/OFF, preference-only save, stale revisions, admin override, unauthorised installation and malformed payloads. PostgreSQL assertions are written but cannot execute until the API submodule points at the accepted schema revision.
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

- [ ] Unconfigured shop reads OFF in v2 response; ON/OFF survives save and reload. Unit coverage passes; PostgreSQL persistence remains blocked on the pinned schema.
- [ ] Notification-only update persists and advances settings revision, while unchanged update remains no-op. Unit coverage passes; PostgreSQL persistence remains blocked on the pinned schema.
- [ ] Stale revisions, malformed/extra keys, unsupported shops and revoked installations fail closed.
- [ ] Admin override never changes merchant opt-in; existing delay/follow-up/offer data survives.
- [ ] Hosted API records a bounded structured failure for unhandled server exceptions and returns the pre-existing error status without exposing the exception or silently defaulting a failed read to OFF.

## Validation

- [x] Focused `tsx --test tests/unit/merchant/recovery-policy/*.test.ts` passed (25 tests). PostgreSQL integration test coverage was updated but not run because the API worktree's pinned database submodule does not contain the required column.
- [x] Route failure tests spy on the injected Shared logger and verify original error, operation, reason, sanitized 500/no-store response, and sink-failure isolation for 200/409/500. Existing 400/401/409 mappings pass.
- [x] `npm run typecheck` was run and failed with TS2339 because `notifyOnInitialRecoveryOutreach` does not exist on the generated `ShopSettings` type from pinned database commit `508a89463ccb24dcc31e5f38e04be8cfd10ad690`. Targeted ESLint and `git diff --check` passed.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

API is the **HTTP contract owner**; WordPress PHP/JS validators will mirror the v2 DTO in WOOCOMMERCE-001 without a new Node Shared dependency. Keep `merchant/effective` recovery-policy shape unchanged; the notification toggle is independent of admin overrides.

## Completion Report

### Status

Blocked — the API worktree's pinned database submodule predates the accepted ARCH-050 schema change.

### Files Changed

Partial implementation in the API task worktree:
- `src/merchant/recovery-policy/contract.ts`
- `src/merchant/recovery-policy/service.ts`
- `src/merchant/recovery-policy/routes.ts`
- `openapi/woocommerce-merchant-recovery-policy-v1.yaml`
- `tests/unit/merchant/recovery-policy/contract.test.ts`
- `tests/unit/merchant/recovery-policy/service.test.ts`
- `tests/unit/merchant/recovery-policy/routes.test.ts`
- `tests/unit/merchant/recovery-policy/openapi-contract.test.ts`
- `tests/integration/merchant/recovery-policy/service.postgres.test.ts`

### Work Completed

Drafted the API v2 DTO/parser/validator and OpenAPI contract with the top-level notice preference. Added the preference to the independent ShopSettings projection, no-op comparison and revision-checked write. Added unit and PostgreSQL assertions for defaults, ON/OFF, preference-only revision changes and route error logging. Unexpected read/write failures log the original error via the injected Shared logger with safe operation context; logger-sink exceptions do not alter API response semantics.

The implementation cannot be completed or safely submitted for review yet: the API task's exact database submodule commit does not contain the prerequisite column. The generated Prisma client therefore cannot typecheck the new persistence access.

### Validation Results

- Passed: focused recovery-policy unit tests, `tsx --test tests/unit/merchant/recovery-policy/*.test.ts` (25 tests).
- Passed: targeted ESLint for all changed TypeScript files and `git diff --check`.
- Blocked: `npm run typecheck` regenerated the client from the API worktree's pinned database schema and failed with TS2339 at the service projection/write and integration assertion because `ShopSettings.notifyOnInitialRecoveryOutreach` is absent.
- Not run: disposable PostgreSQL integration test; it depends on that missing Prisma/schema field.
- No changes were made to the database submodule or its gitlink.

### Deviations

Updated the existing OpenAPI description/schema so its strict response and request documents match the required schemaVersion 2 payload. The API repository's nested database submodule was not advanced because the assigned API agent VCS policy forbids publishing an unmerged implementation gitlink.

### Assumptions

The accepted ARCH-050-DATABASE-001 implementation must first be incorporated into the database revision pinned by the API repository. The API change should resume against that synchronized schema/client rather than stage a gitlink to an unmerged feature branch.

### Unresolved Issues

Dependency mismatch: the accepted database task adds `ShopSettings.notifyOnInitialRecoveryOutreach Boolean @default(false)`, but API implementation preparation pinned its `database` submodule at `508a89463ccb24dcc31e5f38e04be8cfd10ad690`, where the field is absent. The resulting Prisma Client has no such property. `moda_architect`/the repository maintainer must reconcile and publish the API repository's database submodule pointer to the accepted database revision before this task can finish. The source and test changes are retained in the API task worktree for continuation.

### Architectural Concerns

The canonical dependency metadata is complete, but the API implementation checkout does not include that dependency's schema commit. This must be reconciled without an API task agent staging an unmerged database gitlink.

### Task Branch / Worktree Evidence

Canonical launcher claimed Attempt 1 after the dependency status gate passed. Parent branch/worktree: `task/ARCH-050-API-001`, `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-API-001`; implementation branch/worktree: `task/ARCH-050-API-001`, `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-API-001`. Both branches were already current with `origin/main`; the implementation submodule was initialized at `database` commit `508a89463ccb24dcc31e5f38e04be8cfd10ad690`. The accepted ARCH-050-DATABASE-001 report records its implementation commit as `2f702f52372d648abc5f080f02f722046d0e9271` and confirms the schema field exists there. Partial API implementation commit `dd12c25` is pushed to `origin/task/ARCH-050-API-001` for continuation after the dependency pointer is reconciled. No task branch is merged to `main`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet reviewed.

### Follow-up

None.
