---
id: ARCH-035-API-017
architecture_id: ARCH-035
title: Enable Woo knowledge file upload, finalisation and reprocessing
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 46
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-015]
enables: [ARCH-035-WOOCOMMERCE-014]
created: 2026-10-16
updated: 2026-10-17
---

# ARCH-035-API-017 — Enable Woo knowledge file upload, finalisation and reprocessing

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_api`, repository `moda-interact-api`; coordinator: `moda_architect`.

## Objective

Provide authenticated Woo CSV/XLSX upload intents and verified durable finalisation/replacement/reprocess lifecycle over the existing R2 and knowledge revision records.

## Context

Shopify `upload.server.ts` supports upload intent/finalise/edit/reprocess but assumes a myshopify.com upload domain. Woo installations use arbitrary store domains. API must not reuse that provider-specific validation or break existing Shopify R2 paths.

## Scope

- Implement signed short-lived upload-intent and verified finalize endpoints plus upload-source metadata edit/replace/reprocess where the existing source model supports them.
- Derive R2 object namespace solely from authenticated Shop: `merchant-knowledge/<env>/woocommerce/<validated-shop-id>/<asset-uuid>/source.<csv|xlsx>`; prove Background can read that namespace and preserve legacy Shopify object-key semantics.
- Enforce allowed source pairs, entitlement/count/file size, accepted MIME/extension, bounds, SHA-256/integrity and object metadata verification; never trust browser-supplied object key, storage URL or shop ID.
- Make intent/finalize idempotent under retries; mark accepted assets/revisions durably, leave eligible durable `PENDING` revisions for Background reconciliation; expire abandoned intents. Fail closed on R2/network/configuration errors.
- Document signed PUT host/expiry/header contract for PHP server-side proxy, strict OpenAPI and bounded secret-free logging.

## Out of Scope

- Direct browser-to-Moda database/Redis/R2 credential access, new unbounded CORS wildcard, WordPress file persistence, Shopify object-key migrations.
- Changing existing Background worker implementation unless a specific gap is escalated and separately approved.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. Record bounded structured logging through `@modainteract/moda-interact-shared/logging` when changing generic application logs.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [x] Implement signed short-lived upload-intent and verified finalize endpoints plus upload-source metadata edit/replace/reprocess where the existing source model supports them.
- [x] Derive R2 object namespace solely from authenticated Shop; verify Background reads persisted object keys and preserve existing Shopify object-key semantics.
- [x] Enforce allowed source pairs, entitlement/count/file size, accepted MIME/extension, bounds, SHA-256/integrity and object metadata verification; never trust browser-supplied object key, storage URL or shop ID.
- [x] Make intent/finalize idempotent under retries; mark accepted assets/revisions durably, leave eligible durable `PENDING` revisions for Background reconciliation; expire abandoned intents. Fail closed on R2/network/configuration errors.
- [x] Document signed PUT host/expiry/header contract for PHP server-side proxy, strict OpenAPI and bounded secret-free logging.
- [x] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- POST `/v1/merchant/merchant-knowledge/upload-intents`; POST `/v1/merchant/merchant-knowledge/upload-finalize`; PATCH `/v1/merchant/merchant-knowledge/uploads/{sourceId}`; POST `/v1/merchant/merchant-knowledge/uploads/{sourceId}/reprocess`.
- Versioned short-lived upload authorization is for server-side PHP to R2 only; API-015 defines canonical source read-back.

## Dependencies

- `ARCH-035-API-015` (must be Complete and architect accepted)

## Enables

- `ARCH-035-WOOCOMMERCE-014`

## Acceptance Criteria

- [x] Valid CSV and XLSX uploads produce exactly one owned asset and correct source/revision on repeated finalize; expired/tampered/wrong-Shop file fails closed.
- [x] Shopify's `*.myshopify.com` restriction is not bypassed; Woo uses authenticated stable Shop identity and Background reads the persisted asset key.
- [x] Large, wrong MIME, wrong hash, invalid file extension, quota, inaccessible R2 and revoked installation have explicit safe errors.
- [x] Merchant-off configuration remains possible while off without claiming ingestion; source replacement/reprocess observes existing lifecycle.
- [x] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in the real development workspace.

## Validation

- [x] Focused R2 signer/object validation tests, disposable PostgreSQL upload/replace/retry tests and representative Background asset retrieval proof.
- [x] Typecheck, lint, build, bounded security/log review and `git diff --check`.
- [x] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled API-structure handoff (2026-10-16 22:56 snapshot)

- Implement upload/finalise/replace/reprocess as separate, bounded modules under `src/merchant/merchant-knowledge/` with API-only R2 signing/object verification dependencies. Register via `src/composition/merchant.ts`, with Woo authentication from `src/auth/woo-installation/` and HTTP helpers from `src/http/`. Do not import `moda-interact/app/services/merchant-knowledge/upload.server.ts` (it depends on Remix aliases, Shopify domain identity and Shopify server configuration); use it only to preserve existing model/revision semantics.
- The API runtime does not yet define Merchant Knowledge R2 configuration or declare an R2/AWS signing SDK. Add bounded, injectable server-only configuration/dependencies without making unrelated merchant read routes depend on R2 startup availability. Fail closed on upload operations if signing/bucket/environment settings are missing or malformed. Record new deployment secret/Render Blueprint requirements for architect/Gateway ownership; never commit secret values.
- Derive Woo R2 keys from the authenticated Shop ID, validated deployment environment and server-generated asset UUID, preserving all Shopify keys. Confirm Background's uploaded-asset acquisition reads persisted object keys independently of Shopify domain pattern. Document the signed PUT destination and required headers for WordPress server-side transport, with redirects, private/loopback destinations and unintended hosts rejected by the plugin.
- Keep durable asset intent/finalise and source revisions transactionally safe; verified R2 metadata (size/type/SHA-256) must match the expected intent before activating. Background's existing durable `PENDING` revision reconciler provides eventual queue delivery; do not introduce an unapproved BullMQ requirement or network call in the transaction. Cover repeated finalise, aborted upload/expiry, replacement, wrong bytes and error isolation.
- Unit/R2 simulation tests belong under `tests/unit/merchant/merchant-knowledge/`, PostgreSQL lifecycle tests under `tests/integration/merchant/merchant-knowledge/`, with runner integration and `openapi/merchant-knowledge-v1.yaml` updates.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

## Developer Execution Ownership Amendment

On 2026-10-17, the developer invoked `/moda_developer_create ARCH-035-API-017`, explicitly taking over this ready agent-executed task. Execution and completion authority are now `developer`/`developer`; `assigned_agent: moda_api`, repository ownership, scope, dependencies, acceptance criteria and validation requirements are unchanged. Attempt 1 was claimed by developer after canonical parent and implementation worktree synchronization.

## Completion Report

### Status

Developer implementation and self-review passed for Attempt 1; submitted for architect review. The task remains `review`, not `complete`, because completion mode is developer and no explicit completion action was requested.

### Files Changed

In `moda-interact-api` (16 files): `docs/arch035-knowledge-upload.md`; `openapi/merchant-knowledge-v1.yaml`; `package.json`; `package-lock.json`; `scripts/test-arch035-knowledge-upload-postgres.mjs`; `src/composition/merchant.ts`; `src/merchant/merchant-knowledge/upload-contract.ts`; `src/merchant/merchant-knowledge/upload-r2.ts`; `src/merchant/merchant-knowledge/upload.routes.ts`; `src/merchant/merchant-knowledge/upload.service.ts`; `tests/integration/merchant/merchant-knowledge/fixtures/sample-knowledge.xlsx`; `tests/integration/merchant/merchant-knowledge/upload.postgres.test.ts`; `tests/unit/composition/real-route-registration.test.ts`; `tests/unit/http/integration-runner-registration.test.ts`; `tests/unit/merchant/merchant-knowledge/upload-contract.test.ts`; `tests/unit/merchant/merchant-knowledge/upload-r2.test.ts`.

### Work Completed

- Added bounded, installation-authenticated upload intent, finalize, metadata edit/replace and reprocess operations, strict OpenAPI contracts, and API-only lazy R2 configuration so unrelated read routes remain available without R2 configuration.
- R2 keys are derived from the verified Shop principal and server-generated deterministic asset identity under `merchant-knowledge/<environment>/woocommerce/<shopId>/<assetId>/source.csv|xlsx`; user input cannot select a Shop ID, object key or storage URL. Existing Shopify object-key handling was not changed.
- Finalize verifies persisted intent ownership, entitlement/source pair and quota, then checks HEAD metadata and streams GET bytes to verify exact size and SHA-256 before transactional asset/source/revision updates. Repeated intent/finalize resolves to the same asset/revision; replacement and reprocess create durable generations with `PENDING` revisions. Expired intents, wrong-Shop requests, malformed metadata, revoked installations and integrity mismatch fail closed.
- Documented the ten-minute signed PUT contract, required headers, PHP server-side transport restrictions, required API deployment variables and secret-storage ownership. No credentials or object keys are logged or returned in the canonical projection.
- Added a direct unit regression proving R2 transport errors map to the bounded `knowledge_upload_unavailable` response without provider diagnostics.
- Existing Background asset acquisition reads the persisted object key without Shopify-domain validation. No Background files were changed.

### Validation Results

- `npx tsx --test tests/unit/merchant/merchant-knowledge/upload-contract.test.ts tests/unit/merchant/merchant-knowledge/upload-r2.test.ts` — 5/5 passed before the final error-path regression.
- `npx tsx --test tests/unit/merchant/merchant-knowledge/upload-r2.test.ts` — 3/3 passed after the regression.
- `npm run test:arch035-knowledge-upload:postgres` — 1/1 migration-backed disposable PostgreSQL upload lifecycle test, including CSV/XLSX, intent/finalize replay, replacement, reprocess, entitlement/quota, expiry and revoked-installation cases.
- `npm test` — 453/453 passed after the final regression.
- `npm run test:integration` — complete captured run exited successfully; 11 registered harnesses, 55 tests total, zero failures. This includes API-016 commands (2 tests), API-015 read (1 test), and API-017 upload (1 test) PostgreSQL fixtures.
- From `moda-interact-background`: `npx vitest run tests/unit/services/merchant-knowledge-uploaded-asset-acquirer.test.ts` — 6/6 passed; verifies persisted object-key retrieval, Shop isolation, size/hash checks and no storage identifier leakage.
- `npm run typecheck`, `npm run lint`, and `npm run build` — passed after the final test change.
- `git diff --check origin/main...HEAD` and working-tree `git diff --check` — passed.

The first full integration-chain invocation hit a transient Prisma transaction timeout in the unrelated API-014 feature-preferences harness. That harness passed standalone, and the subsequent fully captured integration-chain run exited successfully with zero failures. R2 signing and object verification used the AWS signer and an injected test transport; no live Cloudflare R2 credentials or bucket were available or exercised.

### Branch and Worktree Evidence

- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-017`, branch `task/ARCH-035-API-017`, final commit `c5d0c055333e2ac6657549a2df35a9db78c5df41`, matching `origin/task/ARCH-035-API-017`; clean after publication. The task commits are `716272630edaa39b691c3b12149ff66077946456`, `90e4e630165042202a23b20a0fd98965175bff89`, and `c5d0c055333e2ac6657549a2df35a9db78c5df41`.
- Implementation `origin/main` baseline: `d23e24b5675c6cf07d71b6da7bdfa7cd94a9acad`; task branch contains it and is three commits ahead. Recursive `database` submodule is initialized at `139765042baad3901682cfe9c54a3d6bba73e75c` (`heads/main`).
- Canonical parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-017`, branch `task/ARCH-035-API-017`, clean at claim/report-edit baseline `cbf7e8b4a90bc5f7477baa1e1b524f21144e0e0e`, matching `origin/task/ARCH-035-API-017` before this report update.
- No `_index.md`, submodule gitlink, or unrelated task file is included in the report change. Unrelated changes in the primary shared workspace were not touched.

### Deviations

No cross-repository implementation changes were made. Background compatibility was verified with its existing asset-acquirer unit suite. Live R2 service connectivity remains a deployment-level validation; missing/malformed API R2 configuration fails closed with 503.

### Assumptions

API-015 is complete and remains the canonical Merchant Knowledge projection. Background's existing acquisition and pending-revision reconciliation contracts remain authoritative. Deployment variables listed in `docs/arch035-knowledge-upload.md` must be configured through the owning deployment secret-management path; no secret values are stored in this repository.

### Unresolved Issues

No implementation or validation blocker identified. Live R2 connectivity and deployment-secret provisioning were not exercised in this local task validation.

### Developer Self-Review

**Passed — 2026-10-17.** Attempt 1 satisfies the bounded API-017 scope, acceptance criteria and required validation. The implementation task branch is committed and pushed; this passing review is submitted for architect review and awaits explicit developer completion.

## Architect Review

### Review Status

Pending — submitted for architect review after developer self-review.

### Review Notes

Implementation and validation evidence is recorded in the Completion Report. Architect review has not yet been performed.

### Reviewed Files

Implementation files listed in the Completion Report and this API-017 task definition; no task index or unrelated domain files changed.

### Validation Reviewed

All validation listed in the Completion Report passed; live R2 service connectivity was not exercised.

### Architecture Conformance

Pending architect review.

### Follow-up

`ARCH-035-WOOCOMMERCE-014` remains pending until all explicit dependencies, including API-014 through API-017, are complete.