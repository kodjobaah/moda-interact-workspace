---
id: ARCH-026-SYSTEM-TEST-001
architecture_id: ARCH-026
title: Certify WooCommerce read authorisation and outbound provider access
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-WOOCOMMERCE-015
  - ARCH-026-API-008
enables: []
created: 2026-10-10
updated: 2026-10-10
---

# Certify WooCommerce read authorisation and outbound provider access

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Independently verify a real merchant-authorised, read-only WooCommerce API grant from installed plugin to hosted storage to authenticated provider GET, including failure, tenant and billing isolation.

## Context

DATABASE-003, API-007, API-008 and WOOCOMMERCE-015 introduce three distinct security boundaries: existing plugin-to-Moda installation identity, native WooCommerce merchant consent/callback, and Moda-to-WooCommerce read access. Unit tests cannot prove the actual WordPress approval, HTTPS callback delivery, encrypted persistence and provider read work together. This task is terminal architecture verification and must not gate unfinished implementation tasks.

## Scope

`moda-interact-system-test` only:

- Add deterministic setup/orchestration and evidence collection for an isolated WooCommerce store/administrator and disposable Moda PostgreSQL test Shop.
- Exercise real `scope=read` grant approval, callback/return ordering, reconnect, denial, expiry, replay, re-authorisation and revocation.
- Read bounded product data through API-008's server-owned provider port, without exposing keys to any client or constructing arbitrary requests.
- Verify no changes to initial Free-plan billing/entitlement, Shop international context or the existing inbound installation credential.

## Out of Scope

- Implementation fixes in WooCommerce/API/Database repositories, production credentials, write/read_write API scopes or arbitrary provider read coverage.
- Commerce/MCP or ARCH-030 tool-execution integration (a separately approved consumer task is required).
- New Gateway, shared contract, provider infrastructure or general performance harness.

## Requirements

1. Run against disposable/non-production resources; the Woo provider callback must be reachable over approved HTTPS. A local-only fixture without reachable callback is **blocked**, not considered a pass. Do not weaken callback state/SSRF or production TLS protections to make the test green.
2. Verify a real WordPress administrator approves a dedicated read-only key; forged callback, `read_write` payload, wrong Shop, replay, expired attempt and stale reconnect cannot produce an active grant.
3. Test asynchronous callback-before-return and return-before-callback sequencing; the UI must not treat the browser `success` query parameter as proof.
4. Prove a second Shop cannot borrow another Shop's key, and the selected outbound read connection supports only the initial approved product GET operations without leaking secrets.
5. Verify `401`/`403`/timeout, merchant denial, revocation and re-authorisation preserve Moda Connect, automatic Free subscription, lifetime credits and administrator/store locale separation.
6. Keep test executors, fixture builders, assertions, provider fakes/real-environment adapters and evidence reporters modular, following the established system-test structure.

## Work Items

- [ ] Add isolated Woo store and API/PostgreSQL fixtures with a secure real callback path.
- [ ] Implement lifecycle and negative-condition black-box scenarios with bounded log/evidence inspection.
- [ ] Verify provider product-read success, response bounds, no credential exposure and cross-tenant denial.
- [ ] Verify successful first Connect still automatically assigns Free credits and remains stable across failures/reconnect/revoke.
- [ ] Record independent automated evidence plus any actual WordPress/LocalWP browser observations.

## Interfaces / Contracts

- **Dependencies:** API-007 grant/status/callback, API-008 provider connection, WOO-015 privileged local REST/UI, DATABASE-003 persistence.
- **Evidence:** Established `moda-interact-system-test` run/report format; no new business contract published.

## Dependencies

- `ARCH-026-WOOCOMMERCE-015` — completed merchant-facing consent and 20-locale packaged plugin.
- `ARCH-026-API-008` — completed credential resolution and outbound Woo GET connector.

## Enables

None. This is a terminal system-test task.

## Acceptance Criteria

- [ ] Real approved Woo `read` permission results in encrypted, tenant-bound persistence and a successful bounded provider product GET.
- [ ] Rejected/forged/mismatched/expired/replayed grants cannot be used; no `write` or `read_write` scope is requested or accepted.
- [ ] Reconnect/denial/revoke/key-invalid cases remain tenant-safe and do not change the existing Moda installation credential or Free-plan/credit state.
- [ ] WordPress local UI status, server status and callback ordering agree in both German and English administrator locale without store-language mutation.
- [ ] No raw Woo consumer keys, secrets or Authorization headers appear in browser responses, logs or evidence; the opaque one-time callback state is exposed only where required inside the Woo authorisation URL and is never copied to normal logs or evidence artefacts.
- [ ] Required tests produce durable evidence and no blocked provider/HTTPS prerequisite is mislabeled PASS.

## Validation

- [ ] Execute declared system-test scripts for selected black-box scenarios with fixture setup and cleanup.
- [ ] Inspect provider/HTTP transport behavior, database integrity and logs; report true PASS/FAIL/BLOCKED counts.
- [ ] `git diff --check` and dedicated parent/implementation worktree evidence.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set task to `review`, complete its evidence-backed Completion Report, return to `moda_architect` and STOP. Do not modify producer/consumer implementations.

## Implementation Notes

System-test becomes Ready only after all implementation dependencies are architect-accepted Complete. The developer may perform manual Woo/LocalWP validation before running it. When external callback ingress is unavailable, explicitly report BLOCKED with the missing prerequisite; do not generate fake evidence of provider approval.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Await repository implementation and Completion Report.
