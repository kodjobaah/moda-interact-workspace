---
id: ARCH-050-API-002
architecture_id: ARCH-050
title: Project a tenant-validated recovery reference in Woo hosted Support reads
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-WOOCOMMERCE-002
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-26
---

# Project a tenant-validated recovery reference in Woo hosted Support reads

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Extend existing Woo hosted Support reads with a safe, structured recovery action target for approved system notifications.

## Context

`src/merchant/support/read.service.ts` projects Support SQL rows and `contract.ts` validates exact v1 response shapes. The Woo client validates strict fields too. Authenticated installation and shop enforcement already live in the API route/service.

## Scope

**Modify in `moda-interact-api/`:**

- `src/merchant/support/contract.ts` — history-page schemaVersion 2 and `SupportMessage.checkoutRecoveryId`; compose/read receipt contracts remain v1.
- `src/merchant/support/read.service.ts` — tenant-validated SQL projection while preserving `assertSupportInstallation`, pagination, translations and unread counts.
- `src/merchant/support/routes.ts` — only if needed for v2 history validation; retain GET/POST/read path and auth.
- `tests/unit/merchant/support/` and `tests/integration/merchant/support/` — v2 and recovery reference cases.

Do not write Support notices or change Woo plugin here; BACKGROUND-001 and WOOCOMMERCE-002 own those responsibilities.

## Out of Scope

- Writing notifications, introducing external href, changing Woo PHP/JS clients, or expanding Support send/mark-read APIs.

## Requirements

- Only `GET /v1/merchant/support/messages?page=&pageSize=` changes successful history-page `schemaVersion` from `1` to `2`. Compose/read **receipt** DTOs and endpoints stay `schemaVersion:1`.
- Every history `items[]` object adds required `checkoutRecoveryId: string | null`. Nonrecovery, deleted, invalid or other-shop records return `null`, never omit field or expose raw unverified FK.
- In `read.service.ts`, LEFT JOIN `"commerce"."CheckoutRecovery" r` with both `r.id = m.checkoutRecoveryId` AND `r.shopId = t.shopId`; CASE-project `r.id` only when `kind=SYSTEM`, `state=AVAILABLE`, `systemCode=RECOVERY_INITIAL_OUTREACH_SENT`, `systemVersion='1'`.
- Preserve installed Woo principal check `assertSupportInstallation(..., {write:false,allowSuspended:true})`, exact validators, page sizes 10/25/50, unread, translation logic and message order.
- Do not expose URLs, phone numbers, basket details, or any new write action. Coordinate API v2 rollout with WooCommerce plugin's strict PHP/browser v2 validation.
- `src/merchant/support/routes.ts` already receives an injected `StructuredLogger` from `@modainteract/moda-interact-shared/logging`. Reuse it and existing `merchant.support.*` event names; do not add a feature-local logger, raw `console.*` or new telemetry transport.
- A genuine Support SQL/query, projection or unexpected v2 DTO failure must reach the existing route catch, emit a bounded `logger.error("merchant.support.failed", {operation:"list", reason:"integrity"|"internal", error})`, and return the existing sanitized HTTP 500. Do **not** convert exceptions into an empty page, `checkoutRecoveryId:null`, `[]` or a fabricated successful v2 response. Expected unauthorized/missing/deleted/cross-shop recovery references remain **normal null** projections, not failures; keep handled auth/conflict status mapping. Logging sink failures cannot change the status. No SQL parameters, body, phone, URL, sensitive customer values or raw request payloads in logs.

## Work Items

- [ ] Change history-page v2 types/exact validators and leave v1 compose/read receipts untouched.
- [ ] Add joined same-shop CASE projection and nullable DTO property for all messages.
- [ ] Test correct shop, mismatched shop, missing link, unexpected version, non-SYSTEM, v2 strictness and v1 receipt regressions.
- [ ] Test a thrown Support read/query error separately from a valid nullable recovery projection: structured failure event + 500 (not a successful empty result); exercise throwing injected log sink.

## Interfaces / Contracts

```ts
type SupportMessageV2 = SupportMessageV1 & {
  checkoutRecoveryId: string | null;
};
type SupportPageV2 = {
  schemaVersion: 2;
  page: number;
  pageSize: 10 | 25 | 50;
  total: number;
  totalPages: number;
  unread: number;
  items: SupportMessageV2[];
};
```

- `GET /v1/merchant/support/messages` returns v2; `POST /v1/merchant/support/messages` compose and `POST /v1/merchant/support/messages/:id/read` remain v1 receipts.
- No absolute URL or authorization token in response. WordPress uses its own fixed route builder and separately protected recovery details API.
- Existing API `logger:StructuredLogger` injection is the only required logger contract. On caught unexpected history-read failures emit `merchant.support.failed` with operation `list`, a stable reason and bounded error context.

## Dependencies

- `ARCH-050-DATABASE-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-WOOCOMMERCE-002` may become eligible only after architect acceptance and Complete state.
- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Recognised v1-code SYSTEM notice returns linked recovery ID only when same-shop, available and nondeleted.
- [ ] Forged cross-shop FK, missing recovery, malformed code/version or unrelated Support message returns null.
- [ ] History page strict schemaVersion 2 accepted/rejected correctly; compose/read receipts still validate v1.
- [ ] Existing page counts, translations and unread/read semantics have no regression.
- [ ] Expected null recovery references remain non-errors; actual database read failures are logged with the canonical shared logger and returned as 500, not silently discarded.

## Validation

- [ ] Extend `npm run test:arch035-woo-support:unit` and `npm run test:arch035-woo-support:postgres` fixtures.
- [ ] `npm run typecheck`, relevant lint, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Do not expose `m.checkoutRecoveryId` blindly: an FK proves the recovery exists but does not prove the Support thread belongs to that recovery's shop. The API is the single owner of this hosted HTTP contract; WOOCOMMERCE-002 mirrors strict validation. The persisted `systemVersion` is the string `"1"`.

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
