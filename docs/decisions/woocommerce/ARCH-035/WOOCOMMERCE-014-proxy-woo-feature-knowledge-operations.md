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
status: complete
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-014, ARCH-035-API-015, ARCH-035-API-016, ARCH-035-API-017, ARCH-035-API-018]
enables: [ARCH-035-WOOCOMMERCE-015]
created: 2026-10-16
updated: 2026-10-19
---

# ARCH-035-WOOCOMMERCE-014 — Proxy feature preferences and Merchant Knowledge through WordPress

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- **Initial dependency-ready state (2026-10-17).** The canonical parent task worktree recorded dependency eligibility at Attempt 0 before the developer takeover and claim below.
- **18 October architectural scope reconciliation:** the later approved browser-direct R2 transport replaces the original PHP binary uploader. API-018 is recorded Complete in the 18 October architecture snapshot and is now a declared dependency. The existing developer-owned `in_progress` Attempt 1 claim, physical worktree evidence and completion authority are preserved; do not reset the claim to Attempt 0 or revert execution to `agent`.


## Objective

Implement privileged WordPress REST brokers for approved Woo feature preferences, knowledge-source operations and metadata-only browser-direct R2 upload intent/finalisation.

## Context

W003/W004 currently have production unavailable adapters. The hosted API tasks own authoritative state and validation; WordPress remains a security boundary and Woo site identity/credential guard.

## Scope

- Add bounded WordPress PHP REST routes and API client methods mapping the exact accepted API-014..017 contracts; enforce `manage_woocommerce`, nonce, connected Shop credential, site identity, revocation and safe error remapping on every request.
- WordPress PHP remains the only browser-to-hosted-Moda API caller, with timeouts, bounded **metadata JSON** bodies/responses, strict schema and nonce/session/installation guards. PHP must not receive or forward CSV/XLSX file bytes.
- For uploads: PHP proxies authenticated **metadata-only** intent/finalise requests; on intent, validate and forward only the bounded API-018-approved presigned `uploadUrl`, expiry, `assetId`, limits and exact required headers to the authorised WordPress browser with no-store response. On finalise, recheck connection/session/nonce and send metadata to API-017. PHP never accepts, buffers, streams, proxies, persists or logs the file contents.
- Restrict handoff to the exact non-secret configured R2 account endpoint and bucket (`MODA_MERCHANT_KNOWLEDGE_R2_ENDPOINT`, `MODA_MERCHANT_KNOWLEDGE_R2_BUCKET`); both must agree with the hosted API sealed `merchant.knowledge.r2` destination. Reject missing/mismatched configuration; WordPress has no R2 secret, cURL upload dependency or local-file storage requirement.
- Do not expose installation secrets in browser/logs; re-read installation guard before writes, reject stale credentials/changes, and preserve existing two-stage menus.
- Add PHP tests for authenticated/denied/revoked/cross-installation metadata operations, response no-store/cache safety, unknown signed host/URL/header rejection, safe error mapping and rejection of binary/multipart upload attempts.

## Out of Scope

