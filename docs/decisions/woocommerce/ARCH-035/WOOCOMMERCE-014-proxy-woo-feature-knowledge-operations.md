---
id: ARCH-035-WOOCOMMERCE-014
architecture_id: ARCH-035
title: Proxy feature preferences and Merchant Knowledge through WordPress
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-API-014, ARCH-035-API-015, ARCH-035-API-016, ARCH-035-API-017]
enables: [ARCH-035-WOOCOMMERCE-015]
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-014 — Proxy feature preferences and Merchant Knowledge through WordPress

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- **Defined but not materialised.** This portable task definition did not create a parent/implementation worktree, branch, commit, push or claim. The real `/moda-task ARCH-035-WOOCOMMERCE-014` launcher owns canonical materialisation and start-of-attempt evidence.

## Objective

Implement privileged server-mediated WordPress REST proxies for approved Woo feature-preference, knowledge-source and file operations.

## Context

W003/W004 currently have production unavailable adapters. The hosted API tasks own authoritative state and validation; WordPress remains a security boundary and Woo site identity/credential guard.

## Scope

- Add bounded WordPress PHP REST routes and API client methods mapping the exact accepted API-014..017 contracts; enforce `manage_woocommerce`, nonce, connected Shop credential, site identity, revocation and safe error remapping on every request.
- Use WordPress plugin/server as the only hosted-API caller, with timeouts, bounded JSON/body/file upload sizes, allowed MIME/extensions, response schema and nonce/session handling.
- For file uploads: PHP receives temporary uploaded file from WordPress, obtains API-signed intent, validates signed-URL host against configured approved R2 endpoint, sends time-bounded PUT and calls finalize; no persistent local copy and no browser access to signed URL.
- Do not expose installation secrets in browser/logs; re-read installation guard before writes, reject stale credentials/changes, and preserve existing two-stage menus.
- Add PHP tests for authenticated/denied/revoked/cross-installation operations, error mapping, upload failure cleanup and size/MIME validation.

## Out of Scope

- Implementing business/entitlement decisions, hosted API endpoints, database schemas or browser React presentation.
- Adding permissive R2 CORS or WordPress persistent file storage.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Add bounded WordPress PHP REST routes and API client methods mapping the exact accepted API-014..017 contracts; enforce `manage_woocommerce`, nonce, connected Shop credential, site identity, revocation and safe error remapping on every request.
- [ ] Use WordPress plugin/server as the only hosted-API caller, with timeouts, bounded JSON/body/file upload sizes, allowed MIME/extensions, response schema and nonce/session handling.
- [ ] For file uploads: PHP receives temporary uploaded file from WordPress, obtains API-signed intent, validates signed-URL host against configured approved R2 endpoint, sends time-bounded PUT and calls finalize; no persistent local copy and no browser access to signed URL.
- [ ] Do not expose installation secrets in browser/logs; re-read installation guard before writes, reject stale credentials/changes, and preserve existing two-stage menus.
- [ ] Add PHP tests for authenticated/denied/revoked/cross-installation operations, error mapping, upload failure cleanup and size/MIME validation.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- WordPress `moda-interact/v1` privileged REST operations consistent with existing facade conventions; path details must be chosen to avoid collisions with existing registration, and mapped to API-014..017.
- Proxy canonical server responses and HTTP conflict/errors without fabricating success.

## Dependencies

- `ARCH-035-API-014` (must be Complete and architect accepted)
- `ARCH-035-API-015` (must be Complete and architect accepted)
- `ARCH-035-API-016` (must be Complete and architect accepted)
- `ARCH-035-API-017` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-015`

## Acceptance Criteria

- [ ] Every request enforces nonce, capability, connected-state, canonical-site identity and installation credential; no browser-to-hosted API direct path.
- [ ] File upload succeeds only after server-verified R2 PUT + finalize; URL redirect/SSRF and timeout/replay fail closed; credentials and signed URL are never reflected.
- [ ] No changes to existing Billing/recovery-policy/site categories routes; one failed R2 step does not claim uploaded/active state.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused PHPUnit proxy auth/nonce/capability/upload tests plus fixture HTTP/R2 failure tests.
- [ ] PHP lint, repository declared JS/PHP/build/ZIP checks as changed, `git diff --check`.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled WooCommerce-structure handoff (2026-10-16 22:56 snapshot)

- Extend the existing PHP plugin boundaries: register privileged route controllers through `includes/Runtime.php`, place domain controllers in `includes/Rest/`, add hosted API methods in `includes/Api/ModaApiClient.php` (or a narrow delegated client), and add strict response validation under `includes/Api/`. Do not wire PHP requests into a React view or create a parallel installation-credential resolver.
- Match existing `StoreCategoryController.php`, `RecoveryPolicyController.php` and `StoreContextController.php` patterns for the `moda-interact/v1` namespace, `manage_woocommerce`, WordPress REST nonce/session enforcement, canonical site-URL guard, connection record, `ModaApiClientException` and status mapping. Test both denied and stale-site/rotated-credential cases.
- WordPress receives the merchant file and performs a **server-side** signed R2 PUT using an explicit approved destination/host contract from API-017; reject all redirects, non-HTTPS destinations, DNS rebinding/private addresses and oversize/invalid MIME files. Do not log, cache or return signed URLs/credentials or persist WordPress uploads. Verify the connection identity again before finalising and do not claim successful source creation on an ambiguous/failed PUT.
- Keep browser-to-WordPress requests and PHP-to-Moda requests separately bounded. Add PHP controller/API client/response-contract tests within the existing `tests/` suite, plus negative tests for host validation, timeouts, malformed JSON and failure mapping. This task's implementation does **not** modify the native screen, which remains WOO-015's responsibility.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

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

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.
