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
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-WOOCOMMERCE-002
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-27
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

- [x] Change history-page v2 types/exact validators and leave v1 compose/read receipts untouched.
- [x] Add joined same-shop CASE projection and nullable DTO property for all messages.
- [x] Test correct shop, mismatched shop, missing link, unexpected version, non-SYSTEM, v2 strictness and v1 receipt regressions.
- [x] Test a thrown Support read/query error separately from a valid nullable recovery projection: structured failure event + 500 (not a successful empty result); exercise throwing injected log sink.

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

- [x] Recognised v1-code SYSTEM notice returns linked recovery ID only when same-shop, available and nondeleted.
- [x] Forged cross-shop FK, missing recovery, malformed code/version or unrelated Support message returns null.
- [x] History page strict schemaVersion 2 accepted/rejected correctly; compose/read receipts still validate v1.
- [x] Existing page counts, translations and unread/read semantics have no regression.
- [x] Expected null recovery references remain non-errors; actual database read failures are logged with the canonical shared logger and returned as 500, not silently discarded.

## Validation

- [x] `npm run test:arch035-woo-support:unit` passed (14 tests).
- [x] `npm run test:arch035-woo-support:postgres` passed (1 integration test; disposable PostgreSQL migration and fixture run).
- [x] `npm run typecheck`, `npm run lint`, and `git diff --check` passed.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Do not expose `m.checkoutRecoveryId` blindly: an FK proves the recovery exists but does not prove the Support thread belongs to that recovery's shop. The API is the single owner of this hosted HTTP contract; WOOCOMMERCE-002 mirrors strict validation. The persisted `systemVersion` is the string `"1"`.

## Completion Report

### Status

Ready for Architect Review after completing the v2 history projection and failure-path logging requirements.

### Files Changed

`src/merchant/support/contract.ts`; `src/merchant/support/read.service.ts`; `src/merchant/support/routes.ts`; `openapi/merchant-support-v1.yaml`; `tests/unit/merchant/support/contract.test.ts`; `tests/unit/merchant/support/openapi.test.ts`; `tests/unit/merchant/support/routes.test.ts`; `tests/integration/merchant/support/service.postgres.test.ts`.

### Work Completed

Implemented strict history-page v2 validation with required nullable `checkoutRecoveryId`; compose and mark-read receipts remain strict v1. Read SQL now LEFT JOINs CheckoutRecovery by both message reference and Support-thread shop, then projects the ID only for available SYSTEM notices with code `RECOVERY_INITIAL_OUTREACH_SENT` and version `1`. Missing, deleted, cross-shop, malformed, wrong-version and unrelated records return `null`. Pagination, translations, unread counts, ordering, installation checks and existing command routes remain unchanged.

Unexpected Support read and v2 response failures now reach `merchant.support.failed` with operation, stable reason and the original `Error` passed to the Shared logger for bounded serialization; the route returns the existing sanitized 500. A throwing log sink cannot interrupt that response. Unit coverage verifies query failure/error fields, DTO integrity failure and logger-sink isolation; PostgreSQL coverage verifies valid and invalid recovery references.

### Validation Results

`npm run test:arch035-woo-support:unit` passed (14 tests). `npm run test:arch035-woo-support:postgres` passed (1 integration test after applying all 64 migrations to disposable PostgreSQL). `npm run typecheck`, `npm run lint`, and `git diff --check` passed. The initial unit run identified and corrected an OpenAPI schema-version mismatch; the final run passed.

### Deviations

No product-scope deviations. Dependency installation and test execution required the isolated worktree’s permitted filesystem/runtime access; install artifacts remain ignored and are not part of the commit.

### Assumptions

The recorded ARCH-050 database submodule commit from the prepared packet is authoritative for this attempt.

### Unresolved Issues

None.

### Architectural Concerns

None discovered; hosted API v2 remains aligned with the task’s coordinated WooCommerce contract.

### Task Branch / Worktree Evidence

Task branch: `task/ARCH-050-API-002`.

Physical worktree isolation: canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-API-002`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-API-002`. Both use branch `task/ARCH-050-API-002`; neither shared workspace checkout was switched, neither shared implementation checkout was switched, and no other task worktree was reused.

Start-of-attempt synchronization: parent remote task branch fast-forwarded `not-needed`, parent `origin/main` `already-current`; implementation remote task branch fast-forwarded `not-needed`, implementation `origin/main` `already-current`.

Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; database submodule `database` initialized at `2f702f52372d648abc5f080f02f722046d0e9271`.

Implementation repository: `moda-interact-api`, commit `651c04e4a3cfc6b10ec7e81daf1274d54bcabe8`, pushed to `origin/task/ARCH-050-API-002`.

Parent workspace claim commit: `6265a655f812b5035f90550fa0be22490c3ce824`, pushed. Parent review submission commit: `233e034649dfc942ce3bf0a5c3268b99b1c4420c`, pushed to `origin/task/ARCH-050-API-002`. The implementation submodule gitlink was not staged; neither task branch was merged into `main`.

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
