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
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-10-27T13:36:31Z
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

- [ ] Update v2 DTO/parser/response validator with top-level Boolean and strict field set.
- [ ] Update projection, no-op comparison, and revision-protected persistence for this field.
- [ ] Add unit/Postgres tests for default OFF, ON/OFF, preference-only save, stale revisions, admin override, unauthorised installation and malformed payloads.
- [ ] Extend existing route/logger-spy tests for unexpected save failure: structured error event (with safe `error`), correct 500/no-store, and no fake successful preference result; conflicts remain 409 and warn only.

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

- [ ] Unconfigured shop reads OFF in v2 response; ON/OFF survives save and reload.
- [ ] Notification-only update persists and advances settings revision, while unchanged update remains no-op.
- [ ] Stale revisions, malformed/extra keys, unsupported shops and revoked installations fail closed.
- [ ] Admin override never changes merchant opt-in; existing delay/follow-up/offer data survives.
- [ ] Hosted API records a bounded structured failure for unhandled server exceptions and returns the pre-existing error status without exposing the exception or silently defaulting a failed read to OFF.

## Validation

- [ ] Run focused `tsx --test` tests in `tests/unit/merchant/recovery-policy/` and corresponding disposable PostgreSQL integration tests.
- [ ] Route failure test spies on the injected shared logger to verify error event and no secrets, while preserving response mapping for 400/401/409/500.
- [ ] `npm run typecheck`, targeted lint/build checks defined by `package.json`, and `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

API is the **HTTP contract owner**; WordPress PHP/JS validators will mirror the v2 DTO in WOOCOMMERCE-001 without a new Node Shared dependency. Keep `merchant/effective` recovery-policy shape unchanged; the notification toggle is independent of admin overrides.

## Completion Report

### Status

Not Started.

### Files Changed

None (definition only).

### Work Completed

None.

### Validation Results

Not executed; no implementation claimed.

### Deviations

None.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Not materialised. Launcher-resolved parent/implementation task worktree, synchronization and branch evidence are required at execution.

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