- Implementing business/entitlement decisions, hosted API endpoints, database schemas or browser React presentation.
- Issuing/uploading R2 object bytes in PHP, adding permissive R2 CORS or WordPress persistent file storage. R2 CORS belongs to GATEWAY-001 and browser transfer to WOO-015.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. WooCommerce must not import `@modainteract/moda-interact-shared/logging` into PHP or browser code. Where diagnostic logging is genuinely needed in the WordPress plugin, use existing WordPress/WooCommerce facilities with bounded, redacted metadata; the hosted Node.js API owns shared-logger integration.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [x] Add bounded WordPress PHP REST routes and API client methods mapping the exact accepted API-014..017 contracts; enforce `manage_woocommerce`, nonce, connected Shop credential, site identity, revocation and safe error remapping on every request.
- [x] Implement bounded metadata JSON requests/responses; reject multipart/file-body upload requests; preserve strict nonce/session and credential handling.
- [x] Expose the signed R2 PUT URL and **exact** signed headers to an authorised browser from a no-store WordPress response; broker finalisation metadata after connection revalidation. No PHP binary transport or local temporary file.
- [x] Do not expose installation secrets in browser/logs; re-read installation guard before writes, reject stale credentials/changes, and preserve existing two-stage menus.
- [x] Add PHP tests for authenticated/denied/revoked/cross-installation intent/finalise, non-cacheable signed-capability response, binary rejection, error mapping and bounded metadata validation.
- [x] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- WordPress `moda-interact/v1` privileged REST operations, using existing facade conventions and accepted API-014..017 endpoint paths plus the API-018 browser upload capability contract. No direct browser-to-hosted Moda API.
- Upload metadata routes: `POST /wp-json/moda-interact/v1/merchant/merchant-knowledge/upload-intents` and `POST /wp-json/moda-interact/v1/merchant/merchant-knowledge/upload-finalize`. Intent accepts bounded JSON and returns the exact short-lived `uploadUrl`, `assetId`, `expiresAt`, `maxUploadBytes` and `requiredHeaders` (signed `Content-Type`, `If-None-Match: *`, `x-amz-meta-sha256`) with `Cache-Control: private, no-store`. Finalise accepts metadata after browser PUT and proxies API-017 authoritative verification. The older multipart `/upload` route is not supported.
- Proxy canonical server responses and HTTP conflict/errors without fabricating success.

## Dependencies

