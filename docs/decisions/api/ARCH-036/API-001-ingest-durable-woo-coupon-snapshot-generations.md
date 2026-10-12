---
id: ARCH-036-API-001
architecture_id: ARCH-036
title: Ingest Woo coupon snapshots into the existing discount catalogue
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-036-DATABASE-001", "ARCH-036-SHARED-003"]
enables: ["ARCH-036-WOOCOMMERCE-001", "ARCH-036-API-002", "ARCH-036-ADMIN-001", "ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-10-12
---

# ARCH-036-API-001 — Ingest Woo coupon snapshots into the existing discount catalogue

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Portable canonical task definition; **defined but not materialised**. No Git branch, worktree, commit or push has been made.

## Objective

Accept authenticated paginated Woo coupon snapshots and atomically promote completed generations in the existing discount tables.

## Context

The plugin pushes snapshot pages because self-hosted Woo sites are not reliably reachable for polling. The existing catalogue already tracks sync generation/token/status; DATABASE-001 adds durable bounded progress metadata.

## Scope

Expose installation-authenticated `start/page/complete` Woo coupon sync operations on Moda API. Validate Shared v1 batches, pagination and provider identity; stage new-generation data in the same existing discount rows while catalog status is SYNCING, and atomically promote completed generations/mark missing rows unavailable.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

Reject caller-supplied shop ownership, revoked installations, stale tokens, duplicate coupon identity and mismatched page digests. Pages are sequential, idempotent on exact replay, and bounded in records/size/time. Never expose partial new-generation data as CURRENT. A failed or abandoned sync remains non-current until successful full replacement; no silent reversion to stale CURRENT. Use Shop-scoped transaction locks and existing catalogue row for progress; no new staging table, Redis-only correctness state or unbounded transaction across network calls. Woo provider grant is unrelated to inbound installation credential.

## Work Items

- [ ] Implement installation-bound versioned start/page/complete route and validator.
- [ ] Perform bounded in-place pending-generation upserts with per-page replay proof.
- [ ] Atomically finalize availability and current-generation state; handle timeout/abort.
- [ ] Add provider/shop/auth failures, partial upload and duplicate/replay integration tests.

## Interfaces / Contracts

POST `/v1/merchant/discount-catalogue/sync/start`, `/page`, `/complete` (or equivalent fixed three operations with identical semantics); Shared `woo.discounts.sync.v1`; existing DB catalogue+discount rows.

## Dependencies

- `ARCH-036-DATABASE-001`
- `ARCH-036-SHARED-003`

## Enables

- `ARCH-036-WOOCOMMERCE-001`
- `ARCH-036-API-002`
- `ARCH-036-ADMIN-001`
- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] No new physical tables; Woo rows coexist with existing Shopify catalogue records.
- [ ] Only a successful completed full generation can become CURRENT and invalidate unseen Woo rows.
- [ ] Crash/retry/duplicate/out-of-order/foreign token and cross-tenant cases fail safely.
- [ ] Invalid/revoked installation cannot publish or retain a usable new generation.
- [ ] No coupon provider credentials or sensitive raw objects in logs.

## Validation

- [ ] API contract/parser/auth and partial-replay tests
- [ ] Disposable PostgreSQL concurrent generation, rollback and tombstone tests
- [ ] API typecheck/lint/test/build and `git diff --check`

## Implementation Notes

Do not extend the provider read-grant allowlist or implement merchant selection in this task.

For developer execution, use the canonical `/moda_developer_create ARCH-036-API-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-API-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.
