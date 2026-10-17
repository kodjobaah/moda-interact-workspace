---
id: ARCH-035-WOOCOMMERCE-014
architecture_id: ARCH-035
title: Proxy feature preferences and Merchant Knowledge through WordPress
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 50
executor: developer
claimed_at: 2026-10-17T11:06:29Z
attempt: 1
depends_on: [ARCH-035-API-014, ARCH-035-API-015, ARCH-035-API-016, ARCH-035-API-017]
enables: [ARCH-035-WOOCOMMERCE-015]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-WOOCOMMERCE-014 — Proxy feature preferences and Merchant Knowledge through WordPress

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- **Initial dependency-ready state (2026-10-17).** The canonical parent task worktree recorded dependency eligibility at Attempt 0 before the developer takeover and claim below.

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
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. WooCommerce must not import `@modainteract/moda-interact-shared/logging` into PHP or browser code. Where diagnostic logging is genuinely needed in the WordPress plugin, use existing WordPress/WooCommerce facilities with bounded, redacted metadata; the hosted Node.js API owns shared-logger integration.
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
- Keep browser-to-WordPress requests and PHP-to-Moda requests separately bounded. Add PHP controller/API client/response-contract tests within the existing `tests/` suite, plus negative tests for host validation, timeouts, malformed JSON and failure mapping. This task's implementation does **not** modify the native screen, which remains WOO-015's responsibility. No LocalWP startup, connection or interactive manual validation is assigned to the WOO-014 repository agent; use PHPUnit/HTTP fixtures for PHP boundary proofs. Any live LocalWP check is developer-owned and outside this task's agent Validation gate.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

Logging/runtime boundary: this is a WordPress/PHP proxy, not a Node.js service. Do not add `@modainteract/moda-interact-shared/logging`, another generic logger or a Node-only package to the plugin. Preserve existing error handling and fail-closed security checks. Optional PHP diagnostics must use bounded, redacted WordPress/WooCommerce facilities and must not expose installation credentials, authorisation headers, signed R2 URLs, uploaded file contents or customer data. The hosted `moda-interact-api` owns its own shared structured logging.

## Completion Report

### Status

In Progress — developer takeover and Attempt 1 claim recorded on 2026-10-17; implementation has not yet begun.

### Files Changed

None.

### Work Completed

Execution preparation and the durable developer claim are recorded below. No implementation files have been changed in Attempt 1 yet.

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

## Dependency Frontier Reconciliation (2026-10-17)

API-017 was explicitly completed on its developer-owned task branch after an accepted review. Canonical task routes report all four declared prerequisites complete: API-014, API-015, API-016 and API-017. This unclaimed task is therefore promoted from `pending` to `ready`; `executor` and `claimed_at` remain null and `attempt` remains 0. The canonical parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-014` on `task/ARCH-035-WOOCOMMERCE-014`, created from refreshed `origin/main` at `66b545426e1ced9dfbd05a79dde340db4cfc27f0`. No implementation worktree was created, no attempt was claimed, and no task or main branch was merged.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-014`, explicitly taking over this ready agent-owned task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_woocommerce`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged.

## Developer Claim — Attempt 1

**Claimed — 2026-10-17T11:06:29Z.** The task transitioned from `ready`, Attempt 0, null executor to `in_progress`, Attempt 1, `executor: developer`.

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-014`, branch `task/ARCH-035-WOOCOMMERCE-014`. It was clean before the claim. The task remote was already current at `f34f7958292660a84935c7c7a6ca2cbdb62bc8db`; after fetch, the branch fast-forwarded cleanly from current `origin/main` to `012707c91b12f29c5da333f3df8bc462a2fd608c`. No merge into `main` was performed as part of this preparation.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-014`, branch `task/ARCH-035-WOOCOMMERCE-014`. Created because no local/remote task branch or canonical worktree registration existed, from fetched `origin/main` at `56c5acd6a20c0c1c15897bfa0725f7ea511c7f04`; the new worktree is clean and contains that mainline commit.
- The shared WooCommerce source checkout contains unrelated local edits under `moda-tools/render-localwp/` and an untracked `typescript` path. These were left untouched; all implementation work will use the isolated worktree above.
- Dependency routes were rechecked immediately before claim: API-014, API-015, API-016 and API-017 all report `complete`.
- Required focused validation remains to be run during implementation: PHPUnit proxy authorization/nonce/capability/upload tests, fixture HTTP/R2 failure tests, relevant PHP lint and declared JS/PHP/build/ZIP checks, plus `git diff --check`.