- `ARCH-035-API-014` (must be Complete and architect accepted)
- `ARCH-035-API-015` (must be Complete and architect accepted)
- `ARCH-035-API-016` (must be Complete and architect accepted)
- `ARCH-035-API-017` (Complete; historical upload lifecycle unchanged)
- `ARCH-035-API-018` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-015`

## Acceptance Criteria

- [x] Every request enforces nonce, capability, connected-state, canonical-site identity and installation credential; no browser-to-hosted API direct path.
- [x] Browser receives signed R2 URL and required headers **only** through a privileged no-store intent response; WordPress does not receive file bytes, and hosted API finalisation remains authoritative. Unauthorised callers, stale installation state, unsafe URL destinations and malformed signed headers fail closed; signed URLs are not logged, persisted or exposed through errors. Browser redirect/preflight/PUT handling belongs to WOO-015, object overwrite/replay verification to API-017/018, and R2 origin CORS to GATEWAY-001.
- [x] No changes to existing Billing/recovery-policy/site categories routes; one failed R2 step does not claim uploaded/active state.
- [x] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [x] Focused PHPUnit proxy auth/nonce/capability, signed-intent/finalise metadata, no-store, binary rejection, unsafe URL, malformed response and upstream failure mapping tests.
- [x] PHP lint, declared PHP tests/JS tests as affected, build and plugin ZIP packaging checks (new capability validator included, obsolete PHP uploader excluded), `git diff --check`.
- [x] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update the developer-owned Completion Report, set `status: review`, and stop. Formal completion requires the Accepted review and a separate explicit developer decision (`/moda_developer_update ARCH-035-WOOCOMMERCE-014 complete`) because `completion_mode: developer`. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled WooCommerce-structure handoff (2026-10-16 22:56 snapshot)

- Extend the existing PHP plugin boundaries: register privileged route controllers through `includes/Runtime.php`, place domain controllers in `includes/Rest/`, add hosted API methods in `includes/Api/ModaApiClient.php` (or a narrow delegated client), and add strict response validation under `includes/Api/`. Do not wire PHP requests into a React view or create a parallel installation-credential resolver.
- Match existing `StoreCategoryController.php`, `RecoveryPolicyController.php` and `StoreContextController.php` patterns for the `moda-interact/v1` namespace, `manage_woocommerce`, WordPress REST nonce/session enforcement, canonical site-URL guard, connection record, `ModaApiClientException` and status mapping. Test both denied and stale-site/rotated-credential cases.
- WordPress handles metadata-only intent and finalise. From authenticated API-018 contract, validate that the returned signed destination is HTTPS and exactly the approved R2 S3 endpoint with bounded expiry/headers; return that short-lived capability **only to the authorised administrator in a no-store response**. Never log the query string, store it in WordPress options, add installation credentials to R2 requests or accept binary in PHP. Browser sends bytes directly to R2; the API verifies finalisation. Recheck the current Woo site identity/credential before finalise and never infer success from the intent response.
- Keep browser-to-WordPress requests and PHP-to-Moda requests separately bounded. Add PHP controller/API client/response-contract tests within the existing `tests/` suite, plus negative tests for host validation, timeouts, malformed JSON and failure mapping. This task's implementation does **not** modify the native screen, which remains WOO-015's responsibility. No LocalWP startup, connection or interactive manual validation is assigned to the WOO-014 repository agent; use PHPUnit/HTTP fixtures for PHP boundary proofs. Any live LocalWP check is developer-owned and outside this task's agent Validation gate.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

Logging/runtime boundary: this is a WordPress/PHP proxy, not a Node.js service. Do not add `@modainteract/moda-interact-shared/logging`, another generic logger or a Node-only package to the plugin. Preserve existing error handling and fail-closed security checks. Optional PHP diagnostics must use bounded, redacted WordPress/WooCommerce facilities and must not expose installation credentials, authorisation headers, signed R2 URLs, uploaded file contents or customer data. The hosted `moda-interact-api` owns its own shared structured logging.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and was explicitly completed by the developer on 2026-10-19. The implementation branch remains separate from `main`.

### Files Changed

Implementation commit `c0fbbc8326fa642311f468df60766ffcdf85bdf4`, published as `origin/task/ARCH-035-WOOCOMMERCE-014`, changes:

- `includes/Api/MerchantKnowledgeContracts.php`
- `includes/Api/MerchantKnowledgeUploadCapability.php`
- `includes/Api/ModaApiClient.php`
- `includes/Rest/MerchantKnowledgeController.php`
- `includes/Runtime.php`
- `composer.json`
- focused PHPUnit fixtures and controller/upload tests
- `README.md`

### Work Completed

Implemented privileged WooCommerce REST brokers for feature preferences, merchant knowledge operations, upload intent and upload finalisation. The boundary enforces capability, nonce, connected installation, canonical site identity and credential revalidation; forwards bounded JSON only; rejects multipart/file payloads; validates the approved R2 account, bucket, shop-bound path, expiry and exact signed headers; and returns signed capabilities with `private, no-store` without exposing secrets. Existing Billing, recovery and category routes were not changed.

Added positive and negative PHPUnit coverage for authenticated and denied requests, revocation and credential rotation, cross-installation input, no-store responses, exact hosted contracts, binary rejection, malformed responses, upstream failures, unsafe signed destinations and required-header validation.

### Validation Results

`composer lint` passed with no PHP syntax errors. Focused PHPUnit passed: `php vendor/bin/phpunit tests/MerchantKnowledgeControllerTest.php tests/MerchantKnowledgeUploadControllerTest.php` => 15 tests, 189 assertions. Full PHPUnit passed: `composer test` => 120 tests, 834 assertions. `git diff origin/main...HEAD --check` passed. `npm run package:production` passed: production build and strict i18n verification completed, WOO-014 manifest checks passed, and `moda-interact.zip` was verified with 116 entries. Build emitted only the existing webpack entrypoint-size recommendations.

### Deviations

None.

### Assumptions

The production packaging command temporarily removes Composer development dependencies from the implementation worktree as designed; no tracked implementation changes resulted. No live LocalWP validation was required by this task.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Accepted — developer self-review completed on 2026-10-19.

### Review Notes

The implementation matches the reconciled browser-direct R2 scope. All Work Items, Acceptance Criteria and required Validation entries are complete. The implementation is metadata-only at the WordPress boundary, fails closed on unsafe capabilities and stale installation state, preserves existing protected routes, and does not claim upload success before hosted finalisation.

### Reviewed Files

Implementation branch commit `c0fbbc8326fa642311f468df60766ffcdf85bdf4` and the focused test files listed in the Completion Report.

### Validation Reviewed

`composer lint`; focused PHPUnit (15 tests, 189 assertions); full PHPUnit (120 tests, 834 assertions); `git diff --check`; and `npm run package:production` all passed.

### Architecture Conformance

Conforms to the API-014..018 contracts and the approved browser-direct upload amendment. No out-of-scope repository changes or `main` merges were made.

### Follow-up

Developer completion is recorded below. `ARCH-035-WOOCOMMERCE-015` remains unstarted by this task.

## Developer Self-Review Accepted (2026-10-19)

Attempt 1 is accepted. The implementation task branch is clean and published at `origin/task/ARCH-035-WOOCOMMERCE-014`; the canonical parent task worktree is clean on `task/ARCH-035-WOOCOMMERCE-014`. All declared dependencies `ARCH-035-API-014` through `ARCH-035-API-018` resolve to `complete`. No required Work Item, Acceptance Criterion or Validation item remains incomplete. No `_index.md`, unrelated domain, or `main` branch was modified.

## Dependency Frontier Reconciliation (2026-10-19)

Canonical task routes report all five declared prerequisites complete: API-014, API-015, API-016, API-017 and API-018. `ARCH-035-WOOCOMMERCE-015` remains dependency-ready only after this completion record is integrated; it was not claimed or started. The canonical parent task worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-014` on `task/ARCH-035-WOOCOMMERCE-014`; the implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-014` on the mirrored task branch. Both are clean and their task branches are published. No task branch was merged into `main`.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-014`, explicitly taking over this ready agent-owned task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_woocommerce`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged.

## Developer Claim — Attempt 1

**Claimed — 2026-10-17T11:06:29Z.** The task transitioned from `ready`, Attempt 0, null executor to `in_progress`, Attempt 1, `executor: developer`.

- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-014`, branch `task/ARCH-035-WOOCOMMERCE-014`. It was clean before the claim. The task remote was already current at `f34f7958292660a84935c7c7a6ca2cbdb62bc8db`; after fetch, the branch fast-forwarded cleanly from current `origin/main` to `012707c91b12f29c5da333f3df8bc462a2fd608c`. No merge into `main` was performed as part of this preparation.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-014`, branch `task/ARCH-035-WOOCOMMERCE-014`. Created because no local/remote task branch or canonical worktree registration existed, from fetched `origin/main` at `56c5acd6a20c0c1c15897bfa0725f7ea511c7f04`; the new worktree is clean and contains that mainline commit.
- The shared WooCommerce source checkout contains unrelated local edits under `moda-tools/render-localwp/` and an untracked `typescript` path. These were left untouched; all implementation work will use the isolated worktree above.
- Dependency routes were rechecked immediately before claim: API-014, API-015, API-016 and API-017 all report `complete`.
- Required focused validation remains to be run during implementation: PHPUnit proxy authorization/nonce/capability/upload tests, fixture HTTP/R2 failure tests, relevant PHP lint and declared JS/PHP/build/ZIP checks, plus `git diff --check`.

## Architectural Scope Reconciliation (2026-10-18)

- Supersedes the original 16 October PHP binary-transfer instructions in this task with the approved 17 October browser-direct R2 design, without reopening completed API-017 or rewriting the developer's 17 October task claim.
- The 18 October codebase snapshot records `ARCH-035-API-018` **Complete** (developer-accepted Attempt 1); its browser signing/no-store contract is an additional prerequisite and no longer blocks the existing developer-owned task. Validate the recorded dependency against the actual parent branch when completing this task.
- WOO-014 owns only the privileged WordPress feature/knowledge metadata proxy and signed capability handoff. WOO-015 owns React browser PUT and its redirect/abort/CORS handling; GATEWAY-001 owns controlled R2 origin CORS configuration. No WOO-015 or Gateway changes are authorised here.
- Existing parent/implementation worktree and developer-execution evidence above remain authoritative. The Completion Report, validation checkboxes, actual commits and developer completion decision must be updated from work actually performed, not from the existence of a proposed patch.

## Developer Completion Decision

On 2026-10-19, the developer explicitly invoked `/moda_developer_update ARCH-035-WOOCOMMERCE-014 complete` after the accepted Attempt 1 review. Attempt 1 remains the accepted attempt; status is `complete`, with `executor: null` and `claimed_at: null`. The implementation and parent task branches remain separate from `main` and were not merged.
